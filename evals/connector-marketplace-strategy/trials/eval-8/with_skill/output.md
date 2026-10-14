# Statlas connector strategy: gate decision

**Recommendation: do not build the marketplace. Buy embedded iPaaS for the long tail, join the incumbents' marketplaces for the top names, and keep a curated partner catalog as the step before any build.**

I couldn't run the skill's one-question-at-a-time interview, so I worked from your brief and marked every assumption. Each assumption is a place where a different answer would change the recommendation (see "What would flip this").

## 1. Gate: build, join, or buy

The skill says choose build only when all four triggers hold, each with evidence. Here is how Statlas scores:

| Trigger | Evidence | Verdict |
|---|---|---|
| 1. Customer pull | The RFP list of 40+ named integrations is real demand (interview 2a/c). | ✅ Holds |
| 2. Supply signal | Nothing in the brief shows partners asking to build on Statlas or third parties shipping unofficial connectors (3c, assumed). The 40 integrations are Statlas connecting to other vendors' platforms. That is demand for connectors, not a developer ecosystem. | ❌ Fails |
| 3. Procurement friction from one-off requests | RFP checklist items are not the same as repeated one-off integration requests. This is unverified. | ⚠️ Unproven |
| 4. Lifecycle readiness | Two spare engineers already deliver about 5 integrations a year. A public API, docs, sandbox, review and partner support is a standing commitment on top of that (4 = no, assumed). | ❌ Fails |

Build fails two of four triggers. At $17M ARR, building also lacks the scale the skill reserves for market leaders. Without supply, the result is "little more than an expensive partner directory."

**The real problem is throughput, not distribution.** Forty-plus integrations at 5 per year is about 8 years of backlog, and the list keeps growing. The skill's answer to "we need many integrations fast" is buy. One cited case went from its in-house pace to 100+ integrations in a year with embedded iPaaS.

**Recommended path, in order:**

1. **Buy** an embedded iPaaS or unified-API layer for the long tail (NetSuite, Zendesk, Intercom and similar). This takes the 5/year constraint off the table.
2. **Keep first-party** for the 5-8 integrations that appear most often in RFPs. Salesforce and HubSpot are the likely candidates, and these should be native and deep.
3. **Join** the marketplaces where your buyers already look. Examples are Salesforce AppExchange and HubSpot Marketplace, plus the Zendesk, Intercom and Stripe app directories. This borrows their distribution and trust, and `integration-listing-optimization` covers execution. HubSpot charges 0% and no listing fee (2026 terms). Salesforce charges 15% and a security review fee only on paid apps, and Statlas's connector would be a free app. Re-verify these terms before relying on them.
4. **Publish a curated partner catalog**: a page listing every integration, labelled native or via partner. This is the skill's named intermediate step.

## 2. Why the head of platform's proposal doesn't pass

Developer program, partner tiers and revenue share are three of the four things the operating model bundles. They are premature for three reasons:

- **Revenue share has nothing to share.** With no partner supply and no billing through Statlas, a rev-share rate has no base.
- **Take-rate theory points to 0%.** The skill's default while seeding is zero take, as in HubSpot's marketplace. A revenue share at Statlas's scale taxes the hard side before it exists. The 15-25% rates are earned by distribution (91% of Salesforce customers use an AppExchange app), which Statlas does not have.
- **Partner tiers need partners.** Tiers formalize an ecosystem that doesn't exist yet.

I would present this to the head of platform as "not yet, with explicit promotion criteria", not as a rejection. The skill counts that as a success.

## 3. Promotion criteria for revisiting build

Revisit in 12 months, or sooner if all of these hold:

- At least 3 third parties have asked to build on Statlas, or have shipped unofficial connectors (trigger 2).
- Procurement friction from one-off integration requests is documented, for example 5+ deals where a custom connector request slowed the cycle (trigger 3).
- You can staff a standing partner lifecycle: API, docs, sandbox, review and support (trigger 4).
- Integration data shows retention lift. Compare churn for accounts with 4+ integrations against fewer. This is business case 2 (retention), which is likely the one that carries the decision at your scale. Case 1 (ecosystem flywheel) does not yet apply.

If those hold, the default operating model would be: hybrid curation (open listing plus a certified tier), zero take while seeding, then volume-tiered. Seeding would start with first-party complements. Product analytics data is likely medium sensitivity, which supports hybrid curation. That is a default to confirm later, not a decision now.

## 4. Metrics to track now

- Share of customers with at least 1 installed connector, and integrations per account (watch the 4+ cluster).
- Retention delta between accounts above and below 4 integrations. This is the test of the retention case.
- RFP win rate on deals where the requested integration is native versus iPaaS-served.
- Time from RFP request to shipped integration.

Baseline these in the first quarter and compare against yourself. The skill says no published thresholds exist.

## 5. Payout cadence and merchant-of-record

**I'm not giving a cadence or MoR setup, for two reasons.**

1. **Out of scope for this skill.** The skill explicitly excludes billing and payout mechanics and routes them to `samber/developer-platform-skills@app-marketplace-monetization-model`. I haven't read that skill, and I won't invent a cadence or MoR recommendation without it.
2. **It is premature.** The recommended path has no partner payouts. Joined marketplaces pay or bill on their own terms, and an iPaaS is a vendor cost, not a partner payout. MoR and payout design only matter once partners sell through Statlas, which is after the promotion criteria above are met.

If you want, I can run the monetization skill next. Tax and merchant-of-record questions across jurisdictions need finance or legal input either way.

## What would flip this

- If third parties are already building on Statlas's API, or partners are asking to, trigger 2 passes and the case for build strengthens.
- If you can fund a dedicated partner team, trigger 4 passes.
- If most RFP integrations are with a few platforms that have no marketplace or iPaaS coverage, buy loses value and first-party wins.
- If the 40 are mostly marketplace-listing requirements, not deep integrations, join does most of the work.

**Open questions for you:**

- Is any third party asking to build on Statlas?
- Is there a hard date, such as a renewal or a board target?
- What is the effort ceiling beyond the two engineers?

I'd also check what share of the 40 integrations account for most RFP appearances, because that decides how many go first-party.