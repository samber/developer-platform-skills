# Integration health dashboard for Quillfeather

## Recommendation

Build two views from one dataset:

1. **Internal call list** for the Quillfeather partner team. It ranks partners by who needs a call this week, and why.
2. **Partner-facing page**, scoped to one partner. It shows their migration checklist and their own health, with a clear next action.

Keep the Datadog per-key monitors for alerting. Use the dashboard to decide who to call, not to page anyone.

## What to track

### Track 1: Signing certificate rotation (Feb 14, about 3.5 months out)

This one comes first. A partner that pins the certificate or verifies against a cached copy will start rejecting webhooks on the day, and nothing warns them beforehand.

- **Cert-readiness test result per webhook endpoint.** Add a "send test event signed with the new cert" action. Record pass or fail, the date, and the HTTP status the endpoint returned. This is the only reliable readiness signal for pinned certs, because we can't see their verification from our side.
- **Whether the partner fetches the new cert.** If you publish it at a URL or JWKS endpoint, record the last fetch per partner.
- **Post-rotation failure rate.** Watch 401 and 403 responses and signature-failure responses on webhook delivery, split by endpoint.
- **Strongest mitigation.** Sign with both certs for an overlap window if you can. The dashboard then tracks who has moved, instead of who has broken.

### Track 2: iOS SDK 3.x end of life (April)

- **Share of each partner's requests by SDK major version.** This needs an SDK-version header or User-Agent.
- **Partner's latest shipped app version and the SDK it bundles.** This is the key distinction:
  - Latest app release still bundles 3.x: **call**. The partner hasn't started.
  - Latest app release bundles 4.x but users still run old builds: **email**. This is the app-update tail, not partner inaction.
- **Active installs on 3.x over the last 30 days.** Use a warehouse or logs, not Datadog tags, to avoid device-level cardinality.
- **Lead time.** App review plus staged rollout takes weeks, so the partner's real deadline is well before April. Back-solve a "must have shipped by" date for each partner.

### Track 3: Webhook payload v1 retirement (June 30)

- **Per-endpoint payload version subscribed.** We know this exactly from configuration, so no inference is needed.
- **v1 deliveries per day, by event type.** This sizes the exposure.
- **v2 endpoint registered and passing a test delivery?** Registered but failing counts as not ready.
- **Pending changes.** If a partner has v2 configured but still receives v1 deliveries, flag it as half-migrated.

### Track 4: Steady-state health (always on)

You already have error rates per API key. Make them usable:

- **Error rate with a minimum-volume gate.** Without it, a key with 3 requests and 1 failure outranks a key with a real incident. Use a floor such as 500 requests per day, or a confidence interval.
- **Split by cause.** Separate 5xx (ours), 4xx auth and validation (theirs), and 429 (rate limiting). Rate limiting is a conversation about their usage, not an error.
- **Webhook delivery success, retry depth, p95 endpoint latency, and auto-disabled endpoints.**
- **Trend against the partner's own 28-day baseline.** A rise matters more than the absolute level.

### Plumbing

- **API key to partner mapping.** One partner may have several keys, and some keys may be shared. Exclude sandbox and test keys. Without this mapping, nothing below works.
- **Datadog tags.** Add `partner_id`, `sdk_major`, `payload_version`, and `cert_version` as tags on custom metrics.
- **State store.** Keep a small `partner_readiness` table, refreshed daily. It holds the checks above plus contact name, tier, last contacted date, acknowledgement status, and notes. Datadog can't hold that state.

## Internal view: the weekly call list

Generate it every Monday, with one row per partner. Columns:

| Column | Content |
|---|---|
| Partner, owner, tier | Who and who calls |
| Top reason | One line, e.g. "v1 payload on 2 endpoints, no v2 configured" |
| Deadline hit, days left | Which track, how long remains |
| Exposure | Requests per day, active installs |
| Last contacted, acked? | Avoids repeat calls and finds silent partners |
| Next step | Call, email, or watch |

Use explainable rules, not an opaque score:

- 🔴 **Call now:**
  - active incident (error rate over threshold with volume met)
  - an auto-disabled endpoint
  - a failed cert test within 30 days of Feb 14
  - post-deadline breakage
- 🟠 **Call this week:**
  - not ready with an escalating threshold as each deadline nears (for example, no plan at 90 days, no passing test at 60 days)
  - a partner who ignored two notices
  - latest app release still on 3.x
- 🟡 **Email and watch:** migrated but with a long tail, or ready but untested.
- 🟢 **Fine.**

Add two roll-ups at the top. First, the percentage of partners ready on each track, plotted against a target curve to each deadline. Second, a count of unreachable partners (bounced contact, no reply).

## Partner-facing view

Show each partner only their own data.

1. **Header:** "2 actions needed before Feb 14", with the next deadline first.
2. **One card per migration:**
   - what is changing and the date
   - their status: Ready, Action needed, or Not affected
   - the evidence, e.g. "41,200 v1 deliveries in the last 7 days to 2 endpoints"
   - a link to the migration guide
   - a "Send test event" button
   - "Mark planned, target date" so they can acknowledge
3. **Health:** their error rate and webhook delivery success for 7 and 30 days. Label causes as "Quillfeather" or "your endpoint", and include sample request IDs for debugging.
4. **Contacts:** who we notify, and a way to change it.

Do not show partners:

- the call tier or any internal scoring
- comparisons or rankings against other partners
- revenue or tier data
- raw API keys (show the last 4 characters)

Don't embed Datadog directly. Export partner-scoped data to your own API or store, so there is no cross-tenant leak.

## Open questions

1. What is the exact April date for 3.x EOL? I assumed the start of the month.
2. Can you dual-sign during rotation? It changes cert tracking from "who broke" to "who moved".
3. Do the iOS SDK and webhook payloads already carry a version marker we can log?
4. What happens at v1 cutoff on June 30: hard failure, or degraded rendering? That sets the severity of Track 3.
5. Does the API key to partner mapping exist today, and is it clean?

## Build order

1. Key-to-partner mapping and the `partner_readiness` table.
2. Track 3 (config-based, cheapest, exact) and Track 4 (reuses your existing monitors).
3. The cert test button before the end of the year, so the Feb 14 failures surface early.
4. Track 2 once the SDK version header is confirmed.
5. The partner-facing page.