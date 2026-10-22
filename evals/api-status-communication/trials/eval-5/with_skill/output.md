# Status page decision and posts for the ap-southeast authentication outage

## What to set on the page

| Item | Setting | Reason |
|---|---|---|
| Component | **Authentication API** (a consumer-recognizable component, not an internal service name) | The page follows the user's mental model of the product. |
| Component state | **Partial Outage**, scoped to ap-southeast | Component state encodes breadth of impact, not how bad it felt. It is completely broken for a subset (one region), which is the definition of Partial Outage. |
| Other components and regions | Operational | Nothing else is affected. |
| Top-level page | Whatever the blend rule gives: worst component state, so **Partial Outage (orange)** | Don't override the rule for one incident. |
| Incident status | **Monitoring**, not Resolved | The fix or recovery is observed but not yet proven. |
| Internal severity | SEV2 maps to Partial Outage | This matches the written mapping. SEV2 is never shown publicly. |

## Why not Major Outage red

- **CEO's request:** "Total failure for those customers" is true, and the incident text says so. The color doesn't need to.
- **What Major means:** It means unavailable for everyone. Using it for 15% of customers breaks the vocabulary every reader relies on.
- **Cost to everyone else:** Customers in the other regions would see red and start debugging a problem they don't have. It also makes the next real global outage look the same as this one.
- **How to give the CEO what they want:** The title and body carry the severity. "100% of authentication requests failing in ap-southeast" is plain and impossible to misread. A scoped orange state with that text is the honest way to say "total failure for those customers."
- **The blend rule:** Write the rule down once so this isn't re-argued next incident.

## Why not Resolved now

- **The motive is the problem.** The stated reason for closing now is to shorten the outage window. That is status theater run in reverse, and the page exists to prevent exactly that.
- **Two minutes of recovery proves nothing.** Closing on the first green minute and reopening costs more trust than a visible monitoring period.
- **The window is what it is.** About 30 minutes of 100% failure, from the first failed request to the first sustained recovery. Publish that, not a trimmed version.
- **Don't backdate.** If the page was not opened from the alert at the start, open the incident now and state the true start time in the body. The late disclosure is a detection-to-disclosure lag gap. Fix it afterwards by wiring auto-open from monitoring. Don't hide it.
- **When to resolve:** Resolve only after a stable observation period, for example 30 to 60 minutes of normal error rates. Set that threshold in writing now. Run one workflow-level probe, a real login in ap-southeast, as well as the infrastructure checks.
- **If the on-call engineer wants a shorter window:** The honest levers are faster detection and faster mitigation, not an earlier Resolved stamp.

## Post now (status Monitoring)

Placeholders are in brackets. Post the identical text to the page, email, RSS, and webhook subscribers.

> **Authentication API unavailable in ap-southeast** - Monitoring
> [HH:MM] UTC - Between [START] and [RECOVERY] UTC, 100% of authentication requests in ap-southeast failed. Other regions were not affected. Error rates in ap-southeast returned to normal at [RECOVERY] UTC. We are monitoring to confirm the recovery holds. If your integration cached failures during this window, retrying now should succeed. Next update by [HH:MM + 30 min] UTC.

Rules for this post:
- State only what is confirmed. Don't name a cause until it is identified.
- Don't blame an upstream vendor, even if the root cause turns out to be theirs.
- Keep the next-update promise even if the update only says "still stable".

## Post at resolution

> [HH:MM] UTC - This incident is resolved. From [START] to [RECOVERY] UTC, all authentication requests in ap-southeast failed. We apologize for the disruption. A summary of cause and prevention will be posted here within 3 business days.

## Follow-up

- **Postmortem rung:** Publish the default status-page summary postmortem (impact, cause, fix, prevention). Consumers visibly felt this one.
- **Promote to a blog postmortem if:** it is P1-class by your own policy, or trust is visibly shaken. A total regional auth failure for 30 minutes may qualify, so decide explicitly rather than by default.
- **Blameless rule:** Never name the on-call engineer or anyone else.
- **SLA check:** Check contracts for ap-southeast customers. If an SLA applies, the 30-minute window is evaluated per your documented edge cases. Don't shorten it to improve the number.
- **Open question:** I don't know whether the page was opened from monitoring or whether anyone outside heard about this first. If a third party reported it before you did, record that as a miss.

## One-line version for the CEO

The page goes orange, scoped to ap-southeast authentication, with "100% of requests failing" in the text. Red would be inaccurate for the other 85% of customers. We don't close the incident until the recovery has held, because closing early to shrink the window is the kind of move that costs credibility.