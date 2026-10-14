# API Reference Audit: `POST /v1/transfers`, Fenwick & Vale Treasury API (2026-10-03)

## Verdict

**Not done.** The page reads well, but it documents the happy path and a design essay, and it leaves out the failure surface that your support queue is full of. Against the rubric it has 3 passes, 9 fails (3 blockers), 1 conditional and 2 rows I can't assess. The two errors support sees most, 402 `insufficient_funds` and 422 `currency_mismatch`, appear nowhere on the page. The KYC prerequisite behind most of those failures is also undocumented. The `Idempotency-Key` header, the most important operational fact on a money-moving endpoint, is missing too.

**Scope caveat:** I audited the page as you described it. I had no OpenAPI spec and no census, so I haven't checked for undocumented parameters beyond the header you named. I also haven't verified that the curl example matches the live API.

**Drift diagnosis:** I don't know whether this page is rendered from a spec or written by hand. The prose-heavy format suggests hand-written. If so, every finding below will recur until the reference renders from the spec.

## Row-by-row

| # | Row | Result | Severity | Finding |
|---|---|---|---|---|
| 1 | Description | ✅ Pass | | "Creates a transfer between two ledger accounts" is a clear purpose statement. |
| 2 | Parameters, presence | ❌ Fail | **Blocker** | The `Idempotency-Key` header is not listed. No parameter has its location stated (body vs header). |
| 3 | Parameters, depth | ❌ Fail | Major | `destination_account_id` has no description or example. `amount_cents` has a minimum but no maximum. `currency` has no format or allowed values, and it doesn't say whose currency it must match. `memo` has no example. The page says nothing about disallowed values, such as source equal to destination. |
| 4 | Request example | ✅ Pass | | A complete curl for $25.00 is shown. Check that it sends `amount_cents: 2500` and includes `Idempotency-Key`. |
| 5 | Response example | ✅ Pass | | A full JSON example is shown. The transfer object's fields are not described, and `status` values matter most for transfers. |
| 6 | Response codes | ❌ Fail | **Blocker** | Only 200 is listed. You know of 402 and 422. Probably 400, 401, 403, 404, 409 (key reuse with a different body) and 429 also apply. Confirm against the spec. |
| 7 | Error codes, cause and fix | ❌ Fail | **Blocker** | `insufficient_funds` and `currency_mismatch` have no cause and no fix. Your highest-volume support tickets are exactly these. |
| 8 | Per-language snippets | ⚠️ Conditional | Major if SDKs ship | Only curl is present. If you ship SDKs, curl alone is 0% parity. |
| 9 | Try-it | ❔ Not assessable | | The page doesn't say whether a console exists. |
| 10 | Version statement | ❌ Fail | Major | No API version or migration link. |
| 11 | Idempotency/retry | ❌ Fail | Major | The header is honored but not documented. Nothing says how long a key is retained, what a replay returns, or what a key reused with a different body returns. Integrators will double-send money or never retry. |
| 12 | Ordering constraints | ❌ Fail | Major | The source account must have cleared KYC before the call, and the page doesn't say so. The rubric rates this Major, but it is your top real-world failure cause, so fix it first. |
| 13 | Auth requirements | ❌ Fail | Major | No scopes or permissions are stated. |
| 14 | Quadrant shape | ❌ Fail | Minor | Four paragraphs on why you chose double-entry accounting are explanation on a lookup page. |
| 15 | Currency | ❔ Not assessable | | |

On row 14: the ledger essay is good writing and it is padding here. Move it to a concepts page and link to it. Keep one reference-shaped sentence, "each transfer posts two ledger entries", only if integrators can see or query those entries. Prose like this makes a page feel complete when it isn't.

## Two things to check on the API side

- **KYC failures may surface as the wrong errors.** If an uncleared source account returns `insufficient_funds` or `currency_mismatch`, the API is misleading integrators. Docs can only mitigate that, so consider a distinct `kyc_incomplete` error (see `api-error-design`). I'm inferring this from your support pattern, so confirm what the API actually returns.
- **The `currency` default may cause the mismatches.** `currency` defaults to USD. A caller with EUR accounts who omits it would get `currency_mismatch`. The page should say what the currency is validated against.

## Coverage (this page only)

| Dimension | Score | Gate |
|---|---|---|
| Parameters fully documented | 0 of 5 documented parameters fully documented (the header is missing, and the 5 listed lack location, example or constraints) | 100% |
| Responses documented, including at least one 4xx | 0 of 1 | 100% |
| Error codes with cause and fix | 0 of at least 2 known | 100% |
| Snippet parity | 0 SDK languages if SDKs ship, curl only | 100% |

## Benchmark comparison

- **Stripe:** the reference is generated from the spec, and the page has typed ID prefixes. Your `acct_8f2` example does follow that second practice. Stripe also embeds live test keys in samples, and your page doesn't mention anything like that.
- **Twilio:** each endpoint has a complete error table, and every snippet is CI-tested against a fake API server. This page has no error table and no tested snippets.

## Fix list, in order

1. Add a table of responses and errors: status, error code, cause, fix. Cover `insufficient_funds`, `currency_mismatch`, the 409 idempotency conflict, auth errors and validation errors.
2. Add `Idempotency-Key` as a documented header, plus a retry-safety note with key retention and replay behavior.
3. State the prerequisite: the source account must have cleared KYC, and say how to check this. Name the exact error returned when it hasn't.
4. Finish the parameter details, and add the version and required scopes.
5. Add SDK snippets if SDKs exist.
6. Move the ledger essay off the page.

## Remediation tier

I recommend the default rung: a spec lint gate plus contract tests. The lint gate should require a 4xx response, a description and examples per operation, so the missing error table can't ship again. Contract tests are the right fit for a money endpoint, but only if you have a sandbox or staging environment where tests can safely call it. If you don't, start with lint only and add contract tests once a sandbox exists.

If the page is hand-written, that moves the migration to spec-generated pages up, because no gate on the spec protects a page nobody regenerates.

## Questions that could change this verdict

1. Is there an OpenAPI spec, and is this page rendered from it or written by hand?
2. Which SDK languages do you ship?
3. Is there a sandbox environment tests can call?
4. What does the API return when the source account hasn't cleared KYC?
5. By when does this need to be trustworthy, and is it a one-off cleanup or a standing gate?