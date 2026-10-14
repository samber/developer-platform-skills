# Recommendation: which SDK generator to sign, and what to compare

**Sign the vendor that treats your OpenAPI spec as the source of truth and can run self-hosted. Don't pick on config-file niceness.** I can't name the winner yet because you didn't say which three vendors you demoed.

## Why config niceness is the wrong tiebreaker

- Some generators (Stainless, Fern) put a proprietary config layer between your spec and the output. The config is a second artifact that has to stay in sync with the spec. The Speakeasy/WorkOS framing says that sync cost "is not theoretical" in programs where the schema changes often. Your inference API will change often.
- If the vendor disappears, the config investment doesn't transfer. The 2026 consolidation shows this risk is real:
  - Postman acquired Fern on January 8, 2026.
  - Anthropic acquired Stainless, announced May 18, 2026. It is winding down the hosted generator and has closed new signups. Customers kept their generated code but lost the pipeline that kept it in sync.
  - If Stainless is one of your three, it is off the list.
- Your trade-off is a false one. A clean config file doesn't replace the OpenAPI document. It sits on top of it, so you maintain both.
- The hand-maintenance pain is real, but fix it at the source. Generate the OpenAPI spec from your server code and lint it in CI. The config layer then costs you an afternoon, and spec drift never reaches the SDKs.

## What to compare

Order matters. Items 1 to 3 can eliminate a vendor outright.

1. **Spec as source of truth.** Check whether the SDKs build from a plain OpenAPI file with no vendor DSL required. Small overlays are fine if the spec still works standalone.
2. **Exit plan.** Check whether you can run generation self-hosted or air-gapped. On the mid-2026 snapshot, only Speakeasy and OpenAPI Generator could. Write down who regenerates your SDKs if the vendor vanishes, before you sign.
3. **Continuity and ownership.** Check who owns the vendor, whether it was recently acquired, and what the contract says about wind-down, code ownership, and notice.
4. **Idiomatic output in all four languages.** Judge Go and Java hardest, since generated output tends to read as "Java-like" in other languages. Check TS and Python runtime type safety and dependency count too.
5. **Bake-off on your real spec.** Run all three on your actual OpenAPI, not the demo spec. Include the hardest cases for an inference router:
   - SSE and streaming responses
   - retries and timeouts
   - error types
   - union and polymorphic types
   - pagination
   - auth
6. **Change handling.** Check whether an API change produces a regenerated SDK pull request, whether breaking changes are detected, and how releases are cut.
7. **Versioning.** Check that SDK SemVer is independent of your API version. Check that runtime support windows are configurable, such as Node LTS and the last N Go versions. Ask whether it can publish an SDK-to-API version mapping table.
8. **Docs snippet parity.** Check whether it emits per-language `x-codeSamples` for your reference docs, or whether you'd maintain those yourself.
9. **Pricing shape.** You said pricing is comparable, so just confirm whether it is per language and whether adding a fifth language is cheap. Pricing figures go stale quickly, so re-confirm them.

## How the decision falls out

- You are an AI/dev-tools platform. Python and TypeScript first, then Go and Java, matches the OpenAI/Anthropic pattern. Your four languages fit.
- Nine people can't hand-maintain four SDKs. Hand-maintaining many languages costs multiple engineer-years (a vendor-sourced, order-of-magnitude estimate). A commercial generator driven by the spec is the right default.
- Go and Java are the weakest links in the vendor map. If you don't have traffic or named customer requests for Java, consider shipping it second. That threshold is a self-set rule, not a published standard.
- Official means a support commitment, not hand-written code. Plaid's five official SDKs are generated with the free OpenAPI Generator.
- If procurement or security rules out a hosted vendor, or no vendor passes the bake-off, fall back to the free OpenAPI Generator. Budget time to curate its output.

## Next step

Tell me:
- which three vendors you demoed,
- whether you have a linted OpenAPI spec (CI source of truth, drifting, or none), and
- whether procurement can accept a hosted generator.

With those answers I'll name the pick. The vendor data I used is a mid-2026 snapshot, so re-check each vendor's current status before you sign.