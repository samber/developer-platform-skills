# API design review program for Verrill Systems

**First action: this week, inventory every external-facing surface across the 19 teams.** Collect each OpenAPI spec (or none), plus 5-10 real responses per API. You can't write rules or size reviewer load until you know what exists.

## Verdict on your plan

Keep the 5 architects. Change two things.

1. **Drop the monthly meeting as the gate.**
   - Triggers are audience × lifecycle, never the calendar. No studied program gates on a calendar.
   - The one exception is the .NET API review, which runs a weekly slot over a change-triggered queue.
   - A monthly gate means up to 4 weeks of waiting. The benchmark is under 1 week for small APIs, and a median past ~2 weeks means too heavy.
   - Teams then ship around review.
2. **Don't grow the central board from 5 to 10.**
   - Growing a central committee is the one scaling move no studied company chose.
   - Google measured turnaround and guidance consistency degrading together as its reviewer pool grew.
   - Stripe's Kenneth Auchenberg called central review "a centralized friction point... at scale with 1000s of engineers" and would pivot it toward education.
   - Instead, the 5 become the standards team and trainers. Growth comes from certified reviewers embedded in the teams.

Your real problem is that 19 teams invented their own pagination and error body. That is a consistency problem, and a meeting does not fix it. A rule corpus, a linter, and shared defaults do.

## Assumptions (correct me)

I could not ask first, so these are my assumptions. Each one moves the plan if wrong.

| Question | My assumption | If wrong |
|---|---|---|
| Existing APIs or new designs? | Both. Most of the 19 teams have shipped surfaces. | If all new, skip the retrofit track. |
| Who consumes the APIs? | Mix of partners and public. | If internal only, no formal review. |
| Rule corpus today? | None. | If you have one, skip the fork step. |
| Clients depending on current behavior? | Yes (Hyrum's Law). | None means in-place fixes are allowed. |
| New or changed external APIs per month? | Unknown. | Under ~4 a month: stay on rung 2 longer. |

## Program shape

This is the maturity ladder, adapted to your answers.

- **Weeks 1-8: linter plus two named reviewers per API.**
  - This is Zalando's shape, and it is the default rung.
  - It stands up in days on a forked public corpus.
- **Weeks 8-26: promote to a certified federated reviewer pool.**
  - You have 19 teams, so this rung is on the menu. It is the highest-value and highest-effort rung.
  - You have budget and two quarters, which is about the quarter-scale effort it costs.
- **Skip the linter-only gate as an endpoint.** At 19 teams, semantic checks need humans.

Start with the default rung. It gives you days-to-value, and the federated rung needs the corpus it produces.

## Review rules

1. **Trigger by audience × lifecycle.**
   - Internal-only surfaces get no review.
   - Alpha gets advisory feedback.
   - Beta is required and blocking.
   - GA is required again only if the surface changed.
   - Tag each API with an audience field in its spec (Zalando's `x-api-audience`), so the trigger is automatic.
2. **Review designs, not code.**
   - The input is the spec or design doc.
   - Google's pre-reform failure was reviews starting so late that teams had to start over.
3. **Two buckets, no score.**
   - **Must-change** needs a cited written rule or precedent.
   - **Improvement** covers everything else, including taste.
   - Taste never blocks.
4. **Deviation needs a recorded rationale.**
   - Use a Google-style `not-precedent` tag with one of the enumerated reasons: local consistency, pre-existing functionality, external spec, existing system, expediency, or technical concerns.
   - The burden sits on the deviator. The reviewer does not have to out-argue them.
5. **Defer to settled decisions.**
   - Reopen one only if it was a significant mistake that still matters.
6. **Publish the escalation path and the override authority on day one.**
   - Bypassing review is an explicit decision by a named director or VP.
   - Name that person now.
7. **Walk all eight dimensions every review.**
   - The dimensions are resources and URIs, methods, status codes, field naming, pagination, filter/sort/fields, error shape, and backward compatibility.
   - Add the five one-line sibling checks: versioning, idempotency, auth, rate limits, docs.
   - Review across the surface, never one endpoint alone.

## Timeline (about 26 weeks)

**Phase 0, weeks 1-2: inventory and decisions**
1. Inventory every surface and tag it by audience and lifecycle.
2. Run a Spectral-class linter against the specs you have. A missing spec is itself an Improvement finding.
3. Fork a public corpus: Zalando or Adidas (most reusable), or Microsoft (most enterprise-complete). Adapt it before enforcing it.
4. Name the override authority and the escalation path.
5. Pick the two precedents that hurt most:
   - **One pagination pattern.** Cursor or keyset is the usual fit for external APIs. Require a default size, an enforced max that returns 400 above it, `has_more`, and a specified empty/last-page shape.
   - **One error envelope.** Use RFC 9457 problem details (`application/problem+json`) on every endpoint. Code taxonomy and message wording belong to the `api-error-design` skill, not this review.

**Phase 1, weeks 3-8: default rung live**
1. Publish corpus v0.1 with MUST/SHOULD/MAY keywords.
2. Put the Spectral ruleset in CI and the editor, so humans never spend review time on mechanical checks.
3. Assign 2 named reviewers per API, rotating from the 5 architects.
4. Ship a short design-doc template and an intake queue. Include a writer and a security reviewer, since doc writers are a common composition gap.
5. Hold one office-hours slot per week for teams. Keep the monthly meeting only as a guild forum: settle disputed decisions into the precedent log and train people.
6. Review every new beta/GA API from here on.

**Phase 2, weeks 6-16: make the consistent choice the default**

"It's documented" does not close an inconsistency. Developers don't read docs under deadline pressure.

1. Spend budget here: shared pagination and error-envelope middleware or SDK helpers, plus API templates.
2. Run the existing-API audit and produce one Must-change list per team.
3. **Do not demand silent in-place fixes on shipped APIs.** Clients may already depend on today's shapes. Route each fix through the deprecation machinery in `api-versioning-policy`.
   - The review names the defect.
   - The versioning policy schedules its removal.
   - Prefer adding the new shape beside the old one over modifying it.

**Phase 3, weeks 12-26: federate**
1. Certify reviewers inside the teams, modeled on Google's "API Readability" program.
2. Give each certified reviewer a domain. The 5 architects run certification and own the versioned corpus.
3. Move first-line review into domains. Central review handles escalations and cross-domain precedent.
4. Version the corpus. More reviewers without a versioned corpus amplifies inconsistency.

## Metrics (check monthly)

| Signal | Reading | Action |
|---|---|---|
| Median turnaround over ~2 weeks | Too heavy | Automate more, or federate sooner |
| Teams shipping without review | Too heavy | Same |
| Defects at GA that a written rule would have caught | Too light | Add the rule to the linter and require citations |
| Reviewers giving different guidance on the same issue | Corpus gap | Record the decision as precedent |

- **Ship gate:** zero open Must-change findings at beta/GA, or a recorded deviation for each one.
- **Coverage gate:** all eight dimensions walked, plus the five sibling checks. A skipped dimension makes the review incomplete, not lean.
- **Targets:** under 1 week for small APIs. The ~2-week and ~60% figures are Google-derived calibration points, not industry laws.

## Risks

- **Rubber-stamping.** Counter it with required rule citations, linter coverage, and a defects-at-GA metric.
- **Bottleneck.** Counter it with the under-a-week target, a trigger-based queue, and the federation trigger above.
- **Re-litigation.** Counter it with the precedent log.
- **Cutting rule-writing for headcount.** Corpus-writing and certification are the work. Hiring reviewers without them reproduces Google's pre-reform problems.

## Spend (suggested)

1. Linter and CI integration, plus shared middleware, SDKs, and templates.
2. A technical writer for the corpus, the doc template, and training material.
3. Reviewer training and certification.
4. Not extra central architects.

## Re-ranking triggers

- A hard deadline or low effort ceiling pushes you toward the linter-only gate.
- An existing API guild makes federation cheap.
- A team fluent in Zalando's or Microsoft's corpus skips the corpus-writing cost.

## Next action

Send me the five answers in the assumptions table, or the inventory once it exists. I'll turn that into the corpus v0.1 rule list and the first two precedents (pagination and error envelope), about 30 minutes of work.

**Sources:** Google AIP-100 and AIP-200, Macvean et al. (CHI 2016), the ICSE 2024 "API Governance at Scale" paper, Zalando's guidelines and Zally, Stripe's engineering blog and Auchenberg's account, Microsoft Azure's Stewardship Board, Erik Wilde on linter limits. All come from the skill's reference files and were not re-verified.