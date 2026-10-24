# Spec section: Versioning, updates and telemetry (`lq` 4.3)

**Status:** draft for PM and legal review. This is an engineering position, not legal advice.

## 0. Departures from the request

Two requirements are changed. Both would hurt the stated goals (60% EU customers, a third on self-hosted enterprise, open source).

| Request | Problem | What 4.3 ships |
|---|---|---|
| Telemetry on by default, disabled with `lq config set telemetry off` | A random device ID is pseudonymous personal data under GDPR. Reading and storing it on the user's machine and sending it out also falls under ePrivacy Art. 5(3), which generally requires prior consent. A line in the release notes is not consent, and most users never read them. | **Consent-based.** On first interactive run, `lq` shows a one-time prompt (§4.2). Until the user answers, nothing is sent. Non-interactive runs never send. |
| Update check on every invocation, with silent download and install | A network call on every command adds latency and fails offline. Silent binary replacement is a supply-chain attack surface and breaks CI and pinned enterprise setups. It also fights package managers. | **Check at most once per 24 h, in the background. Notify only.** Installing is explicit (`lq update`). Auto-install is opt-in and restricted (§3.4). |

The PM goal ("everyone stays current") is met by the nudge, a one-command `lq update`, and an opt-in auto mode. The telemetry goal (usage data) is met by consent-based collection. Expect lower coverage than opt-out, but the data is lawful and usable, and the CLI keeps the trust of an open-source audience.

## 1. Versioning

1. `lq` follows SemVer 2.0.0. 4.3.0 is a minor release: additive only, no removed flags, commands or exit codes.
2. The new `telemetry.*` and `update.*` config keys are additive. Existing configs keep working.
3. `lq version --json` outputs `{ "version", "commit", "build_date", "os", "arch", "install_method" }`.
4. `install_method` is one of `script | homebrew | apt | rpm | container | go-install | manual`. It is detected at build time or from the binary path. It gates §3.4.
5. **Support window:** the current minor and the previous minor receive fixes. Security fixes also go to the last minor of the previous major.
6. **CLI/server skew:** a CLI supports servers (including the self-hosted enterprise edition) at the same major, within one minor either side.
7. Outside that range, `lq` prints a warning once per day and continues. It never refuses to run.
8. Deprecations are announced one minor ahead with a stderr warning. Removal happens only in a major release.

## 2. Release channels

| Channel | Content | Default for |
|---|---|---|
| `stable` | Tagged releases | All installs |
| `lts` | Previous minor, security fixes only | Enterprise edition |
| `pinned` | A fixed version, never checked | Set by admin or env var |

- Config key: `update.channel`.
- Enterprise admins can set `update.channel`, `update.mirror_url` and `update.mode` in a system-level config file. System-level values override user-level ones.

## 3. Updates

### 3.1 Check

1. `lq` queries a signed manifest (`latest.json`: version, channel, per-platform URLs, hashes, signature). The query runs at most once per 24 h and the result is cached in the state dir.
2. The check runs in a background goroutine with a 2 s timeout. It never blocks, delays or fails the user's command.
3. The check sends no device ID and no telemetry. The request is a plain GET with `User-Agent: lq/<version> (<os>; <arch>)` and nothing else.
4. The privacy notice states that the request exposes the client IP to the manifest host.
5. If a newer version exists, print one line to **stderr** after the command completes:
   `lq 4.4.0 is available (you have 4.3.1). Run: lq update`
6. The nudge is shown at most once per 24 h and is suppressed when:
   - stderr is not a TTY;
   - `CI` is set;
   - `--quiet` is passed;
   - `--json` or another machine-readable output is active.
7. The check is skipped entirely when `update.mode=off`, `LQ_NO_UPDATE_CHECK=1`, `update.channel=pinned`, or an air-gapped config is detected (§5).

### 3.2 Install (`lq update`)

1. Download the artifact for the current OS and arch.
2. Verify the SHA-256 against the manifest, then verify the **signature** (cosign or minisign key embedded in the binary). Abort on any mismatch.
3. Replace the binary atomically (write temp file, `rename`). Keep the previous binary as `lq.prev`.
4. Smoke test the new binary with `lq version`. If it fails, restore `lq.prev` automatically.
5. `lq update --rollback` restores `lq.prev`. `lq update --check` only reports. `lq update --version X.Y.Z` installs a specific version.
6. Exit codes: 0 updated or already current, 10 update available (with `--check`), non-zero otherwise. Failures never leave a half-written binary.

### 3.3 Unsupported install methods

If `install_method` is `homebrew`, `apt`, `rpm`, `container` or `go-install`, `lq update` does not self-replace. It prints the right package-manager command instead. The nudge says the same.

### 3.4 Auto-update (opt-in)

- `lq config set update.mode auto` enables it. The default is `notify`.
- Auto mode installs at the next invocation after a successful check, using §3.2 in full.
- Auto mode **never** runs when any of these is true:
  - `CI` is set or the session is non-interactive;
  - `install_method` is not `script` or `manual`;
  - the new version is a different major (those need `lq update` plus the migration guide);
  - `update.channel=pinned`;
  - the binary path is not writable by the current user. There is no sudo escalation.
- Every auto-install prints a stderr line with old and new version and the rollback command.

## 4. Telemetry

### 4.1 Principles

- Nothing is collected without a recorded user choice.
- Only the fields in §4.3 are sent. The schema is public and enforced in code.
- `lq telemetry show` prints exactly what would be sent.

### 4.2 Consent flow

1. On the first interactive run after upgrading to 4.3, show once:
   ```
   Help improve lq? We'd like to send anonymous usage data:
   command names, lq version, OS, and a random device ID.
   Never arguments, file paths, hostnames, or output.
   Details: lq telemetry show   Docs: <privacy URL>
   Enable? [y/N]
   ```
2. The answer is stored as `telemetry.consent = granted | denied` with a timestamp and a notice version. The default answer is **N**.
3. Until `granted` is stored, nothing is sent and no device ID is generated.
4. Non-interactive runs (no TTY, `CI` set, or `--json`) never prompt and never send.
5. If the notice text or the §4.3 schema changes materially, the stored consent is invalidated and the prompt is shown again.
6. Controls:
   - `lq config set telemetry off|on`, equivalent to denying or granting.
   - `LQ_TELEMETRY=off` and `DO_NOT_TRACK=1` override everything and win over a stored `granted`.
   - `lq telemetry status | show | reset`. `reset` deletes the local device ID and generates a new one on the next granted send.
7. The enterprise edition ships with `telemetry=off` locked. An admin can only enable it through the system config file (§2). It never sends to our endpoint unless an admin sets one.

### 4.3 Data collected

| Field | Example | Notes |
|---|---|---|
| `device_id` | UUIDv4 | Random, stored locally, rotatable, never derived from hardware, user or hostname |
| `event` | `command_run` | One event type in 4.3 |
| `command` | `query`, `config set` | Command path only. Flag **names** are allowed (a fixed allowlist), never values |
| `cli_version` | `4.3.1` | |
| `os`, `arch` | `linux`, `arm64` | |
| `install_method` | `homebrew` | From §1 |
| `outcome` | `ok` or `error` | Error class only, never the message |
| `ts` | day granularity | Truncated to the date |

**Never collected:**
- arguments, flag values, queries, file paths, environment variables;
- hostnames, usernames, server URLs, API keys, org or tenant IDs;
- command output or error text;
- IP address (the ingest endpoint drops it before storage and does no geo-lookup).

### 4.4 Transport and handling

- HTTPS only. Batched, sent in the background with a 2 s timeout. Failures are dropped, with no retry queue on disk.
- Sending never changes exit codes, output or latency.
- Retention: raw events 90 days, aggregates 13 months.
- **Deletion:** a user can request deletion by device ID (`lq telemetry reset --delete-remote`). Because the ID is random, this is the only way to find their rows.
- The ingest endpoint and its storage are in the EU.
- Legal prerequisites before ship:
  - privacy notice published and linked from the prompt;
  - DPA and sub-processor list updated if a vendor receives the data;
  - lawful basis and ePrivacy analysis signed off by counsel.

### 4.5 Open source obligations

- The telemetry client code, the event schema and the privacy notice live in the public repo.
- The README and the 4.3 release notes describe telemetry, how to see the data, and how to turn it off. This supplements the prompt and does not replace consent.
- Telemetry sends nothing at build time or from `go test` (guarded by `LQ_TELEMETRY=off` in the test harness).

## 5. Air-gapped and enterprise behaviour

- If `update.mirror_url` is set, the check and download use it instead of our public host. The manifest signature is verified against the same embedded key.
- If the system config sets `update.mode=off`, no outbound connection to Lindqvist hosts is made by `lq` itself.
- Enterprise documentation lists every host `lq` may contact and under which setting.

## 6. Acceptance criteria

1. First interactive run after upgrade shows the prompt once. Declined or unanswered means zero telemetry requests (verified by a network-capturing test).
2. With `CI=1`, `DO_NOT_TRACK=1`, or `LQ_TELEMETRY=off`, no telemetry request is sent and the prompt is not shown.
3. No device ID file exists before consent is granted.
4. `lq telemetry show` output matches the bytes actually sent.
5. A fuzz/property test confirms no argument values, paths or hostnames reach the event payload.
6. The update check never adds more than 0 ms to command latency: it is async and cancelled on process exit.
7. With the manifest host unreachable, commands behave identically and exit codes are unchanged.
8. `lq update` rejects a tampered artifact (hash mismatch or bad signature) and leaves the existing binary intact.
9. A forced failure of the smoke test restores `lq.prev`.
10. Auto mode refuses to run in each §3.4 exclusion case (test per case).
11. Homebrew, apt and container installs never self-replace.
12. The enterprise build has telemetry locked off and makes zero outbound calls with `update.mode=off`.

## 7. Open decisions for the PM

1. **Consent prompt vs. a no-prompt alternative.** An opt-out default for non-EU users only is not reliable, because the CLI cannot know the user's jurisdiction. Recommendation: one global consent prompt.
2. **Auto-update default.** Recommendation: `notify` for everyone and `auto` as an opt-in. If the PM insists on auto by default, limit it to patch releases on `script` installs, outside CI, outside enterprise.
3. **Coverage expectation.** Plan product decisions around consented telemetry (a sample, likely a minority of users), not around full-population counts. Download counts and the update-check hit rate are separate, consent-free signals for rough adoption.
4. **Timing.** The signing key, manifest host and `install_method` detection are prerequisites for §3. If they are not ready next sprint, ship the nudge (§3.1) and consent-based telemetry in 4.3, and `lq update` in 4.4.