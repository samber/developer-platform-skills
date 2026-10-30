# Halloway Maps samples: discoverability layer and measurement plan

I made no assumptions about your repos. I did not read `skill-wip/`, as instructed. Everything below comes from your brief.

## 1. Diagnosis

- Four hand-edited lists have no owner and no single source of truth, so they drift.
- Archiving a repo only changes GitHub state. Nothing propagates to the CLI, the docs, the CMS or the README.
- Assistants scaffold from `geocode-express-old` because the repo still looks alive: it's indexed, it has stars, and nothing machine-readable says "superseded".
- Old CLI binaries in the wild keep their hard-coded list forever. Fixing the CLI source does not fix those installs.

## 2. Discoverability layer

### 2.1 One registry, everything else generated

Create `samples.yaml` in a single repo. Every other surface is a build artifact. Nobody hand-edits them.

```yaml
- id: geocode-express
  title: Geocoding with Express
  repo: halloway-maps-samples/geocode-express
  status: active            # active | deprecated | archived
  replaced_by: null         # required when status != active
  supersedes: [geocode-express-old]
  sdk: { node: ">=3.2" }
  apis: [geocoding]
  last_verified: 2026-10-28 # written by CI, never by hand
  owner: team-or-handle
```

Rules:
- `status: archived` requires `replaced_by` (or an explicit `none: reason`). CI fails otherwise.
- Archived entries are never deleted from the registry. They are the tombstone data that every other surface reads.
- Every sample needs a named `owner`, and ownerless samples are flagged as at-risk.

### 2.2 Generated surfaces

| Surface | How it's fed |
|---|---|
| Docs pages | A build step renders the registry into the samples pages. Hand-written prose stays, the lists don't. |
| Marketing CMS gallery | A sync job pushes active entries only, via the CMS API. The CMS is read-only for the sample list. |
| `hw samples list` / `scaffold` | The CLI fetches the published `samples.json` (CDN, ETag, cached 24h). A snapshot embedded at build time is the offline fallback, and it expires after 90 days with a warning. |
| Org README | A generated block between markers, committed by a bot. |
| Agents and crawlers | `/samples.json`, a samples section in `llms.txt`, and a `sample-status` field in each repo's `AGENTS.md`. |

The CLI no longer hard-codes anything. The embedded fallback is generated from the same registry at release time.

### 2.3 Lifecycle: how a sample dies without haunting you

Run this checklist as a script when status changes to `deprecated` or `archived`:

1. Set `status` and `replaced_by` in the registry.
2. In the repo: replace the README with a 5-line tombstone, and add a `DEPRECATED.md` and an `AGENTS.md`. All three say "Do not use. Use `<replacement>`: link."
3. Edit the GitHub description to start with `[ARCHIVED → geocode-express]`. Then archive the repo (unarchive, edit, re-archive if it's already archived).
4. Remove the topics that drive search (`geocoding`, `halloway`, and so on). Add `deprecated`.
5. Deprecate any published packages (npm deprecate, PyPI yank notice) with the replacement in the message.
6. Docs: keep a stub page that redirects to the replacement. Never 404.
7. CLI: the registry keeps the id. `hw samples scaffold routing-v1-demo` now prints "archived March 2026, use `<x>`" and exits non-zero. It does not silently work or silently vanish.

**Naming:** new sample ids are stable and carry no `-old`, `-demo` or `-v1` suffix that implies a version fork. When a breaking rewrite is needed, deprecate the old id and create a new one. Don't rename in place.

### 2.4 Keeping the layer honest (CI gates)

- **Nightly verify:** build and run each active sample against the latest SDK with a smoke call. On success it writes `last_verified`. A sample unverified for more than 30 days is demoted to `deprecated` automatically, with an issue opened for the owner.
- **Drift check (daily):** diff each generated surface against the registry. Any mismatch fails the job and pages the registry owner. This covers CMS, docs, README and the published `samples.json`.
- **Orphan check:** list every repo in the samples org. Anything not in the registry is flagged, and a repo that is unarchived but marked archived is flagged too.
- **Reference check:** grep docs, blog and README for links to non-active sample repos.
- **Registry PR template:** one checklist covering the lifecycle in 2.3.

### 2.5 The assistant problem

You can't edit what a model already learned. You can make the live web and retrieval agree, and you can measure how long the lag lasts.

- Tombstone content (2.3 step 2) is the main lever. Assistants with web access or repo reading see "deprecated" first.
- Do not delete or rename the old repo. Deletion removes the signal, and GitHub redirects keep old links resolving to the tombstone.
- Publish `llms.txt` and `/samples.json` with an explicit "Deprecated, do not scaffold from" section naming the old ids.
- Add the same warning to docs pages and to the SDK READMEs, since assistants read those.
- Expect lag of one or more model release cycles for assistants without web access. Treat that as a known residual, and measure it in section 3.

### 2.6 Old CLI installs

Old binaries still list `routing-v1-demo`. I don't know whether they clone the repo directly or call your API. Open question 1 below. Either way, the tombstone README and archived-repo banner cover the clone-directly case. If scaffolding goes through your API, add a server-side deny and redirect message keyed by sample id. Also add a "new CLI version available" notice to `hw samples list`.

## 3. Measurement plan

### 3.1 What question are we answering?

Do developers who start from a sample reach a working integration, from a sample that is current? Stars and clones do not answer that.

### 3.2 Why not marketing's KPI as the headline

- **Clone counts** from the GitHub traffic API retain only 14 days. A quarterly review needs daily snapshots you don't have. Clones also include CI runs, bots and mirrors.
- **Stars** measure interest and repo age, not working integrations. They favor old repos, which is the exact bug here: `geocode-express-old` is probably your highest-starred sample.
- **Per-repo targets** punish consolidation. Retiring a duplicate sample would "lose" its KPI.
- **Quarterly** is too slow. The drift problem lives in days.

Keep both numbers on the dashboard as context, snapshotted daily from now. Set no targets on them.

### 3.3 Metrics

**A. Integrity (weekly, hard targets)**

| Metric | Target |
|---|---|
| Surfaces disagreeing with the registry | 0 |
| Non-active samples offered by CLI, docs or CMS | 0 |
| Active samples verified green in the last 30 days | 100% |
| Repos in the org not in the registry | 0 |

**B. Adoption (monthly, baseline first)**

1. Extend the SDK user-agent with an optional sample id: `halloway-node/3.2.1 sample/geocode-express@1.4`. Use an `appInfo`-style option, plus an env var for cases without code changes. Every sample sets it at client init.
2. Server-side, aggregate by hashed API key or org, not by person:
   - **Sample-attributed activation:** keys whose first successful call carries a sample id, within 7 days of key creation.
   - **Sample-to-sustained use:** those keys still calling on day 30.
   - **Time to first successful call**, by sample.
3. Scaffold counts come server-side from the registry's tarball or API endpoint, so the CLI needs no new client telemetry.

**C. Staleness leakage (the metric for this problem)**

- **Stale-sample traffic:** distinct keys per week sending a sample id that is `deprecated` or `archived`.
- **Proxy for archived samples that predate the sample id:** SDK versions pinned only in their lockfiles. Treat it as a noisy estimate and label it so.
- **Old-CLI share:** the fraction of scaffold requests from CLI versions with the hard-coded list.

**D. Assistant check (monthly)**

- A fixed set of about 20 prompts ("build a geocoding Express app with Halloway") run against 3–4 assistants, with and without web access.
- Record which repo, sample id and SDK version each answer uses. Run each prompt at least 5 times, because output is stochastic.
- Report the share of answers pointing to an active sample, and the share pointing to an archived one.
- Also track `llms.txt` and `samples.json` fetches by known AI-crawler user-agents, as a leading indicator.

### 3.4 Caveats to state in the report

- Users who copy code and strip the user-agent are invisible. Read the numbers as trends, not totals.
- The sample id is an identifier in a header, so it carries no personal data. Keep it that way: no repo path, no user fields. Run it past whoever owns your privacy policy.
- Attribution is last-touch to a sample. It does not prove the sample caused the activation.
- Don't set targets for sections B–D until 4 weeks of baseline exist. I'd rather not invent numbers.

### 3.5 Cadence

| Cadence | Review |
|---|---|
| Daily | Drift, orphan and verify gates (automated) |
| Weekly | Integrity and stale-traffic dashboard, 10 minutes |
| Monthly | Adoption funnel and assistant probe |
| Quarterly | Which samples to retire, merge or add, using adoption data (stars as a footnote) |

## 4. Rollout

1. **Days 1–2:**
   - Cut the CLI release that drops `routing-v1-demo`.
   - Put tombstones on the two known offenders (`routing-v1-demo`, `geocode-express-old`).
   - Start daily snapshots of stars and clones so a baseline exists.
2. **Week 1–2:** write the registry from the four lists, resolving each disagreement with a human decision. Add the drift check first, before the generators.
3. **Week 2–4:**
   - Add the generators: docs, CMS sync, README block, CLI fetch.
   - Add the nightly verify.
4. **Week 3–5:** ship the SDK `appInfo` option, update the samples, and add the server-side aggregation.
5. **Week 5–8:** run the first assistant probe and collect the baseline. Then set targets for B–D.

## 5. Open questions

1. When the old CLI scaffolds, does it clone the repo directly, or call a Halloway endpoint?
2. Who owns the registry? One named owner is the difference between this working and drifting again.
3. Is the marketing CMS able to take API-driven sync, or do they need a manual import step?
4. Are any samples published as packages (npm, PyPI) that need deprecation notices?
5. Is attributing activation by hashed key or org acceptable under your data policy?
6. Do you want marketing's stars and clones kept as a published vanity number? I'd keep them off the KPI list but on the dashboard.

I'd start with step 1 of the rollout, since the CLI fix and the two tombstones don't depend on any decision above.