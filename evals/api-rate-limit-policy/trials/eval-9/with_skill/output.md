**Next action, today:** pull the MSA clause that cites 1,200/min and send it to legal. Don't change enforcement yet.

I read the skill and its checklist. I haven't seen your gateway config, MSA text, or ticket data. Everything below rests on the facts you gave me and assumes a REST API.

## Verdict

Docs and enforcement disagree in three places. Each one makes a developer hit a limit the docs never mentioned. That is the most likely cause of the doubled tickets, but I haven't confirmed it (see "Confirm the cause" below).

## Findings, ranked

1. **Region scope is wrong in docs and contract. This is the highest risk.**
   - Docs say "global". The gateway enforces 1,200/min separately in each of 4 regions.
   - A key spread across regions gets up to 4,800/min. The skill calls this a real exploit vector.
   - Backend load can be 4x what you planned for.
   - The MSA cites the number as an SLA. The skill's failure list names a published limit cited as an SLA without the policy saying so.
   - Nothing has broken contractually so far. Customers get at least what was promised, but the number's meaning is ambiguous.

2. **The 50-concurrent-connection block is a secret guard.**
   - It is legitimate, but nobody can learn it exists except by tripping it. The skill names this as GitHub's communication failure.
   - A caller under 1,200/min gets blocked. Support sees it as "limit bug".
   - Concurrency is a different metering unit from requests per minute (Twilio documents it separately), so it needs its own line in the docs.

3. **The sandbox gets 10x the production limit.**
   - A developer load-tests at 12,000/min, ships, then hits 1,200/min in production. That is the first 429 they've seen.
   - The skill's default is no separate sandbox tier. Same numbers in test mode keep throttling code honest.

4. **Gaps the skill checks for. I can't see these from here.**
   - Only one number is published, with no separate burst figure.
   - Does every 429 carry `Retry-After`?
   - Does the 429 say which limit was hit: rate, concurrency, or region?
   - Is there a written override path for enterprise?

## What to fix, in order

1. **Contract (legal-owned, start now, then wait).**
   - Reword the MSA so the number is a floor: "at least 1,200 requests/min per API key per region".
   - Reserve the right to adjust limits with notice.
   - The skill says published limits are operational hints, not an SLA. If you keep SLA language, the policy must say so and name the scope.

2. **Region scope. Pick A or B.**
   - **A (recommended): document reality.** Say "1,200/min per key, per region, counted independently". No engineering. Matches what customers already get. No customer loses capacity.
   - **B: enforce a true global limit.** It needs a counter shared across 4 regions, which adds latency, cost, and an on-call burden. It tightens up to 4x for multi-region callers, so it needs at least 6 weeks' notice.
   - Move to B only if finance or abuse data shows the 4x multiplier hurts you.

3. **Concurrency guard, docs only, no behavior change.**
   - Document three things: "more than 50 concurrent connections per key triggers a block", the block duration, and what the caller sees.
   - Make the response machine-readable: a 429 with a distinct reason code, modeled on `Stripe-Rate-Limited-Reason`, and `Retry-After`.
   - Check whether the block hits the enterprise customers who run many workers. If it does, add per-key overrides.

4. **Sandbox.**
   - Set it to production numbers. If evaluation abuse worries you, add an aggregate volume cap instead of a faster per-minute limit.
   - The sibling skill `samber/developer-platform-skills@api-test-mode-design` decides whether that cap exists at all.
   - Roll it out the way the skill says: log the traffic first, then enforce at a high ceiling, then tighten. Give notice before the tightening.
   - If you keep 12,000/min, put a loud warning in the docs: "Sandbox limits do not match production."

5. **Publish the missing numbers and signals.**
   - Publish burst and sustained as two numbers, and describe the algorithm by its behavior, not its name.
   - Document the `Reset` semantics.
   - Write the enterprise override path with a lead time.
   - Add a page that says what a caller sees at each limit.

## Confirm the cause

Tag last quarter's limit tickets by which finding caused them: region, concurrency, sandbox, or other. About 1 hour for a sample of 50. It tells you which fix to ship first and gives you a baseline. If most tickets are "other", the cause is something this audit didn't find.

## Done criteria (the skill's two gates)

- **Docs match enforcement in both directions.** Every enforced limit appears in the docs, including the concurrency guard. Zero drift.
- **Every throttle is machine-readable.** All throttle responses carry `Retry-After` and a documented reason code.

Track these from the first month: 429 rate, limit tickets, and override requests per quarter.

## Rough timing

- Docs edits (steps 2 to 3, option A): about half a day.
- 429 reason codes (step 5): a few days of engineering. I haven't seen your gateway code, so I can't be more precise.
- MSA: depends on legal.
- Sandbox change with notice: about 8 weeks, mostly the 6-week notice floor.

## Questions that would change this answer

1. Does any enterprise customer rely on, or already exploit, the multi-region 4x?
2. What does the 50-connection block return: a 429, a dropped connection, or a block for N minutes?
3. Is the API REST only, or is there GraphQL too?
4. Is there a hard date from an enterprise negotiation?

Answer #2 first: it decides how big step 3 is.