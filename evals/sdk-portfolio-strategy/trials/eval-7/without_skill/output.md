**I can't name a vendor yet, because you didn't say which three you saw.** Tell me the names and I'll score them. Until then, don't sign on config-layer polish. It's the wrong tiebreaker.

## Why the config layer is a weak criterion

1. **You still need an OpenAPI spec.** Every vendor in this category takes OpenAPI as input, and the config file only adjusts what the spec describes. It doesn't replace it.
2. **The spec gets better the more you use it.** Generate it from code (or from a typed schema) instead of hand-writing it. Then the "giant document" problem goes away with any vendor.
3. **You configure once and ship the output forever.** Your customers' experience is the generated SDK, not your config file.
4. **Proprietary config is lock-in.** A portable OpenAPI spec lets you switch vendors later, while the config file doesn't move. Prefer the vendor where you need *less* config.

## What to compare instead

For an inference routing API, rank these roughly in this order:

1. **Streaming (SSE) quality in all four languages.** This is your core use case. Check typed events, cancellation, backpressure, mid-stream errors, and clean resource cleanup (Java `AutoCloseable`, Go context, Python async and sync).
2. **Idiomatic output per language.** Java and Go are where generators are usually weakest. Read the generated code as a Go or Java developer would. Check for builders and nullability in Java, and for context, error types and no `interface{}` leakage in Go.
3. **Type fidelity.** Test unions and discriminated unions (model-specific responses), optional versus nullable fields, and open enums, so a new model or provider field doesn't break old SDKs.
4. **Built-in reliability.** Look for retries with backoff, idempotency keys, timeouts, rate-limit headers, pagination, and request-ID exposure on errors.
5. **Custom code surviving regeneration.** You will want hand-written helpers, such as routing-policy helpers or auth wrappers. Find out how the vendor merges them on regeneration, and how often that breaks.
6. **Spec-change workflow.** Check whether it opens PRs per language automatically, whether it flags breaking changes, and how it handles semver and changelogs.
7. **Publishing and CI.** Look at npm, PyPI, Maven Central, and Go module tagging. Maven Central is the painful one, so ask who owns it.
8. **Exit terms.** Ask whether you own the generated code, whether the license lets you keep it and stop paying, and whether you can eject and maintain it yourself.
9. **Docs and examples generated from the spec.** This is a bonus, not a core criterion.
10. **Pricing shape.** "Roughly comparable" hides the differences. Ask whether it's per language or per SDK, what a fifth language costs, and what the overage terms are.

## The bake-off

At nine people, you can't afford a long evaluation, but you can afford about a week.

1. Take your real spec, or a realistic slice: auth, one non-streaming endpoint, one streaming endpoint, one paginated list, and one union response.
2. Have each vendor (or you, on a trial) generate all four SDKs.
3. Write the same small program in each language: a streaming completion, a forced mid-stream failure, a retry on 429, and a cancellation.
4. Add a spec change that includes a breaking change. Time how long regeneration and the review take.
5. Add one custom helper and regenerate. Check whether it survives.
6. Have your Go or Java developer rank the output blind, without knowing which vendor made it.

Score each vendor 1 to 5 on items 1 to 8 above. Weight streaming, idiomatic Go and Java, and exit terms double. Config ergonomics gets a weight of 1.

## Recommendation

- Sign the vendor with the best **streaming plus Go and Java output**, as long as its exit terms are acceptable.
- Treat config polish as a tiebreaker only.
- Ask for a short pilot or opt-out clause, such as 3 months, before an annual commitment.
- Move your spec to **code-generated OpenAPI** now, whichever vendor you pick.

Send me the three vendor names and any notes from the demos. I'll fill in the scorecard and flag the questions each vendor dodged.