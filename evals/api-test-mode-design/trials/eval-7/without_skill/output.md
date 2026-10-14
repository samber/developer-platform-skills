**Verdict:** Ship Prism this week, but don't call it "Sandbox." Call it "Mock server" and say what it doesn't do. The lifecycle and webhook testing integrators need is the part Prism can't do, so the real sandbox needs a small stateful service behind it.

## Why Prism doesn't cover the lifecycle

"Spec-valid responses for every endpoint" is true. It also isn't what integrators need, because their testing is about behavior across calls.

| Integrator need | What Prism does |
|---|---|
| Create → allocate → ship → deliver | Each call is independent. Prism returns the spec example (or random faker data in dynamic mode). `GET /orders/{id}` after a create doesn't reflect the order they created, and the status never advances. |
| Cancel mid-flow | No state means no rules. Cancelling a shipped order returns a canned 200 instead of the 409 or 422 production would give. The error paths that most need testing are the ones that can't be reproduced. |
| `shipped` and `delivered` webhooks | Prism doesn't dispatch webhooks. It doesn't execute OpenAPI callbacks, as far as I know (worth confirming against the version you'd deploy). Nothing ever calls the integrator's endpoint. |
| Stable IDs and payload consistency | IDs and totals aren't consistent across calls, so integrators can't test reconciliation. |

## Why the label matters

"Sandbox" tells integrators they can validate their integration here. They will build against it, see green, and hit the real behavior in production: wrong status transitions, missing webhooks, unhandled cancellation conflicts. Those become support tickets and a trust problem. "Mock server" sets the right expectation, and the docs page can say "stateless, no webhooks, schema validation only."

Prism is still useful for request validation, response shape and early client codegen. It's a good first stage, not a sandbox.

## Plan

**This week**
1. Ship Prism at `mock.hookline.dev`, labeled "Mock server," with a limitations box on the docs page.
2. Add a "Send test webhook" action, either an endpoint or a dashboard button. It POSTs a sample `shipped` or `delivered` payload to the integrator's URL, signed the same way as production. This is cheap and covers the webhook gap partially.

**Next, as the real sandbox (`sandbox.hookline.dev`)**
- A thin stateful service holds orders per sandbox API key. Prism, or a plain proxy, handles every endpoint that has no behavior.
- A real state machine covers create → allocated → shipped → delivered, plus cancel with the production transition rules and error codes.
- Advancement is deterministic. Either each state auto-advances on a short timer (seconds, not hours), or the integrator calls a sandbox-only `POST /sandbox/orders/{id}/advance`. Support both if you can.
- Webhooks are dispatched on every transition with production signing and retry behavior, so integrators can test signature verification and failed deliveries.
- Cancellation cases are scriptable: cancel before allocation, after allocation, after shipment (rejected).
- Isolation is strict. It uses separate keys, separate data, no production data, and rate limits.

I can't size the second stage without seeing your codebase. The core is small, but allocation logic and webhook signing and retries are where it grows. A spike on one order flow with webhooks would settle the estimate.

## Questions that would change this advice

- Does production already have a webhook dispatcher you can reuse with a sandbox flag? If so, the real sandbox gets much cheaper.
- Are there integrators waiting on this right now? If so, a "Send test webhook" button plus the honestly labeled mock may carry them until the stateful version ships.
- Do allocation outcomes vary in production, for example partial allocation or backorders? If they do, the sandbox needs a way to trigger each outcome.