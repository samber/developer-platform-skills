# Kestrelbase Zapier maintenance plan

**All three premises need correcting before the plan makes sense:**

- **(a)** Zapier documents no integration-level error rate that triggers delisting.† The things that do exist are different: a per-Zap auto-off rule, and a health score built from your open bug reports. Your untouched bug queue is the real exposure.
- **(b)** Gold is 350 active users†, not 500. The gap is about 170, not 320. Gold also carries the same benefits as Silver†, which you already qualify for.
- **(c)** Don't deprecate 1.2.0 next Monday. Zapier's minimum notice is 3 weeks†, so a 7-day notice can't be set. Zapier's own user email goes out 14 days† before the date. The skill says to deprecate only a version that will stop working, and to mark any other version legacy. "Strictly better" has also not been verified.

## 1. Assumptions

Each of these is a stated assumption because the interview answer was missing. Correct any that are wrong and the plan shifts.

1. **Stage:** public since March, so past the 90-day beta†. I don't know whether you build on the Platform UI or the CLI. I give both paths where they differ.
2. **Promoted version:** 1.3.0 is promoted and 1.2.0 is Available. I don't know whether 1.0 or 1.1 exist, or how many users are still on 1.2.0.
3. **API capability:** unknown whether you have a webhook subscription endpoint, newest-first sorting, or stable unique ids. This is the biggest open item for the "Updated Task" fix.
4. **Customer jobs:** unknown. Support tickets and exports should supply them. Assume no Zap templates are live today.
5. **Deadline and capacity:** the Gold deadline is the January 2027 tier evaluation†. Engineering capacity is unknown, so I size work as S (1–2 days), M (3–5 days) or L (more).
6. **Numbers:**
   - "180 active users" is last quarter's Partner Program count. I haven't seen this quarter's.
   - "3.2% of runs errored" has no known definition: it's unclear whether halted errors are included.
   - The "about 25 users" affected by bugs is your estimate.

## 2. Stage and route

**Stage:** public integration with live users and a planned change. Per the skill, classify every change first (Maintain, step 4). Then Maintain and Grow, and go back to Design for the "Updated Task" trigger.

**Premise checks:**

| Claim | What the sources say | Consequence |
| --- | --- | --- |
| Delisted above 5% error rate | No public page states an integration-level threshold.† Documented removal grounds are banned categories, Platform Agreement breaches, gaming review and faked users. The only documented error rule is per Zap: 95% errors over more than 20 runs in 7 days† turns that Zap off. | Don't promise the 5% rule to anyone. Ask where you read it. Treat 2% as your own quality target, not a Zapier requirement. |
| Gold = 500 | Gold is 350 active users this quarter†. Platinum is 3,000, or 350 with 20% quarter-on-quarter growth†. | Gap is about 170. Going from 180 to 350 is +94%, so verify whether that would also qualify for Platinum. |
| Gold gets us something new | Gold lists Silver benefits only.† | The badge adds little. Aim for the user count and the health score, and claim the Silver benefits now. |
| 7-day deprecation notice | Deprecation date must be 3 weeks to 1 year out†. Zapier emails users 14 days before†. | A 7-day notice isn't possible. See section 7. |

**What actually gates a tier:** every tier needs a "healthy" health score†, built from open bugs and feature requests (weighted by votes) and your responsiveness to them. It does not use error rates. Your 14 bugs with no response since July (3+ months) are the likeliest blocker.

Rule of thumb: keep users affected by open bugs under 10% of monthly actives†. 25 of 180 is about 14%, which is over. The 10% applies to monthly actives, a different base from the 180 quarterly count, so recompute once you have the right base.

## 3. Step table

I know one step by name. Fill in the others from the Developer Platform.

| Key | Label | Type | Class | Reason |
| --- | --- | --- | --- | --- |
| `updated_task` | Updated Task | polling (assumed) | **hide** after twin ships | 11% activation vs 55–65% elsewhere is a design defect. Existing Zaps keep running when hidden. |
| `updated_task_v2` | Updated Task | polling, or REST hook if the API allows | **additive** | Composite id `id-updated_at` (original id kept in another field), newest-first by `updated_at`, enough items per page for a burst. |
| `task_completed` etc. | e.g. Task Completed, Task Assigned | polling or hook | **additive**, only if support tickets show the job | Specific state triggers beat a generic "updated" trigger. Pick them from customer jobs, not from guesses. |
| all other visible steps | unchanged | unchanged | **keep** | Activation is 55–65%. Don't touch. |
| any step with a bug fix that changes keys, output shape or polling order | | | **breaking** | Twin it under a new key, or park it for a 2.0 backlog. Never fix in place. |

**Why not fix `updated_task` in place:** changing what counts as "new" is breaking in effect. Each live Zap's dedupe memory holds the old ids, so the first poll after the change fires every unseen item as new.

**Likely causes of the 11% to test in the editor yourself (hypotheses, not findings):**

1. **Plain `id` as dedupe key.** Zapier dedupes by id per Zap, so an updated task keeps the same id and never fires again.
2. **Unsorted or oldest-first results.** Newest updates aren't visible on the first page.
3. **Frequent edits.** More than 100 new items per poll† holds runs and emails the user, which is a signal this trigger belongs on a hook.

## 4. Auth and trigger-type decisions

- **Auth:** don't change it. Changing the auth scheme is breaking and needs a new major. Confirm the API returns HTTP 401 on expired tokens, because Zapier refreshes on 401 only.
- **Trigger type for `updated_task_v2`:** use a REST hook (Instant) if the API can create and delete webhook subscriptions per Zap and keep several alive at once. Otherwise use polling with the contract above. A hook also needs a perform list, and you must send each event once, since hook deliveries aren't deduplicated. **Ask engineering this week**; this is open answer 3.
- **Never switch the existing trigger's type.** If you go to a hook, the hook is a twin under a new key.

## 5. Publish checklist

Covers the 1.4.0 release and the template submissions.

| # | Item | Owner role | Week |
| --- | --- | --- | --- |
| 1 | Open the Partner dashboard. Record the tier, the health score, Q4-to-date active users and users per version. | Head of product | 1 (Oct 26) |
| 2 | Comment on all 14 bugs, even with "triaged, ETA X". Responsiveness is part of the score. | Support lead + integration engineer | 1 |
| 3 | Pull Monitoring logs and group errors by step × error type. Check concentration: if 3 Zaps produce most errors, it's user config, not the integration. | Integration engineer | 1 |
| 4 | Diff 1.2.0 against 1.3.0 on output keys, response structure and perform behavior. This tests "strictly better". | Integration engineer | 1 |
| 5 | Reproduce "Updated Task" in the editor. Confirm which of the three causes applies. | Integration engineer | 1 |
| 6 | Classify every bug and error fix with the versioning table. | Integration engineer + PM | 1–2 |
| 7 | Build 1.4.0 as a clone of 1.3.0, additive only: bug fixes, error mapping, `updated_task_v2`. If CLI, run `zapier-platform pull` first. | Integration engineer | 2 |
| 8 | Run `validate`. Clear all Errors and Publishing Tasks. Read Warnings. Confirm hiding `updated_task` clears its checks. | Integration engineer | 2 |
| 9 | Share the clone with test accounts. On CLI, canary 5–10% for 30–60 minutes† (non-breaking only), and stop if errors rise more than 5%†. | Integration engineer | 2–3 |
| 10 | Promote 1.4.0, then migrate 5% first, watch Monitoring, then the rest. | Integration engineer | 3 |
| 11 | Write 5–10† Zap templates. Rules: no Paths, Code, Webhooks, Looping or Formatter steps†. Titles start with an action verb, with no "sync" or "automatic". Use `references/templates.md`. | Product marketing or DevRel | 3 |
| 12 | Submit the templates after 1.4.0 is promoted. Review takes about 2 weeks†. Don't build any on `updated_task`, because hiding it invalidates them. | Product marketing | 3 |
| 13 | Write one help article per job, with the template embedded. | Support lead | 4–5 |

If 1.4.0 slips past Nov 13, submit templates on 1.3.0 using only steps 1.4.0 won't hide. Confirm with Zapier partner support first, because I haven't verified how promoting mid-review treats pending templates.

## 6. Growth actions, ranked

| Rank | Action | Answer that moved it |
| --- | --- | --- |
| 1 | **Clear the bug queue and get the health score healthy.** | Gold requires it; your 14-bug backlog is the likely blocker. |
| 2 | **5–10 Zap templates for the top jobs.** Most efficient lever, gated only by about 2 weeks† review. | Answer 4: you need real customer jobs. |
| 3 | **Template embeds in launch posts and help articles.** Minutes of work per job. Any embed signup exits beta; you're already public, so its value is the fast-track: next-tier benefits at 300 active users†. | Answer 5: the deadline favors compounding channels. |
| 4 | **Workflow Element in the integrations page.** Hours of work† once a public template exists. Needs a domain allowlist. | Answer 3 doesn't gate it; answer 5 favors it. |
| 5 | **Onboarding, support macros, empty-search fallback.** No gate, so start in week 1. | None. |
| 6 | **Claim the Silver benefits you already qualify for:** "Learn More" lead button with UTMs, featured week, newsletter spotlight, "Best of" flyover.† Time them after the templates and `updated_task_v2` ship. | You're past 50 users†. |
| 7 | **Custom marketplace on the Workflow API.** Skip for now: weeks of work, only worth it if you already run an integrations directory with heavy search traffic. | Answer 5. |

**Realism on Gold by January:** you need about 170 more actives, roughly 17 net per week over about 10 weeks. Last year's pace was 180 in about 7 months. This is my inference from the numbers you gave, not a Zapier fact. Unless Q4-to-date already sits near 250, treat January as a stretch and April 2027 as the realistic target. Compute the real gap from the Q4-to-date number, not last quarter's 180.

## 7. Versioning plan

**Target version:** 1.4.0, a clone of 1.3.0. A version is editable only while private with fewer than 5 users†, so you must clone. Everything in it is additive.

**On the 1.2.0 deprecation:**

1. **Don't deprecate.** 1.2.0 isn't scheduled to stop working. Mark it legacy instead.
2. **What legacy does:** it hides 1.2.0 from new Zaps and keeps existing ones running. With automatic migrations on (the default), marking it legacy moves most users.
3. **Order:** promote 1.4.0, migrate by percentage, then mark Available versions legacy one at a time, oldest first.
4. **Count what remains.** For stragglers, reach out through your own channels: your OAuth grants or API-key records show who connected Zapier. Zapier gives you no email list.
5. **Don't clean house.** Old versions cost nothing, and deletion is allowed only at zero users, including paused Zaps and connections. The only version-count limit is 100 production versions with live Zaps†.

**If you still insist on a real deprecation** (for example, 1.2.0 calls an endpoint being sunset): announce today, Friday Oct 23, and pick a date at least 3 weeks out. The earliest valid Monday is **Nov 16, 2026**. Zapier emails affected users 14 days before, and unmigrated Zaps pause on the date. Deprecating also marks its templates Invalid within 24 hours†, so templates must use the promoted version.

**Migration:**

- Migration works only within one major (`1.x` to `1.y`). Never cross to 2.0.
- Automatic migrations are on by default, so promotion itself moves a first group of users. Test first.
- If you're on the CLI, you're also in the Integration Maintenance Program by default†: Zapier engineers may change your versions, and you must `pull` before pushing or promoting.

**Diff by hand before promotion** (the promotion check does not catch these):

- Renamed or removed output keys.
- Changed response structure.
- Changed perform behavior.
- Polling sort order, page contents and id format for every trigger you touch.

**Error-rate fixes** change perform behavior, so test them against live Zaps. Apply the skill's error rules:

- Return a normal error naming the field and reason, under 250 characters†, for failures the user can fix.
- Return a halted error for unmet preconditions (duplicate, already paid).
- Let 429 surface with a `Retry-After` header.
- Return an empty array for a search with no match.
- Never return 200 on a failure.
- During a known outage, throw a throttled error with a delay.

Set the 2% target after the error Pareto from item 3. If most errors are concentrated in a few user Zaps, 2% may not be reachable by code changes alone.

## 8. Metric baseline

| Metric | Current value | Where to read it |
| --- | --- | --- |
| Active users (quarter) | 180 (Q3); Q4-to-date unknown | Partner dashboard |
| Next tier | Gold = 350† (gap about 170 from Q3) | Partner Program docs |
| Health score | unknown | Partner dashboard |
| Open bugs | 14, untouched since July | Developer dashboard Bugs queue |
| Users affected by bugs | about 25 (estimate), about 14% of 180 | Bug reports, cross-checked against your own OAuth/API-key records |
| Median days to first response | more than 90 days | Developer dashboard |
| Run error rate | 3.2%, definition unknown | Monitoring; check whether halted errors are counted |
| Activation, Updated Task | 11% | Developer dashboard (24-hour activation by step) |
| Activation, other steps | 55–65% | Same |
| Users per version (1.2.0 vs 1.3.0) | unknown | Developer Platform version page |
| Templates live | assumed 0 | Developer Platform |
| Embed click-to-activation funnel | none yet | Your analytics |

## Footnote

† Zapier platform number or rule. Verify against Zapier's live docs before quoting it to a stakeholder. This covers every marked figure: the 95% auto-off rule (more than 20 runs, 7 days), Partner Program tiers (50, 350, 3,000, 20% growth) and fast-track (40, 300, 2,500), the 10% affected-user guideline, the quarterly re-evaluation months, the 3-week to 1-year deprecation window, the 14-day email, the 24-hour template invalidation, 90-day beta, 100 new items per poll, 250-character error limit, editable-version rule (fewer than 5 users), 100-version limit, 5–10 templates, about 2-week template review, and 5–10% canary for 30–60 minutes with a 5% error-rise stop.