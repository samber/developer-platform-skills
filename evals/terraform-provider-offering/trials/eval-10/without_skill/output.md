## Verdict

**Don't commit to a v1.0.0 provider in three weeks.** Spend week 1 on demand and API fixes, then ship a **v0.x** provider on the 2–3 objects that qualify. Revisit 1.0.0 once real users have exercised it.

I didn't look at any files for this, so the API facts are only what you told me.

## Why not

1. **The demand is thin.** One customer asked in passing. That is a question, not a request. Three weeks of your only Go developer is roughly 10% of your engineering capacity.
2. **Your API breaks Terraform's core assumptions.** Terraform needs a stable identity, a safe create, and an in-place update. You have none of the three.

| Terraform assumes | Your API | Result |
|---|---|---|
| Resource has a stable ID | Key is employee email + company | An email change looks like a different resource. State holds a composite `company/email` ID, and renames mean destroy and recreate. |
| A failed or timed-out create can be retried | A retried create makes a duplicate | A timeout after server-side success leaves an orphan, and the next `apply` creates a second record. Duplicate payroll records are the worst possible failure for your product. |
| Update is in place | Update is delete-and-recreate underneath | The plan says "update in-place" while the server destroys the object. You'd need to mark nearly every field as force-replace, which is honest but ugly. Any history, links or in-flight payroll runs attached to the object may be lost. |

3. **A v1.0.0 is a compatibility promise.** Fixing the API later (stable IDs, idempotency) changes resource identity and import format. That would force a 2.0.0 within months. A 0.x version lets you fix this without breaking that promise.
4. **Employees are the wrong thing to manage in Terraform.** Employee records are high-churn HR data, and they would put PII in state files. A useful provider covers configuration: connections, integrations, webhooks, field mappings, company settings. I don't know which of those your API exposes, so check that first.

## What to do instead

**Days 1–2: validate demand (no code).**
- Ask the customer what they would manage with Terraform and why.
- Ask your 5–10 largest customers the same question.
- **Build if** at least 3 customers, or 1 large paying customer, name concrete resources.
- **Don't build if** you get vague "nice to have" answers. Send the customer an OpenAPI spec and a `curl` or `restapi`-provider example instead.

**Weeks 1–2: fix the API for the 2–3 config objects the answers point to.**
- Add an `Idempotency-Key` header on creates. This is the highest-value fix, and every SDK user benefits, not just Terraform users.
- Add a stable server-generated ID for those objects, with email + company as a secondary lookup.
- Add a real in-place update (PATCH) for those objects. If that is impossible, list the replace-on-change fields explicitly.
- These are backend changes. If your Go developer can't make them, the provider can't be done safely in this window, and the answer is "not yet".

**Week 3: ship `v0.1.0` as beta.**
- Use `terraform-plugin-framework` (not SDKv2).
- Support resource + data source + import for the 2–3 objects only.
- Add acceptance tests against a sandbox, GoReleaser with GPG-signed releases, and Registry docs and examples.
- Label it beta and say in the README what is unsupported (employee records).
- Treat v1.0.0 as a later milestone: after the API is stable, a few customers have used it for a month, and no schema changes are pending.

## If you override me and build against the current API anyway

- Use only the composite key as ID, and document that an email change replaces the resource.
- Send a client-generated marker (tag or external reference) and have `Create` search for it before retrying. This only works if your API can filter on that marker.
- On any create timeout, fail loudly with "state unknown, check for duplicates". Never retry automatically.
- Mark all fields force-replace, and warn in the docs that this is destructive.
- Ship it as `0.x`.

## Open questions

- Which objects does a customer actually need to manage, and are any of them config rather than employee data?
- Can your one Go developer change the API server, or only write clients?
- Does a delete-and-recreate update lose anything for the customer (history, links, payroll runs)?

Answer those three and I can turn this into a day-by-day plan.