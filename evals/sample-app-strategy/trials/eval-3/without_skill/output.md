# Ferrowick samples: freshness contract, CI and bot setup

**Assumptions** (correct me if wrong):
- "$3 per full run" means one repo's live suite.
- The 4 CI repos are about the same size.
- Our API can enforce per-key spend caps, because we own it. If it can't, building that is a blocker (see Open questions).

## 0. Do this first

1. **Rotate the production key now.** Fork PRs have run the same workflow that holds it.
2. Audit for exposure:
   - Grep every workflow for `pull_request_target`, `workflow_run` and `secrets.`.
   - Check our API logs for that key from non-GitHub IPs, or at unusual volume.
3. Never use the production key in CI again. Section 3 replaces it with capped, scoped CI keys.

## 1. Why "all green" is currently meaningless

- **Bot PRs merged** counts bot activity, not whether a sample runs.
- **Days since last commit** punishes stable samples and rewards churn.
- Auto-merge has no required check. A PR that breaks the build merges anyway, and the dashboard counts it as a win.
- At 70 PRs a week, one person can't review anything. The volume hides the signal.

Delete both dashboard metrics. A sample with no commits for a year but a live pass this week is Fresh.

## 2. Freshness contract

**Owner:** Ravi. **Backup owner:** required, not named yet (see Open questions). If the owner is out more than 5 business days, the backup takes over.

### Definitions

- **Live pass:** the artifact ran against the production API with a CI key, on the current head of `main`. It used the latest committed lockfile, ran the README quickstart steps, and ended with exit 0. Provider 5xx and 429 get one retry. Two consecutive failures count as failed.
- **Offline pass:** the artifact ran against a mock built from the current published OpenAPI spec. It proves the code compiles and sends well-formed requests. It does not prove the API still behaves as shown.
- Only a live pass can turn an artifact Fresh. Offline passes gate merges.

### Thresholds

| Artifact | 🟢 Fresh | 🟠 Stale | 🔴 Broken | ⚪ Unverified |
|---|---|---|---|---|
| Sample repo | Live pass ≤ 8 days old. No open critical/high alert past SLA (critical 7 days, high 14 days). Runtime not EOL. | Live pass 9–14 days old. Or alert past SLA by ≤ 7 days. Or runtime EOL within 60 days. | Latest live run failed twice. Or live pass > 14 days old. Or critical alert > 14 days past SLA. | No live pass on record. |
| Postman collection | Live run of every request ≤ 8 days old. Hosted collection hash equals the git export. Covers 100% of public operations in the current spec. | Live run 9–14 days old. Or coverage < 100%. | A request fails. Or hosted ≠ git. | Never run. |
| Docs snippet | Live-verified ≤ 28 days ago, and its offline checks pass on `main`. | Live-verified 29–45 days ago. | Offline check fails. Or live run fails. | Never live-verified. |
| Illustrative snippet | Excluded. Labelled "not tested" on the page. | | | |

- Unverified renders grey, never green.
- The docs site as a whole is Fresh only when every runnable snippet is Fresh.

### Re-verification triggers

| Event | What re-runs | Cost |
|---|---|---|
| Push to `main` in a sample repo | Smoke test, then full live suite | ~$3 |
| Weekly schedule (Monday) | Same, skipped if `main` already passed live in the last 6 days | ~$3 |
| OpenAPI spec change in the API repo | Offline gate for all 7 repos, the Postman collection and all 400 snippets | $0 |
| SDK release | Bump PRs to the 7 repos, then the normal path | $0 until merge |
| Docs PR | Snippet offline tiers | $0 |
| Fork PR (any repo) | Offline only, no secrets | $0 |

### Evidence

Each live run writes `freshness.json`: commit SHA, API version, date, run URL, result, cost. The dashboard reads the latest `live` workflow run on `main` through the GitHub API. No new infrastructure.

### Failure handling

- A red state opens one issue per artifact, labelled `freshness-red`, assigned to the owner.
- The issue updates in place and closes itself on the next pass. Never one issue per run.
- **SLA:** triage within 2 business days, fix within 5.
- Red for more than 30 days: unpublish the repo or snippet, or add a "not currently verified" banner. Don't leave a broken sample looking healthy.
- While `main` is red, auto-merge is paused for that repo (section 4).

### Dashboard

Per artifact, show state, date of last live pass, API version tested, and open alerts past SLA. Show **bot PR backlog age** as an ops metric, not a health metric. Add nothing that counts activity.

### Review

Revisit this contract quarterly, or after the first red incident.

## 3. CI setup

### Three tiers

| Tier | Runs on | Secrets | Cost |
|---|---|---|---|
| 1. Offline gate (`ci.yml`) | Every PR, forks included | None | $0 |
| 2. Smoke (first job of `live.yml`) | Push to `main`, schedule, manual | CI key | cents (one request, tiny `max_tokens`) |
| 3. Full live (second job of `live.yml`) | Same as smoke, only if smoke passes | CI key | ~$3 |

### Keys

Create one CI key per repo, plus one for docs and one for Postman. If the API can't do this yet, see Open questions.
- Hard monthly spend cap per key: samples $40 (expected ~$13), docs $30, Postman $5.
- A `max_tokens` ceiling, a cheapest-model allowlist, and no billing or account endpoints.
- A rate limit.
- Rotation every 90 days.
- An alert to the owner above $10/day per key. Auto-revoke above 3× the cap.
- Store each as an **environment secret** in a `live` environment, never as a repo secret.
- Set the `live` environment's deployment branch policy to `main` only. Do not add required reviewers, because they would block scheduled runs.
- Dependabot PRs can't read Actions secrets anyway. That is fine, because they only need tier 1.

### Fork and supply-chain hardening (repo settings)

- Fork PR workflows: **require approval for all external contributors**.
- Leave "send secrets to workflows from fork PRs" and "send write tokens" **off**.
- Set the default `GITHUB_TOKEN` to read-only.
- Add `CODEOWNERS` on `.github/workflows/` so only the owner approves workflow changes.
- No `pull_request_target`, anywhere. `zizmor` in the gate fails the PR if one appears.
- Pin every action by SHA.
- `secrets.` may appear only in `live.yml`.

### `.github/workflows/ci.yml` (tier 1)

```yaml
name: ci
on:
  pull_request:
  push:
    branches: [main]
permissions:
  contents: read
jobs:
  offline-gate:
    runs-on: ubuntu-latest
    timeout-minutes: 10
    env:
      # Dummy key: the mock accepts anything, and no real credential exists in this job.
      FERROWICK_API_KEY: offline-dummy-key
      FERROWICK_BASE_URL: http://127.0.0.1:4010
    steps:
      - uses: actions/checkout@<sha>
        with: { persist-credentials: false }
      - uses: actions/setup-node@<sha>   # swap per repo language
        with: { node-version-file: .nvmrc, cache: npm }
      - run: npm ci
      - run: npm run lint && npm run typecheck
      - name: Workflow lint (fails on pull_request_target, template injection, unpinned actions)
        run: pipx run zizmor .github/workflows
      - name: Start mock from the current published spec
        run: |
          curl -fsSL "$OPENAPI_URL" -o /tmp/openapi.yaml
          npx @stoplight/prism-cli mock --errors -p 4010 /tmp/openapi.yaml &
          npx wait-on tcp:4010
        env:
          OPENAPI_URL: https://api.ferrowick.example/openapi.yaml   # placeholder
      - name: Run the README quickstart and the offline tests against the mock
        run: npm run test:offline
```

`--errors` makes Prism reject any request that violates the spec. A sample sending a removed field fails here, for free.

### `.github/workflows/live.yml` (tiers 2 and 3)

```yaml
name: live
on:
  push:
    branches: [main]
  schedule:
    - cron: "17 5 * * 1"
  workflow_dispatch:
concurrency:
  group: live
  cancel-in-progress: false
permissions:
  contents: read
  actions: read
  issues: write
jobs:
  plan:
    runs-on: ubuntu-latest
    outputs:
      run: ${{ steps.p.outputs.run }}
    steps:
      - id: p
        env: { GH_TOKEN: "${{ github.token }}" }
        run: |
          echo "run=true" >> "$GITHUB_OUTPUT"
          [ "$GITHUB_EVENT_NAME" = schedule ] || exit 0
          last=$(gh run list -R "$GITHUB_REPOSITORY" --workflow live.yml --branch main \
                 --status success --limit 1 --json createdAt --jq '.[0].createdAt // empty')
          # 518400 s = 6 days: the push-to-main run already covers this week.
          if [ -n "$last" ] && [ $(( $(date +%s) - $(date -d "$last" +%s) )) -lt 518400 ]; then
            echo "run=false" >> "$GITHUB_OUTPUT"
          fi
  smoke:
    needs: plan
    if: needs.plan.outputs.run == 'true'
    runs-on: ubuntu-latest
    environment: live
    timeout-minutes: 5
    steps:
      - uses: actions/checkout@<sha>
        with: { persist-credentials: false }
      - uses: actions/setup-node@<sha>
        with: { node-version-file: .nvmrc, cache: npm }
      - run: npm ci
      - run: npm run test:smoke      # one request, max_tokens <= 16
        env: { FERROWICK_API_KEY: "${{ secrets.FERROWICK_API_KEY_CI }}" }
  full:
    needs: smoke
    runs-on: ubuntu-latest
    environment: live
    timeout-minutes: 30
    steps:
      - uses: actions/checkout@<sha>
        with: { persist-credentials: false }
      - uses: actions/setup-node@<sha>
        with: { node-version-file: .nvmrc, cache: npm }
      - run: npm ci
      # The suite retries once, and only on 429/5xx. Assertion failures never retry.
      - run: npm run test:live
        env: { FERROWICK_API_KEY: "${{ secrets.FERROWICK_API_KEY_CI }}" }
      - run: node scripts/write-freshness.js > freshness.json
      - uses: actions/upload-artifact@<sha>
        with: { name: freshness, path: freshness.json }
  report:
    needs: [smoke, full]
    if: always() && needs.plan.outputs.run == 'true'
    runs-on: ubuntu-latest
    env: { GH_TOKEN: "${{ github.token }}" }
    steps:
      - name: Open, update or close the freshness issue
        run: |
          n=$(gh issue list -R "$GITHUB_REPOSITORY" -l freshness-red --state open --json number --jq '.[0].number // empty')
          if [ "${{ needs.full.result }}" = success ]; then
            [ -n "$n" ] && gh issue close "$n" -R "$GITHUB_REPOSITORY" -c "Live pass: $GITHUB_SERVER_URL/$GITHUB_REPOSITORY/actions/runs/$GITHUB_RUN_ID"
          elif [ -n "$n" ]; then
            gh issue comment "$n" -R "$GITHUB_REPOSITORY" -b "Still failing: $GITHUB_SERVER_URL/$GITHUB_REPOSITORY/actions/runs/$GITHUB_RUN_ID"
          else
            gh issue create -R "$GITHUB_REPOSITORY" -l freshness-red -t "Live run failed on main" \
              -b "Run: $GITHUB_SERVER_URL/$GITHUB_REPOSITORY/actions/runs/$GITHUB_RUN_ID"
          fi
```

Fix the shell precedence in the first branch before shipping: `[ -n "$n" ] && gh issue close` returns non-zero when there is no open issue, so wrap it in `if`. Test the workflow once with a deliberately broken key.

### Postman collection

- **Source of truth:** `postman/collection.json` in git, not the hosted copy.
- **Tests:** every request asserts status and validates the response against the OpenAPI schema. Use tiny `max_tokens`. Target under $0.10 a run.
- **Weekly job:** `postman collection run` on the git export using the Postman CLI. It uses the `live` environment's Postman CI key and a separate Postman API key. Compare the hosted collection's hash to the git export, and fail on drift.
- **Coverage check (free):** every operation in the current spec has at least one request.
- **Publish:** on merge, push the git export to the hosted collection through the Postman API. Stamp its description with "Last verified `<date>` against API `<version>`".
- **Key leak check (once):** confirm the hosted collection and its environments hold only `{{api_key}}` with an empty initial value, and no real key in its history.

## 4. Bot setup

### Volume

The target is 7 repos × 1 grouped PR a week, plus majors. Roughly 10 PRs a week, of which Ravi touches about 2: majors and gate failures. That is down from 70.

### `.github/dependabot.yml` (same in each repo; swap the ecosystem)

```yaml
version: 2
updates:
  - package-ecosystem: npm
    directory: /
    schedule:
      interval: weekly
      day: tuesday          # one day after the Monday live run
      time: "06:00"
      timezone: UTC
    cooldown:
      default-days: 5       # skip brand-new releases; most yanks and regressions surface within days
      semver-major-days: 30
    open-pull-requests-limit: 2
    groups:
      minor-and-patch:
        update-types: [minor, patch]
      security:
        applies-to: security-updates
        update-types: [minor, patch]
    labels: [dependencies]
  - package-ecosystem: github-actions
    directory: /
    schedule: { interval: weekly, day: tuesday, time: "06:00", timezone: UTC }
    groups:
      actions:
        patterns: ["*"]
```

- Grouping turns many PRs into one.
- The PR limit of 2 caps open majors.
- Security updates stay timely: they are grouped, but the grouped security PR opens as soon as an alert fires, not on Tuesday.

### Required check (the actual fix)

Add a ruleset on `main` in each repo:
- Require a PR.
- Require the status check `offline-gate`.
- Linear history.
- Enable "Allow auto-merge".
- No bypass for the bot.

Without a required check, GitHub auto-merge merges immediately. That is today's bug.

### `.github/workflows/dependabot-automerge.yml`

```yaml
name: dependabot-automerge
on: pull_request
permissions:
  contents: write
  pull-requests: write
  actions: read
jobs:
  automerge:
    if: github.event.pull_request.user.login == 'dependabot[bot]'
    runs-on: ubuntu-latest
    steps:
      - id: meta
        uses: dependabot/fetch-metadata@<sha>
        with: { github-token: "${{ secrets.GITHUB_TOKEN }}" }
      - name: Pause when main is red
        id: main
        env: { GH_TOKEN: "${{ github.token }}" }
        run: |
          c=$(gh run list -R "$GITHUB_REPOSITORY" --workflow live.yml --branch main \
              --status completed --limit 1 --json conclusion --jq '.[0].conclusion // "none"')
          echo "state=$c" >> "$GITHUB_OUTPUT"
      - name: Auto-merge minor and patch once offline-gate is green
        if: steps.meta.outputs.update-type != 'version-update:semver-major' && steps.main.outputs.state != 'failure'
        run: gh pr merge --auto --squash "$PR_URL"
        env:
          PR_URL: ${{ github.event.pull_request.html_url }}
          GH_TOKEN: ${{ github.token }}
```

- Majors never auto-merge.
- Auto-merge pauses while the last live run on `main` is failed.
- After a merge, the `live.yml` push trigger verifies `main` within minutes.
- Residual risk: a bad minor reaches `main` for a short window before the live run flags it. That is acceptable for sample code, and it costs Ravi one issue, not 70 PRs.

### SDK releases

Our SDK release pipeline opens one bump PR per sample repo, labelled `sdk-bump`. It goes through the same gate and live path. This is the highest-value freshness event, so it doesn't wait for Tuesday.

## 5. The 400 inline docs snippets

Same answer in three tiers, with the live tier rotated so cost stays bounded.

| Tier | What | Runs | Cost |
|---|---|---|---|
| T0 | Extract every runnable snippet to a file. Typecheck or syntax-check it against the pinned SDK. Validate its request body against the current OpenAPI schema. | Every docs PR, nightly, and on every spec change | $0 |
| T1 | Replay against recorded responses. Check the snippet's parsing code against the response shape. Re-record from live responses weekly. | Same | $0 |
| T2 | Execute live with the docs CI key, `max_tokens` ≤ 16, cheapest model. | Weekly | measure it (below) |

### Mechanics

1. **Classify once** with a one-off extraction script. Mark each snippet `runnable`, `runnable-with-fixture` or `illustrative`. Fragments are `illustrative`: labelled "not tested", excluded, never shown as verified.
2. Stop copy-pasting. Move snippets to `snippets/<id>.<lang>` and include them in MDX, so the file that runs is the file readers see.
3. **Live sampling:**
   - Group snippets by (endpoint × language × feature). Run one representative per group live every week. This is the 8-day Fresh bar for the group.
   - Rotate the rest so every snippet gets a live run at least every 28 days (about 100 a week).
4. The page shows "Verified against API vX on `<date>`" only when its snippets are Fresh. Derive that stamp from CI results, never by hand.
5. **Cost formula:** weekly live cost ≈ 100 × average cost per snippet call. At $0.01 that is ~$1/week. At $0.05 it is ~$5/week. Streaming or long-output snippets use T1 plus one live sample.
6. Fork PRs to docs run T0 and T1 only, with no secrets.

## 6. Cost

| Item | Weekly | Notes |
|---|---|---|
| 4 sample repos, one full run each | ~$12 | The push-to-`main` run replaces the Monday run when both fall in a week. |
| Extra runs from SDK releases and manual dispatch | $0–$12 | |
| Postman | < $0.50 | |
| Docs live tier | ~$1–$5 | Depends on cost per snippet. |
| **Monthly** | **~$65–$110** | Per-key caps hold the worst case at about $165/month. |

## 7. Rollout order

1. **Rotate the production key** and audit usage (section 0). ~1 hour.
2. **Create the capped CI keys.** Add them as `live` environment secrets with a `main`-only deployment branch policy.
3. **Merge `ci.yml`** and add the `main` ruleset requiring `offline-gate`. Fix the fork settings.
4. **Add `dependabot.yml`**, then **close the existing bot PRs** and let Dependabot re-open grouped ones.
5. **Merge `live.yml`.** Seed all states from the first run. Everything is Unverified until then.
6. **Merge `dependabot-automerge.yml`** only after one clean live run per repo.
7. **Postman:** export to git, add the weekly job, verify the hosted collection has no embedded key.
8. **Docs:** run the extraction script and read the classification counts. Then wire T0, T1, T2.
9. **Dashboard:** replace both metrics with the state table. ⚠️ Expect a lot of red and grey on day one. That is the real baseline.

## Open questions

1. Can our API enforce per-key spend caps, model allowlists and `max_tokens` ceilings today? If not, building them comes before step 2. A free, deterministic test mode would remove the $3 cost and most of this risk. I recommend building it as a follow-up.
2. Who is Ravi's backup owner?
3. What does an average snippet call cost? It sets the live tier size.
4. Which language and ecosystem does each of the 7 repos use? The Dependabot and workflow templates assume npm.