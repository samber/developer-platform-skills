# Brightfold on Zapier: what to do, in order

## 1. Assumptions

Each line is an interview answer I didn't have.

- **Today:** 2026-10-23. Approval was yesterday, 2026-10-22.
- **Beta window:** listed as Beta since 2026-10-22. The 90-day clock† ends about 2027-01-20, or the next business day after one signup from a Zapier embed.
- **Steps:** I don't know the 7 steps or whether they poll or use hooks. I assume a `New Deal` trigger and a few creates and searches.
- **Auth:** unknown. I assume it is unchanged and stays unchanged.
- **API webhooks:** unknown. This only matters if you add an instant trigger later.
- **Version state:** I assume the approved version is the promoted one. Confirm this before submitting templates, because they must use the promoted version†.
- **Engineering capacity:** only the 4-week hub estimate is known. I assume little other capacity.
- **Deadline:** none stated. I assume the goal is retained, activated users by the end of next quarter.

## 2. Stage and route

Beta, built on the Platform UI. Route: **Grow**, with **Maintain** running alongside. Design comes back in only for a step whose 24-hour activation lags the others.

Your sequence is mostly backwards. Templates are the highest-leverage lever and they are open to you today. The hub is the lowest-leverage lever, so it moves to the end.

## 3. Step table

| Key | Label | Type | Class | Reason |
| --- | --- | --- | --- | --- |
| all 7 existing | as shipped | as shipped | `keep` | Renaming or retyping a key breaks live Zaps. The review already passed them. |
| phone output field | e.g. `Phone (E.164)` | new output field on contact or deal steps | `additive` | Fixes phone cleanup in your integration instead of in a template Code step. The existing `phone` key stays untouched. |
| Code, Formatter or Paths helper steps | – | – | `rejected` | Templates can't use them†. They are also not integration steps. |

If the approved version already has 5 or more users†, clone it to the next minor (`1.0.x` → `1.1.0`) and add the field there. Otherwise add it in place.

## 4. Auth and trigger-type decisions

- **Auth:** keep the current scheme. Swapping it is a breaking change that would force a new major version.
- **Trigger type:** keep what you shipped. Don't flip polling to instant. If you want instant later, add a twin under a new key. That needs a webhook subscribe/unsubscribe endpoint, which is the unknown from the assumptions.
- **Polling contract:** confirm `New Deal` returns newest-first with a stable id. This is the most common cause of floods and misses.

## 5. Publish checklist

Approval already cleared the eligibility, validation and live-run gates. What remains is template work and keeping the integration approvable.

| Item | Owner | Week |
| --- | --- | --- |
| Confirm the approved version is promoted and the Beta listing is correct | Integration admin | This week (week 0) |
| Pick 5-10 compliant templates from the 20 drafts and rewrite titles and descriptions (see §6) | Product marketing | Week 0 |
| Submit the first templates (~2-week review†) | Integration admin | Week 0 |
| Add the E.164 phone output field, validate, diff by hand, promote | Engineer | Week 1-2 |
| Draft 1 help article per template job, embeds left blank until approval | Docs | Week 0-2 |
| Work the Bugs & Feature Requests queue; keep health score "healthy" | Support or engineer | Weekly |

## 6. Growth actions, ranked

| # | Action | Why now | Interview answer that moved it |
| --- | --- | --- | --- |
| 1 | **Submit 5-10 Zap templates this week.** Approval day is the right time, because every other surface embeds them. Review takes ~2 weeks†, so each day of delay pushes everything else back. | Gate is open: beta status is enough. | Stage = beta. |
| 2 | **Free surfaces, no gate:** mention Zapier in onboarding, support macros and the empty integration-search fallback. | Costs hours and needs no approval. It reaches users already inside the product, which the 300-visit page doesn't. | Traffic = ~300 visits/month. |
| 3 | **Embed the first public template** in the launch post and one help article per job. Takes minutes. | This is the fastest route to an embed signup. One signup ends Beta the next business day and can unlock the next tier's benefits early. | Deadline = Beta clock ends ~2027-01-20. |
| 4 | **Workflow Element in the product**, not only on `/integrations`. Hours of work†, needs a public template and a domain allowlist. | Replaces most of what the hub would do, at a fraction of the cost. | Engineering capacity is scarce. |
| 5 | **Phone cleanup in the integration** (§3). Then ship the phone-heavy templates once the field is promoted. | Templates can't contain Code, Formatter or Paths†, so the cleanup has to live in the product. | Template rules. |
| 6 | **Automation Hub on the Workflow API.** Defer, and reconsider around the January re-read. | See below. | Traffic and capacity. |
| 7 | **Revenue-share negotiation.** Drop it. | Zapier pays partners no revenue share. The return is retained, activated users. | – |

### Why the hub drops to #6

- It is a roughly 4-week engineering build against hours for the Workflow Element†.
- The playbook says to promote the Workflow API marketplace only when the product already runs an integrations directory with heavy search traffic. At ~300 visits a month you have a page, not a directory.
- Even a built hub would need public templates to show. Templates come first either way.
- Revisit it with data: the embed click-to-activation funnel and active-user count against the Silver threshold (50†). If Zapier must stay invisible in-product, that is an embedded-iPaaS decision for `connector-marketplace-strategy`, not this plan.

### Template fixes

**Draft limits.** Start with 5-10†, not 20. Several of the 20 use Paths and a Code step, so they would be rejected. Formatter, Webhooks and Looping are also banned†. Duplicate or narrow use cases are rejected too, and 20 variants of one HubSpot flow likely trip that. Keep the rest as a backlog and submit them after the first batch's feedback.

**The first title fails on several rules.** "Automatically sync your Brightfold deals to HubSpot" breaks these rules:
- "sync" and "automatic" are banned.
- "your" is second person.
- It doesn't start with an action verb.

Rewrite, assuming your trigger is `New Deal`:

```
Title: Create HubSpot deals from new deals in Brightfold

Description: Keep sales conversations in one place from the first deal.
When a deal is created in Brightfold, this workflow creates a matching
deal in HubSpot with the amount, stage and owner.
*Note: Map your Brightfold stages to HubSpot pipeline stages during setup.*
```

The description is unique to this template. It has no links and no Zap, trigger or action vocabulary. Pre-fill every required field, and add a filter only if the template is useless without it. Match the title verb to the real trigger: if the event is "updated", say "updated".

## 7. Versioning plan

- **Target:** current promoted version → next minor of the same major (e.g. `1.0.x` → `1.1.0`) with only the added phone field.
- **Canary:** UI integration, so share the cloned version with test accounts. Run a live Zap on the new field first.
- **Migration:** automatic migrations are on by default, so promotion itself moves a first group of users†. Test before promoting, then watch Monitoring and migrate the rest.
- **Diff by hand before promoting:** output keys unchanged, response structure unchanged, perform behavior unchanged. Promotion checks don't catch removed or renamed output keys or changed perform behavior†.
- **Templates:** they must use the promoted version. Deprecating a version marks its templates Invalid within 24 h†. If a later change hides a step, rebuild and resubmit the templates built on it.
- **Don't:** rename keys, change sort order or id format on a live polling trigger, or switch trigger types. Each one breaks live Zaps, floods them with old records, or both.

## 8. Metric baseline

| Metric | Value | Where to read it |
| --- | --- | --- |
| 24-hour Zap activation per step | unknown | Developer Platform analytics, per trigger and action |
| Active users this quarter | unknown | Developer Platform. Tier thresholds: Silver 50, Gold 350†. Re-evaluated each January, April, July and October. |
| Users on promoted version | unknown | Developer Platform versions page |
| Open bugs and feature requests, median days to first response | unknown | Bugs & Feature Requests queue |
| Templates live | 0 | Template dashboard |
| Embed click-to-activation funnel | unknown | Your analytics plus Zapier embed reporting |
| `/integrations` visits | ~300/month | Your site analytics |

## Net answer

1. Templates, this week: 5-10 compliant ones, with fixed titles and no Code, Paths or Formatter.
2. Free surfaces: onboarding, support macros and the empty-search fallback.
3. Embed the first public template in the launch post and help articles.
4. Workflow Element in the product.
5. The phone fix in the integration.
6. Hub: defer, and reassess with data.
7. Revenue share: cut it.

† Zapier platform numbers (template limits, review time, Beta length, tier thresholds, Workflow Element effort, version and migration rules). Verify against Zapier's live docs before quoting any of them to stakeholders.