# Brightmast API Reference: Gate Scorecard

**Date:** 2026-10-03
**Tier:** lint gate only, which is the rung you stopped at. It is the correct rung for you. You have no environment safe for generated traffic, so the contract-test rung is deleted from the menu until one exists.

## Verdict

✅ **PASS on both gates in scope: census coverage and lint.**

Your reference renders from the spec, so drift is structural and not a recurring risk. That is stage 1 done. Lint at fail-on-warn with zero errors is stage 2 done. Your maturity score is **stage 2 of 5**.

Two items fall outside the pass/fail frame. Snippet parity (58%) is a recorded finding. Time-to-first-call (14 minutes) is a trend. Neither is a failed gate at this tier. Both are real gaps, listed below.

## Scorecard

| Gate | Threshold | Result | Status |
| --- | --- | --- | --- |
| Census: operations documented | 100% | 41/41 | ✅ Pass |
| Census: parameters (type, required, description, example) | 100% | 100% | ✅ Pass |
| Census: responses documented, at least one 4xx per operation | 100% | 100% | ✅ Pass |
| Census: error codes with cause and fix | 100% | 100% | ✅ Pass |
| Census: documented-but-removed endpoints | 0 | 0 | ✅ Pass |
| Lint gate | Zero errors at the chosen ruleset | 0 errors, fail-on-warn | ✅ Pass |
| Contract gate | Zero violations | No environment | ⚪ Out of scope at this tier |
| Snippet parity | 100% of operations x languages | 58% (Ruby and Go) | ⚪ Out of scope at this tier. Recorded as a **major finding** |
| Time-to-first-call | Under 10 minutes (trend, never gated) | 14 minutes | ⚠️ Trend: 4 minutes over target |

Out-of-scope gates are not failures. Holding a lint-only team to the contract or parity gates would reject the rung this audit prescribes for you.

## Caveats on the passes

The passes are real, but the evidence behind them has limits. Check these before the director reads "100%" as "fully trustworthy".

1. **The census measures the spec against the reference, not the spec against reality.** With no contract tests, nothing checks that the spec tells the truth. The lint gate only proves the spec describes itself. That is the stated limit of this rung, and it is why the contract gate returns once a sandbox exists.
2. **"Every error code" means every code in the spec.** Gateway logs, SDK internals and support tickets may name endpoints, parameters or error codes the spec lacks. Production APIs have been shown to carry undocumented-but-valid routes even when a spec exists (RESTSpecIT, 2024, a preprint). I recommend a one-off probe of those three sources. It costs no test traffic.
3. **Confirm the Vacuum ruleset covers the stage-2 minimum.** The minimum is per-operation description and operationId, a documented 4xx, and examples on parameters and schemas. Zero errors on a ruleset that skips example rules would be a weaker pass than it looks.
4. **I did not audit rubric rows you didn't report.** Request and response examples, version statements, idempotency and retry notes, ordering constraints and auth scopes are unscored. Idempotency and ordering matter more than usual because you write into municipal systems. "Is this retry-safe?" and "what must exist first?" are the questions an integrator cannot answer by trial. These are rubric rows 11 and 12, the ones audits habitually skip. Grade them next.

## Findings

### Major

- **Snippet parity is 58% across Ruby and Go.** About four in ten operation-by-language cells have no SDK snippet.
  - Get the per-language split. One language may be near 100% and the other very low.
  - Check that the covered 58% are real SDK calls and not relabeled curl. Relabeled curl does not count as parity.

### Trend, not gated

- **Time-to-first-call is 14 minutes, against the under-10 bound.** Your own before/after number is the metric. Do not reuse vendor multipliers (Postman's 1.7x-56x, Moneris's ~10x). They are vendor-produced and conflate the console with better onboarding generally.
- Parity gaps and the absence of a try-it console are plausible contributors. I cannot confirm that from these numbers.

## Benchmark comparison

| Mechanism | Brightmast |
| --- | --- |
| **Stripe:** reference generated from the spec | ✅ Have it |
| **Stripe:** live test keys embedded in samples, plus a try-it console | ❌ Blocked by the same missing safe environment |
| **Stripe:** typed resource-ID prefixes | Not assessed. Check whether your IDs are self-describing. |
| **Stripe:** docs quality in engineering ladders and review | Not assessed. This is stage 5. |
| **Twilio:** per-endpoint error tables | ✅ Likely met, since every error has a cause and fix |
| **Twilio:** CI-tested snippet repository against a fake API server | ❌ Missing. This is the main gap. |

## Path forward

Ranked in order of preference. The first is the cheapest, and it does not need the real municipal systems.

1. **Close the parity gap with a fake API server.** Twilio's mechanism is a CI harness where every snippet runs against a fake server before merge. A fake server never touches municipal systems, so it is safe for you.
   - It would raise snippet parity and keep it from regressing.
   - It does **not** replace contract tests. A fake server verifies your snippets against your spec, not your spec against the live API.
2. **Generate `x-codeSamples` from an SDK generator** if parity stays below target after step 1. See `references/tooling-catalog.md` for options.
3. **Promote the contract gate when a sandbox exists.** The re-promotion trigger is any surface a test suite may call: a staging environment, or a write-sandboxed tenant that cannot reach municipal systems. Until then it stays deleted.
   - Expect Schemathesis to surface roughly 5-15 issues on its first run (practitioner consensus). That is normal.
4. **Do stage 5.** Make spec and docs changes part of every API-changing PR, put documentation expectations into review, and re-audit quarterly against support tickets and docs-search misses.

## Bottom line for the director

- ✅ **Lint rung: complete.** Both in-scope gates pass.
- ⚠️ **The reference is complete and consistent with the spec.** It is **not yet verified against the live API**, and that is a deliberate consequence of the safety constraint.
- ⚠️ **Snippet parity (58%) is the biggest measurable gap.** Time-to-first-call (14 minutes) is over the 10-minute target.