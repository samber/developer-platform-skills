# App directory review depth for Corvid Systems

## Verdict

**Do not run a Salesforce-style multi-week manual review.** Run a light review sized to what an app can touch. An app that can only read a public catalog and published carrier-rate metadata needs the lightest tier in the skill's model, which is functional review plus automated checks. One engineer at 4 hours a week can staff that. ℹ️

## Why the CTO's analogy doesn't hold

- **Review rigor tracks data sensitivity, not the buyer's market.** Salesforce's gate exists because its apps reach business records. Google makes a third-party CASA audit mandatory only for restricted scopes (Gmail, Drive). Slack, Chrome and Shopify use lighter functional review plus post-publication scanning.
- **Your maximum grant is public data, read-only.** There are no orders, shipments, personal data or writes, so a deep gate has almost nothing to protect.
- **Salesforce's cost is far beyond your budget.** Its published pipeline is 1-2 weeks of verification plus 3-4 weeks of manual Product Security testing, a $999 fee, mandatory SAST and DAST, and about 50% first-pass failures (Salesforce's own estimate, relayed by Aquiva Labs). Your 4 hours a week is roughly 16 hours a month.
- **A heavy gate on a public-data directory would also repel partners.** It would produce multi-week queues for apps that can't hurt anyone.

## What procurement actually needs

Procurement teams want to see a written, enforced policy. A multi-week manual audit is not the same thing. The credible signals are:

1. A published review policy.
2. An objective rule for when an app moves up a tier.
3. A visible way to remove an app.

You can ship all three at this effort level. The tier-escalation rule is what makes a light tier believable, because buyers can see the bar rises when risk does.

## Recommended design

This is an interview-lite design. I inferred question 2 as (a), public or metadata only, and question 10 as 4 hours a week. Verify the assumptions below before you finalize.

### 1. Pipeline shape: functional-only review, with a trigger to escalate

- The skill calls functional-only review "the right depth for a metadata-only tier."
- Automated pre-screen first, then human triage. Auto-ticket only critical and high findings, and send humans only judgment calls.
- Give developers your checklist as a self-check tool before they submit. This cuts first-pass failures.
- Estimated reviewer cost is 1-2 hours per new app (my estimate, not a benchmark). At 16 hours a month, that supports a handful of new apps a month plus update triage. If volume outgrows it, promote to a staged gate with a fast path (Atlassian's shape).

### 2. Admission checks

- **Scope minimization:** the app requests only what it uses. With read-only public endpoints this is nearly trivial, so name each scope and check it.
- **Data-access review:** where the data goes after the call (endpoints, subprocessors, retention).
  - Secrets must never appear in source repos, URLs or logs.
  - Check that the app doesn't re-expose or resell the data in ways your terms prohibit.
- **Manifest inspection, functional test and listing accuracy.**
- **Rate-limit and abuse behavior.** With no sensitive data, availability and terms abuse are your real risks.

### 3. Escalation trigger

Write this so a developer can self-assess it before submitting.

- **Tier up** for any app that requests write access, customer data of any kind (orders, shipments, personal data), or any scope beyond public catalog and rate metadata.
- **At that point the light tier no longer applies.** The review shape and depth get redesigned for the new data grant. That is when a deeper gate is justified.

### 4. Re-review on update: objective fast path

Full re-review fires only on:

- New scopes.
- New external endpoints.
- A change in data handling.
- A payment-model change.
- A new app type.

Routine updates clear instantly, with automated scanning on each release. Don't use a subjective trigger like "substantial changes."

### 5. Publish-channel hardening

- **Default controls:** phishing-resistant (FIDO) 2FA on partner accounts, plus short-lived scoped API credentials.
- **Propagation hold:** this applies only if updates auto-propagate into customer tenants.
  - If apps are partner-hosted API clients and Corvid ships no partner code to customers, there is no auto-propagation channel. The 24-48 hour hold then has little to protect.
  - If apps install into customer environments, add the hold.
- **Why this order:** every documented 2024-2026 incident rode a compromised publisher account or an unguarded update channel, not a malicious first submission.

### 6. Appeal path

- Offer a defined, human-reviewed appeal with a stated turnaround, distinct from resubmission.
- The reviewer must be someone who didn't make the original decision.
- Every rejection cites the specific policy violated.
- If you serve EU users, add a mediation path (P2B rules). Check this.

### 7. Revocation ladder

With a read-only public API, revoking the API credential is a near-instant kill switch. Write each rung with an owner, a notice period and the evidence that fires it:

1. Finding raised.
2. Remediation SLA by severity.
3. Listing hidden.
4. New installs suspended.
5. API credentials revoked.
6. Delisting, with customer notice.

Also require a security contact per partner, and give chronic bad-faith partners graduated partner-level consequences.

## Staffing at 4 hours a week

| Work | Rough share |
|---|---|
| New-app reviews | ~2 h/week |
| Automated-scan triage | ~1 h/week |
| Appeals, revocation, policy upkeep | ~1 h/week |

These shares are my estimate, not sourced figures. Build the automation and the developer self-check first. They carry the load as volume grows.

## Gates to check before you publish this

1. Every tier has an objective escalation trigger a developer can self-assess. ✅ (the tier-up rule above)
2. "Minor update" is defined objectively. ✅
3. Every enforcement rung names an owner, notice period and firing evidence. ⚠️ You must fill in owners and notice periods.
4. The publish channel has at least the default controls, plus the hold if updates auto-propagate. ⚠️ This depends on question 4 below.

## Questions to answer before finalizing

1. **Is the "public" data truly public?** Confirm carrier-rate metadata has no contract-confidential or commercially sensitive fields. If it does, the data tier changes.
2. **How do apps reach customers?** If a partner app is installed into customer tenants or can act with customer credentials, the real maximum grant is higher than this API suggests. In that case the light tier doesn't apply.
3. **Do you have EU users?** This decides the appeal rung.
4. **Do updates auto-propagate?** This decides the propagation hold.
5. **Volume forecast:** new apps and updates per month, now and in 12 months.
6. **Deadline:** is there a hard launch date? A hard date favors rungs that ship as policy text.

## Answer for the CTO

> Our apps can read only public catalog and carrier-rate metadata. Salesforce's multi-week review protects apps that reach business records, and we have none to protect. We'll publish a tiered policy: light review now, and a hard gate that triggers the moment any app asks for write access or customer data. That is the signal procurement reads, and it fits one engineer at 4 hours a week.

If the answer to question 2 turns out to be "apps can reach customer data," this verdict reverses and you should redesign the shape and depth.