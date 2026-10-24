# Silverthread × Zapier integration design

**38 endpoints do not become 38 steps. Ship 7 core steps and 2 conditional ones.** The invoice trigger should be a REST hook, which needs engineering to change the webhooks API. A polling trigger would silently lose invoices for your largest agencies. Zapier will not accept "Charge Card" at all.

Zapier numbers are marked †. Check them against Zapier's live docs before you quote them. See the footnote at the end.

## 1. Assumptions

I couldn't ask questions, so each missing answer is stated here. Correct any that are wrong, because they move the design.

- **Stage:** no integration exists, and you've chosen the CLI. Nothing is live, so nothing is a breaking change yet and the step keys are free to choose. They freeze at first promotion.
- **Mobile OAuth server:** it supports the authorization-code grant, refresh tokens, and registering a second client with Zapier's redirect URI. If it is implicit-flow only, the auth decision changes.
- **Invoices:** they have a status or paid field, a human-readable number, and a link to the record.
- **List endpoints:** they accept a page-size parameter, or one can be added. Today's documented size is 20 per page.
- **Payments:** I don't know whether a payments endpoint exists, so the two payment steps are conditional.
- **Which jobs customers automate:** unknown. The step list follows Zapier's Accounting category examples, not your support tickets. Check it against your tickets and CSV-export requests before you freeze the keys.
- **Deadline and engineering days:** unknown. The plan below includes a fallback if the webhook work can't land before launch.

## 2. Stage and route

No integration yet, so the route is **Design → Build → Publish**, then Grow. There are no live Zaps, so the only discipline needed now is to choose keys and output shapes carefully. Renaming a key, changing the sort order, or flipping polling to hook later all break live Zaps.

## 3. Step table

Of the 38 endpoints, 9 map to visible steps, 2 to hidden helper triggers, and 27 are not built in v1.

| Key | Label | Type | Class | Reason |
| --- | --- | --- | --- | --- |
| `new_invoice` | New Invoice | Trigger, REST hook (Instant) | additive | Core event on your core object. See section 4 for why it can't be polling. |
| `new_customer` | New Customer | Trigger, polling, newest-first | additive | Customer volume is low enough for polling. It uses `?sort=-created_at`, UUID as id. |
| `new_payment` | New Payment | Trigger, hook or polling | additive, **conditional** | Zapier's Accounting list leads with it. Needs a payments endpoint. |
| `create_customer` | Create Customer | Action | additive | Required fields mirror the API exactly. Account custom fields come in as dynamic fields. |
| `update_customer` | Update Customer | Action | additive | Half of the old "Create or Update Customer". It is a separate action, not the experimental `update` option of search-or-create. |
| `find_customer` | Find Customer | Search, plus `find_customer` search-or-create | additive | The other half of the old "Create or Update Customer". Returns `[]` on no match. |
| `create_invoice` | Create Invoice | Action | additive | Line items use `children`. Customer comes from a dropdown, never a typed UUID. |
| `find_invoice` | Find Invoice | Search | additive | Replaces "Get Invoice". Zapier users search by number or customer, they don't paste UUIDs. |
| `record_payment` | Record Payment | Action | additive, **conditional** | Records a payment already collected. Confirm with Zapier partner support before building (see Charge Card below). |
| `list_customers`, `list_invoices` | (hidden) | Hidden polling triggers, `canPaginate`, `sort=-created_at` | additive | Power the dynamic dropdowns and cover the "no id typing" rule. |
| 'Delete Invoice' | | | **rejected** | Irreversible and absent from Zapier's recommended accounting steps. If support tickets later prove demand, add it with a `copy` field warning that it can't be undone. |
| 'Charge Card' | | | **rejected** | Zapier's publishing rules ban payment processing and asset transfers†. A step that runs the saved card would block publication or get you delisted. |
| 'Get Invoice' | | | **rejected** | Folded into Find Invoice. |
| 'Create or Update Customer' | | | **rejected** as one step | Split into Find Customer + Create Customer + Update Customer. |
| Webhooks endpoint | | | **rejected** as a step | Used internally by the hook trigger, never exposed. |
| Remaining ~27 endpoints | | | **rejected** for v1 | Add them one at a time when tickets prove a job. Four to eight good steps beat 38 thin ones. |

**Decisions to fix now because they become contracts:**

- **Dates:** every output date is ISO 8601 with offset, converted from epoch seconds. Keep the raw epoch in a separate `*_epoch` field if you want it. Date inputs are `datetime` fields that you convert back to epoch in code.
- **Ids:** use the UUID as `id`. It is stable, so it is safe for deduplication.
- **Output shape:** include `id`, a human name or number, a link to the record, and split names and addresses.
- **Samples:** one realistic record with only keys every account returns. Custom fields go in as dynamic output fields, not in the sample.
- **Errors:** never return 200 on a failure. A user-fixable failure is a normal error that names the field, under 250 characters†. An unmet precondition raises a halted error. A 429 surfaces with `Retry-After`. During a known outage, throw a throttled error.

## 4. Auth and trigger-type decisions

**Auth: OAuth v2.**

- Basis: you already issue OAuth tokens for the mobile app, and Zapier prefers OAuth v2†.
- Register a dedicated client for Zapier. Don't reuse the mobile client.
- Return HTTP 401 on expired tokens. Zapier refreshes on 401 only†.
- Set `refreshAccessToken` and `autoRefresh: true`. Keep the client id and secret in per-version environment variables.
- Use a cheap "who am I" call as `authentication.test`.
- Verify the assumption in section 1 first. Changing the auth scheme after launch means a new major version†.

**Invoice trigger: REST hook, which requires engineering work.**

- **Today's webhook limits:** the endpoint allows exactly one callback URL per account. A REST hook needs a separate subscription per Zap that can all be alive at once, plus delete on turn-off. A single URL can't do this.
- **Static webhook is out:** it isn't allowed in a public integration†.
- **Why polling fails on invoices:** your largest agencies create about 900 invoices in the hour after month-end close.
  - Zapier reads only page one of a poll and never page two.
  - At 20 per page, any burst above 20 between polls loses items silently.
  - Even at a page size of 100, the default per-poll cap is 100 new items†. The free-plan interval of 15 minutes† means about 225 invoices at the average rate, and the peak is worse.
  - The loss is silent, and it hits your biggest customers.
- **What the hook needs from engineering:**
  1. Multiple concurrent webhook subscriptions per account, with create and delete. Design these with `webhook-platform-design`.
  2. A `performList` that returns the exact webhook payload schema.
  3. Each event sent exactly once, because hook deliveries aren't deduplicated†.
  4. A 410 response handling path: when Zapier answers 410, stop sending†.
- **Fallback if the webhook work misses launch:** ship `new_invoice` as polling with `sort=-created_at`, the largest page size you can add, and a help note about burst limits. Then add an instant twin under a **new key** (`new_invoice_instant`) and hide the polling one. You cannot flip an existing trigger's type, because that is breaking. Prefer building the hook first, because the twin costs you a template rebuild and a user-facing migration.
- **Customers and dropdowns:** polling with `-created_at` is fine, since volumes are low.
- **`updated_since`:** don't use it to filter already-sent items server-side. Zapier dedupes by id per Zap. Keep it for a later specific state trigger such as `New Paid Invoice`, if the invoice status supports it. If you ever build a generic "Updated Invoice", its id must be composite (`id-updated_at`), with the original id in another field.
- **Default sort:** the API is oldest-first. Every polling call must pass `?sort=-created_at`, and the dropdown triggers too.

## 5. Publish checklist

Count backwards from your date. Four weeks† between submission and launch is the happy-path minimum, and the user-recruitment step comes first.

| Item | Owner role | Week |
| --- | --- | --- |
| Confirm OAuth assumptions; register Zapier client and redirect URI | Backend engineer | 1 |
| Webhook subscription API (multi-subscribe, delete, 410 handling) | Backend engineer | 1-3 |
| Raise list page size; add `sort=-created_at` everywhere used | Backend engineer | 1 |
| Scaffold, `register`, auth, steps, fields, samples, unit tests with nock, `validate` | Integration engineer | 2-4 |
| Recruit 3+ design-partner agencies with live Zaps; include one large agency to exercise the burst | Product lead | 2-5 |
| One live Zap and one successful run per visible step (9 steps = 9 Zaps), in the admins' Zap history | Integration engineer + design partners | 4-5 |
| Non-expiring test account with paid features for `integration-testing@zapier.com` | Support lead | 3 |
| Admin with a company-domain email; name equals brand; description 40-140 chars† opening "Silverthread is a…", no marketing claims; logo; homepage | Product lead | 4 |
| Clear every validation Error and Publishing Task | Integration engineer | 5 |
| Confirm `record_payment` and any payment-adjacent step with Zapier partner support | Product lead | 2 |
| Submit; reviewer replies about a week†, each fix round adds about another week | Product lead | 5-7 |
| Approval → Beta; submit 5-10 templates the same day (about two-week review†) | Product / marketing | 7-9 |

## 6. Growth actions, ranked

1. **5-10 Zap templates for the top jobs.** This is the highest return and needs beta or public status. Example jobs, to be confirmed by tickets: new invoice → Slack message, new customer → CRM contact, new payment → bookkeeping row. No Paths, Code, Webhooks, Looping or Formatter steps†. *Moved by:* unknown jobs, so confirm the list against support tickets.
2. **Embed one public template in the launch post and one help article per job.** It takes minutes. One embed-sourced signup ends Beta the next business day†. *Moved by:* the deadline, since this is the fastest route to exit Beta.
3. **Workflow Element on your integrations page.** It takes hours and needs a public template and a domain allowlist.
4. **Zapier in onboarding, support macros and empty integration search.** No gate.
5. **Partner Program spotlight benefits.** These start at Silver, which needs 50 active users†.
6. **Custom marketplace on the Workflow API.** Skip it unless you already run an integrations directory with heavy search traffic.

## 7. Versioning plan

- **Target:** `1.0.0`, private first. Share by invite link with the design partners. Pin `zapier-platform-core` exactly.
- **Frozen contract:** step keys, input and output keys, output shape, ISO date format, polling sort order, and the trigger type per key. Document them in the repo.
- **Pin the Silverthread API version** the integration calls. If the API changes shape later, map it back to the old output in perform code.
- **After first promotion:**
  - Clone, change, `validate`, and share with test accounts.
  - Canary 5-10% for 30-60 minutes†, non-breaking changes only.
  - Promote, then `migrate` 5% first and watch Monitoring.
  - Automatic migrations are on by default, so promotion itself moves a first group of users.
- **Diff by hand before every promotion:** removed or renamed output keys, changed response structure, and changed perform behavior. Promotion checks don't catch these†.
- **Breaking changes** go additive (new key, hide the old step) or into a new major. Users can't be migrated across majors†.
- **Integration Maintenance Program:** Zapier engineers may edit your versions. Run `zapier-platform pull` before every push or promote†.

## 8. Metric baseline

All values start as **unknown**. Read them in the Zapier Developer Platform once the integration is in beta.

- **24-hour activation per step:** compare steps against each other. A low step is a design defect, so test it in the editor yourself.
- **Quarterly active users** against the Silver threshold of 50†, re-evaluated each January, April, July and October†.
- **Open bugs and feature requests,** and median days to first response. This is the health score input. Keep users affected by open bugs under 10% of monthly actives†.
- **Run errors:** a Zap that errors on 95% of more than 20 runs over 7 days turns off†.
- **Templates live,** and the embed click-to-activation funnel.
- **Silverthread-side:** invoice-hook delivery count against invoices created, for the large agencies. It should be 1:1.

## Open questions for you

1. Can engineering deliver multi-subscription webhooks before launch? If not, I'll write the polling-first fallback plan.
2. Does a payments endpoint exist?
3. Does the mobile OAuth server support the authorization-code grant with refresh tokens?
4. What do your support tickets and exports say customers automate today?

---

† Zapier platform numbers come from the playbook's reference files, not from live docs. Verify each against docs.zapier.com before quoting it to a stakeholder. The affected numbers are the polling and dedupe limits (100 new items per poll, only page one read, 15-minute free interval), the 250-character error cap, the 5/3-user and Partner Program thresholds, the 95%/20-run auto-off rule, the review timings, and the canary percentages.