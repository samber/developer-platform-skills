**Next action:** don't rename any keys. Open Zapier Developer Platform → Monitoring and Zap history, and count live Zaps per step on 1.0.3. That count decides how much hiding and messaging you need (about 1 hour).

## 1. Assumptions

- Your request didn't give the keys for Create Customer and Delete Invoice. I assume they are acceptable, so check them.
- "Newest-first" sorts on `created_at`. An updated-trigger twin also needs `updated_at`.
- The API has a list endpoint for tax profiles, customer search by email, and an invoice status field. Confirm each.
- I don't know which jobs customers automate. Pull them from support tickets and exports (interview Q4).
- "Next quarter" means submitting by the end of Q1 2027. Engineering budget is unknown, so I assume about 10 days.
- Engineers will maintain this and you are the product owner.
- Delete Invoice has few or no live Zaps.

## 2. Stage and route

Private, 1.0.3, Platform UI, about 40 users, so it has live users. Route: classify every change first, then Design → Build → Publish.

- 1.0.3 is not editable. A version is editable only while private with fewer than 5 users†. Clone it to **1.1.0** (same major).
- Users never see keys. Renaming a key breaks every Zap that uses it. Keys stay as they are, and the new steps get proper keys.
- Fixing the sort order in place floods every live Zap with old invoices on the next poll. Each Zap's dedupe memory holds the old ids.
- The current trigger returns the 20 oldest updated invoices, and Zapier reads only page one. Existing Zaps on `trigger_1` may already miss new invoices. Check their Zap history.
- Hiding a step breaks nothing. Hidden steps keep serving existing Zaps. You have no Zap templates yet, so hiding forces no template rebuild.

## 3. Step table

| Key | Label | Type | Class | Reason |
|---|---|---|---|---|
| `trigger_1` | Updated invoice | polling | **hide** | Oldest-first sort and a generic "updated" event. Keep it serving existing Zaps. |
| `new_invoice` | New Invoice | polling | **additive** | Sort `-created_at`. Page size 100† (not 20). Id is the UUID. Never filter "already sent" server-side. |
| `new_paid_invoice` | New Paid Invoice | polling | **additive** (if status exists) | A specific state trigger beats a generic update. Mark it optional until support tickets show demand. |
| `updated_invoice` | Updated Invoice | polling | **additive, only if customers need it** | Use a composite id `uuid-updated_at` and keep the original id in another field. |
| `list_tax_profiles` | (hidden) | polling | **additive** | Feeds the tax-profile dropdown. Use `canPaginate`. |
| `search_2` | Get Invoice | search | **hide** | Same reason as `trigger_1`. |
| `find_invoice` | Find Invoice | search | **additive** | "Finds an invoice by number or customer email." Returns `[]` on a miss. |
| `find_customer` + `find_or_create_customer` | Find Customer / Find or Create Customer | search + search-or-create | **additive** | Standard accounting steps. They need a customer search endpoint. |
| `create_customer` (keep its current key) | Create Customer | create | **keep** + additive field change | Keep the same input key and output shape. Add a dynamic dropdown on the tax-profile field, backed by `list_tax_profiles`, plus a search so users can map values. |
| delete invoice (keep its key) | Delete Invoice | create | **keep** + additive copy field | Add an optional `copy` field: "Permanently deletes the invoice. This cannot be undone." |
| none | static webhook, in-place renames | none | **rejected** | Static webhooks aren't allowed in a public integration. In-place renames break Zaps. |

- **Titles and descriptions:** Title-case every label. Descriptions read "Triggers when…", "Creates a…", "Finds a…".
- **Tax-profile field:** If promotion blocks the dropdown as a field-type change, ship `create_customer_v2` beside the original and hide the old action. Diff the output keys by hand either way.
- **Delete Invoice:** Zapier's guidance is to avoid deletes. If usage shows no real customer job, hide it before submission. Every visible step needs a live Zap and a successful run.
- **Step count:** The visible set is 4–6 steps, within Zapier's guidance of 4–8 good steps over 20 thin ones.

## 4. Auth and trigger-type decisions

**Trigger type: polling only.**
- Instant triggers need a webhook subscription endpoint that can create and delete subscriptions per Zap. Your API has none.
- Don't flip existing triggers to instant or use a static webhook.
- Polling intervals follow the user's plan: Free 15 min, Professional 2 min, Team and Enterprise 1 min†.
- If you build a subscription endpoint later, add an instant twin under a new key (see `webhook-platform-design`).

**Auth: make the API key self-serve now. Decide on OAuth by week 2.**
- Users who must email support for a key block publication. Add a "Create API key" page in Tarnbrook settings. This is an additive change, and it also removes your support load.
- Your OAuth tokens (interview Q3) make OAuth v2 the preferred end state. Changing the auth scheme is breaking. It needs a new major, **2.0.0**, and the scheme can only be replaced in place with fewer than 5 users†.
- Zapier doesn't migrate users across majors. All 40 customers would reconnect and rebuild their Zaps by hand.
- **Recommendation:** ship 1.1.0 on the API key. In week 1, ask Zapier support whether it can do an assisted connection migration for a private integration, and decide by week 2.
  - If yes, go to 2.0.0 with OAuth before submission.
  - If no, publish on the self-serve API key and plan OAuth for later.
- Don't ship twins in 1.1.0 and then 2.0.0 weeks later. That makes customers rebuild their Zaps twice.
- If you go OAuth, return HTTP 401 on expired tokens, because Zapier refreshes on 401 only†.

## 5. Publish checklist

| Item | Owner | Week |
|---|---|---|
| Count live Zaps per step. Get the user list from the support key-request emails (Zapier gives you no list). | Product | 1 |
| Ask Zapier about assisted OAuth migration. Decide 1.x or 2.0.0. | Product | 1–2 |
| Build the self-serve API key page. | Engineering | 1–2 |
| Build 1.1.0 (twins, dropdown, delete warning, hidden steps). | Engineering | 2–4 |
| Share 1.1.0 with 3–5 friendly customers. Get one live Zap and one successful run per visible step (S002, T001)†. | Product | 4–5 |
| Check the 3-user live-Zap rule (S001)†. You already have far more than 3. | Product | 5 |
| Create the non-expiring test account with paid features for `integration-testing@zapier.com`. | Support | 5 |
| Confirm one admin with a company-domain email. Description 40–140 characters†, name "Tarnbrook". | Product | 5 |
| Clear every validation Error and Publishing Task. Read the Warnings. | Engineering | 6 |
| Draft 5–10 template titles and descriptions plus a help article per job. | Marketing | 6 |
| Submit from Integration Home. | Product | 7 |
| Answer reviewer rounds (about 1 week each)†. | Product + Engineering | 8–9 |

- Submission takes about a week for the first reply, and each fix round adds about another week†. Four weeks from submission to your date is the happy-path minimum.
- Templates exist only after approval and take about 2 weeks to review†. Work that backwards from your date.

## 6. Growth actions ranked

1. **5–10 Zap templates for the top jobs.** Submit them on approval day. No Paths, Code, Webhooks, Looping or Formatter steps†. Q4 (customer jobs) decides which ones.
2. **Template embed in the launch post and help articles.** Takes minutes once one template is public. An embed-sourced signup also ends beta the next business day†.
3. **Workflow Element on the integrations page.** Takes hours†. It needs a public template and a domain allowlist.
4. **Support macros and onboarding.** Replace "email us for a key" with a link to the self-serve key page. No gate, and Q1 moved it up.
5. **Silver benefits at 50 active users†.** You have about 40. Q5 (no hard date) lets this wait.

Skip the Workflow API marketplace. It needs weeks of engineering and an existing integrations directory with heavy search traffic.

## 7. Versioning plan

1. Clone 1.0.3 → **1.1.0**. Make the additive changes. Run validation.
2. Diff by hand what promotion does not catch: output keys of every kept step, response structure and perform behavior.
3. Platform UI has no canary. Share 1.1.0 with test accounts first. If you convert to the CLI, canary 5–10% for 30–60 minutes†.
4. Promote. Migrate 5% first and watch Monitoring. Then migrate the rest. Automatic migrations are on by default, so promotion itself moves a first group of users†.
5. Email the 40 customers: "Replace Updated invoice with New Invoice and Get Invoice with Find Invoice." Include screenshots and a deadline.
6. Mark 1.0.3 legacy after most Zaps move. Deprecate only if an endpoint will stop working.
7. A 2.0.0 for OAuth is a separate release. It stays out of 1.x because it is breaking.

**UI or CLI:** I recommend running `zapier-platform convert` to the CLI before the build. You get source control, mocked-HTTP tests and canaries. The move is effectively one-way, because converting back means a manual rebuild. If a non-engineer will maintain the integration, stay in the UI.

## 8. Metric baseline

| Metric | Value | Where to read |
|---|---|---|
| Users on 1.0.3 | about 40 (100%) | Developer Platform → Versions |
| Live Zaps per step | unknown | Zap history, Monitoring |
| Activation within 24 h per step | unknown | Monitoring |
| Quarterly active users vs the Silver bar of 50† | unknown | Partner Program page |
| Open bugs and feature requests, days to first response | unknown | Bugs & Feature Requests queue |
| Templates live | 0 | Developer Platform |

† These are Zapier platform numbers from the skill and its references. Verify them against Zapier's live docs before quoting them to stakeholders.