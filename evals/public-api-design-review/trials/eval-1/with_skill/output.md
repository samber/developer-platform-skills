**Next: send me your OpenAPI spec and 5–10 real production responses.** Until then this review is partial. It is built from 5 sketched endpoints, and the skill forbids reviewing from a sketch alone.

## Scope

- **Surface:** Harborlane `/v2`, 5 endpoints sketched.
- **Audience and stage:** 6 design partners today, anyone in 5 weeks. This is a public launch, so the review is blocking: open Must-change findings stop the launch.
- **Rule corpus:** you have no style guide. Findings cite the skill's checklist items by name.
- **Observed behavior:** every sketched behavior is assumed to be depended on by the 6 partners. You confirmed `createdAt` on `/carriers`.

## Dimension summary

| Dimension | Result |
|---|---|
| 1. Resource modeling and URI naming | ❌ FAIL, 2 findings |
| 2. HTTP method semantics | not assessed, no data |
| 3. Status-code correctness | ❌ FAIL, 1 finding |
| 4. Field-naming consistency | ❌ FAIL, 1 finding |
| 5. Pagination | not assessed, no data |
| 6. Filtering, sorting, field selection | not assessed, no data |
| 7. Error shape consistency | ❌ finding 3 touches it, rest not assessed |
| 8. Backward compatibility | ⚠️ every fix below is breaking for partners |
| Sibling checks | versioning ✅ (`/v2` exists). Idempotency, auth, rate limits and docs not assessed. |

Dimensions 2, 5, 6 and 8 are not walked, and neither are the sibling checks. The skill's coverage gate counts that as incomplete, not lean.

## Must-change findings (block launch)

| # | Finding | Dim | Cited rule | Fix |
|---|---|---|---|---|
| 1 | `/shipments` returns `created_at` and `updated_at`. `/carriers` returns `createdAt` and `updatedAt`. | 4 | "One casing convention across every endpoint… consistency of the choice is the check." | Standardize on snake_case, the majority in your sample. Emit both names on `/carriers` now. Deprecate the camelCase names and give the 6 partners a sunset date. Do not rename in place, because partners parse `createdAt`. |
| 2 | `GET /shipments/{id}/events/{eventId}/attachments/{attachmentId}/thumbnails` nests 4 levels deep. | 1 | "Nesting stops at 2–3 levels." | Promote to `/attachments/{id}/thumbnails`, which needs globally unique attachment IDs. Keep the old path as a deprecated alias. |
| 3 | `DELETE /webhooks/{id}` returns 200 with `{"ok": false, ...}` on conflict. | 3 (and 7) | "No 200 carrying an error object in the body." | Return 409 with your standard error envelope. Success should be 204 (not verified, since I don't know what it returns today). |
| 4 | `POST /shipments/{id}/cancel-shipment` and `POST /carriers/{id}/verify-carrier` put a verb in the URI. The noun is redundant, since the resource is already in the path. | 1 | "Resources are nouns, never verbs." | Pick one custom-method convention and apply it to every action endpoint: `/cancel`, `/verify`. Keep the old routes as deprecated aliases. |

- **Finding 4** is the weakest of the four. The checklist allows a deliberate custom-method suffix, and yours is consistent between the two endpoints. The real defect is the redundant noun, plus any other action endpoint that follows a different pattern.
- **Finding 3:** `{"ok", "message"}` is also a one-off error shape. Choose one envelope for every endpoint, ideally RFC 9457 `application/problem+json`. The code taxonomy and message wording belong to `api-error-design`.
- **Finding 1, casing choice:** I picked snake_case from only 2 endpoints. Count fields across the full spec before locking it. The `{eventId}` path parameter hints that camelCase exists elsewhere. Either casing passes, as long as it is the same everywhere.

## Improvements (may ship open)

1. **Timestamp format.** Your partners emailed about the `createdAt` timezone format. Check whether `/shipments` emits the same format. If the two differ, that is a shape inconsistency and becomes Must-change. Standardize on RFC 3339 UTC with `Z`.
2. **`shipmentCount` on `/carriers`.** If carriers are shared across customers, this field may leak other tenants' volume. If it is a live `COUNT`, it can be slow at scale. Confirm both before launch. A tenant leak would be a security finding.
3. **`{eventId}` and `{attachmentId}` path parameters.** They are camelCase while the fields are snake_case. Rename them in the spec.
4. **`/thumbnails` is plural.** Is it a list or one image? Clarify the name when you fix finding 2.
5. **Spec and idempotency.** If no OpenAPI spec exists, that is itself an Improvement. Check whether the unsafe POSTs (`cancel`, `verify`) accept idempotency keys or document their retry behavior (`api-idempotency-retry`).

## Why timing matters

Every Must-change fix is breaking for the 6 partners. Today you can list, email, and migrate every affected client. After launch you can't. This is the cheapest moment you will get.

Proposed schedule (rough estimates; adjust to your team):
1. **Week 1, about 2–3 days of work:** ship the aliases and dual fields (findings 1, 2, 4). Ship the 409 and envelope change behind an announced date (finding 3).
2. **Week 1:** email the 6 partners with the old-to-new mapping and a sunset date.
3. **Week 4:** remove the old names, leaving 1 week of buffer.
4. **Launch docs:** document only the new names. Hidden aliases still get depended on, so set `Deprecation` and `Sunset` headers on every old route.

The versioning policy (`api-versioning-policy`) should own the exact dates.

## Ship gate

- **4 Must-change findings are open, so launch is blocked.** Each one needs to be fixed or recorded as a documented deviation with a rationale.
- Improvements 1–5 may ship open. Improvement 1 may upgrade to Must-change after the format check.
- **Accepted deviations:** none recorded yet.

## Style guide

Adopting a guide is how you stop repeating these findings. Fork a public corpus such as Zalando's and run its Spectral ruleset in CI. That takes an afternoon. If you want a standing review process too, tell me how many teams ship APIs and I'll design it.

**Next:** send the spec and the sample responses, and I'll walk the 4 skipped dimensions and the sibling checks.