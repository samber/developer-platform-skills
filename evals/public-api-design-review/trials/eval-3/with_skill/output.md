**Do this first:** run Spectral with a forked Zalando ruleset on your OpenAPI spec. If you have no spec, generating one from the code is Day 1.

## Ranking

The ranking uses the review-program ladder from the `public-api-design-review` skill. I didn't ask the skill's clarifying questions first. The assumptions I used are listed at the end.

| Rank | Option | Verdict |
|---|---|---|
| 1 | **Linter CI gate** on a forked, trimmed rule corpus. This is your "written style guide". | **Do now.** Fits 2 teams, 3 days, ~40 endpoints. |
| 2 | **Two named reviewers** (one per team) added to the gate. This is Zalando's documented shape. | **Do next, as a policy.** It costs no build time, only ~1h/week of reviewer time. |
| ❌ | Reviewer certification (Google "API Readability" model) | **Deleted, not ranked last.** |
| ❌ | Embedded API champions per domain | **Deleted, not ranked last.** |

- **Why the linter ranks first:** two teams owning the whole surface step the ladder down to a linter-only gate, and your 3-day budget promotes it further. The semantic conversation happens in ordinary code review.
- **Why the pair is the default rung:** efficiency ranks `linter + two reviewers` above `linter-only`. The pair is easy to add, but it isn't what you build this week.
- **Why certification and champions are deleted:** with 2 teams there are no domains to embed reviewers in. Certification and a versioned shared corpus are ceremony over a conversation a few people already have.
- **Roadmap risk:** "eventually we'll federate" becomes a roadmap item that eats corpus-writing time nobody needs yet. Deleting the options keeps it off the list.
- **When to bring them back:**
  - A third team ships its own API surface, or
  - median review turnaround passes ~2 weeks.

## What to tell the CTO

- Google's program fits Google's scale. Its ICSE 2024 paper ("API Governance at Scale") describes certification as a way to grow scarce reviewer supply across thousands of engineers.
- Even Stripe's Kenneth Auchenberg called centralized review "a centralized friction point... at scale with 1000s of engineers". He would pivot it toward education.
- The CTO's goal is right: "looks like it was designed by a single team" (Zalando's phrasing). You get that from a linter plus a short corpus, because consistency across the surface is what matters.
- You can still say yes to part of the ask. The written style guide is the forked corpus, and the named reviewers are the lightweight form of champions.

## 3-day plan

All hour figures are my estimates, not sourced.

**Day 1 (~6h): spec and mechanical pass**
1. Get the OpenAPI spec. If none exists, generate it from code or traffic (2-4h) and log "no machine-readable spec" as an Improvement.
2. Fork Zalando's ruleset (Zally or its Spectral equivalent). It is the most reusable corpus.
3. Run the linter on all ~40 endpoints.
4. Pull 5-10 real responses across endpoints. A spec can claim consistency that production doesn't have.

**Day 2 (~6h): human pass and the one-page corpus**
1. Walk the 8 dimensions across the whole surface, not endpoint by endpoint:
   - resource and URI naming
   - HTTP method semantics
   - status codes
   - field naming
   - pagination
   - filtering and sorting
   - error envelope
   - backward compatibility
2. Bucket each finding. **Must-change** needs a cited MUST rule or precedent. No rule means **Improvement**, always.
3. Check consistency first. Mixed `created_at` and `createdAt`, mixed pagination, or two error shapes are top-priority Must-changes. The rule is "pick one, apply everywhere", whichever casing you pick.
4. Trim the forked corpus to ~1-2 pages in MUST/SHOULD/MAY form. Delete rules that don't fit, since a rule you can't explain shouldn't be enforced.
5. Record existing deviations as precedents with a rationale. Google's `not-precedent` convention is the model. That keeps reviewers from re-litigating settled decisions.

**Day 3 (~4-6h): gate and process**
1. Add the linter to CI on PRs that touch the spec. Fail on MUST, warn on SHOULD. Add it to the editor too.
2. Name two reviewers, one per team.
3. Write a one-page process:
   - **Trigger:** by audience × lifecycle, not by calendar. Review is required at beta and at GA-if-changed for externally consumable APIs, and recommended at alpha.
   - **Input:** review the spec or design doc before the code exists.
   - **Rule for blocking:** every blocking comment cites a rule. Taste never blocks.
   - **Escalation:** name the override authority up front (the CTO, if they agree), so disputes resolve in days.
4. Hand the CTO the one-pager with the ranking above.

## Shipped API: don't fix in place

Patients' schedulers and partner systems likely already depend on today's field names, error shapes, and ordering (Hyrum's Law). A Must-change against behavior clients already observe is a breaking change.

- The review names the defect.
- The versioning and deprecation policy schedules its removal.
- Demand no silent in-place fixes. This needs `api-versioning-policy`, which I haven't run.

## Health checks after launch

- **Audit gate:** zero Must-change findings open at beta or GA, or a recorded deviation for each.
- **Too heavy:** median turnaround past ~2 weeks, or teams shipping around review. Target under a week. These are Google-derived calibration points, not laws.
- **Too light:** a defect reaches GA that a written rule would have caught. Add that rule to the linter.

## Not covered

- One line per area, existence checks only: versioning scheme, idempotency or retry handling on unsafe methods, one auth model, rate-limit signaling, and documentation of every endpoint. Each has its own sibling skill.
- Patient-data security and compliance review sits outside this skill.

## Assumptions to confirm

Any of these could change the ranking:

1. **Shipped or proposed?** I assumed the API is shipped. A paper design drops the retrofit caution.
2. **Does a spec exist?** If not, Day 1 shifts to generating one.
3. **Lifecycle stage:** I assumed beta or GA with external consumers. An internal alpha only gets advisory feedback.
4. **Existing corpus:** I assumed none, so the Zalando fork is the start. A team already fluent in Microsoft's or Google's rules can fork those instead.
5. **Hard deadline?** A launch inside 3 days makes the linter-only gate the whole plan.

**Next, ~5 minutes:** tell me whether an OpenAPI spec exists and whether the API is already in production.