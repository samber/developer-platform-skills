# Fieldmark on AppExchange: what you need to do

## Bottom line

- ❌ **"No package, so no security review" is wrong.** An API listing goes through the same review as a package. Your web app and APIs get DAST (dynamic scanning). The review is the same gate for both listing types.
- ❌ **Next month is not feasible.** Today is 2026-10-30. Practitioners estimate 4 to 9 months from signup to first paid install†. Expect first paid install around **April–May 2027**, with a range of March–July 2027.
- ⚠️ **Checkout forces a package.** You can't use Checkout with a pure API listing. You'd need a thin managed 2GP package that carries only your OAuth app (an ECA, defined below).
- 🔴 **Check your 2024 Connected App first.** If it is used by more than two customer production orgs, the OAuth controls were mandatory by May 11, 2026†. That deadline has passed, and the stated sanction is delisting or suspended access to Salesforce†.

**Next action today:** count the customer production orgs authorized through your Connected App, and check which OAuth controls are on.

## 1. Assumptions

You couldn't be asked, so I assumed each of these. Tell me which are wrong.

1. **In-org footprint:** Nothing runs in the customer's org. Your SaaS only calls Salesforce APIs.
2. **Editions:** Buyers run Enterprise or higher. If any run Professional or Group, they can reach the API only through a reviewed managed package with an API token. That's another reason to take the package route.
3. **Stage:** Fieldmark is not yet a Salesforce partner. No Partner Business Org (PBO), no signed partner agreement (PADA).
4. **Pricing:** $40 per user per month, per seat, monthly subscription, charged in USD. Fieldmark is a US company (Austin).
5. **Connected App:** Created in 2024 and authorized in more than two customer production orgs. The OAuth controls status is unknown.
6. **Capacity:** No dedicated security engineer. 40 people means a few engineering weeks are available, not a team.
7. **Date:** Marketing's "next month" means a live listing in November 2026.

## 2. Listing and payment path

**Recommendation: managed 2GP package, thin, carrying only the ECA, with Checkout.**

| Option | Verdict for Fieldmark |
|---|---|
| API listing, bill outside Salesforce | Fastest and lightest: no Code Analyzer, no Checkmarx. But no Checkout. A paid app reports orders through the Channel Order App (COA). Switching to Checkout later means a new listing, because listing type is fixed at creation. |
| **Managed 2GP + Checkout** | **Fits.** Per-seat monthly subscription is supported. You qualify as a US company, not OEM, and you accept the clickthrough PADA. Cost is 15% of net revenue + $0.30 per card payment†. At $40 that is roughly $6 per seat per month†, subject to how Salesforce defines "net". |
| Managed 2GP + GTM app private offers | Not available to you yet. Needs an existing ISVforce partner, USD, GTM terms in the PADA, and application approval. Orders run 12 months, paid upfront by ACH, with no auto-renew, which doesn't match your monthly model. |
| Managed 2GP + COA (offline PADA) | Only if you need usage, tiers or multi-year deals. Not your case. |

**Which answer moved the ranking:**
- Your Checkout ask (answer 3) moved the package route up.
- Your date (answer 5) moves the API listing up. It is lighter, but it can't meet November either, so it doesn't win.

**Consequences of the package route:**
- A thin package that carries the ECA still counts as a managed package. Checkout and License Management App (LMA) licensing become available, but Code Analyzer and Checkmarx scans apply.
- Keep Apex out of the package if you can. That shrinks the Code Analyzer and 75% test-coverage burden.
- Lightning Ready certification is mandatory for new submissions. Confirm with Partner Support how it applies to a package with no UI.
- Switching free↔paid, Checkout↔non-Checkout, or pricing units later sends the listing back to approval†. Settle the $40 per user per month model before submission.
- Listing approval and the signed PADA both come before publishing.

## 3. Irreversible-choice register

Owner names are roles; assign real people.

| Choice | Decision | Owner | Decide by |
|---|---|---|---|
| Listing type | Packaged Solution (thin managed 2GP), not API. Fixed at creation; moving later means a new listing. | CEO + CTO | 2026-11-13 |
| Namespace | The product brand, once. It prefixes every component API name and is fixed to the package at creation. | CTO + Marketing | 2026-11-20, before registering in Dev Hub |
| Global Apex / Visualforce | None. Global is permanent. Ship zero Apex, or only protected and `@namespaceAccessible` code. | CTO | Before first package version |
| Protected components | Mark every internal custom setting, metadata type, label and permission protected. Once released unprotected, they stay. | CTO | Before first managed-released version |
| Pricing path | Checkout at $40 per user per month, monthly subscription. Changing it sends the listing back to approval. | CEO + Finance | 2026-11-20, before the PADA is signed |
| OAuth controls | Enable all four (PKCE, refresh token rotation, 30-day idle expiry, IP allowlist). Each locks once on. Ship client changes first, test in a sandbox, then enable. | CTO / backend lead | Audit in November; enable before submission |
| Promotion to managed-released | Never reverses. Only one beta per minor version can be promoted. | CTO | At release |

**One question to settle before you build.** Your 2024 Connected App is in scope of the OAuth controls. Since Spring '26, new integrations must be built on an ECA. Decide whether to keep the Connected App or move to a new ECA inside the package. Moving may force every customer to re-authorize. Confirm with Partner Support.

## 4. Security review plan

**In-scope endpoints.** Anything that authenticates users or sends or receives Salesforce data:
- OAuth login and callback endpoints.
- The web app UI that displays Salesforce accounts and work orders.
- Your REST APIs.
- Sync workers.
- Webhook receivers.
- Token storage.

Get written permission before scanning any third-party endpoint. Include anything you are unsure about, because missing in-scope parts return the submission.

**Scanners:**
- **DAST** (ZAP, Burp or equivalent) on every in-scope endpoint. Fix every finding above informational. Attach a screenshot proving the scan hit the right host, and send full results, not summaries.
- **Code Analyzer**, run with:
  `sf code-analyzer run --rule-selector AppExchange --rule-selector Recommended:Security --output-file CodeAnalyzerReport.html`
  It need not pass 100%.
- **Checkmarx** (Source Code Scanner), 3 runs per version included, because you ship a package.

**Top three risk classes for Fieldmark:**
1. **External endpoint weakness:** TLS below 1.2, weak session handling, any API that returns Salesforce data without authentication.
2. **Secrets and tokens:** the client secret or refresh tokens in code, logs or an unprotected store. In the package, share the client key in documents, never the secret.
3. **XSS and injection:** work order and account fields are customer-controlled text rendered in your app. Escape all output.

**Other materials:**
- A Developer Edition test org with the managed-released version installed and connected to your app. A dead test-org password stalls verification.
- URLs and test credentials for every authenticated external component.
- Solution documentation and information-security policies.
- A false-positive write-up for any flagged finding. Name the code line that guards it; "by design" gives the reviewer nothing to verify.

**Submission week:** week of **2027-01-18**, in the Partner Console wizard, paying the $999 fee†.

**If the review comes back:**
- *Returned* (materials missing): fix and resubmit, no fee.
- *Failed*: each finding is one example of a class, so fix every instance. Change nothing else. Keep the package ID and namespace, then start a follow-up review with a new fee.
- There is no appeal for a failed test. Product Security office hours are the channel.

## 5. Timeline

I counted forward because the original date can't be met. Durations are from the playbook† and the partner-signup step is my estimate. This plan includes one failed review.

| When | Milestone |
|---|---|
| Week of 2026-11-02 | Count orgs on your Connected App. Audit OAuth controls. Apply to the Partner Community. Start the PADA conversation with the account manager. Start DAST. |
| Nov 2026 | Ship client changes for PKCE and refresh token rotation. Test in a sandbox. Make the listing-type, namespace and pricing decisions. |
| Dec 2026 | PBO, LMA, Dev Hub live. Register the namespace. Build the thin package. First Code Analyzer and Checkmarx runs. Fix DAST findings. |
| Week of 2027-01-18 | Submit. |
| Late Jan to Feb | Verification, 1-2 weeks†. |
| Feb to mid-Mar | First test, 3-4 weeks†. Practitioners estimate half of first submissions fail†. |
| Mid-Mar to mid-Apr | Fix every instance of each finding, then retest, 2-4 weeks†, new $999 fee†. |
| Apr 2027 | Pass. Listing approval and PADA signature. Publish. |
| **Apr–May 2027** | **First paid install via Checkout.** |

**What fits the original date:**
- A Fieldmark-owned landing page and content for Salesforce users, to feed marketing's lead gen now.
- The partner application and OAuth-controls fix in November, so the clock starts immediately.

Nothing about a live AppExchange listing fits in November.

## 6. Maintenance calendar

- **Now, overdue:** OAuth controls on the existing Connected App. Each control locks once on, so ship client changes and test in a sandbox first.
  - PKCE on every authorization-code flow. Confidential clients send both `code_verifier` and `client_secret`.
  - Refresh token rotation. Handle races between parallel refreshes.
  - Refresh tokens expire after 30 idle days†.
  - Refresh-token IP allowlist, 256 addresses at most†. Check the exemptions before enabling it on autoscaling egress.
- **Three Salesforce releases a year** (Spring, Summer, Winter): test each in preview sandboxes. Move API calls off any version announced for retirement.
- **New package versions:** build each on the highest managed-released version as ancestor, so it lists without a new review. Patches are for hotfixes only.
- **Push upgrades:** your own test orgs first, then customer sandboxes for a week, then production in batches. Never at customer quarter-end, and 3-4 weeks after a major Salesforce release. Never auto-assign a new feature's permission set to existing users.
- **Periodic re-reviews:** chosen by risk and time since listing, with a fee†. A failed one gives about 60 days†. Keep the security contact on Company Info current. A missed re-review expires every version.
- **Money duties:** unpaid revenue share or review fees also expire the review and pull the listing.
- **COA:** not expected under Checkout. Confirm with your account manager.
- **Reviews:** ask customers at success milestones, never for an incentive.

## Questions that would change this plan

1. Is Fieldmark already a Salesforce partner?
2. How many customer production orgs use your Connected App, and which OAuth controls are on?
3. Do any buyers run Professional or Group edition?
4. Who owns security work in-house?

## Footnote †

Every Salesforce figure marked † (fees, revenue shares, durations, dates, deadlines, sanctions) must be verified against current Salesforce partner docs before you quote it. Salesforce pages quoting review fees of $2,550 or $2,700 are outdated.