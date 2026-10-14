# Quillon API reference: what to verify, and with what

Short version: don't set up Optic. Your CI gate checks that the docs site builds, which says nothing about whether the spec matches the API. Staging is available, so the right first investment is contract tests against it.

I followed the `api-reference-quality` skill. I haven't seen your spec or docs, so the findings below are expectations and the numbers are targets, not measurements.

## Verdict

- **"Generation keeps everything honest" is false.** Generation keeps the docs faithful to the spec. Nothing in your pipeline checks the spec against the API. A site rebuilds green from a spec that lies. The skill lists "accepting 'the docs site rebuilds green' as a gate" as a failure mode.
- **Optic is archived (January 2026).** The tooling catalog says not to recommend it.
  - Its job was spec-to-spec breaking-change diffing. That never tests spec against live API, so it wouldn't answer your second concern anyway.
  - Use **oasdiff** for the breaking-change diff.
- **Contract tests are in scope because you have staging.** The skill's default rung is lint gate plus contract tests. Contract tests would be dropped from the plan only if nothing could safely receive real requests, and staging fixes that.
- **Expect findings.** Practitioners report 5-15 issues on a first Schemathesis run against a production schema. That is practitioner consensus, not a study. Treat findings as normal, not as a sign the tool is broken.

## What to verify, in order

| # | Verify | Tool | What it catches | Gate |
|---|--------|------|-----------------|------|
| 1 | **Census, both directions:** spec vs live routes vs published reference vs SDKs | Gateway or access logs for the last 30-90 days, route table, SDK method list | Live-but-undocumented endpoints; documented-but-removed endpoints | 100% match |
| 2 | **Spec completeness** | Spectral or Redocly CLI (Vacuum if you want example rules) | Missing descriptions, `operationId`, 4xx responses, parameter examples | Zero errors; start at warn, flip to fail-on-warn |
| 3 | **Spec vs running API** | Schemathesis against staging | 500s on generated input, responses that violate the schema, undocumented status codes | Zero violations |
| 4 | **Breaking changes, spec vs spec** | oasdiff | Accidental removals or renames per PR | CI fails on undiffed breaking change |
| 5 | **Snippet parity** | Later stage, see below | Per-language samples that don't match real SDK usage | Recorded as a percentage for now |

Notes on each step:

1. **Census.**
   - Don't trust the spec as the whole truth. Spec-inference research (RESTSpecIT, a preprint) found undocumented-but-valid routes in shipped production APIs.
   - Cross-check against gateway logs and support tickets that name endpoints your docs lack.
   - The result is a table: operation, in spec, in docs, in SDKs, discrepancy.
2. **Lint.** Minimum rules are per-operation description and `operationId`, a documented 4xx on every operation, and examples on parameters and schemas. Run it on every PR that touches the spec, before the docs build.
3. **Contract tests.**
   - Schemathesis generates requests from the schema and checks that the API never 500s and that every response matches the documented shape.
   - Point it at staging, not production. Check for destructive operations (DELETE, bulk updates) and run those under a dedicated tenant with seeded data.
   - Portman is the alternative if you already live in Postman and Newman.
   - Dredd's author now recommends folding contract assertions into the existing test suite instead.
4. **Breaking-change diff.** This is what you wanted from Optic. oasdiff covers it, and it is a smaller part of the job than you'd expect.

## The AI assistant calling endpoints that don't exist

Neither the cause nor the cure is established yet. Run these in order:

1. **Census first (step 1).** Find out whether the invented endpoints are real in some other form (renamed, removed, undocumented). That tells you if it's a docs-truth problem or a pure model hallucination.
2. **Check the spec's own ambiguity.** Coding agents invent calls when `operationId`s are weak, enums are open, or descriptions mix up when to use an endpoint and how. That is a separate skill: `samber/developer-relations-skills@coding-agent-docs-optimization`. The same spec feeds both human and agent readers, so steps 1-3 above serve both.
3. **Ask the prospect for samples.** Get the actual invented calls. If they cluster around one pattern (for example `GET /employees/{id}/history` where you have `/audit-log`), that points to a naming gap you can fix in the spec.

I'd avoid promising the prospect that this fixes the assistant's behaviour. It removes the spec-side causes, nothing more.

## Rollout, strictly ordered

The skill says never recommend a later stage to a team missing an earlier one.

1. **Stage 1, source of truth: already done.** Your docs render from the spec. Confirm that no page is hand-edited, because that is the pass condition.
2. **Stage 2, lint gate.** Afternoon of setup. Warn first, then fail.
3. **Stage 3, contract tests on staging.**
   - Expect days of setup, plus a triage backlog from the first run.
   - Pass condition: CI fails on any generated-input 500, any schema-violating response, and any undiffed breaking change.
   - Decide whether this runs on every PR or nightly. Staging runtime on 74 endpoints will drive that choice.
4. **Stage 4, snippet parity and try-it.** Out of scope for now. Record parity as a measured percentage instead of failing a gate. Revisit when you know which SDK languages you ship.
5. **Stage 5, institutionalize.** Spec and docs change in the same PR, and a quarterly re-audit against support tickets and docs-search queries.

## Open questions

The skill asks these before auditing. Your answers could change the ranking:

- Which languages do you ship SDKs or snippets for, and are the snippets generated or hand-written?
- Does CI currently run any lint, or only the docs build?
- Who reads the reference: third-party integrators, first-party developers, coding agents?
- Is this a one-off cleanup or a standing gate? Is there a deadline?
- Can staging take writes? What does its data look like, and does it need seed fixtures for Schemathesis to reach deep endpoints?

## Report when you run it

Use the audit-rubric template: coverage percentages per dimension, a per-endpoint findings table with blocker/major/minor severities, and a comparison against Stripe and Twilio's checkable mechanisms. The Twilio one matters most for you: a CI-tested snippet repository with a fake API server validating every sample before merge.

The 100% census-coverage gate is this skill's own definition of done. It is not an industry benchmark.