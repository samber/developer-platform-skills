# Nuvexa rate-limit header strategy

## Decision

**Emit both families. Do not drop the legacy `X-RateLimit-*` trio.** Add `RateLimit` and `RateLimit-Policy` next to it.

The "IETF fields only" option is off the menu in this skill. It is not ranked last. I'm applying that rule here because your inputs don't override it.

## Why not IETF-only

1. **40% of your traffic isn't your SDKs.** The skill allows relaxing the legacy trio's compatibility argument only when the audience is about 90% your own SDKs. At 60%, you don't control the parse for the other 40%. Those clients, and every old SDK version already installed, read `X-RateLimit-*`. Removing it makes them lose the signal with no visible error.
2. **Adoption is thin.** GitHub emits only the legacy family. Stripe emits neither. Cloudflare (September 2025) is the one Tier-1 adopter I can cite.
3. **The spec can still change.**
   - `draft-ietf-httpapi-ratelimit-headers` is draft-11 (23 May 2026) and expires 24 November 2026.
   - It is Standards Track but not an RFC.
   - The syntax has already changed once (draft-08 moved to the quoted structured-field form).
   - The latest directorate review was marked "not ready".
4. **"Cruft" undersells the legacy headers.** They are the only signal that most existing clients parse. Dropping them breaks those clients and gains nothing a client can observe.

## Why your CDN point supports both families

Cheap structured-field emission at the edge is the condition that promotes the both-families rung. The usual cost of that rung is effort and ongoing header maintenance, and your edge removes most of it. So you get the standards-track benefit without removing anything.

`RateLimit-Policy` also lets a well-behaved client self-throttle before its first 429, which the legacy trio can't express. For a payments API, that matters.

## Header spec

Every response from a limited endpoint:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1790000000
RateLimit-Policy: "default";q=100;w=60
RateLimit: "default";r=95;t=23
```

The numbers are placeholders. Use your real tier values.

- **Reset semantics.** The two families reset differently.
  - `X-RateLimit-Reset` is a UTC epoch timestamp (GitHub's convention). Pick that form and document it.
  - `RateLimit`'s `t` is seconds until reset.
  - Both must describe the same instant.
  - Never change `X-RateLimit-Reset` semantics silently. It's the one change that needs its own major announcement.
- **Throttle response.** HTTP 429 with `Retry-After` in delay-seconds, never an HTTP-date. `Retry-After` takes precedence over any computed reset when both are present.
  - Don't let the edge cache 429s (RFC 6585).
  - The body is the standard error envelope with `rate_limit_exceeded`. That envelope belongs to `api-error-design`.
- **Advisory only.** Publish the headers as planning signals, not commitments. The draft says the values "are informative and MAY be ignored". "95 remaining" doesn't promise 95 successful calls.
- **Retry guidance in the docs.**
  - Honor `Retry-After`.
  - Use exponential backoff with jitter.
  - State the consequence for hammering.

## Using the 60% SDK share

The SDK share lets you move the fleet first, without a breaking change.

1. **Now.** Ship both families at the edge. Document `RateLimit-Policy` as forward-looking, using its current field names.
2. **Next SDK release.** SDKs read `RateLimit`/`RateLimit-Policy` first and fall back to the legacy trio. They keep honoring `Retry-After`.
3. **Later, and only if triggered.** Consider deprecating the legacy trio under the change-notice rules below.

Do not publish a removal date now. Neither trigger below has fired.

## When IETF-only comes back on the menu

Re-open the decision when either of these happens:

- The draft reaches RFC status.
- A second Tier-1 platform adopts the fields.

Even then, treat legacy removal as a limit-header change with real notice, not a cleanup:

- Use at least 6 weeks, scaled to blast radius. That is the Stripe-derived floor, and it is a minimum. Given the 40% you don't control, I'd go longer.
- Announce it in the changelog and email affected API keys.
- Roll out in observe, baseline, refine stages.
- Gate removal on measured legacy-header consumers, using SDK-version share from User-Agent. No industry threshold exists, so baseline your own first month.

## Gates

- **Machine-readability.** 100% of throttle responses carry a 429 plus `Retry-After`. A single undocumented path fails the gate.
- **Docs and enforcement parity.** Every header you emit is documented. Every enforced limit, including any secondary or abuse guard, appears in the docs.

## Open questions that could change this

I haven't been told the answers to these. None of them reverses the both-families call, but they change the details:

1. **Time and effort ceiling (Q8).** A hard date favors shipping the legacy trio unchanged and adding IETF later. A compounding contract favors the both-families rung I've recommended.
2. **Multi-region.** If limits are enforced per region, `q` and `r` must state their scope. Otherwise real global throughput is the limit times the region count.
3. **REST, GraphQL, or both.** GraphQL cost points need separate metering, and a throttle inside HTTP 200 breaks status-code-only clients.
4. **Existing limits.** If limits are already enforced, diff the documented numbers against the enforced ones before changing headers.