# Fixing Fieldnest's error documentation, and how to measure it

## The diagnosis

About 251 of last month's 412 tickets (61%) were "what does this error mean?" Two causes sit behind that number, and only one is a docs problem.

1. **The docs can't answer the question.** One shared "Error object" page describes the shape of an error. It never says what a given error means or how to fix it. An integrator who pastes `422 invalid_geometry` into a search box lands on a schema page that tells them nothing.
2. **Support can't trace the request.** A screenshot carries no request ID, no timestamp that can be matched to logs, and no account context. Even a perfect docs page leaves you stuck on the tickets that really are bugs.

The second cause is a product change, not a documentation change. It will probably do more for you than any amount of writing.

## Part 1: the fix

### Step 0 (week 1): make errors traceable

This is the highest-leverage change. Ship it before or alongside the docs.

- **Put a `request_id` in every error body and in a response header** (for example `X-Request-Id`). Log it server-side with account, endpoint, status and the validation failure detail.
- **Add a `doc_url` field to the error body**, pointing at that code's own page (for example `https://docs.fieldnest.example/errors/invalid_geometry`).
- **Use stable, machine-readable `code` values** that are separate from the human message. Never rename a code once it's published.
- **Make SDKs and logs surface the ID.** Exceptions should print `request_id`, so integrators paste text instead of a screenshot.
- **Add a "Request ID" field to the support form and make it required.** Add an auto-reply to screenshot-only tickets: "Please send the `request_id` from the response."

The payoff is that a ticket with a request ID takes support minutes to trace, and many tickets will stop being filed because the error links to its own fix.

### Step 1 (week 1-2): build the ranked queue from tickets

Don't write pages for errors you imagine. Work from the 412 tickets.

1. Export the last 2-3 months of tickets. Add error telemetry (error counts by code) and docs search logs, so you see silent failures as well as the ones people report.
2. Cluster by error code or message. Ten tickets about one cause are one page.
3. Rank by reader-hours saved per hour of writing and verification. Don't rank by raw frequency alone.
   - Write the frequent, reproducible errors first.
   - Move up any error that blocks first use (signup to first successful call), because those readers leave without filing a ticket.
   - Promote rare, expensive errors that hit contract customers in production, even with few tickets.
4. Route clusters that are really product defects (bad messages, bugs) to engineering. A page for an error the product could stop emitting makes the defect permanent.

Expect a short head. Usually 15-25 codes account for most of the tickets.

### Step 2 (weeks 2-5): one page per error code

Replace the shared schema page with one addressable page per code. Keep the schema page as a short reference that links to the catalog.

Each entry has six parts, in this order:

1. **Message**: the exact text from a real run, in a code block, with only genuinely variable parts replaced by placeholders.
2. **Applies to**: API versions, endpoints, plans.
3. **Cause**: one or two sentences.
4. **Fix**: numbered, executable steps. Branch by cause and order the branches by how often each is the real cause.
5. **Confirm it worked**: the response or state that proves the fix.
6. **Still stuck**: where to go and what to attach, which is always the `request_id`.

Example for an agritech API:

> **`422 invalid_geometry`: "Field boundary polygon is not closed or self-intersects"**
> *Applies to:* `POST /v2/fields`, `PUT /v2/fields/{id}/boundary`
> *Cause:* the GeoJSON ring's first and last coordinates differ, or two edges cross.
> *Fix:* (1) Check that the first and last coordinates are identical. (2) Check the ring is `[lon, lat]`, not `[lat, lon]`. (3) Run the polygon through a validity check (`ST_IsValid` or Shapely's `is_valid`) and repair self-intersections.
> *Confirm:* the same request returns `201` with a `field_id`.
> *Still stuck:* contact support with the `request_id` from the response.

Writing rules:

- Put the error string in the page title, first heading and body. Integrators search by pasting it.
- Repeat the string on every entry that shares it, rather than linking to a common section.
- Answer on the first screen, before any background explanation.
- Don't write "simply" or "just". The reader is already failing.
- Strip real tokens and customer identifiers from examples.
- Verify each fix by reproducing the failure and running your own steps. If you can't reproduce an error, say "reported, not reproduced" on the page.
- Stamp each page with an owner and a last-verified date.

### Step 3: wire the pages to where failures happen

- Every endpoint's reference page links to its specific error codes, replacing the single "Error object" link.
- `doc_url` in the payload and the SDK exception message both link to the page.
- Add a triage page for symptoms with no code (such as "request hangs" or "empty results").
- Add a "Known issues" page for confirmed bugs with unshipped fixes, and retire entries when the fix ships.

### Step 4 (medium term): generate the catalog from one source

Declare the codes in one machine-readable file (an enum or YAML) that both the API and the docs build read. The code constant and the doc entry then can't drift apart. PostgreSQL and Rust generate their error documentation this way. This is engineering work, so schedule it separately.

If an AI assistant answers from your docs, re-index after publishing. Otherwise it keeps answering from the old pages.

## Part 2: the target and measurement

### Why "error-related tickets under 10% of volume within a quarter" is a bad commitment

- **It's undefined.** "Error-related" isn't a category you track today. The 61% figure covers one specific pattern (screenshot plus "what does this mean"), not every ticket that touches an error. You need a taxonomy before you can have a baseline.
- **It's a ratio, so it can move for the wrong reasons.** A launch that adds non-error tickets lowers the share. A surge in new integrators raises it. Reclassifying tickets or hiding the contact form also hits the target without helping anyone.
- **6x is not supported by evidence.** Cutting from 61% to under 10% in one quarter assumes docs can resolve almost every error ticket. Gartner's December 2023 survey of 5,728 customers found only 14% of customer service issues fully resolved in self-service, and 36% even for issues customers rated "very simple". Developer docs may do better, but nobody can promise 6x.
- **Part of the target is outside docs' control.** Some tickets are real bugs or account problems. Docs can't deflect those. Only traceability helps.

### What to commit to instead

Offer leadership a small set of targets you control, plus one outcome target with a baseline you measure first.

| Metric | Definition | Why it works |
|---|---|---|
| **Traceable-ticket share** (leading) | Share of new tickets that include a `request_id` | You control it directly. A target like >80% by end of quarter is realistic. |
| **Coverage** (leading) | Share of the top 20 error clusters with a verified page | This is your own baseline, not a published benchmark, so negotiate it with your team's capacity. A reasonable start is 80% of the top 20 within the quarter. |
| **Tickets per covered code, normalized** (outcome) | Tickets mentioning code X per 1,000 API responses returning X, before vs after its page ships | Normalizing by traffic removes growth noise. Compare fixed windows, such as 4 weeks before and after. |
| **"What does this mean" ticket count** (outcome) | Count of that ticket type on covered codes | This is the 61% pattern, so it's the number leadership cares about. |
| **Median time to resolution on error tickets** | Hours from open to close | Traceability should cut it even when ticket volume doesn't move. |
| **Repeat-contact rate** | Share of error tickets where the same person returns within 7 days on the same code | Catches pages that deflect a ticket but don't fix the problem. |
| **Zero-result docs searches** | Searches for pasted error strings that return nothing | Shows the gaps in coverage. |
| **Docs-page-to-ticket rate per error** | Visitors to a code page who then file a ticket mentioning that code | Direct measure of whether each page works. |

Prefer resolution and repeat-contact measures over raw "deflection rate". Deflection looks good while readers fail and contact you again.

### A defensible commitment statement

Something like this:

> "By the end of the quarter, 80% of the top 20 error codes will have verified pages, every error response will carry a `request_id` and doc link, and at least 80% of new tickets will include a request ID. We expect 'what does this error mean' tickets on covered codes to fall materially, and we'll report the measured reduction per code, normalized by traffic. We'll set a numeric ticket-share target after the first month of clean baseline data."

Then set the numeric outcome target after four weeks of tagged data. The baseline will tell you what's realistic.

### How to build the baseline in week 1

1. Define 4-5 ticket tags: *error meaning*, *error plus bug*, *error plus account/config*, *error, no trace possible*, *not error-related*.
2. Hand-tag a sample of last month's 412 tickets to check the 61% and split it by tag. Don't tag all of them with an automated rule you haven't checked.
3. Record, per code, tickets and API error volume for the same window.
4. Keep the tagging definition fixed for the quarter, so before and after are comparable.

### Reporting cadence

- **Weekly:** coverage, traceable-ticket share, and the top 10 codes by ticket count.
- **Monthly:** per-code before/after, repeat-contact rate, zero-result searches.
- **End of quarter:** re-run the clustering. The same clusters reappearing unchanged means the pages aren't being found. That's a discoverability problem, not a volume problem. Clusters that moved mean you're working down the list.

## Timeline summary

| Weeks | Work | Owner |
|---|---|---|
| 1 | `request_id` and `doc_url` in errors, required request-ID field on support form, ticket tagging, baseline | Engineering + support |
| 1-2 | Cluster tickets, rank, agree the queue and coverage target | Support + docs |
| 2-5 | Write and verify top-20 pages, link from endpoints and payloads | Docs + support |
| 4-6 | Re-measure per-code ticket rates, set numeric outcome target | Support |
| Quarter+ | Generate the catalog from one source; maintenance triggers | Engineering |

## Open questions that would change this plan

- Do you have error telemetry and docs search logs, or only tickets? Without the unreported signal you'll only fix what people complain about.
- Are your error codes already stable and machine-readable, or are they free-text messages only? That decides whether Step 0 is a day or a month.
- Are your integrators mostly self-serve or contract customers? Contract customers promote rare, expensive failures up the queue.
- How many writing and verification hours exist per cycle, and whose are they? If nobody can reproduce failures in a test environment, the rare, expensive errors cost far more.
- Is there anything you can't publish, such as security-sensitive causes or unreleased fixes?