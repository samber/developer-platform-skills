# Clearbend webhook subscription design

Date: 2026-10-10. I did not ask the skill's clarifying questions, so the assumptions I made are listed at the end. Please correct any that are wrong.

## Verdict on "delete and recreate works fine"

Delete-and-recreate does not fix the backlog. It resets it.

- Deleting destroys the subscription's delivery and replay state. The new subscription starts at "new events only", so every stuck event is either silently lost or double-replayed.
- For an HR platform the lost events are hires, terminations and pay changes. Nobody sees the loss, so the workaround looks like it works.
- Recreating also forces a secret change unless Clearbend reuses the old one, and a changed secret breaks signature verification at the customer.
- The skill lists this as a named failure mode: "delete-and-recreate of a subscription silently resetting its replay position."

**Do first:** ask Support and Engineering what delete-and-recreate does to stuck events today (drop, replay or skip). Everything below assumes it drops them.

**Replacement playbook for Support:**

1. The customer fixes their endpoint.
2. The customer or Support calls `resume` if the subscription is `disabled`.
3. The customer or Support replays the stuck range.
4. Nobody deletes anything.

## Subscription object

```json
{
  "id": "whs_01J...",
  "url": "https://hooks.customer.com/clearbend",
  "description": "Payroll sync",
  "status": "active",
  "status_reason": null,
  "status_changed_at": "2026-10-10T09:00:00Z",
  "paused_until": null,
  "event_types": ["employee.hired", "employee.terminated"],
  "scope": { "legal_entity_ids": null },
  "signing": {
    "algorithm": "hmac-sha256",
    "secrets": [
      { "id": "sec_1", "prefix": "whsec_ab12", "created_at": "...", "expires_at": null }
    ]
  },
  "replay": {
    "on_create": "latest",
    "on_resume": "earliest_undelivered"
  },
  "health": {
    "last_success_at": "...",
    "last_failure_at": null,
    "consecutive_failures": 0
  },
  "metadata": {},
  "created_at": "...",
  "updated_at": "...",
  "deleted_at": null
}
```

### Field rules

- **`status`** has three values.
  - `active` and `paused` can be set by the customer.
  - `disabled` is platform-only and is rejected on write.
  - `status_reason` records why: `customer_paused`, `retries_exhausted_3d`, `url_failed_validation`, or similar.
- **`paused_until`** is optional. If set, the subscription auto-resumes at that time. Customers with a planned maintenance window need this, because they forget to resume.
- **`event_types`** are catalog names in `resource.action` form, past tense (`employee.hired`).
  - `null` means all events. Say so in the docs.
  - Unknown names are rejected.
- **`scope`** is a second filter, independent of `event_types`. For an HR platform it is a legal entity or a department. `null` means everything.
- **`signing.secrets`** is an array, so zero-downtime rotation works.
  - Both the old and the new secret sign during an overlap window.
  - The secret value is shown once, on create and on rotate.
  - The prefix is `whsec_`. Offer `ed25519` as an option for enterprise accounts that don't want to hold a shared secret.
- **`replay`** holds the two replay positions.
  - A new subscription starts at `latest` (new events only).
  - After a pause or platform incident it resumes from `earliest_undelivered`.
  - The two positions are configured separately, as the skill's lifecycle section requires.
- **`health`** is read-only. It lets the customer see a stuck backlog without filing a ticket.
- **`deleted_at`** means soft delete. Your rules forbid hard-deleting user-owned resources.
  - A deleted subscription stops delivery but keeps its history.
  - Do not allow undelete to reuse the id for a different URL.
- **Validation on `url`:**
  - HTTPS only.
  - Block private and internal address ranges, because customer-supplied URLs are an SSRF vector.
  - Fire a `ping` event on create so the customer can confirm the wiring.

### Fields to leave out

- **Per-subscription retry config.** Use one fixed schedule for now (see the contract below). Add configurability when enterprise accounts negotiate SLAs.
- **API-version pinning.** Pick one versioning camp. I recommend additive-only changes plus a new event type name for any breaking change. Never reshape a payload a subscriber already stores.

## Endpoints

| Method | Path | Purpose |
|---|---|---|
| POST | `/webhook-subscriptions` | Create |
| GET | `/webhook-subscriptions` | List |
| GET | `/webhook-subscriptions/{id}` | Read |
| PATCH | `/webhook-subscriptions/{id}` | Update `url`, `description`, `event_types`, `scope`, `metadata`, `status` (active or paused), `paused_until` |
| DELETE | `/webhook-subscriptions/{id}` | Soft delete |
| POST | `…/{id}:pause` | Pause, with optional `paused_until` |
| POST | `…/{id}:resume` | Resume, with `backlog: "deliver" \| "skip"` |
| POST | `…/{id}:rotate-secret` | Add a new secret and start the overlap window |
| POST | `…/{id}:test` | Send an example event, marked as a test |
| GET | `…/{id}/deliveries` | Delivery log with per-attempt headers, body, response code and timing |
| POST | `…/{id}/replay` | Replay an event or a time range. Gate large ranges behind a cost confirmation. |

Use "retry" and "replay" as two separate terms. A retry is a new attempt of the same event. A replay re-ingests the original as a new event.

## Answer to the two enterprise accounts: the maintenance window

Publish these sentences in the delivery contract.

**Planned window (recommended path):**

1. The customer pauses the subscription before the window, or sets `paused_until`.
2. While `paused`, Clearbend keeps accepting and storing matching events. It does not drop them.
3. Events are retained for 30 days. This matches the dead-letter retention.
4. On resume, the customer chooses `backlog: "deliver"` or `"skip"`.
   - Deliver drains the backlog at a rate-limited pace, so the customer's endpoint isn't flooded.
   - Skip discards it.
5. Order is not guaranteed on drain.
6. If the pause outlasts retention, events older than 30 days are gone. The customer must reconcile through the API.

**Unplanned downtime or an forgotten pause:**

- Each event retries on a fixed exponential schedule spanning about a day. For example: immediately, +5s, +5m, +30m, +2h, +5h, +10h, +10h, about 27.5 hours in total.
- The ack timeout is about 10 seconds. A 2xx stops retries. Customers should queue the work and return fast.
- Non-retriable 4xx responses (anything except 408 and 429) go straight to the dead-letter queue.
- A 429 with `Retry-After` overrides Clearbend's backoff curve.
- An event that exhausts its retries goes to the dead-letter queue. It is retained for 30 days with full headers and is replayable.
- If all deliveries to an endpoint fail for 3 days (a Stripe-like starting number, to be tuned), the subscription becomes `disabled`. Clearbend notifies the customer by email and in the dashboard, not by webhook.
- `resume` followed by a replay recovers everything still in retention.

**The five contract facts to publish:**

1. Delivery is at-least-once, never exactly-once.
2. Ordering is best-effort, with no guarantee.
3. The retry schedule is the one above.
4. The ack timeout is about 10 seconds.
5. The dedup ID is in the `webhook-id` header. It stays the same across retries of the same event.

Also recommend that customers reconcile against the API periodically for high-stakes event types.

## Signing and payload notes

- Adopt Standard Webhooks.
  - Send the headers `webhook-id`, `webhook-timestamp` and `webhook-signature`.
  - The signature is HMAC-SHA256 over `{id}.{timestamp}.{raw_body}`, with a 5-minute tolerance window.
  - A body-only signature has no replay protection.
- HR payloads carry personal data. Prefer thin payloads (ids plus an API fetch). That also avoids payload versioning problems. If you ship full payloads, keep them small and minimise PII.

## Buy versus build

Check whether a managed sender such as Svix or Hookdeck is allowed for HR data. The answer depends on your DPA and data-residency position. If it is allowed, buying gives you the pause, disable, replay and portal machinery. You still own the event catalog, the contract and the docs. If it is not allowed, delete the managed option and compare a self-hosted gateway against building it yourself.

## Assumptions and open questions

1. Delete-and-recreate currently drops stuck events. Verify before you tell customers anything.
2. Peak endpoint count and events per second are unknown. Per-endpoint queue isolation is required either way, so one slow customer never delays another.
3. Consumers are probably a mix. Enterprise accounts want the written contract. Smaller customers need the delivery log, `test` and replay.
4. Build versus buy is not decided. Ship date and DPA constraints decide it.
5. The 3-day auto-disable threshold and the 30-day retention are my picks. Confirm them against storage cost and what the two enterprise accounts need.
6. Do the two accounts need FIFO? I recommend refusing it by default and offering it only as an explicit opt-in.