# Decision: run OAuth 2.0, not long-lived per-app API keys

Security's operational-simplicity concern is real, and the plan below answers it.

## 1. Why OAuth

The question is delegated authorization. An outside developer's app acts on behalf of a customer. API keys can't express that well.

| Need | Per-app API key | OAuth (auth code + PKCE) |
|---|---|---|
| Customer consents to this app | No. The key proves the app exists, not that the customer agreed. | Yes, via a consent screen. |
| Customer revokes one app | Impossible per customer. Revoking the key kills every customer of that app. | Revoke one grant. |
| Limit what the app can touch | Coarse | Scopes, e.g. `dashboards:read` and `dashboards:write` |
| Leak impact | Long-lived secret held by a third party | Access token lives about 15–60 min. Refresh tokens rotate. |
| Know whose data a call touched | You need a key per (app, customer) pair | The token carries app, customer and grant |

The last row settles it. To make keys work you would issue one per app and customer pair. That means building consent, scoping, revocation and rotation yourself, which is a worse version of OAuth. Per-app keys alone fail metering and attribution, which you asked about, because a request can't be tied to a customer's grant.

## 2. How to keep it operationally simple

- **Use a maintained OAuth server or library.** Don't hand-roll one.
- **Flows:**
  - Authorization code with PKCE for apps acting for customers.
  - Client credentials only for the app's own non-customer endpoints, such as its usage reports.
- **Tokens:**
  - Short-lived access tokens.
  - Refresh tokens with rotation and reuse detection. A replayed refresh token revokes the whole grant.
- **Install object.** Create one record per (app, customer workspace) with an ID, the granted scopes, who approved it, and a status of active, paused or revoked. Everything below hangs off this record.
- **Admin consent.** Only workspace admins can approve write scopes.
- **App registration and review.** Require redirect URIs, a contact, and review before an app gets `write` scopes in production.
- **Where API keys stay.** Keep customer-created personal keys for a customer's own scripts. That is first-party use, not third-party delegation. Security gets its simple model there.

## 3. Metering and billing

I haven't seen your pricing, so the first item below is a recommendation to confirm, not a fact.

**Who pays (decide first).** I recommend not billing developers at launch. Include API usage in the customer's plan with quotas, and meter everything from day one so you can add app-level charges later without a data gap.

**What to meter.** Emit one event per request at the gateway:
- `request_id`, `app_id`, `install_id`, `customer_id`, `grant_id`
- scope, endpoint, method
- status, latency, bytes
- read vs write

**Pipeline:**
1. Gateway emits events. They are idempotent on `request_id`.
2. Aggregate hourly into a usage ledger keyed by (install, day, unit class).
3. Billing reads the ledger. It never reads raw logs.

**Billable units (proposed, adjust to taste):**
- Count successful requests only. Don't bill 401, 403, 429 or 5xx responses.
- Weight writes above reads, for example 1 unit per read and 5 per write. The 5 is a placeholder to calibrate against your real cost.
- Meter heavy exports separately by rows or bytes.

**Limits.** Set rate limits per install, so one customer's app can't starve others. Set a second, global limit per app. Return 429 with `Retry-After`.

**Visibility.** Show customers usage per connected app. Show developers their own usage per install. Both prevent billing disputes.

## 4. Telling a customer which app broke something

The aim is a customer who sees a broken dashboard and gets to the responsible app in a few clicks.

1. **Attribute every write.** Dashboard version history records both actor and client: "edited by *App X* on behalf of *Jane*, at 14:03, grant G". This needs `app_id` and `grant_id` on every write, which OAuth gives you and bare keys don't.
2. **Connected apps page** (customer-facing). For each app it shows:
   - who approved it, with scopes and date
   - last success
   - error rate
   - counts of 401, 403 and 429 responses
   - a list of recent writes, with links to the affected dashboards
3. **Fast containment.** Provide Pause and Revoke buttons on that page, and restore of the previous dashboard version from history. Add an internal kill switch per app for incidents that span customers.
4. **Correlation.** Return `X-Request-Id` on every response. A customer or developer can quote it to support, and it maps to the metering event and the audit log.
5. **Notify the developer.** Send webhooks or email on error spikes or a paused install, so the app owner learns about it before the customer does.
6. **Retention.** Keep the audit log for about 90 days. That figure is an assumption, so check it against your compliance needs.

## 5. Order of work

1. Install record, OAuth server and scopes, with the gateway stamping `app_id` and `grant_id`.
2. Audit log and version history with actor and client.
3. Metering events and ledger. Start with the cheapest version, with billing off.
4. Connected apps page with Pause and Revoke.
5. App review and write-scope gating, then open registration to outside developers.

## 6. What to confirm before building

- **Billing party.** Customer plan, developer, or both.
- **Write-unit weight.** It needs a real cost basis.
- **Dashboard version history.** If it doesn't exist yet, it is a prerequisite for the attribution story, not a nice-to-have.

I haven't checked your codebase or existing gateway, so I can't say how much of step 1 is already in place.