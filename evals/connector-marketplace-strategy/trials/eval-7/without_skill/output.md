# Pathvine marketplace: the honest read

## Verdict

Neither one-pager holds up as written. Both sides are half right.

- **The VP is wrong about the mechanism.** At 240 customers, "more customers attract more apps, more apps attract more customers" isn't a flywheel. No independent software vendor (ISV) will fund a product line on a reachable market that small. If the flywheel is the justification, the CEO wins.
- **The CEO is wrong about the conclusion.** "Nobody will build a business on us" is true but beside the point. A marketplace doesn't need to host businesses to pay off. It can be a cheaper way to deliver integrations your customers already want, built by people with other motives.
- **Recommendation:** don't build a marketplace or an app platform now. Run a staged, gated integration program for 12 months. It starts at the cheapest rungs, with an explicit test of whether a marketplace is ever worth building.

## Why the flywheel fails at your size

Two-sided loops need enough volume on each side that the other side's economics work. A builder asks four things:

1. How many of your customers want this?
2. What do I earn?
3. What does it cost me to build and maintain?
4. What's my alternative?

For an ISV, the answer to 1 is a few dozen accounts, and the alternative is building on a bigger veterinary software platform. The arithmetic doesn't clear. Charging a take-rate this early makes it worse.

There's also a risk the one-pager skips. Vet software is a crowded, consolidating space, and larger practice-management systems can bundle most of what a third party would build. A flywheel on your platform could just feed theirs.

## Why the CEO's "distraction" call is premature

The builders who matter at your size aren't ISVs. In order of likelihood:

1. **Your customers' own teams.** Clinic groups have IT and ops people who already write glue: exports, scripts, spreadsheets. They need no business case, only a stable API.
2. **Integrators and consultants.** They bill hours and want certification and referral flow, not revenue share.
3. **Adjacent vet-tech vendors.** Labs, imaging, payments, telehealth, pharmacy, client communications, accounting. They already have customers in your clinics and a reason to integrate. This is partner-built integration, not an "app ecosystem."

One assumption to check: "240 customers" may be 240 groups, each with many locations. If so, the reachable footprint is far larger than "240 clinics" suggests, and the CEO's framing understates it. I don't have your numbers, so verify this first.

## Three questions to answer before any build decision

These should take about two weeks. I can't answer them from here.

1. **Counted demand.** List the last 10 to 20 integration or extension requests, with customer names, ARR, and whether the request came up in a renewal, a churn risk, or a lost deal. Fewer than five concrete requests means there's no market yet. Requests you turned down count most.
2. **Existing workarounds.** Which customers have already built unofficial glue against you (scrapers, exports, CSV pipelines)? That demand is already paid for.
3. **Architecture and staffing.** Do you have a stable, versioned public API you'd be willing to dogfood? Who owns security review, support for third-party breakage, and deprecation, indefinitely? If the answer is "borrowed engineers," skip the upper rungs.

## The staged path I'd recommend

The cheapest rung that clears the evidence wins. Each rung is harder to undo than the one below.

| Rung | What it is | Do now? |
|---|---|---|
| 1. Documented public API + webhooks | Docs, versioning, rate limits. Reversible with notice. | **Yes**, if it doesn't exist or is weak |
| 2. Vendor-built integrations | You build the top-demand connectors. Maintenance grows with each one. | **Yes**, for the top 2–3 on the demand list |
| 3. Partner-built, listed by you | Outsiders build; you provide a listing page, standards, and a review queue. | **Yes, small:** 3–5 hand-picked founding partners |
| 4. In-product extension points | Freezes internal seams permanently. | **No.** Parked until rung 3 shows pull |
| 5. Installable third-party apps | Needs consent and scopes, security review, revocation, tenant isolation. Permanent team. | **No.** Veterinary data and payments raise the stakes |
| 6. Runtime platform | A second product. | **No** |

"Marketplace" in the one-pager is rungs 3 to 5 under one name. Splitting it up is the main way to settle the argument. You can say yes to the VP's direction at rungs 1 to 3 and yes to the CEO's caution about 4 to 6.

Seeding matters. A directory with three listings reads as abandoned. Build the first one or two connectors yourself to set the pattern. Recruit founding partners by hand, chosen to cover the most-requested categories. Point your own distribution at them: onboarding, sales conversations, docs. Keep the take-rate at zero.

## What to measure in year one

The thresholds below are defaults I'm proposing so you can argue with them. They aren't industry benchmarks. Replace them with your own baselines once you have them, and set baselines before launch.

**Business impact (the numbers that fund the program)**
- Share of accounts with at least one active integration.
- Retention and expansion of accounts with an integration versus those without. Control for account size and tenure. Heavy accounts adopt more, so a raw gap proves little.
- Deals won or renewals saved where an integration was cited. Log that in the CRM at close.

**Supply**
- Coverage of the demand list: how many of the top 10 requested complements exist.
- Founding partners who ship something, and median time to first working integration.
- Net new integrations per quarter.

**Health and cost**
- Concentration: share of usage held by the top three integrations. High concentration means you have partnerships, not an ecosystem.
- Support tickets caused by third-party code.
- Engineering hours spent keeping published interfaces stable.

Don't report logos signed, directory listings, or API keys issued. Those are ecosystem theatre.

## Kill and de-escalate criteria

Write these now, while stopping is cheap. Proposed defaults:

- **Month 3:** the demand list has fewer than five concrete, named requests. Stop at rung 1 and close the question for two quarters.
- **Month 6:** none of the founding partners has shipped a working integration. Drop rung 3 and stay with vendor-built connectors.
- **Month 9:** accounts with an active integration show no retention or expansion lift over a comparable cohort. Stop investing beyond maintenance.
- **Month 12:** fewer than a set share of accounts (pick it from your baseline) use any integration. Wind down the listing program with notice.

## Reopen conditions for a marketplace (rungs 4–5)

Revisit only if all of these hold:

- Independent builders are asking to build, unprompted.
- At least some integrations are products in their own right, not data moves.
- A funded team is willing to own security review, support, and deprecation permanently.

Until then the platform question stays closed. Writing it down this way ends the recurring debate.

## What I'd tell the CEO and the VP

- **To the VP:** the flywheel claim isn't defensible at this size. The integration program is, and it keeps the option open.
- **To the CEO:** this isn't a distraction if it stays at the low rungs, is gated on counted demand, and has dated kill criteria. It becomes one if it grows into an app platform before the evidence arrives.

## Caveats

- I didn't see your data, customer mix, or the VP's one-pager, so the demand count, group size, and architecture readiness are open questions.
- The ladder and the thresholds are a structured framework plus my judgment. The numbers are proposals, not measured benchmarks.