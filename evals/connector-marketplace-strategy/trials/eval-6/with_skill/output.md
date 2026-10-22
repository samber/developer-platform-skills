# Onwards Labs: connector marketplace sanity check and seeding sequence

Drafted from the `connector-marketplace-strategy` skill. Its interview asks one question per message, and I can't interview you here. So I've stated my assumptions in §0 and marked each one. Correct them before you treat this as final.

## Verdict

❌ **The plan as written fails.** It uses three of the skill's rungs in the wrong order, and two of them need things you don't have.

| Plan element | Verdict | Why |
|---|---|---|
| 60 connectors, every category | ❌ Cut to a launch catalog of about 6-10 in one cluster | The skill wants a dense atomic network, not a broad thin catalog. Nobody is on record as building or maintaining 60 connectors in 4 months. A wide catalog full of stale or empty entries is the "expensive partner directory" failure. |
| $50k hackathon in month one | ❌ Defer to after launch, and size it to what finance approves | Hackathons are the slowest seeding rung. They compound only on top of an existing community, and you have none (31 portal developers, no Discord, no meetups). Month one also has no proven docs, sandbox or review path for entrants. |
| Build fund | ⚠️ Keep the idea, gate it | A subsidy is promoted by a hard deadline with budget behind it. You have the deadline and no budget. Ask finance for a conditional fund (§6). |

⚠️ **The skill also questions whether you should build at all.** Several of its build triggers are unevidenced or failing (§1). The recommendation is to launch on the date as a **curated partner catalog**, with first-party connectors and a few design partners. Treat "marketplace" as the later promotion once the evidence exists. The shell you built isn't wasted, but it shouldn't set the catalog size.

**Next action (this week):** pull lost-deal and support-ticket data for integration requests. It decides almost everything below. It's about half a day of work.

## 0. Interview: assumed answers

Correct any of these. The ones marked 🔴 change the recommendation.

| # | Question | Assumed from your message | Confidence |
|---|---|---|---|
| 1 | Ecosystem today | Shell built, so (b)/(c) at best. No external ecosystem. | ⚠️ Confirm what bilateral integrations exist. |
| 2 | Demand evidence | **Unknown.** The plan lists categories "we can think of", which sounds like 2d (strategic, no data). | 🔴 |
| 3 | Supply evidence | Closest to (c) neither. The 31 portal developers are customers' internal teams building for themselves, not partners asking to build on you. | 🔴 |
| 4 | Staffing the full partner lifecycle | Not stated, assumed no standing team. | 🔴 |
| 5 | Purpose | Unclear. I set it to retention/stickiness (§1). | ⚠️ |
| 6 | Data sensitivity | **High.** Expense data covers card data, employee PII (HRIS) and ledger data (accounting). | ⚠️ Confirm. |
| 7 | Deadline | Hard, about 4 months, so launch is around **2027-02-08**. | ✅ |
| 8 | One-off vs compounding | Unstated, assumed compounding. | ⚠️ |
| 9 | Effort ceiling | No subsidy budget. Headcount and engineering hours unstated. | 🔴 |

## 1. Gate: build, join or buy

Build requires all four triggers, each with cited evidence.

| Trigger | Status | Evidence |
|---|---|---|
| 1. Customer pull (Q2 a-c) | ❓ Unproven | None cited. Pull the data. |
| 2. Supply signal (Q3 a/b) | ❌ Fails today | 31 developers, nearly all internal at customers. No partners asking to build, and no unofficial third-party connectors cited. |
| 3. Procurement friction from one-off requests | ❓ Unproven | Ask sales and solutions engineering. |
| 4. Readiness for the full partner lifecycle (Q4) | ❓ Unconfirmed | Needs a named standing owner, not a project team. |

**Recommendation: not yet "build". Launch a curated partner catalog on the fixed date.** Promote it to a marketplace when the triggers hold (§8).

The three paths:
- **Join:** list on the accounting and ERP marketplaces your customers already trust. This borrows their distribution and costs little.
- **Buy:** an embedded iPaaS suits the real need ("many integrations fast"). If sales shows long-tail demand across HRIS, travel and BI, buy that breadth rather than building 60 connectors. It needs its own budget approval, so ask finance for it separately.
- **Build:** this is the plan on the table. Its supply side is the weakest part.

**Which business case carries the decision: retention/expansion.** Customers with 4+ integrations churn measurably less, and buyers rank integration capability highly. The ecosystem-flywheel case doesn't apply at 31 developers. What would kill it: after two full quarters, accounts with a connector installed show no better retention or expansion than comparable accounts without one. Beware selection bias, since engaged customers install more. Compare cohorts matched on size and tenure.

## 2. Operating model: three candidates

| | A. Curated catalog, first-party seeded (recommended) | B. Bought breadth | C. Your lead's plan |
|---|---|---|---|
| Archetype | HubSpot: zero take, listed/certified ladder | An embedded-iPaaS-backed marketplace | A Shopify- or AppExchange-style open marketplace |
| Curation | Hard review gate while the catalog is small (§4) | The vendor's connectors, with you reviewing the surface | Open, many listings |
| Partner mix | First-party, 3-5 design-partner customers, 2-3 anchor ISVs | The iPaaS vendor plus yours | Long-tail builders |
| Take-rate | 0% | 0%, since the cost is the iPaaS licence | Implied tiered, unspecified |
| Seeding | First-party, then Trojan-horse tool, then gated subsidy | Vendor-supplied | Hackathon plus build fund |
| Optimizes for | Retention, trust, density | Breadth by the deadline | Buzz |
| Costs | Engineering time, a standing partner owner | An iPaaS licence and vendor lock-in | $50k plus an unfunded fund |
| Failure mode | Slow catalog growth | You become a reseller of someone else's ecosystem | Empty or stale directory |

**Pick A.** It fits the effort ceiling, since it needs no approved subsidy budget, and it fits a hard date and a high-sensitivity domain. B is the contingency if the data in §1 shows broad long-tail demand. Say which you pick before I detail §§3-6 any further.

## 3. Governance (under model A)

| Question | Rule | Owner |
|---|---|---|
| **Admission** | Invite-only at launch. A connector is listed after passing the §4 review. | 🔴 Name one person (ecosystem lead, proposed). |
| **Value split** | 0% take, partner keeps 100% of what it bills (§5). | Finance plus ecosystem lead. |
| **Conflict and removal** | Delist for failed security review, scope creep, or an unmaintained connector (no update for two quarters, proposed). Notice is 30 days, except security, which is immediate (both periods are my proposals). Appeals go to a named review panel. | Security lead for removals, ecosystem lead for appeals. |

Each rule traces to a platform failure cause:
- **Information asymmetry:** disclosure of data scopes on every listing.
- **Externalities:** review plus delisting, because one bad connector damages every customer's trust.
- **Monopoly power:** the notice period for any rule change, and shared analytics for partners.
- **Risk:** least-privilege OAuth scopes, post-approval monitoring.

Two further commitments:
- **Concentration:** commit now to pooled scale (shared analytics and listing-performance dashboards for all partners), so a few winners don't dominate.
- **Review cadence:** schedule a governance review at six months. Curation criteria should loosen over time, not stay at launch settings.

Paid featured placement doesn't exist at launch. If added later, label it and disclose it.

## 4. Quality bar

**Recommendation: a single hard review gate for launch.**

The skill's default is the hybrid (open + certified tier). Question 6 = high promotes the hard gate instead, because every connector would touch card, PII or ledger data. At 6-10 listings the gate's cost scales trivially, so its usual efficiency penalty doesn't bite. The gate has four stages:
1. Submission completeness.
2. Data-handling compliance.
3. Security testing with OAuth-scope minimization.
4. Post-approval monitoring with removal authority.

**Promotion condition:** when review queue time exceeds the target or submissions outpace reviewers, split into an open "listed" tier plus a "certified" tier. That decouples "allowed to exist" from "endorsed". Review the first-party connectors through the same gate. That tests the process before any partner depends on it.

If Q6 is actually low or medium, step down to the hybrid.

## 5. Economics

**Recommendation: 0% take at launch.**

- Zero take is the only subsidy that costs no approved budget, and it fits a cold start. Taxing the hard side first selects against the supply you need.
- No billing flows through your platform at launch, so there's no fee stack and nothing to circumvent.
- **Commit now to six months' notice** for any rate change, in writing in the strategy doc.

**Promotion condition to volume-tiered** (0% under a revenue threshold, a moderate percentage above): billing runs through your platform and some partners visibly win. A flat percentage plus fees is earned only by a distribution position the partner can't replicate. You don't have that yet. A tiered take-rate would also need an anti-circumvention rule backed by delisting. Billing mechanics belong to the monetization sibling skill.

## 6. Seeding sequence

**Hard side: the connector builders.** That means your own engineers first, then anchor ISVs and customer developers. Customers will follow once connectors work.

**Atomic network: one use case, dense.** My hypothesis is expense-to-accounting sync (the ledger side), but let the §1 data pick it. If the data points elsewhere (for example, HRIS for employee provisioning), use that.

### Phases (today is 2026-10-08, launch about 2027-02-08)

| Weeks | Phase | Actions | Output |
|---|---|---|---|
| 1-2 | **0. Evidence and decisions** | Pull lost-deal and support data. Interview all 31 portal developers: what have they built, what would they list? Confirm Q2-Q4 and Q9. Ask finance for the conditional fund (below). Pick the atomic network. | Confirmed gate, chosen cluster, owner named |
| 2-10 | **1. First-party seeding (default rung)** | Build 3-5 first-party connectors in the cluster. Publish API docs, sandbox tenancy and a **connector template or SDK** (the Trojan-horse tool, useful on its own). List on 1-2 third-party marketplaces where your customers already are. | Day-one value with zero external dependency |
| 6-14 | **2. Design partners** | Sign 3-5 of the 31 developers' teams to turn their private integrations into listed connectors. Open bilateral talks with 2-3 anchor ISVs in the cluster (for example, the accounting vendors) about co-listing. Run every connector through the §4 gate. | 3-5 external connectors in the review pipeline |
| 14-16 | **3. Launch** | Ship with about **6-10** connectors, all in one cluster. Announce through existing customers. | Catalog live |
| Months 5-6 | **4. Community** | Stand up a lightweight community around the partner cohort: office hours, a forum or Discord, a public roadmap. | A base for a hackathon to build on |
| Month 6+ | **5. Hackathon and fund, if earned** | See promotion conditions below. | Scale layer |

The 60-connector target becomes a 12-18 month backlog, not a launch KPI. Mark the other categories as "planned" only where you have a named owner for each.

### Conditional fund: the ask to finance

Ask for a fund that releases in tranches:
- **No up-front grants.** Pay on milestones: connector passes review, goes live, and stays maintained for 90 days.
- **Cap total exposure** to what finance approves, and size the first tranche to the design-partner count (3-5), not 60.
- The hackathon draws from this same fund. If finance approves less than $50k, scale the hackathon down. Don't fund it by overspending.

### Promotion conditions

| Rung | Promoted when |
|---|---|
| Subsidies (build fund) | Finance approves budget **and** launch review process is live |
| Hackathon | Enough active external builders to form a community. I propose 15-25 as a starting threshold, but calibrate it against your own first-quarter data. |
| Sequential tool | The SDK or template sees no outside use after a quarter: revisit what the hard side actually wants |
| Buy (iPaaS) | Phase 0 data shows broad long-tail demand across categories |

## 7. Flywheel measurement

The document passes only when:
1. Each build trigger in §1 cites concrete evidence. Today three are unevidenced and one fails, which is why the recommendation is "catalog first".
2. All three governance questions have a written, owner-assigned answer, including the removal path. §3 has it, but the owner names are open.
3. The seeding plan names the hard side, the atomic network and the chosen rung with its promotion condition (§6).

Post-launch metrics. Baseline them against your own first quarter, because no industry thresholds exist at your scale:

- **Supply (lead with these, it's the hard side):** active partners with a live listing, time from signup to first live listing, share of the catalog updated in the last two quarters, partner revenue concentration.
- **Demand:** share of your 2,400 customers with at least one installed connector, integrations per account (watch the 4+ cluster), and the retention delta between accounts above and below that cluster.
- **Flywheel coupling:** marketplace influence on new deals and churn saves. This attribution is soft, so say so in the document. Direction matters more than precision.

## 8. Promotion criteria: from catalog to marketplace

Revisit "build" when all four hold:
1. Documented customer pull (lost deals or repeated requests).
2. At least some external partners building without being asked or paid.
3. Repeated procurement friction from one-off integration requests.
4. A funded standing owner for the partner lifecycle.

## Open items for you

1. 🔴 Confirm the 🔴 assumptions in §0, especially Q2, Q3, Q4 and Q9.
2. Pick the operating model: A, B or C.
3. Name an owner for admission and removal decisions.
4. Confirm Q6 (high sensitivity), since it sets the curation rung.
5. Approve section by section. The skill requires approval of each section, then the whole document, before it counts as final.

I didn't write `developer-platform-context.md`. Say so if you want the chosen path, trigger evidence and rung promotion conditions saved there.