**Do not push this plan as written.** Ship `new_ticket` as a new REST hook step, `new_ticket_v2`, in 1.5.0. Leave the polling `new_ticket` code unchanged and hide it. Migrate in stages, not 100% at once.

First action tonight: run `zapier-platform pull`, then branch from 1.4.0.

## 1. Assumptions

- Public integration, CLI, 1.4.0 promoted, ~600 active users. Today is Fri 2026-10-23, so "tomorrow morning" is Saturday.
- Auth and your other steps stay untouched.
- Automatic migrations are on, and you have not opted out of the Integration Maintenance Program.
- Webhook scope and delivery:
  - A webhook sends the full ticket, in the list endpoint's shape, once per creation.
  - It fires for every creation path (email, API, import).
  - A subscription only receives events for the account that registered it.
  - Retries on non-2xx never double-send. Hook deliveries are not deduplicated, so a double-send becomes a duplicate Zap run.
- Tickets have a stable unique `id`.
- ⚠️ Open question: oldest-first with Zapier reading only page one should return the same 25 oldest tickets forever. Your list endpoint must filter somehow (open only? time window?). Check how, because "miss tickets" may have a second cause.
- The four templates are public and embedded in some launch posts or help articles. I don't know which.

## 2. Stage and route

Public, with live users. Route: Maintain step 4. Classify every change first, then clone, change, validate and diff, then promote.

## 3. Step table

| Key | Label | Type | Class | Reason |
| --- | --- | --- | --- | --- |
| `new_ticket` | New Ticket | polling | hide | Code unchanged, only `display.hidden: true`. Old Zaps keep running. |
| `new_ticket_v2` | New Ticket | REST hook | additive | New key, same label and description. New Zaps get it. |
| `new_ticket` sort flip | n/a | polling | rejected | Breaking in effect. Each live Zap's dedupe memory holds the old ids. |
| `new_ticket` page 25 to 200 | n/a | polling | rejected | Changes page contents, so the first poll fires every unseen ticket in every live Zap. Also over the 100 new items per poll cap†. |
| `new_ticket` polling to hook in place | n/a | n/a | rejected | Type switch is breaking. |
| All other steps | n/a | n/a | keep | Not touched. |

The rejected changes are the ones in your plan. Each would fire a burst of old tickets into 600 live Zaps. Those Zaps feed downstream actions such as Slack posts and task creation, so the burst cannot be undone. Bursts and errors also push Zaps toward the auto-off rule†.

## 4. Auth and trigger-type decisions

- **Auth: keep.** Any change is breaking, and nothing here needs one.
- **Trigger type: REST hook.** It rests on your webhooks endpoint:
  - It takes many callback URLs, one per Zap.
  - It deletes them individually, which `performUnsubscribe` needs.
  - Instant triggers ignore the user's plan polling interval†.
  - A helpdesk bursts past 100 new items per poll†, and the skill puts such triggers on a hook.
- Hook rules to meet:
  - `performList` must return the exact webhook payload shape (validation D006). Make it newest-first and short, since it only fills editor samples.
  - Send each event once.
  - Answer a `410` from Zapier by stopping delivery to that URL†.
  - Check intake limits against your worst Monday burst: 30 per second and 10,000 per 5 minutes†.

```js
new_ticket_v2: {
  key: 'new_ticket_v2', noun: 'Ticket',
  display: { label: 'New Ticket', description: 'Triggers when a new ticket is created.' },
  operation: {
    type: 'hook',
    performSubscribe: async (z, bundle) =>
      (await z.request({ method: 'POST', url: `${API}/webhooks`,
        body: { url: bundle.targetUrl, event: 'ticket.created' } })).data, // event name assumed
    performUnsubscribe: async (z, bundle) =>
      (await z.request({ method: 'DELETE',
        url: `${API}/webhooks/${bundle.subscribeData.id}` })).data,
    perform: (z, bundle) => [bundle.cleanedRequest],
    performList: async (z) =>
      (await z.request({ url: `${API}/tickets`, params: { sort: '-created_at', limit: 3 } })).data,
    sample, outputFields, // same keys as the old step
  },
},
```

## 5. Publish checklist

| Item | Owner role | Week |
| --- | --- | --- |
| `zapier-platform pull`, then build 1.5.0 with `nock` unit tests for subscribe, unsubscribe, perform and performList | Engineer | 1 |
| Private test: two Zaps on one account both receive events. Turn one off and confirm its webhook is deleted on your side. Delete a Zap and confirm no leaked subscription. | Engineer | 1 |
| One live Zap and one successful run on `new_ticket_v2` before promote. Zapier's publishing checks (S002, T001†) require this per visible step, and I'm not sure they apply to new steps on a public integration, so verify. | QA or support | 1 |
| `zapier-platform validate`, then diff by hand (see section 7) | Engineer | 1 |
| Canary, promote, staged migrate | Engineer | 1 |
| Rebuild the 4 templates on `new_ticket_v2`, then submit after promote (they must use the promoted version). Review takes ~2 weeks†. | DevRel or PM | 1 to 3 |
| Swap template embeds in posts and help articles | DevRel | 3 |
| Email and in-app notice to accounts with the integration connected, plus a support macro: "replace the trigger step with New Ticket (instant)". Zapier gives you no user list, so use your own API logs. | Support and PM | 1 to 2 |
| Mark 1.4.0 legacy only after most Zaps have swapped | Engineer | 4+ |

**Template decision for you:** hiding the old step invalidates the four templates, and the replacements need ~2 weeks of review†. Hide at promotion anyway. New Zaps stop landing on the buggy trigger, and you pay about two weeks without templates. If you can't accept that gap, delay the hide until the new templates are approved.

## 6. Growth actions, ranked

1. Relaunch the 4 templates on the instant trigger. Answer 3 (webhooks exist) moved this up.
2. Swap embeds in the launch post and help articles, which takes minutes once a template is public.
3. Support macro and in-app notice, so the 600 existing users move off the buggy step. Answer 5 (the deadline is this sprint, but Zapier gives you no user list) put this next.
4. The Workflow Element is out of scope here.

⚠️ This sprint does not fix Monday for existing Zaps. Zaps on the old step stay oldest-first at 25 per page until their owners swap the trigger by hand. Tell the customers who complained.

## 7. Versioning plan

- **Target version: 1.5.0, not 1.4.1.** Adding a trigger is a minor bump, and a patch label hides the intent. Push is sequential, with no skipped version.
- **Tonight:** `zapier-platform push` to private. Do not promote. Invite testers with `users:add`.
- **Canary:** `zapier-platform canary:create 1.4.0 1.5.0 -p 10 -d 3600`. That is 5 to 10% of traffic for 30 to 60 minutes†, non-breaking only. Stop if errors rise more than 5%†.
- **Promote** tomorrow morning if the canary is clean. Promotion itself moves a first group of users under automatic migrations.
- **Migrate:** `zapier-platform migrate 1.4.0 1.5.0 5`. Watch Monitoring, then raise it in steps to 100. Your `… 100` right after promote skips the watch step. The old step is unchanged, so the migration should be harmless, but a shared bug would hit all 600 at once.
- **Diff by hand.** Promotion does not catch changed perform behavior or output keys.
  - Check `git diff` on `triggers/new_ticket.js`. It should show only `hidden: true`.
  - Check shared `beforeRequest` and `afterResponse`. Changes there hit the old step too.
  - Check that the new step's output keys match the old ones.
- **Do not deprecate 1.4.0.** Nothing in it stops working.
- **Timing:** a Saturday promote has thin monitoring, and Monday morning is the real load test. Finish the staged migration before Monday and keep someone on call.

## 8. Metric baseline

- **Missed-ticket complaints:** unknown. Read your support tracker.
- **24h activation of `new_ticket`:** unknown. Read the Developer Platform analytics.
- **Active users:** ~600, which is Gold range (350 and up)† and well under Platinum (3,000)†. Confirm the quarterly count in the Partner Program page.
- **Share of users on the promoted version:** unknown. Read the Versions page.
- **Open bugs and feature requests, and median days to first response:** unknown. Read the Bugs & Feature Requests queue.
- **Templates live:** 4 now, 0 valid after the hide until the rebuilt ones are approved.
- **New metric:** Zaps on `new_ticket_v2` against Zaps still on `new_ticket`, from Monitoring.

† Zapier platform numbers. Verify them against Zapier's live docs before quoting them to stakeholders:
- 100 new items per poll
- instant triggers ignoring polling intervals
- hook intake of 30 per second and 10,000 per 5 minutes
- `410` handling
- canary 5 to 10% for 30 to 60 minutes, with the 5% error stop
- ~2-week template review
- the 95% error auto-off rule
- the Gold tier at 350 active users and Platinum at 3,000
- the S002 and T001 live-run checks

Next: run `zapier-platform pull`, then tell me what your list endpoint filters on, so we can settle the page-one question.