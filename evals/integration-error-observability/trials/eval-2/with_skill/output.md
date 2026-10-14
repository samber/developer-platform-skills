# Palmate request-ID fix: make `X-Palmate-Request-Id` resolve everywhere

I followed `integration-error-observability`, using steps 1–3 and the correlation-ID and visibility-surface references. I didn't read your codebase, and I couldn't ask the skill's clarifying questions, so the assumptions I made are listed at the end. Correct them and the ranking may change.

## Diagnosis

The skill's negative example matches your situation. Its second cause says "each internal service generates its own, so the returned ID belongs to a hop that has no record of the failure." Three gaps explain the "half the time" figure:

1. **The ID isn't carried through.** The edge assigns it, then each service mints its own. Support searches service logs, so any failure whose log lines carry only a service-minted ID can't be found by the edge ID.
2. **The ID stops at your boundary.** The tax engine and card processor sit on most requests. Failures there are logged under their IDs, or under none.
3. **No surface lets the partner resolve it.** Partners can only paste the ID into a ticket.

Header scope is a smaller issue. You return the ID only on 4xx/5xx. The skill echoes it on every response, because "200 but wrong" is a real ticket class.

## Fix, in build order

Ranked by the skill's step-3 ladder. Echo is the default rung. Searchable-in-log is promoted because the ID is already returned. Propagation to sub-processors is promoted because your support answer is effectively "that's in another system" (the tax engine and card processor).

### 1. One ID, minted once, never regenerated (days)

- **Mint at the edge only.** Format: `req_` plus a random UUIDv4 body. It is opaque and carries no sequence or timestamp.
- **Services read it, never mint it.** Put this in the shared HTTP/gRPC middleware and logger, not in each service:
  - Read `X-Palmate-Request-Id` from the inbound call.
  - Put it in the context.
  - Stamp it on every log line as a structured `request_id` field.
  - If it is missing, mint one but tag `request_id_origin=service_minted` and increment a metric. That metric should be zero. Any non-zero value is a hole to find.
- **Guard against drift:**
  - A lint or AST rule that bans ID generation in request-scoped code outside the edge.
  - A contract test per service: send a request with a known ID and assert that every log line and outbound call carries it.
- **Async paths:** queue messages, cron-triggered retries and background jobs carry the ID in the message envelope. Internal retries reuse the original ID and add an `attempt` field. A fresh ID splits one failure into unlinked fragments.
- **Client-supplied IDs:** don't let a client value replace ours, because uniqueness is what makes lookup work. Accept an optional `X-Palmate-Correlation-Id` for partners who want to join their logs to ours. Store it as a searchable field and echo it back. The request ID stays ours.

### 2. Echo on every response (hours)

- Return `X-Palmate-Request-Id` on **all** responses, including 2xx.
- Include edge-generated failures: 502/504, auth rejects, rate-limit 429s. They are the easiest ones to miss.
- Also put it in the error body. Header-only IDs are lost when a partner's client logs the parsed body and drops the headers. `api-error-design` owns the payload shape, so coordinate with it rather than redesigning it here.
- Never change the header name once documented. Partners write parsers against it.

### 3. Make support's lookup one search (1–2 weeks)

- Index `request_id` in the central log store. Every service, the edge, and the async workers must write to it.
- Give support a single "search by request ID" view that returns every hop's log lines in order. Then "not in anything I can search" can't happen.
- Document the lookup path next to the error docs. That is where a partner is when they need it.

### 4. Cover the tax engine and card processor (1–2 weeks)

The skill says to forward the same identifier on downstream calls and keep it on retries, and to log it on both sides of every boundary. External vendors may not accept your ID, so do both of these:

- **Send ours where the vendor allows it:** a metadata field, a reference field, or a custom header. For the card processor, derive the idempotency key from the request ID plus the operation, so retries stay linked and safe.
- **Capture theirs on return:** each vendor mints its own request ID and returns it. Log it as a child link on our request: `{request_id, vendor, vendor_request_id, vendor_status, latency_ms, attempt}`.
- **Log outbound calls even when they time out or fail**, not just successes. The failing hop is exactly the one the partner can't see.
- **Result:** one search on `req_…` shows the tax-engine and processor calls and the vendor IDs. When a vendor failure needs escalating, support already holds the vendor's ID.

### 5. Partner-facing request log (the part that fixes the root cause for partners)

This is skill step 2, the request log. It is the default because you have no webhook-only complaint here. The 4xx/5xx tickets are synchronous.

- **Searchable by `req_…`** in the developer portal. Show the same ID the partner got in the header, never an internal primary key.
- **Row fields:**
  - timestamp (UTC)
  - method and path
  - status
  - machine-readable error code
  - request ID
  - app/API key and account
  - latency
  - a vendor-hop summary, such as "tax engine timeout after 3 attempts"
- **Metadata-only to start.** This is billing data, so card data, tokens and PII are a legal question. Strip credentials unconditionally and mask PII visibly. Treat the redaction rules as a published contract once partners build on them.
- **Access:** include the partner engineer who maintains the integration, not only the account owner.
- **Retention:** longer than it takes a partner to notice a failure. Billing partners often notice at reconciliation, so I'd pick at least 30 days and publish the number.
- **Tenant isolation:** enforce it structurally in the store, not by a query filter in application code.

## Verify it worked

- **Gate: ID resolvability.** Take 50 real IDs from recent 4xx/5xx responses and look each up as support would. Include some whose failure came from the tax engine or processor. The target is 50 of 50. Run it before and after. Today you should see roughly half.
- **Also a gate:** the `service_minted` metric stays at zero in steady state.
- **Trend: self-serve deflection.** Re-classify the next batch of tickets and compare against your own baseline. The skill says no industry benchmark exists, so don't compare against a published number.

## Out of scope (not needed to fix this)

Replay, rate aggregation, partner alerts and the fleet view are the skill's steps 4–6. Add them later if the ticket classification shows the need. I'd skip them for now.

## Assumptions to confirm

1. **Ticket pile:** I assumed it is mostly synchronous 4xx/5xx and not webhook delivery. If webhooks are a large share, the delivery-attempt log moves ahead of the request log.
2. **Internal propagation:** I assumed services share a common middleware layer or can adopt one. If there are many languages with no shared library, step 1 takes longer and the contract test matters more.
3. **Vendors:** I assumed both vendors accept a reference or metadata field and return their own request IDs. If either doesn't, capturing theirs on return is the only option.
4. **Legal:** I assumed bodies can't leave your tenancy until legal signs off, so step 5 is metadata-only.
5. **Partner mix:** I assumed ISV partners are included. If they are, the access model in step 5 and later alerting matter.
6. **Retention:** 30 days is my guess. Set it from how long your partners actually take to notice a failure.