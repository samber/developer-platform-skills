# Where the Pinewick JetBrains plan breaks

Status: **provisional**. Several interview answers are missing (listed at the end). I read `SKILL.md` and its three references: `plan-templates.md`, `registry-publishing.md` and `vendor-patterns.md`.

Building the JetBrains plugin is the right call. 55% of your users are on JetBrains, and the skill ranks editor families by your own users' share. Six parts of the plan fail, ordered below by how much damage each does.

## 1. The LSP API doesn't cover most of your JetBrains users

This is the biggest break. The IntelliJ LSP API runs only in commercial JetBrains IDEs (IntelliJ IDEA Ultimate, and the free tier of unified PyCharm since 2025.1). It does not run in IntelliJ IDEA Community or in Android Studio. Those are two of the three IDEs in your 55%.

- Android Studio users won't get the same diagnostics, which is the opposite of the plan's stated goal.
- Only the Ultimate slice gets the reused language server.
- Decide this now and write it in the plan. The skill treats "exclude those users, or write a native language plugin" as an explicit decision.
- Options:
  - **A:** Ship LSP-only for Ultimate and tell Community and Android Studio users they are unsupported. This is cheap and probably excludes the majority.
  - **B:** Write a native plugin that spawns your language server and surfaces its output through the platform's own APIs. This is the most effort, and it covers every IDE.
  - **C:** Use a third-party LSP client library that runs in Community builds. LSP4IJ from Red Hat is one I know of, but the skill doesn't cover it. Verify it against Android Studio builds and its maintenance state before committing.
- Get the real split between Community, Ultimate and Android Studio from the survey. It decides which option you pick.

## 2. A half-time VS Code dev is not the owner this plan needs

The skill marks the JetBrains plugin as the starved rung: a second codebase, plus three platform majors a year to verify. It says to promote it only when a second owner who knows Kotlin or Java fits the effort ceiling, and that "a half-time owner already on VS Code is not that owner".

- Your numbers justify promoting it, because JetBrains is your largest group. The owner is the problem.
- Option B in section 1 is much heavier than a thin LSP client, and one half-time person cannot carry it.
- You also keep running the VS Code extension, and one of your two VS Code devs now splits their time.
- Name an owner with Kotlin or JVM experience, an on-call rotation and a test account. If nobody fits, the verdict is "Go later", not "start now".
- Budget one Plugin Verifier pass per platform major, so three a year.

## 3. Changing the plugin ID breaks every beta install

`com.pinewick.beta` then `com.pinewick.plugin` at GA is a hard failure. Contract rule 5 says a published plugin `<id>` must never change.

- A new ID is a new plugin with no upgrade path. Every beta user gets stranded, and any IT allowlist keyed on the beta ID stops matching.
- Claim `com.pinewick.plugin` (or your final choice) now and use it from the first upload.
- Run the beta on the `eap` or `beta` custom channel of the same plugin. Users add that channel as a custom repository URL.
- Nothing is published yet, so this costs you nothing today.
- Pick the final vendor name and plugin name now too. The plugin name must be original and 30 characters or fewer, and lookalike logos or trademark misuse get rejected.

## 4. The Gradle plugin's default compatibility breaks on the next IDE release

The defaults are not fine. IntelliJ Platform Gradle Plugin 2.x sets `untilBuild` to `<sinceBuild major>.*`, a pinned upper bound.

- Users on any newer IDE major see "incompatible", and you ship an update to fix it.
- Set `pluginConfiguration.ideaVersion.untilBuild = provider { null }` and check the generated `plugin.xml`.
- Choose `since-build` deliberately. Build against the lowest platform version you support. Android Studio ships on its own cadence, so pick a floor that covers the Android Studio versions your users actually run.
- Run `verifyPlugin` across the whole range, including EAP. Add it to your release gates.

## 5. IDE data-sharing consent doesn't cover your telemetry

Relying on it fails JetBrains approval and contract rule 4. JetBrains' consent covers JetBrains' own collection, not yours.

- You need your own explicit consent before sending any statistics.
- The plugin must also send nothing while it is idle. Both are approval rules.
- Collect no source code, file paths, usernames or tokens. Publish the event list beside the README.
- Better option: skip client events and measure server-side. Send a versioned `User-Agent` on every CLI and API call, for example `pinewick-jetbrains/0.1.0 (IntelliJ 2025.3; darwin-arm64)`. Keep it to product, version and platform, and document that it is sent.
- For the VS Code side, make sure your telemetry goes through `env.createTelemetryLogger` or `@vscode/extension-telemetry`. Your own setting can only narrow collection.
- JetBrains approval also needs a Developer EULA and, since you collect some data, a privacy policy.

## 6. Same-day hotfixes aren't possible on JetBrains

Every plugin version goes through automated checks plus manual review, with no guaranteed time frame. Plan for working days, and ask JetBrains after 3–4 working days of silence. Treat "JetBrains is the same as VS Code, ship the hotfix tonight" as a rejected rationalization.

- You can't roll back the way you do on VS Code. There you republish the last good code as a higher patch. On JetBrains the options are to hide the update in the vendor console and contact support, then wait for the next review.
- Fix fast through the shared core, not the plugin:
  - Keep the language server or CLI separately updatable. Don't bake it into the plugin zip, and make the plugin check for and download a pinned version.
  - Gate new features on capabilities the server or API reports, not on the plugin's version.
  - Release the plugin on a schedule, with a staged `eap` channel in front of `default`.
- Say in your public support policy that JetBrains fixes can take days.

## Smaller gaps

- **Registries.** The plan says nothing about the VS Code side beyond "reuse the server". Confirm the existing extension is on both the VS Code Marketplace and Open VSX, from the same `.vsix`. Cursor and VSCodium users depend on Open VSX.
- **Verified publisher.** The extension is eight months old. If your domain is also 6+ months old, you qualify for the verified-publisher badge now. It takes about 5 business days.
- **Publish credentials.** Check that CI doesn't use a global Azure DevOps PAT. Those stop working on 2026-12-01. Use `--azure-credential` or `--oidc`, and `ovsx publish --trusted-publishing`.
- **First JetBrains upload.** The first upload is manual through the web UI. Later uploads can use `publishPlugin`.
- **Auth.** Reuse the CLI's login through a command that prints a token as JSON, held in memory only. Use `PasswordSafe` for any stored key. No key in settings.
- **Architecture.** Keep the plugin a thin shell. No business logic and no hand-written API calls (contract rule 1).
- **Schema coverage.** If `.pinewick` is JSON or YAML with a distinctive file name, a schema on SchemaStore may cover part of the job for free in every JetBrains IDE. This is worth checking before building anything.
- **Restricted fleets.** Honour proxy settings and custom CAs, and document offline plugin install.

## Revised plan

| Item | Verdict |
| --- | --- |
| JetBrains first or VS Code first | JetBrains has the larger share, so it is the right priority. Condition: a staffed Kotlin or JVM owner (section 2). |
| IDE coverage | Pick option A, B or C in section 1 and record it. Don't promise Android Studio parity on LSP. |
| Plugin ID | Final ID from the first upload. Beta goes on the `eap` or `beta` channel. |
| Gradle | `untilBuild = null`, a chosen `since-build`, `verifyPlugin` across the range including EAP. |
| Telemetry | Server-side `User-Agent`. Any client event needs explicit consent and nothing sent while idle. |
| Hotfixes | Fixes ship through the server or CLI. The plugin goes out on a schedule with a review buffer. |

## Open assumptions (to confirm)

| ID | Assumption | Drives | Who confirms |
| --- | --- | --- | --- |
| A1 | The 55% is by share of paying customers, not just survey respondents | Ranking (step 2) | Product |
| A2 | The split between Community, Ultimate and Android Studio is unknown | LSP verdict | Survey data |
| A3 | A Kotlin or JVM owner exists beyond the half-time VS Code dev | Owner (Q5) | Engineering lead |
| A4 | The existing VS Code extension is published to both registries | Identity (step 6) | VS Code team |
| A5 | The language server can be updated separately from the plugin | Hotfix path | Language server owner |
| A6 | The jobs the plugin must do beyond diagnostics are not yet listed | Verdict per job (step 1) | Product |
| A7 | Whether customers run restricted fleets, allowlists or air-gapped machines is unknown | Fleet support (Q6) | Support |
| A8 | The ship deadline and effort ceiling are unstated | Rung promotion (Q7) | Leadership |

My first move: get the A2 numbers and settle section 1 before any code is written.