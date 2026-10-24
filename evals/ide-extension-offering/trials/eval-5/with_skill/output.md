# Larkspur VS Code extension: telemetry fix, fleet support, and the exec number

I followed the `ide-extension-offering` skill and its references. I couldn't see your code, CLI, or registry listings, so the plan is **provisional**, and each guess is a numbered assumption (A1–A8) at the end.

## Summary

1. **Telemetry is a contract violation, and it comes first.** A plain `fetch` ignores the host's telemetry level. Sending workspace paths and git emails breaks a second rule. Ship a hotfix before anything goes to the bank or the exec team.
2. **"41k active developers" is wrong.** 41,000 is installs, which measures acquisition only. Present it as "41,000 installs" and put the active number on a roadmap.
3. **The bank's problem is a fleet-support gap.** Fix proxy and CA handling, then hand IT an allowlist pack that includes a `.vsix` they can host in their private marketplace.

## 1. Telemetry complaint

### What is wrong

| Finding | Rule broken | Why it matters |
| --- | --- | --- |
| `fetch` to your analytics endpoint ignores VS Code's `telemetry.telemetryLevel`. | Contract rule 4: the host setting wins, and your setting "can only narrow collection". | `larkspur.telemetry.enabled` (default on) is not a defense. With host telemetry off, nothing may be sent. The customer is right. |
| The payload includes the workspace folder path and the git user email. | Step 7: "Collect no source code, file paths, usernames or tokens." | Folder paths often contain client or project names. A git email is personal data. This is worse than the gating bug. |
| It is hand-rolled, not `env.createTelemetryLogger` or `@vscode/extension-telemetry`. | Step 7: "never hand-roll the gate." | The logger honours all, error, crash and off for you. |

### The hotfix

Ship it as a higher patch, using one packed `.vsix` published to both registries.

1. **Remove path and email.** Delete both fields from every payload. Do not hash them: a hashed email is still a stable per-person identifier.
2. **Route all client events through the telemetry logger.** Use `env.createTelemetryLogger` with your sender, or `@vscode/extension-telemetry`. Treat `larkspur.telemetry.enabled` as an extra off switch on top of the host level, never a bypass.
3. **Send no usage events at `error` or `off`.** Add a test for this, because it is a release gate.
4. **Add `telemetry.json` and publish the event list** next to the README. Contract rule 4 names this as part of the fix.
5. **Measure server-side instead.** Add a versioned `User-Agent` to every CLI and API call, for example `larkspur-vscode/2.4.0 (vscode 1.104; darwin-arm64)`. Include product, version and platform only. Never include user or workspace identifiers. Document that it is sent. This replaces email dedupe (see section 3).
6. **Check the other direct network calls.** Anything that calls the API directly instead of the CLI breaks contract rule 1, and it is probably also what breaks the bank's proxy (section 2).

### Data already collected

- **Stop ingesting** the path and email fields now, server-side, even before the client hotfix ships.
- **Delete the stored values** and find every downstream copy: warehouse, backups, BI exports, any third-party analytics vendor.
- **Quarantine events sent while host telemetry was off.** They were collected against the user's choice, so don't use them for metrics.
- **Get a privacy review.** Git emails are personal data under GDPR, so this is a question for your DPO or counsel, not for engineering. I'm not giving legal advice.

### Public reply

Post this only after the patch is live on both registries. Legal should decide how much detail to give about the email field.

> You're right, and we're sorry. Version X.Y.Z, out today, sends usage events only through VS Code's own telemetry API, so `telemetry.telemetryLevel` = off means nothing is sent. We've also stopped collecting workspace paths and git emails [and deleted the data we had]. The full list of events is published here: <link>. Questions or concerns: <issue link>.

## 2. Bank: proxy, internal CA, allowlist, private marketplace

The skill's own failure mode fits: "works for the team, fails for customers". The extension likely misses proxy and CA handling that the CLI already has.

**Fix the proxy and CA path**

1. **Route network access through the CLI**, per contract rule 1. Don't use `fetch` against the API from the extension.
2. **Pass VS Code's proxy settings to the CLI** when the extension spawns it. That means `http.proxy` and system certificates. The CLI must honour them as well.
3. **If the CLI lacks proxy or custom-CA support, fix that in the CLI.** Don't paper over it in the extension. Assumption A4 covers this.
4. **Test it before telling the bank it's fixed.** Run a proxy that re-signs TLS with a private CA, with and without VS Code's `http.systemCertificates`. Include a remote or dev-container run.

**Give IT "something to allowlist"** by publishing a single "Enterprise deployment" docs page containing:

| Item | Value |
| --- | --- |
| VS Code Marketplace publisher ID and extension ID | `<publisher>.<extension>` (placeholder) |
| Open VSX namespace | `<namespace>` (placeholder) |
| Hostnames the extension and CLI contact | List from a real traffic capture of the patched build. Mark each as required or optional. The extension must work with the analytics endpoint blocked. |
| Proxy and CA setup | The settings and env vars from the steps above |
| Telemetry behaviour | Follows `telemetry.telemetryLevel`; link to the event list |
| Minimum VS Code and CLI versions | From the compatibility matrix |
| Offline install | The `.vsix` with a SHA-256 checksum |
| Security contact | `SECURITY.md` and a vulnerability contact |

IT can restrict installs with VS Code's `extensions.allowed` setting.

**Private marketplace**

- Provide the exact `.vsix` that is on both public registries, so the bank can vet it once and host it.
- Test your install and update flow against a VS Code private marketplace.
- Their ~2,000 developers install from the private marketplace, so they are **not in your install count**. This matters for the exec number (section 3).

⚠️ **Sequence matters.** Don't hand the bank an allowlist before the telemetry hotfix ships. A hostname list that includes an endpoint receiving paths and emails would be a security-review finding, and it would confirm the Mastodon post to a bank.

## 3. The exec number

Use "41,000 installs" on the slide, not "41k active developers." Installs measure acquisition only.

Reasons the number can't be called active developers:

- It counts installs, not use. Anyone who installed and never signed in is in it.
- It excludes private-marketplace fleets such as the bank's.
- Open VSX counts are separate from the Marketplace's.

I can't give you an active-user figure yet, because the data to compute it doesn't exist until the hotfix ships.

**Suggested slide wording**

> 41,000 installs (VS Code Marketplace). Active usage measured from <date> via server-side requests; first figure expected <date>.

**Metrics to define** (step 8):

- Weekly active users by version, from the server-side `User-Agent`.
- First-run success: CLI found, login done, first trace shown.
- Share of users on supported versions.
- Issues and tickets per release.

If the backend already logs authenticated requests from the extension, you may be able to count distinct accounts over the last 7 days now. Check whether that's possible before the meeting.

Don't reuse the old email-deduped number. It came from data collected against the contract.

## 4. Offering plan

```markdown
# IDE extension plan: Larkspur

Status: provisional (assumptions A1–A8 open)

## Verdict per job
| Job | Demand evidence | Surface | Extension part | Verdict |
| --- | --- | --- | --- | --- |
| See traces inline next to the emitting function | 41k installs (acquisition only); bank asks for fleet support | Extension | CodeLens/decorations over CLI output | Go (shipped; fix and maintain) |
| Log in | assumption A5 | CLI login reuse | command | Go |

## Ranking
- Step 1 default rung: thin shell over the CLI; stays default (Q7: hotfix is urgent)
- Step 1 starved option: webview dashboards; promoted only when a job needs it and an owner exists
- Step 2 default family: one VS Code-API extension on VS Code Marketplace and Open VSX
- Step 2 starved family: JetBrains plugin; promoted when JetBrains is the second-largest share and a Kotlin/Java owner exists (A7)

## Editors and registries
| Family | Share of our users | Registry | Owner | Verdict or promotion condition |
| --- | --- | --- | --- | --- |
| VS Code | unknown (A6) | VS Code Marketplace | A8 | Go |
| VS Code forks | unknown (A6) | Open VSX | A8 | Go, if not already published (A1) |
| JetBrains | unknown (A7) | JetBrains Marketplace | none | Go later |

## Architecture
- Shared core: Larkspur CLI (A4: proxy/CA support to be confirmed)
- Extension holds: UI only; no direct API calls
- Runs on: desktop; remote/dev-container behaviour to be tested

## Identity
| Registry | ID or namespace | Claimed | Verification status |
| --- | --- | --- | --- |
| VS Code Marketplace | <publisher> | A2 | verified-publisher status unknown |
| Open VSX | <namespace> | A1 | ownership claim needed if unverified |

## Auth and trust
- Login path: CLI login reuse (`larkspur auth token --json`, A5)
- Secret store: SecretStorage; no keys in settings
- Untrusted workspaces: limited; disable CLI-spawning paths until trusted
- Usage measurement: server-side User-Agent `larkspur-vscode/<ver> (vscode <ver>; <platform>)`; client events only through the telemetry logger, gated by host level then `larkspur.telemetry.enabled`, event list published with `telemetry.json`

## First release sequence
| # | Step | Effort | Depends on |
| --- | --- | --- | --- |
| 1 | Stop server-side ingest of path/email; start deletion | an hour to a day | - |
| 2 | Hotfix: logger-based telemetry, drop path/email, add User-Agent, `telemetry.json` | a day or two | 1 |
| 3 | Test: no usage events at `error`/`off`; secret scan of the `.vsix` | a day | 2 |
| 4 | Publish the same `.vsix` to both registries | an hour | 3 |
| 5 | Public reply and event-list page | an hour | 4 |
| 6 | Proxy/custom-CA fix via CLI; test with a re-signing proxy and a private marketplace | a week | A4 |
| 7 | Enterprise deployment page and allowlist pack; send to the bank | a day | 4, 6 |
| 8 | Active-user dashboard from User-Agent; first exec figure | a week | 2 |

## Compatibility matrix (first row)
| Extension | Min CLI | Min VS Code | JetBrains since-build | API version | Status |
| --- | --- | --- | --- | --- | --- |
| next patch | <A4> | <engines.vscode> | n/a | <A4> | supported |

## Release and support
- Cadence: same train as the CLI
- Host versions tested: minimum `engines.vscode`, current stable, Insiders, one fork, one remote target
- Owner and triage rhythm: A8; weekly
- Metrics: WAU by version, first-run success, supported-version share, tickets per release

## Assumptions
| ID | Assumption | Step it drives | Who confirms |
| --- | --- | --- | --- |
| A1 | Extension is on Open VSX with a claimed namespace | 2 | Extension owner |
| A2 | Publisher ID is claimed; verified-publisher badge status unknown | 6 | Extension owner |
| A3 | CI publishes with a global PAT that stops working 2026-12-01 | 6 | Release engineer |
| A4 | The extension calls the API directly (explaining the proxy failure); the CLI honours proxy and custom CA | 3, 7 | Extension owner, CLI owner |
| A5 | The CLI has a login command that can print a token | 4 | CLI owner |
| A6 | Editor shares of paying customers unknown | 2 | Product |
| A7 | No JetBrains plugin and no Kotlin/Java owner | 2 | Engineering lead |
| A8 | A named owner exists with a test account and weekly triage | 8 | Engineering lead |
```

## Questions I couldn't answer

Please reply on these, in this order. They change the plan.

1. Is the extension on Open VSX, and who holds the publisher accounts? (A1, A2)
2. Does the extension call the API itself, or only through the CLI? Does the CLI support proxy and custom CA? (A4)
3. How does CI publish today? A global Azure DevOps PAT stops working on 2026-12-01. (A3)
4. How are credentials stored? If keys sit in a settings file, that breaks contract rule 3, and we'd need to rotate them.
5. Who is the DPO or counsel for the data deletion and the public reply?