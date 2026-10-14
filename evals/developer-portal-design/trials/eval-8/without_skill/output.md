# Orrery Labs: one-home plan

**Next action:** add the missing pieces below, starting with the first group, which is your real pain. Your list covers only docs. The three problems you described are docs, the dashboard, and failure debugging, and the failure-debugging surface has no entry on your list.

## What's missing

### 1. Failure visibility (your biggest gap)
- **Message log.** A searchable list by recipient, status, date, message ID, and API key.
- **Message detail.** A timeline per send: accepted, queued, delivered, bounced, deferred, or complained. It shows the raw SMTP response from the receiving server.
- **Error code reference.** One docs page per code with cause and fix. The API error body and the dashboard both link to it.
- **Webhooks and event types.** Configuration UI in the dashboard, with payload reference, signature verification, retries, and a replay or test button in the docs.
- **Suppression list.** Shows why an address is blocked and lets the customer remove it.
- **Support handoff.** The customer clicks "Contact support" from a message detail page, and the message ID is attached. Support opens the same view, read-only. This replaces the grep step.

### 2. Sending setup
- **Domain and sender authentication.** SPF, DKIM, and DMARC setup, with a DNS record checker in the dashboard.
- **Deliverability guides.** Warm-up, bounce and complaint thresholds, and why mail lands in spam.
- **Templates.** Management UI plus a docs page, if you offer them.
- **SMTP relay.** Credentials and docs, if supported.

### 3. API fundamentals (the reference docs need these as first-class pages)
- Authentication, rate limits and quotas, idempotency, pagination, and versioning.
- SDKs and libraries, with install and a minimal example for each.
- Changelog and deprecation notices.
- Migration guides from competitors, if you want to capture switchers.

### 4. Account and trust
- Usage and billing, plan limits, and upgrade path.
- Team members, roles, and key scopes (restricted keys that can only send, for example).
- Security and compliance: DPA, subprocessors, SOC 2 or equivalent, data retention.
- Status page and incident history.
- Pricing page.

### 5. Agent-readiness (cheap, so worth doing)
- `llms.txt` and Markdown versions of the docs pages.
- A "Copy as prompt" button on the quickstart.

## Where everything goes

**Root domain with path-based sections.** It's a single domain, so `/docs` and the dashboard share cookies. That enables a logged-in quickstart that shows the reader's own test key, and error links that work in both directions. The `status` page stays on a separate domain and infrastructure on purpose, so it survives an outage of the main site.

| Path | Auth | Contents |
|---|---|---|
| `/` | public | Marketing, pricing, security and compliance |
| `/docs/quickstart` | public | Quickstart, with live key if logged in |
| `/docs/guides` | public | Domain auth, deliverability, webhooks, templates, SMTP, migration |
| `/docs/api` | public | Reference: auth, limits, idempotency, pagination, versioning, endpoints |
| `/docs/errors/{code}` | public | One page per error code (permalinks, never renamed) |
| `/docs/sdks` | public | Per-language install and examples |
| `/docs/changelog` | public | Releases and deprecations |
| `/app/keys` | authed | Key management, scopes, rotation |
| `/app/logs` | authed | Message log and message detail |
| `/app/webhooks` | authed | Endpoints, delivery attempts, replay |
| `/app/domains` | authed | Sender authentication and DNS checker |
| `/app/suppressions` | authed | Blocked addresses |
| `/app/team`, `/app/billing` | authed | Roles, usage, plan |
| `/app/support` | authed | Ticket form with context attached |
| `status.` (separate) | public | Status and incidents |

Your original four items land like this:
- **Reference docs and quickstart** go in `/docs`.
- **Key management** is a dashboard feature at `/app/keys`, with a short docs page that links to it.
- **Sandbox** is two things. The test-mode toggle and test keys live in the dashboard, and the behavior (magic recipient addresses, simulated bounces) is documented in `/docs/guides`.

## Rules that make it feel like one product
1. **Every API error returns a `doc_url`** pointing to `/docs/errors/{code}`.
2. **Every dashboard failure state links to the same page.** Failed-send flow: dashboard log → error code → fix doc → support with message ID prefilled.
3. **Docs pages deep-link into the dashboard** ("Create a key" and "Add a domain" open the right screen).
4. **301-redirect every old docs URL** to its new path, to keep search ranking and existing links in customer code and READMEs.
5. **One navigation bar and one search** across docs and app.

## Suggested order across two quarters
1. **Q1, first half:** message log and detail, error code pages, `doc_url` in API errors. This removes most of the support load.
2. **Q1, second half:** move docs onto the root domain with redirects, and add the shared nav and search.
3. **Q2, first half:** webhooks UI and replay, domain auth checker, suppression list, support handoff with context.
4. **Q2, second half:** sandbox and test mode polish, key scopes, team roles, deliverability guides, `llms.txt`.

## Questions that change the plan
- Do you offer templates, SMTP, or inbound email? Each adds a section.
- How long do you retain message logs? That sets what the log UI can show and what support can answer.
- Is the dashboard a separate app from the docs stack? If it is, the shared-domain move needs a reverse proxy or a routing layer in front of both.