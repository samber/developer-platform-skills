# Dunmore Analytics: what to publish

## Recommendation

**Publish a horizon roadmap with release phases, and pair it with NDA customer briefings for the bank and insurer accounts. Do not publish dated quarters on day one.**

Dated quarters fail one of the four promotion conditions: finance has never reviewed the revenue-recognition exposure (ASC 606, or IFRS 15 outside the US). The other three hold:
- You run release phases.
- 1 of 12 items slipped last year.
- Buyers plan budgets around your release timing.

Finance sign-off is cheap to start and does not depend on the launch date, so dates become a phase 2 on the same page. Leadership gets a live page in three weeks and a dated version on a defined path.

I skipped the interview because your message answered all eight questions. I did not see the competitor's page, so I could not compare against it. I also do not know your actual item list.

## Why not the other postures

| Candidate | Verdict |
|---|---|
| **Horizon roadmap + NDA briefings (recommended)** | Fits a 2h/month budget. It gives sales one citable source and gives procurement evidence. Banks and insurers bring briefings up the ranking because procurement often needs them to close a deal. |
| **Dated quarters at launch** | Ineligible until finance has reviewed. A dated, named feature published to every customer is what revenue-recognition reviews look for. It also costs the most upkeep, because every date is a standing liability. |
| **Direction page + briefings only** | The fallback if the two review cycles below cannot happen in time, or if upkeep drops below 1h/month. It is cheaper but gives procurement less to hold. |

The citation rule is signed, so the "no public page until sales governance is fixed" rule does not apply to you.

## The policy

### 1. Purpose

The roadmap gives customers and sales one externally sayable view of direction, in the order we plan to deliver. It is not a delivery commitment. It is the only roadmap anyone customer-facing may cite.

### 2. Vocabulary

Each state says what a customer may rely on. States describe engineering reality, so no bucket hides a date.

| State | Customer may rely on | Time label |
|---|---|---|
| Exploring | We are researching the problem. Nothing is decided. | none |
| In design | Problem accepted, solution not fixed. | none |
| In build | Named internal owner, engineering underway. | none |
| Private preview | Invite-only access exists and can be requested. | quarter allowed (phase 2) |
| Public preview | Open access, with the preview-stage contract. | quarter allowed (phase 2) |
| GA | Shipped, with a changelog link. | none |
| Delayed / Descoped / Not planned | Status changed, with a reason. Stays visible at least one review cycle. | none |
| Proposed | Community request, not a vendor plan. Separate label. | none |

Rules:
- Write items problem-first: "Match records without a unique ID", not "Matching v2". That lets the solution change without breaking the promise.
- A quarter appears only with a phase, and only from private preview onward. A bare "Q1" reads as GA to every buyer and rep.
- Informal flags like "beta" show as a note on the item, not a phase, until their access rules are written.

### 3. Exclusion gate

The public roadmap is never the internal one minus a few rows. Mark an item public in the internal tool only if it passes.

Never publish:
- **Security and hardening work.**
- **Unannounced deprecations or breaking changes.** Once announced through your deprecation process, link the notice both ways.
- **Pricing, packaging and plan changes,** including anything that would cannibalize a current plan, so customers don't wait for the new version.
- **Data-provider and partner names, and M&A.** Name the capability ("firmographic coverage for a new region"), not the source, until the partner announces too.
- **Competitive bets and surprise launches.**
- **Customer-specific commitments.** These belong in that customer's order form, under legal review.
- **Internal plumbing,** such as refactors, infrastructure and the bug backlog.

The product lead decides edge cases and logs each ruling. The same gate applies to NDA briefings.

### 4. Guardrails

**Page disclaimer** (counsel approves the final wording; it has all four required elements):

> This roadmap is for information only. It is not a commitment to deliver any feature, and plans and timing may change at our discretion. Please make purchasing decisions based on features available today.

Repeat it on slide one of every NDA briefing deck, not in a footer.

**Contract status.** Your MSA and self-serve terms both carry the future-functionality clause, which is the hard part done. Remaining limits:
- The clause reduces reliance claims. It does not cover misrepresentation or deceptive-advertising claims, so never publish an item you know is off.
- Anything written into an order form, SOW or side letter binds regardless of the disclaimer.

**Pre-launch inventory.** You said no order forms name roadmap items. Confirm that against SOWs, side letters and security questionnaires. Also sweep what procurement teams already hold: RFP responses, roadmap decks and emails sent as "evidence". Under this skill's definition, anything shown to a customer as something to expect counts as a commitment.

**Citation rule** (signed by the sales leader and the CEO; covers reps, solutions engineers, customer success, DevRel and execs on stage):
1. Cite only the public roadmap, at the level printed on it. "In private preview, we can request access for you" is allowed. "It ships in Q1" is not, unless the page says so.
2. Deeper previews go through an NDA briefing or private-preview enrollment, with product present.
3. No dates in emails, proposals, decks or keynotes beyond what the page shows.
4. Legal and finance approve any roadmap item written into an order form, SOW or side letter.
5. A deal that depends on an unbuilt feature goes to product for a decision, never to a rep.
6. If an item a deal referenced slips, the account owner tells the customer before the public update, after legal checks the notice against the order-form terms.

### 5. NDA briefings for banks and insurers

- Show public items plus, at most, items product approved for that account.
- Never show unannounced deprecations, security work or partner names, even under NDA.
- Log every briefing: account, date, items, attendees. That log is how a later slip reaches everyone who saw the item.
- Briefings show phases, not dates, until finance clears phase 2.
- Name a briefing owner in product.

### 6. Feedback

**Locked items, with debate in your GitHub Discussions category.** Roadmap items are read-only, and each links to one Discussion thread. Community requests get the `Proposed` label and never read as plans. DevRel's weekly triage already exists, so no new board is needed.

Three guardrails:
- Don't add a separate voting board now. Votes skew toward the free self-serve tier, while your revenue sits with the MSA accounts.
- Give "not planned" its own status, with reasons.
- Treat any vote counts as one signal, weighted by segment, never the ranking.

### 7. Lifecycle

- **Surface:** a public GitHub repo with locked issues and a project board. It supports stable IDs, per-item subscriptions and comment locking.
- **Owner:** you, with a named backup.
- **Cadence:** monthly. Touch every item at each review: confirm, move, or mark Not planned.
- **Stable IDs** (e.g. `DA-014`) that survive from exploring to GA.
- **Subscriptions:** watch, feed or email digest, so a slip can notify anyone.
- **Closing:** close each shipped item with a changelog link.
- **Snapshots:** archive the page at each review. Banks' procurement teams get an audit trail of what was promised versus what shipped.

### 8. Slipped-item playbook

1. Change the status on the item itself: `delayed`, `descoped` or `not planned`. Never delete it.
2. Give a one-paragraph plain-language reason.
3. Offer a workaround.
4. Notify subscribers and every account the briefing log shows saw the item.
5. Customers with a contractual or procurement-evidence dependency hear privately from the account owner, days before the public update. Legal checks first, since a slip may trigger notice, credit or termination rights.
6. Keep cancelled items visible for at least one review cycle.

Last year's slipped item counts as a pre-page commitment. Before launch, check that the customers told to expect it heard the outcome.

### 9. Measurement

| Metric | Target |
|---|---|
| Freshness (items touched each review) | 100% |
| Silent removals | 0 |
| Close rate (shipped items with changelog link) | 100% |
| Slip rate, per step 8's definition | Track now. It gates phase 2. |
| Roadmap items in new order forms or side letters | Baseline before launch, compare quarterly |
| "When will X ship" questions to sales and support | Baseline before launch, compare after |

No independent evidence links public roadmaps to trust, churn or sales-cycle length, so don't promise leadership an ROI. Argue it on the trade-offs above.

## Upkeep budget: the tight spot

The planning assumption is about 15 minutes per public item per monthly review. At 2 hours a month, that is **8 items at most, and only if briefings and snapshots take no time.** Briefings need product present, and they come out of the same hours.

My advice is to **launch with 5–6 public items** and replace that estimate with your actual time after the first month. If briefings are a real workload for your bank accounts, you need more than 2 hours, or product time outside the budget. Treat that as a decision to make with leadership, not something to absorb quietly.

## Three-week plan

| When | Do |
|---|---|
| Week 1 | Run the first internal review cycle: every candidate item gets a decided status. Apply the exclusion gate. Start the contract and procurement inventory. Send finance a short brief covering the phase-2 dates and ask for a review. Send counsel the disclaimer and the clause check. |
| Week 2 | Run the second review cycle. Publication needs two cycles of decided statuses. Compressing them into three weeks is a deviation from a normal monthly rhythm, so say so. Get the citation rule signed. Handle last year's slipped item and any pre-page commitments. Draft items in the template. |
| Week 3 | Counsel signs the disclaimer. Product, sales leadership, the CEO and counsel give written approval. Brief sales. Set up the repo, Discussions links and subscriptions. Take the first snapshot. **Go live.** |

**Launch checklist, all required:**
- [ ] Citation rule signed by the sales leader and the CEO
- [ ] Contract and procurement inventory done, pre-page slips handled
- [ ] Two review cycles done, no undecided statuses
- [ ] Disclaimer approved by counsel
- [ ] Written approval from product, sales leadership and counsel
- [ ] Briefing log and owner in place

## Phase 2: adding dated quarters

Ship phase 2 only when all four hold:
1. Release phases are running (yes).
2. Slip rate is still low. 1 of 12 is a small sample, so track it through the first quarters.
3. Buyers plan around your dates (yes).
4. **Finance has reviewed the exposure in writing.**

Ask finance these questions:
- Does a quarter on a named feature in private or public preview create a "valid expectation of specified upgrades"?
- Does that change how MSA revenue is allocated?
- Does the answer differ for the self-serve tier?

If they clear it, add quarters only to items in private preview or later, always capped by the phase ("Q1 – private preview"). Each such date carries the slip playbook. Dating a feature that has not reached private preview is never allowed under this policy.

## Decisions to take back

1. Is 5–6 items enough for leadership, and are briefings inside or outside the 2h budget?
2. Who on the finance side owns the revenue-recognition review, and by when?
3. Who is the backup owner?

## Where this skill's rules stop

I applied the skill's rules as written. Counsel has the final say on the disclaimer and on whether the existing clauses hold up in your jurisdictions. This is not legal or accounting advice.