# Review of the lead's plan

I'd ship about half of it as drafted. Each point below gives the verdict and the replacement.

| Item in the draft | Verdict | Why | Replacement |
|---|---|---|---|
| `tg login --api-key tk_live_xxx` | ❌ Change | The key lands in shell history, `ps` output, and CI logs. | Read the key from a hidden prompt or from stdin. Accept no key value as a flag. |
| Plaintext `~/.tg/credentials` | ⚠️ Keep with conditions | SSH dev boxes have no keychain, so a file fallback is needed. The draft sets no permissions. | Use the OS keychain when available. Otherwise use a `0600` file in a `0700` directory, and refuse to read it if it is looser. |
| `.tg.json` carrying the key | ❌ Drop | Cloning the repo then hands everyone the key, and the repo history keeps it forever. A `tk_live_` key in git is a payment-account incident. It also makes all teammates share one identity, so a leak can't be traced to a person. | `.tg.json` may hold non-secret settings only. The CLI refuses a file containing anything shaped like a key. CI uses `TG_API_KEY` from the CI secret store. |
| `tg auth token` prints the key | ❌ Cut from v1 | It makes the CLI a key-dispensing tool, since any script or pasted terminal log can then extract the live key. The "later integrations" case doesn't exist yet. | Ship `tg auth status` (masked). Integrations use `TG_API_KEY`. Revisit with a credential-helper protocol when a real integration exists. |
| `--verbose` prints full headers | ❌ Change | The `Authorization` header is the key. People paste verbose output into tickets and chat. | Redact secrets in all debug output, always. |

Four gaps the draft does not cover:
- **Live vs test.** A live key on a laptop can move real money. The CLI needs a visible mode and a guard on destructive live calls.
- **Key validation.** Without a check at login, a typo is stored silently and fails later.
- **Redirects and base-URL override.** An overridden API URL or a cross-host redirect can send the key to a third party.
- **Revocation.** `logout` only deletes the local copy. Users must know the key stays valid until revoked in the dashboard.

---

# Spec: Authentication

## 1. Scope and constraints

- Tollgate has API keys only: `tk_test_…` and `tk_live_…`. There is no OAuth server, so no browser flow and no refresh tokens.
- Keys are long-lived bearer secrets. Possession equals full access, so the CLI limits where the key is stored, printed, and sent.
- Three user contexts must work:
  1. Developer laptop with a keychain.
  2. Remote SSH dev box with no browser and possibly no keychain.
  3. CI, non-interactive.

## 2. Credential sources and precedence

The CLI resolves the key in this order and stops at the first hit:

1. `TG_API_KEY` environment variable.
2. Stored credential for the active profile (keychain, then file).
3. Nothing found: exit code `3` with a message naming `tg login` and `TG_API_KEY`.

Rules:
- No `--api-key` flag exists on any command. A flag value leaks via shell history and process listings.
- `.tg.json` is never a credential source (see §5).
- When `TG_API_KEY` is set, the CLI never reads or writes stored credentials. This keeps CI runs hermetic.
- `tg auth status` shows which source supplied the key.

## 3. Commands

| Command | Behavior |
|---|---|
| `tg login` | Interactive. Prompts for the key with echo off. Works over plain SSH because it needs only a TTY. |
| `tg login --with-api-key` | Reads the key from stdin. For scripted setup, e.g. `pass show tollgate/key \| tg login --with-api-key`. |
| `tg login --profile <name>` | Stores under a named profile. Default profile is `default`. |
| `tg logout [--profile <name>]` | Deletes the stored key. Prints: "Key removed locally. It remains valid until you revoke it in the dashboard." |
| `tg auth status` | Prints profile, mode (`test`/`live`), masked key (`tk_live_…a1b2`), source, and the account name from the API. Never prints the full key. |

`tg login` steps:
1. Check the prefix. Anything other than `tk_test_` or `tk_live_` is rejected before any network call.
2. Call a read-only whoami endpoint, `GET /v1/account`, over HTTPS.
3. Store the key only on a 2xx response. A 401 stores nothing and exits `3`.
4. On a network error, store nothing and say why. `--no-verify` is available, with a warning that the key is unchecked.
5. For a `tk_live_` key, print: "Live key stored. Commands will affect real money." Prefer test keys on laptops.

`tg login` is refused when `CI=true` or when no TTY and no `--with-api-key` is given. CI must use `TG_API_KEY`.

## 4. Storage

Order of preference:
1. **OS keychain** (macOS Keychain, Windows Credential Manager, Secret Service on Linux). Service name `tg`, account name = profile.
2. **File fallback** when no keychain is reachable, which is the usual case on SSH boxes. The path is `~/.tg/credentials`, overridable by `TG_CONFIG_DIR`.

File requirements:
- Directory mode `0700`, file mode `0600`, set at creation with `umask 077`. Write via temp file plus atomic rename.
- On read, if the file is group- or world-readable, or owned by another user, the CLI refuses to use it. It exits `3` with the exact `chmod` fix. It does not silently tighten permissions.
- Format: TOML or JSON, one table per profile. It never contains anything except keys and the profile name.
- The first fallback write prints once: "No keychain found. Key stored in `~/.tg/credentials` (mode 600)."
- On Windows, apply an ACL equivalent restricted to the current user.

## 5. Project file `.tg.json`

Allowed (non-secret): `profile`, `default_currency`, `webhook_endpoint_ids`, `api_version`.

Forbidden: any credential.

- At load, the CLI scans every string value for `tk_(test|live)_`. On a match it exits `2` and names the file and field but does not echo the value.
- `tg init` writes `.tg.json` and adds nothing secret. If a `.gitignore` exists, it also offers to add `.tg/`.
- Teammates each run `tg login` with their own key. CI sets `TG_API_KEY` from its secret store. This gives per-person attribution and per-person revocation.

## 6. Test and live safety

- Every command that makes API calls prints a mode line to stderr when the key is live: `[live] acct_name`. Test mode prints nothing, so the live line stands out. `--quiet` suppresses it.
- State-changing commands (refunds, payouts, deletes, any POST/DELETE) with a live key require `--yes` or an interactive confirmation. In non-interactive use without `--yes`, they fail with exit code `4`.
- `tg auth status` and a `tg login` warning are the only places mode is explained. Don't add more.

## 7. Secret hygiene

MUST:
- **Redaction.** The `Authorization` header value is always replaced with `Bearer tk_live_…a1b2` (prefix plus last 4). This applies to `--verbose`, `--debug`, error output, and crash reports. Redaction runs at the HTTP client layer, not per call site.
- **Body scrubbing.** In verbose output, request and response body fields named `api_key`, `secret`, `token`, or `card[number]` are replaced with `[redacted]`.
- **No telemetry of keys.** Telemetry, if any, never includes key material, including the masked form.
- **No keys in URLs.** The key travels only in the `Authorization` header.
- **Transport.** HTTPS only. A base-URL override (`TG_API_URL`) must be `https://`, or `http://` to `localhost`/`127.0.0.1`. When the override points at a non-Tollgate host, the CLI warns before sending the key.
- **Redirects.** The `Authorization` header is stripped on any redirect to a different host.
- **No dispensing.** No command prints the full key. This includes `tg auth token`, which is not part of v1.

SHOULD:
- `tg auth status --json` carries the same masked data, for scripts.
- `tg doctor` flags a loose credentials file, a key found in `.tg.json`, and a live key on a machine whose hostname looks like CI.

## 8. Exit codes

| Code | Meaning |
|---|---|
| 0 | Success |
| 2 | Invalid usage, or a key found in `.tg.json` |
| 3 | No credential, invalid credential, or unsafe credentials file |
| 4 | Live confirmation required in non-interactive mode |

## 9. Acceptance tests

Each test must be able to fail, so pair every negative check with a positive control.

1. `tg login --api-key x` fails as an unknown flag. A positive control confirms `tg login --with-api-key` works.
2. A `.tg.json` containing `tk_test_abc` exits `2`. The same file without the key loads.
3. A credentials file at mode `0644` is refused. The same file at `0600` is accepted.
4. `--verbose` against a mock server shows the redacted header. The raw key appears nowhere in stdout or stderr, checked by grepping the full capture. A control run confirms the mock received the full key.
5. With `TG_API_KEY` set, the credentials file is unread and unwritten, checked by file mtime and absence of open calls.
6. A cross-host redirect arrives at the mock second host with no `Authorization` header.
7. A live-key `POST` with no TTY and no `--yes` exits `4`. With `--yes` it succeeds.
8. `tg login` with a 401 from the mock stores nothing. The previous stored key is unchanged.
9. `tg logout` removes the key and prints the revocation notice.

## 10. Open questions for the API team

- **Restricted keys.** Can the dashboard issue keys limited to read-only or a scope, or to specific operations? This is the biggest safety win available without OAuth.
- **Expiry.** Can keys be given an expiry date, so a forgotten key on a dev box dies?
- **Whoami endpoint.** Does `GET /v1/account` exist and work with every key type, including restricted ones?
- **Leak scanning.** Register the `tk_live_` prefix with GitHub secret scanning so committed keys are reported to Tollgate and can be auto-revoked.
- **Future integrations.** If a real consumer of the stored key appears, design a credential-helper protocol (like Docker's or git's) instead of reviving `tg auth token`.