**Start with the cold-run baseline, then fix errors and the README. Defer MCP.**

Next action, about 2 hours: pick 5 to 8 real tasks. Examples: "authenticate", "list stock for SKU X", "reconcile a location", "handle a 429", "handle a bad request". Give each to a fresh coding agent that sees only your public surfaces (README, public spec, public docs). Log every point where it guesses, invents a method, or needs a human correction. That log is your baseline and your priority list. Don't fix anything before you have it.

I didn't inspect your repo, so the sizing below rests on what you told me.

## Why this order

All three complaints have one root cause. An agent can't recover when your surfaces are silent. It can't find the auth variable, it can't reach the examples, and `bad request` gives it nothing to correct. An MCP server on top of that would expose the same silence through a new door.

## Plan

1. **Check agents can fetch your docs at all (1 hour).**
   - Request your docs site and the README with common AI user-agent strings and record the status codes.
   - If the CDN blocks them, every other docs fix scores zero.
   - Letting AI crawlers in is a policy call, so the decision may sit outside your team.

2. **Fix the README this week (half a day).**
   - Name the auth env var and show a complete snippet: imports, client construction, call, printed result, error branch.
   - Pin the package version in the snippet.
   - Add a short table of error codes with causes and fixes.
   - Put one full reconciliation example inside the repo, not on the docs site.
   - Make the SDK read that env var by default. If it's missing, fail at construction with a message that names the variable.
   - This directly answers the engineer who said the SDK is "basically unusable by a coding agent".

3. **Replace `bad request` with structured errors (about 1 to 2 weeks, depending on how many error sites you have).**
   - Each body gets a stable `code`, a human `message`, the offending `field` where relevant, a `retryable` flag, and a docs URL. RFC 9457 `problem+json` is a reasonable shape to adopt.
   - Add the fields without removing the old message string, so existing customers don't break.
   - Do the endpoints a reconciliation agent touches first: auth, stock reads, movements, adjustments.
   - Include `Retry-After` and rate-limit headers on 429s.
   - This is the biggest single gain for the two accounts, because unattended agents self-correct from error bodies.

4. **Publish and annotate the OpenAPI spec (about 1 week for the reconciliation endpoints).**
   - Give every operation a verb-noun `operationId`.
   - Close the value space with enums, `required`, defaults, and formats.
   - Write descriptions covering preconditions, side effects, idempotency, pagination, and rate limits.
   - Serve the spec at a public URL and link it from the README.

5. **Add markdown versions of the docs pages and an `llms.txt` (a few days, only if your docs build can emit them).**
   - Link both from the README and the docs navigation.
   - The index file alone changes nothing. It only pays off once the pages it points at exist.

## MCP: what to tell the account

Say it's on the roadmap after items 2 to 4. Then ask them one question: read-only lookups, or write access such as stock adjustments?

- Reconciliation is likely a programmatic job, so the SDK and API quality matter more than a tool wrapper. They may be satisfied without MCP.
- Once the spec is annotated, an MCP server is cheap to generate. Curate it to fewer than 20 tools.
- Ship it read-only first. Writes need idempotency keys and an audit trail before you let an agent adjust inventory.

## Product gaps to check before next year

These aren't docs work, but an agent running reconciliation will hit them:

- Idempotency keys on write operations.
- Stable cursor pagination.
- An `updated_since` filter or change feed, so it doesn't re-read everything.
- Consistent snapshot reads.
- Realistic rate limits.

Ask the two accounts what volume they plan to pull.

## Done when

- You re-run the same task set from a clean agent and corrective turns drop.
- The agent never invents an API call on the three most common tasks.
- Each routine task needs at most 3 fetched documents.

Set the success-rate target from your own baseline, not a round number.

## Timeline

- **This week:** steps 1 and 2, plus the baseline.
- **This month:** steps 3 and 4.
- **Next quarter:** step 5, the product-gap review, and a read-only MCP server if the accounts still want it.

Next: tell me whether you own the docs CDN and build output. If you do, step 5 moves up. If you don't, I'll drop it and keep the rest repo-only.