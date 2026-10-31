# Router review for the partners variant (Brackwater go-live, Nov 18)

**Verdict:** yes, change it before Nov 18. The current config sends every client header, including the user's `Authorization` token, to a third-party insurer. It also has no timeout, so one slow insurer can break your 800 ms p95.

I reviewed only the config and SDL you pasted. I haven't run it, and I haven't checked key names against your exact Router 2.x version. Check each one in the docs before merging.

## Must fix before Nov 18

### 1. Header propagation leaks credentials to Brackwater

`matching: ".*"` forwards every client header to every subgraph. That includes cookies, `Authorization`, internal tracing headers and anything a client or proxy adds. Router sends them to all four insurers' endpoints, outside your trust boundary.

The extra `named: Authorization` rule does nothing, because the regex already covers it.

- **Use an allowlist per subgraph, with nothing in `all`.** A subgraph added later then gets no user token by default.
- **Give each insurer its own service credential,** not the fleet manager's token. Load it from an env var, and rotate it separately from user tokens.
- **Name what you propagate to the nine internal subgraphs.** Authorization and a request ID are the usual set.

```yaml
headers:
  subgraphs:
    # repeat for each of the 9 internal subgraphs
    vehicles:
      request:
        - propagate: { named: Authorization }
        - propagate: { named: x-request-id }
    brackwater:
      request:
        - insert:
            name: x-tallowmere-partner-key
            value: "${env.BRACKWATER_API_KEY}"
        - propagate: { named: x-request-id }
```

Prove the fix with a capture proxy or a logging stub standing in for Brackwater. Send a request carrying `Authorization`, `Cookie` and `X-Foo`, and check that only your two headers arrive.

### 2. No timeout: a slow insurer breaks the SLA

Subgraph timeouts default to about 30 s, so one hung insurer holds the whole query open.

Latency is also serial in front of Brackwater. Router has to fetch `dateOfBirth` and `licenseClass` from the owning internal subgraph first, because of `@requires`. Then it calls Brackwater. The insurers run in parallel after that, so the slowest one sets the tail, not the sum.

```yaml
traffic_shaping:
  router:
    timeout: 2s          # placeholder: hard cap on the whole request
  all:
    deduplicate_query: true
    timeout: 1s          # placeholder: internal subgraphs
  subgraphs:
    brackwater:
      timeout: 400ms     # placeholder: see below
```

To pick the real numbers:

1. Measure the dashboard query's current p95 without quotes.
2. Subtract that from 800 ms. The remainder is the budget for the extra DOB hop plus the insurer call.
3. Ask Brackwater for a contractual p95. Set the timeout slightly above it, not far above.

Use the same pattern for the other three insurers.

### 3. `brackwaterQuote: Quote!` can wipe out the vehicle or driver

When a non-null field errors or times out, GraphQL nulls its parent. If the parent is itself non-null, the null climbs further. A Brackwater timeout could null a `Driver`, then the whole `drivers` list, then the dashboard data.

- **Make every insurer field nullable** (`Quote`). Don't ship non-null for fields that depend on a third party.
- **Make the quote a business-level result,** not an error. For example, a "no quote available" state.
- **Consider `@defer`** on the quote fragment, so the dashboard renders at once and quotes stream in. This also takes insurers off the 800 ms path. Check your clients support incremental delivery first.

This one is a schema-contract change. Make it a hard requirement in Brackwater's onboarding, because the router config can't fix it.

### 4. The `@requires` fields send driver PII to a third party

Router will send Brackwater `{__typename: "Driver", id, dateOfBirth, licenseClass}` for every driver in the query. For a 500-driver fleet, that's 500 dates of birth in one request.

- **Minimise.** Ask whether Brackwater needs an exact date of birth. An internal computed `ageYears` or age band as the required field would shrink what you share. You can then say "we send age, not DOB".
- **Confirm the legal basis before launch.** The data subjects are drivers, not the fleet manager logging in. Check controller/processor roles, the data processing agreement, and whether the driver or fleet needs to opt in. If your drivers are in the EU or UK, GDPR applies. Get a privacy review.
- **Define behaviour when the data is missing.** If a fleet opts out or `dateOfBirth` is null, Brackwater must return a null quote, not an error.
- **Check the SDL snippet.** `licenseClass` appears in `@requires` but isn't marked `@external` in what you pasted. In Federation 2 every field in `@requires` must be `@external`, so composition should fail. Confirm it's just a trimmed snippet.

### 5. Treat each insurer's `@requires` as a data-access request

Any insurer subgraph that composes can add `@requires` on any `Driver` field, such as email or address. Router will then fetch it and send it to them.

- **Don't let insurers publish to your supergraph directly.** Route publishes through your CI.
- **Add a CI check** that fails when an insurer subgraph's `@key`, `@external` or `@requires` fields leave an approved list. Per insurer, the starting list is `id`, `dateOfBirth` (or `ageYears`) and `licenseClass`.
- **Use `@authenticated` or `@requiresScopes`** on the quote fields and the sensitive source fields.

## Should fix before launch

### 6. Add query limits, because quotes can be amplified

Quotes may be billable, and each one is a pricing call. Aliasing `brackwaterQuote` across many drivers multiplies those calls. The current config has no `limits`.

```yaml
limits:
  max_depth: 15
  max_aliases: 30
  max_root_fields: 20
  max_height: 200
```

The values are starting points. Tune them against the real dashboard query, which must still pass. Also add a per-subgraph rate limit sized to Brackwater's contract (`traffic_shaping` supports rate limits per subgraph). If you're on GraphOS Enterprise, demand control with `@cost` is the better fit.

### 7. Check what `deduplicate_query` does here

Deduplication merges identical in-flight subgraph requests. It's useful for avoiding duplicate paid quote calls.

- **With `matching: ".*"` it does almost nothing.** Requests differ by per-user headers, so they never match. It starts working after fix #1.
- **Verify the key first.** Check the dedup key in the docs for your version. Then confirm Brackwater's response depends only on the request body and your service key, never on a hidden per-user input.
- **Don't cache quotes.** Leave entity caching off for insurer fields.

### 8. Harden the rest

- **Keep subgraph errors redacted.** That's the default. Don't set `include_subgraph_errors` for insurers, since their error text would reach your clients.
- **Use TLS and the right URL.** Set the insurer URL with `override_subgraph_url` and use `https`. Add mTLS if Brackwater supports it.
- **Keep logs and telemetry free of request bodies.** Subgraph bodies contain DOBs. Check that no subgraph-request logging or tracing attribute captures them.
- **Turn off the homepage and sandbox on a public router:** `homepage.enabled: false`, `sandbox.enabled: false`. `supergraph.introspection: false` is correct as is.
- **Confirm authentication.** Your config shows no `authentication.router.jwt` and no coprocessor. If a gateway in front handles auth, say so. If not, add JWT verification at the router.

## Suggested `router.yaml` (placeholders marked)

```yaml
supergraph:
  introspection: false
homepage:
  enabled: false
sandbox:
  enabled: false

headers:
  subgraphs:
    # one block per internal subgraph, repeated 9 times
    vehicles:
      request:
        - propagate: { named: Authorization }
        - propagate: { named: x-request-id }
    brackwater:
      request:
        - insert:
            name: x-tallowmere-partner-key
            value: "${env.BRACKWATER_API_KEY}"
        - propagate: { named: x-request-id }

traffic_shaping:
  router:
    timeout: 2s              # placeholder
  all:
    deduplicate_query: true
    timeout: 1s              # placeholder
  subgraphs:
    brackwater:
      timeout: 400ms         # placeholder, set from Brackwater's p95

limits:
  max_depth: 15              # starting values, tune on the real dashboard query
  max_aliases: 30
  max_root_fields: 20
  max_height: 200
```

## Pre-launch tests (before Nov 18)

1. **Header capture:** the stub Brackwater receives only the allowlisted headers (#1).
2. **Fault injection:** Brackwater returns 500, hangs past the timeout, returns a malformed body, and returns a null for a driver. The dashboard still renders vehicles and drivers, with `brackwaterQuote: null` (#2, #3).
3. **Load test:** run the dashboard query for your largest fleet with a 300 ms Brackwater stub and check p95 stays under 800 ms. Repeat with the stub at the timeout limit.
4. **Alias abuse:** a query with 100 aliased quotes is rejected or rate-limited (#6).
5. **Composition check:** `rover supergraph compose` passes, and `licenseClass` is `@external` (#4).

## Questions for you

1. Does the dashboard query include the quote fields, or is it a separate query? That decides whether `@defer` or a separate query is the right answer to the SLA.
2. What is the dashboard's p95 today, without quotes?
3. Who publishes the insurer subgraphs: you or the insurers?
4. Is the partners router public, or behind a gateway that does auth?
5. Will Brackwater accept age or an age band instead of an exact DOB?
6. Are your drivers in the EU or UK, and has privacy or legal reviewed sharing DOB with insurers?

Answers to 2 and 5 would let me set concrete timeout and field values.