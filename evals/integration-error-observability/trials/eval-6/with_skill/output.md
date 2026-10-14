# Diagnosis: why Tuliphase's 22 ISV partners still learn about breakage from their own customers

**Promoting the dashboard harder won't fix this.** The dashboard is good. It's pointed at the wrong audience, and it can only be pulled, never pushed.

I applied the `integration-error-observability` skill and its four references. I couldn't ask its clarifying questions, so the unconfirmed assumptions are listed at the end.

## Root cause

The skill splits integrators into three segments, and each needs a different surface:

| Segment | What finishes the job |
|---|---|
| Single-account integrators | A good self-serve log. They go looking because their own users are complaining. |
| **Partners/ISVs with a fleet of installs** | Cross-install aggregation and push notification. |
| No-code and agent builders | A plain-language failure list. |

Your dashboard serves the first segment well. Your 22 ISVs are the second: one app on about 6,000 customer accounts, where every install can fail independently. The skill is blunt about this case: "a per-account dashboard is structurally useless to them: nobody watches a thousand dashboards." It names your situation as the documented default failure: logs shipped, visibility called done, partners still hear about outages from end users.

Three structural gaps explain what you're seeing:

1. **Scope.** The data is per customer account and visible to that customer's admins.
   - The ISV's engineers usually aren't admins of those accounts.
   - Each ISV would need to open up to 6,000 separate dashboards to see their own app.
   - The skill calls this an access-model gap, not a logging gap.
2. **No push.** The dashboard has no alerts or digests.
   - It only helps someone who already suspects a problem and goes to look.
   - The person who notices first is the customer's user, who complains to the ISV.
   - That is exactly the pattern you report.
3. **No per-app view.** Nothing aggregates by app across installs.
   - Nobody, including you, can see "app X is failing on 200 of 240 installs."
   - Nobody can see "app X went silent."

Promotion would make this worse. If it works, it sends the ISVs' customer admins to your dashboard, and those admins would then escalate to the ISV even faster.

## How to check this before you act

Two quick checks:

- **Ask the 22 ISVs** how many of their engineers have ever opened the dashboard, and whether they could for a given install. I expect "few" and "only with the customer's login."
- **Classify your last 20 integration tickets** by failure class: request not found, webhook never arrived, silent mismatch, auth failure, rate-limit confusion. This is the skill's audit step, and it sets your baseline.

## What to build, in order

The order follows the skill's rungs.

### Week 1 to 2: close the push gap with what you already record

1. **Confirm every inbound request is tagged with the app or client ID at ingestion.** This is the prerequisite for everything else.
   - Aggregation is only as granular as that tag.
   - If the tag is missing, adding it is the first job, because history before the tag is unqueryable by app.
2. **Aggregate per app, per window.** Keep these separate:
   - 4xx, which is the integrator's side.
   - 5xx, which is yours.
   - 429, which is a quota conversation.
   - Add the top error codes and the number of installs affected.
   - Never send one blended error rate.
3. **Send a per-app digest to a named partner contact.** This is the skill's default rung.
   - It carries the failure classes and a link into the filtered log.
4. **Add immediate state-change alerts.** They fire on credential revoked, app disabled, subscription lapsed, and mass uninstall. These are single events, so there's no cooldown.
5. **Check your own deploy timeline before telling a partner anything about a 5xx spike.**

### Next: threshold alerting, if the partners lose money within hours

- Alert when an app's error rate crosses its own baseline, then hold a cooldown. Salesforce uses 30 minutes by default; pick yours from typical incident length.
- Each alert should name the top error code and the number of installs hit. It should also say what you ruled out ("no Tuliphase release in this window") and when the next alert can arrive.
- Send a recovery message.
- Use two windows: a short one for sudden breaks and a long one for slow creep.
- This is the skill's "starved rung." It only gets built if you decide it matters, and for commerce-style apps it likely does.

### Then: a partner-scoped cross-install view

Give each ISV's engineers a view that spans all installs of their own app.

- **Start metadata-only:** timestamp, endpoint, status, error code, request ID, install ID, and counts per error code.
- **Leave bodies in the per-customer dashboard.** Your dashboard exposes bodies to a customer's admins about that customer's own data. Showing an ISV bodies across 6,000 tenants is a different data-classification decision that needs legal sign-off, and it's close to irreversible once partners build tooling on it. Make it a separate decision.
- **Isolate tenants structurally** (per-app scoping enforced below the query layer) rather than by filter convention.
- **Make the request ID searchable here,** so an ID quoted in a support ticket resolves for the ISV without them writing to you.

### Internal fleet view for your partnerships and support team

With only 22 partners, a ranked queue is a five-minute Monday job.

- Rank by blast radius (installs affected out of installs total), not by raw error count.
- Include a **volume-drop-to-zero** signal. An app that stopped calling shows up in no error list.
- Separate "broken since our deploy," which you own, from "broken since their release," which is the outreach case.
- Name a contact per partner.
- **Don't publish per-partner reliability scores or rankings externally** until you can defend how they're computed.

### Still open from the skill's menu

- **Webhook delivery log:** if you send webhooks, expose the delivery attempts you already record. It is the skill's default rung and kills the "webhook never arrived" ticket.
- **Replay:** build it later, independent of your retry schedule, with stable event IDs.

## What your head of partnerships can usefully own

Their role fits better in the build than in promotion:

- Collect a named technical alert contact per ISV. A partnerships lead probably holds the relationship, but an alert needs an engineer's address.
- Define the escalation path for repeated alerts nobody acts on.
- Run the outreach queue from the fleet view.

Promotion becomes useful afterwards, aimed at the right audience: customer admins who want to self-diagnose.

## How to measure it

- **Gate:** every failure class in your ticket audit has a surface an integrator can use unaided.
- **Gate:** take a request ID from a real response and look it up as an outside ISV engineer would. Binary pass or fail.
- **Trend:** time from first failure to the ISV acting. Track it per notification rung. This is the number that proves the problem is fixed. "ISV heard from us first" is a sensible secondary count.
- **Trend:** alert action rate. A sustained drop means you're building alert fatigue. Widen thresholds or lengthen the cooldown before adding another channel.
- **Trend:** re-run the ticket classification after shipping. The direction matters, not any industry level, since none exists.

## Assumptions to confirm

These change the ranking above:

1. **App identity tagging.** Is every call tagged with an app or client ID today, or only an API key? This decides whether week 1 is two weeks or two months.
2. **Money timeline.** Do the ISVs lose money within hours of a break? If so, the threshold alerts move up; if it's noticed at reconciliation, the digest alone may do.
3. **Legal.** Who signs off on showing an ISV any request or response data from customer accounts? I assumed metadata-only is allowed.
4. **Webhooks.** Does Tuliphase send them, and are per-attempt outcomes recorded?
5. **Existing partner channel.** Do you already have an outbound notification channel to partners? If so, every push rung gets cheaper.
6. **Ticket mix and deadline.** What do the last 20 tickets actually look like, and what are the deadline and engineering budget?

I wasn't able to confirm any of these from your message. The diagnosis itself rests only on what you told me: a per-customer dashboard, 22 ISVs across about 6,000 customers, and ISVs hearing from their customers first.