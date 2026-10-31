# Pollen HR: legacy-scope sunset (2027-03-01), email and send plan

**Recommendation: don't send the blast to all 3,000 accounts.** Send a targeted notice to the apps that actually hold or use `people.read.all` and the other legacy scopes. Also fix how you reach the 38% whose address bounced. A second email to the same bouncing addresses fails the same way, whatever the subject line says.

**Next action:** run the census query below. The first send is planned for Tue 2026-11-03 and depends on that query.

## 1. Why not the blast (for your manager)

- **It mails people who never touched a legacy scope.** About 3,000 accounts across 400 apps is roughly 7 accounts per app. Most of them have nothing to migrate. Mailing them trains the affected few to ignore the next notice.
- **It doesn't reach the people you missed.** The 38% bounced because the owner address is dead. A louder subject line to the same address changes nothing.
- **It misses the plugin shape.** For WordPress-style plugins, the developer shipping a fix is not the end. Each agency-installed site upgrades on its own schedule, and those site owners never signed up with you.
- **A stronger subject line comes from specifics, not volume.** The subject carries the app name and the date (see §3). Avoid "URGENT" and all-caps, which spam filters penalize.
- **Safe middle ground for the broad audience:** a changelog post, a developer-dashboard banner and a docs-page notice reach everyone without email. `api-versioning-policy` owns those, and they reach no specific owner.

Time left: **122 days** (2026-10-30 to 2027-03-01). That fits a monthly cadence with room for brownouts.

## 2. Assumptions to confirm

1. "Emailed in November" means November 2025. If the first email was this coming November, say so, because the plan changes.
2. "38% bounced" means 38% of the 400 apps (about 152). Silence from the other 62% still counts as unverified, not as contact.
3. The gateway logs OAuth client ID and granted scope per request. If it doesn't, that logging gap is the first fix. On an authenticated surface, unattributed calls must be zero.
4. The replacement scopes are stable and cover the migrating use cases. If not, brownouts and escalation are off the table until they do (see §5).
5. Break date is **2027-03-01 00:00 UTC**.

## 3. The email

Send one email per app, to every contact on file. Fill the merge fields from the census. Never send it to an app with no legacy-scope grants or calls.

**Subject:**
`[Action needed before 2027-03-01] {{app_name}} will lose access to {{legacy_scope_list}}`

**Body:**

```
Hi {{first_name_or_"team"}},

Your Pollen HR marketplace app {{app_name}} (client ID {{client_id_prefix}}...) still
uses legacy OAuth scopes that we remove on 2027-03-01 00:00 UTC.

What we see
- Scopes: {{legacy_scopes}}  (granted to {{n_installs}} customer installs)
- Calls using them: {{call_count}} in the last {{lookback_months}} months
- Last seen: {{last_seen_utc}}
- Sample request you can look up: {{sample_request_id}}

What happens on 2027-03-01
{{failure_behavior}}   <- e.g. token requests for these scopes fail with <error code>,
                         and existing tokens holding them stop authorizing calls.
Your customers' syncs stop; no data is lost on our side.

What to do
- Replace {{legacy_scope}} with {{replacement_scope}} (full mapping: {{scope_map_link}}).
- Migration guide: {{guide_link}}
- Questions: {{named_engineer_or_alias}}

Please reply to this email with ONE of:
1. "Confirmed - I maintain this app" plus the date you expect to ship the change.
2. The name and email of whoever maintains it now.
3. "Not mine" if this is not your app, or "Disputed" if the call counts look wrong
   (shared tokens happen; we will correct our records).

We removed these scopes from new app registrations on {{notice_day}}, so new apps start
on the replacement. Existing installs keep working until 2027-03-01.

If we hear nothing, we will contact your account's other developers, your commercial
contact and, for installed apps, your customers' admins.

{{sender_name}}, Partner team, Pollen HR
```

**Bounce-recovery variant.** Same body, with this opening line and the same fields:

```
Subject: [Action needed before 2027-03-01] Who maintains {{app_name}}? Legacy scopes end 2027-03-01
We could not reach the owner address for {{app_name}} ({{old_address}}). You are listed as
{{role}} on this app. Please confirm you maintain it or name who does.
```

Send it to everyone else on the app's developer team and the commercial owner. This is where the 3,000 accounts become useful: they are the alternate contacts for the roughly 152 bounced apps, not a mailing list.

**Customer-admin notice** (for plugin and agency installs, and any app that stays silent):

```
Subject: An app in your Pollen HR account will stop syncing people data on 2027-03-01

{{app_name}}, installed in your account, uses access we retire on 2027-03-01.
We have notified its developer. After that date the app will stop reading
{{human_readable_data}} unless the developer updates it.
You can contact the developer, check for an app update, or plan a replacement.
```

**Clear this notice with legal or partner management first.** It tells a partner's customer about the partner's integration, and some partner agreements restrict contacting the partner's customers.

**In-response warning.** On every API response where the token carries a legacy scope, add:

```
Deprecation: true
Sunset: Mon, 01 Mar 2027 00:00:00 GMT
Link: <{{guide_link}}>; rel="deprecation"
```

Add a short warning in the body too, if your consumers read bodies more than headers.

## 4. Census: who gets the email

Group by OAuth client ID. Join to owner account, installs, contacts and their verification date.

```
SELECT client_id,
       MIN(first_call_legacy), MAX(last_call_legacy), COUNT(*) AS calls,
       MIN(first_call_replacement),
       installs, integration_shape, contacts, contacts_verified_at
FROM   gateway_calls
WHERE  scope IN ('people.read.all', /* every legacy scope */)
  AND  ts >= now() - interval '{{lookback}}'
GROUP  BY client_id ...
ORDER  BY installs DESC;
```

Add these rows:

- **Dormant credentials** (live grants, no recent calls). Flag them, don't exclude them. HR apps run payroll, open enrollment, annual reviews and year-end close. A credential that called once last January resumes on the old scopes in January and breaks after the cutoff.
- **One summary row** for calls with no client ID.

Rules that matter here:

- **Lookback:** at least 12 months, 13 is safer. Never 7 or 30 days. If log retention is shorter, mark the rows unknown, not migrated, and start retaining now.
- **Migrated means one of two things.** Either there is no legacy call for one full lookback after the first replacement call, or the owner confirms in writing that every job moved. One replacement call proves nothing.
- **Scope grants live on the customer side.** A token granted last year still holds the scope. Record the scopes held per grant, not only the scopes requested per call.
- **Abandoned credentials** go to `api-auth-key-management`'s revocation flow. Don't expire them inside this program.

**Integration shapes:**

| Shape | Contact chain |
|---|---|
| Single-account integrator | One owner. Risk is a mailbox nobody reads. |
| Fleet partner app | One fix repairs every install. Reach a named person. |
| Plugin or agency build (WordPress-style) | Developer fixes, then each site upgrades separately. Track installs on the fixed release and send the customer-admin notice. |

## 5. Send plan

**Rank by days to break, then by end customers affected.** All rows share one date, so installs decide the order. Don't rank by call volume. Add a commercial-weight column for contracts and strategic accounts.

- **Top tier:** named outreach by a partner manager. Size it by hours available, not a percentage. Take rows from the top until the hours run out. Fleet apps and plugins with many installs go first.
- **Long tail:** the automated ladder below.

**Before notice day (Mon 2026-11-02):**

1. Run the census, then confirm the unattributed share is zero.
2. Close the door:
   - New app registrations and new webhook destinations default to the replacement scopes.
   - **Don't block** rotated keys, new tokens or new installs of existing apps. Those inherit the app's current scopes until its break date or exception. Blocking them breaks integrations inside the notice window you promised.
   - Flag marketplace listings that still use legacy scopes. Block new installs only after 2027-03-01.
3. Get legal and partner management to clear the customer-admin notice.

**Schedule:**

| Date | Action |
|---|---|
| Tue 2026-11-03 | **Notice day.** Targeted email to every contact on file for every affected app, with the confirmation request inside the email. Also: in-response warning live, changelog post, dashboard banner, bounce-recovery variant to alternates. |
| 2026-11-03 to 11-20 | Named outreach to the top tier. Write the owner and ship date on each census row after the call. |
| Tue 2026-12-01 | Reminder to apps still calling and not acknowledged. Bounced or silent rows go to the commercial owner. |
| Tue 2027-01-05 | Reminder. Unverified rows that stay silent get the customer-admin notice (plugin and fleet shapes first). |
| Wed 2027-01-20 | **Brownout 1, 4 h**, only if readiness line 4 holds (below). |
| Tue 2027-02-02 | Reminder, with the exception path offered to rows that can't make the date. |
| Wed 2027-02-03 | **Brownout 2, 12 h.** |
| Wed 2027-02-17 | **Brownout 3, 24 h.** |
| Tue 2027-02-23 | Final notice, one week before cutoff. |
| Mon 2027-03-01 | Cutoff. Keep the old code path deployable behind the exception allowlist for one more lookback. |

**Cadence rules:**

- One email per app per month. A higher rate reads as spam and gets filtered.
- Stop an app's cadence when it acknowledges. Resume only if calls continue past the date it gave.
- Stop entirely when calls reach zero across the full lookback.
- Send each brownout announcement in advance, by changelog, email and the error body.

**Brownout mechanics:**

- Return the same status the cutoff will return (the legacy-scope error), with "temporary brownout" and the schedule in the error body.
- Send `Cache-Control: no-store` so no cache keeps the failure past the window.
- Start each window inside working hours for the affected regions.
- Pause on any incident in the replacement.
- Check the brownouts against your SLA terms first.
- If you can, offer a self-serve toggle so admins can force the breakage themselves and find their own dependent apps.

**Readiness gate.** Fill this in one week before each brownout and before cutoff. Every line must hold.

| Line | Check | Required |
|---|---|---|
| 1 | Top-tier apps not migrated and not under exception | 0 |
| 2 | Long-tail apps not notified at a verified contact or routed to a customer admin | 0 |
| 3 | Unattributed calls | 0 on authenticated surfaces |
| 4 | Replacement scopes met their service objective for migrated traffic over the last several weeks (at least one brownout interval), no open incident, headroom for residual load | yes |
| 5 | Exceptions missing owner, reason or expiry | 0 |

An unverified contact counts as no contact. A failed line names the next action: line 1 returns to named outreach, line 2 to contact resolution, line 3 to attribution work, line 4 to the replacement's owners.

**Exceptions** go per app, never as a global slip. Each is an allowlist entry keyed to the client ID, with an owner, a reason and one expiry date. Slip the date for everyone only if line 4 fails. Never pull the date earlier because few calls remain: that is a policy change for `api-versioning-policy`, not a burn-down result.

**Track weekly:**

- Calls on legacy scopes, which falls first and flatters progress.
- Apps still on legacy scopes, split into top tier and long tail. **The gate reads this one, not the calls curve.**
- Unattributed calls.
- New apps starting on legacy scopes after notice day. Target zero.
- Verified-contact coverage. Target 100%, or routed to a customer admin.

## 6. What I need from you

I have no census data, so every number above is a placeholder. These answers change the plan:

1. Does the gateway tag each request with client ID and scope? What share of traffic has no client ID?
2. How many of the 400 apps hold a legacy scope today, and how many are fleet apps or plugins?
3. What's the longest business cycle your apps run (annual reviews, year-end payroll)? How many months of logs do you retain?
4. Are the replacement scopes stable and complete for the use cases that migrate? What happens to existing tokens on 2027-03-01 (reject, or silently narrow)?
5. How many hours can the partner team spend on named outreach? Is there an account manager per top app?
6. Is the date fixed by contract or security, or is this the first of many sunsets you'll run?
7. Does your partner agreement allow contacting a partner's customers?

Answers 1, 2 and 4 matter most. With them I can turn the placeholders into a real send list and a sized top tier.