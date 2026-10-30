**Recommendation: do not announce "fully supported by Glimmerdeck." Announce "certified connectors are backed by a support guarantee," where Glimmerdeck owns the front door and the partner owns the fix.**

Next action: send the head of partnerships the wording in section 5 and the rule in section 1. The rest of this answer is the model behind them.

I assumed three tiers, because you didn't list yours: uncertified, certified, and a top tier. Rename them to match yours.

## 1. Core rule: split "support" into three duties

- **Front door.** The customer files with Glimmerdeck. Glimmerdeck always answers.
- **Triage.** Glimmerdeck decides whether the defect is in the platform or in partner code. Glimmerdeck proves it with a repro.
- **Fix.** The owner of the defective code fixes it. For partner code, that is the partner.

"Fully supported" promises all three. A 30% partner-bug share then becomes your cost on a free product. You also cannot withdraw the promise: customers will quote it in renewals and escalations.

The badge is worth more when it carries a real guarantee that Glimmerdeck can keep. Glimmerdeck guarantees the front door and triage. The partner guarantees the fix.

## 2. Support model per tier

**Tier 0: Uncertified or community connectors**
- Glimmerdeck gives no support for connector behavior.
- The listing says "not tested by Glimmerdeck."
- Glimmerdeck only supports the platform and SDK. Platform bugs found through these connectors are still accepted.

**Tier 1: Certified (free to customers)**
- Label: "Certified: tested by Glimmerdeck, maintained by [Partner]."
- Glimmerdeck owns:
  - Intake and tagging by connector ID.
  - Triage with a repro against the conformance suite. Target: first response in 1 business day, routing decision in 2 (default, adjust to your capacity).
  - Platform and SDK bugs, which are fixed by Glimmerdeck.
  - Tracking the partner handoff and telling the customer the status.
- The partner owns:
  - Fixes for defects in its code.
  - Acknowledgment SLA: Sev1 4 business hours, Sev2 1 business day.
  - Fix-plan SLA: Sev1 1 business day, Sev2 5 business days.
  - A named support contact and a security contact.
- Glimmerdeck does not promise a fix date for partner code.
- Customers get a workaround or the partner's status, not a Glimmerdeck engineer in partner code.

**Tier 2: Premier or Managed (top tier, earned)**
- A partner qualifies after two consecutive quarters of SLA compliance and a minimum install base.
- Glimmerdeck adds:
  - A shared ticket with the partner.
  - An escalation path to a named partner engineer.
  - Joint incident handling for Sev1.
  - Priority recertification on platform releases.
- Customers with a paid Glimmerdeck support plan get Glimmerdeck-led escalation on Tier 2 connectors.
- "Fully supported" is allowed only here, and only in one of two cases:
  - The connector is first-party (Glimmerdeck builds and maintains it).
  - The customer holds a paid support plan that covers it.

## 3. Obligations that make the guarantee real

Put these in the partner agreement and the certification terms.

1. **SLA with consequences.** After 2 missed Sev1 SLAs in a quarter, the badge becomes "suspended." After 90 days without recovery, the connector is delisted. Both thresholds are defaults I set. Tune them against your own ticket data.
2. **Recertification** on every major platform version and annually.
3. **Cost recovery.** Charge partners an annual certification fee, or tie Tier 2 to a partner-paid program. This funds triage without charging customers.
4. **Publish partner status.** Show a connector health page and SLA compliance to customers. Public accountability makes partners respond.

## 4. Fix the ticket flow now

1. Tag every connector ticket by connector ID. You cannot manage the 30% until it is measured per connector.
2. Add the connector name, owner and contact to in-product connector errors. Many customers then go straight to the partner.
3. Ship a repro bundle and conformance report so support can prove ownership in minutes.
4. Send a templated handoff to the partner, with the customer kept in the loop.
5. Review the top 5 connectors by ticket volume monthly with their partners.

Measure these:
- Share of connector tickets resolved by the partner.
- Time to route.
- Partner SLA compliance.
- Tickets per 1,000 installs, per connector.

Target: Glimmerdeck-handled partner-bug time falls each quarter. Set the target from your current baseline.

## 5. Announcement wording

Use: "Certified connectors are tested by Glimmerdeck and backed by a support guarantee. Report any issue to Glimmerdeck. We triage it, and the partner fixes it within a committed SLA. Partners that miss the SLA lose certification."

Avoid: "fully supported by Glimmerdeck." It implies Glimmerdeck fixes partner code and removes the partner's incentive to staff support.

## 6. Why this beats the alternatives

- **"Fully supported":** adds an unfunded obligation to a free product. Partner bugs become your engineering and support cost.
- **"Partner support only, tell customers to contact the partner":** removes the badge's value. The customer is left to deal with a vendor they never chose.
- **Triage plus partner SLA plus delisting:** keeps the single front door customers want. It also makes the badge mean something, because the guarantee is enforceable.

## 7. Open question

Do your partners have support staff today? If many are solo developers, Tier 1's SLA must be softer, and Glimmerdeck should reserve Tier 2 for partners with real support teams. Tell me the partner profile and I'll adjust the SLA numbers.