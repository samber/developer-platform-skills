# Freshness and upkeep

Load this file during step 5, when writing the freshness contract, and during step 3 when estimating upkeep for the capacity cap.

## Contents

- Why upkeep binds
- CI patterns
- Dependency bot cadence
- Red-build SLA shape
- Upkeep estimates for the capacity cap

## Why upkeep binds

- Public code rots fast. About a quarter runs as published: 26% of 14,876 tutorial code blocks from commercial hosting providers (Docable, ESEC/FSE 2020), 24.4% of 10,259 Python gists (Gistable, ICSME 2018, over half failing on missing imports), 24.11% of notebook runs (MSR 2019).
- These figures measure uncurated public code, not CI-tested vendor samples. No vendor publishes the breakage rate of its own samples, so use them as the "no CI" baseline, never as your expected rate.
- Scale outruns capacity. MongoDB's documentation audit counted 35,000+ code examples and concluded the team "cannot actively maintain all of the existing code examples", recommending pruning thousands of low-value ones; its tested framework covered a few hundred.
- Upkeep often needs paid capacity: Twilio used contracted engineers to build 10 new gallery apps and maintain 45 existing ones.

## CI patterns

| Pattern                         | Who            | What it buys                                                    | Cost                                           |
| ------------------------------- | -------------- | --------------------------------------------------------------- | ---------------------------------------------- |
| Shared CI harness across samples | Stripe `sample-ci`, `make ci` per sample | One place to change install, lint, type-check, test | A small standing team or owner for the harness |
| Polyglot integration framework  | AWS doc examples | Routine runs of every language against the real service      | Live-service charges, credential handling      |
| Per-sample test plus flaky-test bot | Google Cloud samples | A failing sample files a `samples`, `priority: p1` issue automatically | Bot setup, triage queue                |
| Build, lint, type-check only    | Any, no sandbox | Catches removed symbols and broken imports                     | Near-zero per sample after setup               |

Run against test mode or a sandbox with test credentials (Stripe runs samples in test mode with test cards). Trigger runs on a schedule, on every SDK release, and on every API version change.

## Dependency bot cadence

Example Renovate shape. The cadence follows Google's `python-docs-samples` configuration (minor monthly, patch quarterly, vulnerability alerts any time); the automerge rule and the ignored path are additions to adapt, not Google's:

```json
{
  "extends": ["config:recommended"],
  "dependencyDashboard": true,
  "packageRules": [
    { "matchUpdateTypes": ["minor"], "schedule": ["* 0-3 1 * *"], "groupName": "minor updates" },
    { "matchUpdateTypes": ["patch"], "schedule": ["* * 1 */3 *"], "groupName": "patch updates" },
    { "matchUpdateTypes": ["patch", "minor", "lockFileMaintenance"], "automerge": true }
  ],
  "vulnerabilityAlerts": { "schedule": ["at any time"] },
  "ignorePaths": ["legacy/**"]
}
```

- Group updates; a polyglot sample has one lockfile per language, so ungrouped weekly bots bury the owner.
- Automerge only behind a green CI run against the sandbox; automerge without CI ships breakage faster.
- Exclude archived and legacy paths, or the bot keeps reviving them.

## Red-build SLA shape

Write the SLA as three numbers the team sets and labels self-set:

1. Time to an owner ticket after the first red run (usually same day, automated).
2. Days red before a fix-or-deprecate decision is forced.
3. Days deprecated before archive.

State who decides when the owner is absent. An SLA with no fallback decider never fires.

## Upkeep estimates for the capacity cap

No vendor publishes upkeep hours per sample. Estimate per type in orders of magnitude and label the estimates self-set:

| Artifact                 | Upkeep driver                                               | Order of magnitude per language per quarter |
| ------------------------ | ----------------------------------------------------------- | ------------------------------------------- |
| Hosted collection        | Spec changes only                                           | near-zero to an hour                        |
| Tiny quickstart          | One dependency tree, one route                              | an hour                                     |
| Scenario sample (shared repo) | Shares CI and bot with siblings                        | an hour                                     |
| Deploy template          | Host platform changes plus dependencies                     | an hour or two                              |
| Flagship quickstart      | Many products, frontend plus backends                       | half a day                                  |
| Mobile or device app     | App toolchain, OS releases, store or device changes        | a day or more                               |
| Embedded playground      | Hosting, sandbox credentials, abuse controls                | a day or more, plus platform cost          |
| Reference app            | Full dependency tree, infra, security review                | a couple of days                            |

Multiply by languages, sum the kept rows, compare with the interview capacity. Recalibrate after the first quarter using the real hours the owner logged.
