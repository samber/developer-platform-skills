**Verdict: all four parts of the proposal need to change.** First action: call Ridgeway's technical owner this week, before anything else ships, including the rename.

You are 5 months into a 6-month private preview with no written terms and no exit criteria. The skill treats that as a rescue case. Fix the paperwork first, then decide the outcome.

## 1. "Extend 6 more months because we're close"

- **Too long.** The rule allows one extension, at most half the original time box. That is 3 months. Six more makes 11 months, which is close to the 12-month line the skill calls a perpetual beta.
- **"Close" is not a criterion.** Nothing is written down, so you cannot name what failed. An extension needs "new date plus the failed criterion written down."
- **Without criteria, the loudest voice decides.** Today that is leadership, and in practice Ridgeway.
- **Likely honest outcome:** one extension of 3 months or less, with a named failed criterion. The probable one is "no production traffic on the final shape under a signed exception." See point 4.

## 2. "Auto-expire every beta flag on the new end date"

This is the wrong behavior. An expiry that disables access cuts all 12 accounts on one date.

- Ridgeway runs production on this endpoint. It would hit a silent 404 with no outcome decided.
- Make the expiry alert the program owner on the exit date and never disable access. An unresolved beta then shows up as an alert, not as an outage.
- Only the step-9 outcome (GA, extension or kill) changes access. Never remove access by deleting the flag.
- Check that flags are keyed per account or org, not per user.

## 3. "12 signups = demand validation"

Signups measure reach. Only activation and production use measure demand.

- **What you can claim:** 12 enrolled, 3 activated (25%), 1 production-shaped (Ridgeway).
- **The 9 silent accounts:** after 5 months with no calls, they are evaluating, not building.
- **Concentration:** in a preview of 4 or more accounts, no partner should exceed about a third of traffic. Check Ridgeway's share. If it is most of the traffic, your demand evidence is one customer.
- **If leadership wants a demand slide**, use "3 of 12 activated, 1 in production," plus whether the 3 will pay at GA. Ask them. An answer of "can't say" means their usage counts as reach, not demand.
- **Check the 12 against the entry gate** (retroactively): evidence of the problem, a planned integration, a named technical owner, signed pre-GA terms, intent to pay. Any account failing the first three is a free-rider signal.

## 4. "Rename `matches` to `segments` the week before the review"

It is a breaking change, and it is backwards in two ways.

- **No freeze, no final-shape evidence.** The skill requires a contract freeze at least one partner release cycle before the review, so the review judges a frozen shape. A rename the week before means nobody, Ridgeway included, runs on the final shape at the review. The GA criterion "production traffic on the final shape" cannot be met. It also needs a design re-review because the surface changed.
- **Ridgeway has no notice.** Breaking changes are allowed in private preview, but only with direct notice to every technical owner before they ship. Notice length scales with production use, and Ridgeway is in production. The rescue rule is to grandfather production callers: nothing they call changes until the surface has a decision.

Decision rule: ask Ridgeway's release cycle.
- **If the freeze date (review minus one cycle) is still ahead:** ship the rename now, with written notice to all 12 technical owners and a changelog entry. Then expect the review to produce the extension from point 1.
- **If the freeze date has passed:** the rename waits. Review the current shape, and ship the rename inside the extension or in the next preview version.

## Ridgeway

1. Call their technical owner this week, before any public notice or relabel.
2. Offer a signed production exception for this surface. It names the account, the surface, and the notice they get.
3. Ask whether payloads carry driver or vehicle location. For a fleet customer that is likely personal data. "Do not send personal data" would make the beta unusable. They then need a per-account data addendum that legal signs, extending named DPA terms to the preview.
4. Check Ridgeway's MSA or DPA for "all services" coverage. Pre-GA terms must say they override it, and counsel signs the wording.
5. Record the production exception in the enrollment record. That record is also your GA evidence.

If the outcome were a kill, Ridgeway's production use would force notice of months, not weeks.

## Revised proposal for leadership

Do these in order. Estimates are for a PM with legal on call.

1. **Retroactive stage contract** (about half a day, then counsel review). Fill all 11 rows for private preview: Access, Availability, Support, Breaking changes, Removal, Production use, Pricing, Data and compliance, Limits, Marking, Discontinuation. Include a note that these terms override any MSA or DPA that promises coverage on "all services." Ask whether the other 11 accounts signed pre-GA terms. Those who did not get the contract by reference.
2. **Exit criteria, signed by leadership before the review**, ideally before anyone re-reads the current numbers. Draft:
   - **GA when all hold:**
     - at least N accounts activated (you set N; today it is 3)
     - at least one account in production on the final shape under a signed exception
     - no open blocker
     - design re-review passed after the rename
     - support, docs and SDKs ready
     - GA pricing set
     - internal SLO met for a sustained window
   - **Kill when any holds:**
     - activation is below the floor at the review date
     - the problem statement is disproved
     - cost to serve exceeds what GA pricing can carry
     - a better route is found
   - **Extension:** one, at most 3 months, with the failed criterion written down.
   - **Freeze date:** at least one partner release cycle before the review.
3. **Ridgeway call and exception** (per above), then decide the rename per the rule in point 4.
4. **Contact the 9 inactive accounts** this week. Ask for their activation event and what they would pay at GA. Re-qualify or release the seats.
5. **Review in 4 weeks** (about 2026-11-20): decide GA, extension or kill against the signed criteria. Tell enrolled accounts first, then the waitlist, then the public changelog.

Pitch for leadership: "We found the rules weren't written down. We are fixing that before we judge, and we expect a short extension, not a rubber stamp."

## Open questions

These change the advice. Answer them in this order:
1. Does Ridgeway's payload carry personal data (driver or vehicle location)?
2. What is Ridgeway's release cycle, and what share of beta traffic is theirs?
3. Did the other 11 accounts sign any pre-GA terms?
4. Who owns the program by name, and is the beta on a separate version, path or header?
5. What is the GA target date? It sets the freeze and the review.

I checked none of this against your systems. Every number above comes from your message.

**Next:** call Ridgeway's technical owner this week and ask question 2 on that call.