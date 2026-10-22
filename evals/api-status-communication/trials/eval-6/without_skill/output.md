# What Brightmesh should publish after the 3-hour outage

## Recommendation

Don't publish only a one-line "resolved" note. After a 3-hour total outage, with furious enterprise customers and churn already mentioned on calls, a one-liner reads as hiding something. It also sets up a worse story if the details leak later.

Publish in three layers, in this order:

| # | Where | Audience | When | Content |
|---|---|---|---|---|
| 1 | Direct email and CSM calls | Affected enterprise accounts, starting with the two who mentioned churn | First, within 1 business day | Personal apology, impact on their account, what changes, credits |
| 2 | Status page incident entry (final post-incident update) | Everyone | Same day as the emails | Timeline, plain-language cause, fix, link to the blog post when it is live |
| 3 | Engineering blog postmortem | Customers, prospects, engineers | Within about 7 days, after legal and security review | Sanitized, blameless, concrete |

The internal postmortem stays internal. The public version is a rewrite with the same facts at a different level of detail, not a redaction of the original.

**Why the blog, not only the status page.** The status page is where customers look during an incident. The blog is where a prospect or a churning customer's security team looks afterward. Enterprise buyers judge vendors by how they handle failures. A specific, honest postmortem is evidence of operational maturity. A vague one is evidence of the opposite.

## What to include and what to leave out

| Internal postmortem item | Public treatment |
|---|---|
| Priya's name and role | **Omit.** Write "a configuration change". The real failure is that one change could take down everything, and the post should say that. |
| Mesh topology | **Abstract.** Say "a configuration change propagated to all production regions at once". Don't list services, hops, or names. A detailed map helps attackers and adds no credibility. |
| Auth token exposure | **Separate decision. See below.** |
| Timeline, detection time, recovery steps | **Include.** Times in UTC, including how long detection took. |
| Customer impact | **Include.** Sync failures, whether data was lost or only delayed, and what customers need to do (ideally nothing). |
| Contributing factors (no canary, no staged rollout, slow rollback) | **Include.** This is the substance. |
| Corrective actions | **Include**, with owners as teams, not people, and target dates you will actually hit. |

**On Priya.** Naming her is unfair, and it also reads badly to customers: it suggests the problem was one person rather than a system that let one change cause a total outage. Tell her before anything is published, and show her the draft.

## The token exposure needs a decision before the blog post

Don't let the blog post or legal's one-liner settle this by default. Security and legal need to answer these first:

1. Was the token exposed to anyone outside the company, or only internally?
2. Is there any evidence it was used? Do the logs cover the full exposure window?
3. Did it grant access to customer data or customer credentials?
4. Do contracts, DPAs, SOC 2 or ISO commitments, or GDPR (72-hour clock) require notification?

Then decide:

- **Customer data or credentials were potentially reachable.** Notify the affected customers directly and promptly, outside the blog post, as the contracts and law require. The blog post can then say a security finding was handled and point to that notice.
- **Internal exposure only, no evidence of access, rotated.** You may leave it out of the public post. Never write "no security impact" or "no customer data was affected" unless that is verified. If a customer asks, answer truthfully.
- **Unknown.** Treat it as the first case until the logs prove otherwise.

Don't bury it in the outage narrative, and don't deny it. The worst outcome is a customer's security team finding out later that it existed and was omitted.

## Answer for the CTO on legal's one-liner

Legal's concern is real: public statements about fault can be used in disputes. But a three-hour outage under enterprise contracts likely already triggers SLA credits, so the facts are not secret. Say this to legal:

- State facts, not fault or negligence. A blameless technical postmortem does this.
- Have legal review the draft, not replace it.
- Avoid unverifiable claims ("this will never happen again"). Commit to specific changes instead.

## Drafts

I don't have the facts for the bracketed items. Fill them from the internal postmortem.

### 1. Email to affected enterprise customers

> Subject: Brightmesh outage on [date]: what happened and what we're doing
>
> Hi [name],
>
> On [date], Brightmesh was fully unavailable for [3 hours, from HH:MM to HH:MM UTC]. During that time [syncs failed / were delayed]. [No data was lost / describe actual data impact]. This was the longest outage we have had, and we are sorry for the disruption to your team.
>
> A configuration change we deployed reached all production regions at once and took the service down. Recovery took longer than it should have, because [reason].
>
> We are changing how we deploy: [staged rollouts, automated validation, faster rollback]. We will publish the full details on our engineering blog by [date].
>
> Per your agreement, we are applying [credit]. I'd also like 30 minutes this week to walk you through the details and answer questions. [Scheduling link]
>
> [Name, title]

Send it from someone senior, not from a no-reply address. For the two accounts that mentioned churn, make the CTO or CEO call first.

### 2. Status page post-incident entry

> **Resolved: full service outage on [date]**
>
> **Impact:** All Brightmesh API and sync operations were unavailable from [HH:MM] to [HH:MM] UTC. [State data impact.]
>
> **Cause:** A configuration change was deployed to all production regions simultaneously and caused the service to fail.
>
> **Resolution:** We rolled back the change and confirmed full recovery at [HH:MM] UTC.
>
> **Next steps:** We are changing our deployment process so changes roll out gradually and are validated before reaching all regions. A detailed postmortem will be published on our engineering blog by [date].

### 3. Engineering blog post outline

Title: **"Postmortem: the [date] Brightmesh outage"**

1. **Summary** (3 sentences): what broke, how long, who was affected, and an apology without hedging.
2. **Impact**: what customers saw, data integrity statement, number of affected accounts or syncs if you are comfortable sharing it.
3. **Timeline** (UTC): change deployed, first alert, detection, diagnosis, rollback decision, recovery, full confirmation. Be honest about gaps, such as how long detection took.
4. **Root cause**: why the change broke things, at a level an engineer finds credible without exposing architecture.
5. **Why it affected everything**: the missing safeguards (no staged rollout, insufficient validation, slow rollback). This section is the one readers will judge you on.
6. **What we're changing**: 3 to 5 concrete actions, each with a target date. Examples: staged rollouts with automatic halt, config validation in CI, rollback runbook with a time target, alerting improvements.
7. **Closing**: reiterate the apology. Say you will post an update when the actions land, then actually do it.

Tone: first-person plural, plain, specific, no marketing language and no "unforeseen circumstances".

## Next steps

1. Tell Priya, and get her sign-off on the wording.
2. Get security and legal answers on the token question before anything goes out.
3. Send the customer emails and update the status page.
4. Write the blog post from the outline and have legal and security review it.
5. Publish within about a week, and post the corrective-action follow-up when it ships.