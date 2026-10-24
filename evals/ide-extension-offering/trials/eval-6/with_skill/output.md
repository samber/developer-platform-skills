# Deprecation plan: `fernhollow.fernhollow-login`

**Status: provisional.** Seven assumptions are open (table at the end).

## Changes to your plan

| Your plan | This plan | Why |
| --- | --- | --- |
| Remove from the Marketplace and Open VSX next Friday | **Deprecate on both registries and keep the extension installable.** Announce 2026-10-30, stop updates 2027-01-29, never remove. | Removal deletes the stats and reserves the name forever, even for you. Customer allowlists key on `fernhollow.fernhollow-login`. 18k installs would also get no migration path, and the removed listing stays squattable on Open VSX. |
| Say nothing about JetBrains | **Deprecate the JetBrains plugin too, on its own track.** | It is a second codebase with its own review queue. `fernhollow-tools` is a VS Code-API extension, so it does not replace the plugin. |
| Newsletter mention | **Newsletter is the third channel, not the announcement.** The announcement is a public issue, the changelog, and a notice in the extension. | Most of the 18k installs never read the newsletter. |
| Publish `fernhollow-tools` | **Gate the announcement on `fernhollow-tools` being live** on both registries, with a named owner. | A deprecation notice can't say "replace it with X, available now" until X exists. |

## Decisions needed before Friday

1. **Who owns `fernhollow-tools`?** The only maintainer left last month, and an extension with no owner is a no-go. Without a named owner and on-call, ship the MCP server docs and the CLI only, and do not publish a new extension.
2. **Is "VS Code's built-in auth" really the replacement for sign-in?** VS Code ships only Microsoft and GitHub providers. Signing in to the Fernhollow CLI from the editor needs one of these:
   - the CLI's own login, reused through a `fernhollow auth token --json` command;
   - an `AuthenticationProvider` over Fernhollow OAuth.
   
   Confirm which one `fernhollow-tools` uses. If neither exists, job 1 is not covered and the notice must not claim it is.
3. **Is "poke at tenant config" covered by the MCP server?** MCP serves agents, not a human browsing a tree. If humans used that feature, either `fernhollow-tools` keeps a thin tree view over the CLI, or the notice says plainly that the feature goes away.
4. **Confirm "next Friday" means 2026-10-30.** Today is Saturday 2026-10-24, so that's six days out. If you meant 2026-11-06, shift every date below by a week.

## Verdict per job

| Job | Replacement | Verdict |
| --- | --- | --- |
| Sign in to the CLI from the editor | CLI login reuse or `AuthenticationProvider` (decision 2) | Deprecate once the replacement is verified |
| Inspect and edit tenant config | MCP server for agents; CLI for humans; possible thin tree view (decision 3) | Deprecate; gap if humans used it |
| Agents operate Fernhollow | MCP server, one-click setup from `fernhollow-tools` | Go |

## Timeline

| Date | Step | Owner |
| --- | --- | --- |
| Sat 10-24 to Mon 10-26 | **Revoke every publish token** the departed engineer created. Audit the VS Code publisher members, the Open VSX namespace and the JetBrains vendor profile. Move CI to federated publishing (`vsce --oidc` or `--azure-credential`, `ovsx --trusted-publishing`). | Platform lead |
| Mon 10-26 | Build the last JetBrains release (notice, no features) and **submit it now**. Every version is manually reviewed with no guaranteed time frame; ask after 3-4 working days. | Platform lead |
| Mon 10-26 to Wed 10-28 | Claim `fernhollow-tools` as the extension name on the existing publisher, and claim the Open VSX namespace if any item is unclaimed. Publish the new ID on the docs site so IT can allowlist it before anyone is asked to install it. | Owner of `fernhollow-tools` |
| Wed 10-28 | **Publish `fernhollow-tools`** (the same packed `.vsix` hash on both registries, with the gates below). | Owner of `fernhollow-tools` |
| Thu 10-29 | Final `fernhollow-login` release: one notice at activation, with a link. Use the even-minor rule, publish a higher patch, and keep `engines.vscode` unchanged. Package once, scan the `.vsix` for secrets, publish the same file to both registries. | Platform lead |
| **Fri 10-30** | **Announce**: public issue, changelog, docs banner. Comment on the `microsoft/vscode-discussions` "Deprecated extensions" thread naming `fernhollow.fernhollow-tools`. Open the Open VSX pull request to `extension-control/extensions.json` in `open-vsx/publish-extensions`, naming the replacement and keeping the extension downloadable. It shows the day after merge. Add the deprecation note to the JetBrains listing. | Platform lead |
| Next newsletter | One paragraph with the date and the link to the issue. | Marketing |
| Fri 2027-01-29 | **Stop updates** (91 days). Archive the repository and keep the security contact live. The extension stays installable. | Platform lead |

If `fernhollow-tools` isn't live on both registries by Wednesday 10-28, move the announcement, not the safety checks.

## Gates before the announcement

- `fernhollow-tools` is live on the VS Code Marketplace and Open VSX with an identical `.vsix` hash and a clean secret scan.
- Integration tests are green on the minimum and newest VS Code, one fork (Cursor or VSCodium) and one remote target, against a real sandbox tenant.
- Telemetry follows the host setting (no usage event fires at `error` or `off`), and untrusted-workspace behaviour is tested.
- The credentials in `fernhollow-tools` are in `SecretStorage`, never in settings.
- The compatibility matrix is published with the `fernhollow-tools` v1 row.
- The JetBrains submission is in review.

## Deprecation notice (publish verbatim)

> # Fernhollow Login is deprecated on 2026-10-30; it stops receiving updates on 2027-01-29
>
> **Replace it with:** the Fernhollow Tools extension (`fernhollow.fernhollow-tools`) on the VS Code Marketplace and Open VSX, available now. For JetBrains, use the Fernhollow CLI login plus the Fernhollow MCP server (assumption A4).
>
> **Why:** VS Code's built-in authentication and the Fernhollow MCP server now cover what this extension did.
>
> **What to do:**
> 1. Install `fernhollow.fernhollow-tools`.
> 2. Sign in again from the editor (`<command from decision 2>`). Your CLI login is unchanged.
> 3. Uninstall `fernhollow.fernhollow-login`.
>
> **What keeps working:** the current version stays installable on all registries until 2027-01-29, and after it. We are not removing it.
>
> **Questions:** `<issue link>`

For allowlists, tell IT in the same issue to add `fernhollow.fernhollow-tools` (VS Code `extensions.allowed`) alongside the old ID.

## Release and support

- **Old extension:** security fixes only until 2027-01-29. Track the weekly active users still on it, by version, from the server-side `User-Agent`. Check them at day 30 and day 60. If many remain, extend the date instead of forcing the move.
- **New extension:** release in the same train as the CLI, test on the minimum and newest host weekly, and triage issues weekly.
- **Metrics:** share of users migrated, first-run success, tickets per release.

## Assumptions

| ID | Assumption | Drives | Who confirms |
| --- | --- | --- | --- |
| A1 | "Next Friday" is 2026-10-30. | Whole timeline | You |
| A2 | `fernhollow-tools` is a thin shell over the CLI plus an MCP server definition, with no hand-written API calls. | Architecture and gates | Owner |
| A3 | `fernhollow-tools` has a named owner and on-call. | Go/no-go for the new extension | You |
| A4 | The JetBrains plugin has no VS Code-style replacement; the CLI and MCP docs are the pointer. | JetBrains notice | You |
| A5 | The publisher ID is the same and already verified, so `fernhollow-tools` inherits the badge. | Identity | Publisher admin |
| A6 | Customers have allowlisted the old ID. A new ID needs IT approval, which is why the notice goes out early. | Notice and docs | Support/CS |
| A7 | 91 days is long enough. Adjust after the day-30 and day-60 usage reads. | Sunset date | You |