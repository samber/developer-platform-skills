# Ferrowick samples: freshness contract, CI and bot setup

All sections are **unapproved - assumed**. I skipped the interview and recorded my assumptions instead.

## Do today, before anything else (rule 1: a leaked credential overrides every verdict)

1. **Rotate the production key** held in Actions secrets. Fork PRs ran the same workflow with it. Either "send secrets to fork PRs" is on, or a workflow uses `pull_request_target`. Treat the key as exposed.
2. Check the old key's usage logs for unknown IPs, volume spikes and odd models. You own the API, so you can see them.
3. Run a secret scan and a dependency vulnerability scan on all 7 repos, including git history.
4. **Turn off bot auto-merge on all 7 repos.** Today it merges untested dependency changes weekly. That is why the dashboard is green.
5. Remove the key from any Postman collection, environment or fork that holds it.

Estimate: about 2 hours for steps 1-4, plus 30 minutes for step 5. Both are self-set.

## Assumptions to confirm

- **A1:** "$3 per full run" means per repo, so 4 repos cost about $12 per weekly cycle.
- **A2:** Which 4 repos have CI, and which of the 7 are on the adoption path (quickstart, auth, first call), is unknown. The register is not built yet.
- **A3:** You can mint a separate API key with a hard spend cap, a rate limit and a token ceiling. You own the platform, so this should be cheap. It is the interim stand-in for a sandbox, not the sandbox itself.
- **A4:** GitHub Actions with Renovate. If you use Dependabot, the same cadence and grouping apply.
- **A5:** Ravi's fallback decider is not named. The SLA below needs one.

## Dashboard verdict

All 7 repos are really **unknown**, not green.

- "Bot PRs merged" counts the thing that breaks repos, because merges have no CI gate.
- "Days since last commit" is reset by the bot's own commits. It measures the bot, not health.
- Replace both with these columns:
  - Owner.
  - Date of last green live run.
  - Open red-build issue age.
  - Oldest unmerged dependency PR age.
  - CI pass rate over the quarter.
- Show every repo as `unverified` until its first baseline live run.

## 1. Freshness contract

Every kept repo signs it. A repo that can't is not kept.

**Clause 1: CI target and schedule.** There is no sandbox, so CI splits in two:

| Layer | Trigger | Secrets | Proves |
| --- | --- | --- | --- |
| Build, lint, type-check, replay tests on recorded fixtures | every PR, including forks, and push to main | none | Code builds and handles recorded responses. Label: **compiled, not run**. |
| Live smoke against production | weekly schedule, SDK release, API version change, manual | scoped CI key, `live-api` environment, `main` only | The sample works against the current API. |

- Replay tests don't prove live behavior. Keep the "compiled, not run" label on every repo until its live smoke has been green.
- **Never run live smoke on PRs.** That covers fork PRs, bot PRs and `pull_request_target`.
- A malicious or compromised dependency update would otherwise run with the key.
- Post-merge detection is acceptable because Ravi reviews every grouped PR by hand.
- Live smoke is limited to the 4 repos with CI (A2). The other 3 get the PR layer only. That keeps live cost near $624 a year plus event runs, against about $1,100 for all 7.
- **First queue item after cleanup:** build a real test mode. See `samber/developer-platform-skills@api-test-mode-design`. Once it exists, run the live layer on PRs against it and enable automerge.

**Clause 2: Scoped credentials.**

- Mint one dedicated CI key. Set a hard monthly spend cap of about $100 (self-set, roughly 2x the expected $52).
- Add a token ceiling and a rate limit, and tag its traffic as `ferrowick-sample/<sample-id>` in the user-agent. That gives you the per-sample traffic the measurement plan needs.
- Store it only in the `live-api` environment, restricted to `main`. Delete every repo-level copy.
- Rotate it quarterly and on any suspected exposure.
- Smoke tests send tiny requests (`max_tokens` about 16) and use the cheapest model that exercises the code path. Measure the real cost after the first baseline run.
- If a sample creates files, batches or other server state, delete them in an `if: always()` step.
- Pin every GitHub Action by digest, since a workflow now holds a secret.

**Clause 3: Dependency updates.**

- Updates are grouped, throttled and never auto-merged (see the bot config below).
- Security alerts bypass the cadence.

**Clause 4: Red-build SLA (all numbers self-set).**

- An issue labelled `red-build` is opened automatically on the first red live run, assigned to the owner.
- A fix-or-deprecate decision is forced at 14 days red.
- A deprecated repo is archived after 30 more days.
- Fallback decider if Ravi is absent: `<named sign-off owner>`. This is needed; without it the SLA never fires.
- A red adoption-path repo is never archived for lack of an owner. It escalates to the fallback decider.

**Clause 5: Pinned versions.**

- Each repo has a `versions.json` listing its SDK major, runtime and API version.
- CI checks it against the SDK support window and the API versioning policy.
- A pin outside the window turns the PR check red.

## 2. CI workflows

Copy these into each repo. Pick a different cron day and minute per repo so the live runs don't pile up.

`.github/workflows/pr.yml` (no secrets, safe for forks):

```yaml
name: pr
on:
  pull_request:
  push:
    branches: [main]
permissions:
  contents: read
jobs:
  build:
    runs-on: ubuntu-latest
    timeout-minutes: 10
    steps:
      - uses: actions/checkout@<pinned-sha>
      - name: Forbid pull_request_target
        run: '! grep -rn "pull_request_target" .github/workflows'
      - name: Install, lint, type-check, replay fixtures
        run: make ci   # no network calls to Ferrowick; fixtures are recorded
```

`.github/workflows/live-smoke.yml`:

```yaml
name: live-smoke
on:
  schedule:
    - cron: "17 6 * * 2"   # weekly; vary day and minute per repo
  workflow_dispatch:
  repository_dispatch:
    types: [sdk-release, api-version-change]
permissions:
  contents: read
  issues: write
concurrency:
  group: live-smoke
  cancel-in-progress: false
jobs:
  live:
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    timeout-minutes: 15
    environment: live-api
    env:
      FERROWICK_API_KEY: ${{ secrets.FERROWICK_CI_KEY }}
      FERROWICK_MAX_TOKENS: "16"
    steps:
      - uses: actions/checkout@<pinned-sha>
      - name: Run live smoke
        run: make live-smoke
      - name: Clean up server-side fixtures
        if: always()
        run: make live-cleanup
      - name: Open red-build ticket
        if: failure()
        env:
          GH_TOKEN: ${{ github.token }}
        run: |
          open=$(gh issue list --label red-build --state open --json number --jq length)
          if [ "$open" = "0" ]; then
            gh issue create --label red-build --assignee <ravi-github-handle> \
              --title "live-smoke red: ${GITHUB_REPOSITORY}" \
              --body "Run: ${GITHUB_SERVER_URL}/${GITHUB_REPOSITORY}/actions/runs/${GITHUB_RUN_ID}"
          fi
```

- Send the `sdk-release` and `api-version-change` dispatches from your platform's release pipeline.
- Repo settings, on all 7:
  - Actions > "Fork pull request workflows": require approval for all outside contributors.
  - Confirm "Send secrets to workflows from fork pull requests" is off.
  - Enable secret scanning with push protection and vulnerability alerts.

## 3. Bot setup

`renovate.json` per repo. Change the day of month (`8`) per repo (1-7 and so on) so the monthly PRs don't all land on one day.

```json
{
  "extends": ["config:recommended", "helpers:pinGitHubActionDigests"],
  "dependencyDashboard": true,
  "prConcurrentLimit": 3,
  "prHourlyLimit": 2,
  "minimumReleaseAge": "7 days",
  "automerge": false,
  "packageRules": [
    { "matchUpdateTypes": ["minor", "digest"], "groupName": "minor updates", "schedule": ["* 0-3 8 * *"] },
    { "matchUpdateTypes": ["patch"], "groupName": "patch updates", "schedule": ["* 0-3 8 1,4,7,10 *"] },
    { "matchUpdateTypes": ["major"], "dependencyDashboardApproval": true }
  ],
  "vulnerabilityAlerts": { "schedule": ["at any time"], "labels": ["security"] },
  "ignorePaths": ["legacy/**"]
}
```

- Verify that `minimumReleaseAge` doesn't delay security PRs in your setup.
- Cadence follows Google's `python-docs-samples`: minor monthly, patch quarterly, alerts any time.
- Expected volume for 7 repos is about 16 grouped PRs per repo per year, or about 2 a week on average. Add roughly 1 a week for majors and alerts.
- That is down from 70. Estimates are self-set.
- Ravi's load drops to about 1 hour a week, at about 20 minutes per grouped PR.
- **Close the existing open bot PRs.** Let the dashboard regenerate them under the new groups.
- Merge rule: Ravi merges only after `pr.yml` is green. Then he runs `live-smoke` by hand (`workflow_dispatch`) on any PR that touched runtime dependencies.
- Automerge returns only when a sandbox lets the live layer run on the PR itself. Even then, restrict it to patch and minor updates behind required checks.

## 4. Postman collection

A hosted collection has no build. Test it as a contract.

1. Statically validate the collection against the OpenAPI spec on every spec change. No calls, no key.
2. Run it with Newman in `live-smoke` on every API spec change, with the `live-api` key and tiny `max_tokens`. Use cheap endpoints (auth check, model list) wherever possible.
3. The collection must hold no key. Use an empty `{{api_key}}` variable. Audit the public workspace, its forks and its environments now.
4. Label it "validated against spec; live-checked on spec change, date X".

## 5. The 400 docs snippets

The tier policy comes from `samber/developer-relations-skills@docs-code-sample-standards`. I inherit it and do not rewrite it. What changes here is the no-sandbox constraint.

- **Inventory first.** Run `scripts/sample-audit.py docs/ --format summary` for the census and its secret-shaped-literal flag. I have not run it. Fix any P0 hit this week.
- **Tier every snippet** as Run, Compile-only or Illustrative. Untiered defaults to Run.
- **Compile-only** is the default for the bulk of the 400.
  - Extract the snippets, then build and type-check them per PR with no secrets.
  - Fork-safe. The docs build fails when a snippet fails.
  - The page labels them "valid, not run for you".
- **Run** is limited to the adoption path (quickstart, auth, first call) and the top copy-button snippets.
  - They join the same `live-smoke` job and share the capped key and its spend cap.
  - Cost per snippet is unknown. Measure it in the first baseline run before promoting any more snippets to Run.
- **Illustrative** snippets carry a visible label on the page.
- No snippet claims "works as written" unless it is in Run and green.
- A sandbox, once built, promotes Run broadly.

## 6. Order of work and estimates

Self-set estimates. The one-off total is about 3 working days, or about 25 hours.

1. Rotate the key, scan all 7 repos, disable automerge (about 2.5 hours, today).
2. Mint the capped CI key and create the `live-api` environments (about 1 hour).
3. Add `pr.yml` and the fork settings to all 7 repos (about 3 hours).
4. Add `live-smoke.yml` to the 4 CI repos and run one baseline by hand (about 4 hours, about $12).
5. Replace the dashboard columns (about 2 hours).
6. Swap in the Renovate config and close the old bot PRs (about 2 hours).
7. Do the Postman checks and the snippet census (about 1 day).

Steady-state upkeep is under 2 hours a week for Ravi.

## 7. Open questions

1. Which 4 repos have CI, and which of the 7 are on the adoption path?
2. Who is the fallback decider when Ravi is absent?
3. Is the $3 per repo or for the whole run?
4. Can you mint a capped key today?

Next: do steps 1-4 of "Do today" and tell me when the key is rotated.