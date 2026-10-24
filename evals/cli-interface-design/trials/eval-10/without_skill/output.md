# `sm` design: configuration, profiles and the create path

I didn't read the repo or `skill-wip/`. This is a design from the incident descriptions alone.

## 0. Incident to cause to fix

| Incident | Root cause | Fix |
|---|---|---|
| Wrong customer's org, no explanation | Implicit context: the profile, region and token come from layered files, and nothing shows which one won. | Explicit profiles, a pinned org, a resolved-context banner, and a refusal to mutate on an implicit default. |
| Config truncated by 4 parallel refreshes | The token sits in a config file that refresh rewrites in place, with no lock and no atomic write. Rotating refresh tokens make the race worse. | Split config from credentials, use a lock plus a re-read, and write atomically. |
| Duplicate fleet after a 504 | A create is not idempotent, and a 504 leaves the outcome unknown. | `Idempotency-Key` on every create, a unique name per org, and an "unknown outcome" exit path. |
| Always the latest API | The CLI and server are coupled, and self-hosted installs lag. | Pin the API version per CLI release and per profile, with negotiation. |

## 1. Files and secrets

Config and secrets live in separate files. Refresh only ever touches credentials.

| File | Contents | Secret? | Written by |
|---|---|---|---|
| `$XDG_CONFIG_HOME/sm/config.toml` (default `~/.config/sm/config.toml`) | Profiles and `default_profile` | No | `sm profile …`, `sm login` |
| OS keychain, fallback `~/.local/state/sm/credentials.json` (0600) | Tokens, one entry per profile | Yes | `sm login`, refresh |
| `.sm/project.toml`, committed to git | `profile = "acme-eu"`, optional `org = "org_123"` | **Never** | The humans in the project |
| `SM_TOKEN` | A bare token for CI | Yes | The CI system |

Rules:
- The project file refers to profiles by name, so the same repo works for everyone.
- `sm` **refuses** any token in a project file. Tokens in git are the worst outcome here.
- The legacy `.smrc` token is honored for one release with a loud warning, then removed.

### Profile schema

```toml
default_profile = "acme-eu"

[profiles.acme-eu]
region      = "eu"                  # us | eu | apac; mutually exclusive with base_url
org         = "org_8f2c"            # pinned expected org, verified on every response
# api_version = "2026-10-01"        # optional override of the CLI pin

[profiles.globex-onprem]
base_url    = "https://sm.globex.example.com"   # self-hosted
org         = "org_31ab"
ca_bundle   = "/etc/ssl/globex-proxy-ca.pem"
proxy       = "http://proxy.globex.example.com:3128"
api_version = "2026-04-01"          # an older install stays on a version it supports
```

### Token binding

- A token is stored under its profile and sent only to that profile's host.
- Redirects to another host drop the `Authorization` header.
- A token from one customer therefore can't reach another customer's endpoint.

## 2. Resolution order

Each field resolves independently. Highest wins:

1. Flag: `--profile`, `--region`, `--base-url`, `--org`
2. Env: `SM_PROFILE`, `SM_REGION`, `SM_BASE_URL`, `SM_ORG`, `SM_TOKEN`
3. `.sm/project.toml`, found by walking up from cwd
4. `config.toml`: `default_profile`
5. Compiled defaults (API version only)

Region has no compiled default. A guessed region would silently pick the wrong data residency.

## 3. Wrong-org fix, in four layers

**a) Banner.**
- Every command prints one line to stderr, for TTY and non-TTY alike:
  ```
  sm: profile=acme-eu (from .sm/project.toml) org=Acme Corp [org_8f2c] region=eu api=2026-10-01 token=keychain
  ```
- Stdout stays clean for piping.
- `--quiet` hides the banner only for read commands.

**b) Org pin.**
- The server returns the org id on every response.
- If the profile or project pins `org` and the response differs, `sm` aborts with an error that names both orgs and the source of each.
- A pin is a cheap guard that survives copy-paste mistakes.

**c) Mutation guard.**
- A command that creates, updates or deletes needs an explicit profile: flag, env, or project file.
- If the profile came only from `default_profile`:
  - On a TTY, `sm` prompts `Create in acme-eu? [y/N]`.
  - Non-interactively, it fails with exit code 2.
- Reads on the default profile are allowed. The banner covers them.

**d) Diagnostics.**
- `sm config show --resolved` prints each field with its source.
- `sm whoami` prints identity, org and the token's expiry and source.
- Setting `SM_TOKEN` over a stored credential shows `token=env (overrides keychain)` in the banner.

`SM_TOKEN` rules:
- It applies to the resolved profile.
- It requires a profile, region or base URL from an explicit source.
- It is never refreshed or written to disk.
- CI should use long-lived service-account keys, not refreshable user tokens.

## 4. Concurrent refresh without corruption

Four agents hit expiry at the same moment.

**Write path.** Write to a temp file in the same directory, `fsync`, then `rename` over the target, so readers never see a partial file. A keychain write is already atomic per item.

**Refresh protocol:**
1. Read the credentials. If the access token has more than 60 s plus jitter left, use it. No lock is taken.
2. Otherwise take an exclusive `flock` on `credentials.lock`, with a 30 s timeout. The kernel releases it if the process dies. On network filesystems where `flock` is unreliable, fall back to an `O_EXCL` lockfile with pid and TTL.
3. **Re-read** the credentials. If another process already refreshed, use that token and release the lock. This double check is what prevents N refreshes.
4. Otherwise call refresh, write atomically, and release.

**Server side.** Rotating single-use refresh tokens turn this race into a revoked session. Ask the server team for a 30-60 s reuse grace window on a just-rotated refresh token, which gives the same result as an idempotent refresh. The lock is the primary defense, and the window is the backstop for processes that don't share a filesystem.

**Corruption handling.**
- If a file fails to parse, `sm` never overwrites it.
- It copies the file to `*.corrupt-<ts>` and tells the user to run `sm login`.
- Config is never rewritten by refresh. That removes the original incident's blast radius.

**Parallel agents.** Recommend one `SM_TOKEN` from a service account, set by the parent. Agents then share nothing mutable.

## 5. TLS-re-signing proxies and self-hosted

- Honor `HTTPS_PROXY`, `NO_PROXY` and per-profile `proxy`.
- Trust the **OS trust store**. Corporate proxy CAs are usually installed there, and a bundled Mozilla root list would fail.
- Add extra CAs per profile with `ca_bundle`, plus `SSL_CERT_FILE` as a global fallback.
- A TLS failure never degrades silently. The error names the issuer it saw, says whether a proxy was detected, and suggests `ca_bundle`.
- `sm doctor` prints the proxy used, the certificate chain and issuer, DNS, region reachability, the API versions supported, and clock skew.
- No `--insecure` flag and no env switch. If a customer demands one, make it a profile-only `tls_pin_sha256` setting, which is safer than disabling verification.
- Self-hosted domains are just `base_url`. The `region` shortcut is for SaaS only.

## 6. API version pinning

- Each CLI release ships a pinned date-style version, sent as `SM-API-Version: 2026-10-01`. Upgrading the CLI is the deliberate act that moves the version.
- Precedence is `--api-version`, then `SM_API_VERSION`, then the profile, then the CLI pin.
- On first contact per profile, `GET /version` lists the supported versions, and the result is cached for 24 h.
- If the pinned version is unsupported, say so. For example: "server supports 2026-01…2026-04, this CLI needs ≥ 2026-07, use `sm` v1.x or upgrade the server".
- Surface deprecation headers as warnings.
- Self-hosted installs can lag by quarters. The per-profile pin (see `globex-onprem` above) handles this.

## 7. Create path

### Idempotency

1. Every `POST` create sends `Idempotency-Key`, a UUIDv7 generated once per invocation. Internal retries reuse it.
2. The server stores key, request fingerprint and response for 24 h:
   - Same key and same body: replay the original response, with `Idempotent-Replay: true`.
   - Same key and different body: `422 idempotency_key_reuse`.
   - Same key still in flight: `409` with `Retry-After`.
3. A CI re-run is a new process and gets a new key. For that case, offer `--idempotency-key` / `SM_IDEMPOTENCY_KEY`. For example, `--idempotency-key "$PIPELINE_ID-edge-01"`. The key must stay stable across job retries, so don't include the attempt number.
4. Do not derive the key by hashing the body automatically. Deleting a fleet and recreating it within 24 h would replay the deleted one.

### Natural-key uniqueness

- The real invariant is "one fleet named `edge-01` per org". Enforce it server-side, returning `409 fleet_name_taken` with the existing `fleet_id`.
- Add `sm fleets create --if-not-exists`:
  - If the existing spec is equal, return it and exit 0.
  - If it differs, exit non-zero and show the diff.
- This covers the retry when the idempotency window has expired or the CI run lost its key.

### Retry policy

- Retry connection errors, 408, 429, 502, 503 and 504.
- Use at most 3 attempts, exponential backoff with jitter, a total deadline of 60 s, and honor `Retry-After`.
- Never retry a non-idempotent request that lacks a key. Creates always have one.

### Unknown outcome

- If the final attempt ends on a 504 or a timeout, the result is unknown, not failed.
- Exit with a dedicated code, 75, and print the request id and key:
  ```
  outcome unknown (504). request-id=req_… key=0192…
  Check:  sm fleets get --name edge-01
  Retry:  sm fleets create --name edge-01 --idempotency-key 0192…
  ```
- Document that exit code for CI authors.

### Long creates

A corporate proxy often times out at 30-60 s, sooner than the server. Make creates asynchronous: return `202` with the fleet in `provisioning` state right away, and add `--wait` to poll. That removes most of the 504 window.

## 8. Migration

1. On first run, `sm` detects `~/.sm/config` and `.smrc`, reads them as legacy, and warns.
2. `sm config migrate` **writes** the new `config.toml`, **moves** the token into the keychain, and **renames** the old file to `config.bak` with `mv`.
3. For `.smrc`, it removes the token and creates `.sm/project.toml`. It warns that the old token may be in git history and should be **rotated**.
4. Legacy support is read-only for two minor releases, then removed.

## 9. Tests that would have caught the incidents

- Run 8 processes refreshing in a loop against a fake server. Assert that the file always parses and that the server sees one refresh per expiry.
- Send `kill -9` during the credential write. Assert that the old file is intact.
- Run two profiles. Assert the banner, the org-pin abort, and the mutation guard in non-TTY mode.
- Make the fake server return a 504 after committing the create. Assert that the retry replays and exactly one fleet exists.
- Use a TLS-terminating proxy with a private CA, with and without `ca_bundle`.
- Set the pinned version to one the server doesn't support. Assert the error message.

## 10. Decisions I need from you

1. Are fleet names already unique per org? If not, enforcing uniqueness is a breaking server change, and we'd ship `--if-not-exists` plus idempotency keys first.
2. Can the server team add idempotency keys and a refresh reuse window? Both are server work.
3. Is `202` plus `--wait` acceptable for creates, or must `create` stay synchronous?
4. Is a one-release deprecation enough for token-in-`.smrc`, or do enterprise customers need longer?

**Suggested order:**
1. Atomic write, lock and credentials split. This is client-only, and it fixes the corruption.
2. Idempotency key, retry policy and exit code 75.
3. Profiles, banner and mutation guard.
4. API pin.
5. TLS tooling and `sm doctor`.