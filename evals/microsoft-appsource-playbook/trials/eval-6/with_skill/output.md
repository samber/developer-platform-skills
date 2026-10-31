**Next action (Mon 2026-11-02, about 30 min):** create the Partner Center account in the AI Cloud Partner Program and start tax profile validation. It takes up to 48 h†, and the payout profile waits on it.

† means a Microsoft figure. Verify it in Partner Center before you quote it.

## 1. What changed since the 2024 notes

| 2024 step | Status now | Replacement |
|---|---|---|
| 1. ISV Success | Absorbed into Frontier Accelerate for Marketplace | Enroll in Frontier Accelerate (no-cost tier exists†). Azure credits do not gate your date. |
| 2. Marketplace Rewards | Absorbed into Frontier Accelerate | No separate signup. Same enrollment as step 1. |
| 3. Qualified Referral Program | Retired | Register your own opportunities in Partner Center referrals, only after you are co-sell ready. |
| 4. List on AppSource | AppSource and Azure Marketplace are now one Microsoft Marketplace | List a transactable SaaS offer. This is now the critical path, so it moves to step 1. |

## 2. Assumptions (flag any that are wrong)

1. **Microsoft 365 footprint:** no Teams app, add-in or Copilot agent. A Teams app would force per-user pricing and add a separate 3-6 week† validation. That cannot fit before end of January.
2. **Hosting:** primarily Azure, and Brightmoor accepts Entra SSO. This keeps the offer eligible.
3. **Pricing:** enterprise contracts sold as private offers. The pricing model is not decided yet.
4. **MACC:** unknown whether your buyers hold Azure commitments (MACC).
5. **Stage:** no Partner Center account.
6. **Capacity:** about 4-5 engineering weeks are available before mid-December.
7. **Owner:** you own Microsoft seller outreach and collateral.

## 3. Path

**Transact SaaS offer plus private offers.** This is the default rung. Only transact offers unlock private offers, MACC and IP co-sell. Contact me and listing-only offers do none of these.

- **Answer 5 (hard date):** promotes private offers. They are the only route to a deal by January.
- **Answer 2 (Azure):** keeps Azure IP co-sell as a later rung.
- **Answer 3 (MACC buyers unknown):** keeps IP co-sell out of this quarter.
- **Answer 1 (no Teams app):** keeps the Teams app off the plan.

**Realism check.** Co-sell ready is visibility, not pipeline. Practitioners report months before any seller engagement. Microsoft sellers will not produce your first transaction by January 31. Your first transaction is a private offer to a buyer you already know.

## 4. Locked-choice register

These cannot change after the offer or plan publishes. Decide by **Fri 2026-11-13**.

- **Pricing model (flat rate or per user, same for all plans):** `unassigned`. Recommend flat rate with a usage overage. Metering exists only on flat-rate plans, and per user is needed only for a Teams link.
- **Plan ID:** `unassigned`.
- **Per-user seat min/max:** `unassigned`, and only applies if you choose per user.
- **Metered dimension IDs and values:** `unassigned`.
- **Public plan or private plan:** `unassigned`. A public plan cannot go private later.
- **Standard contract or your own terms:** `unassigned`. Ask Legal.

Build transact from day one. Microsoft pages disagree on whether a listing-only offer can switch to transact.

## 5. Submission plan

**SaaS offer**
1. Register a multitenant Entra app that accepts work and personal accounts. Request only `User.Read` at activation.
2. Enter the same tenant ID and app ID in Technical configuration as you use to mint API tokens. A mismatch fails `resolve`.
3. Build the landing page. It must always be up, have no `#` in the URL, show no secrets and offer no downloads. Resolve the purchase token (valid 24 h), then activate.
4. Use Fulfillment API v2 only. Validate every webhook through the Get Operation API. Answer plan and seat changes within 10 s.
5. Send metering hourly per resource and dimension. Events older than 24 h are rejected.
6. Disclose the SSO admin consent in the offer description.
7. Write the Notes for certification: test accounts with no MFA and no developer interaction, plus purchase-to-activation steps. Missing notes are a top failure.
8. Test on a separate DEV offer at a nominal price. **Never press Go live on it.** Test purchases are invoiced and refunded only if cancelled within 72 h†.

**Teams validation and Publisher Attestation:** not applicable under assumption 1.

**First private offer:** if the first buyer is an existing customer (a renewal, a migrated contract or an upsell), tick the renewal attestation when you create it. The fee halves† for the whole term. You cannot add it after creation.

## 6. Co-sell plan

- **Status target this quarter:** co-sell ready, not IP co-sell eligible.
- **Threshold gap:** IP co-sell needs $100,000 Azure consumed revenue (trailing 12 months) or $100,000 billed through the offer†. Brightmoor's figure is unknown. Pull it from your Azure bill.
- **Other IP co-sell requirements:** solution type IP, technical validation, a reference architecture diagram, and "Sell through Microsoft".
- **Collateral owner:** you.
- **Collateral list:**
  - Business profile and PartnerID.
  - A sales contact per geography.
  - A one-pager on the Microsoft template.
  - A pitch deck on the Microsoft template.
  - A reference architecture diagram showing Brightmoor deployed on named Azure services.
- **First seller accounts:** list your customers that are Microsoft-managed accounts and map each to a Microsoft account executive. Unmanaged accounts never qualify for IP co-sell registration.
- **After eligibility:** check the offer shows MACC "Enrolled" within about a week†.

## 7. Timeline (today 2026-10-31, target 2027-01-31, one failed cycle included)

**Nov 2-13: setup and decisions**
- Create the Partner Center account. Start tax validation, then the payout profile.
- Enroll in Frontier Accelerate.
- Register the Entra app.
- Lock the register in section 4 (Nov 13).
- **Name the first buyer** and ask whether they will procure through Marketplace. Their procurement is the longest unknown on this plan.

**Nov 16 - Dec 11: build**
- Engineering builds the landing page, Fulfillment API v2, webhook and SSO, and tests on the DEV offer.
- You draft the co-sell collateral and the architecture diagram in parallel.

**Dec 14-18: first submission**
- Publish the real offer to a preview audience.
- Submit for certification with full notes.

**Dec 21 - Jan 8: failed cycle, fix, resubmit**
- Assume the first review returns defects.
- Holiday slowdown (Dec 19 - Jan 2) is a risk.
- SaaS certification duration is not in my source. Ask Partner Center support for the current figure.

**Jan 11-15: go live**
- Press Go live on the real offer.
- Send the first private offer.

**Jan 18-29: buyer acceptance**
- The first transaction happens when the buyer accepts the private offer.
- This leaves 2 weeks of buffer.

**Late January: co-sell solution**
- Submit the co-sell solution. Expect a few weeks of review, so it lands in February.

**Slip risks, ranked:**
1. Buyer procurement.
2. A second failed certification cycle.
3. The pricing-model decision slipping past Nov 13.

## 8. Questions to confirm (they can change the plan)

1. Does Brightmoor plan a Teams app or Office add-in this year? If yes, decide that before the first publish.
2. Who is the first buyer, and do they hold a MACC?
3. How many engineering weeks, and who owns the Entra app?
4. What is the Azure consumed revenue over the last 12 months?
5. Is the pricing flat rate or per user?

**Next:** do the account creation above, then reply with answers to 1 and 2.