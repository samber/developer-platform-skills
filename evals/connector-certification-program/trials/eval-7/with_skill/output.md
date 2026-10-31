# Quillbarrow badge structure: verdict

**Verdict: not ready for exec review.** I'd replace the structure, not tune it. Three of the five elements break the skill's rules, and the mechanism that would make the search boosts defensible doesn't exist yet.

I didn't run the interview, so every answer below that I assumed is marked "assumed". Correct those first, because the go/no-go depends on them.

## 0. Inputs

| Question | Answer | Status |
|---|---|---|
| 1. What do partners build? | Apps in a marketplace for an HR platform | Given |
| 2. Partner share of installs; partner count | ~150 partner apps; share of installs unknown | Count given; share **assumed** ≥ 20% |
| 3. Who reads the badge? | Enterprise procurement and security review (HR data is sensitive) | **Assumed** (b) |
| 4. Per-app production measurement | No per-app error rates | Given |
| 5. Platform release cadence and published versions | Unknown | **Open** |
| 6. Reviewer and engineering capacity | Unknown | **Open** |
| 7. Existing tier? | Proposal pending; "Approved" seal may already be shown | **Open** (b, or c if the seal is live) |
| 8-11. Deadline, one-off vs compounding, effort ceiling, partner fee | Unknown | **Open** |

- **Re-ranking:** the answer to question 4 ("no per-app error rates") removes every telemetry-based rung. That is why the search boosts fail below.

## 0b. Proposals evaluated

| Proposal (Product Marketing) | Verdict | Rule it meets or breaks |
|---|---|---|
| Platinum: top 10 by installs | **Rejected** | A metal ladder of three or more tiers, keyed on installs. Installs measure popularity, not behavior. A fixed top 10 also certifies a rank, so one app can lose the badge without getting worse. |
| Platinum: quarterly co-marketing webinar | **Rejected as a badge benefit** | Co-marketing belongs to the partner program. Tying it to the badge makes certification a sales asset. |
| Platinum: +40% search boost | **Rejected now** | Rank weight is allowed only with telemetry criteria behind it. You have none, so it rewards installs only, and installs then drive more installs. |
| Gold: security review + 500 installs | **Changed** | Drop the installs gate: it is a commercial criterion. Keep security review as a criterion of the single earned label. |
| Gold: +20% search boost | **Rejected now** | Same rank-weight rule as Platinum. |
| Silver: passes security review | **Changed** | Becomes a criterion of the earned label, with a renewal rule. A review that is never repeated certifies one release. |
| Bronze: listed | **Changed** | This is the listing bar, not a label. Keep it apart from labels. |
| "Quillbarrow Approved" seal for anything checked manually | **Rejected as designed** | Manual inspection is the starved rung, with no written criteria and no renewal. It also puts Quillbarrow's brand on a label, which reads as an operator support promise. |

## 1. Go/no-go

- **Outside reader:** procurement and security reviewers, assumed. It holds if they ask for the badge, so confirm.
- **Partner share:** assumed to hold at ≥ 20% of installs. Check the number.
- **Evidence:** no telemetry, so only the operator-run conformance kit is available. It holds only if partner apps talk to your platform through API, OAuth, webhook or SCIM contracts that one kit can exercise. It fails if the apps are mostly self-hosted widgets you can't test generically.

**Decision (provisional): run a one-label program if the kit is feasible. Otherwise ship ownership labels only and re-check in a quarter.** Ownership labels only is a complete outcome. It is not a failure.

## 2. Labels (replace the five)

| Label | Buyer meaning | Maintained by | Earned by |
|---|---|---|---|
| Quillbarrow-built | We built and support it | Quillbarrow | n/a |
| Partner-maintained | Partner built it; not certified | Partner | Listing bar only |
| Community | Unsupported contribution | Whoever | Listing bar only |
| **Verified** (name TBD; avoid "Quillbarrow" in it) | Partner-built, passed our kit and security review, still current | Partner | Criteria below |

- **Listing bar, kept apart from labels:** a manifest that validates, declared data scopes, a named support contact, a privacy policy URL, and a basic automated security scan. Don't make Verified mandatory for listing. With 150 apps it would cap your catalog at reviewer capacity.
- **Seal fate:** delete it. The security reviews it stood for now live in Verified. If you want manual review for apps holding restricted employee-data scopes (a good reason), keep it as a scope-specific review feeding Verified. Run it through `app-marketplace-review`, not as a second badge.
- **Popularity:** show installs as a catalog sort and filter. It is a fact, so it doesn't need a badge.
- **Homepage features:** keep them as editorial placement, labelled "Featured". Don't tie them to Verified.

## 3. Criteria (Verified)

All thresholds are starting values until you have a baseline from your best existing apps.

| Metric | Threshold | Window | Min. volume | Measured by |
|---|---|---|---|---|
| Contract kit: required tests pass, overall pass bar | All required, > 90% | Per app release | n/a | Operator CI |
| Platform-version currency | Passes on every supported version | Per platform release | n/a | Operator CI |
| Security review | Passed, no open critical findings | Annual floor, plus on new scopes | n/a | Reviewer |
| Security contact | Named, reachable | Annual check | n/a | Operator |
| Release cadence | One release, or a signed no-change attestation | 6 months | n/a | Operator registry |
| Support response | First response ≤ 3 business days | Trailing quarter | ≥ 5 tickets | Operator ticketing (if tickets exist) |

- **No production success-rate criterion yet.** You can't measure it. Inventing one is how criteria become unfalsifiable.
- **Telemetry roadmap:** tag every API call with an app ID and version. Build a fault split that excludes platform outages. After that, add success rate (for example ≥ 95%, 28 days, ≥ 200 calls, as a starting value) and re-evaluate on a published date.
- **Low-volume apps:** an app with too little data holds Verified on kit evidence and shows "kit-verified, insufficient production data". Low volume never fails a criterion.

## 4. Kit

- Semver it, with a changelog.
- Layers: static (manifest, scopes, no secrets), contract (auth, read, write, webhooks, error handling, rate limits), platform matrix.
- Open to partners for self-testing. Block submission until required tests pass.
- Generate tests from the app's declared contract, not from partner-written tests.
- Exemptions need reviewer sign-off, and the count is published.

## 5. Support routing

| Label | First contact | Who fixes | Sentence on listing |
|---|---|---|---|
| Quillbarrow-built | Quillbarrow | Quillbarrow | "Built and supported by Quillbarrow." |
| Verified | Quillbarrow triages, then routes | Partner, under a stated response time | "Verified apps meet our published criteria. Quillbarrow takes your first call and routes it; the partner fixes it." |
| Partner-maintained, Community | Partner | Partner | "Supported by <partner>, contact <channel>. Not supported by Quillbarrow." |

## 6. Renewal

- Pin each badge to the kit version, the platform version (or API contract version), and the lowest app version it covers. Older versions show the ownership label.
- Re-run the kit on a contract-changing platform release, a new kit major, a behavior-changing app release, and new scopes.
- Ship the new kit to partners at platform beta, before general availability.
- Calendar floor: annual, for security review and contact only.
- Give 6 months' notice before new criteria apply to existing Verified apps.

## 7. Decertification ladder (starting defaults)

| Rung | Trigger | Owner | Notice | Customer action |
|---|---|---|---|---|
| Warning | One failed evaluation | Marketplace ops | Same day | None |
| Badge suspended | Two consecutive failed evaluations | Marketplace ops | 14 days | None |
| New installs blocked | Suspended > 90 days, 6 months unmaintained, or partner exit | Marketplace lead | 30 days | Notified |
| Existing installs disabled | Only after rung 3 with migration path | Marketplace lead plus legal | 60 days | Notified, migration path published |

- **Evaluation clock:** failures are counted at trigger-driven kit re-runs plus the annual floor.
- **Dispute:** one route, decided by the marketplace lead within 10 business days. The badge stays during the dispute, except on the security fast path.
- **Security fast path:** an unpatched critical vulnerability blocks new installs within 3 days. This matters more here because the apps handle HR data.
- **Adoption:** offer an abandoned high-usage app to a new maintainer before rung 3.
- **Contract:** back the ladder with agreement clauses (revocation right, support obligation, badge-use scope).

## 8. What the label buys

- A catalog filter, a listing chip, and operator triage.
- **No search boost yet.** Revisit after telemetry criteria have run for two quarters.
- No co-marketing tie-in. Run those through the partner program.
- Partner fee: none assumed. A fee turns revocation into a refund question.

## 9. Transition

Only needed if the Approved seal or any tiers are live. If so, revert every badge granted without the kit evidence (by installs, by a one-time manual look) to its ownership label on a published date. Give holders one release cycle to re-earn Verified. Add one sentence on affected listings explaining the change. Don't grandfather anyone.

## 10. KPIs

- Share of installs on Verified apps.
- Verified vs non-Verified production success rate, once telemetry exists. No gap means the criteria measure nothing.
- Time from submission to label.
- Renewal lapse rate per platform release.
- Support tickets misrouted to Quillbarrow for partner-owned apps.
- Decertifications per quarter, by rung.
- Review date: one quarter after launch.

## 11. Gate check

| Gate | Result | Evidence |
|---|---|---|
| Go/no-go recorded with each condition | Pass (provisional) | §1 |
| Every criterion has metric, threshold, window, volume, measurer | Pass | §3 |
| Every tier has one support sentence | Pass | §5 |
| Every badge pinned (kit, platform, lowest app version) | Pass | §6 |
| Every ladder rung has trigger, owner, notice, customer action | Pass | §7 |

## What to tell exec review

1. The proposal certifies popularity and the partner relationship, not app quality. A badge should be a promise about how an app behaves next quarter.
2. Four tiers plus a seal are more labels than a buyer can tell apart. One earned label over ownership labels is clearer.
3. The search boosts rank by installs and can't be defended without per-app error data. Fund per-app telemetry first.
4. Co-marketing and homepage placement can stay. They move to the partner program and editorial, outside the badge.

## Questions that could change this

1. Do partner apps integrate through contracts a kit can test (API, OAuth, webhooks, SCIM)? If not, the decision is ownership labels only.
2. What share of installs is partner-built, and does procurement ask for a badge?
3. Is the Approved seal already live, and on how many apps?
4. How many reviewer hours per week, and can you build and maintain a kit?
5. Does the platform publish API versions, and how often does it ship breaking changes?
6. Is there a hard date, and will partners pay for the badge?