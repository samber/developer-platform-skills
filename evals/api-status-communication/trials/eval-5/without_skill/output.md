# Vaultic status page: what to set and what to post

## Decision

| Question | Answer |
|---|---|
| Whole page red? | **No.** Set only the affected component to Major Outage. |
| Which component? | Authentication API, ap-southeast. If the page has no regional component, add one now. |
| What does the page-level banner show? | Whatever your platform rolls up from that one red component. Don't override it manually. |
| Incident status now? | **Monitoring**, not Resolved. |
| Internal severity? | SEV2 stays internal. Customers never see it, and it doesn't drive the page color. |

## Why

**The CEO is right about severity and wrong about scope.**
- For ap-southeast customers, a 100% failure rate is a major outage. Say so plainly, on their component.
- A page-wide red banner tells the other ~85% of customers that Vaultic is down for them too. It isn't, and they will open tickets, pause deploys, or fail over without need.
- A page that overstates impact once teaches customers to discount it later, when it matters.
- Offer the CEO this framing: "ap-southeast auth shows Major Outage in red, and the incident text says total failure in that region."

**Don't mark it Resolved yet.**
- Two minutes of normal error rates is a recovery signal, not a confirmed fix. Incidents often flap, and clients stuck in retry backoff can make error rates look better than the real state.
- A second failure after a Resolved post costs more trust than the shorter window gains.
- The window isn't shortened by closing early. The outage lasted from the first failed request to the first sustained healthy period. Both timestamps are facts.
- Record the impact end as the recovery time, about 2 minutes ago. That is accurate, and it is the honest way to keep the window as short as it truly was.
- Resolving at the earliest moment and then re-opening, or backdating, would make the record wrong. Don't do either.

## Before moving to Resolved

1. Confirm recovery with synthetic auth checks from ap-southeast, not only aggregate error rate.
2. Hold a clean period. I suggest 30 minutes with no errors above baseline, or whatever your policy says.
3. Identify what changed (fix, rollback, upstream recovery) so you can say recovery is durable.
4. Check for a backlog or retry storm that could re-degrade the service.

## Timeline for the record

- **Start:** the first failing request, not the time of the first alert. Pull it from logs.
- **Impact end:** the time error rates returned to normal (about 2 minutes ago).
- **Resolved:** posted after the clean period. This is a communication timestamp, kept separate from the impact window.

## Post now (status: Monitoring)

> **Authentication API – ap-southeast: elevated errors, recovery observed**
>
> **[HH:MM UTC] – Monitoring.** From approximately [START UTC] to [RECOVERY UTC], authentication requests to Vaultic in the ap-southeast region failed. During this time, customers in that region could not authenticate. Other regions were not affected.
>
> Error rates in ap-southeast returned to normal at approximately [RECOVERY UTC]. We are monitoring to confirm the recovery is stable. [One sentence on cause or mitigation only if confirmed, e.g., "A change was rolled back." Otherwise omit.]
>
> Customers who still see authentication failures should retry. We will post our next update by [HH:MM UTC], or sooner if anything changes.

Component state: **Authentication API – ap-southeast → Major Outage**. Move it to Operational only when you post Resolved, or to Degraded Performance if you want it to show partial recovery during monitoring.

## Post later (status: Resolved)

> **[HH:MM UTC] – Resolved.** The authentication issue in ap-southeast is resolved. Impact ran from [START UTC] to [RECOVERY UTC] (about [N] minutes), during which authentication requests in that region failed. Service has been stable since [RECOVERY UTC]. We will publish a post-incident review by [date].

## If your page can't show a regional component

Keep the global status at Partial Outage, not Major Outage. Then put the scope in the first line of the incident title and body: "Authentication API – ap-southeast: complete outage." Use the same wording in both so no one has to read between the lines.

## One-line replies

- **To the CEO:** "For ap-southeast customers it shows Major Outage in red. Turning the whole page red would tell the 85% of customers who are fine that they're down too."
- **To on-call:** "Good news on the recovery. Put it in Monitoring now, and we resolve after a clean period. The impact window ends at the recovery time, so it is no longer than it truly was."