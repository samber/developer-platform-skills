# Verdict: don't sign off on this plan

The fairness goal is right, but the mechanism doesn't deliver it, and it creates a security and liability problem on top. I'd fix four things before launch.

## What's wrong

**1. A single bar treats unequal risk as equal.**
- An app that reads the installing admin's own records and an app that reads the whole vendor list and every employee's expense reports carry very different risk.
- One questionnaire for both is either too heavy for the first, which slows the launch, or too light for the second, which is the dangerous failure.
- Uniform *criteria* are fair. Uniform *depth* isn't. Favouritism means applying different standards to apps with the same risk. It doesn't mean applying stricter standards to riskier apps.

**2. A self-filled questionnaire can't carry the word "Verified."**
- Nobody at Ledgerline has checked the answers.
- Customers will read "Verified" as "Ledgerline vetted this." After an incident, that gap is a trust problem and likely a legal one.
- Either do some verification or use a label that matches what you did, such as "Self-attested."

**3. The badge is a one-time snapshot.**
- Apps change scopes, subprocessors, owners and code after submission, and a badge earned in month 1 still shows in month 18.
- A badge that never expires or gets revoked is the one customers will trust most when they shouldn't.

**4. A binary badge on every listing carries no information.**
- If all 60 launch apps are "Verified," the badge distinguishes nothing, and it hides the one thing an admin needs: *what this app can see.*

**5. The warning banner is the wrong control for the real risk.**
- Banners on install screens get clicked through.
- Identity of the vendor isn't the issue. The issue is the *permission*.
- Today, a single installing admin can apparently grant org-wide access to employees' expense reports (personal data) with one click. The plan has no control for that at all.

## What I'd do instead

1. **Tier by data access, not by app.**
   - **Tier 1, own records only:** questionnaire plus automated checks (OAuth config, TLS, scope list).
   - **Tier 2, org-wide, low-sensitivity:** Tier 1, plus evidence such as a SOC 2 or ISO 27001 report, or a recent pen-test summary.
   - **Tier 3, org-wide vendor list or all employees' expense reports:** Tier 2, plus a Ledgerline review of the actual scopes requested, a named security contact, an incident-notification SLA, and a subprocessor list.
2. **Publish the criteria and apply them identically**, including to any Ledgerline-built or partner-favoured apps. That is the real answer to "we don't want to look like we play favourites."
3. **Show what the app accesses on every listing.**
   - Plain-language scopes and the tier, instead of one badge.
   - Rename the badge to describe what happened: "Security reviewed, Tier 3, reviewed 2026-10."
4. **Build consent controls for sensitive scopes.**
   - Granular OAuth scopes with least privilege.
   - Org-wide sensitive scopes need a finance-admin or owner role, not any admin.
   - Customer-level policy to restrict or allowlist installs.
   - Audit log of installs and API access, and one-click revocation.
   - A platform kill switch for a compromised app.
5. **Expire and re-check.**
   - Re-attest annually, and re-review on any scope increase.
   - Remove the badge automatically when it lapses.
6. **Replace the banner with a gate.** Unreviewed apps shouldn't be able to request Tier 3 scopes at all. For lower tiers, an unreviewed app can be installable but visibly labelled as unreviewed.

## Launch implications

- **Launch with fewer than 60 apps if needed.** A smaller directory where Tier 3 apps are actually reviewed beats 60 with a meaningless badge.
- **Check review capacity.** Tiering lets you spend review time where the risk is. If you have no one to do Tier 3 reviews, you shouldn't list Tier 3 apps yet.
- **Get legal input.** Employee expense reports are personal data. You need to know who is processor and who is subprocessor in the chain Ledgerline → customer → app, and what your DPA and customer contracts promise.

## What I need to know to firm this up

1. How many of the 60 apps would request org-wide vendor-list or all-employee expense scopes?
2. Who has Tier 3 review capacity, and how many reviews a week can they do?
3. Do your OAuth scopes already separate "own records" from "org-wide," or is that new work?

If the answer to #3 is "new work," that's the launch blocker, not the badge.