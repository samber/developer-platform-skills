# IDE extension plan: Brindlewood

**Status: provisional.** The plan depends on a named owner (A1), and several answers below are assumptions. The first step is to name that owner.

## Verdict per job

| Job | Demand evidence | Surface | Extension part | Verdict |
| --- | --- | --- | --- | --- |
| Validate and autocomplete `flags.yaml` | Steady support tickets about mistyped keys | JSON Schema, published on SchemaStore under a distinctive file name, plus a `$schema` modeline | None. If the thin shell ships, it can add a `yamlValidation` contribution so plain `flags.yaml` is also covered. | **Go** (schema only). It needs no owner. |
| "IDE integration" on RFP checklists | 3 lost enterprise deals in Q3 | Not a job yet | None | **Go later.** Count it once sales shows what the RFP lines asked for and each ask maps to a job below. A checklist logo is not demand. |
| Browse flags per environment in a sidebar | 2 customers built an internal extension and asked for an official one | Extension | Tree view (environment → flag → state and rollout %), quick pick, "open in dashboard", login | **Go**, gated on a named owner (A1). With no owner this becomes No-go. |
| Rollout-percentage charts in a React webview | A product mockup only. No customer or ticket asked for it. | Dashboard already exists on the web | None for now | **Go later** (see promotion condition below). |
| Cursor and Claude Code agents toggle flags | A growing number of customers | MCP server over the public API (`samber/developer-platform-skills@mcp-server-offering`) | Optional one-click "add Brindlewood MCP server" command in the extension | **Go**, as a separate workstream. Agents need no IDE UI. |

Three points on those verdicts:
- **`flags.yaml` is too generic a name for catalog matching.** SchemaStore only fires on distinctive names. Ship the schema at a stable URL and register it for a distinctive name (for example `brindle.flags.yaml` or `.brindle/flags.yaml`). `brindle init` should write the `# yaml-language-server: $schema=…` modeline into the user's existing `flags.yaml`.
- **VS Code and Cursor users need a YAML extension.** Red Hat YAML is on both registries, so say so in the docs. JetBrains IDEs read the schema natively.
- **The dashboard panel is not a no-go on technical grounds.** A webview needs a staffed owner and is re-themed and re-tested per editor family. The same information fits a tree item (`prod · 25%`), and a link opens the real dashboard through `env.openExternal`. I'd promote the webview only when a customer names a job the tree cannot show, and only with an owner.

## Ranking

- **Step 1 default rung:** JSON schema for every config file, plus a thin shell (tree view, login, open in dashboard). It moves up when a job like "see rollout history in the editor" appears with real demand.
- **Step 1 starved option:** the rich extension (webview). It is promoted when a named job can't be shown by a tree view, quick pick or diagnostic, and a staffed owner exists. Today neither is true.
- **Step 2 default family:** one VS Code-API extension, published to both the VS Code Marketplace and Open VSX. It covers the 70% on VS Code and Cursor.
- **Step 2 starved family:** a JetBrains plugin. Note the unusual position: JetBrains is the second-largest group (20%, about 280 teams), but a second codebase needs a second owner who knows Kotlin or Java. That owner doesn't exist (Q5). It is promoted when such an owner fits the effort ceiling. The schema and the MCP server cover JetBrains until then.
- **Other editors (Neovim, Zed, Emacs):** reached through the schema and the MCP server, with documented client config and no plugins.
- **Language server:** not now. The schema fixes mistyped YAML keys. A server would only be needed to check flag keys against the live flag list. If you later build one, remember the JetBrains LSP API runs only in commercial IDEs.
- **Interview answers that moved a rung:** Q5 (no owner) holds the JetBrains plugin and the webview at starved and gates even the thin shell. Q3 (70/20 split) confirms the VS Code-API extension as the default family. Q7 (deadline and effort ceiling) is unanswered, so default rungs stay (A7).

## Editors and registries

| Family | Share of our users | Registry | Owner | Verdict or promotion condition |
| --- | --- | --- | --- | --- |
| VS Code | ≤70% (shared with Cursor; split unknown, A3) | VS Code Marketplace | TBD (A1) | Go, same `.vsix` as Open VSX |
| Cursor and other forks | in the 70% | Open VSX | TBD (A1) | Go. Claim the namespace and file the ownership claim before launch. |
| JetBrains | 20% | JetBrains Marketplace | none | Starved. Promote when a Kotlin or Java owner fits the effort ceiling. Until then: schema and MCP. |
| Neovim, Zed, others | ≤10% | none | none | Schema and MCP only |

## Architecture

- **Shared core:** the `brindle` CLI, called with `--json` and exit codes. The extension renders and routes commands and holds no flag logic.
- **Extension holds:** tree view, commands, walkthrough and the optional MCP setup command.
- **No direct REST calls from TypeScript.** Auth, proxy, region, retry and pagination already live in the CLI. If the CLI lacks a command, such as `brindle flags list --env <e> --json` (A2), add it to the CLI rather than to the extension.
- **Customers' internal extensions:** treat the two customers as design partners. Ask what they list and which API calls they make, so the CLI covers those cases.
- **CLI detection:** look on `PATH` plus a configurable path. Offer a pinned install, never `curl | sh`. Check the version at activation and show one upgrade message.
- **Activation:** specific events only (a view, a command, a `flags.yaml` file), never `*`.
- **Runs on:** desktop only at first. State "desktop only" on the listing, since it spawns the CLI. Remote workspaces are a known limit (A4).

## Identity

| Registry | ID or namespace | Claimed | Verification status |
| --- | --- | --- | --- |
| VS Code Marketplace | `brindlewood` (publisher) | claim this week | Verified badge needs an extension listed 6+ months and a 6-month-old domain. Publish early to start the clock. |
| Open VSX | `brindlewood` (namespace) | claim this week | Unverified until an ownership issue on `EclipseFdn/open-vsx.org` is granted |
| JetBrains | vendor profile; plugin `<id>` reserved | claim the vendor profile now | Plugin ID permanent. Nothing published (starved). |

Publish the publisher ID and extension ID on your own docs so buyers' security teams can allowlist them.

## Auth and trust

- **Login path:** reuse the CLI login. The extension runs `brindle auth token --json` and holds the token in memory only. It never reads the CLI's credential file and never writes the token to settings, logs or output channels.
- **Fallback:** a pasted API key stored in `SecretStorage`, masked in all logs.
- **Promotion:** an `AuthenticationProvider` over product OAuth, only if Brindlewood offers OAuth to desktop clients or remote workspaces become common (A4). See `samber/developer-platform-skills@oauth2-provider-design`.
- **Untrusted workspaces:** `"limited"`. The extension runs the CLI, so guard those paths with `workspace.isTrusted` and re-enable on `onDidGrantWorkspaceTrust`. The schema and read-only UI stay available.
- **Never read `.env` or workspace credentials** without an explicit user action.
- **Usage measurement:** server-side only. Every CLI and API call from the extension sends `brindle-vscode/<ver> (vscode <ver>; <platform>)` in the User-Agent. This needs a CLI env var or flag for the suffix (A2). No client events in v1. If you add any later, send them through `env.createTelemetryLogger`, which honours the host's `telemetry.telemetryLevel`, and publish the event list.

## First release sequence

| # | Step | Effort | Depends on |
| --- | --- | --- | --- |
| 0 | Name the owner, the on-call and a test account (Q5) | a decision, this week | – |
| 1 | Claim the VS Code publisher ID and the Open VSX namespace. File the Open VSX ownership claim. Create the JetBrains vendor profile. | an hour, plus days of waiting | – |
| 2 | Publish the JSON Schema at a stable URL. Submit it to SchemaStore under a distinctive file name. Make `brindle init` write the modeline. Document Red Hat YAML for VS Code and Cursor. | a day to a week | – |
| 3 | Audit the CLI: `flags list --json` per environment, the minimum CLI version, a User-Agent suffix | days | – |
| 4 | Ship the MCP server (separate workstream, `mcp-server-offering`). Include scoped, read-only-by-default tokens and confirmation before changing production flags. | a week or more | – |
| 5 | Build the thin shell: tree view, login via `brindle auth token --json`, open in dashboard, walkthrough. Bundle with esbuild. | a week or more | 0, 3 |
| 6 | Set up CI publishing with federated auth: `vsce publish --oidc` (or `--azure-credential`) and `ovsx publish --trusted-publishing`. Publish the same packed `.vsix` to both registries after a secret scan. | days | 1, 5 |
| 7 | Add the optional one-click "add MCP server" command | days | 4, 5 |
| 8 | Publish the compatibility matrix and link the extension from the CLI help, the quickstart and the dashboard | a day | 6 |

On step 6: global Azure DevOps PATs stop working on 2026-12-01, about five weeks from now. Don't build the publishing pipeline on one.

## Compatibility matrix (first row)

| Extension | Min CLI | Min VS Code (`engines.vscode`) | JetBrains `since-build` | API version | Status |
| --- | --- | --- | --- | --- | --- |
| 0.1.x (pre-release) | first CLI with `auth token --json` and `flags list --json` (A2) | Code-OSS base of the oldest Cursor or VSCodium build customers run (A3) | n/a | current public API | supported |

## Release and support

- **Cadence:** same train as the CLI. The extension never ships ahead of the CLI it calls.
- **Host versions tested:** the minimum `engines.vscode`, current stable, Insiders, plus Cursor. Use `@vscode/test-cli` against a real sandbox account and one remote target.
- **Owner and triage rhythm:** the owner from step 0, with weekly issue triage. Answer every listing review below 4 stars.
- **Metrics:**
  - Weekly active users by version, from the User-Agent.
  - First-run success: CLI found, login done, first flag listed.
  - Share of users on supported versions.
  - Tickets per release.
  - Business outcomes: "mistyped `flags.yaml` key" tickets before and after the schema, and RFP lines that the schema, extension and MCP now answer.

## Assumptions

| ID | Assumption | Step it drives | Who confirms |
| --- | --- | --- | --- |
| A1 | An owner (and on-call) will be named. If not, the extension becomes No-go and only the schema, the MCP server and the name claims proceed. | 0, 5 | you |
| A2 | The CLI can list flags per environment as JSON and can send a User-Agent suffix. If not, add these to the CLI first. | 3, 5 | CLI team |
| A3 | The VS Code and Cursor share of the 70%, and the oldest Cursor build in use, are unknown. They set `engines.vscode`. | 5, 8 | support and telemetry |
| A4 | Remote workspaces are rare and product OAuth for desktop clients does not exist. If either is false, promote the `AuthenticationProvider`. | 5 | product |
| A5 | "Mistype keys" means YAML property names. If it means flag keys that don't exist on the server, the schema is not enough and a language server or CLI-backed diagnostic enters scope. | step 1 verdict | support tickets |
| A6 | The 3 lost RFPs listed only "IDE integration", with no named job. If they named jobs, re-run the verdicts with that evidence. | step 1 verdict | sales |
| A7 | There is no hard deadline and the effort ceiling is small. A near deadline keeps the default rungs, and a staffed maintained surface would promote the starved ones. | all | you |
| A8 | There are no restricted fleets (allowlists, custom-CA proxies, air-gapped machines) among the enterprise buyers. If there are, add proxy, CA and offline `.vsix` support. | 7 (SKILL.md) | sales |

## Next three actions

1. Name the owner (A1).
2. Ask sales for the exact RFP wording (A6).
3. Ask support whether the typos are in YAML property names or in flag keys (A5).