# Tollgate `tg` CLI: auth review and spec section

## Review of the lead's plan

Four of the five items fail the skill's secret-hygiene gate or its auth rules. Each has a replacement that keeps the intent.

| # | Lead's plan | Verdict | Problem | Replacement |
|---|---|---|---|---|
| 1 | `tg login --api-key tk_live_xxx` | ❌ Change | A live payments key in argv leaks into `ps` and shell history. The gate forbids any secret accepted only as a flag. | `tg login` uses a hidden prompt on a TTY, or `--with-key` reading stdin. There is no `--api-key` flag anywhere. |
| 2 | Plaintext `~/.tg/credentials` | ⚠️ Fallback only | An unencrypted live key on every laptop. | OS credential store first. Plaintext is a last resort: owner-only, warned, and opt-in off-TTY. Config follows XDG, not `~/.tg`. |
| 3 | `.tg.json` carrying the key | ❌ Reject | A committed live key. Teammates would share one identity, so revocation and audit become impossible. | `.tg.json` holds no secret. CI uses a secret-store env var. Teammates run `tg login` with their own key. |
| 4 | `tg auth token` prints the key | ❌ Drop for v1 | "Later integrations" is not a named integration. In s1ngularity (Aug 2025), malware ran `gh auth token` to harvest tokens at scale. | `TG_API_KEY` is the machine path. `tg auth status --json` gives a redacted identity. Revisit when a named integration needs a handoff. |
| 5 | `--verbose` prints full request headers | ❌ Change | The `Authorization` header is the key. CI logs keep it. This is the Azure CLI CVE-2023-36052 pattern. | `--verbose` and `--debug` redact the key by default. Bodies are not printed in verbose output. |

On item 2: SSH dev boxes usually have no keyring, so the plaintext fallback is the common path for that audience. The spec therefore makes the fallback safe instead of pretending it is rare.

## Assumptions (auth-relevant)

| Question | Answer or assumption | What it changes |
|---|---|---|
| Audiences | Laptops (majority, assumed), a few remote SSH boxes, CI. Assumed that CI and a live key leak hurt most, because this is a payments API. | Live-key handling is the strictest path. |
| Auth available | API keys only (`tk_test_…`, `tk_live_…`), no OAuth. No PKCE or device flow. | Both are marked "not available" in the table below. |
| Scoped or expiring keys | Assumed **not available** today. | Agent and CI hardening is limited to mode (test vs live) until the API ships scoped keys. This is a dependency. |
| Identity endpoint | Assumed none. | `login` and `auth status` need a "who am I" call (dependency D1). |
| Existing CLI | None shipped (assumed). | No migration from `~/.tg/credentials`. |
| EU or regulated users | Assumed yes (payments). | No secret or card data ever reaches telemetry or logs. |

## Auth

### Credential model

- A key's mode comes from its prefix: `tk_test_` or `tk_live_`. Any other prefix is rejected before any API call.
- A profile holds up to two stored keys, one per mode. The default profile is named `default`.
- **Default mode is test.** Stored-key commands use the test key unless `--live` is passed or `TG_MODE=live` is set. If only a live key is stored and `--live` is absent, the command fails with the auth-required exit code and the message "no test key stored; run `tg login` with a test key, or pass `--live`".
- **Env-key exception:** an explicit `TG_API_KEY` sets the mode by its prefix, so CI does not need `--live`. A `--live` flag combined with a `tk_test_` key is a usage error.
- Mode is shown in every login prompt, in `auth status`, and in the confirmation line of every severe action. Live mode also prints a one-line stderr banner on the first mutating call of a run.

### Flows by context

| Context | Flow | Token, scope, lifetime | Available now? |
|---|---|---|---|
| Laptop with a browser | `tg login` opens the dashboard keys page (URL: open item O1), then reads the key from a hidden prompt. | Static key, full account scope, no expiry. | ✅ |
| SSH or no-browser box | Same command. When no browser is detected, it prints the URL and reads the key from a hidden prompt or `--with-key` on stdin. | Same. | ✅ |
| CI and scripts | `TG_API_KEY` (or `TG_API_KEY_FILE=<path>`) from the CI secret store. No `login`, nothing written to disk. | Same today. A restricted, expiring key is the target. | ✅ env var; ⏳ scoped key (D2) |
| Coding agent | Env var `TG_API_KEY` holding a **test** key. | Same. A read-only key is the target. | ⚠️ test key only (D2) |
| Authorization code + PKCE | – | – | ❌ no OAuth server |
| Device grant (RFC 8628) | – | – | ❌ no OAuth server |

**Piped example, keeps the key out of argv:** `pass show tollgate/test | tg login --with-key`

### Commands

| Command | Behavior |
|---|---|
| `tg login [--with-key] [--profile <name>] [--live]` | **Writes a credential.** Reads the key from a hidden TTY prompt or from stdin with `--with-key`. Never accepts the key as a flag value. Verifies it with the identity call (D1) before storing. Prints mode and account. Off-TTY with no stdin key, it fails naming `--with-key`. |
| `tg auth status [--json]` | Shows account, mode, which source won (`env TG_API_KEY`, `env TG_API_KEY_FILE`, `keychain`, `file`), the key as prefix plus last 4 (`tk_test_…a1b2`), and storage backend. It also shows scope and expiry once the API returns them (D2). Calls the identity endpoint with a short timeout, and `--offline` skips that call. |
| `tg logout [--profile <name>] [--live\|--test\|--all]` | **Deletes the local credential.** It does not revoke the key server-side. The output says so and prints the dashboard revoke URL. |
| `tg auth token` | **Not shipped in v1.** Decision recorded in Open items (O2). |

Frozen `auth status --json` shape:

```json
{"profile":"default","mode":"test","source":"keychain","key":"tk_test_…a1b2",
 "account":{"id":"…","name":"…"},"storage":"keychain","scope":null,"expires_at":null}
```

`scope` and `expires_at` are `null` until D2 ships. Adding them later is additive.

### Precedence

1. The key: `TG_API_KEY` > `TG_API_KEY_FILE` > the stored profile key for the resolved mode. **There is no key flag.**
2. The profile: `--profile` > `TG_PROFILE` > `.tg.json` `profile` > `default`.
3. When an env key overrides a stored login, the CLI prints a stderr notice: `Using TG_API_KEY (live) instead of stored profile 'default'.` The notice appears only when a stored credential exists.
4. If both `TG_API_KEY` and `TG_API_KEY_FILE` are set, the CLI fails as a usage error instead of picking one silently.

### Storage

1. **OS credential store** (Keychain, Windows Credential Manager, Secret Service). The service name is `tg`, and the item name is `<profile>/<mode>`.
2. **Plaintext fallback** when no store is reachable. This is the likely case on SSH boxes.
   - Path: `$XDG_CONFIG_HOME/tg/credentials.json` (default `~/.config/tg/`; `%APPDATA%\tg\` on Windows). The directory is `0700` and the file is `0600`.
   - On a TTY, the CLI prints a warning naming the path and asks for confirmation.
   - Off a TTY, the CLI **fails** unless `--insecure-storage` is passed. It never prompts. The failure names the flag and suggests `TG_API_KEY` instead.
   - On read, if the file is more permissive than `0600`, the CLI refuses to use it and prints the `chmod` fix. This is the same behavior as `ssh` for private keys.
3. Writes take a file lock, because agents run commands in parallel.
4. The CLI never writes a key into the working directory, a project file, or a shell profile.

### `.tg.json` (project file, no secrets)

- Allowed keys: `profile`, `api_version`. The project file **cannot** select live mode.
- If any value matches `tk_(test|live)_…`, or the file contains a key such as `api_key`, `key` or `token`, the CLI aborts with a usage error. The error names the file and the offending key, never echoes the value, and tells the user to move it to `TG_API_KEY`.
- This is what teammates and CI get from cloning: a shared profile name and API version. Each teammate runs `tg login` with their own key, and CI injects `TG_API_KEY` from its secret store.

### Redaction and debug output

- Every output stream passes through one redactor that replaces `tk_(test|live)_[A-Za-z0-9]+` with `tk_<mode>_[redacted]`. This covers stdout, stderr, `--json` error objects, panic and crash output, and echoed user input in error messages.
- `--verbose` prints method, URL, status, request ID, timing, and headers with `Authorization` and `Cookie` redacted. It never prints bodies.
- `--debug` is the full HTTP trace. It uses the same redactor and also masks card-bearing body fields (PAN, CVC, expiry, bank account numbers) and webhook signing secrets. It prints a stderr notice that the trace may still contain customer data and should be reviewed before pasting into a ticket.
- Telemetry (see the Versioning section) never includes keys, key fragments, or body data.

### Agent handoff

- A confirmation prompt stops mistakes, not an agent that has decided to proceed, so the boundary is the key the agent holds.
- Document: give agents a `tk_test_` key in `TG_API_KEY`, never a live key.
- Once D2 ships, give agents a read-only, expiring key.
- Agents read `tg auth status --json` for a redacted identity check.

## API-side dependencies

| Need | Owner | Blocks |
|---|---|---|
| D1: identity endpoint returning account id and name, key mode, and scope (once scoped keys exist) | API team (open) | `login` verification, `auth status` |
| D2: scoped (read-only, resource-limited) and expiring keys, with key labels such as "created via CLI" | API team (open) | Safe agent and CI path, `auth status` scope and expiry |
| D3: register the `tk_live_` and `tk_test_` patterns with GitHub secret scanning and other scanner programs | Security (open) | Leak detection when someone commits a key anyway |
| D4: key creation, listing and revocation UI, with a stable deep link | Dashboard team (open) | `tg login` browser step, `logout` revoke hint |

## Open items

| Decision | Owner | Due |
|---|---|---|
| O1: dashboard keys-page URL for `tg login` | Dashboard team | Before v1 |
| O2: whether a named integration will need `auth token`. If yes, specify the safeguards first: TTY-only, mode shown, never in CI, and an audit note. Until then it stays out. | Lead and Security | When an integration is named |
| O3: whether the identity call (D1) is mandatory at login or skippable offline with `--no-verify` | CLI lead | Before v1 |
| O4: exit-code number for "authentication required". Proposed: 3, in the shared exit-code table. | CLI lead | Before v1 |

## Auth gates

- [ ] **Secret hygiene:** no code path accepts a key as a flag; a contract test plants `tk_live_CANARY…` and greps stdout, stderr, `--json`, `--verbose`, `--debug` and panic output for it, and the test must be able to fail (a positive control prints the canary un-redacted in a test build).
- [ ] **Non-interactive run:** `tg login` with stdin closed and no `--with-key` fails naming `--with-key`; plaintext fallback off-TTY fails naming `--insecure-storage`.
- [ ] **Exit-code test:** auth-required, usage error (secret in `.tg.json`, conflicting env vars), and the permission-too-open refusal each have an automated test.
- [ ] **Project file:** `.tg.json` containing a key-shaped value is rejected without echoing it.
- [ ] **Precedence test:** env key beats stored key, and the stderr notice appears only when a stored credential exists.

## Note on this deliverable

I read `SKILL.md` and its auth and spec-template references. I did not read the other reference files, so the exit-code number in O4 is a proposal. I also did not run any command. The dashboard URL, the API endpoints in D1 to D4, and the `chmod` and lock behavior are design decisions for you to confirm, not facts about Tollgate's current systems.