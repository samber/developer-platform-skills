# Legacy scope removal: email and send plan

⚠️ **I recommend against the blast as framed.** I didn't read anything under `skill-wip/`, as you asked. The advice below comes from your numbers and general practice.

## Why not blast all 3,000

- 38% of the November emails bounced, so the owner address is stale for about 150 of your 400 apps. A stronger subject line can't reach a mailbox that doesn't exist.
- Repeating the send to hard-bounced addresses hurts your sender reputation. Mail to the remaining developers is then more likely to land in spam, and those are the people you most need to reach.
- 3,000 accounts includes many that are unrelated to the apps that need to migrate. Emailing everyone trains people to ignore you.
- Plugin-style apps have a second problem. The developer must ship an update, and the agencies and their clients must install it. One email to the developer doesn't cover that.

## Step 0: data pull (this week, about half a day of data work)

1. **Find apps that still use legacy scopes.** Pull this from OAuth token and grant logs, not from the marketplace listing. Count the apps with a legacy-scope call in the last 90 days.
2. **Split bounces into hard and soft.** Suppress hard bounces. Retry soft bounces once.
3. **Map each app to every contact.** Include the owner address, all developer accounts attached to the app, the partner-manager contact, and any billing or security contact.
4. **Mark plugin-style apps.** Record how many installs each has and which agencies or tenants run it. The install list is yours to query.
5. **Rank by risk.** Order apps by installs times legacy-call volume.

## Segments

| Segment | Who | Channel | Message |
|---|---|---|---|
| A | Apps still calling legacy scopes, reachable | Email to all developer accounts on that app only | Email A below |
| B | Plugin-style apps (agency installs) | Email B to developers, plus a notice to installing admins | Email B below |
| C | Apps whose owner hard-bounced | Partner manager outreach, console banner, secondary contacts, then a postal or LinkedIn fallback for the top 20 by installs | Short personal note |
| D | Apps with no legacy calls in 90 days | One short FYI, or none | "No action needed" |
| E | Developer accounts with no app attached | Nothing | None |

If A, B and C together are under about 1,500 accounts, you have already cut the audience in half.

## Non-email channels (the bounce fix)

- **API signal.** Add `Deprecation` and `Sunset: <date>` response headers on every call made with a legacy scope. Include a link to the migration guide. Developers who ignore email still see the headers in their logs.
- **Developer console banner.** Show it on every login for affected apps, naming the scopes in use.
- **OAuth consent screen.** Warn users and admins who authorize a legacy-scope app.
- **Admin notice to customers.** For plugin installs, tell the HR admin that the app may stop working on March 1 and who to contact.
- **Partner manager calls** for the top 30 apps by install count.
- **Optional brownouts.** Return errors on legacy scopes for one hour on two announced days. This needs engineering and exec approval, and I haven't assumed it. It is the single most effective nudge.

## Email A: active app, reachable developers

**Subject (primary):** `[Action by Mar 1] {{app_name}} still uses legacy Pollen scopes that stop working`
**Subject alternatives to A/B test:**
- `{{app_name}} will lose access to Pollen people data on March 1`
- `Your Pollen app calls people.read.all: it stops working March 1`

Avoid all caps, "URGENT", and "FINAL". They raise spam-filter scores and don't increase action.

**Preheader:** `Our records show {{call_count}} legacy-scope calls from your app in the last 30 days.`

```
Hi {{first_name}},

On March 1, 2027, Pollen HR will remove these legacy OAuth scopes:
people.read.all, {{other_legacy_scopes}}.

Your app, {{app_name}}, called them {{call_count}} times in the last 30 days.
After March 1, those calls will return {{error_code}} and the features that
depend on them will stop working for your customers.

What to do:
1. Replace each legacy scope with its new equivalent: {{mapping_link}}
2. Test in the sandbox: {{sandbox_link}}
3. Mark the migration complete in your developer console: {{console_link}}

Most apps need {{typical_effort}} of work. If your app needs a scope that has
no replacement, reply to this email by {{gap_reply_date}} so we can look at it
before the deadline.

You received this because you are a developer on {{app_name}}. We sent a
similar message in November to the app owner address, and many of those
messages did not arrive. If you know the right person to receive this,
please forward it or add them in the console: {{contacts_link}}

Questions: {{partner_team_email}}

Pollen HR Partner Team
```

## Email B: plugin-style apps installed by agencies

**Subject:** `[Action by Mar 1] {{plugin_name}} needs an update before legacy Pollen scopes are removed`

```
Hi {{first_name}},

On March 1, 2027, Pollen HR will remove the legacy OAuth scopes
people.read.all, {{other_legacy_scopes}}.

{{plugin_name}} uses them, and it is installed by agencies on behalf of their
clients ({{install_count}} active installs). Because your plugin runs on sites
you don't control, the update has to reach those installs before March 1.

What to do:
1. Ship a plugin release that uses the new scopes: {{mapping_link}}
2. Make the update path safe. Existing installs hold tokens for the old
   scopes, so the plugin must re-request consent after updating: {{reauth_link}}
3. Publish a changelog entry and a short note for agencies explaining that
   they must update and re-authorize.
4. Send us your release date by {{release_reply_date}}. We will notify the
   admins who installed your plugin, and we can send them your note.

Plan for a gap between your release and when agencies update. We suggest
releasing by {{target_release_date}} to leave eight weeks for installs to catch up.

Questions: {{partner_team_email}}

Pollen HR Partner Team
```

## Email C: short personal note for unreachable top apps (sent by the partner manager)

```
Subject: {{app_name}}: Pollen scope removal on March 1

Hi {{name}}, we tried to reach {{app_name}} in November and the message
bounced. Legacy scopes ({{list}}) are removed March 1, and your app still uses
them. Who should we talk to? Reply here or book 15 minutes: {{calendar_link}}
```

## Send plan

All dates are proposals. Today is Oct 30, and the deadline is about 17 weeks out.

| When | What | Gate |
|---|---|---|
| Nov 2 to 6 | Step 0 data pull, segment lists, suppression list, console banner and API headers ready | Engineering confirms the headers ship |
| Nov 9 | **Test send** to 20 internal and friendly addresses. Check SPF, DKIM and DMARC alignment, then spam-folder placement | Placement is clean |
| Nov 10 | **Wave 1:** Email A to 10% of Segment A, highest-risk apps first | Bounce rate stays under 2% and complaints under 0.1% |
| Nov 11 to 12 | **Wave 2:** rest of Segment A, then Email B to Segment B in batches of 25% of the list per day | Same thresholds each day. Pause if either is breached |
| Nov 10 onward | Partner managers start Segment C outreach and Email C | Top 30 apps contacted by Nov 24 |
| Dec 7 | Reminder 1, only to apps with no migration marked complete | Check status in console first |
| Jan 12 | Reminder 2, same filter. Skip Dec 19 to Jan 4 | |
| Feb 2 | Reminder 3, and begin optional brownout announcement | Exec approval for brownouts |
| Feb 17 | Reminder 4. Partner managers call every app still unmigrated in the top 100 | |
| Feb 24 | Final notice, plain tone, with the exact error behavior after March 1 | |
| Mar 1 | Scopes removed. Support staffed. Status page note live | |

Remove any app from further sends as soon as it marks migration complete.

## Deliverability and compliance checks

- Send from a dedicated subdomain with SPF, DKIM and DMARC aligned. Use a real reply-to mailbox that a person monitors.
- Treat these as service notices about a change to the product they use. Keep promotional content out of them, and confirm your terms and privacy notice allow this use of developer contact data. Ask Legal if unsure.
- Use plain-text-friendly formatting and one link per action. No tracking pixels are needed.
- Honor unsubscribe requests for the reminder series, but keep the console banner and API headers on.

## What to report back to your manager

Track these weekly, and the second blast stops being a debate:
- Apps with legacy calls in the last 7 days. This is the real success metric, and the target is zero by Feb 24.
- Apps marked migrated, by segment.
- Delivery, bounce and reply rates per wave.
- Top 100 apps by installs that are unmigrated, each with a named owner at Pollen.

## Open questions for you

1. Can engineering add the `Sunset` headers and a console banner by Nov 9? Everything else leans on them.
2. Will leadership approve brownouts?
3. Can you query plugin installs and installing admins from your own data? If not, Email B's admin notice needs a different path.
4. What are the exact replacement scopes? I used placeholders for scope names, error codes, links and effort estimates. Fill them in before any send.