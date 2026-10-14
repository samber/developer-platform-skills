# Plumridge: integration error observability

I read `SKILL.md` and all four references. Your message answers some of the skill's clarifying questions but not all of them. I've marked the assumptions below, and the open questions are at the end.

## Diagnosis

Both problems are named failure modes in the skill.

| Your problem | Skill failure mode |
|---|---|
| 24h retention, monthly reconciliation | "Log retention shorter than the time it takes a partner to notice, so the evidence expires before the investigation starts." |
| Raw JSON plus status codes, 60% non-engineers | A `400 Error` row with no error code or request ID produces a ticket. Raw JSON is noise to the no-code segment. |

The audit baseline is simple. A monthly reconciler sees a wrong total around day 28 to 31. Your log expired 27 or more days earlier, so every such ticket is unanswerable by the integrator. Failures that no one notices for weeks are also the ones you can't help with, which is why payroll problems feel like "it's not working."

You serve two segments from the skill's ownership model:

- **Single-account integrators.** These are the engineers, about 40%. They get the full request detail.
- **No-code and agent builders.** These are the ops staff, about 60%. They get one plain-language failure list scoped to their flow, with a "what do I do" line on each entry.

Fleet partners appear only if you have ISVs with many installs. That's open question 2 below.

## 1. Fix retention without keeping 30 days of JSON

Split retention by what each layer costs, not one window for everything.

| Layer | Contents | Retention | Why |
|---|---|---|---|
| Request metadata row | Timestamp, method, path, status, error code, request ID, integration identity, account, latency, and the field that failed | Longer than your slowest realistic reconciliation lag. Start at about 90 days and set it from ticket data. | Rows are small and carry the answer to most tickets. |
| Request and response bodies | Raw JSON | Keep short, or keep failures only. | Bodies are the expensive part, and in payroll they hold SSNs, salaries and bank details. |
| Event log | Business events, such as pay run created or employee updated, with a pointer to the causing request | Same as metadata, or longer. | This is what monthly reconciliation needs: "what did it change". |
| Daily aggregates | Per-integration counts by 4xx, 5xx and 429, plus top error codes | 13 months | They cost almost nothing, and they answer "when did this start" across a year-end close. |

- **Publish the windows.** An undocumented window gets discovered during an incident.
- **Set the metadata window from data.** Measure the gap between first failure and the ticket for your last 20 tickets. The window must exceed the slow end of that gap. That number is self-set, not an industry figure.
- **Legal may cap what you can show (open question 7).** The skill says "no bodies leave our boundary" removes payload logging from the menu. Metadata-only logging then becomes the ceiling, and the plan above still works. Payroll bodies almost certainly need a redaction pass anyway:
  - Strip credentials unconditionally.
  - Mask PII visibly, so the integrator knows a field was withheld rather than absent.
  - Enforce tenant isolation structurally, not by an application-code filter.
  - Treat the redaction rules as a published contract.

## 2. Change what the viewer shows

Keep raw JSON, but behind a "Technical details" toggle for the engineers.

**Default view for everyone: a plain-language row.**

```
Today 14:22 UTC   Pay run NOT created        [Fix needed]
  What happened   Employee "J. Moreau" has no valid tax ID, so the pay run was rejected.
  What to do      Open the employee in Plumridge, add the tax ID, then re-run the step.
  Flow            "Monthly payroll sync" (key: zapier-payroll-prod)
  Support code    req_8f2c1ab9d3e04c7f   [Copy]
  > Technical details (status 422, code invalid_tax_id, field employee.tax_id, request/response)
```

What this needs:

- **A message catalogue.** Map every machine-readable error code to a one-line plain-language cause, a "what to do" line, and an owner label: yours to fix, theirs to fix, or quota.
  - The 4xx, 5xx and 429 split decides the wording. A 5xx must never read as the customer's fault.
  - The error body text is owned by `api-error-design`. Coordinate with it rather than redesigning it here.
- **Status code plus error code on every row.** A bare `400` tells an integrator nothing their client didn't already know.
- **One entry per flow.**
  - Tag every request with the API key or app ID at ingestion, and never retrofit it.
  - Require named keys, and encourage one key per automation, so "Monthly payroll sync" is a filterable view.
- **A "Failed only" default filter**, newest first, grouped by flow.
- **Access for the person who actually maintains the automation.**
  - Ops staff are often not the account owner.
  - Add a viewer role, or a read-only log invitation, so they don't borrow the owner's login.
  - The skill calls this an access-model gap, not a logging gap.

## 3. Make "it's not working" a ticket you can resolve in one lookup

- **Return a request ID on every response**, success and failure, in a response header (`X-Request-Id`, opaque UUIDv4).
  - Also put it in the error body. No-code tools usually show the body and drop the headers.
  - Accept a client-supplied ID and echo it.
  - Never regenerate it mid-flight.
- **Make the ID searchable in the viewer.** A header with nothing external that can resolve it produces integrators quoting a string only your engineers can look up.
- **Add a "Copy support code" button and a search box**, as in the row above.
- **Change the ticket form.**
  - Add a required "Support code" field, with help text pointing at the Failed list.
  - A non-engineer can copy a code even when they can't describe a failure.
- **Document the lookup path next to the error docs**, not on a separate observability page. Ops staff land there when something breaks.
- **Defer propagation to sub-processors.** Promote it only if your support answer is "that failure came from our provider and we can't see it", for example a bank or tax authority hop.
- **Add a correlation ID only if multi-call flows show up in tickets.** An example is "the whole pay run flow broke". A request ID is enough to start.

## 4. Tell people before the reconciliation does

For a payroll API, ask whether the integrator loses money within hours (question 6). Pay-run cutoffs suggest yes, so I'd go one rung above the skill's default.

1. **Weekly or daily digest per integration.** This is the skill's default rung. Write it in the same plain language as the viewer, with failures by class and a link to the filtered Failed list.
2. **Immediate state-change alerts.** Cover credentials expired or revoked, key disabled, and subscription lapsed. These are single events, sent with no cooldown.
3. **Threshold alerts with a cooldown, promoted for payroll.**
   - Fire once when the error rate crosses the integration's own baseline.
   - Hold a cooldown of 30 minutes or your typical incident length before the same integration can alert again. (30 minutes is Salesforce's default, not a rule.)
   - Send a recovery message.
   - State what you ruled out. For example: "no Plumridge release in this window".
   - Name the top error codes and link into the filtered log.
4. **Volume-drop detection.** An automation that stops calling, such as an expired Zapier connection or a turned-off scenario, produces no errors.
   - Compare call volume with the integration's own baseline, and weight it around pay-run dates.
   - This is the most likely cause of a payroll that silently didn't run.

Do not alert per failed call. That is the alert-fatigue failure mode, not a rung.

Send alerts by email to a configurable contact, not only to the account owner. No-code builders don't live in your dashboard.

## 5. Webhooks and replay, if you have them

- **Webhooks exist (question 5).** Expose the per-attempt delivery log you already write: attempt number, timestamp, actual failure reason, response received, next retry. It retires "the webhook never arrived."
- **Replay events, never synchronous requests.**
  - A re-issued POST on a payroll API can pay someone twice.
  - Give the integrator the full request detail so their own client re-sends.
  - For event replay, use a bounded published window, the same event ID on every replay so consumers can deduplicate, and independence from your own retry schedule.
  - Promote replay only if the audit shows integrators losing events during their own downtime.

## 6. Provider-side fleet view (last)

Build this after the surfaces above, using the same aggregation read from your side.

- Rank by blast radius (installs affected out of installs total), not raw error count.
- Keep "broken since our deploy" separate from "broken since their change".
- Add a silent-integration list for volume drops.
- Add a named contact per row.
- Don't publish a per-partner reliability number or health grade you can't defend line by line.

It matters most if you have partners who run across many customer accounts. Otherwise it's an internal support queue.

## Build order

| Step | Ship | Effort and why now |
|---|---|---|
| 1 | Request ID in headers on every response, plus a retention policy decision with published windows | Hours for the middleware. Both are cheap and unblock the rest. |
| 2 | Metadata-only request log with plain-language rows, search by request ID, "Copy support code", and ticket form field | Biggest deflection. Covers every segment. |
| 3 | Daily aggregates by 4xx, 5xx and 429 per API key, and state-change alerts | Needs the ingestion tag from step 2. |
| 4 | Digest, then threshold alert with cooldown, then volume-drop | Reaches ops staff who never open a dashboard. |
| 5 | Delivery-attempt log (if webhooks), then event replay if the audit says so | Largest effort. Do after the core. |
| 6 | Fleet view | Internal queue for proactive outreach. |

## How to measure it

- **Failure-class coverage (gate).** From your last 20 tickets, classify each as request not found, webhook never arrived, silent data mismatch, auth failure or rate-limit confusion. Check that every class now has a surface an integrator can use unaided.
- **Request-ID resolvability (gate).** Take one ID from a real response and look it up as an outside, non-owner user would. This is binary.
- **Self-serve deflection (trend).** Re-classify a fresh batch of tickets after launch and compare with your own before-and-after. No industry benchmark exists.
- **Time from failure to the integrator acting (trend).** Track it per notification rung.
- **Alert action rate (trend).** A falling rate means fatigue. Widen thresholds or lengthen the cooldown before adding a channel.

## Open questions

These are the skill's clarifying questions I couldn't answer from your message. Each one reorders something above.

1. What can an integrator see today besides the raw viewer? Is there a delivery log, and is the viewer available to non-owners?
2. Are there partners or ISVs with many installs, or only single-account integrators plus no-code builders? This decides how much weight the fleet view and push alerts get.
3. What do the last 20 tickets look like, and what is the typical gap between failure and ticket? This sets the retention window and the build order.
4. Is every request already tagged with an API key or app ID at ingestion?
5. Do you send webhooks, and do you record per-attempt outcomes?
6. Do integrators lose money within hours of a failure (pay-run cutoffs), or only at reconciliation? I assumed hours, which promotes threshold alerts.
7. Can bodies be shown to a third party at all, and who signs off? If not, bodies drop out and metadata is the ceiling.
8. What are your deadline, effort ceiling and storage budget? A hard deadline means steps 1 and 2 only.

I can store the retention windows, aggregation key, alert thresholds and redaction rules in `developer-platform-context.md` once you confirm them.