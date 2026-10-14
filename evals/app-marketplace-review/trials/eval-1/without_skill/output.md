# Marketplace security changes after the 3.2.1 compromise

## Bottom line

A pre-listing penetration test would not have stopped this incident. The app passed review as a legitimate product. The attacker then took over the publisher's account and shipped a malicious update, and your platform pushed it to every tenant with no gate, no delay, and no admin action.

The failures were all after listing:
1. A phished credential was enough to publish.
2. A new version reached all installed tenants in under an hour.
3. Nothing flagged a reporting app sending job records to a new destination until someone noticed.

Make "stricter review" mean controls on identity, updates, and runtime. Keep the pentest, but only for high-risk apps (see change 8).

## What to tell the CEO

- **The pentest tests the wrong moment.** It checks version 1.0 on the day it is submitted. Version 3.2.1 shipped months later from an attacker holding the publisher's real credentials.
- **It has real costs.** An external pentest typically costs five figures and takes weeks per submission, which is my estimate and not a quote. That slows supply on a marketplace that is only 14 months old.
- **Both fixes target the same risk.** Gating updates and enforcing identity controls reduce the damage from any future takeover. The pentest only addresses malicious or sloppy first submissions.
- **Offer her a real tightening.** Risk-tiered review, with the pentest mandatory for apps that touch sensitive data (change 8).

## Changes, in priority order

### Do now (this week)

1. **Contain.** Confirm 3.2.1 is delisted and rolled back, and revoke all API tokens and OAuth grants issued to that app. Block the unknown endpoint at any egress you control.
2. **Audit the other 61 publishers.** Force a credential reset and MFA enrollment, and review recent logins and version pushes for anomalies. The same phishing campaign may have reached others.
3. **Notify.** Decide with legal what the affected tenants are owed. Customer job records are likely personal data, so notification deadlines (for example GDPR's 72 hours) and contract terms may already apply. Give tenants the endpoint, the time window, and the record types involved.

### Within 30 days

4. **Phishing-resistant MFA for all publisher accounts.** Use passkeys or hardware keys, and do not allow SMS or email codes. Require step-up re-authentication to publish a version. Alert on new device or location logins, and add a cooling-off period after any change to the account's email, MFA, or ownership.
5. **Staged rollout with a platform kill switch.** Roll each new version out in stages, for example 1%, then 10%, then 100%, with hold times between stages. A bad update then hits dozens of tenants, not 4,100. Build a one-click global "halt and revert app X" that you control, not the publisher.
6. **Automated diff review on every version, not just the first.** Scan each release for new outbound domains, new permission scopes, new dependencies, and obfuscated code. Hold any release that expands scopes or egress for manual review before it starts rolling out.
7. **Per-app runtime limits and detection:**
   - Rate-limit and volume-cap each app's reads per tenant.
   - Alert on bulk reads that deviate from the app's baseline.
   - Alert on traffic to any destination the app has not declared.
   - If apps run on your infrastructure, enforce a declared egress allowlist at the proxy.

### Within 90 days

8. **Risk-tiered review.** Tier apps by the data they can reach:
   - **High** (customer PII, job records, write access, or credentials): code review plus a third-party pentest at listing, repeated annually and on any major change.
   - **Medium:** automated scanning plus a manual review.
   - **Low:** automated scanning only.

   This covers the CEO's concern for the apps that matter, without a blanket gate on everything.
9. **Tenant-side control over updates.** Keep auto-update, because it delivers security fixes fast. Make it conditional:
   - Updates with no permission or egress change continue to auto-apply, but only after the staged rollout.
   - Updates that expand scopes or add destinations require tenant-admin approval.
   - Let tenants pin a version, and show them a per-app activity log.
10. **Signed releases.** Require releases to be signed with a key held separately from the publisher's web login, so account takeover alone cannot publish. Verify the signature at install and update time.
11. **Publisher agreement.** Require a security contact, an incident-notification SLA, and your right to suspend an app immediately.
12. **Incident runbook and drills.** Write the runbook and rehearse a "compromised publisher" scenario. Track time to detect and time to contain.

## Metrics to report

- Share of publishers on phishing-resistant MFA (target 100%).
- Median blast radius of a bad release before halt (target under 1% of tenants).
- Time to detect and time to contain a malicious release.
- Share of releases that triggered a manual hold.

## Open questions to answer before Friday

I can't answer these from here, and they change the plan:

- **Time to detect:** how long did the exfiltration run before anyone noticed, and how did you find out? This sets the priority of change 7.
- **Scope of loss:** how many tenants and records were actually sent out? Your logs should show this, and your notification duty depends on it.
- **Where apps run:** if they run on your infrastructure, you can enforce egress. If they run on the publisher's servers, you can only limit what your API exposes to them, and the controls in change 7 shift to API-side limits.
- **Existing kill switch:** can you halt or revert a version platform-wide today? If not, build that first.