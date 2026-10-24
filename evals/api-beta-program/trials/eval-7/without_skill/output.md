# Second opinion on the eight beta rules

I'd change all eight. Most keep the right intent and need a different mechanism.

**Fix first:** #8, then #2 and #3. They can hurt a real user or damage trust.

| # | Verdict | Why | Replace with |
|---|---|---|---|
| 8 | ❌ Change now | You have a de facto production user that the terms forbid. Silent tolerance weakens your terms, and a later breaking change hits their end users. | Talk to the partner this week. Either sign a written production-pilot exception (rate cap, notice period, no SLA) or move them to a limit. Don't enforce silently. |
| 2 | ❌ Change | Calling a rename "not breaking" doesn't stop clients from failing. It just removes your duty to warn. | Beta may break things, so say so. Mark each change as breaking or not, with a notice period. A rename is breaking. |
| 3 | ❌ Change | Silent edits to a live public endpoint, announced only on social, mean integrators find out when their app breaks. Social isn't a reliable channel. | Version the preview (for example `preview.3`). Publish a dated changelog page, and email registered keys before breaking changes. Social is a copy, not the notice. |
| 1 | ⚠️ Change | A GA-style freeze defeats the purpose of a beta and slows learning. Partners feel safe when changes are predictable, not when nothing changes. | Write a stability promise that lists what is stable (auth, endpoint paths), what may change, and the minimum notice (for example 14 days public, 7 days private). Revisit at GA. |
| 4 | ⚠️ Change | One partner out of seven gets all five requests, which looks like a pay-to-steer roadmap. It also conflicts with rule 1 if the features change the API. | Triage the five against demand from the other six partners. Tell Halden which are committed, which are considered, and which are declined, each with a reason. |
| 5 | ❌ Change | Seven partners are building on this API, and they are the people a change breaks. "Private" only means the changelog isn't public. | Keep a short dated changelog and send it to the partners. It can be the same format as the public one. |
| 6 | ⚠️ Change | A channel with no owner means requests get lost, and each person assumes someone else answered. | Name an owner or a weekly rotation. Set a response target (for example one business day). Turn anything that needs work into a tracked ticket. |
| 7 | ❌ Change | Granted access is not activation. The number looks good and measures nothing. | Report three numbers: granted, activated, and active in the last 7 days. Define activated as a real event, such as the first successful tile request (public) or the first style published (private). Write the definition before you measure. |

## Proposed replacement set

1. Both previews have a written stability promise with notice periods.
2. Breaking changes are allowed in beta but labeled, dated, and announced in a changelog (public for the preview, partner-only for the private beta).
3. The public preview is versioned. Social posts only point to the changelog.
4. Partner feature requests go through one triage process, and every requester gets a written answer.
5. The private Slack channel has a named owner or rotation and a response target.
6. "Activated" is a defined event, reported next to "granted".
7. The live-key partner gets an explicit decision: exception with limits, or migration to a limit.

## Check before you act

- Why is the partner at 2M requests a day? It may be a real product launch, which would change whether you offer an exception or a limit.
- Did the terms promise partners any stability or notice? If so, rule 2 may already be in conflict with them.

I can draft the stability promise, the note to the live-key partner, or the activation definition. Tell me which you want first.