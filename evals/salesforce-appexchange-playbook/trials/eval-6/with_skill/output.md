# Pellucid on AppExchange: week-by-week plan

**Bottom line:** "Live on AppExchange" in 10 weeks is not achievable. Today is 2026-10-30, so the booth date is about **Fri 2027-01-08**. You haven't joined the partner program, the Salesforce security review takes 1-2 weeks for verification and 3-4 weeks for the first test†, and about half of first submissions fail†. Practitioners estimate 4-9 months from signup to first paid install†.

- **Best case:** you pass first time, and the listing goes live around **week 13 (late January 2027)**.
- **Realistic case:** one failed review and a retest, so live around **week 19 (mid-March 2027)**.
- **What fits the original date:** a partner badge, a submitted package in review, a working demo, and 1-3 pilot customers on a released version.

Tell the CEO now. The booth messaging must say "coming to AppExchange", not "available on AppExchange".

## 1. Assumptions

I couldn't ask, so each gap below is an assumption. Correct any that are wrong.

| # | Gap | Assumption | If wrong |
|---|---|---|---|
| A1 | What runs in the org | Lightning web components, Apex sync and objects or fields live in the customer's org. Pellucid's SaaS also holds notes and calls Salesforce over OAuth. | Nothing in the org would make an API listing possible. You've described a package, so this is unlikely. |
| A2 | Buyer editions | Enterprise and above. | Professional or Group edition buyers still need the managed package, which you have anyway. |
| A3 | Stage | Not a partner, no Dev Hub, no namespace. | |
| A4 | Pricing | Per user, monthly or annual subscription, list price. No negotiated enterprise deals at launch. | Usage or multi-year deals push you to the offline PADA path (see §2). |
| A5 | Countries | Pellucid is incorporated in the US, UK or EU. | Checkout needs a US, UK or EU company†. Otherwise use COA. |
| A6 | Existing Salesforce integration | No Connected App is live in customer production orgs. | If one exists, the OAuth controls in §4 apply to it too. |
| A7 | Team | 25 people, 2 engineers on this at about 60% each. No in-house AppSec. | Fewer engineer-weeks slips the submission week. |
| A8 | Partner acceptance | The Partner Community application is accepted in about 1-2 weeks. I have no figure for this; check with Salesforce. | A slow acceptance slips everything after it. |

## 2. Listing and payment path

Chosen: **Packaged Solution, managed 2GP, with Checkout.**

- **Why a package (A1):** LWC and Apex in the customer's org rule out an API listing.
- **Why Checkout (A4, A5):** per-seat subscriptions are what Checkout is for. Cost is 15% of net revenue plus $0.30 per card payment†. It needs a clickthrough PADA, a US, UK or EU company, and no OEM.
- **Review fee:** $999 per initial, follow-up or periodic review†. Check the wizard for the current figure. Quotes of $2,550 or $2,700 are outdated†.
- **Package type:** only managed-released versions pass review. 1GP, unlocked and unmanaged packages are not options.
- **Pricing changes:** switching free to paid, Checkout to non-Checkout, or changing pricing units sends the listing back to approval†. Decide pricing in week 2.
- **Fallback (A4, A5):** if you need usage tiers, multi-year deals or a non-US/UK/EU entity, use managed 2GP with COA and an offline PADA. The PNR is set in your PADA, commonly 15% for ISVforce†. Each sale needs a Channel Order App order within one business day†.
- **GTM app private offers:** these need an existing ISVforce partner and a PADA with GTM terms, applied for separately. Don't plan for them at launch.

## 3. Irreversible-choice register

Decide each item before the week shown. Owner names are placeholders; assign real people in week 1.

| Choice | Recommendation | Why it can't be undone | Owner | Decide by |
|---|---|---|---|---|
| Listing type | Packaged Solution | Fixed at creation. Changing later means a new listing. | CEO plus eng lead | Week 1 |
| Namespace | The Pellucid brand (for example `pellucid`) | Fixed to the 2GP package. It prefixes every component API name. | Eng lead | Week 2 |
| Global Apex and Visualforce | Expose one small, versioned global facade. Mark everything else `public` and use `@namespaceAccessible` if you add a second package. | Global classes can never be removed. | Eng lead | Before the first promoted version, week 5 |
| Protected components | Mark all internal custom settings, metadata types, labels and permissions protected. | Once released unprotected, they stay unprotected. | Eng lead | Week 5 |
| Pricing path | Checkout, per user, subscription | Changing it later sends the listing back to approval†. | CEO plus finance | Week 2 |
| OAuth controls on the ECA | Build the external client app. Ship PKCE, refresh-token rotation and the IP allowlist in your client first. Enable the controls after sandbox tests. | Once enabled, the controls can't be turned off. | Eng lead | Week 5 |
| Promotion to managed-released | Promote only a version that passed Code Analyzer and has 75% or more coverage. | Promotion never reverses. Only one beta per minor version can be promoted. | Eng lead | Week 6 |

## 4. Security review plan

**In-scope endpoints.** Test every Pellucid endpoint that authenticates a user or moves Salesforce data. That means:

- the OAuth callback and token endpoints;
- the sync API that writes notes to opportunities;
- the web app login and any pages that show Salesforce data;
- the webhook receivers.

Get written permission before scanning any third-party endpoints.

**Materials** (package plus external service):

- a Developer Edition test org with the managed-released version installed;
- the Code Analyzer report, run with `sf code-analyzer run --rule-selector AppExchange --rule-selector Recommended:Security --output-file CodeAnalyzerReport.html`;
- the Checkmarx source scan report (3 runs per version included†);
- a DAST report (ZAP or Burp) per in-scope endpoint, with a screenshot showing the scan hit the right host, and every finding above informational fixed;
- URLs and test credentials for the external app;
- a false-positive write-up for anything you dispute;
- solution documentation and security policies.

Use the Checklist Builder in the Partner Community for the exact list. A dead test-org password stalls verification, so check it the day before submitting.

**Top three risk classes for your code:**

1. **CRUD/FLS not enforced** in the `@AuraEnabled` methods behind your LWCs and their helpers. Use `WITH USER_MODE` and `AccessLevel.USER_MODE`.
2. **Missing `with sharing`** on classes that handle opportunities and notes. Declare `with sharing` on every class.
3. **SOQL injection or XSS** in the Apex sync and the LWCs. Use bind variables, avoid `innerHTML`, and load no third-party JavaScript off platform.

Check for secrets in code and labels too. Use protected custom metadata or named credentials.

**Scanning and fixing:** run Code Analyzer in CI from the first sprint, not the week before submission. Fix CRUD/FLS first, then the sharing and SOQL sweep, then DAST, then write up false positives.

**If it fails:**

- Each finding is one example of a class, so fix every instance across the solution.
- Change nothing else. Extra changes force a full initial review and a new fee†.
- Keep the package ID and namespace.
- Rescan, start a follow-up review, and pay the fee.
- There is no appeal for a failed test†, though Product Security office hours are the channel.
- If every finding is a false positive, attach the write-up to the failed review and resubmit without a fee.

**Submission week:** week 6 (Dec 7-11).

## 5. Timeline

Week 1 starts Mon 2026-11-02. Salesforce durations are† figures.

| Week | Dates (Mon) | Work | Output |
|---|---|---|---|
| 1 | Nov 2 | Apply to the Partner Community. Tell the CEO the realistic date. Pick owners. Start the PADA conversation with the account manager. | Application sent. Booth messaging changed to "coming soon". |
| 2 | Nov 9 | Partner acceptance. Create the Partner Business Org (LMA, COA, Dev Hub). Pick the namespace. Confirm the Checkout and pricing decision. | Dev Hub on. Namespace registered and linked. |
| 3 | Nov 16 | Build the 2GP package skeleton, LWCs and Apex sync in user mode. Create the ECA. Set up Code Analyzer in CI. | First scratch-org install. |
| 4 | Nov 23 | Continue the build. Run the first Code Analyzer scan and fix CRUD/FLS. Start the DAST setup on the Pellucid endpoints. (US Thanksgiving week: slow.) | First scan report. |
| 5 | Nov 30 | Feature freeze. Sharing and SOQL sweep. Fix DAST findings. Mark protected components. Ship PKCE and rotation in the client. Cover every trigger and reach 75% or more coverage. | Release-candidate code. |
| 6 | Dec 7 | Create and promote the managed-released version. Complete Lightning Ready certification. Build the test org and docs. Run Checkmarx. Submit and pay the fee. | **Submitted.** |
| 7-8 | Dec 14, Dec 21 | Verification (1-2 weeks†). Prepare the booth demo, pilot installs and the PADA review. Holidays: expect delays. | Verified, or returned and fixed with no fee. |
| 9 | Dec 28 | First test begins (3-4 weeks†). Install a released version behind an installation key for pilot customers. | Pilots running. |
| 10 | Jan 4 | **Booth week (Jan 8).** Demo from a sandbox or Developer Edition org. Show the review status, not a live listing. | Booth runs on "in security review". |
| 11-12 | Jan 11, Jan 18 | First test result lands. | **Pass:** go to the listing steps below. **Fail:** fix every instance and start the follow-up review. |
| 13 | Jan 25 | **Best case:** listing approval, signed PADA, publish. | Live, about week 13. |
| 14-17 | Feb 1-22 | **Fail case:** each retest takes 2-4 weeks† plus a new $999† fee. | Retest result. |
| 18-19 | Mar 1, Mar 8 | Listing approval, signed PADA, publish. | **Live, realistic, about week 19.** |

Before publishing, listing approval and the signed PADA must both be done. Negotiate the PADA from week 1, not after the review.

For the realistic case, plan on week 19 and treat week 13 as the upside.

## 6. Maintenance calendar

- **Salesforce releases (three a year):** test each in preview sandboxes. Move API calls off any version announced for retirement.
- **Push upgrades:**
  - Build each new version on the last passed version, so it lists without a new review.
  - Test in your own orgs, then customer sandboxes for a week, then production in batches.
  - Avoid customer quarter-end and the first 3-4 weeks after a major Salesforce release.
  - Never auto-assign a new feature's permission set to existing users.
- **Re-reviews:** expect periodic ones, with the fee due†. A failed one gives about 60 days†. Keep the security contact on Company Info current. A missed re-review expires every version.
- **OAuth controls:** these were mandatory for any partner app used by more than two customer production orgs, with a May 11, 2026 deadline†. Check that your ECA complies, since Pellucid's go-live comes after that date. Refresh tokens expire after 30 idle days†. Keep the IP allowlist to 256 addresses at most†, and check its exemptions before enabling it if your egress autoscales.
- **Fees:** unpaid review fees or revenue share expire the review and pull the listing†.
- **COA duties:** only if you take the COA path. File cancellations per the PADA, usually 30+ days before renewal†, and note that COA blocks them within 5 days†.
- **Reviews:** ask customers at success milestones, never with an incentive.

## Next steps (this week)

1. Tell the CEO the date cannot be met and show the realistic date (§Bottom line).
2. Apply at the Partner Community today.
3. Confirm assumptions A4 and A5: company country and pricing. These decide Checkout versus COA.
4. Name one owner for each row in the §3 register.

† Verify every Salesforce figure (fees, revenue shares, durations, dates, deadlines) against current Salesforce partner docs before quoting it.