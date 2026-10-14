# Larkfield marketplace: what we change after 3.2.1

## Decision for the CEO

**Don't make a pen test on every new submission the main change.** It would not have stopped this incident, and it costs reviewer and developer time on the wrong control.

- The reporting app was already listed and presumably already reviewed. The attacker took over the publisher's account with phished credentials, then pushed 3.2.1 through the update channel.
- A stricter front door only checks the first submission. The compromise happened afterward.
- This was a publisher-account compromise, not a review failure. Don't write the incident up as "review missed it." The fix is to harden the channel that ships code to tenants, and then to deepen review where the data sensitivity justifies it.

**Recommended answer to her:** "Stricter, yes, but applied to updates and publisher accounts. Third-party testing stays for the apps with the most data access."

## Assumptions

I could not interview you before Friday, so these are my assumptions. Each one says what changes if it's wrong.

| # | Assumption | If wrong |
|---|---|---|
| 1 | The maximum app grant is read-write on job and customer records, with personal data likely (customer names, addresses, technicians). I'm treating this as "(c), edging into (d)". | If apps are read-only, the third-party test tier shrinks. If regulated, the hard gate stays regardless of volume. |
| 2 | Updates auto-propagate with no admin action. You confirmed this. | n/a |
| 3 | Update volume is the cost driver. I don't have your numbers. | If you see fewer than ~5 updates a month across all 62 apps, you could keep the hard gate on everything. |
| 4 | There is no hold between "update cleared" and "update live". 3.2.1 hit every tenant within an hour, so this seems true. | n/a |
| 5 | You have a hard Friday deadline, so I've ordered the rungs that ship as policy text first. | n/a |
| 6 | I don't know whether you serve EU customers. This affects the appeal path and possibly breach notification. | If EU, promote the appeal rung (section 5). |

## What actually changes, in order of urgency

### A. This week: contain and verify

These are not new policy. They are the incident response.

1. **Kill 3.2.1.** Pull the version, roll tenants back to the last known-good version, and revoke the app's tokens and installed grants.
2. **Reset the publisher.** Rotate every credential and session, and require FIDO keys before any restore.
3. **Sweep the other 61 publishers.** One phish usually means a campaign. Check them for the same lure, unexpected recent logins, and unrecognized endpoints in current versions.
4. **Tell the affected tenants, with legal in the loop.** Job records likely include personal data. Ask counsel about notification deadlines now (e.g. GDPR's 72 hours for EU data). I can't tell you what applies to you.
5. **Preserve evidence.** Keep the 3.2.1 artifact, the exfiltration endpoint, and the account logs.

### B. The policy the Friday write-up should contain

**1. Publish channel (the main fix)**

| Control | Rule | Why |
|---|---|---|
| Publisher login | Phishing-resistant FIDO 2FA required on every publisher account, with a cutoff date after which non-FIDO accounts can't publish | Phished credentials were the entry point. TOTP-style 2FA can be defeated by a reset flow, as in the 2025 npm maintainer phish. |
| Publish tokens | Short-lived and scoped, with a 7-day default and 90-day maximum (the npm model after its 2025 worm) | A stolen token expires before most attackers use it. |
| **Propagation hold** | **24-48 hours between "cleared" and "auto-propagates" to tenants**, with a kill switch inside the window and an expedite path for genuine security fixes | This is mandatory when updates auto-propagate. It is the missing control: an hour from push to every tenant is the failure. |
| OIDC trusted publishing | Promote it as the publisher count grows | It removes long-lived credentials to steal. |
| Signed artifacts enforced at install | Not now | It is the highest effort. It matters most when clients run auto-updated code (extension-style runtimes). Revisit later. |

Layer these controls. Independent researchers demonstrated bypasses of a major marketplace's documented controls in 2025, so none of them is enough alone.

**2. Re-review on update, with objective triggers**

A "minor update" is one with **all** of the following:
- no new OAuth scopes
- no new external endpoints
- no change to data handling
- no payment-model change
- no new app type

Anything else triggers a full re-review. A developer can self-assess this list before submitting.

**Would this have caught 3.2.1?** An unknown external endpoint is exactly the "new external endpoints" trigger. If 3.2.1 added one, a diff of declared and observed endpoints between versions should have held it for human review. I can't confirm the attacker didn't obfuscate or reuse an allowed domain, so don't promise that to the CEO. Treat the trigger as one layer, not a guarantee.

- **Automated scan on every release:** endpoint and scope diff, secret scan, and dependency check. Without a scan, the fast path becomes the gap.
- **Ticketing:** auto-ticket critical and high findings only. Send only genuinely ambiguous signals (secret-scan hits) to humans.
- **Annual floor for the restricted tier:** apps with write or restricted scopes get re-reviewed once a year even with no code change. That catches drift in apps that never ship an update.

**3. Where a third-party pen test belongs (the CEO's idea, scoped)**

- **Trigger, self-assessable:** an app requesting write access to customer records or restricted scopes moves up one review tier. At that tier, an independent third-party security assessment is part of admission and repeats annually.
- **Everything below that tier** gets the internal automated pre-screen plus human triage.
- **Cost anchor:** Google's CASA program lists roughly $500-$6,000 per assessment, and $4,500 for a full manual test at one named lab. These are Google's figures, not yours, so treat them as an order of magnitude.
- **Scale:** a mandatory test on all 62 apps and every new submission is the single hard gate at its most expensive. It gives buyers a uniform guarantee, but it was not the control that failed here.

**4. Review pipeline shape**

- **Today:** full review for new apps and major versions.
- **Move to a staged gate:** instant or near-instant clearance for objectively minor updates, plus continuous scanning. Atlassian's shape is the benchmark: new apps and major versions take 5-10 business days, minor updates clear instantly.
- **Move up only if reviewer cost isn't the constraint.** If your volume is low, keep the hard gate for everything and still add the hold.

**5. Appeal**

Add a defined human-reviewed appeal with a stated turnaround, run by someone who did not make the original decision. Every rejection or suspension cites the violated policy. This matters here because you are about to suspend and revoke more often, and publishers will contest it. If you serve EU businesses, plan to build the dashboard-integrated version later (EU P2B mediation rights).

**6. Enforcement ladder**

Role names are placeholders for your org.

| Rung | Owner | Notice to developer | Evidence that fires it |
|---|---|---|---|
| 1. Finding raised | Marketplace security | n/a | Scan or report finding |
| 2. Remediation SLA | Marketplace security | Per severity: critical 24h, high 7d, medium 30d (my proposal, adjust to capacity) | Confirmed finding |
| 3. Listing hidden | Marketplace security lead | 24h, or none if active harm | Unfixed critical/high past SLA |
| 4. New installs suspended | Head of platform | Same day | Active exploitation suspected, or repeated SLA misses |
| 5. Tokens revoked / kill switch | On-call security engineer (no approval wait) | None for active compromise, notify immediately after | Unrecognized endpoint, compromise indicators, or the account-takeover pattern |
| 6. Delisting, with notice to affected tenants | Head of platform plus legal | Per contract | Confirmed malicious behavior or bad-faith publisher |

Also write:
- **Discovery channels:** a required security contact per partner, an incident-reporting address, internal scanning, and a disclosure program. Add a bug bounty as the program matures.
- **Publisher-level enforcement:** repeated non-response or low-quality submissions escalate at partner level, separate from single-app action.
- **Notice runway:** give already-listed apps at least six months before a new requirement takes effect (Atlassian's commitment). The FIDO cutoff and hold policy should use this runway except where active-risk exceptions apply.

**Additions beyond the skill (my suggestions, not from it)**
- **Staged rollout:** after the hold, release to a canary percentage of tenants before 100%.
- **Step-up auth at publish:** FIDO re-prompt on every publish action, plus alerts on new devices or a dormant account suddenly publishing.
- **Runtime egress control:** apps declare their endpoints, and the platform blocks or alerts on traffic to anything else. This would address "endpoint nobody recognized" directly, but it is real engineering. Scope it before promising it.
- **Two-person approval for publishing** on the restricted tier.

### C. Four gates for the write-up

1. Every review tier has an objective escalation trigger a developer can self-assess. ✅ (write-or-restricted-scope moves a tier)
2. "Minor update" is defined by objective criteria. ✅ (the list in B2)
3. Every enforcement rung has an owner, notice period, and firing evidence. ✅ (the ladder table; fill in real names)
4. The publish channel has FIDO 2FA, short-lived tokens, and the hold, since updates auto-propagate. ✅

## Sequence

1. **By Friday (policy text):** FIDO requirement and cutoff date, the minor-update definition, the ladder, the pen-test tier trigger, and the notice-runway communication.
2. **Next 2-4 weeks (engineering):** the propagation hold with kill switch and expedite path, and the per-release endpoint and scope diff scan. If the kill switch doesn't exist yet, build it first.
3. **Next quarter:** short-lived tokens, OIDC for larger publishers, canary rollout, the egress allowlist decision, and the first third-party assessments for the restricted tier.

## What I'd put in front of the CEO

- **What happened:** a legitimate publisher account was phished, and the attacker used the normal update path. Stricter review of first submissions would not have intervened.
- **What we're changing:** locking publisher accounts to hardware keys, putting a 24-48 hour hold and kill switch in front of every update, and re-reviewing any update that adds an endpoint, scope, or data-handling change.
- **What we keep from her instinct:** independent security testing for apps with write or restricted access to customer records, repeated annually.
- **Trade-off:** security fixes still need to go out fast, so the hold has an expedite path. The cost is that ordinary updates reach customers a day or two later.

## KPIs once live

- First-pass approval rate
- Time to first decision against the published SLA
- Share of updates clearing the fast path
- Time from alert to kill switch (the number 3.2.1 would have failed)
- Appeal overturn rate
- Post-approval findings per quarter, with time to remediate
- Scan false-positive rate. If it rises, reviewers learn to ignore the scanner.

## Open questions

- What is your update volume per month, and how many of the 62 apps hold write access to job records?
- Does a kill switch exist today?
- Do you serve EU businesses?
- How many reviewer hours per week can you commit?

I'm confident in the update-channel diagnosis and the ordering of the controls. The numbers in the SLA and ladder tables are my proposals and need your capacity to settle.