**Run `public-api-design-review` on your OpenAPI file today.** Don't build anything new. That means no sandbox, no webhooks and no status page in this window.

**Why this one**
- The task is a surface audit, and the committed spec makes it cheap. It needs one session, no deploy and no sign-off, and nothing can be rolled back.
- Two years and ~40 integrators mean every quirk in those 60 endpoints is something someone depends on (Hyrum's Law). The audit shows which flaws are worth fixing and which of the missing pieces you should build first.
- "No sandbox, no webhooks, no SDKs" are each large builds you'd maintain forever. Today you can't tell which one hurts integrators most.
- You said hours only, so I cut the list to two surface-audit entries and dropped macro strategy.

**The three hours**
1. **Hour 1, mechanical pass.** Lint the spec with Spectral (or similar). Collect URI naming, HTTP method and status-code mistakes, and field-name inconsistencies. Also check pagination and filtering conventions, and whether every endpoint returns the same error shape.
2. **Hour 2, judgment pass.** Read the 60 endpoints in resource groups. Spot-check "mostly current" against the live API on a dozen endpoints, picking the busiest and the oddest. Where spec and behavior disagree, the behavior is the contract your integrators have today.
3. **Hour 3, bucket the findings.**
   - Mark each finding **Must-change** or **Improvement**.
   - Flag every fix that would break an existing integrator, since those can't ship casually.
   - Tally the Must-change items by theme (errors, retries, limits, undocumented behavior). That tally tells you what to do next week.

**What you have at the end:** an evidenced list, not a change. Nothing ships today, which keeps it safe to do before you go back to firefighting.

**Second entry (only if the audit has time left): `api-reference-quality`.** Your docs are generated from the spec, so completeness is mostly mechanical. Run it only if the spot-check shows the spec has drifted from reality. Its output is a CI lint gate that stops further drift.

**One thing could flip this.** Ask yourself: can you name who owns the API contract and who signs off a breaking change? If the answer is "nobody" or "it depends", route to `api-versioning-policy` first. Every later fix ships into a surface with no owner, even though this session wanted something else.

**Assumptions I made instead of interviewing you**
- Your 40 integrators are customer or partner engineers using API keys, not a third-party app ecosystem. If it's an open ecosystem, the ranking changes (OAuth moves up).
- Nothing is announced to sunset, and you have no launch date this quarter.
- Capacity is you plus fire-fighting. That also pushes webhooks, SDKs and a sandbox to "not now".

**Not now:** `api-error-design`, `api-idempotency-retry` and the other classes below the audit. They come after the audit, in whichever class it flags.

**Gap:** none. This task is covered.

**Not written:** `developer-platform-context.md`. This repo is `example-repo`, not Beacon's, so I didn't create it here. Save these lines in Beacon's repo root for next time:
- Audience: customer and partner engineers, ~40 integrators.
- Published surface: REST, ~60 endpoints, 2 years, OpenAPI checked in.
- Constraint: hours only, one-off.
- Open: contract owner and breaking-change signer.
- Session log: 2026-10-08, routed to `public-api-design-review`.