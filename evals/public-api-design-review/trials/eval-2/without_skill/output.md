# API Design Review Board: Process Design

## Recommendation

Don't make the monthly meeting the main control. At 19 external-facing teams, a monthly sync becomes a 30-day queue. Teams will ship around it, and 5 architects can't deep-review everything.

Build three layers:

1. **Standards plus automation** remove most review work. Your pagination and error-body problem is a standards problem, so fix it there first.
2. **Async review with an SLA** covers the middle tier.
3. **The monthly board** handles only novel, contested, or high-risk decisions, plus standards governance.

## 1. Capacity math

These are assumptions. Replace them with real numbers from your inventory.

| Input | Estimate |
|---|---|
| External-facing teams | 19 |
| New or changed external API surfaces per team per quarter | about 2–3 |
| Reviews per quarter | about 40–60 |
| Deep reviews a 2h board meeting handles | 4–6 |
| Deep reviews per quarter (3 meetings) | about 12–18 |

A sync-only board covers about a third of the load. That's why tiering is needed.

## 2. Review tiers

| Tier | Trigger | Mechanism | SLA |
|---|---|---|---|
| **0: Automated** | Every PR touching an OpenAPI/proto spec | Linter (Spectral or equivalent) in CI, blocking on MUST rules | Minutes |
| **1: Async light** | New endpoint or additive change on an existing API that follows the standard | One steward reviews the spec diff in a PR, no meeting | 3 business days |
| **2: Async deep** | New external API, new resource model, auth change | Written design doc, two board members review, comments in doc | 5 business days |
| **3: Board meeting** | Breaking change to a public API, a deviation from a MUST rule, a new cross-cutting pattern, or an unresolved Tier 2 disagreement | Team presents, board decides in the room | Next meeting, or an ad hoc session if blocking |

Expect roughly 60% Tier 0/1, 30% Tier 2, and 10% Tier 3. The meeting stays small and the discussions stay interesting, which keeps architects engaged.

**Early-stage rule:** review the design before implementation. Reviewing a built API means nobody will change it.

## 3. Standards: the real deliverable

Write a short "API Standard v1" in the first 6 weeks. Mark each rule **MUST**, **SHOULD**, or **MAY**. Only MUST rules are enforced by the board and the linter.

Start with the pain you already have:

- **Error body:** adopt RFC 9457 (Problem Details) with a small mandatory extension set: stable machine-readable `code`, `request_id`, and field-level `errors[]`.
- **Pagination:** pick one default. Cursor-based is the usual choice for external APIs. Define the request params, response envelope, and max page size. Allow offset only by exception.
- **Versioning and deprecation:** the scheme, a minimum notice period (for example 6 months for external APIs), and the `Deprecation` and `Sunset` headers.
- **Cross-cutting items:**
  - Idempotency keys on unsafe POSTs
  - Rate-limit headers
  - Naming and casing
  - Auth scheme naming
  - Filtering and sorting
  - Timestamps (RFC 3339 UTC)
  - ID formats
- **Definition of "external-facing":** partner, customer, or public. Write it down. Edge cases like internal APIs called by one partner will cause arguments otherwise.

Ship these alongside the standard so it's cheap to comply:

- A shared library or middleware per main language that emits the error body and paginates correctly. Teams adopt the standard because it's easier than inventing their own.
- A spec template and a worked example.
- Linter rules as code, versioned, with a public changelog.
- A mock server or contract-test harness.

The standard itself changes through an RFC process, so teams can propose changes and the board doesn't look like an ivory tower.

## 4. Board structure

**Roles**

- **Chair** (one of the 5, rotating every 2 quarters): owns the agenda and the decision log.
- **Program manager** (dedicated, full-time-ish, **the most important hire**): runs intake, tracks the queue, publishes decisions, chases follow-ups. Without this person the board decays within a quarter.
- **Reviewers:** the architects, at about 15–20% of their time. Set that expectation with their managers up front.
- **Standing non-architect seats:** one security rep, one docs/DevRel or technical-writing rep, and ideally one consumer voice (support or solutions engineering, who see what external developers struggle with).
- **Quorum:** 3 of 5, including the chair or a delegate.

**Scaling from 5 to 10:** don't add reviewers just because the calendar says so. Add them when a trigger fires:

- p90 time-to-review exceeds the SLA for 2 consecutive months.
- The Tier 2 queue stays above N open items (set N after the pilot).
- A reviewer is carrying more than about 6 reviews per month.

Prefer growing a **steward network** over growing the board. Make one trained "API steward" per group of 3–4 teams. Stewards handle Tier 1 locally and escalate to the board. The board stays at 5–7 and the steward pool absorbs the load. If you do reach 10, split by domain (for example, platform/data/payments) with a shared chair group, rather than 10 people in one meeting.

## 5. Decision rights

Decide this explicitly early:

- **Binding on MUST rules for external-facing APIs.** No GA release without a pass or a recorded exception.
- **Advisory on SHOULD rules and on internal APIs.**
- **Exceptions** are granted by the board, recorded as short ADRs with an owner and an **expiry date**, and re-reviewed on expiry. Exceptions without expiry become the new de facto standard.
- **Escalation:** you (head of platform) are the tiebreaker if a team disputes a decision. Make that visible so the board has teeth.
- **Enforcement point:** the release process, not goodwill. Add a check to your release or API-gateway onboarding so an external API can't be exposed without a review ID.

## 6. The monthly meeting

Two hours, fixed agenda, pre-read required (no pre-read, no slot):

1. Decision log and exception expiries (10 min)
2. 2–3 Tier 3 designs, 30 min each: 10 min present, 15 min discuss, 5 min decision recorded in the room
3. Standard/RFC changes (20 min)
4. Metrics and queue health (10 min)

Rules:

- Decisions are written within 2 business days: approved, approved with conditions, or rework.
- Reviewers give the reasoning, with a link to the standard's rule.
- Open a recurring "office hours" slot weekly so teams can get informal help before they write a design doc.

## 7. Legacy: 31 teams, years of divergence

Don't try to retrofit everything. Triage the existing surface:

1. **Inventory (weeks 1–4):** catalog every external API: owner, consumers, pagination style, error format, spec availability. Many will have no OpenAPI spec, so start there. This also gives you the real numbers for the capacity model.
2. **Score by exposure:** external consumer count and traffic × divergence from the standard.
3. **Migrate at version boundaries:** new endpoints and new major versions must conform. Existing endpoints get a funded migration plan only when exposure justifies it. Where an error-body change is breaking, offer the new shape alongside the old (versioned or opt-in header) and deprecate on the standard timeline.
4. **Fund it.** Part of your budget should buy migration capacity for the highest-exposure teams. Otherwise the standard becomes an unfunded mandate and the board becomes the villain.

## 8. Two-quarter timeline

| Weeks | Milestone |
|---|---|
| 1–2 | Name the chair, pick the 5 architects, negotiate their time with their managers. Start the program manager hire. Announce the intent and the "why" to all 31 teams. |
| 1–4 | API inventory. Gather examples of the divergent pagination and error shapes. |
| 3–8 | Draft Standard v1 (pagination, errors, versioning, deprecation, external definition). Circulate it for RFC comment from the teams. |
| 6–10 | Linter rules in a CI template. Shared error and pagination libraries for the top 2 languages. |
| 8–12 | **Pilot** with 4–5 willing teams (mix of high-exposure and friendly). Run Tiers 0–3 end to end, including 2 live board meetings. Tune the SLAs. |
| 12 | Checkpoint: publish pilot metrics. Revise the standard to v1.1. |
| 13–18 | Rollout: **mandatory for all new external APIs and new major versions.** Train stewards. Add the release gate. |
| 18–26 | Migration program for the highest-exposure legacy APIs. Review the board-size triggers. Publish the first quarterly report. |

Don't make the process mandatory before the pilot. A badly tuned first month burns trust that's hard to recover.

## 9. Metrics

Track these from week 1 so you have a baseline:

- **Convergence:** number of distinct pagination styles and error body shapes across external APIs. Target: 1 for new APIs, a falling count for old ones.
- **Speed:** p50 and p90 time from submission to decision, per tier. A review process that slows delivery will be routed around.
- **Coverage:** percentage of external APIs with a spec, percentage passing the linter, percentage of new external APIs that had a design review before build.
- **Quality:** breaking changes shipped to external consumers, exceptions open past expiry.
- **Team sentiment:** a 3-question survey after each review: was it useful, was it fast, would you bring the next design earlier?
- **Consumer signal:** external support tickets about pagination and error confusion.

## 10. Budget priorities

In rough priority order:

1. A dedicated program manager
2. Backfill or protected time for the 5 architects
3. Migration capacity for high-exposure legacy APIs
4. Tooling: linter and CI integration, an API catalog (Backstage or similar), contract-test or mock infrastructure
5. A technical writer for the standard and the examples

## 11. Failure modes to watch

- **Board becomes a bottleneck:** the tiers and SLAs prevent this. Watch p90.
- **Architects review nitpicks:** the MUST/SHOULD split and the linter keep them on the decisions that matter.
- **Teams bring designs after building:** the release gate and an early-engagement norm fix this. Celebrate early arrivals.
- **Standard drifts from reality:** run the RFC process and a quarterly standard review.
- **Exceptions pile up:** expiries, plus a count on the quarterly report.
- **Seen as the "no" committee:** publish approved examples, keep decisions short and reasoned, and have the board offer fixes rather than only objections.

## Questions that would change this design

- Do most of the 19 teams already have OpenAPI or proto specs?
- Who are the external consumers: paying customers, partners, or both? Do you have SLAs or contracts that restrict breaking changes?
- How many languages and frameworks are in use? That sets the scope of the shared libraries.
- Can you get a binding release gate from engineering leadership, or is the board advisory in practice?