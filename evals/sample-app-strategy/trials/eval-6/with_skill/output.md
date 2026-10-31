# Halloway Maps: discoverability layer and measurement plan

Covers steps 7 and 8 of `sample-app-strategy`. No one answered the interview, so every assumption below is marked **unapproved - assumed**. Steps 1-6 (register, shape, triage, freshness, archive) are not done. This layer depends on them, so the first action is the register.

## 0. Assumptions to confirm

| # | Assumption | If wrong |
|---|---|---|
| A1 | The four lists (docs, CMS gallery, `hw samples list`, org README) hold roughly the same ~15-30 repos. I have not seen the inventory. | Run the register first. |
| A2 | `geocode-express-old` is not yet archived, or is archived without a banner. | If it is archived and agents still pick it, the failure is in section 3 (agent surface), not triage. |
| A3 | No true sandbox exists. CI would use a quota-capped, CI-only key against the live service. | If a sandbox exists, CI runs against it. If neither exists, CI is build, lint and type-check only, and every sample is labelled "compiled, not run". |
| A4 | The SDKs' user-agent can take an app-info suffix. | Add an `appInfo` option to each SDK (one small change per language). |
| A5 | `hw samples create` can mint or label a test key. | Tag the key out of band, with a `--sample` flag on `hw keys create`. |
| A6 | One named person can own the index (the portfolio owner). | No owner means no index. This is the blocker for everything below. |

Questions that would change the design (one at a time, as the skill requires):

1. Which sample repos exist today, with their language and last CI date?
2. Is there a sandbox or test mode?
3. Who signs off on archiving?

## 1. Diagnosis

The four lists are four independent sources of truth, so they drift. Two failures show it:

- **`routing-v1-demo` is still in the CLI.** The March archive skipped step 4 of the archive sequence, "remove from every surface". The CLI's hard-coded list was one of those surfaces, and nothing checked it. Binaries already shipped keep offering the repo until users upgrade.
- **Assistants scaffold from `geocode-express-old`.** An archived repo stays public, cloneable, and in crawled corpora. A bare "archived" flag does not tell a model what to use instead. The fix is to say what is current, in places agents read.

## 2. One canonical index

**Location:** repo `<samples-org>/index`, owned by the named portfolio owner. CI publishes `samples.json` and its JSON Schema to a stable URL on the docs domain, for example `https://<docs-domain>/samples/index.json`. Only a PR to this repo changes a sample's status.

```json
{
  "schema": 1,
  "generated_at": "2026-10-30T00:00:00Z",
  "samples": [
    {
      "id": "geocode-quickstart",
      "scenario": "geocode-first-call",
      "type": "flagship-quickstart",
      "job": "first-call",
      "languages": ["node", "python", "java", "go"],
      "framework": "minimal",
      "repo": "https://github.com/<samples-org>/geocode-quickstart",
      "status": "current",
      "owner": "<named person>",
      "sdk_pin": { "node": "3.x", "python": "3.x" },
      "api_version": "2026-01",
      "scaffold": true,
      "ua_tag": "geocode-quickstart"
    }
  ],
  "aliases": {},
  "deprecated": {
    "routing-v1-demo": {
      "status": "archived",
      "archived": "2026-03",
      "successor": "<routing-scenario id or null>",
      "message": "Routing v1 is retired. Use <successor>."
    },
    "geocode-express-old": {
      "status": "archived",
      "successor": "geocode-quickstart",
      "message": "Superseded. Use geocode-quickstart (Node folder)."
    }
  }
}
```

Rules:

- **`status`** is one of `current`, `community`, `archived`. Every `archived` entry needs a `successor` or an explicit `null`.
- **Index CI** fails the PR when:
  - a `current` repo is missing, is archived on GitHub, has no owner, has red CI past the SLA, or pins an SDK major outside the support window;
  - an `archived` repo is not archived on GitHub, lacks the banner, or still has a deploy button or the template flag.
- **IDs are never reused.** An old name stays resolvable through `aliases` or `deprecated`, as in Expo's `meta.json`.

## 3. Surfaces driven from the index

Each surface becomes a generated view. Nobody hand-edits a list.

| Surface | Today | Change | Drift guard |
|---|---|---|---|
| `hw samples list/create` | Hard-coded list | Fetch the index at runtime with ETag caching. Ship an embedded snapshot, generated at release, as the offline fallback. Warn when the snapshot is more than 30 days old (self-set). | Release build fails if the snapshot differs from the live index. |
| Docs pages | Hand-edited | A docs component renders sample tables and links from the index at build time. | Docs build fails on any sample link whose ID is not `current`. |
| Marketing gallery (CMS) | Own list | The CMS stores only editorial fields (blurb, screenshot) keyed by `id`. Membership and status come from the index through a nightly sync. | The sync opens a ticket when a CMS entry has no index ID, or maps to a non-`current` one. |
| Samples org README | Hand-edited | Generated from the index by CI on every merge. | Index CI commits it. |
| GitHub repo description, topics, template flag | Manual | A sync job sets them from the index, including `deprecated` topics and the "ARCHIVED, use X" description prefix. | The sync job reconciles weekly. |
| Coding agents | Nothing | See below. | The monthly probe in section 5. |

**`hw samples create <id>` behaviour:**

- `current` ID: scaffold the sample, write test keys into `.env` (never commit it), and tag the key with the sample ID.
- Alias or `archived` ID: do not scaffold. Print the `message`, name the successor, and exit non-zero. Offer `hw samples create <successor>`.
- Old binaries cannot be recalled. Their only protection is the archived repo's own banner (below). Add a minimum-version warning once the new CLI ships.

**Agent surface.** Agents ingest archived repos as readily as current ones, so make "what is current" available in four places:

1. **`/llms.txt`** on the docs domain lists current samples, with a link to `index.json`. It states: "Do not scaffold from archived repos. Archived IDs: …".
2. **An agent guide page** (the "vibe coding guide" shape Plaid ships) with one canonical quickstart per job, each pointing to its index ID.
3. **Archived repos, set once at archive time:**
   - The first three README lines are the banner and successor link.
   - The repo description begins `ARCHIVED - use <successor>`.
   - Add an `AGENTS.md` that says the same.
   - Set the GitHub archived flag.
   - Remove deploy buttons.
   - Never delete the repo.
4. **Current repos** carry an `AGENTS.md` with the sample ID, API version, and SDK pin, so an assistant that lands in a repo knows what it is looking at.

I cannot guarantee that models trained on old crawls stop recommending the old repo. The guard is the monthly probe in section 5, which measures it.

**Immediate fixes, this week (security scan first, per step 1):**

1. Run the secret and vulnerability scan on `routing-v1-demo` and `geocode-express-old`.
2. Add both IDs to `deprecated`.
3. Ship the CLI change that reads the index. Until then, hand-remove `routing-v1-demo` from the CLI list.
4. Apply the archive banner and `AGENTS.md` to both repos.

## 4. Archive-gate change

Archiving a sample is not done until the index PR is merged and the index CI passes. This closes the gap that left `routing-v1-demo` in the CLI. Add it to the archive playbook as a step-4 exit check.

## 5. Measurement plan

### Marketing's proposed KPI: report it, do not decide on it

Stars and clones per repo, reviewed quarterly, is a poor decision metric for three reasons:

- **Clones are inflated** by CI, dependency bots, mirrors and agents. GitHub keeps only 14 days of traffic data, and only for people with push access.
- **It rewards sprawl.** Merging scenarios into one shared repo, which the skill's triage rule recommends, splits one repo's stars from many into one. Per-repo counts then look like a loss.
- **It reflects marketing reach.** It does not say whether a sample got a developer to a working call.

Proposal for marketing: stars and clones stay in the quarterly report as context columns, tagged "vanity, report only". Decisions use the four signals below.

### Tagging

- **User-agent suffix.** The sample's source code passes app-info with its ID, for example `halloway-node/3.2.1 sample/geocode-quickstart/1.4`. Because it lives in the code, a plain `git clone` is tagged as well as a CLI scaffold.
- **Key label.** The CLI labels the test key it mints with the same ID, so the first call can be joined to the scaffold event.
- **Caveat.** A developer who copies the sample into production keeps the tag. So measure activation only on calls within the key's first 7 days. Count post-7-day tagged traffic separately as "descended from sample" usage. Use that second number for sunset notices and for finding who still runs archived samples.

### Four signals per artifact

| # | Signal | Definition | Source |
|---|---|---|---|
| 1 | Invocations | `hw samples create <id>` runs, plus deploy-button uses, plus first-seen key labels per ID | CLI (disclosed, opt-out telemetry) or the key-mint API |
| 2 | Time to first call | Median and p90 from scaffold or key creation to the first 2xx on that key. Also report the share that reaches one within 24 hours and 7 days. | API logs joined on key label |
| 3 | Tickets naming the sample | Count per quarter. Add a required "sample ID" field, or a tag, in the support form. | Support tool |
| 4 | CI pass rate | Green runs ÷ runs over the quarter, with days red | CI |

### Added signals for this layer

| Signal | Target | Why |
|---|---|---|
| Surface drift: count of surfaces disagreeing with the index | 0 (nightly check) | Measures the original complaint directly |
| Deprecated-ID traffic: CLI redirect hits and API calls whose UA carries an archived ID | Falling quarter over quarter | Shows who still depends on archived samples, and who to notify |
| Agent probe: each month, ask 3-5 coding assistants to scaffold a Halloway geocoding app and routing app, and record which repo they use. Keep it as a pass/fail log. | 100% current by quarter 2 (self-set) | Closes the loop on the assistant failure; the only direct measure of it |

### Baseline and cadence

- **Quarter 1** is the baseline. No vendor publishes clone-to-signup or deploy-to-activation benchmarks, so set targets only after one full quarter. Recalibrate the upkeep estimates from real hours at the same time.
- **Until tagging ships, usage is `not measured`, not zero.** Decide on tickets and inbound links, and say so in the register row.
- **Continuous:** drift check and CI red alerts.
- **Monthly:** agent probe and the red-build and deprecated-traffic review.
- **Quarterly:** decision review on the four signals, with stars and clones as footnote columns.

### Decision rules

- An artifact with red CI past the SLA and **measured** zero invocations and zero tagged traffic for two quarters is archived.
- A sample with high invocations but a long time to first call goes to the owner for a fix. It does not go to marketing.
- Archive and merge decisions never use stars.

## 6. Pass gate (current status)

| Check | Status |
|---|---|
| Every kept artifact has a named owner and freshness contract | Not met (register not built) |
| Kept upkeep hours within the owner's capacity | Not assessed (capacity unknown) |
| Every archived artifact has a successor or an explicit `null` | Partly: the two named repos are specified; others unknown |
| Every section approved | Not met: all sections marked unapproved - assumed |

## 7. Order of work

1. This week: scan the two named repos, fix the CLI list, banner and `AGENTS.md` on both repos.
2. Week 1-2: build the register, so the index has real contents.
3. Week 2-3: create the index repo with its schema and CI.
4. Week 3-5: wire the CLI, docs build, CMS sync and README generator.
5. In parallel: add the UA suffix and key labels to the SDKs and samples.
6. Quarter 1 end: baseline review.

**Open decision for you:** who is the named index owner (A6)? Nothing past step 1 can start without one.