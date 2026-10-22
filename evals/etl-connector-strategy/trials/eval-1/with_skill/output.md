# Business case: Cadenza source connector for ELT platforms

**Status: not yet approvable.** I can't write the revenue line or a payback date you can defend. I also can't confirm the demand evidence the funding gate requires. Section 3 says what to bring the CFO instead.

## 1. Why there is no revenue line

- No ELT platform pays a source vendor for a connector. There is no revenue share, referral fee or reseller margin.
- The one platform that floated revenue share shipped flat one-time bounties of $10–150 per task instead.
- Certification costs engineering time, not a fee. Nobody pays you for it either.
- The reseller and referral model the CFO used last year doesn't carry over. A connector is a cost center bought for **support deflection, retention and competitive parity**. Putting an income line in this case would fail at finance review, so I left it out.

## 2. Cost

| Item | Estimate | Basis |
|---|---|---|
| First build | 9 weeks of engineering | Engineering's quote |
| Cost of the build | **C = 9 weeks × team size × loaded weekly cost** (fill in) | Needs Finance's loaded rate |
| Annual upkeep | **15–30% of C per year, up to 50% in high-change phases** | Vendor-published figures, so an order of magnitude |
| Month-13 owner | Must be a named team with standing budget | A side-task is how connectors decay |

Illustrative only, with the inputs being my assumptions: 3 engineers at $4k per loaded week gives C ≈ $108k. Upkeep would then be about $16–32k a year.

Two costs are not in the quote:
- **API fixes.** Cadenza's API may need an incremental cursor, a bulk export and a delete signal first. That work may cost more than the connector.
- **Platform review.** The platform's review adds weeks and can reject the source. A managed-listing path would cut your build effort but adds that gate.

## 3. Benefit and payback

Payback comes from two things only:

1. **Retention.** ARR kept from customers with a data team who would otherwise churn over data-stack incompatibility.
2. **Support deflection.** Tickets and engineer time no longer spent helping customers who hand-roll pipelines against your API.

Competitive parity (appearing in the catalogs) is real but hard to attribute, so I assign it no dollar value.

**Payback formula:** payback in months = C ÷ (monthly retained gross profit + monthly support savings − monthly upkeep)

Average ARR per customer is $18M ÷ 1,400 ≈ **$12.9k**. That lets you state the case as a break-even count, which I can defend without guessing at churn:

- **Break-even in year 1:** (C + year-1 upkeep) ÷ (annual gross profit per retained customer).
- **Illustrative:** with C ≈ $108k and upkeep ≈ $24k, that's about $132k. At $12.9k revenue and an assumed 80% gross margin (about $10.3k each), you need roughly **13 customers retained or won** in year 1. That is about 0.9% of your base, before counting any support savings.
- **What I can't fill in:** how many customers that is. It needs the evidence below.

## 4. Decision gate (what the CFO should require)

I could not run the demand interview, so none of these are confirmed. **No build approval until at least one exists:**

- Support tickets asking for a named ELT platform.
- Lost-deal or churn notes citing the data stack.
- API logs showing customers extracting data on a schedule.
- Procurement questionnaires asking about warehouse sync.

**Reopen signal if evidence is thin today:** three named-platform tickets in a quarter, or one lost deal citing the gap. Meanwhile, improving the raw API for extraction helps every customer's own pipelines.

## 5. Scope and recommendation

- **Platform:** one platform, chosen from where your customers' data teams actually run. If you don't know, run a short customer survey first.
- **Build path:** default to the platform-managed listing. It carries the lowest upkeep exposure and the least control. Move to the vendor SDK only if the platform rejects the source or you need control over sync logic.
- **CDC wording:** say "incremental sync, eventual consistency" and state the poll interval. Name what it misses: overwrites within an interval, and hard deletes until a delete feed exists. Don't promise "CDC."
- **Success metrics, baselined in the first quarter:**
  - Tickets deflected.
  - Sync success rate against the ≥95% bar.
  - Share of new customers connecting through the platform versus the raw API.

## 6. What I need from you to finish the case

1. Which ELT platforms do customers ask for, and how many tickets or lost deals can you name?
2. Does the Cadenza API already have a stable incremental cursor, a bulk export and a delete signal?
3. Who owns the connector in month 13, and how many hours a month can they spend?
4. Is there a deadline, such as a deal to unblock?
5. How many engineers are on the 9-week quote, and what is the loaded weekly rate?

With those answers I can replace the illustrative numbers with a real payback period.