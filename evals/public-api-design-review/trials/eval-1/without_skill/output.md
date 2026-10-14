# Harborlane /v2: what to fix before opening it up

You described the API "roughly," so this covers the five examples you gave. Run the same checks against the full spec before launch.

## Order of work

1. 🔴 **`DELETE /webhooks/{id}` returns 200 on failure.** Fix first.
2. 🔴 **Field casing and timestamp format are inconsistent.** This is a breaking change, so it needs a migration plan.
3. 🟠 **Verbs repeat the resource in the action URLs.**
4. 🟠 **The thumbnails URL is 5 levels deep.**
5. 🟢 **Write a one-page style guide and lint against it in CI.** Without it, the first four problems come back.

## 1. DELETE /webhooks/{id}: a failure returned as 200 🔴

A 200 with `{"ok": false}` tells every HTTP client, retry layer, monitor, and generated SDK that the call succeeded.

- A customer's script that checks only the status code will think the webhook is deleted. Events will keep flowing to an endpoint they believe is gone.
- Your own error-rate dashboards undercount real failures.

**Fix:**
- Return `409 Conflict` when the webhook is attached to an active subscription.
- Return `204 No Content` on success.
- Use a structured error body (see the error-format point below). Include a stable machine-readable `code`, for example `webhook_has_active_subscription`, so clients don't match on the message string.
- Drop the `{"ok": ...}` envelope everywhere. Search the whole API for other endpoints that return `ok`.

**Migration:** you can't serve both the old and new behavior, because a response has one status code. Check your logs for how often `ok:false` is returned and which partners hit it. Tell those partners the date it changes. Because of the 200→409 switch, this is the one change that will break someone who handled the old behavior correctly.

## 2. Casing and timestamps 🔴

| Endpoint | Fields |
|---|---|
| `/shipments` | `created_at`, `updated_at`, `carrier_id` (snake_case) |
| `/carriers` | `createdAt`, `updatedAt`, `shipmentCount` (camelCase) |

**Decision:** pick snake_case. It is already used by `/shipments`, which is probably your higher-traffic resource, and by the `carrier_id` field. Apply it to response fields, request bodies, query parameters, webhook payloads, and enum values.

**Timestamps:** you know clients parse `createdAt` because two of them emailed you about its timezone format. That means the format is ambiguous or inconsistent today. Standardize every timestamp in the API on RFC 3339 in UTC with a `Z` suffix, for example `2026-10-10T14:03:22Z`. Pick one precision (seconds or milliseconds) and use it everywhere.

**Migration for `/carriers`:**
1. Add `created_at`, `updated_at`, and `shipment_count` in the new standard format.
2. Keep the old `createdAt`, `updatedAt`, and `shipmentCount` in their current format, unchanged, for a fixed window. This means existing parsers don't break.
3. Send `Deprecation` and `Sunset` headers and publish the removal date.
4. Tell the two clients who emailed you first. They already want a fix, so ask them to switch to the new fields.
5. Remove the old fields on the announced date.

Since you have only 6 known partners and have not opened the API yet, doing this before launch is cheap. After launch you would be breaking strangers.

## 3. Redundant verbs in action URLs 🟠

`POST /shipments/{id}/cancel-shipment` and `POST /carriers/{id}/verify-carrier` repeat the resource name that is already in the path.

**Fix:**
- Use `POST /shipments/{id}/cancel`.
- Use `POST /carriers/{id}/verify`.
- Keep the old paths as aliases for the same deprecation window.

Two other points for these endpoints:
- **Idempotency:** cancel is a state change that clients will retry on timeouts. Support an `Idempotency-Key` header, and define what happens when you cancel an already-cancelled shipment. Returning the current state with 200 is the usual answer.
- **Pattern:** `POST .../{action}` is fine for actions that aren't CRUD. Use it consistently, and don't mix it with a `PATCH {status: "cancelled"}` style on other resources.

## 4. The thumbnails URL is too deep 🟠

`GET /shipments/{id}/events/{eventId}/attachments/{attachmentId}/thumbnails` has four IDs of nesting.

Problems:
- Clients must carry the full ancestor chain to fetch one image.
- It is easy to get wrong and hard to cache.
- Any future move of attachments breaks the URL.

**Fix:**
- Limit nesting to two levels.
- Expose the resource by its own ID: `GET /attachments/{id}/thumbnail`, or `/attachments/{id}/thumbnails` if it returns several sizes.
- Return the parent links in the attachment body, as `shipment_id` and `event_id`.
- Check that attachment IDs are globally unique. If they are only unique within an event, make them global first.
- Decide whether this returns one image or a list, and name it to match: singular for one image, plural for a collection.
- Use the same path-parameter naming style everywhere in the spec, for example `{event_id}` rather than `{eventId}`.

## 5. Things I couldn't see, to check before launch

These matter more once strangers can use the API:

- **Error format:** adopt one shape for all errors. RFC 9457 `application/problem+json` is a good default. Include a stable `code` field.
- **Pagination:** use one style on every list endpoint, preferably cursor-based. Use the same parameter names everywhere (`limit`, `cursor`).
- **Rate limits:** return `429` with `Retry-After`. Document the limits per plan.
- **IDs:** use one format, and make them opaque strings.
- **Nulls:** decide between `null` and an omitted field for missing values, and apply it everywhere.
- **Webhooks:** sign payloads, retry on failure, and set the payload field casing to match the rest of the API.
- **Versioning and deprecation policy:** state in writing what counts as a breaking change, how much notice you give, and which headers you use. After launch, treat `/v2` as frozen except for additive changes.

## 6. Write the style guide 🟢

Four different inconsistencies in five examples says nothing is checking new endpoints. A guide of about one page is enough. It should cover:

- Field casing and timestamp format
- URL structure: plural nouns, max two levels, action naming
- Status codes and the error shape
- Pagination, idempotency, and deprecation rules

Then enforce it. Put the OpenAPI spec through a linter such as Spectral in CI, and make API changes need review against the guide. Without this gate, the inconsistencies will return after launch, when fixing them is expensive.

## Suggested 5-week plan

| Week | Work |
|---|---|
| 1 | Write the style guide. Inventory the full spec against it. Pull logs for `ok:false` and for `createdAt` usage. Email the 6 partners with the change list and dates. |
| 2 | Ship the webhook 409 fix. Ship the additive changes: new snake_case fields, `/cancel` and `/verify` aliases, and `/attachments/{id}`. Add `Deprecation` and `Sunset` headers. |
| 3 | Add the linter to CI. Fix the remaining items from the inventory (pagination, error shape, and so on). Get the two timestamp-complaint clients onto the new fields. |
| 4 | Remove the old fields and paths, or confirm every partner has migrated. Final review of the full spec. |
| 5 | Open the API. |

If a partner can't migrate by week 4, keep the old fields for them and set a firm removal date. Don't leave them open-ended.

I haven't seen your code or the full spec. Send me the OpenAPI file and I can turn this into an exact inventory of every field, path, and status code to change.