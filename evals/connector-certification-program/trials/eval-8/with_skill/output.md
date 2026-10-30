# Vantorra connector certification: renewal policy (charter sections 0b, 6, 7, 9)

**Answer:** Don't adopt a yearly full manual re-review. Renew on events, with continuous telemetry. Pin every badge to the kit, platform and connector versions it was earned on. Keep an annual check only for evidence that expires on its own.

Partners get **at least 6 months' notice** before a new criterion applies to an already-certified connector. Re-running existing criteria against a new platform release is renewal, not a new criterion. That path gets the roadmap (4 months ahead) plus the kit at beta (8 weeks ahead).

## 0. Inputs

I did not run the interview. These answers are assumed, so please correct them.

| Question | Answer | Status |
|---|---|---|
| Q1 What partners build | (c) drivers and adapters | Stated |
| Q2 Partner share | 47 certified partner connectors; share of installs unknown | Assumed: holds the go/no-go bar |
| Q3 Who reads the badge | Buyers and procurement; compliance lead is the internal sponsor | Assumed (b) |
| Q4 Per-connector telemetry | Not stated | Assumed available via a partner User-Agent or connector ID. If not, use kit-only evidence (see Fallback). |
| Q5 Breaking-change cadence | Contract-changing release twice a year; roadmap 4 months ahead; beta 8 weeks before GA | Stated |
| Q6 Reviewer capacity | Not stated | Assumed part-time reviewers, with a kit to build |
| Q7 Existing program | Running, never expires | Stated, so (c) |
| Q8–Q10 Deadline, one-off vs compounding, effort ceiling | Not stated | Assumed compounding, no hard date, moderate effort ceiling |
| Q11 Partner fee | Not stated | Assumed none |

**Re-ranking:**
- Twice-yearly contract-changing releases make platform-release triggers the main renewal driver. A calendar date would not line up with them.
- The compounding mandate promotes the kit and telemetry over manual rungs.

## 0b. Proposals evaluated

| Proposal (who) | Verdict | Rule |
|---|---|---|
| Recertify everything yearly on the anniversary, full manual re-review (compliance lead) | **Changed.** The calendar survives only as a floor for expiring evidence. Manual review is rejected. | Manual code inspection is the starved option, at full reviewer cost per release. It is reserved for restricted data scopes. A fixed calendar cannot see a contract change that lands mid-year, so a badge could be 11 months stale. |
| "Too heavy" (partners) | **Adopted.** | Event-triggered kit runs are cheap for partners because they self-test with the same kit. |
| Never expires (today) | **Rejected.** | "No expiry" is deleted. The badge certifies only the platform version it was earned on. |

The compliance lead's real need is an auditable, current claim. Give them these records:
- Per-badge pins.
- Published kit results.
- A dated evaluation log.

## 6. Renewal

**Pin.** Each badge names the kit version (e.g. 2.x), the platform contract version, and the lowest connector version covered. Older connector versions show the ownership label.

**Re-run the kit when any of these fires:**
1. A platform release that changes the contract (twice a year). This is the platform-matrix layer.
2. A new kit major version.
3. A connector release, scaled to the change. Behavior changes get the full contract layer. Cosmetic changes get a static check.
4. New data scopes or endpoints.

**Timeline for each contract-changing release (GA = G):**

| When | What |
|---|---|
| G − 4 months | Roadmap published. Partners learn what changes. |
| **G − 8 weeks (beta)** | **Kit version for the new contract ships, with the matrix layer. Partners self-test.** |
| G | GA. Badges are extended to the new platform version where the matrix passes. |
| G, if not passing | The badge stays pinned to the older versions, where it is still true. The new version shows the ownership label and the partner gets a Warning. Suspension follows only after two consecutive failed scheduled evaluations. |

This assumes Vantorra keeps supporting the older platform versions. If it does not, tell me and the pins change.

**Telemetry re-evaluation.** Run it on the first business day of each month over a trailing 28-day window. Partners see their own values on a dashboard that day. Below the minimum volume, the criterion reads "insufficient data" and never fails. The listing says "kit-verified, insufficient production data".

**Calendar floor (annual, anniversary date acceptable).** It applies only to criteria that expire on their own:
- Security contact named and reachable.
- Support contact.
- Security attestations.

If a connector has no release for 6 months, it needs a release or a signed no-change attestation.

**Notice before new criteria apply: at least 6 months.** This is a starting value, modeled on Atlassian's former Cloud Fortified commitment. Two cases:

| Change type | Notice partners get |
|---|---|
| New criterion or threshold (policy, not contract) | ≥ 6 months from publication. It takes effect at the first scheduled evaluation after that. The kit includes the check from announcement, in advisory mode. |
| Requirement that comes from a platform contract change | Roadmap (4 months) plus kit at beta (8 weeks). This is renewal, so it earns no extra runway. |

A 6-month notice spans roughly one release cycle. Announce a new criterion alongside a roadmap, and it lands no sooner than the release after next, not the next one. Keep the two cases apart in writing. Otherwise a platform change gets relabeled as a "new requirement" to demand more runway, or the reverse.

## 7. Decertification ladder

These numbers are starting defaults.

| Rung | Trigger | Owner | Notice | Customer action |
|---|---|---|---|---|
| Warning | One failed scheduled evaluation, or a failed matrix at GA | Certification lead | Same day, with the dashboard value | None |
| Badge suspended | Two consecutive failed evaluations. The label reverts to ownership. | Certification lead | 14 days | None |
| New installs blocked | Suspended more than 90 days, no release plus no support response for 6 months, or a partner exit | Platform owner | 30 days | Notified |
| Existing installs disabled | After rung 3 | Platform owner | 60 days | Notified, with a migration path published first |

- **Clock:** failures are counted at monthly evaluations, each reading a trailing 28 days.
- **Dispute route:** the partner contests to the program owner, who decides within 10 business days. The badge stays during the dispute, except on the security fast path.
- **Security fast path:** an unpatched critical vulnerability gets new installs blocked within 3 days.
- **Adoption before rung 3:** offer an abandoned connector above the usage threshold to a new maintainer, or to Vantorra.

## 9. Transition for the 47 existing badges

No grandfather clause.

1. Each existing badge becomes "Partner-maintained" (ownership label) on a published date.
2. Run the kit's contract layer on all 47 at the next beta, together with the matrix.
3. Holders have until that release's GA to re-earn. That gives them one release cycle and the 8-week beta head start.
4. Re-earned badges are pinned. Listings carry one sentence: *"Certification now expires with platform releases; this connector is verified for <version>."*

Revoke even for politically important partners. Lengthen the notice instead.

## Fallback if telemetry isn't available

If per-connector attribution or a platform-vs-connector fault split doesn't exist yet:
- Renewal rests on the kit triggers above.
- The annual floor stays.
- Add telemetry criteria once the fault split exists.

## KPIs and 11. Gate check

**KPIs:** renewal lapse rate per platform release, time from submission to label, and decertifications per quarter by rung. Review the charter after the first two releases.

| Gate | Result |
|---|---|
| Go/no-go recorded | **Pass, on assumptions** (reader, partner share, evidence) |
| Criteria have metric, threshold, window, volume and measurer | **Not covered here.** This answer covers renewal only. Section 3 still needs your baseline. |
| Support sentence per tier | **Not covered here** (section 5) |
| Pins name kit, platform and connector version | **Pass** |
| Ladder rungs name trigger, owner, notice and customer action | **Pass** |

## Questions for you

1. Does Vantorra have per-connector production telemetry (Q4)?
2. How many hours a week do certification reviewers have (Q6)?
3. Does Vantorra support older platform versions after a new GA?

The first answer decides whether the telemetry criteria go live now or later. The other two could change the pins and the notice numbers.