# Veriquil Marketplace: Quality Bar and Placement Design

## Recommendation

1. **Don't launch open with no review.** Gate every app by the data it can read. An unreviewed app that touches patient records is a liability for you and for your customers.
2. **Don't sell the "Featured" slot.** Selling it turns a trust signal into an ad. Sell a clearly labeled sponsored slot instead, open only to apps that already pass the bar.
3. **Fix supply with onboarding and economics, not by dropping review.** Details are in section 4.

## 1. Why "we review nothing" fails here

I used the open-versus-curated test from the developer-ecosystem playbook. It says to curate when brand damage risk is high (regulated, security-sensitive) and when review volume is small enough to handle by hand. Both apply:

- **Regulated data.** Even de-identified records can be re-identified when joined with site financials and protocol deviation logs. Customers (CROs and sites) are the data controllers. They will ask "who vetted this?" in every security questionnaire. "Nobody" ends deals.
- **Regulated process.** Deviation logs and trial data feed GxP and 21 CFR Part 11 workflows. An app that writes back or alters them can put a customer's trial at risk of failing inspection.
- **Volume is small.** You have four launch partners. Human review is not a bottleneck at that scale, and tooling can carry it later.
- **Post-publication moderation doesn't work.** The open model removes spam after it goes live. A data leak can't be undone after the fact.
- **The supply argument is weak.** An open door doesn't create apps. Developers in this field build where there is a sandbox, a clear API, customers, and a path to revenue. A "no review" policy can also keep out the serious vendors you need, because their own compliance teams won't list on an unvetted store.

Position this to your head of product as "open to apply, tiered by access." Anyone can publish. What an app can touch determines how much review it gets. That keeps her supply goal and fits the risk.

## 2. Quality bar

### Tiering by data scope

| Tier | Data access | Review | Typical time |
|---|---|---|---|
| **T0: Sandbox** | Synthetic data only. Never live customer data. | Automated checks only. | Instant |
| **T1: Low-risk** | Aggregate or non-sensitive data, such as UI widgets or reports on non-patient, non-financial data. | Automated scan plus a light manual check. | ~3 business days |
| **T2: Sensitive** | De-identified patient records, site financials, or deviation logs (read-only). | Full review (below). | ~2-4 weeks |
| **T3: Write-back** | Any app that writes, updates, or triggers actions in the system. | Full review plus a validation package. | Case by case |

Anyone can reach T0 on day one. This gives you supply-side velocity without exposing real data.

### Requirements for T2 and T3 (the bar)

**Security and privacy**
- Security attestation. Accept SOC 2 Type II or ISO 27001, or complete a security questionnaire plus a pen-test summary from the last 12 months.
- Signed data processing agreement and a signed marketplace agreement. The agreement bans re-identification attempts, secondary use, model training on customer data, and resale of data.
- Declared data scopes, with least-privilege OAuth. The app requests only the scopes it needs. Customers see each scope in plain language at install.
- Encryption in transit and at rest. Declared data residency and subprocessors. Data isn't retained after uninstall, with a documented deletion timeline.
- No customer data sent to third-party AI or analytics services unless it is declared and the customer opts in.

**Regulatory fit**
- Documented HIPAA/GDPR posture where relevant.
- For T3 only: audit trail for every write, and a validation summary customers can use in their own computer-system validation (CSV) documentation. Note that Part 11 compliance of an app depends on the customer's use. Don't promise it on the vendor's behalf.

**Functional quality**
- Passes automated API conformance and error-handling tests in a staging tenant with synthetic data.
- Documented install, uninstall, and permission-revocation behavior.
- Support contact with a stated response time. For security issues, a named contact and a 24-hour acknowledgment commitment.
- Clear pricing and terms shown on the listing.

**Ongoing obligations**
- Re-review on any scope change or major release (new scopes trigger review before release).
- Annual re-attestation. Lapsed attestations suspend the listing.
- Incident notification to Veriquil within 24 hours of a suspected breach. The marketplace agreement lists the consequences.
- Kill switch. Veriquil can suspend an app tenant-wide, and customers can revoke it individually.

### Review process

1. Self-serve submission through a checklist. Most T2 rejections should happen here, from automated checks.
2. Automated checks: scope diff, dependency vulnerability scan, API conformance on synthetic data.
3. Human review by security plus one product owner, using a written rubric with pass/fail criteria and published reasons for rejection. Publish SLA targets and hold to them. A slow review recreates the supply problem.
4. Post-listing monitoring: anomaly detection on API access volume per app, plus customer reports.

Staffing note: the four launch partners are your calibration set. Review them thoroughly and write the rubric as you go. Estimate roughly 1-2 people part-time at launch. Revisit once the queue passes ~10 submissions a month.

## 3. Placement design

### Principle

Placement is a trust signal. In a regulated store, customers read "featured" as "Veriquil vouches for this." Selling it breaks that meaning and creates legal and reputational exposure. If a featured app later causes a breach, "it was a paid slot" is a bad answer to customers and regulators.

### Slots

| Slot | Who gets it | How | Paid? |
|---|---|---|---|
| **Veriquil Verified badge** | Apps that pass T2/T3 review | Automatic on passing. Revoked on lapse. | No |
| **Editor's Picks (homepage)** | Apps chosen by Veriquil | Written criteria: customer adoption, ratings, security record, fit with customer needs. Rotate quarterly. | No |
| **Launch spotlight** | New apps passing T2 review | Free, 30 days, first come within queue. This rewards early partners and costs nothing. | No |
| **Category and search ranking** | All listed apps | Ranked by relevance, active installs, ratings, support responsiveness. Never by payment. | No |
| **Sponsored placement** | Verified apps only | Labeled "Sponsored." Separate row, never inside Editor's Picks or search ranking. | Yes |

### Rules for the paid slot

If she still wants revenue from placement, use these rules:

1. **Eligibility.** Only apps with the Verified badge and a clean security record can buy it. Payment never substitutes for review.
2. **Label.** Visible "Sponsored" on the tile and in any API or email that repeats it.
3. **Separation.** Not on the "Featured" or "Editor's Picks" row. Paid slots never use trust language.
4. **Pricing.** Don't anchor on $5,000 a quarter without testing. With four partners and no install base, the slot has little value to sell yet. Price it after you have traffic data. Pilot with launch partners at a discount or in exchange for case studies.
5. **Revocation.** Any security incident or lapsed attestation pulls the placement immediately, with a pro-rated refund.
6. **Conflict.** Veriquil reviewers have no knowledge of who is a paying sponsor.

Check with counsel on disclosure obligations before launch.

### Funding the program without selling trust

These alternatives fund the program with less risk than paid featuring:

- **Revenue share** on paid apps (typically 10-20%). It aligns your incentive with customer success.
- **Annual listing and certification fee** for T2/T3 apps. It covers review cost and also filters out low-commitment publishers. Waive it for launch partners in year one.
- **Premium partner program.** Paid co-marketing (webinars, case studies, joint events) that doesn't affect ranking or trust badges.
- **Customer-side value.** CROs and sites may pay for marketplace-enabled tiers or add-ons.

## 4. Fixing the supply constraint

Four committed partners is a thin start. Open review doesn't change that. These do:

1. **Make the first 90 days about partner success.** Pair each of the four launch partners with a named engineer. Publish their case studies. Social proof pulls in the next ten.
2. **Provide a good sandbox.** Synthetic trial data, a full API, and sample apps, so a developer can build without a customer contract or legal wait.
3. **Reduce review friction instead of removing review.** Publish the checklist and a pre-submission self-test. Pre-approve common security attestations. Offer a fast lane for apps with SOC 2.
4. **Source supply directly.** Recruit from adjacent vendors already selling into CROs and sites (eCOA, EDC, finance and analytics tools), and from customers' internal teams building their own integrations. Customer-built private apps can use T1/T2 review for internal use only.
5. **Set the metric.** Track apps submitted, apps approved, median review time, and installs per approved app. If review time stays under your SLA and submissions are still low, the problem is demand or incentives, not the review gate.

## 5. Decisions to make

1. Approve the tiered model in place of "no review." It keeps her open-submission principle, since anyone can apply, but gates what an app touches.
2. Remove "Featured" as a paid product. Rename and relabel any paid slot as "Sponsored."
3. Name the owner of the review rubric and the SLA (suggest security lead plus product).
4. Have legal confirm DPA terms, marketplace agreement, and sponsorship disclosure.
5. Revisit the model at 6 months, with data: submissions, rejections by reason, review time, installs, incidents.

If you want, I can draft the one-page version for the head of product, which leads with her goal (supply) and shows how this protects it.