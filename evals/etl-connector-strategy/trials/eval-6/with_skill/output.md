# Sablefin connector: marketing claim and certification cost

I assumed "marketplace" means Airbyte's Marketplace, because a merged connector PR is that contribution path. If you're on another platform, the claim analysis changes, so tell me. The program details come from a snapshot dated 2026-08-30 and should be re-checked against Airbyte's current partner docs before anything is published.

## 1. Do not publish "Certified connector, supported by the platform" ❌

Both halves of the phrase are wrong for what you shipped.

- **"Certified" is wrong.** A merged PR gets you Marketplace inclusion, which only means the connector passed the standard test suite. Airbyte keeps that bar low on purpose. Certification is a separate, optional tier that is earned afterwards.
- **"Supported by the platform" is wrong.** Marketplace connectors are community-maintained. Airbyte's own wording is that they are "not covered by Airbyte support SLAs… may experience backward-incompatible, breaking changes with no notice." The platform's support commitment applies to the Certified tier, not to your listing.
- **Whoever supports it is you.** If a customer's sync breaks, Sablefin owns the fix.

In the security questionnaire this is worse than a marketing overstatement. It is a false statement in a document that customers rely on for procurement, and it tells their security teams they have a vendor-backed SLA that doesn't exist. Remove it from the boilerplate before it goes into another questionnaire. Also check which questionnaires have already gone out with it.

### Wording you can use today ✅

**Integrations page:**
> Sablefin is available as a source connector in the Airbyte Marketplace. Sync your reconciliation data to your warehouse with incremental sync. The connector is maintained by Sablefin.

**Security questionnaire boilerplate:**
> Sablefin provides a source connector listed in the Airbyte Marketplace, a community-tier listing. The connector is built, maintained, and supported by Sablefin. It is not covered by Airbyte's support SLAs. Sync is incremental and eventually consistent, with a [X]-minute poll interval. Changes overwritten within one interval, and hard deletes (if no deletion feed exists), may not be reflected downstream.

Keep that last sentence. "CDC" without that scoping is the other claim that fails customer data audits. Sales should say "incremental sync," never an unqualified "CDC support." Fill in the real poll interval, and confirm with engineering whether you expose a delete or change feed.

If sales still wants the word "Certified," that is a goal for later and shouldn't be claimed now (see section 2).

## 2. The Partner Certified badge, for the CTO

**Partner Certified doesn't exist for you.** It applies to destination connectors only. Sablefin is a source, so the badge isn't available however much effort you put in. Fivetran has no equivalent either. Its Partner-Built program is closed to new source partners, and its Connector SDK listing carries no badge.

**Cost: no fee on any platform.** Neither Airbyte nor the others charge a source vendor for certification, and none pays you for it. The cost is engineering time, so it can't be quoted as a price. I won't invent a dollar figure, and the reference material doesn't contain one.

**The tier you can actually target is Airbyte Certified.** It is optional and earned, and it is judged on reliability rather than feature count. The criteria the reference lists:
- Every supported sync mode is integration-tested.
- Incremental sync wherever the source allows it.
- Fast, actionable failures. Never accept a configuration that is guaranteed to break.

Airbyte publishes numeric bars only for Partner Certified: at least 95% first-sync success, at least 95% overall sync success, first response within 3 business days, and an update at least every 6 months. Adopt those as Sablefin's own SLOs now, since they are the best proxy for what a reviewer would look for. They are not confirmed requirements for the source Certified tier.

**March is not something I can promise.** Three reasons:
1. Certification is earned after the connector holds up in real syncs, and you went live on Tuesday. You have no sync history yet.
2. I have no published review timeline or application process for the Certified tier in the reference. The promotion decision is Airbyte's, not yours.
3. The criteria are quality-based, so the date depends on how clean your first months of production syncs are.

**What to tell the CTO:**
- Partner Certified is off the table because it is destinations-only.
- Airbyte Certified is the realistic target. It costs engineering time and has no fee.
- Ask Airbyte directly what the path and timeline are for promoting your source from Marketplace to Certified.
- Present March as a stretch goal and don't announce it at the user conference. If it doesn't land, "available in the Airbyte Marketplace, maintained by Sablefin" is still a true statement.

## 3. Actions, in order

1. ⏳ **Today:** pull the "Certified / supported by the platform" line from the integrations page draft and the questionnaire boilerplate. Audit questionnaires already sent.
2. Replace both with the wording above, and fill in the poll interval.
3. Name the connector owner for month 13. You are the support path, and a side-task owner is how connectors decay.
4. Budget maintenance at 15–30% of the original build cost per year, up to 50% in high-change phases. These are vendor-published estimates, so treat them as an order of magnitude.
5. Alert on sync failures and schema-drift errors instead of waiting for tickets, because Marketplace listings carry no platform SLA.
6. Baseline sync success rate against the 95% bar now, so you know how far you are when you ask Airbyte about Certified.
7. Email Airbyte to ask about the source Certified path and timeline.

Two questions would sharpen this. Which platform is the marketplace? And do you have a delete or change feed on the Sablefin API? That affects the "what it misses" wording and the Certified readiness.