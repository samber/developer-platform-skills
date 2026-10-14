**Recommendation: don't launch open. Launch with review depth tied to what each app can touch. Heavy review applies only to apps that write to CRM records or read job files. Light review covers everything below that. Add the "Certified" badge and the enterprise trust tier on top of that gate, not in place of it.**

The skill's interview asks ten questions. You answered about four, so I filled gaps with stated assumptions. The list at the end shows which gaps would change the answer.

## Why not open-then-badge

1. **Write access to customer records is the heaviest review tier.** Review depth follows the maximum grant an app can hold. Read-write on contacts, deals and job files is the case where the skill says an uncertified-but-listed tier is "an incident waiting to be attributed to you."
2. **A later badge does not reduce what uncertified apps can do.** An open-listed app still holds the same write grant. The badge only labels the good ones. The bad ones stay live with the same access.
3. **Your top 20 accounts are already asking.** Under open launch the renewal answer is "a completeness check." That fails the question these accounts keep raising.
4. **You cannot tighten later without cost.** Apps already listed need at least six months' notice before a new requirement applies. That is the benchmark commitment from Atlassian's Cloud Fortified docs. Retroactive tightening burns the partner trust the program exists to build. The same shape (a minimal bar to list, plus an optional certified tier) is the "starved" two-rung ladder. The skill reserves it for cases where developer-adoption friction is the main risk, which is rare once apps can write to business records.
5. **Her 50-app argument is real but misdirected.** The risk is friction, not depth. Fix friction with tooling, tiers and a fast service level, not by removing the gate.

## What to build instead

**Three tiers, with objective triggers a developer can self-assess before submitting.** The per-scope taxonomy belongs to `oauth2-provider-design`.

- **Tier A:** no customer-record access (widgets, metadata, public data). Review: automated pre-screen, completeness, functional and scope check. This is the light, fast lane.
- **Tier B:** read-only on named, narrow objects. Review: Tier A, plus a scope-necessity check and a data-egress check (external endpoints, subprocessors, retention).
- **Tier C:** any write access, any job-file access, or broad read. Review: the full gate. That means a security questionnaire, SAST and secret scan, DAST on external endpoints, data-access review, and OAuth/install flow tracing.

Any scope upgrade moves an app up a tier. Reviewers must verify that each scope is necessary, not just declared.

**Pipeline.** Automation runs first, and humans only triage. Auto-ticket critical and high findings. Route only genuinely ambiguous signals, such as secret-scan hits, to people. Give developers the reviewer's own scan tool before they submit. Salesforce reports that roughly half of first submissions fail. Self-screening attacks that rate directly.

**Targets.**
- Tier C decision in 5–10 business days. That is Atlassian's band for new apps. Salesforce runs 6–10 weeks, which would not fit your window.
- Tier A and B much faster.
- Set a submission cutoff around week 6–7 so Tier C reviews finish before week 11.

## Close the update channel first

Every major 2024–2026 marketplace incident rode a compromised publisher account or an ungated update, not a malicious first submission. A heavy front gate with an open back door is the skill's first named failure mode. These controls are mostly policy text, so they fit 11 weeks:

1. **Phishing-resistant (FIDO) 2FA** on publisher accounts.
2. **Short-lived scoped publish tokens.** npm's model is a 7-day default and a 90-day maximum.
3. **A 24–48 hour propagation hold** between a cleared update and its rollout, with a kill switch and an expedite path for security fixes. It becomes mandatory if updates auto-propagate to installed tenants.
4. **Objective re-review triggers.** Full re-review fires on any of these:
   - New OAuth scopes.
   - New external endpoints.
   - A change to data handling.
   - A payment-model change.
   - A new app type.

   Anything else clears a fast path. Scan every release. Add an annual floor for Tier C.

## The 50-app question

- **Be honest about the number.** If most useful CRM apps need write access, the Tier C gate caps launch count. Her estimate of about 12 is her own, and I can't verify it.
- **Count tells you less than activation.** Twelve vetted apps with real installs make the marketplace look alive more than 50 listings no one trusts. Use Tier A and B volume, pre-recruited launch partners, and a public "in review" pipeline to fill the shelf honestly.
- **If you have no reviewers at all, don't fall back to open.** Launch with read-only scopes and unlock write scopes per app as each one clears review. The marketplace still opens on time, and the grant stays capped.

## Enterprise trust tier

- Build it later, stacked on a proven base gate. It means security, reliability and support commitments re-verified annually, as in Atlassian Cloud Fortified and Microsoft 365 Certification.
- Trigger: two review cycles completed within the stated service level.
- At launch, give the top 20 accounts the published review policy and the tier model. That answers their renewal question now.
- Fix the badge's meaning in advance. Tier C approved means "Verified." The enterprise tier is the extra, annually re-verified layer.

## Enforcement and appeals

- **Enforcement ladder.** Write it before launch, because a rule with no rung behind it is a preference. The rungs are finding, remediation deadline by severity, listing hidden, new installs suspended, tokens revoked, and delisting with customer notice. Each rung needs an owner and a notice period.
- **Appeals.** Every rejection cites the specific policy violated. A human who did not make the original decision reviews appeals, with a stated turnaround. If you have EU users, that also covers EU platform-to-business (P2B) rules.

## Assumptions to confirm

Reply with answers to any of these and I'll re-rank:

1. **Max grant:** is it read-write on CRM records (my assumption), or does it also include regulated data such as financial or personal data?
2. **Reviewers:** who reviews today, and how many hours per week? Zero reviewers triggers the read-only-first fallback above.
3. **Update propagation:** do updates auto-propagate to tenants, or does each customer admin upgrade?
4. **Volume:** how many apps and updates per month do you expect?
5. **EU users:** do you serve EU-based business users?

**Next step:** answer question 2, then I'll draft section 1 of the design document, the pipeline shape and tier triggers, for your review.