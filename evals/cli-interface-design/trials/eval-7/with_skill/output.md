# Lindqvist Observability `lq`: Versioning, updates and telemetry (spec section, target 4.3)

I read `cli-interface-design` (step 11 and its references). This section departs from the PM's request in two places and keeps the rest. I did not ask the clarifying questions, so the assumptions below are mine.

## Answer to the PM

| Request | Verdict | What ships in 4.3 |
|---|---|---|
| Telemetry on by default, announced only in 4.3 release notes | ❌ Not in a minor release. 60% of customers are in the EU, and `lq` is open source. | Telemetry ships **opt-in**, with a one-time consent prompt on a terminal. |
| Update check on every invocation | ⚠️ Changed to at most once per 24 h. | A cached, non-blocking check, on a terminal only. It prints a notice and never runs in CI. |
| Auto-download and install of the new binary | ❌ Not by default. | An explicit `lq update` command. Unattended install is a separate opt-in, and only within the same major version. |

**Why not default-on telemetry.** A random device ID collected by default is a consent question under EU rules. Opt-in carries consent by construction. GitHub CLI did default-on telemetry in a minor release (v2.91.0, April 2026), with only release notes and docs as notice. It drew press and community backlash even though it was documented and switchable. Release notes are not notice for an open-source CLI whose users are mostly in the EU.

**Why not install on every invocation.** A binary that replaces itself breaks pinned CI images and reproducible builds. For the self-hosted third of customers, it can also move the CLI out of the version range their server supports. Only a user's explicit action, or an explicit opt-in, can move the binary.

**What the PM still gets.** A legitimate signal path, plus a documented route to opt-out by default. That route needs a major version and advance notice (see the telemetry section below). It is a growth question for the PM, and a legal question for your DPO.

## Assumptions

| Question | Assumption | What it changes |
|---|---|---|
| 7. Where do users sit? | 60% EU, about 33% self-hosted enterprise, open-source community. | Opt-in rung instead of opt-out. No collection or update check against self-hosted targets. |
| 6. Does a CLI ship today? | Yes, 4.2.0. Customer scripts parse flags and `--json`. | The frozen list applies. Config key `telemetry` is added, and nothing existing is renamed. |
| 1. Who runs it? | Developers, CI and agents. | Every notice is silent off-TTY. CI never collects or checks. |
| Distribution | Release binaries, Homebrew and deb/rpm already exist. | Package-manager installs update through the package manager. `lq update` refuses and prints the right command. |
| Server compatibility | The self-hosted edition lags the SaaS API by one or more minors. | The CLI pins an API version, and updates never raise it silently. |
| Legal | Not a lawyer's review. | Open item: DPO sign-off on the payload and the consent text before 4.3 ships. |

## Versioning

- **SemVer for the CLI, separate from the API.** 4.3.0 is a minor release: additive changes only. Anything that removes or changes a frozen element waits for 5.0.
- **Pinned API version.** Each CLI release carries one default API version, shown in `lq version --json` as `api_version`. Override with `--api-version <v>` or `LQ_API_VERSION`.
- **Self-hosted targets.** On a profile with a custom `base_url`, the CLI reads the server's version and warns on stderr when the server is outside the supported range. It never bumps the API version silently.
- **Frozen surface.** Command names, flags, env vars, config keys, `--json` shapes, exit codes and stream rules. Human tables, wording and colors are unstable, and the docs say so. 4.3 adds only: `lq update`, `lq telemetry`, and the config keys `telemetry` and `update.check`. Nothing is renamed.
- **Deprecation policy.** Warn on stderr naming the replacement. Keep an alias for the longer of 12 months or 2 minor releases, and remove it only in a major release. A security fix may be breaking, as long as the release notes say so.
- **`lq version --json`:** `{"version","commit","api_version","build_date","install_method"}`. `install_method` is one of `brew|deb|rpm|binary|go-install`, and it decides which update command the notice suggests.

## Update checks

| Rule | Value | Reason |
|---|---|---|
| Frequency | At most once per 24 h, cached in the state dir. | Every invocation adds network latency and a phone-home to every script. |
| Where | Only when stdout and stderr are terminals. Never in CI (`CI` set) or with `--no-input`. | An update hint in a pipeline is noise at best and a hang at worst. |
| Blocking | Never. Check in the background with a 2 s timeout. Show the result on the next invocation. | A slow or filtered network must not slow a command. |
| Output | One stderr line: `lq 4.4.0 is available (you have 4.3.0). Run: brew upgrade lq`. | Stdout and `--json` stay clean. The suggested command matches `install_method`. |
| Request | A GET of a static, signed version manifest. No device ID, no identifiers. | The check must not become a telemetry channel. |
| Off switches | `LQ_NO_UPDATE_CHECK=1`, `lq config set update.check off`, or `--no-update-check`. | One documented switch per context. |
| Self-hosted / air-gapped | Off when the active profile has a custom `base_url`. Optional `update.manifest_url` points at an internal mirror. | Enterprise networks block outbound calls, and a surprise outbound request is a security finding. |
| Major versions | The notice names a new major, but `lq update` never installs one without `--major`. | Majors may break scripts. |

### `lq update`

- **Explicit command.** It downloads from the release host, verifies the checksum and the signature (cosign or minisign, per the signing setup in `sdk-package-publishing`), and replaces the binary atomically. It keeps the previous binary for `lq update --rollback`.
- **Package-manager installs.** It refuses, prints the exact package-manager command, and exits `2`.
- **Flags.** `--check` (report only, exit `0` whatever the answer, `--json` supported), `--version <v>` (pin a version, so downgrades work), and `--yes` for the moderate confirmation.
- **Failure.** Signature or checksum failure leaves the old binary in place and exits non-zero. It never falls back to an unverified download.
- **Unattended install (not in 4.3 by default).** `lq config set update.auto minor` enables it. It is an explicit consent and applies only to minor and patch releases within the current major. It never runs in CI, never against a self-hosted profile, and never mid-command (it applies at the next start). Ship it in 4.4 or later if demand appears.

## Telemetry

### Posture

| | 4.3 (this sprint) | Candidate for 5.0 |
|---|---|---|
| Default | **Off until the user says yes.** | Opt-out with first-run notice, only if the DPO approves and the PM still wants it. |
| Consent | One prompt on a terminal at first run after the upgrade. `Help improve lq by sharing anonymous usage data? [y/N]` with a link to the payload schema. | First-run notice, plus a 4.3/4.4 announcement at least one release before it takes effect. |
| Off a terminal | No prompt. Telemetry stays off. | Same. Never collect in CI. |
| Answer storage | `telemetry = on\|off` in the user config. Re-asked never. | Same. |

Opt-in is the right rung for this audience because 60% EU, regulated enterprise buyers and an open-source community all point the same way. The cost is lower coverage, and you should expect a minority of users to opt in. Treat the data as a sample, not a census. Report it with that caveat.

The decision to move to opt-out for 5.0 is the PM's, with the DPO. It does not need to block 4.3.

### Never collected

- Self-hosted or enterprise targets: any profile with a custom `base_url`.
- CI environments (`CI`, `GITHUB_ACTIONS`, `GITLAB_CI` and similar) and non-terminal runs.
- Anything when `DO_NOT_TRACK=1` or `LQ_TELEMETRY=off` is set. Those override the config value.

### Payload (one event per invocation)

| Field | Example | Notes |
|---|---|---|
| `device_id` | random UUIDv4 | Generated at opt-in. Not derived from hardware, hostname, user or account. |
| `cli_version` | `4.3.0` | |
| `os`, `arch` | `linux`, `arm64` | |
| `command` | `logs tail` | Command path only. No arguments, no flag values, no flag names, no paths, no queries, no profile or org names. |
| `exit_class` | `ok`, `usage`, `auth`, `error` | From the published exit-code table. Optional. Drop if the DPO objects. |
| `install_method` | `brew` | |

- **No IP retention.** The collection endpoint must not store source IPs or log them. This is an API/infra dependency, listed below.
- **No account link.** The device ID is never joined to a login, org or customer record. Say that in the docs only if it is true in the pipeline.
- **Retention.** Raw events are deleted after 13 months. Aggregates are kept. This is a proposed default, to be confirmed by the DPO.
- **Pseudonymous, not anonymous.** Do not describe the data as anonymous anywhere. A persistent device ID is personal data under GDPR.

### User controls

- `lq config set telemetry on|off` (frozen key; the PM's requested `off` command works as written).
- `lq telemetry status` shows the state, the winning source (flag, env or config) and the device ID.
- `lq telemetry reset-id` generates a new device ID.
- `lq telemetry show` prints the exact events it would send. `LQ_TELEMETRY_DEBUG=1` prints each event to stderr as it is sent. Neither sends anything.
- The payload schema is published in the docs and in the repo, with a changelog. Adding a field needs a minor release, a schema update and a release-note line. Adding a field that identifies more resets consent (the prompt appears again).
- `lq telemetry delete-id` is optional, and it depends on the backend supporting deletion by device ID. This is what makes an erasure request answerable.

## 4.3 release notes (wording)

> **Telemetry (opt-in).** `lq` can now send pseudonymous usage data (command names, CLI version, OS) to help us prioritize. It is **off by default**. On first run in a terminal, `lq` asks once. Review the exact payload with `lq telemetry show`; change your mind with `lq config set telemetry off`. Never collected in CI or against self-hosted servers. [Schema and privacy details]
>
> **Updates.** `lq` now tells you once a day when a newer version exists, on a terminal only. Install it with `lq update`, or your package manager. Silence the hint with `LQ_NO_UPDATE_CHECK=1`.

## API-side dependencies

| Need | Owner | Blocks |
|---|---|---|
| Telemetry collection endpoint: no IP storage, schema validation, 13-month deletion job, delete-by-device-ID | Platform / data | Telemetry on, in 4.3 |
| Signed version manifest and release-host hosting for `lq update` | Release engineering | `lq update`, the update notice |
| Server version endpoint reporting the supported CLI range (self-hosted compatibility warning) | Backend | Self-hosted version warning |

## Release cut line

| Capability | 4.3 | Later | Reason |
|---|---|---|---|
| Opt-in telemetry plus `lq telemetry` commands | ✅ | | Matches the PM's goal inside the EU constraint. |
| Daily non-blocking update notice | ✅ | | Cheap and safe. |
| `lq update` with signature check and rollback | ✅ | | Gives the PM the "stay current" path without the risk. |
| Default-on telemetry | | 5.0, if approved | Major version, advance notice and DPO sign-off. |
| `update.auto` unattended install | | 4.4+ | Needs demand evidence. Minor and patch only. |

## Open items

| Decision | Owner | Due |
|---|---|---|
| DPO review of payload, consent text, retention and the pseudonymous-ID position | Legal / DPO | Before 4.3 code freeze |
| Telemetry endpoint built with no IP retention and delete-by-ID | Platform / data | Before 4.3 code freeze |
| Opt-out for 5.0: go or no-go | PM + DPO | After 4.3 opt-in rate is measured |
| Signing tool and key custody for `lq update` | Release engineering | Before `lq update` merges |
| Whether to keep `exit_class` in the payload | PM + DPO | Before 4.3 code freeze |

## Gates for this section

- [ ] Non-interactive run: with stdin closed and stdout piped, no prompt, no update hint and no telemetry banner appears, and no command waits on the update check.
- [ ] Secret hygiene: no token, hostname, path or argument value appears in any telemetry event or in `lq telemetry show`.
- [ ] Contract coverage: `lq version --json`, `lq update --check --json` and `lq telemetry status --json` have schemas. The telemetry payload schema is published.
- [ ] Exit-code table tested: `lq update` on a package-manager install returns `2`, and a checksum failure returns non-zero and leaves the old binary in place.
- [ ] Opt-out proof test: with `DO_NOT_TRACK=1`, or a custom `base_url`, or `CI` set, a mock collector receives zero events.