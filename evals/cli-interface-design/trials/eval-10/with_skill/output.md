# Saltmarsh `sm` design spec v0.1: configuration, profiles, create path

Scope: the three incidents. The spec covers configuration, profiles, credential storage and concurrency, and `fleets create`. It leaves out the command tree, `--json` coverage beyond these paths, and telemetry. Those need the interview answers below.

## Assumptions

You didn't answer the skill's clarifying questions, so each assumption below is mine and says what it changes. Please correct any that are wrong.

| Question | Assumption | What it changes |
|---|---|---|
| Audiences | Enterprise CI is the audience that breaks the business. Developers and coding agents follow. | Machine-safe defaults come before prompts. |
| Auth | OAuth-style login gives a short-lived access token and a refresh token. CI tokens are scoped and expiring. | The refresh lock matters. `SM_TOKEN` never refreshes. |
| Token and region | Each org lives in exactly one region (us, eu or apac). A token works only against that region's API. | The profile binds the token to a base URL. |
| Create | `POST /fleets` is asynchronous (provisioning), and names are not unique today. | Wait defaults apply. A name-uniqueness backstop is an API dependency. |
| Idempotency | The API accepts an `Idempotency-Key` header. This is not confirmed. | The create path depends on it. See API dependencies. |
| Existing CLI | `~/.sm/config`, `.smrc` and `SM_TOKEN` are in customer scripts. | They are deprecated with a window, not removed. |
| Platform | macOS, Linux and Windows. | Config paths and the keychain differ per OS. |

## Answer to the requester

You asked for a fix for three incidents. The root causes are not three bugs.

- **Wrong org, no indication.** A token in `.smrc` or `SM_TOKEN` silently beat the logged-in account, and the CLI never said whose account it was using.
- **Truncated config.** The token refresh rewrote the same file that holds user settings, and there was no lock.
- **Duplicate fleet.** The create call had no idempotency key, so the CI rerun looked like a new request.

The design below does four things:

- It separates settings from secrets.
- It makes profile selection explicit and always visible.
- It serializes refresh behind a lock and an atomic write.
- It gives every create call a stable idempotency key, and it reports an unknown outcome as its own exit code.

## Configuration

**Precedence** (one order, documented in `sm help config`): flag > environment variable > project file > user config > built-in default. This applies to every setting. An explicit token follows the same rule (see Credentials).

**Files**

| File | Holds | Never holds |
|---|---|---|
| User config: `$SM_CONFIG_DIR`, else `$XDG_CONFIG_HOME/sm/config.toml`, else `~/.config/sm/config.toml` (Windows: `%APPDATA%\sm\config.toml`) | Profiles (non-secret) and `default_profile` | Tokens |
| Credential store: the OS keychain, one entry per profile (`sm:<profile>`) | Access token, refresh token, expiry | Settings |
| Credential fallback: `<state dir>/credentials/<profile>.json`, mode 0600 | Same as the keychain entry, only when no keychain exists | Settings |
| Project file: `.sm.toml` in the repo (found by walking up from the current directory) | `profile = "<name>"` and non-secret defaults such as `output` | Tokens, `api_url`, CA bundle, proxy |

**Why the project file is so narrow.** A cloned repo is untrusted. If `.sm.toml` could set `api_url`, a hostile repo could send your token to its own server. It can only name a profile, and that profile must already exist on this machine.

**Environment variables.** One prefix, and each has a flag.

| Env var | Flag | Meaning |
|---|---|---|
| `SM_PROFILE` | `--profile` | Select a profile. |
| `SM_TOKEN` | none | Explicit token. A flag is not allowed (leaks via `ps`). Stdin is supported by `sm auth login --with-token`. |
| `SM_API_URL` | `--api-url` | Base URL for an ad hoc target. |
| `SM_REGION` | `--region` | `us`, `eu` or `apac`. Resolves to the standard base URL. |
| `SM_API_VERSION` | `--api-version` | Override the pinned API version. |
| `SM_CA_BUNDLE` | `--ca-bundle` | Extra CA certificates (PEM). |
| `SM_CONFIG_DIR` | none | Config location. |
| `SM_NO_INPUT` | `--no-input` | Never prompt. |

**Rules for `SM_TOKEN`.**

- With `SM_TOKEN`, the CLI needs a target: `SM_PROFILE`, `SM_REGION` or `SM_API_URL`.
- If it finds none, it exits 2 and names the missing setting. It does not guess a region.
- With `SM_TOKEN` set, the CLI writes nothing to disk and never refreshes. This is the recommended mode for CI and for coding agents.
- If `SM_TOKEN` overrides a logged-in profile, the CLI prints one stderr notice: `using SM_TOKEN, ignoring logged-in profile acme-eu`.

**Network (enterprise)**

- Trust the OS certificate store by default. Corporate re-signing CAs are installed there.
- Also honor `SM_CA_BUNDLE`, `SSL_CERT_FILE`, `HTTPS_PROXY`, `HTTP_PROXY` and `NO_PROXY`.
- There is no `--insecure` flag. TLS verification stays on.
- On a certificate failure, the CLI names the issuer it saw and the knob to set. Example: `TLS: certificate signed by "Acme Corp Proxy CA", not trusted. Set SM_CA_BUNDLE or install the CA in the OS store.`
- `sm doctor` checks DNS, proxy, TLS chain, API version support and auth against the selected profile, and prints the winning source for each setting.
- `sm config explain <key>` shows the value and which layer won.

**API version**

- Each `sm` release is pinned to one API version. It sends that version on every request.
- A profile can override it (`api_version`), for self-hosted installs that lag.
- If the server does not support the pinned version, the CLI fails before any mutation. The message names the server's supported versions and says to upgrade `sm` or set `--api-version`.
- `sm auth status` shows the API version.

**Migration from the old files**

- `~/.sm/config` and `.smrc` stay readable for 12 months or 2 minor releases, whichever is longer. Removal happens only in a major release.
- Every run that reads them prints a stderr deprecation warning naming the replacement.
- A token found in `.smrc` is treated as a stored token, below env and above the user profile. It triggers the override notice, so it can no longer win silently.
- `sm config migrate` is the only command that writes during migration. It moves the token into the credential store, creates a profile, and writes `.sm.toml`. It tolerates a truncated legacy file: it reports what it could not parse and does not overwrite.
- It then offers to move the legacy file to `*.migrated`. It never deletes. This is a moderate action: it confirms on a terminal and takes `--yes` otherwise.

## Profiles

A profile is a named tuple: base URL (or region), org identity, API version and CA bundle. Credentials are stored separately, keyed by profile name.

```toml
default_profile = "acme-eu"

[profiles.acme-eu]
region = "eu"                      # resolves to the standard base URL
org_id = "org_8f2"                 # cached at login, refreshed by `sm auth status`
org_name = "Acme GmbH"

[profiles.globex-selfhosted]
api_url = "https://fleet.globex.internal"
ca_bundle = "/etc/ssl/globex-ca.pem"
api_version = "2025-09-01"
```

**Commands** (noun verb, frozen)

- `sm profiles list|get|create|delete|rename|use`
- `sm auth login --profile <name> [--region|--api-url]`
- `sm auth status`
- `sm auth logout [--profile <name>]`

`sm profiles use <name>` sets `default_profile`. `delete` removes the stored credential and is moderate.

**Selection order**: `--profile` > `SM_PROFILE` > project `.sm.toml` > `default_profile`.

**Guards against the "other customer's org" incident**

1. **No implicit choice among several.** If two or more profiles exist and none was selected by any of the four sources, the CLI exits 2 and lists them. A single profile is selected without ceremony.
2. **A context line on every run.** The CLI prints one stderr line with profile, org name and id, region and the source that won. Example: `-> acme-eu | Acme GmbH (org_8f2) | eu | from .sm.toml`.
   - Mutating commands always print it, including in CI and with `--json`.
   - Read commands print it on a terminal.
   - It comes from the cached identity, so it adds no latency.
3. **`default_profile` is a visible choice.** Confirmation prompts on a terminal name the org. `sm auth status` shows the source of the selection and warns when it came from `default_profile` while other profiles exist.
4. **Mutating results name the org.** Their `--json` output includes `org_id`, so a script can assert it.
5. **Each region has its own profile.** A profile never changes region silently. `--region` conflicting with the profile's region is a usage error (exit 2).

## Credentials and concurrent refresh

This is the fix for the truncated config. The cause was that every process rewrote one shared file with no coordination.

**Rules**

- Refresh writes only the credential entry for that profile. It never touches `config.toml`.
- Reads need no lock, because writes are atomic.
- Every file write uses a temp file in the same directory, `fsync`, then `rename`. The keychain write is a single call.
- The file fallback is 0600 and prints one warning when first written, naming the path. Nothing is written to the project directory.

**Refresh algorithm** (per profile)

1. Read the credential. If the access token is valid for more than 60 seconds (clock-skew margin), use it. No lock.
2. Otherwise take an exclusive advisory lock on `<state dir>/credentials/<profile>.lock`. It is an OS file lock, so a crashed process releases it. No PID files.
3. Re-read the credential. If another process refreshed in the meantime, use that and skip the network call.
4. Call the refresh endpoint with an HTTP timeout of 10 seconds. Write the result atomically. Release the lock.
5. Wait for the lock at most 30 seconds (three times the HTTP timeout, so a slow refresh by another process can finish). On timeout, exit 5 with code `credential_lock_timeout`. Nothing was sent, so it is safe to rerun.
6. If the refresh is rejected (`invalid_grant`) and the credential did not change, exit 4: `run sm auth login --profile <name>`.
7. A credential file that fails to parse is never overwritten. The CLI moves it aside as `*.corrupt-<timestamp>`, exits 4, and says so.

**Four parallel agents** therefore cause exactly one refresh call and no write races. Still, give agents `SM_TOKEN` with a scoped, expiring service token. It involves no disk writes and no refresh, and it bounds what an agent can do.

## The create path: `sm fleets create`

```
sm fleets create --name edge-01 [--description ...] [--idempotency-key <key>]
                 [--wait|--no-wait] [--wait-timeout 5m] [--dry-run] [--json]
```

**Behavior**

1. **Key per invocation.** The CLI generates a random idempotency key and sends it as `Idempotency-Key`. It reuses that key on every automatic retry of the same invocation.
2. **Automatic retry.** Up to 3 retries on connection errors before send, 429, 503 and 504, with backoff of 1 s, 2 s and 4 s plus jitter. It honors `Retry-After`. The key makes the retry safe: a 504 after the server created the fleet returns the original result on retry, marked as a replay. A 409 `idempotency_in_progress` is retried like a 503.
3. **Caller-controlled key.** `--idempotency-key` accepts the caller's own key. It is a flag only; there is no env var. An env var would apply to every `sm` call in a script and break "one key per operation".
4. **Printed key.** The key used appears in the `--json` output and in every error, so a rerun can reuse it.
5. **Async create.** By default the CLI waits for provisioning, with progress on stderr and a default `--wait-timeout` of 5 minutes (my assumption for provisioning time; confirm with the API team). `--no-wait` returns the operation id. `sm operations wait <operation-id>` resumes. Ctrl-C or SIGTERM detaches and prints the operation id and the resume command (exit 130 or 143). It does not cancel server-side work.
6. **`--dry-run`** validates the name and permissions without creating anything, where the API supports it.

**Exit codes for create**

| Situation | Code | Why |
|---|---|---|
| Created, or replay of the same key and payload | 0 | An idempotent replay is success. |
| Usage error, such as a missing `--name` | 2 | Never retry. |
| Authentication required or expired | 4 | Re-authenticate. |
| 429 or 503 with `Retry-After` after the retries are used up, or a connect error before send | 5 | Nothing was created, or the key makes a rerun safe. |
| 5xx or timeout after send, retries exhausted, key generated by the CLI | 6 | The outcome is unknown. The CLI's key is gone when it exits, so a blind rerun can duplicate. |
| 5xx or timeout after send, retries exhausted, caller supplied the key | 5 | The caller's own key makes the rerun safe. |
| Name already exists (409 `fleet_name_taken`) | 1 | Business conflict. Not retryable. |
| Same key reused with a different payload (422 `idempotency_key_reused`) | 1 | A caller bug. |

On exit 6, the error text says: check `sm fleets get edge-01`, or rerun with `--idempotency-key <the key printed>`.

**CI guidance** (published as a docs recipe):

```
sm fleets create --name edge-01 --idempotency-key "$CI_PIPELINE_ID-edge-01" --json
```

Retry the job only on exit 5. On exit 6, run `sm fleets get edge-01` first. The key must be stable across job retries within a pipeline and must differ between pipelines.

**The CLI alone cannot fully fix this.** If a customer's wrapper retries on every non-zero exit without its own key, a 504 can still produce a duplicate. The backstop is the API: fleet names must be unique per org (409 on a duplicate), which turns the second create into a conflict. This is the first API dependency below.

**JSON shape of a create result** (frozen, additive only):

```json
{
  "operation_id": "op_9",
  "state": "succeeded",
  "idempotency_key": "k_3c1",
  "replayed": false,
  "org_id": "org_8f2",
  "result": {"id": "flt_41", "name": "edge-01"}
}
```

## Severity table (rows relevant to this spec)

| Command or method + path | Grade | Terminal | Non-interactive |
|---|---|---|---|
| `fleets create`, `POST /fleets` | mild | none | none |
| `profiles use`, `profiles create` | mild | none | none |
| `profiles delete`, `auth logout`, `config migrate` | moderate | confirm | `--yes` |
| `fleets delete`, `DELETE /fleets/{id}` (through `sm api` too) | severe | type the fleet name | `--confirm=<name>` |

## API-side dependencies

| Need | Owner | Blocks |
|---|---|---|
| `Idempotency-Key` support, retained at least 24 hours, replay returns the original result, a different payload returns 422 | API team | `fleets create` safety |
| Fleet names unique per org (409 `fleet_name_taken`) | API team | The backstop for unkeyed retries |
| Refresh-token rotation with a reuse grace window of about 60 seconds (or non-rotating refresh tokens) | Auth team | The lock covers one machine, not two machines sharing a token |
| Scoped, expiring service tokens for CI and agents | Auth team | The `SM_TOKEN` recommendation |
| Token or key prefix that encodes the region (such as `sm_eu_`) | Auth team | Optional. Lets the CLI infer the region and drop the "need a target" error. |
| Operation status endpoint and `Retry-After` on 429 and 503 | API team | `wait` and the retry classification |
| `GET /version` listing supported API versions (self-hosted too) | API team | The pre-flight version check |

## Release cut line

| Capability | v1 | Later | Reason |
|---|---|---|---|
| Profiles, `.sm.toml`, `SM_*` env, precedence, context line | yes | | These fix the wrong-org incident. |
| Credential store, lock and atomic write | yes | | These fix the truncation incident. |
| Create path with key, retries, exit codes | yes | | These fix the duplicate incident. |
| `config migrate`, legacy deprecation warnings | yes | | Needed to move existing customers. |
| `sm doctor`, `config explain` | yes | | Cheap, and they cut enterprise TLS and proxy support load. |
| Device-code login for SSH boxes | | yes | Separate auth design pass. |
| Generated per-endpoint layer | | yes | Out of scope here. |

## Open items

| Decision | Owner |
|---|---|
| Confirm the idempotency, name-uniqueness and refresh-grace dependencies | API and auth teams |
| Confirm provisioning time to set `--wait-timeout` | API team |
| Confirm "one org per region, token bound to a region" | Auth team |
| Deprecation window length for `~/.sm/config` and `.smrc` (12 months proposed) | Product |

## Gates

- [ ] **Contract coverage:** `fleets create` and `profiles list|get` have `--json` and a published JSON Schema. The frozen list is published.
- [ ] **Non-interactive run:** with stdin closed, no command hangs. No profile selected and several profiles exist means exit 2, naming `--profile`. Every wait is bounded.
- [ ] **Exit-code table tested:** one automated test per code. Specific cases: 504 with a CLI key gives 6, 504 with a caller key gives 5, lock timeout gives 5, corrupt credential gives 4.
- [ ] **Severe-action guard:** `fleets delete` and `sm api DELETE /fleets/...` both need `--confirm=<name>`.
- [ ] **Secret hygiene:** no token accepted as a flag. Nothing printed in default, verbose or `--debug` output. The project file cannot hold a token.

## Tests to write first

- **Concurrency:** run 8 processes with an expired access token against one profile. Exactly one refresh request reaches the server, and the credential parses afterward. Kill one process mid-write and check the file stays valid.
- **Create retry:** a mock server answers 504 after creating the fleet. The retried request returns the original result (replay) and the exit code is 0. With retries exhausted, check exit 6 with a CLI key and exit 5 with a caller key.
- **Selection:** two profiles, no selection, exit 2. `SM_TOKEN` plus a logged-in profile prints the override notice. A hostile `.sm.toml` containing `api_url` is ignored with a warning.