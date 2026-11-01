# Gmail inbox-summary app: CASA Tier 2 and the fine-tuning plan

**Bottom line:** book the assessment, but don't plan on "done forever", and don't start the fine-tuning project. As described, it breaks Google's policy and would put the app's Gmail access at risk. I wrote this from memory of Google's and the App Defense Alliance's (ADA) published policies, without checking live docs, so confirm the details below against the email and current docs.

## Do this week

1. **Confirm the email is real.** Fake "CASA required" emails exist. Open the Google Cloud Console OAuth verification center for the project and check that the same request shows there. Pick a lab only from the ADA's authorized-lab list.
2. **Read what Google assigned.** Google sets the tier, not you. Note the deadline, the tier, the project and client IDs in scope, and the scopes in scope. If it says Tier 3, a Tier 2 self-scan won't satisfy it.
3. **Get 2–3 lab quotes.** Fees vary a lot by lab. Ask what's included: retests, the letter of validation, and the renewal price. The cheapest first-year quote can lose to a lab with a cheaper annual renewal.
4. **Do a short pre-scan fix pass** before paying (see "Prepare for the scan" below).
5. **Park the fine-tuning work** until the policy question below is settled.

## Gaps in the CTO's plan

### 1. It is annual, not one-time
- CASA validation lasts about 12 months, and Google re-requests it each year.
- If it lapses, restricted-scope access can be pulled, and the app falls back to unverified status with a user cap.
- Material changes can trigger earlier review. Examples are new scopes, new data flows, new subprocessors, and a changed privacy policy.
- **Make it cheap to repeat.** Run the same approved SAST and DAST tools in CI on a schedule. Keep evidence (scan reports, fix tickets) in one folder. Put the renewal on the calendar about 3 months ahead.

### 2. Scanning is the easy part
- Tier 2 means you run an approved scan, fix the findings, and the lab validates the result.
- Findings, especially high and medium ones, must be fixed before the letter is issued.
- The assessment is based on a subset of OWASP ASVS (the app-security checklist). The scan alone won't cover every item, so expect questionnaire items too.

### 3. Prepare for the scan
These are the usual failures for a server-side Gmail app:
- Encrypt OAuth refresh tokens at rest and keep them in a secrets manager.
- Keep email bodies and summaries out of logs, traces, and error trackers.
- Set a retention limit on stored mail and summaries.
- Delete everything on user revocation or account deletion, including backups, queues, and caches.
- Restrict staff access to production data, and log that access.
- Check dependencies, TLS configuration, and security headers.
- Write down which scopes you use and why. Request the narrowest scope that works.

### 4. Check where email content flows
- Mail content sent to an LLM vendor counts as a transfer of Google user data.
- The vendor must be contractually barred from training on it, and zero-retention terms are best.
- Disclose the vendor in your privacy policy.
- Limited Use also restricts humans reading user mail. Staff generally may not read it, except with the user's consent, for security or legal reasons, or in aggregated and anonymized form. That affects debugging sessions and eval sets built from real mail.

### 5. Policy and disclosure
- The privacy policy and homepage need the Limited Use disclosure for Google user data.
- Keep the OAuth consent screen, demo video, and scope justifications consistent with what the app actually does. Mismatches fail the OAuth verification review, which is separate from CASA.

## Product's fine-tuning request: not as described

**Don't do it.** Google's API Services User Data Policy, with its Limited Use rules for restricted scopes, bars using Google user data to develop, improve, or train generalized AI/ML models.

- **Summaries don't escape the rule.** They are derived from user data, and Limited Use covers derived data. "Summarized" doesn't make it clean.
- **"For everyone" is the problem.** A shared model trained on customer mail is exactly what the policy prohibits.
- **Consequences.** Token revocation, app suspension, and a failed or revoked verification. This is the same restricted access you're paying CASA to keep.

**Beyond Google, there are other problems:**
- **GDPR.** Training is a new purpose. Email senders never consented, and legitimate interest is weak for content this private. You'd need a DPIA at minimum.
- **Controller and processor roles.** If business customers use the app, training for your own purposes makes you a controller for that data. Your DPAs probably don't allow that.
- **Leakage and deletion.** Fine-tuned models can regurgitate training text to other users. You also can't reliably delete one person's data from weights, which conflicts with the revocation and deletion duties above.

**Alternatives that stay inside the rules:**
- **Per-user personalization.** Use a per-user prompt, preference store, or retrieval over that user's own mail, visible to and used for that user only.
- **Non-Gmail data.** Public or licensed email corpora, or synthetic emails you generate. Check the licenses first.
- **Prompt and pipeline work.** Improve prompts and the summarization pipeline, using evals on synthetic or consented data.
- **Ask Google.** If product insists, get written clarification from Google's OAuth verification contact before building anything. Don't rely on an internal reading of the policy.

**If any training on customer mail has already happened,** stop it, record what data and which models were involved, and get legal advice before the assessment starts. Assessors and Google both ask about data use.

## Open questions

- Which tier does the email assign, and what is the deadline?
- Which LLM vendor receives mail content, and under what terms?
- Has any customer mail already been used for training or eval sets?
- Are there EU users, or business customers with DPAs?

If you send me the answers, I can turn this into a one-page checklist for the CTO and a short memo for product.