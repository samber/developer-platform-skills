**Use a tiered, event-driven renewal. Do not run an annual full manual re-review.**

Partners get at least 4 months to read a new requirement, 8 weeks to test it, and 90 days after GA before it is enforced. That is about 7 months from first sight to enforcement.

## Renewal model

A certificate says "conforms to contract version N". It is not valid "until forever" or "until the anniversary". Four layers:

1. **Release delta recert, twice a year.**
   - Trigger: each contract-changing release.
   - Scope: only the requirements that changed.
   - Method: partner runs the conformance suite on the beta and submits results.
   - Review: the Vantorra team reviews the delta only.
2. **Annual attestation on the anniversary date, automated.**
   - Partner re-runs the full suite and submits the result.
   - Partner signs an attestation: the driver is maintained, security and support contacts are current, and no critical issue is open.
   - Vantorra checks the evidence. No manual re-review.
3. **Manual re-review only for high-risk tier.**
   - Tier by customer install base, data-path criticality (credentials, bulk load), security surface, and past failures.
   - Review the top tier every 2 years. Sample about 10% of the other tiers each year as an audit control.
4. **Event triggers force an off-cycle review.**
   - Failed suite run.
   - CVE or security incident.
   - Major rewrite of the driver.
   - Ownership change.
   - Unresponsive support contact.

## Lapse ladder

Never expire silently.

1. **Certified**: current.
2. **Notice**: a deadline was missed. Partner gets 30 days.
3. **Certified for N-1 only**: not recertified for the new release. Vantorra lists it as supporting the old contract version only.
4. **Lapsed**: delisted after the old contract version reaches end of support.

## Why this satisfies the compliance lead

- The control is "evidence of continued conformance", not "a human re-read every year".
- Annual suite results plus a signed attestation give an audit trail for all 47 partners.
- The sampled manual audit gives independent assurance and catches partners who game the suite.
- Event triggers cover the real risk, which is change.
- An anniversary date alone detects change up to 11 months late. Release-aligned recert detects it at the release.

Cost, with my assumption of 2 to 5 reviewer-days per partner: the full manual model costs 94 to 235 reviewer-days a year, plus partner time. The tiered model needs manual days for about 5 top-tier partners per year plus a 10% sample, so roughly a tenth of that.

## Notice for a new requirement

Measured against the release calendar you described, with GA as T0:

1. **T-16 weeks (roadmap):** requirement announced with a draft spec. Partners can plan.
2. **T-8 weeks (beta):** final spec and the conformance test are available in the beta. Spec freeze: no new requirement after beta starts. A late one moves to the next release, 6 months later.
3. **T0 (GA):** the requirement applies to new certifications and to new partner driver releases.
4. **T+90 days:** existing certificates must pass the delta. Otherwise the partner moves to "Certified for N-1 only".
5. **Security exception:** a critical security requirement can bypass this. Give a 14-day window for critical issues and 30 days for high ones. Publish the reason afterwards.

Hard floor: never enforce a requirement less than 6 months after it first appears on the roadmap, except under the security exception.

## Transition from "never expires"

1. Publish the policy now.
2. Give every partner 12 months for a first full suite run and attestation. Mark grandfathered partners as "legacy, pending".
3. Start the delta recert cycle at the next contract-changing release.

## Assumptions to check

- **A conformance suite exists and is automated.** The model depends on it. If it covers less than about 70% of the requirements, manual review share rises, and building the suite comes first.
- **Old contract versions stay supported for at least 12 months.** Otherwise "Certified for N-1" has no value. This is a Vantorra policy call.
- **Tier thresholds and sample sizes are my proposals.** Tune them after the first cycle.

**Next (about 10 minutes):** list the 47 partners with the four tier inputs (install base, data-path criticality, security surface, past failures). That gives you tier sizes to confirm the manual review cost with the compliance lead.