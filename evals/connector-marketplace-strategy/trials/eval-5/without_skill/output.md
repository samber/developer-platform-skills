# Brightloom Marketplace Rules (Draft v0.1)

**Status:** Draft for Legal review. Not yet in force.
**Owner:** TBD (see §3.1). **Applies to:** every app listed, or applying to be listed, on the Brightloom Marketplace ("Partners" and "Apps").

Bracketed values like **[10 business days]** are proposed defaults for Legal and the business to confirm. §14 lists the decisions I could not make for you.

---

## 1. Purpose and principles

The Marketplace exists so merchants can extend Brightloom safely. These rules set out what we require of Partners, what Partners can expect from us, and how we decide when something goes wrong.

1. **Merchant and customer data come first.** Transaction and customer data belong to the merchant. An App may use that data only as disclosed and as the merchant authorized.
2. **Same rules for every Partner.** Size, GMV, and commercial relationship do not change the requirements or the enforcement process.
3. **Decisions have owners.** Every decision under these rules has a named role, a written reason, and a record.
4. **Partners get notice and a hearing, except where merchants are in immediate danger.** Even then, review follows quickly.
5. **Differences in treatment must be published and objective.** Any benefit available to one Partner must be available to every Partner who meets the same published criteria.

## 2. Definitions

- **App:** software listed on the Marketplace that connects to the Brightloom platform.
- **Partner:** the legal entity that publishes an App and signed the Partner Agreement.
- **Merchant Data:** all data an App accesses or receives through Brightloom, including transaction, customer, product, and employee data, and anything derived from it.
- **Third-Party Recipient:** any entity other than the Partner that receives Merchant Data from the App, including analytics, logging, AI, and hosting vendors (subprocessors).
- **Data Flow Disclosure:** the Partner's current, complete list of Third-Party Recipients, the data categories each receives, and the purpose (see §5).
- **Security Lead:** the person responsible for Marketplace security review (§3.2).
- **Review Board:** the body defined in §3.3.
- **Suspension:** an App stays installed for existing merchants but is hidden from search and new installs, and optionally has API access limited.
- **Delisting:** the App is removed from the Marketplace. Whether existing installs keep working is decided case by case (§8.4).
- **Termination:** the Partner Agreement ends.

## 3. Who decides what

### 3.1 Marketplace Owner
A single accountable executive, the **Marketplace Owner** **[role TBD: VP Platform or equivalent]**, owns these rules, appoints the Review Board, and signs off on rule changes (§12).

### 3.2 Security Lead (emergency authority)
The Security Lead, or a designated on-call deputy, may **immediately suspend** an App if they reasonably believe either of the following:
- Merchant Data is being accessed, sent, or stored in a way that is undisclosed, unauthorized, or contrary to these rules.
- The App poses an imminent security risk to merchants or the platform.

The Security Lead needs no prior approval and does not have to consult commercial teams first. They must notify the Marketplace Owner, Legal, and the Partner within **[24 hours]** (§8.2).

### 3.3 Review Board (standing authority)
Review Board members:
- Security (chair)
- Legal
- Marketplace/Product
- Privacy or Compliance
- One Partnerships representative, **non-voting** on enforcement decisions

The Board decides on:
- Delisting, Termination, and Suspensions lasting more than **[10 business days]**.
- Appeals of Security Lead suspensions.
- Exceptions to these rules (§12.3).

**Quorum:** Security, Legal, and one other voting member. Decisions are by majority, and the chair breaks ties.

### 3.4 Decision matrix

| Action | Decides | Consults | Notice to Partner |
|---|---|---|---|
| Approve or reject a listing | Marketplace Review team | Security (if data scope is high) | With decision |
| Emergency Suspension | Security Lead | Notify Legal, Owner | Within [24h] |
| Suspension beyond [10 business days] | Review Board | Legal | Before decision, where possible |
| Delisting / Termination | Review Board | Legal, Partnerships | Written notice per §8 |
| Merchant communication on a data issue | Marketplace Owner + Legal | Security, Comms | See §8.5 |
| Paid placement and featuring | Marketplace Owner | Partnerships | Published criteria (§9) |
| Appeal outcome | Appeals Reviewer (§8.7) | n/a | Written decision |

### 3.5 Conflicts and independence
- Partnerships may advocate for a Partner but may not vote on or override any enforcement decision.
- A Board member who has a financial or relationship stake in the Partner recuses themselves.
- Commercial importance of a Partner, including its share of GMV, is **not a permitted factor** in an enforcement decision, either for or against.
- Every decision is recorded with its reasons, the rule applied, and who decided.

## 4. Listing eligibility

Partners must meet the Listing Requirements (existing page, incorporated by reference **[link]**). Additionally:

1. The Partner has signed the Partner Agreement and has a verified legal entity and security contact.
2. The App has a published privacy policy that matches the Data Flow Disclosure.
3. The App requests only the API scopes it needs ("least privilege"). Review may reject over-broad scopes.
4. The Partner submits a Data Flow Disclosure before approval (§5).
5. The Partner provides a named security contact reachable 24/7 for critical issues **[confirm feasibility for small Partners]**.

## 5. Data handling rules

These apply to all Apps and are the basis for most enforcement.

1. **Purpose limitation.** Use Merchant Data only to provide the App's functionality to that merchant, as described in the listing and privacy policy.
2. **Disclose every Third-Party Recipient** in the Data Flow Disclosure before data flows to it. Undisclosed transfers are a violation regardless of the recipient's identity or good faith.
3. **Update the Disclosure before adding or changing a recipient**, with at least **[30 days]** advance notice to Brightloom so we can notify merchants. Emergency replacement of a failed vendor may be notified within [5 business days] after the change.
4. **Merchants must be able to see recipients.** We will display a summary of the Data Flow Disclosure on the App's listing page.
5. **No sale, no advertising use, no model training** on Merchant Data, and no combining with other customers' data for the Partner's own analytics beyond what merchants authorized in the Partner Agreement **[Legal to confirm exact scope]**.
6. **Cardholder data** stays within the scope of our payment-security requirements **[reference PCI obligations; Legal/Security to specify]**.
7. **Minimization and retention.** Collect and retain only what the disclosed purpose needs. On merchant uninstall, delete or return Merchant Data within **[30 days]** unless law requires otherwise.
8. **Security baseline.** Encryption in transit and at rest, access controls, vulnerability management, and a breach-notification commitment. Partners must notify Brightloom within **[72 hours]** of becoming aware of any incident involving Merchant Data **[Legal to align with contractual and regulatory clocks]**.
9. **Audit.** Brightloom may monitor API traffic metadata, run automated and manual reviews, and request evidence (architecture diagrams, vendor lists, logs). Partners must respond within **[10 business days]**.

## 6. Ongoing compliance

1. **Annual re-attestation** of the Data Flow Disclosure and security contact by each Partner.
2. **Risk-based re-review.** Apps with broad scopes or large merchant counts are reviewed more often **[propose: annually; others every 2 years]**.
3. **Triggered review** on a material change in scopes, ownership, hosting, or recipients, or on a credible report (internal, researcher, merchant).
4. **Vulnerability reports.** Anyone may report to **[security contact]**. We investigate regardless of source.

## 7. Violation severity

| Severity | Examples | Default response |
|---|---|---|
| **Critical** | Undisclosed or unauthorized transfer of Merchant Data; active compromise; fraud; misuse of credentials | Immediate Suspension (§8.2) |
| **Major** | Missed breach notice; recipient added without notice but with merchant-aligned purpose; unresolved high-severity vulnerability past deadline; false attestation | Notice, cure period **[10 business days]**, flagged status, Suspension if uncured |
| **Minor** | Stale Disclosure, broken policy link, missing contact, listing inaccuracies | Notice, cure period **[30 days]** |

Severity is set by the decider using these criteria: type and sensitivity of data, number of merchants affected, duration, intent or concealment, remediation speed, and prior history. Repeat violations move up one level.

## 8. Enforcement process

### 8.1 Investigation
The Security Lead (or delegate) opens a case, preserves evidence (traffic captures, App versions, Disclosure on file), and assigns a case number.

### 8.2 Emergency Suspension (Critical)
1. Security Lead suspends the App. Existing installs continue by default unless continued operation endangers merchants, in which case API access is restricted.
2. Within **[24 hours]**, written notice goes to the Partner's security and legal contacts stating: the rule apparently violated, the facts known (without compromising an investigation), the scope of the Suspension, and how to respond.
3. The Partner has **[5 business days]** to respond with explanation and a remediation plan.
4. The Review Board decides within **[10 business days]** of the Suspension: lift, continue pending remediation, or move to Delisting or Termination.

### 8.3 Standard process (Major and Minor)
1. Written notice with the specific rule, the evidence summary, the required remediation, and the cure deadline.
2. Partner may respond and request an extension for good cause. The Board or its delegate decides within **[3 business days]**.
3. If uncured, escalate: Major → Suspension; Minor → Major.
4. Brightloom confirms cure in writing.

### 8.4 Delisting and Termination
- Decided only by the Review Board, in writing, with reasons.
- Delisting is the default sanction for uncured Major or confirmed Critical violations. Termination follows for willful concealment, repeated Critical violations, or failure to cooperate.
- The Board decides whether existing installs keep working, based on merchant risk. If the App stays functional, merchants are told its status.
- **Transition period:** at least **[30 days]** for merchants to migrate unless there is continuing data risk.
- Outstanding payouts: handled per Partner Agreement **[Legal: confirm treatment of withheld funds during investigation]**.

### 8.5 Merchant notification
- If a confirmed violation involved Merchant Data, the Marketplace Owner and Legal decide notification content and timing. Target is within **[72 hours]** of confirmation, subject to law and any regulator requirements.
- Merchants are told what happened, what data was affected, and what they can do. Commercial sensitivity of the Partner is not a reason to delay.
- Brightloom may notify regulators where required.

### 8.6 Partner recourse
Partners may:
1. Respond in writing at each notice stage.
2. Submit evidence, including independent assessments.
3. Request an extension for cure.
4. Appeal under §8.7.
5. Seek relief under the Partner Agreement's dispute clause **[governing law, venue, and any arbitration: Legal]**.

### 8.7 Appeal
- Filed within **[10 business days]** of a Board decision to Delist, Terminate, or continue a Suspension.
- Decided by an **Appeals Reviewer** not involved in the original decision **[proposed: General Counsel or a senior executive outside Marketplace, Security, and Partnerships]**.
- Reviewer may uphold, modify, or reverse, and issues a written decision within **[15 business days]**.
- The App stays suspended or delisted during appeal unless the Reviewer orders otherwise, except where reversal is clearly warranted by new evidence.

### 8.8 Records and transparency
- Maintain a case file per action. Partners can request their own file.
- Publish an annual aggregate **Marketplace Integrity Report** (number of reviews, suspensions, delistings, appeals, outcomes) without naming Partners unless a Partner consents or the action is public.

### 8.9 Limits on Brightloom's authority
- Enforcement actions must cite a rule in this document or the Partner Agreement.
- We do not delist for competitive reasons, commercial disputes, or Partner criticism of Brightloom.
- Reasonable suspicion, not proof, suffices for emergency Suspension. Excessive or bad-faith use is reviewable by the Board and appealable.

## 9. Placement, featuring, and commercial terms

This section exists so that no Partner, whatever its size, can obtain special treatment outside these rules.

### 9.1 Organic ranking
Search and category ranking uses published factors **[propose: relevance, merchant ratings, install retention, support responsiveness, compliance standing]**. Partner revenue, GMV, or negotiated status is not a ranking factor. Apps under Suspension or with open Major violations are excluded from featured placements.

### 9.2 Homepage and featured placement
1. Brightloom publishes the **placement criteria** and rotation schedule **[e.g., quarterly editorial slots chosen on merchant value, quality, and fit; plus a small number of clearly labeled paid slots]**.
2. Any paid or sponsored placement is **labeled** to merchants and offered to all eligible Partners on the same rate card.
3. No permanent or exclusive homepage placement. Slots are time-limited and re-decided.
4. The Marketplace Owner decides placement. Partnerships may nominate but not guarantee.

### 9.3 Commercial terms and tiers
1. Standard revenue share, fees, and payment terms are defined in the Partner Agreement.
2. Preferential terms are available **only through published program tiers** with objective criteria (e.g., merchant count, retention, security certifications, support SLAs). Any Partner meeting the criteria receives the tier.
3. Bespoke terms outside a tier require Marketplace Owner and Legal approval, written justification, and an exception log. Material terms must be offerable to similarly situated Partners **[Business: confirm]**.
4. **No exclusivity** and no terms that restrict a Partner from listing on other platforms or restrict Brightloom from listing competing Apps **[Legal/Business confirm]**.
5. **Terms do not buy forbearance.** No commercial benefit, tier, or placement reduces a Partner's obligations or enforcement exposure under these rules.

### 9.4 Concentration risk
The Marketplace Owner reports quarterly to the executive team on Partner concentration (share of GMV, installs, and merchant-critical functionality per Partner), and on contingency plans if a major App is suspended. This is internal governance, not a Partner right.

## 10. Brightloom-owned and affiliated Apps
Apps built or owned by Brightloom or its affiliates follow the same rules, review, and enforcement. They carry a visible label. Brightloom may not use non-public Partner data or analytics to design competing Apps **[Legal: confirm commitment]**.

## 11. Confidentiality and reporting
- Enforcement records are confidential except as required for merchant notification, regulatory obligations, or legal proceedings.
- Partners may not retaliate against a person who reports a violation in good faith. Brightloom will not disclose a researcher's identity without consent, except as required by law.

## 12. Changes to these rules

1. The Marketplace Owner, with Legal, may amend the rules.
2. **Notice:** at least **[30 days]** before material changes take effect, via email to Partner contacts and a changelog. Changes required by law or an urgent security need may take effect sooner with explanation.
3. **Exceptions** to a rule require a written Board decision, a time limit, and an entry in the exception log. No exception may waive §5 (data handling) or §8 (process).
4. Version history is public.

## 13. Relationship to other documents
These rules supplement the Partner Agreement and Listing Requirements. If they conflict, the Partner Agreement controls, except that §3 (authority) and §8 (process) are intended to be **incorporated into the Partner Agreement**. **[Legal: confirm the incorporation mechanism and whether existing Partners must re-sign or accept via click-through with notice.]**

## 14. Decisions and checks for Legal and the business

1. **Binding force.** How do these rules reach the existing ~180 Partners? Options are an amended Partner Agreement or acceptance with notice. The two large Partners may negotiate, so decide now what is non-negotiable. I suggest §3, §5, and §8.
2. **Emergency suspension without prior notice.** Confirm existing contracts permit it. If not, the amendment above must cover it.
3. **Liability and indemnity** for Brightloom's good-faith enforcement, and for Partner data violations. This is left entirely to Legal.
4. **Regulatory mapping.** Controller/processor roles for Merchant Data and end-customer data, applicable privacy laws, and breach-notice clocks. Align the [72h] timelines.
5. **Payment-card scope.** Confirm PCI-related obligations and who certifies what.
6. **Withheld payouts** during investigation.
7. **Appeals Reviewer** identity and independence.
8. **Review Board staffing** and Security Lead on-call capacity. These powers are meaningless without a named person at 2 a.m.
9. **Numbers.** All bracketed periods are proposals. Stress-test the cure periods with Security.
10. **Partnerships' role.** I made them non-voting to protect against the two large Partners' leverage. Expect pushback and confirm the executive sponsor will hold the line.
11. **Existing incident.** The app found forwarding transaction data should be handled under this framework once it is in force, or under existing contract terms in the meantime. Do not apply these rules retroactively without Legal's sign-off. Confirm whether merchants affected have been told, and whether notification obligations have already been triggered. That may be time-sensitive regardless of this document.

---

### Notes on design choices

- **The 61% concentration is why §3.5 and §9 exist.** Written authority and objective criteria protect Brightloom from being pressured case by case, and protect the two Partners from arbitrary action. They give you a defensible reply to "why not us?": the terms are published and anyone who meets them gets them.
- **Two-tier authority.** One person can act in an emergency, but only a Board can end a Partner's business. That split is what makes the emergency power defensible.
- **Undisclosed recipient is a violation regardless of intent.** This makes the rule enforceable without proving bad faith, and the cure for non-malicious cases is simply a fast disclosure update.
- **Not included yet:** a Partner-facing summary (one page), the Disclosure form template, and the Board's internal runbook. I'd draft those after Legal's first pass.