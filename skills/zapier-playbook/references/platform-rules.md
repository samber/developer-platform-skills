# Zapier platform rules and numbers

Zapier changes these numbers. Before quoting one to a stakeholder, check the page named beside it on docs.zapier.com; the site's `llms.txt` index lists every page and each page has a `.md` version.

## Contents

- Recommended steps by category
- Auth schemes
- Runtime limits
- Publishing eligibility
- Validation checks that block publishing
- Stages
- Partner Program
- Run-error rules

## Recommended steps by category

Source: integrations/quickstart/recommended-triggers-and-actions (about 40 categories; read the one matching the app).

| Category | Triggers | Actions | Searches / search-or-create |
| --- | --- | --- | --- |
| Accounting | New Payment, New Invoice/Bill, New Expense, New Customer, New Quote/Estimate | Create Customer, Create Invoice/Bill, Send Invoice, Create Payment/Sales Receipt | Find Invoice, Find Customer; Find or Create Customer |
| Contact management | New Contact/Lead/Company, New Form Submission | Create Contact, Add Contact to Group/Tag/List, Update Contact | Find Contact; Find or Create Contact |
| Customer support | New Ticket, New Customer, New Message, New Closed Conversation, Tag Added | Create/Update Ticket, Add Comment/Note, Send Message, Create Customer | Find Customer, Find Ticket; Find or Create Customer |

## Auth schemes

Source: integrations/build/auth.

- OAuth v2 (preferred), API Key (next; keys must be self-serve), Session, Basic (least appropriate), Digest. Custom schemes need the CLI.
- The scheme can be replaced only on an unpromoted version with fewer than 5 active users. Otherwise clone a new major; ask Zapier first, since it can sometimes migrate connected accounts between schemes for public integrations.
- Zapier refreshes OAuth v2 and session credentials on HTTP 401 only. Throw the refresh-auth error in code if the API signals expiry another way.
- Credentials are collected only in the auth configuration, never in a step's fields, and never hardcoded.

## Runtime limits

Source: integrations/build/operating-constraints, integration-build-guidelines.

| Limit | Value |
| --- | --- |
| Poll, hook processing, action, search, editor test | 30 s each, requests plus code |
| Polling interval | by the user's plan: Free 15 min, Professional 2, Team and Enterprise 1; Instant triggers ignore plan |
| New items per poll | 100 by default after dedupe; more holds runs and emails the user; only page one is read |
| Deduplication memory | 105,000 ids per Zap, cleared when the Zap turns off |
| REST hook intake | 10,000 per 5 minutes, 30 per second |
| Payloads | webhook 10 MB; action input 6 MB (35 MB on platform v17.2.0+); response 20 MB; files about 120 MB |
| Unsubscribed hook | Zapier answers 410: stop sending; `DELETE <targetUrl>` unsubscribes from your side and pauses that user's Zap |
| Hook deliveries | not deduplicated: never send one event twice |
| Error message | truncated at 250 characters |
| Editable versions | private with fewer than 5 users; otherwise clone |

## Publishing eligibility

Source: integrations/publish/integration-publishing-requirements.

- You own the API or hold the owner's written permission; you hold the trademarks.
- Name equals the brand, no "Zapier", "app", "integration" or TM. Description opens "<Name> is a…", functional, no marketing claims. Homepage is the marketing site.
- The product is publicly launched, not invite-only; its API is documented.
- HTTPS everywhere, production endpoints only, English user-facing text.
- One public integration per app; duplicate or replacement integrations stay private.
- Description 40-140 characters.
- Test account for `integration-testing@zapier.com`: non-expiring, paid features on.
- One admin whose email domain matches the app's domain, employee or contractor.
- Banned: financial transactions, asset transfer, payment processing; spam or unsolicited messaging; steps that name or target a specific third-party site, or user-facing "scraping" wording (generic data-pull steps are allowed).
- Banned publishers: companies Zapier deems competitors, and apps from US-sanctioned countries.

## Validation checks that block publishing

Source: integrations/publish/integration-checks-reference. Errors and Publishing Tasks block; Warnings don't.

| Code | Rule |
| --- | --- |
| S001 | At least 3 users with a live Zap (on, recent successful run) |
| S002 | One live Zap per visible trigger, action and search |
| T001 | One successful run per visible step, in the admins' Zap history |
| D006 | REST hook trigger needs a perform list (polling URL) |
| D017 | Static webhook discouraged; not allowed public |
| D004 | Id fields should have dynamic dropdowns |
| D010, D012, D024 | Static sample present, contains the primary key, matches output fields |
| T002, T004-T006 | Live results contain the primary key and a superset of the sample's keys |
| M001-M006 | Category, description, logo, admin role and domain, homepage |
| C001-C004 | On promotion: avoid removing steps, fields, samples; incompatible `json` field schema blocked within a major |
| S003 | At most 100 production versions with live Zaps |

## Stages

Source: integrations/publish/public-integration.

1. Private: share by invite link; any number of users.
2. Submitted: version Pending; reviewer reply within about a week.
3. Beta: listed with a Beta tag for 90 days, or until the next business day after one embed-sourced signup.
4. Public: Beta tag removed, enrolled in the Partner Program.

Zap templates and the Workflow Element need beta or public status; templates must use the promoted version.

Templates: 5-10 to start; no Paths, Code, Webhooks, Looping or Formatter steps; rejected for duplicate or narrow use cases, hard-coded values, non-English copy. Deprecating a version marks its templates Invalid within 24 h. Workflow Element: Zapier estimates hours to implement, against weeks for the Workflow API.

## Partner Program

Source: integrations/publish/partner-program, benefits-guide.

| Tier | Active users this quarter | Notable benefits |
| --- | --- | --- |
| Bronze | any public integration | partner support, free Partner Sandbox workspace |
| Silver | 50 | "Learn More" lead button with UTMs, one featured week per year, newsletter spotlight once a year, "Best of" blog flyover, monthly Community post of new steps and resolved issues |
| Gold | 350 | Silver benefits |
| Platinum | 3,000, or 350 with 20% quarter-on-quarter growth | priority Solutions Engineer support, 1:1 advocacy session, priority in Zapier-led co-marketing |

- Re-evaluated at the start of January, April, July and October; a dip at quarter start is normal because the count accumulates.
- Every tier needs a "healthy" health score: open bugs and feature requests, weighted by votes, and your responsiveness to them.
- Embed fast-track: with an embed-sourced signup and a healthy score, next-tier benefits unlock at 40, 300 or 2,500 active users.

## Run-error rules

Source: help.zapier.com troubleshooting articles; integration-build-guidelines.

- A Zap whose runs error 95% of the time over 7 days, with more than 20 runs, turns off (24 h grace on Team, 72 h on Enterprise plans).
- No public page states an integration-level error rate that triggers delisting. Removal grounds documented: banned categories, Platform Agreement breaches, gaming review, faked users.
- Halted errors never count toward it. Expired-auth errors turn the Zap off, email the user, and hold runs for replay after reconnecting.
