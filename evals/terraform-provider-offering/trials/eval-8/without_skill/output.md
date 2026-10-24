# Thornfield provider configuration review

I reviewed the design as you described it, not the source. I assumed a Terraform provider, probably on the Plugin Framework. Findings are ranked by severity.

## Fix first

### 1. 🔴 `POST /v1/projects/default` at configure time

- **It mutates the account during `plan`.** Configure runs on plan, refresh, import and data-only runs. A read-only CI job, or a plan on a PR, now creates a project.
- **It creates an untracked resource.** The project is not in state, so it can't be destroyed and it drifts.
- **It makes the wrong-account bug worse.** If the key resolves to the wrong account, the provider writes into that account.
- **It is racy.** Two concurrent runs both try to create it. Handling 409 is the minimum.
- **Fix:**
  - Remove it from configure.
  - Make the default project a `thornfield_project` resource that other resources depend on.
  - Or have the create path of resources that need a project do an idempotent ensure-exists check, and only during apply.
  - If you must keep it, gate it behind an opt-in `ensure_default_project = true`, run it on apply only, and treat 409 as success.

### 2. 🔴 "Silently used the wrong account"

The Vault data source is the likely trigger. An unknown value reaches `Configure` in the situations below, and each one is a candidate cause. I can't tell which one hit that customer without the source.

- **Unknown at plan time.** The `vault_generic_secret` value is unknown whenever the data source is deferred, for example when it depends on a resource that has not been applied yet. The provider then receives an empty or null `api_key`.
  - If your code falls back to an env var, a credentials file or a cached token, it authenticates as a different identity without any error.
  - Check `config.APIKey.IsUnknown()` and `IsNull()` explicitly.
  - If the value is unknown, skip all API calls in configure and fail only when a request actually needs the key.
  - Never fall through to another credential source after an unknown value.
- **Package-level session state.** If the session token lives in a package-level variable or a shared client, a second provider instance (an alias, or a module per project) overwrites the first.
  - The last-configured key then wins for all instances.
  - Keep the state on the provider instance. If you cache across instances, key the cache by a hash of the API key.
- **Wrong key inside the secret.** `vault_generic_secret.data["api_key"]` can point at a stale or wrong key in a multi-key secret.
  - Surface the identity so this is visible: call `GET /v1/whoami` (or the equivalent) once, lazily, and log account and org at INFO with `tflog`.
  - Offer an optional `expected_account_id` attribute and fail on mismatch. Customers with several accounts will want it.
- **Secret in state.** The data source also writes the key into state in plaintext. Document the ephemeral `vault_kv_secret_v2` resource (Terraform 1.10+) as the recommended wiring.

### 3. 🟠 Session creation at configure time

- **Every command creates a session.** Plan, refresh and apply each create one that nothing revokes, because providers have no close hook. That adds API load and leaks sessions.
- **Failures break unrelated commands.** A session failure at configure fails `plan -refresh-only`, `import` and destroy of unrelated resources.
- **Long applies outlive the token.** There is no refresh on expiry, so a long apply can fail midway.
- **Fix:**
  - Create the session lazily on the first request, guarded by `sync.Once` or a mutex.
  - Refresh it on a 401, or shortly before the known TTL.
  - Make the session token never appear in logs. Mark it sensitive and mask it with `tflog.MaskFieldValuesWithFieldKeys`.
  - Ask whether the API key can authenticate directly. If it can, drop the session.

### 4. 🟠 429 storms

Two of your configure calls per provider instance multiply the load. Terraform's default `-parallelism=10` multiplies it again, and large customers run many aliases.

- **Backoff.** Retry 429 and 5xx with exponential backoff and full jitter. Honor `Retry-After` and any `X-RateLimit-*` headers. Bound it with `max_retries` and respect `ctx` deadlines.
- **Shared limiter.** Use a token-bucket limiter shared across all provider instances for the same key hash, not one per instance. Add a concurrency semaphore below Terraform's parallelism.
- **Idempotent retries only.** Retry non-idempotent POSTs only with an idempotency key. Otherwise a retry after a timeout can create duplicates.
- **Fewer calls.** Prefer list endpoints or ETags over one GET per resource on refresh.
- **Config and logging.** Expose `max_retries` and `rate_limit_per_second` as optional attributes with env var overrides. Log retries at WARN so customers can see the throttling.

## Smaller fixes

### 5. 🟡 `api_key` as Required

Required blocks the env var path (`THORNFIELD_API_KEY`), which CI users expect. It also makes the unknown-value case above harder to handle.

- Make `api_key` Optional and Sensitive, with env var fallback.
- Fail in configure with a clear diagnostic only if the value is known and empty, or if it is still missing when a request needs it.
- Document the precedence: attribute, then env var. Never fall back past an explicit but unknown value.

### 6. 🟡 `base_url` defaulting to EU

- **Data residency.** An EU default is reasonable, but a US-region key against it returns 401, or worse, matches a different account.
  - Consider a `region` attribute instead of a raw URL, with `base_url` as an override.
  - Allow `THORNFIELD_BASE_URL` / `THORNFIELD_REGION` env vars.
- **URL validation.** Require https and normalize trailing slashes. The key is sent as a bearer token, so never send it over plain http without an explicit opt-out.
- **Diagnostics.** Include the resolved host in auth-failure messages.

### 7. 🟡 Hygiene

- Set an HTTP client timeout.
- Send a User-Agent with the provider and Terraform versions.
- Use `tflog` masking on the key and token.

## Tests to add

1. **No mutations on plan.** Configure plus plan against a mock server records zero non-GET calls.
2. **Unknown key.** Pass an unknown `api_key` and assert no request is made and no fallback credential is used.
3. **Two aliases, different keys.** Assert each alias's requests carry its own key.
4. **429 handling.** A mock returns 429 with `Retry-After`, and the test asserts the wait, the bounded retries and the shared limiter.
5. **Session expiry.** A mock returns 401 mid-apply and the test asserts one refresh.
6. **Region mismatch.** A key from another region produces a diagnostic that names the host.

I'd start with items 1 and 2, because they are the account-safety bugs. Items 3 and 4 are the performance fixes. To confirm the root cause of the customer's report, ask for their `TF_LOG=debug` output. It should show whether `api_key` arrived empty and which credential source the provider used.