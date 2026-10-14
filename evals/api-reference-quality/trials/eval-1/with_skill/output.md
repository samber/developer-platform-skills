# API Reference Audit: Ledgerline, 2026-10-03

Next action: send me the OpenAPI 3.1 file, the 49 page URLs (or a Contentful export of those entries), and the Python and Node SDK method lists. With those, the census takes about an afternoon.

I have not scored coverage, because I have only your description, not the spec or the pages. Every percentage below is marked "not measured". I won't invent them.

## Verdict

⚠️ **The reference is hand-maintained, so every finding will recur.** Contentful pages updated "when PMs remember" is a second copy of the contract. Nothing stops it drifting from the spec, and fixing pages once does not change that.

**"Mostly polish" is not supported by what I know.**
- Page quality and traffic measure only pages that exist. An undocumented operation gets zero traffic.
- The rubric rows that matter most (response codes, error cause and fix, retry safety, ordering) can't be seen from how well a page reads.
- Corpus priors point to substantive gaps:
  - OASQuali (peer-reviewed, 2,529 public specs): mean documentation quality 67.11%.
  - Postman 2024 (survey self-report): 39% name inconsistent docs their biggest roadblock, and 44% read source code.
  - Both are priors, not Ledgerline measurements.

**52 operations against 49 pages is at least a 3-operation gap, if pages map 1:1 to operations.** It could be larger:
- One page may cover several operations.
- Pages may document removed endpoints. These are blockers too, and they hide live-but-undocumented operations behind a deceptively close count.
- Do not read "49 vs 52" as "3 missing".

Recommended remediation: **migrate to spec-rendered docs, with lint and contract gates on top** (see Remediation).

## Census (to fill in)

| Operation | In spec? | In reference? | In SDKs? | Discrepancy |
| --- | --- | --- | --- | --- |
| 52 rows | yes | not measured | not measured | not measured |
| Pages with no spec match | no | yes | not measured | documented-but-removed: blocker |

I will also probe beyond the spec. Sources: gateway logs, SDK internals, and support tickets that name endpoints the docs lack.

The spec is "current from code annotations", but that is not verified. I'll run Spectral or Vacuum on it before trusting it as the census source.

## Coverage scores

| Dimension | Score | Gate |
| --- | --- | --- |
| Operations documented | ≥3 gap, rest not measured | 100% |
| Parameters fully documented | not measured | 100% |
| Operations with all responses (incl. ≥1 4xx) | not measured | 100% |
| Error codes with cause and fix | not measured | 100% |
| Snippet parity (52 operations × 2 languages = 104 cells) | not measured | measured % at this tier |

## Findings

No per-endpoint findings yet. These are hypotheses to check first, not findings. They are the likeliest misses for a payouts API:

1. **Retry and idempotency note (row 11, major).** A retried payout can pay twice. Check every POST for an idempotency-key statement.
2. **Ordering constraints (row 12, major).** Examples: create the beneficiary or funding source before the payout, and the required state before cancel.
3. **Error cause and fix (row 7, blocker).** Check for per-endpoint error tables, not only a global error page.
4. **SDK-based snippets (row 8, major).** Check that Python and Node snippets call the SDK, not relabeled curl.
5. **Version statement and scopes (rows 10 and 13, major).**

## Benchmark comparison

| Mechanism | Ledgerline |
| --- | --- |
| Stripe: reference generated from spec | No, hand-written in Contentful |
| Stripe: live test keys in samples | Unknown. A sandbox exists, so it is feasible. |
| Stripe: typed ID prefixes | Check the spec and examples |
| Stripe: docs quality in the engineering ladder | Unknown |
| Twilio: per-endpoint error tables | Unknown |
| Twilio: CI-tested snippet repository | Unknown. Ask how snippets are made. |

## Remediation

The default rung is lint gate plus contract tests. Two answers move it:

- **Hand-maintained reference promotes the full migration (stages 1+4).** Drift is structural, and no gate on the spec protects pages nobody regenerates.
- **The sandbox keeps contract tests on the menu.** They would be deleted only if no safely callable environment existed.

Question 6 (deadline, one-off vs standing gate, effort) is unanswered, and it can still re-rank this. Stages are strictly ordered:

1. **Adopt the source of truth.** Render the reference from the spec (Redocly, Mintlify, ReadMe or similar). The tech writers keep guides and narrative layered over it (the Twilio model). Pass: no page is edited independently of the spec.
2. **Lint gate.** Spectral, Redocly CLI or Vacuum on every PR touching the spec. Start at warn, then fail-on-warn. Pass: zero errors, or ≥80/100 on RateMyOpenAPI (a tool default, not an industry bar).
3. **Contract tests against the sandbox.** Schemathesis plus oasdiff for breaking changes. Expect 5-15 findings on the first run (practitioner consensus). Pass: no 500s, no schema violations, no undiffed breaking change.
4. **Snippet parity and try-it.** Python and Node `x-codeSamples` from an SDK generator, plus a console with sandbox test keys. Pass: 2 languages × 52 operations. Vendor try-it multipliers (Postman 1.7x-56x, Moneris ~10x) are named case studies, not controlled results. Measure your own time-to-first-call instead.
5. **Institutionalize.** The spec change and its docs change land in the same PR, docs expectations enter PR review, and you re-audit quarterly.

I would run the linter now as an audit instrument, since it takes about 15 minutes and shows how much to trust the spec. That is separate from the rollout order.

## Questions I still need answered

1. How are the Python and Node snippets produced: generated from the spec, or hand-written per page?
2. Which CI gates touch the spec or docs today (lint, contract tests, breaking-change diff, none)?
3. Who reads the reference: third-party integrators only, or coding agents too? If agents, I route spec annotations to `coding-agent-docs-optimization`.
4. Question 6: deadline, one-off cleanup or standing gate, and effort you can spend, including appetite for leaving Contentful.

Next: attach the spec and the 49-page list, and answer question 1.