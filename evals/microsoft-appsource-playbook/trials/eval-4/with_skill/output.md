# Corvane on Microsoft Marketplace: what to tell the CEO, and what to do next

This follows the microsoft-appsource-playbook skill and its submission-packet reference. I couldn't see Corvane's Partner Center account, so the assumptions below are flagged and need checking. Figures marked † come from the playbook: confirm them in Partner Center before quoting them to anyone.

## What to tell the CEO

**Don't pull the listing. Zero referrals doesn't show the channel failed.**

1. **The channel already paid.** About $180k has billed through Microsoft Marketplace, mostly from two enterprise deals. That is the thing Marketplace does best: enterprise procurement through Microsoft billing, for a fee of about 3%†.
2. **"Co-sell ready" doesn't generate referrals.** It lists the solution in Microsoft's internal seller catalogs and nothing more. Microsoft calls it a starting line, and practitioners report months before any seller engages. Microsoft sellers work to quota, so they won't pick Corvane up unprompted. Zero referrals after about 3.5 months is the normal state of a passive co-sell listing.
3. **Pulling the listing is the costly move, and it is hard to undo.** Many choices lock once an offer publishes: pricing model, plan IDs, contract terms. If those two customers hold Azure commitments (MACC), buying through Marketplace may be why they could buy at all. Delisting could put renewals at risk and cost Corvane the best procurement route it has. Check what happens to existing subscriptions with Partner Center support before anyone proposes it.
4. **Co-sell is a separate bet from the listing.** If the CEO wants to judge Microsoft's referral value, the fair test is a deliberate co-sell push, with an owner and a deadline, not three months of waiting. If that push fails, scale back the co-sell effort and keep the listing, because the listing is where the revenue is.

**Suggested one-liner:** "Marketplace has billed $180k with no sales effort from Microsoft. Referrals never come on their own. Give me 90 days with an owner, a target account list and a MACC pitch, and we judge co-sell on that. We keep the listing either way."

## Assumptions to confirm

I filled these in where the request was silent:

1. **Hosting:** Corvane runs primarily on Azure, and the Azure-hosted compute or data plane grows fastest with usage. That keeps Azure IP co-sell open.
2. **Offer:** It is a transactable SaaS offer, since $180k was billed through it. No Teams app, so Teams validation and attestation don't apply.
3. **Private offers:** I don't know whether the two enterprise deals closed as private offers. If not, that is a gap.
4. **MACC:** I don't know whether those two buyers hold Azure commitments.
5. **Frontier Accelerate:** I don't know whether Corvane is enrolled in Frontier Accelerate for Marketplace. The playbook's FAQ source treats enrollment as a prerequisite for any co-sell listing, and a no-cost tier exists.
6. **Ownership:** I don't know who owns Microsoft seller outreach. I assume nobody does. That is the likeliest cause of the silence.

## Recommended path

The default rung is transact SaaS with private offers, which Corvane already has. The next rung is **Azure IP co-sell eligible**, because the answers point to Azure hosting and likely MACC buyers. It takes the least engineering for the most pipeline, and it moves Microsoft sellers from indifferent to incentivized.

Corvane may already be past the threshold. $180k billed through the offer exceeds the $100k† bar. The full requirements are:
- Solution type IP.
- Primarily on Azure, with technical validation.
- A reference architecture diagram.
- "Sell through Microsoft" enabled.
- $100k Azure consumed revenue (trailing 12 months) or $100k billed through the offer†.

Getting there is probably a matter of paperwork and a request, not new engineering.

If any of this is untrue, the path changes:
- **If Corvane is not primarily on Azure,** drop IP co-sell. Stay at co-sell ready and keep the listing as a procurement channel only.
- **If there is no Microsoft integration,** the playbook flags the offer itself as at risk. The listing rules say a non-Azure SaaS offer must integrate with or extend a Microsoft product. Confirm Corvane's position.

## Locked-choice register

These are fixed once published. The owner and decision date for each are `unassigned`, so fill them in before touching the offer:

| Choice | Owner | Decision date |
| --- | --- | --- |
| Pricing model (flat rate or per user) | unassigned | unassigned |
| Plan IDs | unassigned | unassigned |
| Seat min and max | unassigned | unassigned |
| Metered dimensions | unassigned | unassigned |
| Standard contract or custom terms | unassigned | unassigned |
| Public plan going private | unassigned | unassigned |

Open question for you: who at Corvane owns these decisions?

## Co-sell plan

**Status targeted:** Azure IP co-sell eligible, with MACC showing "Enrolled" on the offer.

**Threshold gap:** possibly none on revenue. Verify the $100k† billed-through-offer figure in Partner Center, and check whether the architecture diagram and "Sell through Microsoft" are in place.

**Steps:**
1. **Check the co-sell solution** in Partner Center under Co-sell > Solutions. Confirm the business profile, PartnerID, a sales contact per geography, one-pager, pitch deck, and a reference architecture diagram showing Corvane's IP deployed on, and driving consumption of, named Azure services.
2. **Confirm Frontier Accelerate enrollment.**
3. **Request IP co-sell eligibility.** Review takes a few weeks.
4. **Check MACC enrollment** shows "Enrolled" on the offer within about a week† of eligibility.
5. **Register your own opportunities** in Partner Center referrals, against Microsoft-managed accounts. Unmanaged accounts never qualify for IP co-sell registration.
6. **Map target accounts to Microsoft account executives.** Start with Corvane's two existing buyers: ask who their Microsoft AE is and whether they hold MACC. Lead with MACC drawdown, because for a buyer with a commitment, Corvane purchases count toward it. That gives an AE a reason to care.
7. **Appoint one owner.** Without a named person, none of this happens.

**First seller accounts:** the two current enterprise customers, plus any Azure-heavy prospects already in your pipeline.

## Private offers

- **Run every deal as a private offer.** Enterprise buyers procure that way.
- **Use the renewal attestation** when the two enterprise deals renew, or on an upsell to an existing customer. It halves the fee† for the whole term. It can't be added after creation, and an offer created before October 2024 never qualifies. In that case the customer must stop auto-renew and accept a new attested offer.
- **Use a multiparty private offer** if a reseller owns the relationship. CSP private offers never count toward MACC.

## Timeline (forward from 2026-10-31)

| When | Action |
| --- | --- |
| Week 1 | Reply to the CEO. Name the owner. Verify enrollment, billed-through-offer total, architecture diagram and "Sell through Microsoft". Ask the two customers for their Microsoft AEs and MACC status. |
| Weeks 2-3 | Fill any collateral gap and submit for IP co-sell eligibility. |
| Weeks 3-6 | Review runs. Register the first opportunities and start AE conversations in parallel, since the AE outreach doesn't have to wait for approval. |
| About week 7 | Check MACC shows "Enrolled". Pitch drawdown to target accounts. |
| Day 90 (late January) | Judge co-sell on a count of Microsoft-engaged opportunities and a pipeline figure, then decide. |

I didn't add a failed-validation cycle, because this path involves collateral review, not Teams validation. Add a week or two of slack if the architecture diagram is rejected.

## The one question that could change this

Did the two enterprise deals close through private offers, and do those buyers hold MACC? If yes to both, your case is strong: Corvane is already a way for them to spend a commitment they must spend anyway. If no to both, the listing is mostly a billing convenience. It is still worth keeping at a 3%† fee, but the co-sell push gets much weaker. Tell me the answer and I'll adjust the plan.