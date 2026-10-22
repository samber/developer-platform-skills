# Nessforth App Marketplace: 10-week launch plan for Nessforth Connect

I followed `app-marketplace-launch-marketing` and its three references. The skill asks its interview questions one at a time, but you asked for a full plan now. So I filled the gaps with assumptions, listed at the end. Each one changes the plan if it's wrong.

## Bottom line

"At least 50 partners on stage" cannot be met honestly in 10 weeks. Nessforth has no apps, no reviewer and no pipeline, and the plan below fits that.

- **Founding cohort:** 3-6 vetted design partners, anchored by 1-3 recognizable logos. This is the "design-partner micro-cohort" rung. Notion debuted with 3 partners in 2021.
- **The 50:** present it as a dated roadmap and waitlist at Connect, and as the second wave. It is never counted as "launch partners."
- **Vetting claim:** use "vetted" only if a minimal review gate runs before Connect. Otherwise drop "curated" and "vetted" from all launch language.

## Why 50 fails

- **Nothing to vet.** Real founding cohorts are 15-65 apps, and those operators already had review pipelines or partner bases.
  - Zoom had 15, Stripe 50+, HubSpot 65.
  - The 200+ outlier, Salesforce AgentExchange, rests on a 20-year partner base.
  - Slack launched with ~150 of ~4,000 built apps because the rest "were not vetted well enough."
- **Press counts independently.** monday.com claimed "100+" apps and press counted 78. Atlassian's "1,000" was a migrated catalog. A padded Nessforth number will be audited, and a billing platform's credibility depends on trust.
- **Timeline.** Partners need time to build, and the reviewer has to be hired and trained first. 10 weeks supports single digits, not 50.
- **Security stakes.** Billing data is security-sensitive, which makes an unvetted cohort the riskiest claim you could make.

## What to tell the VP of Marketing

Offer three options:

1. **Recommended: micro-cohort now, waves after.**
   - Connect gets 3-6 live, vetted apps and a stage moment.
   - Wave 2 targets roughly 15-25 apps within 1-2 quarters.
   - The "50" becomes a public, dated target.
2. **"50 logos" slide, labeled "building on the Nessforth API."**
   - Only partners who have signed on in writing and have API keys count.
   - The slide never says "launch partners," "live," or "vetted."
   - Risk: press asks how many are live. The answer is 3-6, and the headline then reads as inflated.
3. **Slip the marketplace to a later event, and announce only the API and design partners at Connect.**
   - This is cleanest if no reviewer is in place by week 4 (see the gate below).
   - It costs the all-hands promise, but it avoids a public miss.

## The plan

### Step 1: Gate (weeks 1-2)

The review checklist is a doc, not a gate. Make it real, or drop the claim.

- **Minimum viable gate for 3-6 apps.**
  - Assign a reviewer: contract, borrow from security or engineering, or hire part-time.
  - Run the checklist on each cohort app before week 8.
  - For billing, cover the following. Treat the list as a draft for your security lead to finish; I am not asserting these are complete.
    - OAuth scopes
    - Data handling
    - Webhook signing
    - Idempotency
  - Use the `app-marketplace-review` sibling skill to design the checklist.
- **Decision date: end of week 2, or week 4 at the latest.**
  - If a reviewer is in place, you may say "vetted."
  - If not, remove "curated," "vetted" and "reviewed" from every launch asset, or take Option 3.

### Step 2: Founding cohort (weeks 1-7)

- **Size and shape:** 3-6 design partners, with 1-3 marquee anchors. Anchors can be partners, or customers who already integrate manually.
- **Selection (a16z design-partner criteria):**
  - **Urgency:** the partner needs the integration now.
  - **Capability:** they can ship against a young API in about 6 weeks.
  - **Representativeness:** their use case generalizes to the partners you want next.
- **Where to find them.** These are suggestions, not data I have:
  - Customers who already built custom integrations.
  - Adjacent categories such as accounting, CRM, tax and payments.
  - Existing integration vendors.
- **Sourcing.** Run outreach in weeks 1-2. Sign design-partner agreements by week 3. Give them early API support and a named engineer.
- **Onboarding.** Use the `partner-app-onboarding` sibling skill. A shared channel and weekly office hours are the minimum.
- **Cohort risk.** Expect 1-2 of 5 to slip, so recruit 6-8 to land 3-6. If fewer than 3 are live by week 8, switch to Option 3.

### Step 3: Reveal (weeks 6-10)

Anchor to the Nessforth Connect keynote.

1. **Week 6:** the operator release draft embeds pre-approved partner quotes. Partner comms teams approve them.
2. **Week 8:** freeze the cohort and the quotes.
3. **Weeks 8-9:** ship each partner a kit with these items, so no approval round-trip is needed:
   - the embargo notice
   - approved boilerplate for both brands
   - the cleared quote
   - logo and banner assets
4. **Embargo lead:** 1-2 weeks, since a billing launch is security-sensitive. This is a PR-practice inference, not a disclosed operator rule.
5. **One canonical announcement time and timezone** in every kit. No partner release lifts before the keynote.
6. **Social posts:** within roughly 15 minutes of the wire time (also inferred from PR practice).
7. **Stage:** the 3-6 partners appear in person or on video. The "next 50" appears as a roadmap slide, labeled as such.

### Step 4: Ongoing featuring (start after launch)

- **Default:** always-on, quality-gated badges. Publish the eligibility gates, re-audit on a cycle, and make losing a badge drop the endorsement, not the listing.
- **Add a time-boxed editorial rotation early.** Badge traction thresholds structurally exclude new apps, and a small cohort needs surfacing. Shopify requires 50 net installs and 5 reviews, and its rotating Staff Picks fills that gap.
- **Skip the paid catalog.** It is high-effort and needs published pricing. It only makes sense once co-marketing demand outstrips team capacity.
- **Claims.** Quote only your own baselined figures. Shopify's "49% install lift" is operator-published and contested by independent rank tracking, so do not borrow it.
- **Paid placement, if you ever add it,** must be labeled as paid.

### Step 5: Budget split

Two motions, per the skill:

- **Platform-wide demand gen (fund for every partner).**
  - Examples: marketplace SEO, category pages, the Connect keynote, curated collections.
  - It is non-rival, so one partner benefiting costs the others nothing.
- **Per-partner co-marketing (ration it).**
  - Examples: MDF, custom campaigns, spotlights.
  - Each engagement consumes staff time, and with a 40-person company that time is tight.

For launch, the 3-6 cohort partners get a fixed, published kit and one joint announcement. Nessforth has no tier program, so do not invent a ladder now. Publish a one-page rule before wave 2, using one of these:

- cohort criteria
- a threshold such as installs or reviews
- a price list

A tier ladder, if you want one, belongs to the `connector-marketplace-strategy` sibling skill. Unpublished, ad hoc co-marketing reads as favoritism to every partner who didn't get it.

### Step 6: Measurement

The program document passes when these three gates hold:

1. Every "vetted" or "curated" claim traces to a live review gate.
2. The reveal plan has one canonical embargo time, and every partner has the kit before it.
3. The rival co-marketing layer has a published allocation rule.

After launch, track:

- press pickup
- partner same-day posts
- day-one installs
- install lift per feature window, against each app's own prior fortnight
- the share of spend on non-rival demand gen versus rival co-marketing

Baseline against your own first quarter. The operator benchmarks are context, not targets.

## 10-week timeline

| Week | Milestone |
|---|---|
| 1-2 | Reviewer assigned. Partner outreach starts. Review checklist finalized. |
| 2-4 | Decision point: reviewer in place, or drop "vetted," or take Option 3. Design-partner agreements signed. API access and onboarding begin. |
| 3-7 | Partners build. Reviewer runs the gate on each app as it lands. Messaging drafted. |
| 6 | Operator release draft, with partner quotes sent for approval. |
| 8 | Cohort and quotes frozen. Fewer than 3 live apps triggers Option 3. |
| 8-9 | Co-marketing kits and embargo notices out. |
| 10 | Connect keynote and simultaneous reveal. |
| After | Wave 2 pipeline, published allocation rule, first featuring rotation. |

## Risks

- **Reviewer slips.** Mitigation: the week 2-4 decision above.
- **Partners miss the API build.** Mitigation: recruit 6-8 for a 3-6 cohort, and give each a named engineer.
- **The "50" gets quoted as live.** Mitigation: every slide and release says "roadmap" or "building on the API," and the VP signs off on that wording.
- **A partner publishes early.** Mitigation: one canonical time in every kit, and the kit ships with the embargo notice.
- **Claims drift.** Mitigation: legal or comms checks every "vetted" or "curated" sentence against the gate.

## Assumptions (not confirmed with you)

If any is wrong, tell me and I'll re-rank the plan.

1. Connect is about 10 weeks out, roughly mid-December 2026, and the date is fixed.
2. The review gate is "none" today, since the checklist exists only as a doc.
3. 1-3 marquee brands could plausibly co-sign.
4. No partner-tier program exists.
5. Budget and headcount are tight, since the company has 40 people.
6. You want a loud, credible debut now, and a program that compounds later.

**Open questions that change the plan:**

- Can a reviewer be in place by week 4?
- Are there 3-6 customers or integrators with urgent, shippable use cases?
- How firm is the VP on the number 50?