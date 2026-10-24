**Next action, today:** email Zapier partner support with the four questions in Week 1 below. Their answers decide the plan.

Dec 4 is 42 days away, which is six weeks, not five. The extra week is useful, but the plan still has almost no slack.

## 1. Assumptions

- Auth type, polling versus hook triggers, and the exact step keys are unknown. I assumed a self-serve API key or OAuth, polling triggers, and unique ids. Check each against the API before Week 1 ends.
- I assumed Fennwick has an API and that the team owns it.
- I assumed 3 invited customers will run real Zaps. Zapier's "3 users with a live Zap"† rule is from the skill's references. Nobody outside the team has used the integration, so confirm what Zapier counts as a user.
- I assumed Fennwick has no Zapier category of its own. Contract management sits closest to Contact management or Accounting.
- Engineering days are unknown. I assumed about 5 days in total.

## 2. Stage and route

- **Stage:** private, CLI-built, 0 external users.
- **Route:** Design audit, then Build fixes, then Publish, then Grow.

**Blockers.** Six items would fail submission or review as things stand:

1. **Name.** "Fennwick for Zapier" is not allowed. Zapier's rule† is that the name equals the brand, with no "Zapier", "app" or "integration". Name it **Fennwick**. Your announcement copy can say "Fennwick on Zapier".
2. **Invite-only product.** Publishing requires a publicly launched product†. This is the biggest risk. A listing can be rejected until the product is public.
3. **Test account.** A 14-day trial expires. Zapier needs a non-expiring account with paid features†.
4. **Admin email.** The admin needs a company-domain email†. A personal Gmail fails check M001-M006†.
5. **Send Payment Link.** Payment processing and asset transfer are banned†. The skill says to confirm payment links with partner support before building. It also risks the unsolicited-messaging ban†. Hide it for the first submission.
6. **Live-Zap evidence.** Submission needs at least 3 users with live Zaps†, one live Zap per visible step†, and one successful run per visible step†. You have none yet.

## 3. Step table

I don't know your keys, so each row is by role.

| Step | Type | Class | Reason |
| --- | --- | --- | --- |
| 3 triggers | polling (assumed) | keep, audit | Confirm newest-first order, a stable unique id, and 100 or more items per page. Use specific triggers such as "New Signed Contract", not a generic "Updated Contract". |
| 2 actions | create | keep, audit | Check required fields against the API and use dynamic dropdowns instead of typed ids. |
| Send Payment Link | create | **hide** | Payment ban†, and it needs a live-Zap run you can't safely exercise. Hiding is free now because no Zap uses it. Unhide later in an additive version once partner support approves. |
| 1 search | search | keep | A miss returns `[]`. Feeds dropdowns and search-or-create. |

**Audit keys now.** Renaming a key breaks Zaps once users run it. A version is editable only while private with fewer than 5 users†. Fix keys, labels, sample data and field types this week, before the first recruit builds a Zap. Stay under 5 users until the audit is done.

**Visible steps drop from 7 to 6.** That means 6 live Zaps and 6 successful runs to produce.

## 4. Auth and trigger-type decisions

- **Auth.** OAuth v2 if Fennwick already issues OAuth tokens, otherwise a self-serve API key. A key that users must request by email blocks publication.
  - Invite-only means a key must be creatable from the account settings of the invited users.
  - Return 401 on expired tokens, because Zapier refreshes on 401 only.
- **Triggers.** Keep polling unless the API can create and delete a webhook subscription per Zap and keep several alive.
  - If a trigger routinely exceeds 100 new items per poll, put it on a hook.
  - Never ship a static webhook.
- **Errors.** Never return 200 on failure. Keep messages under 250 characters†. Use halted errors for duplicates.

## 5. Publish checklist and week-by-week plan

Today is Fri Oct 23.

### Week 1: Oct 23 to Oct 30. Unblock.

| Item | Owner | Day |
| --- | --- | --- |
| Email Zapier partner support: (a) can an invite-only product submit, (b) is Send Payment Link allowed, (c) who counts as a user, (d) the naming rule | Founder | Day 1 |
| Decide: open signups before Nov 6 if Zapier says "public launch required" | Founder | by Oct 30 |
| Rename the integration to "Fennwick". Write a 40-140 character† description opening "Fennwick is a…" | Engineer | Day 2 |
| Replace the Gmail admin with a company-domain admin (employee or contractor). Make that person Technical Contact. Keep the Gmail user as co-developer | Founder | Day 2 |
| Create a permanent paid test account for `integration-testing@zapier.com`† | Founder | Day 2 |
| Hide Send Payment Link | Engineer | Day 2 |
| Run the key and field audit (section 3). Run `zapier-platform validate`. Clear every Error and Publishing Task | Engineer | Day 3 to 4 |
| Pick 3 or more design partners from the invite list. Send them private invite links (`users:add`/`users:links`) | Founder | Day 3 |
| Add Fennwick's own test cases for every error path (401, 429, not found) | Engineer | Day 5 |

Gate on Oct 30: partner support has answered, and the product-public decision is made.

### Week 2: Oct 30 to Nov 6. Produce evidence, then submit.

| Item | Owner | Day |
| --- | --- | --- |
| Each partner builds live Zaps. Every visible step needs one live Zap and one successful run† | Partners, CS lead | Oct 30 to Nov 3 |
| Check the Zap history of the admin account for 6 successful runs | Engineer | Nov 3 |
| Fix bugs partners report. Do not rename keys | Engineer | Nov 3 to 5 |
| **Submit from Integration Home** | Admin | **Target Nov 3, hard cut Nov 6** |

A reviewer replies in about a week†. Each fix round adds about another week†. Four weeks between submission and the date is the happy-path minimum†. A Nov 6 submission uses all of it.

### Week 3: Nov 6 to Nov 13. Review runs. Prepare everything that needs no approval.

| Item | Owner |
| --- | --- |
| Answer reviewer items within 24 hours | Engineer |
| Draft 5 to 6 Zap template titles and descriptions to Zapier's rules (`references/templates.md`) | Marketing |
| Write one help-centre article per template job | Marketing |
| Draft the announcement with a placeholder for the template embed | Marketing |
| Prepare the domain allowlist and Workflow Element placement on the integrations page | Engineer |
| Seed an empty-search fallback and a support macro that mentions Zapier | Support |

### Week 4: Nov 13 to Nov 20. Approval, then templates.

| Item | Owner |
| --- | --- |
| Approval lists you as Beta. Beta ends after 90 days or one embed signup† | Zapier |
| **Submit templates the same day as approval.** They need the promoted version† | Marketing |
| Template rules†: no Paths, Code, Webhooks, Looping or Formatter steps. No hard-coded values. English only. No "sync" or "automatic" | Marketing |
| Reserve one template slot per core job. Templates must not use Send Payment Link | Marketing |

**Gate on Nov 13:** not approved yet. Switch to Plan B copy (below).

### Week 5: Nov 20 to Nov 27. Template review.

Template review takes about two weeks†. Public templates land about Nov 27 on the happy path.

| Item | Owner |
| --- | --- |
| Fix any template rejection the same day | Marketing |
| Embed the first public template in the launch post and each help article | Marketing |
| Add the Workflow Element once a template is public | Engineer |

**Gate on Nov 27:** no public template yet. Ship the announcement with the directory link and "templates coming".

### Week 6: Nov 27 to Dec 4. Freeze and ship.

| Item | Owner |
| --- | --- |
| Run an end-to-end smoke test as a new user: find Fennwick in the directory, connect, run each template | Founder |
| No integration changes after Dec 1 | Engineer |
| Publish the announcement Dec 4 | Marketing |

### What you may claim

- Approved and Beta in the directory: "Available on Zapier" is true. Say "in beta" in small print.
- Submitted but not approved: write "Zapier integration coming soon". Do not claim availability.
- Templates not public: do not say "ready-made Zaps".

## 6. Growth actions ranked

| Rank | Action | Moved by |
| --- | --- | --- |
| 1 | 5 to 6 Zap templates, submitted on approval day† | Deadline (answer 5) |
| 2 | One template embedded in the launch post. One embed signup ends Beta the next business day† | Deadline (answer 5) |
| 3 | A help article per job, each with an embed | Customer jobs |
| 4 | Workflow Element on the integrations page | Needs a public template |
| 5 | Onboarding, support macros, empty-search fallback (no gate) | Low effort |

Skipped: newsletter spotlight (Silver needs 50 active users†) and a custom marketplace on the Workflow API (weeks of work).

## 7. Versioning plan

- **First version.** Submit 1.0.0. No users means no breaking-change risk yet.
- **After submission.** The version is Pending. Fix reviewer items on a clone, for example 1.0.1. Do not rename keys once 5 users exist.
- **Unhiding Send Payment Link.** Do it later in 1.1.0 as an additive clone. Hiding and unhiding invalidates templates built on it, so keep it out of every template.
- **Canary.** Not useful before launch (0 users). After launch, canary 5 to 10% for 30 to 60 minutes† on any change.
- **Hand diff before each promotion.** Diff output keys, response structure and perform behaviour. Promotion does not block those changes.

## 8. Metric baseline

| Metric | Value | Where to read |
| --- | --- | --- |
| Active users this quarter | 0 | Developer Platform, Partner Program page |
| 24-hour Zap activation per step | unknown | Developer Platform analytics |
| Open bugs and feature requests | unknown | Bugs & Feature Requests queue |
| Median days to first response | unknown | same queue |
| Templates live | 0 | Developer Platform, Zap Templates |
| Embed click-to-activation funnel | unknown | Embed analytics, after the first embed |

† Zapier platform numbers and rules, from the skill and its references. Check each against Zapier's live docs (`docs.zapier.com`) before you quote it.

**Next:** send the partner-support email today. If you want, I can draft it now.