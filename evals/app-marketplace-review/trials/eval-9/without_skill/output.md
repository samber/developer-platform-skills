# Ferrule review policy: ship-readiness verdict

**Verdict: ❌ Not ready to ship.** I only saw your summary, so the full doc may already cover some of these gaps. As summarized, Sections 2 and 3 together let one stolen developer password push code into customer tenants that hold purchase-order data, with no human review. Section 5 is a strategy decision that doesn't belong inside a policy doc.

## Blockers (fix before shipping)

### 1. Section 3 (Publish) is the biggest hole
- **Weak login.** Password plus SMS is phishable and open to SIM-swap. It guards the one action with the most blast radius.
- **No safety net after publish.** Builds go live to tenants "that night" with no staging, no signature check and no rollback.
- **Result.** An attacker who phishes one developer ships malicious code into every tenant that installed that app.
- **Fix:**
  - Require phishing-resistant MFA (WebAuthn/passkeys) for publish rights.
  - Sign builds, and verify the signature at install time.
  - Roll out in stages (for example 1%, then 10%, then 100% over days), with an automatic halt on error or anomaly.
  - Give Ferrule a kill switch and one-click rollback.
  - Add a publish-to-live delay for apps in enhanced review.

### 2. Section 2 (Updates) makes Section 1 meaningless
- **The review happens once, then goes stale.** An app can pass admission, then change anything in a "minor" update.
- **"Minor" is undefined.** If it means the version number, the developer decides, and an attacker will label everything minor.
- **Fix:** trigger re-review on objective changes, whatever the version number says:
  - any new or widened scope
  - new data access
  - new outbound domains
  - new or changed permissions
  - changed dependencies or the build pipeline
  - a change of developer account or ownership
  Run automated diff checks on every update, including minor ones.

### 3. Auto-install into tenants needs customer consent for risk changes
- **Silent scope growth.** Overnight auto-install means an update that gains scopes grants them without any customer admin saying yes.
- **Fix:**
  - Auto-install only updates that keep scope unchanged.
  - Hold any scope or data-access increase until a tenant admin approves it.
  - Let tenants pin versions or opt out of auto-update for sensitive apps.

### 4. Section 5 contradicts the rest of the doc
- **You've already chosen.** Sections 1 and 4 are curation: admission review, plus the power to hide, suspend and remove. The doc is a curated marketplace whether or not it says so.
- **Decide before you write the sections.** Open versus curated sets how strict Sections 1 to 4 must be.
- **Don't settle it in this doc.** It's a strategy call for leadership. The policy doc should record the outcome.
- **My recommendation: curated, with tiers.**
  - You hold PO and financial data, and you push updates automatically. Customers are trusting Ferrule, not each developer.
  - Use light-touch review for low-risk apps that never touch tenant data.
  - Use the full review for apps with data scopes.
  - Revisit if developer supply, not trust, becomes the bottleneck.

## Fix before shipping, but not blockers

### 5. Section 1 (Admission)
- **"Enhanced review at the reviewer's discretion" is inconsistent.** Two reviewers will treat the same app differently.
  - **Fix:** make the trigger objective. Any read or write scope on PO, supplier, payment or bank data goes to enhanced review.
  - Keep discretion as an escalation only, never as an exemption.
- **The security questionnaire is self-attested.** Say what you verify independently: a scan of the build, an outbound-domain list checked against traffic, and a dependency audit.
- **Define what enhanced review contains.** Examples are a code or behavior test, a pen test report, and data-flow documentation.
- **Say what happens to the 210 existing apps.** Are they grandfathered or re-reviewed? Leaving this out is how the oldest apps become the weakest.
- **State the reviewer SLA, the rejection reasons and an appeal path.**

### 6. Section 4 (Enforcement) is a power with no process
- **"Policies" isn't defined.** Name the rule set (the developer terms, this doc, and so on).
- **The three actions aren't defined.** Spell out what hide, suspend and remove each do. For example: does a suspend stop new installs only, or also disable existing installs and revoke their tokens?
- **No emergency path.** Split it into an immediate-action path for active harm and a normal path with notice.
- **Nothing for affected customers.** Say how and when they are told, and what happens to their data and integrations.
- **Nothing for developers.** Give them notice, an explanation and an appeal, except where there is active harm.
- **No incident and vulnerability process.** Add a disclosure channel, response times and a requirement to notify tenants.

## Missing sections to add

- **Continuous monitoring after publish.** Look for behavior drift, new egress and anomalous API use.
- **Developer account security rules.** Cover team roles, who can publish, and offboarding.
- **Customer-side controls.** Cover admin approval, version pinning and an audit log.
- **A definition of "major" and "minor"** that is tied to the objective triggers above.

## Fastest path to a shippable version

1. **Decide the open versus curated question.** I'd start from curated with tiers. This can happen in parallel with the other work.
2. **Rewrite Sections 2 and 3**: objective re-review triggers, WebAuthn, signed builds, staged rollout, rollback, and consent for scope changes.
3. **Tighten Sections 1 and 4**: objective enhanced-review triggers, the existing-app plan, and defined enforcement actions with emergency and appeal paths.
4. **Add monitoring and the incident process.**
5. **Run a second review of the full doc,** ideally with someone who owns the security side of the auto-install pipeline.

If you can share the full text of Sections 1 to 4, I can mark up exact wording changes. If the open versus curated decision is still undecided, I can lay out the options for the leadership discussion.