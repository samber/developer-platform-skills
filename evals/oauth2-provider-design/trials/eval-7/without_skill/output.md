**Verdict: don't sign off.** The idea of a trust signal is right. The design has four problems, and the first is serious.

## What's wrong

**1. One badge at one bar cannot be both honest and reachable.**
- Apps differ in risk. Some read the installing admin's own records. Others read the whole vendor list and every employee's expense reports.
- A single bar has to sit at one of two levels.
  - **Set it low**, to be fair to small apps. "Verified" then means almost nothing on the apps that matter most. A customer reads the badge as "Ledgerline vouches for this", and that is a false statement for a broad-scope app.
  - **Set it high**, to be safe for broad-scope apps. You will turn away small, low-risk apps, or review them far more heavily than they need.
- Spend-management data is sensitive. It covers vendor pricing, employee reimbursements, bank details and possibly payroll-adjacent information. A breach through a "Verified" app lands on Ledgerline's brand and could create liability, because you advertised vetting.

**2. A questionnaire filled in once is self-attestation, not verification.**
- The word "Verified" claims that someone checked. A questionnaire the app's own vendor fills in checks nothing.
- With about 60 apps at launch, you will get optimistic answers and no evidence behind them.
- Once at submission means the badge never expires. Apps change owners, add scopes, get breached and ship new code. A badge earned in month 1 is still shown in month 18.
- The user-facing wording makes it worse. The badge reads as a vouch, but your legal position is probably "we asked and they said yes". Resolve that gap before launch.

**3. "Same bar for everyone" confuses equal treatment with fairness.**
- Applying one rule to apps with different risk is not even-handed. It mistreats the two ends:
  - Low-risk apps pay compliance cost they don't need.
  - High-risk apps get less scrutiny than they need.
- Favouritism means applying different standards for reasons unrelated to risk, such as partner deals or friendships.
- Tiering by data access is a neutral, published rule, and it is easy to defend. A customer or app vendor who asks "why does this app get more scrutiny?" can be given a one-line answer: "because it can read X."

**4. A warning banner on unverified apps pushes people to the wrong place.**
- If a badge is nearly universal, unverified apps are rare. The banner then reads as an accusation, and small, harmless apps get punished.
- Meanwhile every verified app, including the high-risk ones, looks equally safe.
- The banner also fires at install time, when the admin has already decided. The information that matters is what the app can read, and the banner doesn't say that.

## What I would sign off on instead

1. **Tier by data access, not by app.** Use the OAuth scopes the app requests. Publish the tiers.
   - **Tier 1, own-records only** (the installing admin's own data). Lightweight review: questionnaire plus automated checks, such as scope validation and a basic security scan.
   - **Tier 2, org-wide read** (vendor list, all employees' expenses). Needs evidence, not claims: SOC 2 Type II or ISO 27001 report, a pen-test summary, a data-processing agreement and a named security contact. Add a manual review of your own.
   - **Tier 3, write or payment actions.** Everything in Tier 2, plus a stricter review and contractual incident-notification duties.
   - Treat the scope list as the source of truth. If an app asks for broader scopes later, it drops back to review. Don't let the app self-select its tier.

2. **Badge what was actually checked.**
   - Show the tier and the scopes on each listing: "Reads: your vendor list and all expense reports. Reviewed: SOC 2 report, pen test, 2026-09."
   - If you only collect a self-attested questionnaire, use "Self-assessed" and say so. Reserve "Verified" for apps where you reviewed evidence.

3. **Make the badge expire.**
   - Re-verify annually.
   - Re-verify on any scope change, change of ownership or reported incident.
   - Define a suspension path, including a way to remove the badge fast, and write it into the listing terms now. That is much cheaper than negotiating it after an incident.

4. **Replace the banner with a scope disclosure on the install screen.**
   - Show plain-language permissions and the tier before the admin consents.
   - Add a stronger confirmation step for Tier 2 and 3, such as "This app will read every employee's expense reports", with a named approver in the customer's org.
   - Keep a lighter notice for unreviewed apps. Don't use alarm language for them.

5. **Cap what you promise at launch.**
   - With about 60 apps, you probably can't manually review all of them by launch.
   - Launch Tier 1 apps with the light process. Hold broad-scope apps back until their review is done, or label them "Not yet reviewed" and disable org-wide scopes meanwhile.
   - Staff the review queue before launch. Name an owner, because reviews, re-verification and incident handling are permanent work.

## Open questions before you finalize

- **Which of the 60 apps need org-wide scopes?** If it's 5, a manual review is cheap. If it's 40, the staffing plan changes.
- **Who owns reviews, and what happens when an incident hits a verified app?** Without an owner and a suspension path, the badge is a liability.
- **Does Legal agree on what "Verified" is allowed to claim?** Ask before launch, not after.
- **Do you have customer commitments** (SOC 2 scope, DPA terms, regulated customers) that say what you must review for third parties with access to their data? Check them.

I can draft the tier definitions, listing copy and install-screen wording next if you want them.