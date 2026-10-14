# Brightloom Retail Marketplace Rules (Draft v0.1 for Legal review)

## Status and assumptions

I could not run the interview, so this draft rests on the assumptions below. Please correct any that are wrong, because each one changes a section.

| # | Assumption | What changes if wrong |
|---|---|---|
| A1 | The marketplace stays. It is live with about 180 apps, so the build, join or buy gate is already decided. | Not applicable. |
| A2 | Apps touch customer transaction data, so data sensitivity is **high**. | If medium, §3 can drop to a hybrid ladder for low-risk apps. |
| A3 | The marketplace is mainly a retention and ecosystem lever, not a revenue line. | If revenue is the goal, §5 needs rework. |
| A4 | Billing runs partly or fully through Brightloom. | If not, the take-rate and anti-circumvention clauses in §5 are moot. |
| A5 | Brightloom can staff a standing security and partner-quality function. | If not, §3 admission has to be narrowed. |

**Placeholders.** Anything in `[brackets]` is a number or name I could not know. I did not invent any rates, fees, or SLAs.

**Legal scope.** This is an operating-rules document, not a contract. Legal still has to map it onto the partner agreement, the DPA, and PCI and privacy obligations.

---

## 1. Purpose and principles

**Purpose.** The marketplace gives Brightloom merchants trusted, useful integrations and gives partners fair access to them. [Owner decision A3: state here whether it is primarily a retention asset or a revenue line.]

**Principles**
1. Merchant data belongs to the merchant. Partners hold it only for the purposes disclosed to the merchant.
2. Every partner gets the same published rules. There are no side letters on placement, ranking, enforcement, or removal.
3. Every enforcement action has a named decider, a written reason, and a defined route to challenge it.
4. Paid visibility is always labeled.
5. Rules are reviewed on a schedule, not set once (§9).

## 2. Definitions

- **App:** any partner-built integration listed in the marketplace.
- **Partner:** the legal entity that owns and operates an App.
- **Merchant data:** any data from a Brightloom tenant, including transaction, customer, and product data.
- **Subprocessor:** any third party that receives merchant data from an App, directly or indirectly.
- **Listed:** the App is visible and installable.
- **Certified:** the App has passed the higher bar in §3 and carries the badge.
- **Suspended:** the App is hidden from new installs. Existing installs are either paused or continue, as the decision states.
- **Delisted:** the App is removed and its API credentials are revoked.
- **Marketplace Trust Lead (MTL):** the named person accountable for enforcement decisions (§6). [Name or role.]
- **Marketplace Review Board (MRB):** the standing panel for appeals and policy decisions (§6). [Seats: Security, Legal, Partner Management, Product. No seat is held by anyone who owns a partner's commercial relationship.]

## 3. Admission: who gets in

**Position.** Because Apps can read transaction and customer data (A2), the default is a **single review gate with post-approval monitoring**. Every new listing is reviewed before it exists. A looser "open plus certified tier" ladder is available only for Apps that never receive merchant data (§3.4).

### 3.1 Review stages (all Apps that receive merchant data)
1. **Completeness.** The listing is accurate, the support contact works, and the privacy policy is published.
2. **Data-handling compliance.** The Partner submits a data-flow declaration listing every field read, why it is needed, where it is stored, and **every Subprocessor** with its purpose and location.
3. **Security testing.** Testing covers OWASP Top 10 and OAuth scope minimization. Unused or excessive scopes are removed before approval.
4. **Contract.** The Partner accepts the Partner Terms, including the data and enforcement clauses in this document.

### 3.2 Standing obligations after approval
- **Disclosure of change.** The Partner must submit a new data-flow declaration, and re-review is triggered, before it does any of the following:
  - adds a Subprocessor;
  - adds a data field or scope;
  - changes how data is used.
- **Annual re-attestation.** The Partner re-attests its declaration every 12 months.
- **Ongoing monitoring.** Brightloom may review API behavior against the declaration. Examples: outbound destinations, volume anomalies, and scopes used versus granted. [Define what telemetry Brightloom can legally and technically see.]

### 3.3 Certified tier (optional badge)
Certified is a separate, higher bar with quantitative gates:
- API success rate of at least [x]%;
- a security questionnaire;
- maintenance evidence within [x] days;
- a review-quality threshold.

Losing certification removes the badge only. It does not remove the listing. Only the enforcement ladder in §6 removes a listing.

### 3.4 Lower-risk path
Apps that receive **no** merchant data may use a lighter automated check plus the standing obligations. Only the Security team can classify an App this way.

### 3.5 Capacity
Review is a standing function with a published turnaround target of [x business days]. [Staffing decision A5.]

## 4. Discoverability: who gets seen first

Admission and visibility are separate.

1. **Organic ranking.** The default ranking uses install-based signals, merchant reviews, Certified status, and catalog freshness. It never uses commercial relationship size.
2. **Paid or featured placement.** Homepage or promotional slots are allowed under four conditions:
   - They are clearly labeled "Sponsored" or "Featured by Brightloom".
   - They are available to any Listed App that meets the published criteria, on the same published terms.
   - They are time-limited, with a published rotation.
   - Where a slot is editorial, the selection criteria are published.
3. **No exclusivity.** Brightloom does not grant a single Partner permanent or exclusive homepage placement, in exchange for any commercial term.
4. **Placement and security status.** An App under an open Suspension or Delisting process is ineligible for featured placement.

## 5. Value split and commercial terms

Commercial terms below are placeholders. They are a framework for owners to fill in.

1. **Published schedule.** All fees and revenue share are in one published schedule. [Take-rate level, tier axis, and any fee stack. Recommended default while the marketplace is still building supply: zero or volume-tiered, with 0% under a revenue threshold.]
2. **Preferential terms.** Brightloom may offer different terms only through **published program tiers** with objective criteria that any Partner can meet. Examples: revenue band, Certified status, or hosting and architecture model. Bespoke terms outside the schedule need MRB approval and a written rationale.
3. **Notice of change.** Fee and revenue-share changes require a minimum of **[6] months' written notice**. Changes favorable to Partners may take effect sooner. Unfavorable ones are never retroactive.
4. **Anti-circumvention.** If Brightloom takes a share of Partner revenue (A4), a Partner may not route billing around the marketplace to avoid it. Violation is an enforcement event under §6.
5. **Pooled scale.** Brightloom provides shared analytics and shared marketing programs to smaller Partners, so scale benefits do not accrue only to the largest. [List the first two programs and owners.]
6. **Concentration guardrail.** If the top two Partners exceed a set share of marketplace GMV, the MRB reviews terms and placement, even if no complaint exists. Today it is **61%**. [Set the trigger threshold. Suggestion: review at 50% and escalate at 60%.]

## 6. Enforcement and conflict resolution

### 6.1 Decision authority
| Action | Decider | Consulted | Notice to Partner |
|---|---|---|---|
| Emergency Suspension (§6.3) | MTL, or Security on-call if the MTL is unreachable | Legal (afterwards if urgent) | Immediate, with reason within 24 hours |
| Standard Suspension | MTL | Security, Legal | See ladder |
| Delisting | MRB (majority) | MTL, Legal | See ladder |
| Policy exceptions | MRB | Legal | Recorded in the decision log |

**Conflict-of-interest rule.** Nobody who manages a Partner's commercial relationship decides or votes on enforcement against that Partner. Account managers may provide input only.

### 6.2 Violation classes and the ladder
| Class | Examples | Remedy ladder | Cure time |
|---|---|---|---|
| **A: Critical** | Undisclosed transfer of merchant data to a third party; confirmed breach or credential misuse; deceptive data practices | Emergency Suspension, then Delisting if not cured | Remediation plan within [x] days; cure within [x] days |
| **B: Serious** | Undeclared Subprocessor with no evidence of misuse; scope abuse; anti-circumvention; missed critical patch | Written notice, then Suspension, then Delisting | [14] days |
| **C: Standard** | Stale listing; missed re-attestation; support failures; low API success rate | Warning, then loss of Certified badge, then Suspension | [30] days |

### 6.3 Emergency Suspension
- Allowed only for Class A where continued operation risks merchant data or trust.
- The Partner is told immediately and given a written reason within 24 hours.
- Merchants are told within [x hours] if their data may be affected. [Legal to define notification duties and thresholds.]
- The MRB reviews the Suspension within **[3] business days**. It either confirms it, converts it to the ladder, or lifts it.

### 6.4 Partner recourse
1. **Written statement.** Every enforcement action states the rule broken, the evidence summary, the remedy required, and the deadline.
2. **Response.** The Partner may respond within [7] days (2 days for Emergency Suspension).
3. **Appeal.** The Partner may appeal to the MRB. The MTL who made the original decision does not vote. A decision is issued within [10] business days.
4. **Reinstatement.** After the cure is verified, the Partner may request reinstatement. The standard is fixed in the decision, and the clock is [x] days.
5. **Beyond appeal.** The Partner Terms govern further remedies. [Legal to complete: dispute resolution, liability, and the Partner's rights on merchant data on termination.]

### 6.5 Merchant protection on removal
- Merchants get [30] days' notice for a standard Delisting. For Class A, the connection is cut immediately.
- Data deletion at the Partner is required within [x] days and must be confirmed in writing.
- Brightloom publishes a short, factual explanation for Delistings. It does not publish confidential security detail.

### 6.6 Transparency
Brightloom publishes a **quarterly enforcement summary** with counts by class and outcome, with no partner names unless the Partner consents or the law requires it.

## 7. Treatment of the open data-forwarding case

Per policy, this App is handled under §6 like any other, regardless of Partner size or revenue.

1. **Immediate.** The MTL classifies it Class A or B, based on whether merchant data actually reached the undisclosed vendor, and issues an Emergency Suspension if A. [Needs facts from Security.]
2. **Within [7] days.** Brightloom determines which merchants were affected. Legal decides whether notification duties are triggered.
3. **Within [30] days.** Run a **fleet audit of all ~180 Apps**: compare each App's declared data flows and Subprocessors against observed outbound traffic. Findings go through the same ladder.
4. **Ongoing.** Apps found in the same condition get the same treatment, with no exceptions for the two large Partners.

## 8. How the two large Partners' requests are handled

Brightloom answers these requests with policy:
- **Preferential terms:** available only through published tiers (§5.2). If both Partners would qualify for a tier, then any Partner meeting the same criteria qualifies too.
- **Homepage placement:** available only as labeled, criteria-based, time-limited placement (§4). No exclusivity and no placement guarantees in exchange for volume.
- **Bargaining position:** Brightloom's concentration guardrail (§5.6) and pooled-scale programs (§5.5) reduce its dependence on the two Partners. Product and Partnerships should also measure how much of each Partner's volume would still reach Brightloom through direct merchant relationships. [Open item.]

## 9. Governance of the rules

- **Rules owner:** [name or role]. **MRB chair:** [name or role].
- **Review cadence:** the MRB reviews this document **every 6 months**, and after any Class A event.
- **Changes to these rules:** [90] days' notice to Partners. Security-driven changes can take effect sooner, with the reason published.
- **Version log:** every change is recorded with date, author, and reason.

## 10. Traceability: why each rule exists

| Market-failure cause | Rules that address it | Gaps |
|---|---|---|
| **Information asymmetry:** Partners know where data goes, merchants don't. | Data-flow declaration (§3.1), change disclosure (§3.2), labeled placement (§4), quarterly summary (§6.6) | Merchants cannot yet see a Partner's declared Subprocessors in the listing. **Recommend adding this to listing pages.** |
| **Externalities:** one App's breach hurts trust in all of them. | Security testing (§3.1), monitoring (§3.2), Emergency Suspension (§6.3), fleet audit (§7) | None identified. |
| **Monopoly power:** two Partners hold 61% of GMV, and Brightloom itself could extract. | Published tiers (§5.2), no exclusivity (§4.3), concentration guardrail (§5.6), pooled scale (§5.5), conflict-of-interest rule (§6.1) | Brightloom's own conduct is only partly covered. **Consider publishing its own commitments on data use and self-preferencing.** |
| **Risk:** Partners fear arbitrary removal and merchants fear data loss. | Decision authority (§6.1), notice and cure (§6.2), appeal (§6.4), merchant protection (§6.5) | None identified. |

## 11. Metrics (track from the first quarter)

Baseline against your own first quarter. Do not copy another platform's numbers as targets.

- **Supply side, which fails first:**
  - active Partners with a live listing;
  - time from signup to first listing;
  - share of catalog updated in the last two quarters;
  - **top-2 Partner GMV share** (61% today).
- **Trust and enforcement:**
  - Apps with a complete data-flow declaration (target 100% within [x] days);
  - mean time to enforcement decision;
  - appeals and their outcomes.
- **Demand side:**
  - share of merchants with at least one installed App;
  - integrations per account, watching the 4+ cluster;
  - the retention delta above and below that cluster.
- **Flywheel coupling:** deals and churn saves where integrations were cited. Attribution is soft, and the document should say so.

---

## Decisions I need from you

Please answer these in order, since each affects the next.

1. **A2:** Do Apps receive customer transaction data in general, or only some of them? That sets whether §3 is a full gate or a ladder.
2. **A3 and A4:** Is the marketplace a revenue line or a retention lever, and does billing flow through you today? That sets §5.
3. **Authority (§6.1):** Who holds the MTL and MRB seats? Nothing in §6 works until these are named people.
4. **Incident facts:** Did transaction data actually reach the analytics vendor, and what is the App's current status? That sets §7 and any notification duty.
5. **Placeholders:** The `[x]` values (notice periods, cure windows, SLAs) need owners. Legal and Security can set the first draft.

**Next steps.** Legal reviews §3.2, §6.3 to §6.5, and §7 first, because they carry the most legal exposure. Security confirms what monitoring in §3.2 is technically and legally possible. Then I can turn this into a Partner Terms addendum and a shorter public version.