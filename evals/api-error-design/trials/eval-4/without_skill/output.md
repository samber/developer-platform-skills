# Meterhaus error-code migration

## Recommendation

Don't rename in place. Ship the new scheme additively, behind a per-key API version. Updating the docs page the same day won't help. The 2,300 consumers' code won't read it.

Their code does `if (err.code === "billing_failed")`. After an in-place rename, that branch silently stops matching. Failures fall into the generic handler, which may retry, swallow the error, or page someone. Billing and meter-validation errors are the likeliest to be handled specifically. Five years of integrations also include consumers who never read changelogs.

## Target design

**1. One registry as the source of truth.** A single file lists every code:

```yaml
- code: BILLING_FAILED
  legacy: [billing_failed]
  http_status: 402
  replaced_by: null
  status: active        # active | deprecated | removed
  since: v2026-11
```

Generate the OpenAPI enum, SDK constants, the docs page and the mapping tests from it.

**2. A naming rule, enforced.** Codes must match `^[A-Z][A-Z0-9]*(_[A-Z0-9]+)*$`. Add a contract test that every code the API can emit is in the registry. A CI failure on an unregistered code stops new drift.

**3. Mapping needs judgment, not a regex.**
- `billing_failed` → `BILLING_FAILED` and `INVALID-METER` → `INVALID_METER` are mechanical.
- `ERR_17` needs a human-chosen meaningful name. Review it with whoever knows what it means.
- Check for collisions. Two old codes may normalise to the same new one, and that's a semantic merge. Decide it explicitly.
- Keep HTTP status codes unchanged. Only the code string changes.

**4. Response shape during the transition.**

```json
{
  "error": {
    "code": "billing_failed",
    "error_code": "BILLING_FAILED",
    "message": "…"
  }
}
```

- Pinned (old) version: `code` stays legacy, and the new `error_code` is added alongside.
- New version: `code` is the canonical value and `legacy_code` is included for one version.
- Add a `Deprecation` header and a docs link whenever a legacy code is served.

## Removing about a dozen codes

"Nobody should be using them" is a hypothesis. Test it before cutting.

1. For each candidate, pull 90 days of emissions from logs, broken down by API key.
2. Zero emissions: remove it in the new version.
3. Still emitted: the condition still occurs, so say what it returns instead. Map it to a specific replacement or a generic code such as `INVALID_REQUEST`, and record it in `replaced_by`.
4. Emitted to named consumers: contact them directly before the cutoff.
5. Never remove a code that clients can still receive. Mark it deprecated, keep it in the registry, and drop it only at sunset.

## Rollout phases

| Phase | What happens | Exit criteria |
|---|---|---|
| 0. Inventory (1–2 wks) | Emission counts per code per key, plus a list of every internal consumer of the codes (dashboards, alerts, webhooks, SDKs, support macros, status page) | Registry complete, collisions resolved |
| 1. Additive release | Ship `error_code` next to `code`. Existing keys are pinned to the current version. Docs show both. | Zero behaviour change for pinned keys, verified by diffing responses on replayed traffic |
| 2. SDKs and docs | Release SDK constants for the new codes. Docs lead with the new codes and have a legacy-to-new table. | SDK adoption visible in user-agent telemetry |
| 3. Outreach (2–3 months) | Email the keys that still emit or match legacy codes. Add a dashboard of keys per code. Offer a migration checklist and a sandbox toggle to try the new version. | Weekly burn-down of keys still on legacy |
| 4. Default flip | New keys default to the new version. Existing keys stay pinned unless they opt in. | No spike in error-handling bugs or support tickets |
| 5. Sunset | Announce a date at least 6 months out, with reminders at 90, 30 and 7 days. Remaining keys get a final direct contact. | Legacy traffic under an agreed threshold, say below 1% of keys |

Treat the long tail as an account-management problem. It won't fix itself.

## Testing

- Replay production traffic against both versions and assert that the old version's responses are byte-identical.
- Check for each code that the legacy and canonical forms map one-to-one, with no orphans in either direction.
- Add a test that fails if any emitted code is missing from the registry or breaks the naming regex.
- Test webhook payloads and any error codes embedded in async job results too, not only synchronous HTTP responses.

## Rollback

The version gate is a server-side switch. If a cohort breaks, move those keys back to the old version without a deploy. An in-place rename gives you no such option, because rolling back would break the consumers who already migrated.

## If you still want a hard cutover

You'd be accepting breakage for some consumers, so at minimum:
- Announce it at least 6 months ahead, by email to every key owner, not only on the docs page.
- Return the old code in the `message` or a `legacy_code` field for a grace period.
- Keep a kill switch to restore old codes quickly.
- Staff support for the day-of surge.

That is roughly the same work as the versioned path, with more risk and no escape hatch.

## Decisions for you

1. Is there an API versioning mechanism today (a header or a per-key pin), or do we need to build one?
2. Is a 6–12 month sunset acceptable?
3. Who owns choosing the meaningful name for `ERR_17` and the other numeric codes?