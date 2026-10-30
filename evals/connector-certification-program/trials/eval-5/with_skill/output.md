# Kestrelgate connector certification charter, v0.1 (draft), 2026-10-30

**Short answer on leadership's idea:** don't certify on the form alone. A form is self-attestation, and self-attestation alone never certifies. For an identity platform that is worse than usual, because the badge tells a buyer that a connector validates SAML assertions and handles provisioning correctly. Nobody would observe that claim.

You also shouldn't keep reading code on every release. Manual inspection is the most expensive evidence rung, and it is the reason for your 9-week queue. The fix is to move the proof into an operator-run test kit, keep human review for a small high-risk subset, and keep the form only for what a kit can't observe.

I wrote this in one pass instead of interviewing you question by question. Every assumed interview answer is labelled in section 0, so correct them there.

## 0. Inputs

| Interview question | Answer | Asked or assumed |
|---|---|---|
| 1. What partners build | Protocol implementations: SSO (SAML/OIDC) and provisioning (SCIM or similar) | Stated |
| 2. Install share and count | About 260 partner-built integrations. Install split between operator-built and partner-built is unknown. | Count stated; share assumed ≥ 20% partner |
| 3. Who reads the badge | Enterprise procurement and security review, plus your support team | Assumed (b)+(c) |
| 4. Per-connector production telemetry | Assumed auth and provisioning logs exist. Whether you can separate platform faults from connector faults is unknown. | Assumed, **verify** |
| 5. Platform changes that can break connectors | Assumed versioned API/contract, a few contract-changing releases a year | Assumed |
| 6. Reviewer and engineering capacity | 2 senior engineers, fully consumed. Kit-building capacity unknown. | Reviewers stated, kit capacity assumed ~1–2 engineers for a quarter |
| 7. Existing program | Running, being revisited because the queue is 9 weeks and partners are threatening to leave (7c) | Stated |
| 8. Deadline | No hard date, but 9 weeks of queue is the pressure | Assumed |
| 9. One-off or compounding | Compounding asset | Assumed |
| 10. Effort ceiling | Low reviewer hours, moderate engineering, low tolerance for partner churn | Assumed |
| 11. Fee | None | Assumed |

**Re-ranking:**
- Q10, low tolerance for partner churn: the operator-run kit moves to the default rung, because it lets partners self-test before submitting.
- Q4, fault split unknown: telemetry criteria start in "kit-verified, insufficient production data" mode until the split exists.
- Q7c: the transition section becomes mandatory.
- Q6, reviewers fully consumed: manual review is limited to restricted scopes, so reviewer hours stop scaling with release count.

## 0b. Proposals evaluated

| Proposal (who) | Verdict | Rule it meets or breaks |
|---|---|---|
| Certify on the 40-question form alone (leadership) | **Rejected as stated** | Breaks "self-attestation alone never certifies". The badge would promise behavior nobody observed, and a first compromised connector would end its meaning. |
| Drop per-release code reading (leadership, implied) | **Adopted** | Manual inspection is the starved option, promoted only for connectors with restricted data scopes. The per-release cost is what made the queue. |
| Keep the form (leadership) | **Changed** | Kept only as a legally binding declaration paired with published kit results, trimmed to questions the kit can't observe. |
| Keep reading code on every release (status quo) | **Rejected** | The queue shows it doesn't scale. Fivetran closed its curated partner-built program after 13 connectors for a similar reason. |

## 1. Go/no-go

- **Outside reader:** procurement and security reviewers read the label. Holds, assuming Q3.
- **Partner share:** about 260 partner integrations; assumed ≥ 20% of installs, or including the most-installed ones. Holds, **verify**. If Kestrelgate builds the connectors buyers mostly use, own those first.
- **Evidence:** SSO and provisioning follow standard protocols, so a connector-agnostic kit is affordable. Telemetry is not yet affordable without a fault split. Holds on the kit alone.
- **Decision:** run the certification program, kit first, telemetry later.

## 2. Labels

| Label | Meaning to a buyer | Maintained by | Earned by |
|---|---|---|---|
| Kestrelgate-maintained | Built and supported by us | Kestrelgate | n/a |
| Partner-maintained | Listed, partner-built, not tested by us | Partner | Meets the listing bar |
| Certified | Passed our published test kit at a stated version | Partner | Section 3 criteria |
| Community | Unreviewed | Anyone | n/a |

**Listing bar**, kept apart from labels and automated: static layer passes, security contact named, no known critical vulnerability open. Certification is never required to be listed. Making it mandatory would cap the catalog at reviewer capacity.

I deleted metal tiers and anything keyed on partner commercial status. Partner-company tiers belong to the partner program, not the connector label.

## 3. Criteria

Thresholds are starting values until you have a baseline. Recalibrate after two cycles against what your best current certified connectors already achieve.

| Metric | Threshold | Window | Minimum volume | Measured by | Label |
|---|---|---|---|---|---|
| Static layer: manifest and metadata valid, declared scopes, no secrets in fixtures | all pass | per submission | n/a | operator CI | Listing + Certified |
| Contract layer, required tests | 100% required pass, >90% overall | per connector release, results ≤ 48 h old | n/a | operator CI | Certified |
| Security negative tests (below) | 100% pass | per connector release | n/a | operator CI | Certified |
| Platform-version currency | passes matrix on every supported version | per contract-changing platform release | n/a | operator CI | Certified |
| Dependency vulnerabilities | no critical/high CVE unpatched > 30 days | per release plus monthly rescan | n/a | partner-run scan, artifacts published, operator rescan | Certified |
| Connector-attributed error rate | ≥ 95% operations succeed, platform faults excluded | trailing 28 days | ≥ 200 operations | operator telemetry | Certified, activates once fault split exists |
| Support response | first response ≤ 3 business days | trailing quarter | ≥ 5 tickets | operator ticketing | Certified |
| Release cadence | one release or signed no-change attestation | 6 months | n/a | operator registry | Certified |
| Security contact reachable | named and answering | annual check | n/a | operator | Listing + Certified |
| Restricted-scope review | no open findings | first certification and on scope change | n/a | reviewer, via `app-marketplace-review` | Certified, restricted-scope connectors only |

Below the minimum volume, a telemetry row reads "insufficient data", never pass or fail. The listing then says "kit-verified, insufficient production data". There is no usage minimum on Certified itself, so partners don't hit a catch-22.

## 4. Kit

- **Version:** semver, starting at 0.x pilot; changelog published in the partner docs.
- **Layers:**
  - Static: every submission.
  - Contract: every connector release, against a sandbox tenant.
  - Regression: only for connectors above a usage threshold you set.
  - Platform matrix: each contract-changing platform release.
- **Contract tests**, generated from the connector's declared contract, not from partner-written tests:
  - Provisioning: create, read, update, deactivate, group membership, filtering, pagination, PATCH semantics, error mapping, 429 handling, idempotent retries.
  - SSO: assertion/token validation, state and nonce, redirect URI matching, clock skew, logout.
- **Security negative tests:** these replace the part of code reading that was hunting for auth flaws.
  - SAML: unsigned, wrong-key, wrong-audience, expired and replayed assertions must be rejected.
  - OIDC: bad state, nonce or redirect URI must be rejected.
  - Secrets: a canary secret in the fixtures must not appear in connector logs or outbound calls.
  - Dependencies: dependency scan results are published.
  - Evaluate the existing open conformance suites for OIDC, SAML and SCIM before writing your own.
- **Pass bar:** 100% of required tests and >90% overall. A single percentage lets partners skip the tests that matter.
- **Partner self-test:** partners run the same kit locally. Submission is blocked until required tests pass: **yes**.
- **Exemptions:** destructive or paid operations may be flagged exempt. Each needs a reason and a replacement check, a reviewer signs it off, and the exemption count is published.
- **Kit regression:** regression-test the kit itself, because a kit bug fails every partner at once.

**Validate before you build.** Take the last 12 months of findings from your two reviewers and replay each against the proposed kit. Every finding the kit would miss is either a new test to write or a reason to keep human review for that class. This is how you check that dropping code reading doesn't drop real catches.

## 5. Support routing

| Label | First contact | Who fixes | Response commitment | Sentence shown on listing |
|---|---|---|---|---|
| Certified | Kestrelgate triages, isolates platform vs connector fault, routes | Partner | First response ≤ 3 business days | "Certified by Kestrelgate against kit vX. Maintained and fixed by <partner>; Kestrelgate takes your first call and routes it." |
| Partner-maintained | Partner | Partner | Partner's own | "Supported by <partner>, contact <channel>." |
| Community | Community | Community | None | "Community-maintained, no support commitment." |

A "Kestrelgate Certified" label reads as an operator support promise. Keep the support sentence directly beside the badge.

## 6. Renewal

- **Pin:** each badge names kit v<x>, platform contract version <y> with the date of the last matrix run, and the lowest connector version it covers. Older connector versions show the ownership label.
- **Triggers, scaled to the change.** This is the main queue reducer: today every release gets full human review.
  - Cosmetic release (copy, icon, docs): static check only, automatic.
  - Behavior-changing release: full contract and security layers.
  - New scopes or endpoints: full layers, plus restricted-scope review if the new scope is restricted.
  - Contract-changing platform release or new kit major: re-run the matrix.
- **Telemetry re-evaluation:** first business day of each month, trailing 28 days. Partners see their own values on a dashboard the same day.
- **Beta lead time:** ship the kit version for a contract-changing platform release to partners at platform beta, before GA.
- **Calendar floor:** annual, for the security contact and the form declaration only.
- **Notice before new criteria apply:** 6 months. Re-running existing criteria on a new platform version is renewal and needs no extra runway.

## 7. Decertification ladder

| Rung | Trigger | Owner | Notice | Customer action |
|---|---|---|---|---|
| Warning | One failed scheduled evaluation | Certification lead | Same day, by email | none |
| Badge suspended | Two consecutive failed evaluations | Certification lead | 14 days | none; listing and installs untouched |
| New installs blocked | Suspended > 90 days; or no release and no support response for 6 months (after a 30-day offer of the connector to a new maintainer or to us); or partner exit | Platform program manager | 30 days | Existing customers notified |
| Existing installs disabled | Only after rung 3 with no recovery | Head of platform plus legal | 60 days | Customers notified, migration path published first |

- **Ladder clock:** failures are counted at scheduled monthly evaluations, each reading a trailing 28 days.
- **Dispute route:** the certification lead's manager decides within 10 business days. The badge stays during the dispute, except on the security fast path.
- **Security fast path:** an unpatched critical vulnerability blocks new installs within 3 days.

These counts are starting defaults. Replace them with your own numbers before publishing.

## 8. What the label buys

- A catalog filter, a listing chip, and operator triage for Certified connectors.
- **No search-rank weight** until two quarters of telemetry exist. Ranking by badge invites gaming.
- **No co-marketing slots.** They belong to the partner program.
- **Fee:** none.
- **Badge use:** only on listed versions at or above the pinned version. After suspension, the partner may not claim "Certified".
- **Agreement clauses to add:** revocation right, partner support obligation, version scope of the badge, liability disclaimer.

## 9. Transition (running program)

Every existing badge was earned by code reading plus a form. That is not the new evidence, so each one needs a fate.

| Old label | New label | Re-earn deadline | Buyer-facing sentence |
|---|---|---|---|
| Certified (code-read + form) | Partner-maintained until re-earned | 120 days from the date the kit opens, about one release cycle | "Certification now uses a published test kit. This connector is being re-tested." |
| Not certified | Partner-maintained | n/a | none |

- **No grandfather clause.** For politically important partners, lengthen the notice instead.
- **Waves:** start with the most-installed connectors, and give those partners hands-on help with the kit.
- **Count before announcing:** the number of connectors now holding the badge isn't in your brief. It sets the size of the re-earn wave.

## 10. KPIs and review date

- Share of installs on certified connectors.
- Certified vs non-certified production success rate. No gap means the criteria measure nothing.
- Time from submission to label (target: days, not weeks).
- Renewal lapse rate per platform release.
- Tickets misrouted to Kestrelgate for partner-owned connectors.
- Decertifications per quarter, by rung.
- Kit first-pass failure rate per partner, which shows whether the kit is clear.
- **Review date:** 6 months after the kit goes blocking.

## 11. Gate check

| Gate | Pass / fail | Evidence |
|---|---|---|
| Go/no-go recorded with each condition | Pass | Section 1 |
| Every criterion has metric, threshold, window, minimum volume and measurer | Pass | Section 3 |
| Every tier carries a support sentence | Pass | Section 5 |
| Every badge names kit version, platform/contract version and lowest connector version | Pass | Section 6 |
| Every decertification rung names trigger, owner, notice and customer action | Pass | Section 7 |

## 12. Rollout sequence

The durations below are rough estimates and depend on how many engineers you can put on the kit.

1. **Week 1:** publish the change-type policy. Reviewers stop reading cosmetic and non-behavioral releases. This alone should shorten the queue; measure what share of queued items are cosmetic.
2. **Weeks 1–6:** build kit 0.x, contract layer plus security negative tests. Replay last year's review findings against it.
3. **Weeks 4–8:** pilot with about 10 partners, including the most-installed. Fix kit bugs before it blocks anyone.
4. **Weeks 8–12:** the kit becomes blocking for new submissions. Publish the ladder and agreement clauses. Start the re-earn waves.
5. **After the fault split exists:** switch on the telemetry criteria.

Reviewers' remaining work is maintaining the kit, restricted-scope reviews, exemption sign-offs and disputes.

## What I need from you to firm this up

1. How many connectors hold the Certified badge today, and what share of installs are partner-built?
2. Can you separate platform faults from connector faults in production logs?
3. How many releases per week reach the queue, and what share are cosmetic?
4. Which of the 40 form questions can the kit observe? Those can be deleted.
5. How many engineers can build the kit this quarter?