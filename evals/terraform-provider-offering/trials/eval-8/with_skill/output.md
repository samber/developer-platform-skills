# Thornfield provider configuration review

## Verdict

Do not ship this configure block as it stands. Four issues, ranked by harm:

| # | Issue | Harm |
|---|---|---|
| 1 | Likely cause of the "wrong account" report: no guard for unknown `api_key` | Silent wrong identity |
| 2 | `POST /v1/projects/default` at configure time | Hidden writes on every plan, fails for read-only keys |
| 3 | `POST /v1/sessions` at configure time, no throttling | Feeds the 429 storms, leaks sessions |
| 4 | `api_key` is `Required` | Blocks env vars and secret injection, and widens #1 |

I have not seen your Go code, so #1 is a hypothesis built from the symptoms. Use the repro under #1 to confirm it.

## Findings

### 1. The "wrong account" report (🔴)

**Likely mechanism.** `vault_generic_secret` can be unknown at plan time. That happens when the data source has `depends_on`, reads from a path another resource creates, or sits behind a not-yet-applied dependency. The provider then receives `api_key` as unknown.

In the framework, `types.String.ValueString()` returns `""` for an unknown value. If Configure doesn't check `IsUnknown()`, one of these happens:
- The empty key falls through to some fallback, such as an ambient env var, a credentials file or a cached session. The provider then authenticates as a different identity.
- The unknown value is coerced to `""` and a stale session is reused.

The rule in the skill: guard unknown values on auth attributes, or the provider silently authenticates as the wrong identity.

**Second suspect: the session cache.** If the session token is cached in a package-level variable, or on disk, and the cache key ignores `api_key` and `base_url`, then two provider aliases can share one session. Anyone running a multi-account setup with `alias` hits this. Check it.

**Third suspect: the region.** `base_url` defaults to EU. Check whether a key is bound to a region. If keys aren't region-bound, a US-region customer's key can resolve against the EU endpoint without any error.

**Repro.** Write an acceptance test first.
1. Wire `api_key` from a data source that is unknown at plan, for example with `depends_on` on a resource.
2. Set a different `THORNFIELD_API_KEY` in the environment.
3. Assert that the run errors and never authenticates as the env-var account.
4. Add a second test with two aliases using different keys.

**Fix.**
- If any credential attribute is unknown, don't build a client or call the API.
- Return one error: "`api_key` is unknown at plan time. Wire it from a value known during plan, or set `THORNFIELD_API_KEY`."
- Resolve the credentials as a complete set (key, base URL, region) with this precedence, highest first: provider block, then env vars, then credentials file.
- Key any session cache on a hash of the whole credential set. Never use a global singleton.
- If your Vault provider and Terraform are on 1.10 or later, tell these customers about ephemeral Vault secrets as the supported wiring.

**Release note.** Turning a silent success into an error is stricter validation, which the contract says belongs in a major. It is a judgement call. I would ship it in a minor as a security fix with a prominent changelog entry, because the old behaviour was wrong-identity authentication. Your call: if you hold to the rule literally, it waits for a major.

### 2. Creating the default project at configure time (🔴)

- Configure runs on every `plan`, `apply` and `refresh`. A write there fires on every plan, including read-only plans and CI drift checks.
- It fails under least-privilege or read-only keys. The "first apply doesn't fail" fix then breaks every restricted-key user.
- The project exists outside state. Destroy can't remove it, and two workspaces racing on first run can collide.
- It hides the real gap. The first apply fails because configs assume a project exists that no resource declares.

**Fix.** Move the behaviour out of the provider block:
1. Ship a `thornfield_project` resource with import, and a singular `thornfield_project` data source. The data source errors when the project is missing or when more than one matches.
2. Better, make the API create the default project when the account is created. Ask the API team for that.
3. Resources then reference `thornfield_project.default.id`. Terraform orders the dependency itself, so the first apply works with no hidden write.

**Compatibility.** Existing customers rely on the project appearing. Removing the call outright changes behaviour for unchanged configs, which is a breaking change. So:
1. In a minor, add an opt-out attribute and deprecate the implicit creation with a `DeprecationMessage`. Keep the default behaviour for now.
2. In the next major, remove it.

### 3. Session creation at configure time and 429 storms (🟠)

**Why it hurts.**
- `POST /v1/sessions` per configure means one session per provider instance, and one more per alias.
- Terraform runs 10 operations in parallel by default. Large configs have many resources and many aliases, so request bursts are certain. Sessions are never closed, so they also pile up.
- With no client-side throttling and no `Retry-After` handling, 429s turn into failed applies.
- The gate row "Documented rate limits" is UNKNOWN. Under the skill, UNKNOWN counts as FAIL until answered.

**Fix.**
- **Validation:** replace the eager session with one cheap read-only identity call (for example a "who am I" GET). Put it behind `skip_credentials_validation`, and skip it when any credential is unknown.
- **Session token:** if the API needs a token exchange, do it lazily inside the HTTP client. Keep it in memory only, refresh it once on 401, and reuse it across all resources of that provider instance. If another resource must consume the token, expose it as an ephemeral resource instead.
- **Throttling:** add a client-side token-bucket limiter sized to the documented quota.
- **429 handling:** honour `Retry-After`, add jitter, bound the retries, and retry only 429 and the specific typed temporary errors. Never retry broad classes such as all 5xx.
- **Create retries:** a retry after a 429 is safe because the request was rejected. A retry after a timeout is only safe if the create is idempotent. That gate row is also UNKNOWN. Until it is answered, look up by unique name before retrying a create.
- **Docs:** document a safe `-parallelism` for large configs, and the rate-limit constants, with each constant justified.
- **API team:** route quota design to `api-rate-limit-policy` and idempotency to `api-idempotency-retry`.
- **Logging:** send a `User-Agent` with the provider name and version so your API logs separate provider traffic from other clients.

### 4. `api_key` is Required (🟠)

"So people don't forget it" is the wrong trade. `Required` rejects env-var and CI-secret injection, so users must write the key into HCL. The fix:
- Make it `Optional` and `Sensitive`, with no default.
- Fall back to `THORNFIELD_API_KEY`.
- When nothing resolves, error with every source tried and a docs URL, for example: "No API key found. Tried: provider `api_key`, env `THORNFIELD_API_KEY`, credentials file. See <docs URL>."
- Never log secret values.
- `Required` to `Optional` is a relaxation, so it is not breaking.

### Fine as designed

- A `base_url` default is acceptable because it is not a credential. Just document it, and add an env override such as `THORNFIELD_BASE_URL`.

## Target Configure flow

1. Read `api_key` and `base_url` from config.
2. If any is unknown, return the single "unknown at plan time" error and make no API call.
3. If any is null, resolve it from the env var, then the credentials file. If none resolves, return the error naming every source tried.
4. Build the client with the user agent, the limiter and the lazy in-memory session, keyed on the resolved credential set.
5. Unless `skip_credentials_validation` is set, make one read-only identity call.
6. Make no writes.

## Gate rows for the provider

| Check | State |
|---|---|
| Documented rate limits | UNKNOWN, owner API team, due week 1 |
| Idempotent create | UNKNOWN, owner API team |
| Secrets identified | PASS (`api_key` is user-supplied and never returned, so it stays a provider-config `Sensitive` attribute) |
| Side effects at configure | FAIL, fix by moving to a resource |

Per the skill's cut rule, do not ship the dependent resources while rate limits and idempotency read UNKNOWN.

## Tests to add

- The unknown-key repro from #1, including the alias case.
- Read-only key: `plan` succeeds, with no write call.
- No credentials: the error lists every source tried.
- 429 with `Retry-After`: bounded retry, then a clear failure.
- Mutation check: remove the unknown guard and the first test must fail.

## Questions I need answered

1. Are keys bound to a region, and does the EU default ever hit a US account?
2. Is the session token cached anywhere (global, disk, per alias)?
3. What are the documented quotas, and what does the 429 response carry (`Retry-After`, reset headers)?
4. Is create idempotent, and does the API support idempotency keys?
5. Which Terraform and OpenTofu minimums do you support? That decides the ephemeral and write-only options.
6. Who owns the provider's issue queue? Partner status requires a 48-hour fix for critical issues.