# What to do with the CTO's API readability idea

**Do this:** build a short style guide, enforce it with a linter in CI, and name 2 API reviewers. Defer the formal certification. Fold the "champions" into the reviewer role.

I haven't looked at your codebase. I'm assuming you have, or can quickly generate, an OpenAPI spec. If you don't, add about half a day for that.

## Why not copy Google

Google's readability certification fits thousands of engineers. It keeps a large reviewer pool consistent, and tooling backs it up. You have 11 engineers and 40 endpoints, so three things follow:

- A certification process needs a pool large enough that "who is certified" is a real constraint. You'd have 2 to 4 reviewers, so naming them is enough.
- Per-domain champions need domains big enough to staff separately. You have 2 teams, so a champion per team is just a tech lead with a new title.
- What makes Google's setup work is the written rules plus automated checks. The human process sits on top of that. Copy that part first.

## Ranking

| Rank | Option | Value | Cost | Verdict |
|---|---|---|---|---|
| 1 | Short style guide **plus** linter in CI | High | ~1.5 days | Do now |
| 2 | Named API reviewers, required on spec changes | High | ~0.5 day | Do now (this replaces "certification" and "champions") |
| 3 | Breaking-change check in CI | High for a public API | ~0.25 day | Do now if the spec exists |
| 4 | One champion per team | Low to medium | Ongoing, small | Fold into #2 |
| 5 | Formal reviewer certification | Low at your size | Several days plus upkeep | Defer |
| 6 | Per-domain embedded champions | Low at your size | Ongoing | Defer |

Ranks 3 and 4 are my judgment, not CTO asks. I added the breaking-change check because a public scheduling API can't casually break its consumers. A written guide that nothing enforces tends to drift.

## The 3 days

**Day 1: audit and decide**
1. Export or write the OpenAPI spec for all 40 endpoints.
2. Tabulate how each endpoint handles these areas. Expect inconsistencies, and the table will show where:
   - resource naming and plural/singular
   - pagination
   - filtering and sorting
   - error shape and status codes
   - date/time and time zones, which matter for scheduling
   - idempotency on create/book/cancel
   - versioning
   - auth scopes
3. For each area, pick the convention the majority already follows. Pick a new one only where the majority is clearly wrong.
4. Get the other team lead to agree on the decisions in a 45-minute session.

**Day 2: write and automate**
1. Write the guide in 2 to 4 pages. Each rule gets a one-line rationale and one good example. Pull the good examples from your own API.
2. Add a "healthcare rules" section covering at least:
   - no patient identifiers in URLs or query strings, since those end up in logs
   - error messages must not leak PHI
   - idempotency keys on booking
3. Encode as many rules as possible in a linter such as Spectral. Run it in warn-only mode first, so it doesn't block the build on day one.
4. Add a breaking-change diff check, for example oasdiff. Make it fail the build, with an explicit override label for intentional breaks.

**Day 3: gate and roll out**
1. Add a CODEOWNERS rule so any change to the spec or API handlers requires 1 of 2 named API reviewers. Pick one from each team.
2. Write a one-page reviewer checklist that references the guide.
3. Run a 30-minute walkthrough with all 11 engineers.
4. Write a short note for the CTO (below).
5. List the existing violations as a backlog. Don't fix them in these 3 days.

## What you leave out for now

- The certification exam, levels, and credentials.
- Per-domain champions.
- Fixing the existing inconsistencies. Changing a public API's behavior is a compatibility decision, so handle it as separate, versioned work.

## Triggers to revisit

Reopen certification and champions when one of these happens:
- Headcount grows past about 25.
- The reviewer pool becomes a bottleneck, for example a PR waiting more than 2 days for API review.
- The linter and 2 reviewers still let inconsistencies through, for example 3 or more in a quarter.
- A third team starts shipping endpoints.

## Note for the CTO (draft)

> We're adopting the parts of Google's approach that scale down. We'll have a written guide, automated enforcement in CI, and two named API reviewers who must approve every API change. Formal certification and per-domain champions solve problems of a 1,000-engineer org. At 11 engineers they'd cost more than they'd return. We'll revisit them if we reach 25 engineers or the review process becomes a bottleneck.

## Risks

- **Unfixed legacy:** the guide will describe a better API than the one you ship, which is fine if you say so explicitly.
- **Reviewer load:** two reviewers can become a bottleneck. If so, add a third before you add a certification process.
- **Linter noise:** if it blocks the build on day one, people will route around it. Keep it in warn mode for a sprint, then promote the rules one at a time.

Next action: start Day 1 by exporting the spec.