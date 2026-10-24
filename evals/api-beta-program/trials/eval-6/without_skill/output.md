**Don't post "GA" and delete on Tuesday. Post a deprecation notice for the two dead endpoints, publish terms for the four live ones, and set the GA date after those terms exist.** That is a one-week change to the plan.

## Why the CTO's sequence breaks

- **GA with no written terms is a promise with no content.** Customers read GA as "stable, with notice before breaking changes". You have no owner and no notice period to back that up.
- **Delete-and-GA on the same day contradicts itself.** The first thing the GA announcement does is remove two endpoints without notice. Your 30 customers will read that as the real policy.
- **"Zero calls in 90 days" doesn't prove "unused".** Quarterly or annual freight jobs, customers mid-integration, and failed 401/404 calls can all hide behind it. A silent delete is also irreversible.
- **A versioning policy only governs what it names.** Check whether yours covers `/v1beta` at all, and whether customers ever saw it. Once you announce GA, today's behavior (including quirks) becomes the contract.
- **A `/v1beta` URL labelled GA stays a mismatch forever.** Customers will keep asking whether it's really stable.

## Sequence

**Before Tuesday (about 1–2 days):**

1. Name one owner for the API surface. Everything below needs one person.
2. Re-check the "zero calls" data. Confirm the log retention window, that it covers all regions and gateways, and that it includes 401/403/404 attempts. Search docs, SDKs, sales decks, support tickets and contracts for mentions of the two endpoints.
3. List which customers have credentials that can reach those two endpoints.
4. Call Pacific Crate before any public post. At roughly 40% of calls, they hold a de facto contract and the most to lose.

**Tuesday: publish the notice, not the GA:**

5. Post a changelog entry that does three things:
   - Announces that `/v1beta` is moving to GA, with the date.
   - Lists the four endpoints in scope.
   - Deprecates the two dead endpoints, with a sunset date at least 90 days out.
6. Add `Deprecation` and `Sunset` response headers to the two dead endpoints. Email every account that holds credentials for them.

**Before the GA date (about 2–6 weeks):**

7. Write the terms (one page, owner signs):
   - What counts as a breaking change.
   - Notice period. Use 12 months for GA, since 6 is thin for B2B customers.
   - Deprecation channels: headers, changelog and email.
   - Support and uptime expectations.
8. Review the four endpoints for contract warts: field names, error codes, pagination, rate limits, idempotency. GA freezes them, so this is the last cheap fix window. Share the draft terms and fixes with Pacific Crate and your top few customers and collect objections.
9. Ship the endpoints under `/v1` with identical behavior. Keep `/v1beta` as a working alias for the full notice period, so customers only change a URL when they choose to. Update docs and SDK defaults to `/v1`.
10. Announce GA with the terms linked. From that day your versioning policy governs the four endpoints.

**After the sunset date:**

11. Brown out the two dead endpoints for a day, then return `410 Gone` for a few weeks.
12. Delete them only after nobody has complained or called in that window.

## If the CTO insists on Tuesday for GA

Ship steps 5–7 in minimal form: the four endpoints under `/v1`, a short written terms page, and the two dead endpoints deprecated rather than deleted. Skip the contract review in step 8 and accept that today's quirks become the contract. Leave step 11 out entirely.

## One question

Do any of your customer contracts or order forms mention `/v1beta` endpoints by name? If so, legal needs to see step 6 before Tuesday.