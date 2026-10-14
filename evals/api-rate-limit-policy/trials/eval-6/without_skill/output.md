# Limit-increase process, Vantiq Cloud

I made this up without seeing your real Pro limit, costs, or tooling. The numbers marked **[confirm]** are placeholders for you to check.

## Three changes to the sales plan

1. ⚠️ **Attach limits to the account, not the admin's user.**
   - Admins leave, change roles, or sit behind SSO. A limit tied to one user vanishes or lands on the wrong person.
   - It also hides the entitlement from finance, support, and the contract.
   - Store the limit as a quota record on the organization/tenant, linked to a contract or order form. Admins can view it but don't own it.
2. ⚠️ **Don't leave the decision to the AE's discretion alone.**
   - The AE is paid on closing, so they shouldn't be the only gate on a cost to the platform.
   - Give AEs a bounded authority and require Finance and Engineering sign-off beyond it (see "Approval tiers").
3. ❌ **Enterprise must not imply an automatic increase. Fix the prospect's assumption now.**
   - Say plainly what Enterprise includes at purchase and what needs a separate approval.
   - The pricing row should state the included baseline and mark anything higher as a quote.
   - Send the correction to the confused prospect in writing before signature. That avoids a dispute at go-live.

## Pricing page wording

Publish a baseline, not a promise.

| Plan | Requests/day |
|---|---|
| Pro | [Pro limit, as published today] |
| Enterprise | **Starting at 500,000.** Higher limits available by contract. [Contact sales] |

Add a footnote: "Limits are set per organization and confirmed in your order form. Plan upgrades do not change limits until the order form is signed."

- **[confirm]** Check that 500,000 is the baseline you want to commit to publicly. Two prospects asked for ~10x Pro, so it should match your capacity and unit cost. Publishing it makes it hard to lower later.
- **Alternative:** if 500,000 is a ceiling you'd rarely grant, publish "Custom" and keep the number internal.

## Process

### 1. Request intake
- Every increase starts as one request in one place (CRM deal field plus a ticket). Slack or email alone doesn't count.
- Required fields:
  - organization ID
  - requested limit and duration
  - business reason and workload shape (steady or bursty, peak rate)
  - contract status (pre-sale or existing customer)
  - AE name

### 2. Approval tiers
Define the tiers as multiples of the plan's included baseline (B). Pre-signature requests count against the plan the customer is buying.

| Request | Who approves | SLA [confirm] |
|---|---|---|
| ≤ 2× B | AE alone, inside a pre-priced rate card | same day |
| > 2× B up to 10× B | AE + Finance (price/margin) + Engineering (capacity) | 3 business days |
| > 10× B, or sustained above 10× B | Above, plus VP-level sign-off | 5 business days |

- **Rate card:** pre-price each band so an AE can quote without inventing terms. Increases are paid, and a discount needs Finance approval.
- **Capacity check (Engineering):** confirm the platform can serve the load, and check the noisy-neighbour risk to other tenants. Decide whether the customer needs isolated capacity.
- **Written decisions only:** no verbal promises. A promise made before the approval is complete is not binding on Vantiq.

### 3. Commercial terms in the order form
Every granted increase gets these terms in the order form:
- the exact limit and the unit (requests/day, window, timezone)
- start and end dates, with a review at renewal (limits don't carry over silently)
- price, or a commit plus overage rate
- behavior at the limit: throttle, block, or bill overage. State which.
- a burst allowance, if any

### 4. Provisioning
- Support or Engineering applies the limit **by writing the quota record** on the org. The AE can't change it.
- Each change records who requested it, who approved it, the order-form reference, and the timestamp.
- Apply the increase only after the signed order form arrives, never on a verbal OK or a pending signature. The exception is a time-boxed trial.
- Trials: allowed with an expiry date (e.g., 14 days [confirm]) and a hard cap. The limit auto-reverts when the trial ends.

### 5. Monitoring and review
- Alert the account owner and the customer at 80% and 100% of the limit.
- Send a monthly report to the AE of accounts above 80%. That's your upsell list.
- Review all custom limits at renewal. Lapsed or unused increases revert to the baseline.
- Track: time to approve, share of requests approved, margin on increased accounts, incidents caused by increased tenants.

### 6. Customer-facing view
- Customer admins can see their org's current limit, usage, and expiry in the dashboard. They can't change it.
- The "request an increase" button routes to the AE and creates the intake record.

## Roles
- **AE:** gathers requirements, quotes within the rate card, files the request.
- **Finance:** approves price and margin above the AE tier.
- **Engineering/SRE:** capacity check and provisioning.
- **Support:** applies approved quota records and handles customer questions.
- **Process owner [pick one person]:** keeps the rate card and tier thresholds current.

## Next steps
1. Confirm the Pro limit, the 500,000 figure, and the rate-card prices **[confirm]**.
2. Send the written correction to the prospect who assumed Enterprise auto-raises limits.
3. Create the org-level quota record and the intake form.
4. Update the pricing page once Finance and Engineering sign off.