# Sanity check: Mirelet platform plan

## Verdict

⚠️ **Don't ship this as written.** The ambition is fine. The order and the scope are the problem.

- You have 8 new surfaces (webhooks, 5 SDKs, GraphQL, widget) for 11 people.
- You would build them on a spec that goes stale and with no usage data.
- Each surface is a multi-year maintenance commitment, not a one-quarter task.

## What to change

### 1. Make the OpenAPI spec the source of truth first (about 1–2 weeks)

Everything else depends on this: SDKs, docs, the GraphQL schema, and widget types. A hand-edited wiki spec means the SDKs ship wrong on day one and drift further every release.

- Move the spec into the repo. Generate it from code, or write it first and validate the code against it.
- Add a CI lint (Spectral or similar) and a breaking-change diff check (oasdiff or similar). A PR that changes the API without changing the spec should fail.
- Add contract tests against staging.
- Treat the spec as a release artifact with a version.

### 2. Add API usage analytics now, not after launch (about 1 week)

"After the surfaces are live" is backwards, for three reasons:

- **Language choice.** You are about to pick 5 languages without knowing which ones your customers use. Even a crude breakdown by `User-Agent` shows it.
- **Baselines.** Without pre-launch numbers you can't say whether any launch worked. Friday's review will ask for outcomes, not shipped features.
- **Fintech reliability.** You need per-endpoint latency, error rates, and per-key volume anyway.

Minimum viable version, built from gateway or access logs:

- Per request: API key or customer ID, endpoint, status, latency, user agent, API version.
- Require an SDK identification header (e.g. `X-Mirelet-SDK: python/1.2.0`) so SDK adoption is measurable from the first release.
- Report: top endpoints, active keys per week, error rate per customer, language split.

### 3. Ship webhooks first. They have the best value for the risk.

Webhooks usually matter most to fintech infrastructure customers because they replace polling for async state like settlements, failures, and status changes. They are also easy to get wrong.

Before launch, you need:

- Signed payloads (HMAC with timestamp, to prevent replay).
- Retries with backoff, a dead-letter path, and a manual replay option.
- Stable event IDs so consumers can deduplicate.
- A documented ordering guarantee. Say plainly that you don't guarantee order, if you don't.
- A customer-visible delivery log, and a way to rotate secrets.
- A published event catalogue and an event schema in the spec (OpenAPI 3.1 supports webhooks).

### 4. Ship 2 SDKs, generated, not 5 hand-written

- **Generate** them from the spec (Stainless, Speakeasy, Fern, or openapi-generator). Hand-written SDKs in 5 languages is a team's worth of work.
- **Pick the first two from your analytics and customer list.** Python and Node/TypeScript are the usual default. If your buyers are banks, Java may beat Node. Check before assuming.
- **Go and Ruby can follow** if demand shows up. Go for infra buyers is a reasonable third.
- Each SDK still needs docs, examples, a release pipeline, semver, a changelog, and someone answering issues. Generation removes the typing, not the ownership.
- Define a deprecation and versioning policy before the first release. Once SDKs are public, you can't change it cheaply.

### 5. Defer GraphQL until a customer asks for it

REST already works. GraphQL here is mostly a second API to secure, version, and support.

- It adds abuse surface: query depth and cost limits, field-level authorization, and introspection exposure.
- It adds operational difficulty: N+1 queries, rate limiting by cost rather than by call, and harder caching.
- It sits awkwardly with money movement. Idempotency keys and mutation semantics are simpler and better understood in REST.
- Gate it on evidence: at least 3 named customers asking, or a concrete use case REST can't serve.

### 6. Defer the embeddable widget until the platform basics are solid

Embedding financial data in a customer's page is a security design problem before it is a UI problem.

- You need an auth model, most likely short-lived, narrowly scoped tokens minted by the customer's backend. Never ship long-lived API keys to the browser.
- You need an isolation choice (iframe vs. web component), CSP and CORS behavior, theming, and a browser support matrix.
- Plan a security review. If it touches card or bank-account data, check compliance scope early.
- It also needs the sandbox, auth, and docs groundwork from the earlier steps.

## Cross-cutting items the plan doesn't mention

- **Sandbox and test mode** for every new surface. Integrators can't safely trial financial APIs without one.
- **Idempotency, rate limits, and a versioning policy** documented once and applied everywhere.
- **Docs and quickstarts** per surface. For a developer product, docs are most of the product.
- **Support and on-call.** Who answers integration questions and who gets paged when webhooks back up? Eleven people can't absorb this without a named owner.
- **Release comms**: changelog, migration notes, and a status page.

## Suggested sequencing for the roadmap

| Phase | Scope | Exit gate |
|---|---|---|
| 1. Foundation (wks 1–3) | Spec in repo and CI, usage analytics, SDK header, versioning policy | Spec drift fails CI; weekly usage report exists |
| 2. Ship (wks 3–10) | Webhooks GA, 2 generated SDKs (chosen from data) | Delivery success rate and p95 delivery latency tracked; first integrations live |
| 3. Decide (wks 10–13) | Review adoption data, pick next SDKs, decide GraphQL and widget | Written go/no-go per item with demand evidence |

Check the calendar. If this quarter ends in December, holidays shrink your real working weeks. Budget for that.

## How to present it Friday

Suggested framing: **"We're building the platform foundation first, so every surface after it ships faster and can be measured."**

- Lead with the outcomes you'll measure (integration count, time-to-first-call, webhook delivery rate), not the list of surfaces.
- Show GraphQL and the widget as gated bets with explicit criteria, not as cancelled. That is easier to defend than a vague "later".
- If the board wants the big-platform story, the foundation phase is the headline. It is what makes the later launches credible.

## What I'd want to know before Friday

I'm working only from what you wrote. These would change the advice:

1. Who are your customers: banks, fintechs, or startups? That decides the SDK languages.
2. Has any customer asked for GraphQL, the widget, or a specific SDK?
3. How many engineers can work on the platform full time, and who owns on-call?
4. Is the raise tied to a public platform commitment you've already made?
5. Where does the OpenAPI spec come from today: code annotations, or purely hand-written?

If you share answers to 1–3, I can tighten the phase plan into a one-page roadmap slide.