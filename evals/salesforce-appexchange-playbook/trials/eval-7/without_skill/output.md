# Brightpath: channel, renewals, card payments, and prompt-template re-review

I answered this from general knowledge of the Salesforce ISV program. I didn't check live Salesforce documentation, and I didn't use anything under `skill-wip/`. Confirm the items marked **verify** with your Partner Account Manager (PAM) before committing.

## Bottom line

1. Don't make the Channel Order App (COA) the default route for new customers. Card payment and auto-renew both fit better on your own paper. Decide the route per deal.
2. Auto-renew is feasible, but it needs contract language, a renewal-notice process, and a License Management App (LMA) step so seats don't lapse.
3. Card payment works for small deals only. Offer ACH or wire as the default for larger ones, and price card fees in.
4. The CTO should treat the prompt templates and agent actions as in scope for re-review. Run an AI-specific security pass before it.

## 1. Channel: COA versus your own paper

**What COA is for (verify).** COA is for deals that go through Salesforce's channel. Salesforce's order and billing path applies, and you report the order to Salesforce. It isn't a generic place to file every deal.

**What this means for the three asks:**
- **Card payment.** If Salesforce or the channel bills the customer, you probably can't take their card. Card payment is a feature of your own billing, or of AppExchange Checkout if you enable it. **Verify** what Checkout supports for managed-package subscriptions.
- **Auto-renew.** Salesforce-paper order forms follow Salesforce's order and renewal mechanics, not yours. You can't promise auto-renew terms that Salesforce's paper doesn't carry.
- **Revenue share.** Fee treatment differs between channel deals and direct deals. Finance should model net revenue per route before sales picks one. **Verify** the current rates in your ISV agreement.

**Recommended rule:**
- **Salesforce-sourced or Salesforce-billed deals:** keep using COA.
- **Direct deals where the customer wants card or auto-renew:** use your own order form and billing. Report as your partner agreement requires.
- **Ask your PAM** whether one customer can mix routes (for example, a COA first term and direct renewals). Don't assume it can.

## 2. Auto-renew everything

**Contract changes:**
- Add a clear renewal clause: term length, price on renewal, a cap on uplift (for example, a fixed percentage), and the cancellation window.
- Send a renewal notice before the cancellation deadline, typically 30–60 days ahead. Some states require notice for certain auto-renewing service contracts, and New York's rule is the well-known one. B2B coverage is uncertain, so ask counsel. The notice is cheap and removes the risk either way.
- Don't use "everything" literally. Exclude pilots, free trials, and any customer on Salesforce paper.

**Operations changes:**
- An LMA license has an expiration date. A contract that auto-renews does nothing to the license unless someone extends it. Add a renewal job: at the renewal date, extend the license expiry and update the seat count.
- Define what happens to seat changes at renewal (true-up and true-down) so billing and LMA stay equal.
- Add a dunning flow for failed renewal charges, with a grace period before you set the license to expire.

**Finance changes:**
- Recognise revenue per the contract term, and book the renewal as a new invoice cycle.
- Decide whether auto-renew uses the same price ($45 per seat per month) or a list price at renewal.

## 3. Card payments

- **Fees.** Card processing is roughly 3% before any B2B surcharge. On a 100-seat deal that is $54,000 per year, which is about $1,600 per year in fees. Consider offering ACH or wire as the default, with card for small teams.
- **Surcharging.** US surcharge rules vary by state and by card network. Ask counsel before adding one.
- **Large deals.** Large card charges also attract more chargebacks and fraud review. Cap card payment at a deal size finance is comfortable with, or require a purchase order.
- **Sales tax.** Cloud software is taxed in some US states and cities, not others. Chicago applies its lease transaction tax to cloud software, and that matters since you are based there. Confirm your nexus and collection obligations by state before you invoice directly. Salesforce-billed deals may shift who collects, which is another reason the route affects cost.
- **Provider.** Use a processor that supports recurring billing and card updaters, so expired cards don't cause involuntary churn at auto-renew.

## 4. CTO question: do the prompt templates need anything before re-review?

**Short answer:** yes. Don't rely on the March pass alone. Treat the prompt templates and Agentforce actions as the highest-risk surface.

**Check first with your PAM (verify):**
- The trigger and timing of the periodic re-review. Reviews also apply when you ship versions with material new functionality. Any template or action added since March could need its own review.
- Whether Salesforce has published AI-specific review criteria for Agentforce components. If so, map each one to your package before submitting.

**Run a pre-review pass on these:**
1. **Prompt injection.** Case text is untrusted input. Test whether a malicious case comment can steer the summary or trigger an action. Keep instructions and case data clearly separated in each template, and tell the model to treat case content as data.
2. **Data access.** Confirm that merge fields and grounding respect field-level security and sharing for the running user. A summary must never expose a field the user can't read.
3. **Agent actions.** Each Apex or Flow action should enforce user mode (`WITH USER_MODE` or `with sharing`), validate inputs, and follow least privilege. Check for dynamic SOQL built from model output. Remove any action with write or send side effects, or require confirmation.
4. **Output handling.** Don't render model output as HTML or pass it to further actions unescaped.
5. **Trust layer.** Confirm the templates run through the Einstein Trust Layer with data masking and zero-retention settings as configured. Document which of your data categories the templates send to a model.
6. **Disclosure.** Make sure your listing, security questionnaire, and privacy documentation describe the AI features accurately. A mismatch between what you said in March and what ships now is a common reason for follow-up.
7. **Scan evidence.** Rerun the standard scanner (Code Analyzer or Checkmarx, whichever applies), and fix all findings. Keep the reports for submission.
8. **Regression record.** Keep a short test log of injection attempts and their results, with dates and package version.

## Decisions for you

1. Which route is the default for new direct customers: your paper, COA, or a per-deal rule?
2. Is the renewal price fixed, capped, or at list?
3. What is the maximum deal size for card payment?
4. Who owns the LMA renewal job?

If you answer these, I can draft the renewal clause outline and the pre-review checklist as documents.