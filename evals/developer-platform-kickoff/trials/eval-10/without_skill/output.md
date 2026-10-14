# Ridgeway Clinical: API GA plan (2 engineers, 11 weeks)

⚠️ **Check the dates first.** Today is 2026-10-08, so 6 November is **4 weeks** away, not 11. Eleven weeks from today lands on 24 December. Either "eleven weeks" is stale, or the GA is 6 November 2027. I wrote the plan for 11 weeks as you said, with a **4-week cut line** at the end. If the real gap is 4 weeks, use the cut line.

## Recommendation

1. **GA is the plan.** Roughly 90% of the two engineers' capacity goes to it. Three design partners have been told the date.
2. **The ecosystem question gets a bounded, mostly non-engineering answer.** It costs about 3–4 engineer-days plus your own time.
3. **The marketplace is a documented "not now" with reopen conditions.** Don't build or design one in this window.

Reasons, and the assumptions behind them, follow.

## Why the marketplace waits

The ecosystem-strategy ladder runs from a documented API up to partner-built integrations, extension points, installable apps and a runtime platform. Each step needs more standing staff and is harder to withdraw. For Ridgeway Clinical, the gates fail at the marketplace rung:

| Gate | Status |
|---|---|
| Counted demand (5+ named complements requested, with customers) | **Unknown.** Nothing in this brief shows a list. |
| Externalizable interfaces | **Unknown.** The REST surface is the first public one. It hasn't been used by outsiders yet. |
| Complementor supply | **Fail today.** The API has no external users, so there are no builders. |
| Staffing | **Fail.** Two engineers, fully committed to GA. |
| Security and consent review | **Likely fail.** You're a clinical company, so installable apps mean consent, revocation and data-handling review (PHI, if applicable). That is a permanent function you almost certainly don't have. |

A marketplace listing without an API anyone uses yet is a directory nobody installs from. The GA is the first step toward the ecosystem. It isn't a competing priority.

## Weeks 1–11: GA workstream (2 engineers)

The goal is to make the 90-endpoint surface *safe to freeze*. GA commits you to a deprecation policy, so what you publish now is hard to withdraw.

**Weeks 1–2: Audit and freeze decisions** (both engineers)
- Spec-vs-implementation conformance: run contract tests against all 90 endpoints. Generated docs are only as true as the spec.
- Triage every endpoint as GA, beta-labelled, or withheld. Withholding a weak endpoint is cheaper than deprecating it later.
- Decide and write down the versioning scheme, deprecation notice period, and rate limits and quotas.
- Fix inconsistencies in naming, pagination, error shapes and idempotency while changes are still free.

**Weeks 3–6: Hardening** (split: one engineer on auth/security/limits, one on reliability/tests)
- Auth and scopes, audit logging, and per-key rate limiting.
- Error model, idempotency keys on writes, and webhook signing if webhooks exist.
- Load and soak tests at 2–3× the traffic you expect from the three partners.
- Authorization tests: tenant isolation, and no cross-tenant reads on any endpoint. For a clinical API this is the highest-severity risk.
- Staging environment and sandbox with synthetic data only.

**Weeks 5–8: Partner readiness** (one engineer, plus you)
- Run each of the three design partners through the quickstart in a live session. Log where they stall.
- Fix the top issues from those sessions. Don't wait until week 10.
- Publish a changelog and a status page, and set up an escalation path.

**Weeks 9–10: Release hardening**
- Docs pass: every endpoint has a working example, and every error code has a documented cause.
- Runbook, on-call rota and a rollback plan for GA day.
- Freeze 1 week before GA, bug fixes only.

**Week 11: GA and the first week after it**
- Ship, then watch the dashboards. Hold a daily partner check-in for the first week.

## The partner ecosystem story: what goes in the plan

Your director wants a story and a board member asked a question. Neither needs engineering time now. Put these four items in the plan:

1. **Count demand (you, about 4 hours a week for 3 weeks, weeks 2–4).** Build a list of every complement customers and partners have asked for, with the customer named: integrations with EHRs, billing, analytics and so on. Five or more named requests is the bar to open the next rung. Look for unofficial glue customers already built against you. That is the strongest signal.
2. **Ask the design partners one question (week 4).** "If we didn't ship X, what changes for you?" An answer like "we lose a certification" means they will build. "Nothing really" means you have a logo, not a partner.
3. **Write the story as a ladder (week 5, 1 page, you).** "GA API now → vendor-built connectors we choose from demand → partner-built integrations we list → apps/marketplace when conditions are met." Directors and boards accept a staged story that has measurable gates. They usually don't accept "no".
4. **Write the decline memo for the board (week 6, 1 page).** It states that the marketplace is deferred, why, and what would reopen it (below). This stops the question coming back every quarter.

**Engineering cost: about 3–4 days in total.** Use it to publish an OpenAPI file and Postman collection (already derivable from your spec) and to make sure the sandbox is usable by outsiders. That is the real "developer ecosystem" work you can do now, and it overlaps with GA.

## Reopen conditions for the marketplace

Revisit after GA plus roughly 90 days, and only if **all** of these hold:

- 5 or more named complement requests, each with a customer.
- At least 3 external teams are actively calling the API in production.
- At least 2 builders have a stated business case (revenue, certification, or cost avoided).
- A named owner and funded headcount exist for security and consent review.
- A decision has been made on PHI and consent handling for third-party apps.

Without those, don't build it.

## Risks and cut line

- **Biggest risk: scope creep.** One marketplace discussion with the board can eat a week of the team's attention. Put the decline memo in front of the director early, in week 2 or 3, instead of fielding questions through week 10.
- **Second risk: tenant isolation and security bugs.** Never cut that work. If something has to slip, drop in this order: endpoint docs polish, sandbox extras, then non-critical endpoints (label them beta).
- **If the real gap is 4 weeks:** do the audit, mark the weakest endpoints beta or withheld, run authorization tests and a short load test, and onboard the three partners. Skip the ecosystem tasks, and give the director the one-page ladder as the interim answer.
- **Kill or de-escalate trigger.** If fewer than 2 of 3 partners are live in production by 4 weeks after GA, pause every ecosystem item and put the full team on partner success.

## Open questions that would change this

- Is the 6 November date 2026 or 2027?
- Is any PHI exposed through the API?
- Do you already have a list of requested integrations?
- Is there any security or compliance review function today?

I assumed no, no, no, and no for the last three, so the plan is conservative. Better answers would only make the ecosystem section stronger.