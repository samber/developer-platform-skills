# Verdict for `/billing-internal`: no blocking design review

The public-partner-API gate does not apply to this service. Neither side is fully right, though. A light, non-blocking review applies, and the architecture lead gets one condition.

## Why the blocking review doesn't apply

The `public-api-design-review` skill sets review severity from two things: who consumes the API and what lifecycle stage it is at.

| Axis | `/billing-internal` | What the skill says |
|---|---|---|
| Audience | Internal only: your web app and one nightly batch job. Both live in your monorepo and you deploy both. | Internal-only or single-customer surfaces can skip formal review. This follows Google AIP-100. |
| Lifecycle | Alpha | Review is recommended at alpha and required and blocking at beta. An alpha may ship to a known user set without approval. |
| Combined posture | Internal alpha | "An internal alpha gets advisory feedback." The full blocking checklist is for a public beta. |

The blocking gate exists because of Hyrum's-Law exposure. On a public API you can't enumerate, contact, or migrate the clients. Here you know both clients, you own both, and you deploy them together. Any breaking change is one atomic monorepo PR, so the cost the gate guards against is close to zero.

Every other program the skill benchmarks keys review on audience and lifecycle: Google, Zalando (which excludes `component-internal`), Azure, Stripe and PayPal. None of them runs its external gate on an internal alpha.

## What the team should do instead

1. **Add a linter to CI.** Run a Spectral-class linter over the OpenAPI spec if one exists. It takes an afternoon, and it handles the mechanical findings, such as casing, pagination shape and error envelope. This is advisory.
2. **Get one human skim of the spec.** Use the skill's eight-dimension checklist, with every finding bucketed as Improvement. A Must-change needs a cited written rule, and an internal service with no adopted corpus has none to cite. Taste-based blocking comments are the failure mode the skill warns against.
3. **Keep a machine-readable spec.** The skill treats its absence as an Improvement finding.

## The architecture lead's legitimate concern

The risk to this decision is "internal permanently" turning out false. Two triggers should change the answer:

- **A consumer outside your control appears.** That could be a partner, a customer integration, or a service outside the monorepo and your deploy pipeline. Reclassify the API as partner or public, and the blocking review then applies at beta.
- **It goes to beta.** If your lifecycle model has a beta stage, GA-if-changed review follows the audience rule, so for a permanently internal API it stays skipped.

Write both triggers into the service's README or ADR as the re-promotion rule. Then the architecture lead is covered by a written trigger, not by gating today's alpha.

## Settling the deadlock

- **Decision:** `/billing-internal` needs no blocking review. It gets a CI linter plus one advisory skim.
- **Rationale to record:** internal-only audience, alpha stage, and consumers that are known and co-deployed.
- **Escalation:** if the architecture lead still insists, the skill's model has an explicit override authority. At Google, bypassing or imposing review is a named director-or-VP decision. Ask for that decision, not for continued debate.
- **Note on billing:** the skill's rule is about API-design review only. If the service handles money or sensitive data, your security review is a separate track and isn't waived by this answer.

I didn't have your spec or any real responses. This answer rests on the facts you gave: internal consumers only, alpha stage, and no external consumers.