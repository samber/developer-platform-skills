# Hexavolt docs quarter: plan

## Recommendation

Don't start with the console. Start by making the spec and the samples trustworthy, then build the console on top of them. Stripe's docs feel the way they do because the samples are correct and use the SDKs. The console is the smallest part of that.

Two facts in your setup change the order of work.

1. **The tabs show raw HTTP, not your SDKs.** The widget converts curl into each language's HTTP-client syntax. Python shows `requests`, TypeScript shows `fetch`, and Java shows `HttpClient`. You ship official SDKs in all three, so the tabs teach the one path you don't want people on. Stripe-style samples call `client.meters.list()`.
2. **The swagger file is "mostly right" and nothing checks it.** A try-it console renders the spec as a live product. Every drift between spec and API becomes a customer-visible failed request, and customers will read that as the API being broken.

Staging helps a lot. Your team can use it to verify samples automatically, and that is the main reason this order works.

## Phases (13 weeks)

### Phase 1: Make the spec trustworthy (weeks 1–3)

1. Add Spectral (OpenAPI lint) to CI. Fix the errors that block rendering first. Defer style rules.
2. Run a drift check: replay every documented endpoint against staging and diff status codes and response shapes against the spec. Tools like Schemathesis or Dredd do this.
3. Fix the drift. Decide where truth lives: spec as source, or code as source with the spec generated from it. Pick one.
4. Add a CI job that reruns the drift check nightly against staging. This is your contract test, and it is cheap.
5. Add realistic `example` values to every schema (meter IDs, kWh readings, timestamps). The console and the samples both pull from these.

**Exit criterion:** the drift check is green in CI, and a spec change that breaks it fails the build.

### Phase 2: Real SDK samples, executed in CI (weeks 3–7)

1. Write one canonical sample per operation as a real SDK file in Python, TypeScript and Java. Don't put them inline in markdown. Keep them in a `samples/` directory.
2. Run those files in CI against staging with a throwaway key. A sample that doesn't run doesn't ship.
3. Replace the curl-to-HTTP widget with a component that reads those files. Keep a curl tab, since people paste curl into support tickets. Retire the converter.
4. Start with the 10–15 endpoints that make up the quickstart and the top traffic. Check page analytics first. Then extend to the full API.
5. Fix SDK gaps as you find them. Missing methods, awkward naming, or stale SDK versions will surface here. Feed them to the SDK owners as tickets and don't paper over them in docs.
6. Add SDK version pinning to the samples so a new SDK release can't silently break a page.

**Exit criterion:** every sample on the quickstart and top endpoints is SDK-based and has run green in CI within the last 24 hours.

### Phase 3: Stripe-feel layout and personalization (weeks 7–9)

1. Build the three-pane layout: prose, then the sample and response. Docusaurus can do this with a custom theme component.
2. Add a persistent language preference, so the choice carries across pages.
3. Fill in the signed-in user's sandbox key and meter IDs where possible. This is the feature people remember from Stripe, and it needs a session or key-lookup endpoint.
4. Show real response payloads next to each sample. Generate them from the staging run in Phase 2 so they can't go stale.

### Phase 4: Try-it console (weeks 9–12)

1. Scope it small: one request builder per endpoint, driven by the spec, sending to a **sandbox**, not staging. "Safe for the team" is not "safe for the public." Anonymous visitors need rate limits, a sandbox tenant with synthetic data, and a key scoped to it.
2. Decide the auth flow first: sign-in with a sandbox key issued per user, or paste your own key. This is the real design question, and it has product and security owners beyond docs.
3. Build on an existing renderer (Scalar, Redocly, or Swagger UI behind a theme) before considering a custom one. Customizing a renderer costs about a week. Building from scratch costs about the quarter.
4. Instrument it: requests sent, errors by endpoint, and sandbox-to-production-key conversion.

### Week 13: Buffer and measurement

Use it for slippage, a docs-feedback pass, and a read of the metrics below.

## Risks

| Risk | Mitigation |
|---|---|
| Spec drift shows up in the console | Phase 1 comes first and nightly checks continue |
| Sandbox abuse (scraping, load) | Per-IP and per-key rate limits, synthetic data only |
| SDK gaps block good samples | Treat as tickets to SDK owners from week 3 |
| Hand-edited docs diverge from samples again | Samples live in files that CI executes; pages only import them |
| Console scope creep eats the quarter | Phase 4 has a hard stop at week 12 |

## Success metrics

- Percentage of samples executed green in CI (target: 100%)
- Time from signup to first successful API call
- Support tickets tagged "docs wrong" or "sample doesn't work"
- Console sessions that end in a sandbox request, then in a production key

## Questions for you

1. Which side is the source of truth, the code or the swagger file?
2. Is there a sandbox environment separate from staging, or would the public console hit staging directly?
3. Who owns the SDKs? Phase 2 will generate tickets for them.
4. Are the three SDKs currently at parity on all endpoints?