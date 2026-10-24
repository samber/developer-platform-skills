# Silverthread Zapier integration: design

## Verdict

Don't ship 38 mirrored steps. Ship about 11 workflow-shaped steps. Cut `Delete Invoice` and `Charge Card` from v1. Use polling triggers first, and add instant triggers once the webhook limit is fixed.

Zapier users build "when X happens, do Y" workflows. They don't call endpoints. Every extra step is a maintenance cost and a review burden. Several of your API facts also break a naive mirror.

## 1. v1 step list

| Type | Step | Notes |
|---|---|---|
| Trigger | New Invoice | Polling, newest-first (see §2). |
| Trigger | Updated Invoice | Uses `updated_since`. |
| Trigger | Invoice Paid | Same fetch as Updated Invoice, filtered to paid. Probably the most-used trigger. |
| Trigger | New Customer | Polling, newest-first. |
| Search | Find Customer | By email, name or reference. Returns an empty result when nothing matches, never an error. |
| Search | Find Invoice | By id or invoice number. Replaces `Get Invoice`. |
| Action | Create Customer | Paired with Find Customer as "create if not found". |
| Action | Update Customer | |
| Action | Create Invoice | |
| Action | Update Invoice | |
| Action | Send Invoice | Include only if the API has a send endpoint. |

I haven't seen your endpoint list. Swap in the real endpoints, but keep the shape: few triggers, searches, then writes.

### Why `Get Invoice` becomes `Find Invoice`
- A user rarely holds a bare id outside a Zap. A search that can match on invoice number is more useful.
- A search step lets the Zap continue or branch when nothing is found.

### Why `Create or Update Customer` becomes Find Customer plus Create Customer
- An upsert needs a match key. Agencies often share an email across several client records, so a silent merge corrupts books.
- Zapier's native "find, else create" pattern makes the match key explicit and visible to the user.
- If product insists on a single upsert, add a required "Match on" field (email or external reference). Don't pick one silently.

### Why `Delete Invoice` is cut
- It's destructive and irreversible in accounting software, and Zaps loop and misfire.
- A bad Filter step or a trigger replay could delete real records, and agencies need an audit trail.
- If users ask for it, ship `Void Invoice` instead, which keeps the record.

### Why `Charge Card` is cut from v1
- It moves money and is not idempotent. Zapier users can replay failed tasks, and a replay double-charges the customer.
- A Zap that misfires also charges cards in bulk.
- If you ship it later, require all of the following:
  - An idempotency key.
  - A reference to an existing invoice instead of a free-form amount.
  - A dedicated OAuth scope that users must grant explicitly.
  - A per-account daily cap.
  - A visible audit log entry.
  - Confirmation that card-on-file consent covers automated charging, including any SCA rules.
- Meanwhile, `Send Invoice` with a pay link covers most of the need.

The remaining ~27 endpoints stay API-only. Revisit them when users ask.

## 2. Decisions driven by your API facts

| Fact | Consequence | Decision |
|---|---|---|
| List endpoints return oldest-first, 20 per page. | Zapier polling reads the first page and expects newest-first. Oldest-first would return the same 20 oldest invoices every poll, and new invoices would never fire. This is the biggest trap. | Every polling trigger sends `?sort=-created_at`. |
| 900 invoices in an hour after month-end. | That's ~15 per minute. One 20-item page is fine at 1-minute polling, but Zapier polls only every 1 to 15 minutes depending on the user's plan. At 15 minutes that's ~225 new invoices per poll, and the whole burst may land in one poll. A first page alone silently drops items. | Enable paginated polling in the CLI (`canPaginate`). Confirm the page cap in current CLI docs. Ask engineering for `limit=100`. |
| Webhooks allow exactly one callback URL per account. | Zapier instant (REST hook) triggers subscribe one URL per Zap. One slot per account means the Zapier subscription would overwrite the agency's own webhook, or the second Zap would overwrite the first. | No instant triggers in v1. Polling only. See §6 for the fix. |
| `updated_since` filter on invoices. | Allows an efficient Updated Invoice trigger. | Query with `updated_since = now − 1h`. Use dedupe id `${id}:${updated_at}`. Ask engineering for `sort=-updated_at` on that filter. |
| Dates are epoch seconds. | Zapier users expect ISO datetimes, and the Formatter and Date pickers work with ISO. | Outputs: keep the original epoch field and add an `_iso` twin. Inputs: accept a datetime and convert to epoch seconds in code. Document the timezone used for date-only values (use the account timezone if exposed, else UTC). |
| IDs are UUIDs. | Users can't type them. | Use dynamic dropdowns or searches. Show invoice number and customer name as labels. Always allow mapping an id from an earlier step. |
| Customers carry account-specific custom fields. | A static schema is wrong for every account. | Use function-based `inputFields` and `outputFields` that fetch the account's field definitions at runtime. Needs a field-definitions endpoint (§6). |
| OAuth tokens already exist for mobile. | Reuse the OAuth server, not the mobile client. | See §3. |

### Polling details
- **Dedupe key.** Use the `id` field. For Updated Invoice and Invoice Paid, use `${id}:${updated_at}`. Epoch seconds can collide when two updates land in the same second, so keep the 1-hour lookback generous.
- **First poll.** Zapier doesn't fire on items seen in the first poll after a Zap is turned on. That's expected.
- **Sample data.** Fetch the 3 newest records. Fall back to static sample data when the account is empty.
- **Rate limits.** Map 429 to Zapier's throttled error and honor `Retry-After`. Every Zap polls independently, so budget your API rate limit for N Zaps per account.
- **Task cost.** Warn in the docs that 900 invoices means 900 Zap runs and 900 tasks for the user's plan. Suggest a Filter step or a digest.
- **Idempotent creates.** Add an optional "External reference" field on Create Invoice and Create Customer. Ask engineering to enforce uniqueness per account. That makes a Zap replay safe instead of creating duplicates.

## 3. Authentication

- Use OAuth 2.0 against your existing authorization server.
- Register a **new, separate OAuth client for Zapier**. Don't reuse the mobile client.
  - The mobile app is probably a public client with PKCE.
  - Zapier uses a confidential client with a secret and a fixed redirect URI.
  - Separate clients let you revoke, rate-limit and scope Zapier on its own.
- Request the narrowest scopes: read plus write for invoices and customers. Leave out card and payment scopes for v1.
- Enable refresh tokens, and map expired tokens to Zapier's expired-auth error so it refreshes automatically.
- Add a lightweight "who am I" endpoint for the connection test, such as `GET /me`. Use the account name as the connection label so agencies with several accounts can tell them apart.

## 4. Build and test in the CLI

1. **zapier init** a TypeScript or JS project. **zapier register** the app as private.
2. Implement one trigger first (New Invoice with paging), and check it end to end.
3. Run **zapier validate** and **zapier test**.
4. **zapier push** a private version. Invite 3 to 5 friendly agencies.
5. Request public listing only after the acceptance tests below pass.

### Acceptance tests
- **Burst.** Seed 900 invoices into a sandbox account in under an hour. Run New Invoice at the slowest poll interval. Every invoice fires exactly once, with none missing and none duplicated.
- **Sort.** With 50+ existing invoices, create one new invoice. Confirm it fires. This fails under the default oldest-first order.
- **Custom fields.** Two accounts with different custom fields show their own field sets in Create and Update Customer.
- **Dates.** A date-only input round-trips to the right epoch second and back to the right ISO value.
- **Replay.** Replaying a Create Invoice task with the same external reference creates no duplicate.
- **Auth.** Expire the token, then confirm a refresh succeeds with no user action.

## 5. Error handling

- 401: refresh the token, then retry once.
- 404 on Find: return an empty result.
- 422: surface the API's field-level message to the user, not a generic failure.
- 429: throttle and honor `Retry-After`.
- 5xx on a write: fail visibly and never auto-retry silently, because retries risk duplicates without idempotency.

## 6. Asks for engineering

1. `limit` up to 100 on list endpoints (high value, small change).
2. `sort=-updated_at` together with `updated_since`.
3. A custom-field definitions endpoint for customers.
4. A `GET /me` account endpoint for the connection test.
5. A unique `external_reference` on invoices and customers.
6. **Phase 2:** a multi-subscriber webhook resource. It needs one subscription per target URL, an event-type filter, a signing secret, and delete-on-unsubscribe. With it, every trigger becomes instant. Keep polling as the fallback. Don't touch the existing single-URL webhook endpoint.

## 7. Phasing

- **v1 (CLI, private beta):** the 11 steps above, polling only.
- **v1.1:** public listing, plus `Void Invoice` if users ask.
- **v2:** multi-subscriber webhooks and instant triggers.
- **Later, only on demand:** `Charge Card` with the guardrails above.

## 8. Decisions I need from you

1. Is the Find Customer plus Create Customer pairing acceptable, or does product insist on a single upsert?
2. Will engineering take asks 1 to 5 before the private beta?
3. Does the API have a send-invoice endpoint? It decides whether `Send Invoice` is in v1.
4. Do you want `Charge Card` on the roadmap at all, or permanently out?