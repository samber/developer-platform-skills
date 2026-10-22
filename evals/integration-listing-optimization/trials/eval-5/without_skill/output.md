**I don't confirm the sequencing.** Two of the three premises are off, and the order should change.

## Why the order changes

| # | CTO's call | Problem | Verdict |
|---|---|---|---|
| 1 | Salesforce Security Review badge first | Okrahead is already on AppExchange, so it already passed Security Review. That review is the gate to listing, not a separate badge. What remains is re-review, which Salesforce requires periodically and after major changes. | ⚠️ Mostly done. Do readiness only. |
| 2 | Atlassian Cloud Fortified next | Fortified needs an app that is already live on the Marketplace with a track record. You launch in H2, so you can't qualify this quarter. | ⏳ Start the long-lead prerequisites now. Apply later. |
| 3 | Built for Shopify last, "just a sticker" | It's the only one of the three with a measurable, engineering-owned bar you can clear in one quarter. The badge also affects App Store ranking and merchant trust, so it isn't cosmetic. | 🥇 Go first. |

⚠️ I couldn't check current program requirements, so thresholds below come from memory. Verify them against each program's docs in week 1.

## Recommended order

1. **Built for Shopify**: the main bet, about 60% of capacity.
2. **Atlassian Cloud Fortified prep**: about 25%.
3. **Salesforce re-review readiness**: about 15%.

## Quarter plan (13 weeks, Oct 12 to Jan 9)

Dec 19 to Jan 2 is mostly dead time, so the real capacity is about 10 weeks.

**Week 1: Gap audit (all three, 1 engineer-week)**
1. Pull the current Built for Shopify checklist and run it against Okrahead.
2. Find the date of your last Salesforce Security Review and any pending re-review trigger.
3. Pull Atlassian's Cloud Fortified requirements and the bug bounty and security self-assessment steps.
4. Output: one gap table per program, with owner and effort in days.

**Weeks 2–7: Built for Shopify**
- Weeks 2–3: check the install and review thresholds, and the rating floor. Start review collection if you're short. This is a calendar blocker, not engineering.
- Weeks 2–5: fix the performance bar (web vitals and Lighthouse impact on storefront).
- Weeks 3–6: fix embedded admin UX (App Bridge, current navigation and design patterns, onboarding).
- Weeks 6–7: self-check, then submit for review.
- Exit: submitted by week 7. Week 8–9 is buffer for reviewer feedback.

**Weeks 4–11: Atlassian prerequisites (low intensity)**
- Join the Marketplace Bug Bounty program and set up the triage process.
- Complete the Cloud Security Participant self-assessment.
- Define uptime, support SLA, and incident-response commitments, and implement the monitoring that proves them.
- Write a Fortified requirements tracker with dates. Pin the earliest eligibility date after H2 launch.
- Exit: every prerequisite that doesn't need launch history is done.

**Weeks 8–12: Salesforce readiness**
- Run the code scanner (Code Analyzer or Checkmarx) and fix findings.
- Refresh the architecture, data-flow, and pen-test evidence.
- Assemble a reusable security package for enterprise questionnaires. Enterprise logos usually want this faster than they want a badge.
- Exit: you could pass re-review tomorrow, and sales has the packet.

**Week 13: Buffer and retro**
- Handle Shopify reviewer feedback and slip.

## Risks

- 🔴 **Shopify review lag.** Feedback cycles are outside your control. Submit by week 7 to leave room.
- 🟠 **Install and review thresholds.** If Okrahead is short, no amount of engineering helps. Check this in week 1.
- 🟠 **Atlassian eligibility.** The H2 launch date drives when you can apply. Confirm the minimum time-in-Marketplace and install requirements.
- 🟢 **Salesforce.** Low risk if your last review is recent.

## Questions that could change this

1. When was the last Salesforce Security Review, and has Salesforce flagged a re-review?
2. Does Okrahead currently meet the Built for Shopify install and review thresholds?
3. Is the CTO's Salesforce priority driven by a specific enterprise deal? If so, a security packet may beat the re-review work.
4. How many engineers do you have for the quarter? I assumed about 2.

## Pitch to the CTO

"We already passed Salesforce, so there's no badge left to win there. Shopify is the one we can win this quarter, and it feeds ranking. Atlassian can't be won until after launch, but its long-lead items start now."