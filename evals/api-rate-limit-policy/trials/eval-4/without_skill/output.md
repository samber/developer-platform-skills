# Nuvexa rate-limit header strategy

## Decision

**Dual-emit now. Do not drop `X-RateLimit-*` yet.** Add `RateLimit` and `RateLimit-Policy`, keep the legacy trio, and remove the legacy headers only on a dated sunset, gated by an API version bump.

You are right that the legacy trio is cruft, and the new fields are the right target. The problem is the order of operations. Dropping the old headers first breaks clients you can't see, and it saves almost nothing.

## Why not a hard swap

1. **The IETF fields may not be final.** The `httpapi` rate-limit-headers draft has changed wire format between revisions. Early revisions used `RateLimit-Limit`, `RateLimit-Remaining` and `RateLimit-Reset`. Later revisions moved to the structured `RateLimit` and `RateLimit-Policy` fields. Before you commit, check whether it is now an RFC. If it is still a draft, pin the revision number in your docs and your changelog.
2. **Your 60% SDK share doesn't cover your risk.** It means 40% of traffic is third-party code, scripts and gateways, and you don't control any of it. Many of those clients back off on `X-RateLimit-Remaining` or `X-RateLimit-Reset`. Removing the headers makes them fall back to blind retries, which is the retry storm a payments API most wants to avoid.
3. **The SDK 60% is not instantly migratable either.** Pinned and old SDK versions in production still read the legacy headers. "Official SDK" tells you what you can ship, not what is deployed.
4. **The saving is tiny.** Three legacy headers cost roughly 80–100 bytes per response. The risk side is larger: retry storms, tickets and trust.
5. **Edge cost is not the constraint.** Your CDN can format structured fields cheaply, so that part is not a reason to rush removal.

## Target state

| Header | Status | Notes |
|---|---|---|
| `RateLimit-Policy` | Add | Describes the quota and window. |
| `RateLimit` | Add | Remaining quota and reset, as structured fields. |
| `X-RateLimit-Limit/Remaining/Reset` | Keep, deprecate | Remove at the sunset date. |
| `Retry-After` | Keep forever | Required on every 429 and 503. This is RFC 9110 and the only header every HTTP client honors. |
| `Deprecation` and `Sunset` | Add to legacy responses | Machine-readable notice. |

## Rules for emitting the new headers

- **Reset is delta-seconds in both new fields.** Check what your legacy `X-RateLimit-Reset` uses. If it is an epoch timestamp, the two values differ by design. Document that explicitly, or clients will treat one as the other.
- **Compute the counters at the limiter, not at the edge.** The CDN can format and emit the fields, but the remaining and reset values must come from your real limiter state. If the edge computes its own, it will disagree with the origin and give clients wrong numbers.
- **Never cache these headers.** Strip them from cached responses, or set cache keys so a hit can't replay stale quota values.
- **Expose them to browsers.** Add `RateLimit`, `RateLimit-Policy` and `Retry-After` to `Access-Control-Expose-Headers`. Otherwise browser clients can't read them.
- **Parse defensively on the client.** A malformed structured field must be ignored, never fatal.
- **Be consistent across endpoints.** Use one policy name per limiter and the same units everywhere. Where the draft's syntax is ambiguous, pick one interpretation and document it.

## Rollout

1. **Weeks 0–2: ship dual emit.** Add the new headers behind a flag, canary them at a small percentage, then go to 100%. Watch error rates, header size and proxy or WAF rejections of the new fields.
2. **Weeks 2–8: release SDKs.** The new versions read `RateLimit` first, then `X-RateLimit-*`, then `Retry-After`. Ship one SDK change per language.
3. **Weeks 2–8: publish docs and a deprecation notice.** Add a changelog entry, a docs page with a migration table (old header → new field), and the `Deprecation` and `Sunset` headers on responses. Notify account owners directly. For a payments API, give at least 12 months of notice.
4. **Months 3–12: measure.**
   - You can't see which clients read the headers, so track proxies. Use SDK version share from `User-Agent`, and the share of traffic from keys that have never sent an SDK user agent.
   - Run per-key opt-out cohorts, and offer a no-legacy flag to willing customers. Watch their 429 rate, retry volume and ticket count.
5. **At sunset: remove legacy on an API version bump.** Remove it only for new API versions first. Keep it for pinned older versions until their own end of life.

## Gates before removing anything

Remove the legacy headers only when all of these hold:

- Supported SDK versions that read only the legacy headers are below a threshold you set. Pick a number, such as 5% of SDK traffic.
- The opt-out cohort showed no rise in 429s or retries.
- The sunset date has passed with the notice period honored.
- A rollback switch exists and was tested.

## Open questions to confirm

1. What is the current status of the IETF draft, and which revision are you implementing?
2. Is `X-RateLimit-Reset` an epoch or delta-seconds today?
3. Where does the limiter state live, and can the edge read it without a round trip?
4. Do you have an API versioning mechanism that can carry the removal?

Once you've answered the first two, I can draft the exact header examples and the migration table for the docs.