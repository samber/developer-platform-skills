# Vantage Ledger: is the `customer_ref` → `counterparty_id` rename safe?

**No. Treat it as breaking until a written policy says otherwise.** I did not review the API: no spec or traffic data was in scope, so I can't tell you how an integrator would actually break.

## Why the "just a rename" half is wrong

- **The rename.** A rename removes the old field and adds a new one. Any integrator who reads or sends `customer_ref` on those eight endpoints gets a missing field or a rejected request on day one.
- **The two dropped fields.** After three years and about 400 integrators, "nobody should be reading these" is a hope, not a measurement. Some integrator will be reading them (Hyrum's Law). Strict deserializers can also fail when a field disappears.
- **Why nobody can settle it.** You have no written definition of "breaking" and no named person who signs off on one. That missing document is the real problem.

## Route: `samber/developer-platform-skills@api-versioning-policy`

This is a macro-altitude question: what you are allowed to change, and who decides. Question 4 of the kickoff interview (who signs off a breaking change) came back empty. Under the skill's ordering, that promotes the versioning policy to first place whatever else the session wanted. `public-api-design-review` audits a surface against a promise, and you have no promise yet. Starting there would misroute the session.

The versioning policy covers the version scheme, a written breaking-change definition, notice windows by audience, Sunset/Deprecation signalling, and who signs off.

## Short-list, ordered by value per unit of effort

The versioning policy goes first because it was promoted. The rest follow the default order.

1. **`api-versioning-policy`**
   - Bottleneck: the team can't agree what "breaking" means or who decides.
   - Cost: one policy session, plus sign-off from product, support and whoever signs breaking changes. It ships no code.
2. **`public-api-design-review`**
   - Bottleneck: nobody has an evidenced list of what the eight-endpoint change touches.
   - Cost: one session over the existing spec and docs, with no deploy and no rollback.
3. **`api-reference-quality`**
   - Bottleneck: whether the two fields are documented decides if integrators were told not to read them.
   - Cost: one session over the spec and published reference.
4. **`integration-error-observability`**
   - Bottleneck: you can't enforce a cutoff, or notify the right integrators, without knowing who still calls these endpoints and reads these fields.
   - Cost: real engineering, such as a per-integration request-log store with retention. Check first whether your gateway logs already answer this.
5. **`sdk-portfolio-strategy`**
   - Bottleneck: only relevant if you ship official SDKs, since the rename must ship through them.
   - Cost: one session. Drop it if there are no official SDKs.

## Chain (dependency order)

1. `api-versioning-policy` produces the breaking-change definition, the notice windows and the sign-off role.
2. `public-api-design-review` applies that definition to the eight endpoints and the two fields, and returns a list of must-change items.
3. `api-reference-quality` documents the deprecation and the replacement field once the review has settled what changes.

## Not now

- `api-integration-surface-strategy`: unblocked when someone proposes a second public surface. Another surface before the compatibility promise exists multiplies the problem.

## Gap

The collection has no skill for API changelog automation, such as a CI diff that flags breaking spec changes. The versioning policy can state the rule, but nothing here builds the gate.

## What you can do while the policy is pending

Hold the removal and run the change additively. This is the standard pattern, and the versioning-policy session will formalize it:

- Return both `customer_ref` and `counterparty_id`.
- Accept either name on requests.
- Mark the old name deprecated in the reference and in response headers.
- Measure who still uses it.
- Remove it only after a notice window that someone with sign-off authority has approved.

The two dropped fields follow the same path: deprecate first, remove later.

## Routines (dry-run only, nothing created)

Proposed output channels are placeholders until you confirm them.

1. **Pre-release API design review** → `public-api-design-review`. It fires on each spec diff and posts a comment on the spec-change PR. This is the routine that can stop a breaking change before it ships.
2. **Quarterly kickoff re-invocation.** It posts a summary to the contract owner. You haven't named one yet, so this one is blocked until you do.

I would add the deprecation-window sweep once a sunset date is announced, anchored a full notice period ahead of the cutoff.

## Questions I couldn't ask (cold start, one-shot session)

These would re-rank the list above:

1. Who integrates: customers' own engineers, partners, third-party app builders, or AI agents?
2. Which other surfaces are published (webhooks, SDKs, bulk export)?
3. What is the deadline, and do you want a one-off fix or a standing process?
4. Does a spec file exist? Sharing it would make `api-reference-quality` nearly free and let a design review run.

## Context artifact

I did not write `developer-platform-context.md`, because there is no Vantage Ledger project root in this session. Writing it into `example-repo` would put it in the wrong repo. So the pass-bar item requiring the artifact is not met. Below is its content for you to commit to the real project:

```markdown
# developer-platform-context

- Audience: ~400 integrators (type unconfirmed)
- Published surfaces: REST, ~140 endpoints, public 3 years, no written compatibility promise
- Spec locations: unknown
- Contract owner / breaking-change signer: none named
- In-flight (2026-10-08): rename customer_ref -> counterparty_id on 8 endpoints; drop 2 response fields
- Decided: none
- Open: what counts as breaking; who signs; notice window; usage of the 2 fields
- Constraints: date, horizon, effort ceiling unknown
- Session log: 2026-10-08 kickoff (cold, no interview); routed to api-versioning-policy
```