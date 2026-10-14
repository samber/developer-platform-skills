# What Brightmesh should publish after the 3-hour outage, and where

**Recommendation:** publish a full public postmortem on the engineering blog, link it from the incident entry on the status page, and send a direct note to enterprise customers. Don't publish the one-line "resolved" note on its own.

I followed the `api-status-communication` skill and its postmortem and update-template references. I'm assuming the outage was Tue 2026-09-29, so please confirm the date. I haven't seen your status page or the incident's update history, so a few points below are conditional.

## Why the one-liner is the wrong call

- **This is the case the skill promotes to a full public postmortem.** It was a P1 and a total outage, and customers say they may leave. The skill says P1-class incidents get a published incident report, and also any incident where trust is visibly shaken. Cloudflare's policy is the cited precedent. Both conditions apply.
- **Silence hurts you with the people already angry.** An enterprise buyer weighing churn reads a bare "we've fixed it" as concealment. Google SRE calls an honest postmortem "a key tool in restoring shaken trust". The skill also cites the transparency–trust effect, where admitting failure increases trust in how you'll handle the next one.
- **You already have the cheap channel.** An active engineering blog and practiced writers make the deep write-up nearly free in effort, which is the effort penalty the skill assigns that rung.
- **Legal's concern is legitimate, but the one-liner isn't the only way to address it.** Legal's real risks are cause language, admissions, third parties and security specifics. The skill's internal-to-external filtering step handles those. Legal should review the draft, not replace it with one line. Every publication is irreversible: you can append a correction, but you can't unpublish a screenshot.

## What to publish, in order

| # | Artifact | Where | When |
|---|---|---|---|
| 1 | Final incident update (template below) with the full lifecycle visible: Investigating, Identified, Monitoring, Resolved | Status page, plus email/RSS to subscribers | Now |
| 2 | Direct note to enterprise customers: apology, link to the blog post, offer of a call | Email from the account owner or CTO | Same day as #1 |
| 3 | Full public postmortem | Engineering blog, linked from the incident entry | Target within 3 to 5 business days. Commit to a date in #1 |
| 4 | Action-item table updated as items complete | Same blog post | Ongoing; post a "done" update when the items land |

If SLA credits apply, handle them in #2 and don't improvise a policy in public.

## 1. Final status-page update (draft)

> **Full outage of the Brightmesh API** - Resolved
> [HH:MM] UTC, 29 Sep - This incident is resolved. Between [HH:MM] and [HH:MM] UTC (about 3 hours), the Brightmesh API and sync jobs were unavailable for all customers. We are sorry. This was our most serious incident to date and we know how much your own customers depend on your data staying in sync. A full postmortem, covering cause, impact and what we are changing, will be published on our engineering blog by [date] and linked here.

Two things to check before posting:

- **Confirm what was true during the outage.** If the page stayed green or was updated late, say that plainly in the postmortem and fix it. That is the "status theater" failure mode. Measure the lag from first alert to first public update.
- **Don't deflect blame.** If an upstream vendor was involved, the update still owns the outage. The customer's contract is with you.

## 2. Public postmortem: structure and what to filter

Use the skill's three-question frame: why it happened, could it have been worse, and how you'll prevent a repeat. Put it on the blog, in plain language, with UTC timestamps.

**Filter these out on the way from the internal postmortem to the public one:**

| Internal postmortem content | Public treatment |
|---|---|
| Priya's name and role | **Remove entirely.** Write "a configuration change deployed to production". Her push is the trigger, not the cause. Blamelessness applies in the document itself. The cause is that a config change could take down everything. |
| Internal service mesh topology | **Remove or abstract.** Say "a shared routing/control layer" and keep only what a reader needs to follow the story. Topology is both an attack map and noise to customers. |
| Auth token exposure | **Don't fold it into the postmortem without a decision.** See the next section. |
| Speculation that didn't survive internal review | Remove. |
| Internal system and team names | Remove. |

**Keep and sharpen:**

- Quantified impact: duration, what was down, what was not, and whether any data was lost or delayed. For a sync product, say explicitly whether data was lost or only delayed and what is being replayed.
- The timeline from first alert to resolution, including when customers were first told.
- 2 to 5 systemic contributing factors. Candidates, to confirm against your internal doc:
  - A config change reached all of production at once.
  - There was no staged rollout or automatic rollback.
  - Validation did not catch the bad config.
  - Detection or recovery took longer than it should have.
- "Where we got lucky": the blast radius that almost was. Readers trust this section most, so don't skip it.
- An action-item table with owners and status, split into mitigative and preventative items.

**Skeleton:**

```markdown
# Brightmesh API outage - 29 September 2026

## Summary
What broke, who was affected, for how long, one-sentence cause.

## Impact
Share of customers and requests, duration, data loss vs. delay, replay status.

## Timeline (UTC)
- HH:MM first alert
- HH:MM public incident opened
- HH:MM cause identified
- HH:MM mitigation deployed
- HH:MM resolved

## Why this happened
Trigger (a configuration change) and 2-5 systemic factors. No individuals.

## Where we got lucky
...

## What we are doing about it
| Action | Type | Owner | Status | Target date |
| ------ | ---- | ----- | ------ | ----------- |
We will update this table as items complete.
```

## 3. The auth token exposure needs its own decision

The skill says to filter security-sensitive specifics out of the public document. That is right for technical detail such as which token, which mechanism and how it was found. It doesn't settle whether to disclose at all.

- **First, scope it.** Were customer credentials or customer data exposed, or only internal tokens? Was there evidence of access, or only exposure? I don't know the answers.
- **If customer tokens or data were involved,** you may have contractual or regulatory notification duties, such as DPAs or GDPR breach rules. Those run on their own clocks and need direct, targeted notice to affected customers, not a mention in a blog post. This is the call for security and legal to make this week.
- **If it was internal only and fixed with no evidence of access,** a short, non-technical line in the postmortem is defensible, for example "we also found and fixed an unrelated credential-handling issue; no customer data was affected". Do that only if security confirms the statement. A customer who later learns about the exposure from someone else will read the omission as concealment, and that does more damage than the outage.
- **Either way, don't bundle it silently into the outage story.** Treat it as a separate disclosure decision with a named owner.

## 4. How to answer the CTO and legal

Suggested line for the CTO: *"We publish the full postmortem on the engineering blog and send enterprise customers a direct note. We remove names, internal topology and security specifics, and legal reviews the draft before it goes out. The one-liner alone would confirm the story customers are already telling themselves."*

For legal, offer a trade rather than a refusal:

- They get review rights over cause language and named third parties.
- They decide the token-exposure question separately.
- You avoid one line claiming "we've fixed it" while customers know it was worse than that.

## 5. Follow-through and checks

- **Close the loop.** The skill treats postmortems without follow-through as theater, with a sourced threshold of under 50% action-item completion. Post a "these are done" update on the blog within a month or two. It is cheap and strongly credible.
- **Check detection-to-disclosure lag.** If your page didn't open an incident automatically from monitoring, wiring that up is the first preventative action. Add a workflow-level probe, such as a real sync job, in addition to infrastructure checks.
- **Check where customers heard first.** If they heard from a third-party aggregator before your page, say so in the postmortem and fix it.
- **Check the status page's infrastructure.** If it shares DNS, CDN or cloud account with the platform, it may have been unreachable during a total outage. If so, make hosting it off-platform an action item.
- **Pick one maintainer for the practice.** The skill suggests recording the practice's core decisions in `developer-platform-context.md` so the next incident starts from them.

## Questions that would change this answer

1. Did the status page show the outage promptly, or was it late or green? This changes the postmortem's honesty section and the first action items.
2. Were any customer credentials or data in scope for the token exposure? This decides whether the notification duty applies.
3. Do any enterprise contracts have SLA credits or notification-channel clauses? This drives the enterprise note and whether you need an SMS/phone channel.
4. What is your deadline and effort ceiling? A hard deadline holds you at the status-page summary. A multi-year trust-building mandate favors the blog post as recommended here.

If you answer these, I can draft the blog post and the enterprise email in full.