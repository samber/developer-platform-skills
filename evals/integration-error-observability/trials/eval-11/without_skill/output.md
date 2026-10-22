# Plumridge: integration logs and the log viewer

## Short answer

Treat these as two problems with two fixes.

1. **Reconciliation:** stop asking raw logs to do it. Keep a small, structured, long-lived record of each call, and give customers a monthly reconciliation export.
2. **Non-engineers:** make a plain-language outcome view the default. Raw JSON and HTTP codes move behind a "Technical details" toggle.

## Part 1: Retention vs. monthly reconciliation

### Why 24h of raw logs is the wrong fix point

Raw request and response bodies are the expensive part. They also hold sensitive payroll data (salaries, tax IDs, bank details). Keeping them longer raises both cost and breach exposure.

Reconciliation only needs to answer three questions. What did you receive? What did you do with it? What was the result? A compact record answers all three.

### Change 1: Add a call ledger, kept 13–15 months

Write one structured, append-only row per API call. It should be about 0.5–1 KB.

- Timestamp, request ID, idempotency key, endpoint, and method.
- Customer and API key, plus the calling tool if detectable (User-Agent or header: Zapier, Make, n8n).
- Business identifiers: pay-run ID, employee ID, and the customer's own external reference.
- Outcome category (see Part 2), error code, and latency.
- Payload hash and non-sensitive totals (record count, gross total). No names or bank details.

Why 13–15 months: it covers monthly reconciliation plus a year-over-year comparison and a buffer for late disputes. Store it compressed in columnar form on object storage. At 1M calls a day that is roughly a few hundred GB a year before compression, which is cheap. Check this against your real volume.

### Change 2: Tier the raw bodies by what the call did

| Call type | Raw body retention |
|---|---|
| Reads, health checks, successful no-ops | 24h (unchanged) |
| Failed calls | 7–30 days, redacted |
| Money-moving writes (pay-run submit, adjustments) | 13 months, redacted and encrypted, in cold storage |

Most of the cost sits in high-volume reads. Long retention for the small share of writes that change money is cheap by comparison. Sensitive fields (tax IDs, bank details) should be tokenized or hashed before they go to the cold tier.

### Change 3: Give customers a reconciliation export

Customers need an export, not a log search.

- A monthly CSV or JSON statement per customer, generated from the ledger. It lists every accepted, rejected, duplicate, and pending submission with the customer's own reference IDs.
- A "pay-run events" endpoint and webhooks, so finance tooling can pull the same data.
- Optional scheduled email delivery on the 1st of each month.

### Watch-outs

- Get legal or compliance sign-off on retention periods and on what is stored in the cold tier. This is payroll data, and data-minimization rules (GDPR/CCPA) may apply. Your customers' own record-keeping rules sit on top of that.
- The ledger is a derived record. The payroll system of record stays the source of truth, so say so in the docs.

## Part 2: Making the viewer usable for ops staff

Today's viewer shows what an engineer wants. About 60% of your users think in pay runs and employees, not requests and status codes.

### Change 4: Show outcomes instead of status codes

Replace the HTTP code with a small, fixed set of outcomes:

- ✅ Succeeded
- ⚠️ Succeeded, but nothing changed (duplicate or no-op)
- ❌ Rejected: your data needs fixing
- 🔴 Failed on our side
- ⏳ Received, still processing

HTTP 400 and 422 look the same to an ops person. "Your data needs fixing" vs. "our side failed" is the question they are actually asking.

### Change 5: Add an error catalog with plain-language fixes

Give each error a stable code. Write the message for the person using the tool:

> **Rejected:** `pay_date` "03/04/2026" isn't a valid date.
> We expected `YYYY-MM-DD` (for example 2026-04-03).
> **Fix in Zapier:** add a Formatter → Date/Time step before this action.

- Name the field, the value received, and the value expected.
- Add per-tool fix snippets for the top 2–3 no-code tools.
- Start with the 10–20 most common errors. Pull them from the last few months of tickets before writing anything.

### Change 6: Organize logs by business object

- Add a timeline view: "March pay run → submitted → accepted → processed".
- Search by employee name or ID, pay-run, external reference, and date range. Request ID stays available but is not the main path.

### Change 7: Keep raw JSON, but move it

- Put it behind "Technical details", with copy buttons.
- Highlight the offending field and show expected vs. received.
- Engineers still get everything. Everyone else gets a readable default.

### Change 8: Turn "it's not working" into an actionable ticket

- Add a **Report a problem** button on every log entry. It attaches the request ID and the plain-language context to the ticket automatically.
- Replace the free-text ticket form with guided fields: which tool, which step, and a log link.
- Give support the same view customers see. Write macros per error code.

### Change 9: Alert people so they don't have to watch logs

- Send an email or Slack alert on failure spikes.
- Alert on missing activity, such as "no pay-run submission received 5 days before payday".
- Send a weekly digest of failures by cause.

### Change 10: Fix the cause upstream

- Add a **validate / dry-run** endpoint and a "test this payload" button in the viewer.
- Publish official connectors and templates for the top no-code tools (Zapier, Make, n8n). This is likely the highest-leverage change if 60% of builders use them. Correct date and number formatting built into the connector removes whole classes of errors before they reach a log.

## Suggested order

1. **Weeks 1–2:** ship the call ledger and the 24h-to-13-month tiering for money-moving writes. This stops the data loss. Add the request ID to every ticket flow.
2. **Weeks 2–6:** ship outcome categories and the error catalog for the top errors, with the "Technical details" toggle.
3. **Weeks 6–10:** ship the timeline and search, the report-a-problem button, and the monthly reconciliation export.
4. **After that:** ship alerts, dry-run validation, and official connectors, starting with the most-used tool.

## How to know it worked

- Share of tickets with a request ID attached.
- Time to first correct response, and reopen rate.
- Share of errors resolved without a ticket (viewed the error, no ticket within 24h).
- Share of tickets covered by the top 10 error codes.
- Reconciliation-related tickets and "can you resend the logs" requests, which should fall toward zero.

## Assumptions to check

- The "60% non-engineers" figure should be confirmed by tagging a sample of tickets by tool and cause. The error catalog depends on it.
- Confirm whether the viewer is customer-facing or internal-only. I assumed customer-facing.
- Confirm whether the API already returns stable error codes. If not, that is a prerequisite for Change 5.
- Call volume and legal retention requirements are unknown. I used 1M calls a day as an illustrative figure, so check the sizing against real volume.