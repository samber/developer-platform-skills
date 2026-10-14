# Sanity check: PCI "90-day rotation" and the SOC 2 policy plan

**Verdict:** ❌ The PCI claim is wrong as stated. ❌ The SOC 2 plan fails as written. The 90-day cadence itself can be fine, and the rotation tool is a later purchase.

## 1. "PCI requires rotating every key every 90 days"

**What PCI says.** PCI-DSS 4.0/4.0.1 Requirement 8.6.3 has been mandatory since April 1, 2025. It sets no fixed interval. It requires three things:

- Credentials are changed periodically, at a frequency you define in a documented **targeted risk analysis** (Requirement 12.3.1).
- Credentials are changed immediately on suspicion or confirmation of compromise, whatever the schedule says.
- Credential complexity matches the rotation frequency. A 120+ bit random key meets this easily.

**Caveat on my source.** The skill's reference quotes 8.6.3 from eight independent QSA and compliance sources, not from PCI SSC's own PDF. Before you cite it in a contract or to an auditor, download the PDF from PCI SSC and quote the literal text.

**Why 90 days is still probably fine.** The common practitioner convention for payment and highest-blast-radius keys is 30 to 90 days, so your hire's number is defensible. What's missing is the justification. An auditor will ask for the risk analysis document, not for a "90 days" claim. Reframe it this way:

- Write the targeted risk analysis: exposure, how likely and how bad a leak is, and why the interval you picked fits. A 90-day result can come out of it.
- Add the compromise path as a separate, unconditional rule: **revoke with zero grace** and accept the downtime.
- Set cadence by key class. Don't use one number for everything:

| Key class | Starting point |
| --- | --- |
| Payment and production keys | 30 to 90 days |
| Third-party integration keys | about 90 days |
| Service-to-service credentials | about 30 days, or short-TTL dynamic secrets |
| CI and agent workloads | workload identity, with no stored key to rotate |

**Whose keys are in scope?** "Our API" could mean two things:

- **Keys Fintar issues to its customers.** You can't force-rotate these without breaking their integrations. Rotation becomes a feature you ship: expiry warnings and a self-service roll, with the cadence enforced on your side by mandatory expiry.
- **Keys Fintar holds internally**, such as processor keys, internal service credentials and CI. You control these fully.

Settle which one the hire means before anything else.

## 2. The rotation tool budget

⚠️ Don't buy yet. Check three things first, because a tool built on top of them is useless without them. Without overlap, rotating on a schedule just schedules outages.

1. **Dual-key overlap.** Both the old and new key must validate at once. That needs an `expires_at` column and no unique-active-key constraint.
2. **Last-used telemetry per key.** This is how you know the old key has hit zero traffic. Never delete a key before it does.
3. **One atomic "roll" operation.** It creates the new key and schedules the old key's expiry in one call. Never ship it as two manual steps.

If you already have these, an off-the-shelf tool may add little. Spend the money on evidence instead:

- Audit logs of every create, use, rotate and revoke, with who, when and why.
- Expiry warnings and forced-rotation reminders.
- KMS custody, if you store keys in a retrievable way.
- Service accounts and org-owned keys, so offboarding works.

**Also check:** are keys stored hashed (SHA-256 with a constant-time compare), and are production integrations running on personal keys? Those are audit findings regardless of cadence.

## 3. "Write the key-management policy the week before the SOC 2 auditor shows up"

❌ This fails by construction if the audit is Type II.

- **What Type II tests.** Controls must operate consistently across an observation window of 3 to 12 months. The auditor checks evidence that the policy ran: key-event logs, access reviews, approval records, and rotations that actually happened.
- **What a late policy gives you.** A policy adopted the week before satisfies Type I, a point-in-time check. It fails Type II because there is no operating history behind it.
- **Your timeline.** 10 weeks is under the 3-month minimum. Even if you start today, you can't accumulate a clean 3-month window by the audit date unless the window began earlier.

**What to do this week, in order:**

1. **Ask the auditor**, in writing: Type I or Type II, and what are the observation window start and end dates? Confirm this before anything else, because the rest depends on it.
2. **Ask sales exactly what was promised.** Was it a Type II report, or "SOC 2 in progress"? Many buyers accept a Type I report or a bridge letter now, with Type II to follow. If the deal truly needs Type II, escalate the date risk to the deal owner now, not in week 9.
3. **Adopt the policy this week**, not the week before the audit. Covers provisioning, rotation, revocation and destruction (CC7.2, C1.2). The window can't start until the policy exists.
4. **Start generating evidence now.** This is what the window actually measures:
   - key-event logs
   - periodic access reviews with a scheduled cadence
   - approval records for privileged key actions
   - at least one real, logged rotation
5. **Exercise the runbook once end-to-end.** Roll a real key with zero downtime, confirm the old key hits zero traffic, deactivate it, wait 24 to 48 hours, then delete it. Log every step.
6. **Run an offboarding sweep.** Enumerate each leaver's user-owned keys, revoke them with zero grace, and log it. Auditors ask for this trail.

## Order of work

Do these in order:

1. Settle which keys are in scope for rotation: customer-issued, internal, or both.
2. Email the auditor (Type I or II, and the window dates) and ask sales what was promised.
3. Adopt the policy and turn on evidence generation.
4. Write the targeted risk analysis, with the cadence your hire wants as the proposed output.
5. Verify overlap, last-used telemetry and atomic roll exist. Then decide on the tool.

## Questions that would change this answer

- Does Fintar touch card numbers directly, or does a processor tokenize them? This changes your PCI scope and which requirements apply.
- Are keys stored hashed, encrypted or in plaintext today?
- Roughly how many live keys exist, and who owns them?