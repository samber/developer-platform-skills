# Clovermast integration error visibility: what we can ship under "no PHI leaves the tenancy boundary"

I followed the `integration-error-observability` skill. I couldn't ask its clarifying questions, so the assumptions are listed at the end. Treat them as things to correct.

## The decision

Legal's answer removes payload logging from the menu entirely. Metadata-only logging is the ceiling, and that is enough for most of the 70% pile.

The integrator already holds the request body they sent. What they lack is the reason it failed. The reason is metadata: which stage rejected it, which field, which rule, and whether anything was stored. The viewer needs to show those. It does not need to show bodies.

**Ship a request log with structured failure detail but no values.** It is the rung that fits a pile dominated by synchronous POST failures. Webhook delivery logs, replay and fleet tooling come later, or are cut.

## The log row

The current viewer shows `timestamp, method, path, status`. The new row:

```
2026-10-08 14:22:07 UTC  POST /v1/claims  422  claim.line_dx_pos_mismatch
  request_id   req_8f2c1ab9d3e04c7f
  app / key    acme-pm v2.3 · key …a91f      tenant acct_19KdQ2
  stage        validation   (rejected, nothing stored)
  problems     /lines/2/diagnosis_code      rule=dx_pos_mismatch
               /lines/2/place_of_service    rule=dx_pos_mismatch
  retryable    no, fix the payload
  idempotency  key present, no prior result
  latency      84 ms     request 18 KB     response 312 B
  docs         <link to the error-code page>
  bodies withheld by policy
```

The fields that do the work:

- **Machine-readable error code.** A status code alone tells the integrator nothing new.
- **Stage.** One of `auth | validation | eligibility | payer-downstream | internal`. For a 5xx or timeout it also names the dependency.
- **Outcome.** One of `not processed | processed | unknown`. After a timeout on a synchronous POST, "did my claim get created?" is the real question.
- **Problems.** Field pointers plus a rule ID. Array indexes are fine, so the integrator can find line 2 in their own data.
- **Retryable.** A yes/no flag.
- **Idempotency state.** Shown only when the key matches a strict opaque-ID pattern. Otherwise show "present (non-conforming)", because client-chosen keys can embed PHI.

## PHI leaks through metadata too

The skill's own example row includes `"SW1A" is not a valid postal code`. That is a value echo, and in our domain it would be PHI. These are the ways metadata leaks:

| Leak path | Rule |
|---|---|
| Raw path, e.g. `/v1/patients/123/claims` | Log the **route template**, `/v1/patients/{id}/claims`. |
| Query string | Drop it, or keep allowlisted parameter **names** only. |
| Validation messages that echo values | No free text. Messages come from a closed catalog of enum codes. |
| Dynamic JSON keys in field pointers | Generate pointers from the schema. Map keys become `*`. |
| Downstream payer error strings | Map them to our own codes. Unmapped becomes `downstream_unmapped` plus the dependency name and its numeric status. Never pass strings through. |
| Headers | Allowlist about 6 (content-type, user-agent and similar). Never log `Authorization`. |
| Body hashes | Skip them. A hash of a low-entropy field can be brute-forced. |

## Making the rule structural

Redaction after the fact fails with PHI, so the design is an allowlist, enforced in four places:

1. **A dedicated record type.** Validation and error paths emit a `DevLogRecord` whose only fields are enums, pointers, numbers and IDs. It has no string field that could carry a value. The developer-facing store is separate from internal logs and is never fed by scraping them.
2. **A write-time schema check.** Rows with unknown fields are rejected.
3. **A PHI canary test in CI.** Fixture requests carry sentinel values such as a fake SSN, name and DOB. They are sent through every error path (4xx, 5xx, timeout, downstream failure). The test asserts the sentinels never appear in the developer store, the viewer API responses, digests or alert payloads. I'd also break the code on purpose once to confirm the test goes red.
4. **A published field list.** It is the contract. Adding a field needs Legal sign-off, and loosening it later is a privacy incident.

Notification channels also sit outside the boundary. Emails and alerts carry counts, codes and a login-gated link, with no field content.

## Access and retention

- **Scope:** per tenant and per app, with the scoping enforced structurally, for example by row-level security rather than a query filter. Add a separate "partner engineer" role for people who maintain an integration but aren't users of the customer account.
- **Retention:** 30 days as the default. Claims are often reconciled weekly or monthly, so 24–72 hours would expire the evidence early. Confirm the window with Legal.
- **Internal support:** keeps body access inside the boundary, with access auditing. That is outside this scope but needs an owner.

## Build order

**Week 0 (days, mostly free)**

1. **Ask Legal one question:** does a record of `{tenant, time, route template, error code, field pointer}` fall under PHI? Everything below assumes "no". If the answer is "yes", the viewer stays internal and this becomes a support-assisted flow.
2. Classify the last 20 tickets. For each, ask whether code, stage, field pointer and outcome would have answered it. That share is your baseline and your target.
3. Ship the request ID: an opaque UUIDv4 in the response header of every response, and in the error body (coordinate with `api-error-design`). Accept a client-supplied ID and echo it. Persist it in the logs support searches.

**Phase 1 (core)**

- Define the error-code catalog and `DevLogRecord`. Cover the top 10–20 codes by ticket frequency on `POST /v1/claims` and the other synchronous POSTs first.
- Add the new log row to the viewer, with search by request ID and filters on status, code, route and time.
- Add the canary test and the retention policy.

**Phase 2 (reach)**

- Per-integration aggregation, tagged at ingestion by API key or app ID, split into 4xx, 5xx and 429, with top error codes.
- A daily digest per integration as the default notification.
- Immediate state-change alerts for revoked credentials, a disabled integration or an expired subscription.
- A volume-drop detector against each integration's own baseline.

**Phase 3 (only if the audit justifies it)**

- Threshold alerts with a cooldown, 30 minutes to start, plus a recovery message. This matters if partners lose money within hours or run fleets of installs.
- An internal fleet view ranked by blast radius, kept separate from the "broken since our deploy" queue.
- A correlation ID, if multi-call flows such as submit, eligibility and status show up in tickets.
- A webhook delivery-attempt log, if webhooks exist. Show endpoint, attempt number, failure class and next retry. Do **not** show the response body our server got back, because an integrator's endpoint can echo PHI.

## Not shipping

- **Request and response bodies.** Legal ruled these out.
- **Replay of synchronous POSTs.** Re-issuing a POST on someone's behalf is wrong anyway, and replay needs a stored-body PHI store.
- **Webhook "resend" that never displays the body.** Deferred. It still sends PHI to an external endpoint, so it needs its own Legal question.
- **Per-failure alerts.** Those are the alert-fatigue failure mode.

## Honest limits

- A **200 that did the wrong thing** and silent data mismatches still need support, using the request ID and internal body access.
- Some claim-semantic rejections will still need a docs page per rule ID. Budget for that, because the rule ID is only useful if the docs explain it.

## Gates

1. **Failure-class coverage.** Each ticket class has a surface, or a written reason it doesn't.
2. **Request-ID resolvability.** Take a real ID from a response and look it up as an outside user would.
3. **Zero canary leaks in CI.** This gate is specific to our setup.

Trends to watch, with no pass threshold: self-serve deflection on a fresh batch of 20 tickets, time from failure to partner action, and alert action rate. No industry benchmark exists, so compare against your own baseline.

## Assumptions to correct

- The log viewer faces external integrators.
- The mix likely includes ISVs with fleets of installs, such as practice-management vendors and clearinghouses.
- Tagging by API key or app ID at ingestion is unconfirmed.
- Whether webhooks exist is unknown.
- Filing deadlines make a digest-first approach sufficient. Is a partner losing money within hours?
- There is no deadline or team-size constraint yet. Phases are ordered by dependency, not dated.