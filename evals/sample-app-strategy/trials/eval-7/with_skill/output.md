**Next action:** run the inventory script in section 1 (about 10 minutes) and paste me the output. I haven't seen your repos, your API, your error catalog, or your traffic by language. Everything below rests on assumptions, and each affected section is marked **unapproved - assumed**. No section is approved yet, so the pass gate is 0 of 4. I wrote no files.

## Short answers

1. **SDK languages:** Go next, then Java or Ruby. This is provisional and has no traffic data behind it. Do not start before the hackathon.
2. **Sandbox:** soft toggle (test keys write to a separate test partition), built in weeks 1-3. It gates the quickstart, CI, and the hackathon.
3. **Quickstart:** drafted in section 4. It stays a draft until a cold run passes against the sandbox.
4. **Examples:** I can't triage 14 repos I haven't seen. Section 1 gives the register script and the rule order. Section 2 gives the target shape.
5. **Hackathon demo app instead of all this?** No. A standalone demo is a reference app, the most expensive artifact to maintain. Build it last, as a scenario in the shared samples repo, and only if weeks 1-3 land.

## 1. Inventory and baseline (unapproved - assumed)

Run this first. It **writes files to /tmp**. Replace the two org names.

```bash
for org in <CURRENT_ORG> <OLD_ORG>; do
  gh repo list "$org" --limit 200 \
    --json name,url,isArchived,isTemplate,pushedAt,primaryLanguage \
    > "/tmp/samples-$org.json"
  for repo in $(gh repo list "$org" --limit 200 --json name -q '.[].name'); do
    gh run list -R "$org/$repo" --limit 1 --json conclusion,createdAt \
      > "/tmp/samples-$org-$repo-ci.json"
  done
done
```

Then, per repo, in a fresh clone directory:
- Run `gitleaks detect` for secrets.
- Run `osv-scanner` for vulnerable dependencies.

A secret or vulnerability hit overrides every later verdict (fix or archive this week).

Register columns, one row per repo:
- Scenario ID, shared across languages of the same scenario.
- Type and job.
- SDK major pinned.
- **Owner:** a named person, so for now you.
- Last green CI.
- Usage signal. Write `not measured`, never zero.
- Tickets naming the sample.
- Inbound links: docs, sales decks, blog posts, old-org README pointers.

An `unknown` CI cell or an ownerless row is itself a finding.

**Triage order (first match wins).** Apply it after the scans:
1. Leaked credential or vulnerable dependency: fix or archive this week.
2. Targets a retired SDK major or API version: archive with redirect. Targets a language the target shape drops: community label if it is green and someone accepts it, otherwise archive with redirect.
3. On the adoption path (quickstart, auth, first call, top-ticket scenario): fix in place, or rebuild if the fix costs more.
4. Nobody accepts ownership: archive with redirect.
5. Duplicates another row's job and language: merge.
6. Single-concern sample in its own repo: merge into the shared samples repo.
7. Red, and usage measured near zero: archive with redirect.
8. Otherwise: keep, and sign the freshness contract.

**Predictions to check against the output (unconfirmed guesses):**
- Most old-org repos will match rule 2 or 4 and get archived.
- Per-language copies of one scenario will merge.
- Without a sandbox, CI cannot run the samples. Every kept row is "compiled, not run" until section 3 ships.

**Veto and link rules:**
- Linked from a sales deck or partner page: swap the link first, then archive.
- Usage not measured: decide on tickets and inbound links, and say so in the row.
- With a 5-week deadline, move borderline fix rows to merge or archive.
- If someone vetoes an archive, relabel the row community-maintained. A red row gets "currently failing CI" in its banner.
- Never delete a repo.

## 2. Portfolio shape and coverage (unapproved - assumed)

**Chosen shape: lean golden path.** You are solo, and it has the lowest upkeep. Gallery-led needs curated intake and per-template telemetry. Reference-app anchored needs a regulated or multi-service flow driving deals, which I have no evidence of.

| Developer job | Artifact | Status |
| --- | --- | --- |
| Evaluate without installing | Hosted collection, preloaded with a sandbox key | Build after the sandbox |
| First call | Flagship quickstart repo, one folder per language | Build (section 4) |
| Integrate one workflow | Scenario samples in one shared repo | Merge existing repos here |
| Production pattern | Docs architecture page | Reference app not served. Add if a regulated or multi-service flow drives deals. |
| Start a project | Starter template | Not served. Add if telemetry shows framework concentration. |
| Mobile or device | None | Not served. Add if a mobile SDK reaches tier 1. |
| Coding agents | Canonical index plus agent guide | Build (section 5) |

**Coverage rules:**
- Full language parity goes to the flagship only.
- Scenarios ship in the 2-3 languages that dominate API traffic.
- Everything else is community-labelled or absent, and the tier table is published.
- Scenario names below are placeholders. Replace them with your top-ticket workflows.

**Capacity sum.** The upkeep numbers are my self-set estimates, and your hours are assumed at 24 per quarter. Tell me your real number.

| Item | Calculation | Hours/quarter |
| --- | --- | --- |
| Flagship | 2 languages × 4 h | 8 |
| Scenarios | 4 scenarios × 2 languages × 1 h | 8 |
| Hosted collection | | 1 |
| CI harness and index | | 2 |
| **Total** | | **19 of 24** |

- Adding Go to the flagship adds 4 hours, for 23 of 24.
- Java would break the cap. If Java is promoted, cut a scenario language first.
- Cleanup is budgeted separately at about 25 one-off hours (self-set): scans, register, about 10 archives, merges. The sandbox work, quickstart, and CI harness come on top.

## 3. Sandbox design (unapproved - assumed)

**Domain.** Analytics ingestion carries real end-user data, so the "no test mode, integrator convention" option is ruled out. A documented "use a separate project" convention is not a sandbox. I'd use it only as a hackathon-only stopgap, and say so in the docs.

**Isolation model: soft toggle.**
- One account. Keys with a `_test_` mode substring route to a separate test partition.
- Every event and project carries a mode flag.
- Live reads never see test data, and test reads never see live data.
- Test events are never metered or billed.
- State this isolation level in the docs.
- Hard separate-copy is deferred. It returns on the first cross-mode leakage incident or a compliance requirement.
- Estimate: 1-2 weeks of platform engineering, mostly leak testing. **Who builds this?** If it's not you, week 1 includes handing eng the spec below.

**Keys.**
- Use a type prefix plus a `_test_` / `_live_` mode substring, so leak scanning can match the shape.
- Live keys reject test-only magic values. Test keys reject production-only operations.
- A live key against test routing, or the reverse, returns a clear `wrong_environment` error, never a bare 401.
- Test keys still write test-project configuration. Treat them as secrets.

**Failure paths.**
- The magic value is the `distinct_id` or event name, active only under test keys (in live mode, they are ordinary data).
- Each value must trigger the real error code from your published catalog. Fill that column from your catalog.
- Do not invent sandbox-only error shapes.

| Test value | Outcome | Your real error code |
| --- | --- | --- |
| `distinct_id: test_rate_limited` | Rate limit | fill in |
| `distinct_id: test_quota_exceeded` | Plan quota exceeded | fill in |
| `event: test_malformed` | Payload validation failure | fill in |
| `event: test_oversize_batch` | Batch too large | fill in |
| `timestamp` far in the past or future | Rejected timestamp | fill in |
| Repeated `event_id` | Duplicate or idempotent replay | fill in |

Treat these values as contract: stable and never removed. Add or drop rows to match your real error catalog.

**Simulation endpoints (sandbox-only):**
- `POST /sandbox/seed` loads a named synthetic dataset, for example a SaaS signup-to-purchase funnel with several weeks of history. Retention and funnel queries work on day one with no waiting.
- `POST /sandbox/reset` wipes the test partition. Also schedule a periodic automatic reset.
- Auto-aging: seeded timestamps shift daily so "last 7 days" is never empty.
- Read-your-writes: under test keys, a query sees an event the moment `capture` returns (or via `POST /sandbox/flush`). Without this, the quickstart's "query returns what you sent" fails randomly on ingest lag, and CI flakes.
- A clock-advance primitive is a stub for now. Build it only if alerts or scheduled jobs need time to pass. If you have webhooks or alert deliveries, add a "fire this event now" trigger per event type.

**Quotas.** Reuse production rate limits in test mode, so integrators' throttling code stays honest. Add one aggregate daily event cap per test project, to stop free-storage abuse. Self-set the number.

**Graduation.** Probably no compliance gate. The checklist:
1. Swap keys everywhere.
2. Create live project IDs.
3. Send one live canary event.
4. Confirm it appears in the live project and not in the test project.
5. Recreate any webhook or alert endpoints with live secrets.

A green sandbox run does not predict real volume or real latency. Say that in the docs.

**Gates (100% each):**
- Every documented failure path is triggerable by a magic value or endpoint.
- Every async event is fireable on demand.
- Cross-environment auth tickets: target zero, achieved structurally by the prefixes and the clear error.

## 4. Quickstart page (draft, unverified - assumed names)

- **Success moment:** the query returns the event you just sent.
- **Time budget:** 5 minutes (hosted API baseline, and a commitment).
- **Assumed names, replace before publishing:** package `oakhurst-signals`, class `Signals`, methods `capture` and `events.list`, env var `OAKHURST_API_KEY`. Python is the single happy path, which I assumed. If JS dominates your traffic, swap to JS.
- **Signup:** I wrote a self-serve test key with no card. The strongest form is no account at all. Ask platform eng whether a temporary anonymous test key is feasible.

~~~markdown
# Quickstart: send your first event and read it back

In about 5 minutes you send one event to Oakhurst Signals and query it back.
You use a test key, so nothing touches production data.

## Before you start

- Python 3.9 or later. Check: `python --version`
- A test API key. Create one under **Settings > API keys > Create test key**.
  Test keys start with `<TEST_KEY_PREFIX>`.

## 1. Install the SDK

```
pip install oakhurst-signals==1.*
```

Expected output ends with:

```
Successfully installed oakhurst-signals-1.x.x
```

If `pip` is not found, run `python -m pip install oakhurst-signals==1.*`.

## 2. Set your test key

```
export OAKHURST_API_KEY=<YOUR_TEST_KEY>
```

The command prints nothing. Check it with `echo "$OAKHURST_API_KEY"`.
If the output is empty, you set the variable in another shell. Run the export again here.

## 3. Send an event

Create `send.py` with this full content:

```python
import os
from oakhurst_signals import Signals

client = Signals(api_key=os.environ["OAKHURST_API_KEY"])

client.capture(
    distinct_id="quickstart-user-1",
    event="quickstart_completed",
    properties={"plan": "free"},
)
print("sent")
```

Run it:

```
python send.py
```

Expected output:

```
sent
```

If you see `wrong_environment`, you used a live key. Create a test key and try again.
If you see `KeyError: 'OAKHURST_API_KEY'`, repeat step 2 in this shell.

## 4. Read the event back

Create `read.py` with this full content:

```python
import os
from oakhurst_signals import Signals

client = Signals(api_key=os.environ["OAKHURST_API_KEY"])

events = client.events.list(distinct_id="quickstart-user-1", limit=1)
print(events[0].event, events[0].properties)
```

Run it:

```
python read.py
```

Expected output:

```
quickstart_completed {'plan': 'free'}
```

If you see `IndexError`, run `python send.py` again, then retry.
Test keys read their own writes immediately.

## You are done

You sent an event and your query returned it. Next:

- [Track events from your server](<LINK>): the most common second task
- [API reference](<LINK>)
- [Get help](<LINK>)
~~~

**Verification plan (required before publish).** Someone other than the author runs it on a clean machine with a fresh test key, all five must hold:
1. Every command succeeds exactly as written.
2. Real output matches the documented output.
3. No prerequisite appears after the first step.
4. Elapsed time is 5 minutes or less. If not, shrink the success moment, never extend the budget.
5. The reader reaches success without leaving the page.

**Instrumentation (build after publish):**
- Step-level events, from which median time to success and completion rate follow.
- Support tickets quoting a step.
- Run these exact commands in CI weekly and on every SDK release.
- Baseline for 4 weeks before setting any target.

## 5. Freshness, archive, discoverability, measurement (unapproved - assumed)

**Freshness contract (every kept artifact signs it):**
1. Scheduled CI against the sandbox, plus a run on every SDK release and API version change.
2. Sandbox-only CI keys, hidden from fork PRs, rotated on a schedule.
3. Grouped dependency updates: minor monthly, patch quarterly, security alerts any time, automerge only behind green sandbox CI.
4. Red-build SLA, all self-set:
   - An owner ticket on the first red run, automated.
   - A fix-or-deprecate decision after 14 days red.
   - Archive after 30 days deprecated.
   - You decide while you are the only owner.
5. Pinned SDK major, runtime, and API version, checked against support windows.

**Archive rules.**
- Triggers: red past the SLA, no owner for a quarter outside the adoption path, superseded by a merged artifact, or the pinned SDK or API reached end of life.
- Never archive on age alone.
- Sequence: README banner with successor link, remove deploy buttons, update the index, fix docs links, stop bots and CI, last secret scan, archive read-only, changelog note if it was on the adoption path.
- Old-org repos get a banner and a redirect, not deletion.

**Canonical index.**
- One JSON file with ID, type, job, languages, status, successor, and an `aliases` / `deprecated` section.
- Docs links, the gallery, a scaffold CLI that writes the test key into `.env`, GitHub topics, and the agent guide all read it.
- Coding agents ingest archived repos as readily as current ones, so the index must say what is current.

**Measurement.**
- Tag SDK user-agent or app-info with the sample ID.
- Four signals per artifact: tagged invocations, time to first successful sandbox call, tickets naming it, quarterly CI pass rate.
- Stars and forks are reported, never decisive.
- Baseline in quarter 1.

## 6. SDK languages next (unapproved - assumed)

**Reasoning.** I'm treating Oakhurst Signals as a dev-tools or data platform. That vertical front-loads Python and TypeScript, then expands to Go, Java, Kotlin, Ruby. You have two of those already. Go is next. This is an inference from the vertical pattern, not from your traffic.

**Portfolio shape.** Lean core plus a self-service long tail: 3-4 official SDKs, everything else generated from your published spec.

**Promotion rule (self-set):** promote a language to official when it has a sustained double-digit share of API traffic, or repeated named deal requests. Until then it is community or spec-generated.

**Do now (about 2 hours):** add a language tag to the SDK user-agent and read the per-language split after 30 days. Without it, "which language next" is guesswork.

**Mobile:** if your product captures from iOS or Android apps, mobile may outrank Go. I assumed server-side ingestion. Tell me if that's wrong.

## 7. Hackathon: build one demo app or do all this?

Do the sandbox and quickstart first. Participants need a test key and a path to first success more than they need a showcase app.

| Week | Work |
| --- | --- |
| 1 | Scans, register, archive the obvious rows. Hand the sandbox spec to eng. Add the user-agent language tag. |
| 2 | Merge scenario repos into the shared repo. Draft the quickstart against staging. Write the magic-value catalog and seed dataset. |
| 3 | Sandbox ships. Cold-run the quickstart. Turn on scheduled CI. |
| 4 | Hackathon kit: quickstart, test-key issuance for participants, one hackathon-flavored scenario. Someone else cold-runs it. |
| 5 | Freeze three days before the event. Plan support coverage. Announce archives. |

**Demo app rule.** Only if weeks 1-3 are done. Build it as a scenario in the shared repo, with you as the named owner and CI on the sandbox, never as a standalone repo. Set an archive-or-keep decision for 30 days after the event.

## 8. Questions that would change this answer

1. Does the sandbox have a named engineer? If not, the 3-week plan slips.
2. How many real hours per quarter can you spend on samples, and how many one-off hours before the hackathon?
3. Do you host the hackathon or sponsor it, and which languages do participants register with?
4. Is there a published OpenAPI spec? If yes, Go could be generated and fit before the event.
5. Do you ship client-side capture (browser, mobile) or only server ingestion?

**Next:** run the inventory script and paste the output. With it I can fill the register and give real verdicts for the 14+ repos.