# Cadence Ops Marketplace Operating Model

**Prepared 2026-10-08 for the board meeting on Thursday. Status: recommendation for decision.**

## 0. Read this first

I wrote this without interviewing you, so I made assumptions. Each is flagged ⚠️ and listed in section 12. If any is wrong, the affected section changes. I say which ones.

**The recommendation in five lines:**

1. ✅ Build a **curated marketplace on the public API**. Partners build and list the apps. We do not run partner code.
2. ✅ Let the six partners charge from day one, **billing customers themselves**. We take **0%** until the pool is liquid.
3. ✅ Offer the three unofficial builders a **90-day path to official status**. Do not sue first, and do not break them silently.
4. ⚠️ Marketplace revenue is small. Expect about **$120K a year at maturity**, or 0.5% of ARR. The case is retention and expansion, not take-rate.
5. 🟠 Two partner engineers cannot carry this alone. Request **one hire plus a fractional security reviewer**. Without them, cap the program at 12 Verified apps.

## 1. Strategic hypothesis

Because our customers need **complements we will not build** (accounting, payroll, parts ordering, telematics, vertical add-ons), **independent software vendors and integrators** will build them on **our public API and webhooks**. Their return is **license revenue and deal flow from our 1,100 accounts**. That makes Cadence more valuable to **operations buyers** because **each integrated account is harder to leave and wider in usage**.

**Complement we commoditize:** connectors and vertical add-ons. We want them abundant and cheap. We do not want core scheduling and dispatch commoditized, so the roadmap boundary in section 6 protects it.

## 2. Evidence and gates

| Gate | Status | Evidence / resolver |
|---|---|---|
| Counted demand | ✅ Pass | 6 partners asking to charge. 3 unofficial integrations built by reverse-engineering our web app. That is the strongest demand signal there is: people pay engineering cost to integrate without our permission. |
| Complementor supply | ✅ Pass | 40 listed integrations, 6 with a commercial motive. |
| Architectural readiness | ⚠️ Unknown | The public API is documented. Unknown: does it cover what the unofficial builders scrape? **Resolver:** audit their endpoint usage, 2 weeks (section 8). |
| Staffing | 🟠 Partial | 2 partner engineers exist. Review, support and billing ops are not staffed. |
| Envelopment risk | ⚠️ Unknown | Name which larger FSM or ERP platform could bundle this category (ServiceTitan-class vendors, ERP suites). **Resolver:** board discussion Thursday. |
| Security function | ⚠️ Unknown | Field-service data includes customer addresses, access codes, technician locations and job photos. Assumed no dedicated reviewer. |

**Rung chosen:** partner-built integrations listed by us, on the documented API. This is rung 1 of 6 on the openness ladder.

**Rungs deleted:**
- **Installable apps that run inside our product.** Needs a standing security and tenant-isolation team we do not have.
- **Runtime platform.** No evidence any complement must run in our execution context.

**Promotion condition for installable apps:** more than 25% of Verified partners ask for in-product UI surfaces, and a security reviewer is funded. Revisit at month 12.

## 3. Curation model

**Position: open submission, curated listing, because the data is sensitive.**
- Anyone may build against the API with a sandbox. There is no gate on building.
- Only reviewed apps reach the marketplace. Field-service data (addresses, access instructions, technician locations) makes brand damage from a bad app high. And with 40 current partners, human review still scales.

**Two tiers. More would confuse partners.**

| | **Listed** | **Verified** |
|---|---|---|
| Who | Any partner passing automated and attestation checks | Partners passing security review and an SLA |
| Review | Automated scope check, privacy policy, working demo, support contact | Manual security review, data-handling questionnaire, 2 reference customers |
| Can charge through the marketplace | No | **Yes** |
| Badge and search ranking | Standard | Verified badge, ranked higher |
| Review SLA | 5 business days | 15 business days |

**Strategic partners** are not a third tier. They are invited co-development deals, capped at 3 at any time, because the two engineers are the limit.

**Discovery and trust layers** (so quality surfaces without us hand-picking winners):
- Install counts, active-account counts, and a health score (error rate, uptime, support responsiveness).
- Customer ratings, but only from accounts with an active install.
- Category pages built around the demand list.

## 4. Revenue model

### Principle

Keep the take-rate at **zero until there is a market worth taxing**. A fee charged before liquidity eats the surplus that makes a partner build. ⚠️ This is a design rule I reasoned from the partner arithmetic, not a measured benchmark.

### Phases

| Phase | When | Who bills | Cadence take |
|---|---|---|---|
| **A: Partner-billed** | Launch to the exit test below | Partner bills customer directly. Customer owns the contract. | **0%** |
| **B: Marketplace-billed (optional)** | After the exit test | Cadence invoices on the partner's behalf, on the customer's existing invoice | **15% flat** on marketplace-billed revenue |

**Exit test for Phase A → B:** at least 8 Verified apps, at least 150 accounts with an active paid app, and 2 consecutive quarters of positive net new apps.

**Rules:**
- Partners set their own prices. No price floor, no most-favored-customer clause.
- Phase B is optional. Partners may keep billing directly. We never force migration.
- No take on partner-billed revenue, ever. Taxing revenue we cannot see invites evasion and builds distrust.
- Give 12 months' notice before any rate change, and publish the schedule now.
- Agencies and integrators get referral flow and certification, not revenue share.

### Sizing (illustrative, all inputs assumed)

| Input | Assumption |
|---|---|
| Accounts | 1,100 |
| Accounts buying a paid app at maturity | 20% (220) |
| Paid apps per buying account | 2 |
| Average price per app | $150/month |

- Gross marketplace volume: 220 × 2 × $150 × 12 = **$792K a year**
- Cadence at 15%: **about $119K a year**

⚠️ I have no baseline. Pull the current share of accounts using any integration before Thursday and replace these inputs.

### Why the board should still care

Retaining 1 point of the $22M ARR is worth **about $220K a year**. If integrated accounts churn even 1 to 2 points less than non-integrated ones, the retention effect beats the take-rate by 2 to 4 times. **Test that with the cohort comparison in section 9 before claiming it.**

## 5. Governance rules (partner agreement summary)

**Data and security**
1. OAuth with least-privilege scopes only. Partners may not scrape the web app or use undocumented endpoints.
2. Partners are processors for customer data and use it only to deliver the app.
3. On uninstall, the partner deletes customer data within 30 days and confirms in writing.
4. Security incidents involving our customers' data: notify us within 24 hours, and notify customers within 72 hours.
5. Technician location and job photos are a restricted scope. Verified tier only, with a stated purpose.

**Quality**
6. Verified apps meet a 99.5% uptime target and a response time to customers of 2 business days.
7. Health score below threshold for 2 consecutive quarters triggers a remediation plan, then delisting.

**Our obligations**
8. **API stability.** Breaking changes need 12 months' notice on major versions and 6 months on individual endpoints. Published changelog. Versioned from day one.
9. **Roadmap boundary.** We will not build in categories on a published list. We give 90 days' notice before entering a listed category. The list can change, and we say so openly.
10. **Wind-down.** If we shut a surface or the marketplace, partners get 12 months' notice, a migration path and data export.

**Process**
11. Delisting: written notice with reasons, 14 days to cure, except for security incidents, which allow immediate suspension.
12. Disputes go to a named owner first, then the VP Product, with a 10-business-day decision SLA.
13. Customers own their data and their relationship with the partner. We are not liable for partner apps, but we handle escalation.

## 6. Obligations register (owner required)

| Obligation | Owner (⚠️ proposed) |
|---|---|
| API versioning and deprecation | VP Engineering |
| Security review | Fractional security reviewer (to hire) |
| Partner support and escalation | Partner engineers |
| Roadmap boundary list and notices | VP Product |
| Billing and disputes (Phase B) | Finance lead |
| Wind-down terms | Legal |

Every published API surface goes into a liability register. The register, not the architecture diagram, tells us whether the next refactor is affordable.

## 7. Seeding plan

**Subsidize the partner side.** Free sandbox, free listing, free review in year 1.

**Founding cohort: 10 partners, chosen by hand for coverage of the demand list, not logo value**
- The **6 partners asking to charge**, onboarded to Verified first.
- **4 more** covering the largest unmet requests from the demand list. ⚠️ I have not seen this list. Build it from the last 5 to 10 customer requests we refused.

**Triage the 40 existing integrations by end of month 2:**
- **Keep as Listed:** most of them.
- **Fast-track to Verified:** about 12, ranked by active accounts.
- **Sunset:** any with no active installs or no support contact, with 90 days' notice.

**Distribution we commit to** (partners leave when we stop pointing at them):
- In-product "Integrations" page with category browse.
- Mention in onboarding for new accounts.
- CS and sales playbook listing the top 10 apps by use case.
- Quarterly partner spotlight to customers.

**Minimum credible pool:** 12 Verified apps across at least 5 categories. Below that, the marketplace reads as abandoned. **Do not launch publicly before reaching it.** Soft-launch to customers via CS until then.

**Reference builds:** the two engineers build or rebuild at most **2** reference apps to set the pattern, then hand them to partners.

## 8. Unofficial integrations (the three third parties)

Treat them as paid-for demand research and as a risk.

1. **Weeks 1 to 2:** log which web-app endpoints they call, which customers use them, and what data moves. This tells us the API gaps.
2. **Weeks 2 to 4:** contact each one personally. Offer official status, a sandbox, and priority review. Tell them access via the web app will end.
3. **Days 30 to 90:** close the gaps they rely on in the public API. Send customers who use these integrations a clear notice.
4. **Day 90:** block undocumented access with technical measures and terms-of-service enforcement. Do it only after a published notice, never silently, because it breaks live customers.

If any of the three refuses, enforce at day 90 and offer affected customers the official alternative. ⚠️ Legal must confirm the terms of service cover reverse engineering, and what exposure the existing scraping creates for customer data.

## 9. Measurement

Pull **baselines before Thursday**. Targets below are defaults I set so the board can argue about them, not industry benchmarks.

| Metric | Baseline | Target |
|---|---|---|
| Accounts with at least 1 active integration | **Pull today** | +15 pts in 12 months |
| Churn gap: integrated vs non-integrated accounts | **Pull today** | Documented by month 6. Funds the program. |
| Verified apps | 0 | 12 by month 6, 20 by month 12 |
| Net new apps per quarter | n/a | ≥ 3 |
| Share of registered builders who ship anything | n/a | ≥ 40% |
| Concentration: top-5 apps' share of installs | **Pull today** | < 60% |
| Cost: eng hours and support tickets from partner code | n/a | Tracked from launch |

Report **active apps per account**, never announced partners.

## 10. Timeline

| When | Milestone |
|---|---|
| Thursday | Board decision on scope and headcount |
| Nov 2026 | Baselines, endpoint audit, security reviewer engaged, partner agreement drafted, triage of the 40 |
| Dec 2026 – Jan 2027 | Review process live, first 6 Verified (the six charging partners), unofficial-builder outreach |
| Feb – Mar 2027 | Soft launch to customers via CS, 12 Verified target |
| Apr 2027 | Public launch if minimum pool is met |
| Q3 2027 | Phase A → B exit test |
| Q4 2027 | Decide on installable apps (section 2 condition) |

## 11. Kill and de-escalate criteria

- **Month 6:** fewer than 6 Verified apps or fewer than 50 accounts with a paid app → pause paid listing and return to a free directory plus API.
- **Month 12:** the churn gap between integrated and non-integrated accounts is under 1 point after controlling for account size → stop investing beyond maintenance, and drop the retention story.
- **Any time:** a partner-caused data incident reaches customers → pause new Verified approvals until the review process is rebuilt.
- **Any time:** review backlog exceeds 30 business days for two consecutive months → freeze new submissions. Staffing is the failure, not demand.

## 12. Decisions for the board and open assumptions

**Decisions requested Thursday:**
1. Approve the curated model with partner-billed Phase A at 0%.
2. Approve one ecosystem hire and a fractional security reviewer (cost to be quoted).
3. Approve the 90-day path for the three unofficial builders.
4. Approve the kill criteria in section 11.

**⚠️ Assumptions to check, and what changes if wrong:**
- **No dedicated security reviewer exists.** If one exists, staffing improves and the ramp can be faster.
- **The partner contract, billing and support functions are unstaffed.** If Finance already supports partner billing, Phase B moves earlier.
- **API coverage gaps unknown.** Gaps push the timeline right by up to 2 months.
- **All sizing inputs are guesses.** Replace them with real data.
- **The envelopment threat is unnamed.** The board should name it.
- **Partner terms:** I have not seen the six partners' current agreements. They may already contain terms that conflict with section 5.