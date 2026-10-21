# Plan templates

Output shapes for the offering plan, the compatibility matrix and the deprecation notice. Fill every field. Where a field rests on a guess, write `assumption A<n>` in it and add row A<n> to the Assumptions table; one record per assumption.

## Offering plan

```markdown
# IDE extension plan: <product>

Status: provisional (open assumptions below) | confirmed

## Verdict per job
| Job | Demand evidence | Surface | Extension part | Verdict |
| --- | --- | --- | --- | --- |
| <job> | <tickets, deals, community extension installs> | <schema / language server / MCP / CLI / extension> | <command, tree view, diagnostic, launch config, none> | Go / No-go / Go later (condition) |

## Ranking
- Step 1 default rung: <...>; moves up when: <...>
- Step 1 starved option: <...>; promoted when: <...>
- Step 2 default family: <...>; starved family: <...>; promoted when: <...>
- Interview answers that moved a rung: <Q7 deadline kept default / Q5 owner promoted ...>

## Editors and registries
| Family | Share of our users | Registry | Owner | Verdict or promotion condition |
| --- | --- | --- | --- | --- |

## Architecture
- Shared core: <CLI vX / language server / SDK>
- Extension holds: <UI only>
- Runs on: <desktop only / web too>

## Identity
| Registry | ID or namespace | Claimed | Verification status |
| --- | --- | --- | --- |

## Auth and trust
- Login path: <CLI login / AuthenticationProvider / key fallback>
- Secret store: <SecretStorage / PasswordSafe>
- Untrusted workspaces: <false / limited + what is disabled>
- Usage measurement: <server-side User-Agent format; client events only if needed: list, host-level gate, own setting, event list URL>

## First release sequence
| # | Step | Effort (order of magnitude) | Depends on |
| --- | --- | --- | --- |
| 1 | Claim publisher ID, Open VSX namespace, JetBrains plugin ID | an hour | - |
| 2 | <...> | <a day / a week> | <...> |

## Compatibility matrix (first row)
Copy the matrix below with the v1 row filled.

## Release and support
- Cadence: <same train as CLI, monthly, ...>
- Host versions tested: <oldest, newest, pre-release>
- Owner and triage rhythm: <team, weekly>
- Metrics: <WAU by version, first-run success, supported-version share, tickets per release>

## Assumptions
| ID | Assumption | Step it drives | Who confirms |
| --- | --- | --- | --- |
```

## Compatibility matrix

| Extension | Min CLI / language server | Min VS Code (`engines.vscode`) | JetBrains `since-build` | API version | Status |
| --- | --- | --- | --- | --- | --- |
| 2.4.x | 1.18.0 | 1.95.0 | 243 | 2025-06 | supported |
| 2.2.x | 1.12.0 | 1.90.0 | 241 | 2025-01 | security fixes until <date> |

Example values; replace with your own.

## Deprecation notice

```markdown
# <Extension name> is deprecated on <announce date>; it stops receiving updates on <end date>

**Replace it with:** <replacement extension, built-in feature, or CLI command>, available now.

**Why:** <the host or protocol now does this job / the feature moved to ...>.

**What to do:**
1. Install <replacement> (<link to both registries>).
2. <Setting or command migration, old -> new>.
3. Uninstall <old extension ID>.

**What keeps working:** the current version stays installable on all registries until <end date>; no forced removal.

**Questions:** <issue link>
```

Post the same text in the public issue, the changelog and the activation notice of the last release.
