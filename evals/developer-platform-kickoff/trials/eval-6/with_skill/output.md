# Helios Dispatch: what to do first

**Do first: `api-idempotency-retry`, on `POST /jobs`.** It is the only one of your two problems that charges a customer. The VP's "one fix" doesn't exist, because the two duplicates sit on opposite sides of the contract.

This is a cold-start pass. I found no `developer-platform-context.md` for Helios Dispatch, and I couldn't run the interview, so the open questions below are unanswered. The ranking is conditional on them.

## Route

**`samber/developer-platform-skills@api-idempotency-retry`**

Your incident is a client retrying a call into you after a timeout. That is idempotency keys, replay windows, and SDK retry defaults. The skill's own signal list includes "customers are double-charged".

## Why it isn't one fix

| | Triple charge | Duplicate callbacks |
|---|---|---|
| Direction | The client retries into you | You deliver out to the customer |
| Who retries | The customer's library | Your delivery system |
| Is the duplicate a bug? | Yes. The retry was safe to send and unsafe to receive. | No. At-least-once delivery produces duplicates by design. |
| Skill | `api-idempotency-retry` | `webhook-platform-design` |

The kickoff names this as a "provider vs client" split: same word, inverted advice. Your customer's dedupe table is the correct consumer behavior under at-least-once delivery. Your job is to make that dedupe cheap, with a stable event ID and documented delivery semantics. You can't make duplicates impossible.

For the VP: "two contracts, one shared word, and the charging one goes first."

## Short-list

Ordered by value per unit of effort, highest ratio first.

1. **`api-idempotency-retry`**
   - Attacks: double charges on retried POSTs.
   - Cost: one design session, plus a backend change per unsafe endpoint. It ships additively behind the current responses.
2. **`api-error-design`**
   - Attacks: a client that timed out at 30s has no machine-readable signal for "retry safely, the first call may have succeeded".
   - Cost: one design session, plus an additive change to response bodies per endpoint class.
3. **`webhook-platform-design`**
   - Attacks: duplicate callbacks, and customers building private dedupe tables because the contract is silent. It covers the stable event ID, the payload envelope, and the at-least-once retry and dead-letter policy.
   - Cost: the largest session of the three. You are changing a published surface and owe a deprecation window on any payload change.
4. **`public-api-design-review`**
   - Attacks: you don't yet know which other unsafe POST/PATCH endpoints share the `POST /jobs` flaw.
   - Cost: hours over the spec or surface, with nothing to deploy.
5. **`api-reference-quality`**
   - Attacks: the new key header and the webhook delivery semantics shipping undocumented.
   - Cost: near-free if you have a committed OpenAPI spec, and a CI gate afterwards.
6. **`integration-error-observability`**
   - Attacks: customers who can't see their own request and delivery history, which is what turns a retry mess into a support ticket.
   - Cost: real engineering (a log store with retention) and a surface you then run forever.

**Re-rank stated out loud:** the default order opens with a surface audit. Your incident already names a class-2 failure, so the audit is demoted to rung 4 and scoped to sweeping for sibling endpoints. If Q3 comes back "nothing public yet", the audit is deleted and macro strategy moves to rung 1.

## Chain

None. The two problems are independent, and neither skill consumes the other's output. Run them in separate sessions, charging problem first. A chain here would be invented.

## Not now

- **`api-versioning-policy`**: unblocked if the idempotency fix needs a breaking change, or if Q4 comes back "nobody signs off on breaking changes". In that case it jumps to rung 1.
- **`sdk-portfolio-strategy`**: unblocked once `api-idempotency-retry` sets retry defaults, and only if you ship official SDKs. If the customer's library was their own, this doesn't apply.
- **`api-rate-limit-policy`**: unblocked if retry storms show up in traffic once clients start retrying under the new contract.

Everything else in the collection (marketplace, partner, specialist protocols, ecosystem) left the list. Nothing in your task gates it.

## Gap

- No skill covers the **customer remediation** (refund, apology, billing correction). That is a support and finance task, not platform design.
- Consumer-side dedupe guidance for your customers is excluded from `webhook-platform-design`'s scope ("consumer-side retry mechanics"). The skill covers your delivery contract. The how-to-dedupe tutorial would be a DevRel content task (`samber/developer-relations-skills`), if you want one.

## Open interview questions

I'd ask these one at a time, as tappable choices. Each shows what it would move.

1. **Who integrates today?** Customers' own engineers, partners, an open ecosystem, agents, or mixed. A customers-only answer deletes ecosystem work. A partner answer promotes `integration-error-observability`.
2. **Q2, the session goal, is answered:** decide what to do first. I assumed it matches the project goal. Correct me if it doesn't.
3. **Which surfaces are published under a compatibility promise?** REST and webhooks, from your description. Is anything else public?
4. **Who owns the API contract, and who signs off a breaking change?** An empty answer promotes `api-versioning-policy` to rung 1.
5. **Any hard date?** A GA date, a sunset, or an audit window. A date inside a quarter keeps the list tight on rungs 1 to 3.
6. **One-off or standing, and what is your effort ceiling?** "Hours only" cuts the list to two entries: rungs 1 and 4.
7. **What is already decided?** For example, "we already chose header-based keys". A decided item is removed, not ranked.

## Routines (dry-run, nothing installed)

1. **Pre-release API design review** → `public-api-design-review`
   - Trigger: event-based, on each spec diff or release candidate.
   - Output channel: a comment on the release PR.
   - It stops the next non-idempotent POST before it ships.
2. **Quarterly kickoff re-invocation** → this skill
   - Trigger: calendar reminder.
   - Output channel: the platform team channel.

I held the third and fourth routines back until a sunset date or real spec churn exists.

## Context artifact (draft, not written)

I did not write this into the `example-repo` repo, because that is not the Helios Dispatch project root. Save it as `developer-platform-context.md` at that root.

```markdown
# Developer platform context: Helios Dispatch
## Audience: unconfirmed (Q1)
## Published surfaces: REST (POST /jobs), outbound webhooks; version scheme unknown
## Spec locations: unknown
## Contract owner / breaking-change signer: unknown (Q4)
## In-flight (2026-10-08)
- Triple charge via client retry of timed-out POST /jobs -> api-idempotency-retry
- Duplicate outbound callbacks -> webhook-platform-design (separate session)
## Decided: duplicates are two contracts, not one fix
## Open: Q1, Q3-Q7
## Constraints: date / horizon / effort ceiling unknown (Q5, Q6)
## Stakeholders: VP (wants one fix; decision role unconfirmed)
## Session log
- 2026-10-08: cold kickoff; routed to api-idempotency-retry; interview pending
```

The artifact names no customer. If you save any of this to memory, keep customer names tied to their traffic, keys, and contract terms out of it.