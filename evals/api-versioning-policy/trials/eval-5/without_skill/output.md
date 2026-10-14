# Corvid v2 reporting API deprecation: communication plan

## Verdict

Ship the `Sunset` header, but it is one channel of six, not the plan. Two of your claims don't hold:

- **"Every client gets the signal on every call."** The header is sent on every call, but few people see it. Most HTTP clients and SDKs discard response headers, and server-to-server integrations are rarely watched by a human. The developer who built the integration may have left. Treat the header as a machine-readable backstop.
- **"After the date we're covered."** RFC 8594 doesn't give you legal or contractual cover. Cover comes from your ToS, any enterprise contract notice clauses, and whether you made a documented, direct effort to reach people. Have legal check this before you announce.

## Prerequisites (do these before announcing)

1. **v3 is GA with parity.** List the v2 endpoints that have no v3 equivalent. If any exist, resolve them first or the date is fiction.
2. **Migration guide.** Include an endpoint-by-endpoint mapping, request and response diffs, auth changes, and a before/after code sample per SDK language.
3. **SDKs and tooling.** Ship updated SDKs, and a codemod or compatibility shim if feasible.
4. **Per-key v2 usage data from your logs.** Pull the last 90 days by key, endpoint, and volume.
5. **Key-to-account map.** One customer often has several keys. Find out what contact data you actually hold for each key owner.
6. **Written shutdown policy.** Decide now what happens to stragglers: hard cut, or exceptions by exec sign-off. Decide who can grant an extension.

## Header spec

On every v2 response, including errors:

- `Deprecation: @<announce-epoch>` (RFC 9745). `Sunset` alone doesn't mean "deprecated".
- `Sunset: <HTTP-date>`. Use a fixed date, and never move it silently.
- `Link: <migration-guide-url>; rel="deprecation"` and `Link: <policy-url>; rel="sunset"`.

Checks before launch:

- Confirm your CDN and gateway pass these headers through.
- Add `Access-Control-Expose-Headers` for them if browser clients call v2.
- Don't change response bodies. It breaks parsers.

## Timeline (T = sunset date, 14 months out)

| When | Action | Audience |
|---|---|---|
| T-14m | **Announce.** Turn on headers, publish the changelog entry, migration guide, and docs banner, and send email to key owners | All ~3,000 keys |
| T-14m | Personal outreach (CSM or engineer) | Top-volume keys and strategic accounts |
| T-12m | Reminder with usage stats ("you made N v2 calls last month") | Still-active keys only |
| T-9m | Reminder, plus office hours or a migration clinic | Still-active keys |
| T-6m | Reminder. Dashboard or console banner for any user of an active v2 key | Still-active keys |
| T-3m | **First brownout:** a 1–2 hour planned v2 outage, announced a week ahead | Still-active keys |
| T-2m / T-1m | Longer brownouts. Direct contact with every remaining caller | Remaining callers |
| T-1w | Final notice | Remaining callers |
| T | **Shutdown.** Return `410 Gone` with a JSON body linking the migration guide. Don't return 404 or time out | Everyone |
| T+3m | Keep the 410 responses. Remove the code later | Everyone |

Notes:

- From T-12m on, reminders go only to keys still seen in the logs. Dormant keys get the announce email and the headers, then nothing more.
- Brownouts are the most effective step. They are the first time many teams notice, and they are cheap to run.
- Fourteen months is generous. It's fine if you hold the milestones, but a long window with no checkpoints invites procrastination.

## Channels beyond the header

- Email to the key owner, plus any billing or technical contacts you hold.
- Developer docs banner on every v2 page.
- Changelog and status page.
- Dashboard or console notice where keys are managed.
- Support macros, an FAQ, and a named inbox for migration questions.
- Third-party connectors (BI tools, Zapier-style integrations). The end user can't migrate on their own, so contact the vendor directly.

## Measurement and go/no-go

Track weekly:

- v2 request share
- Active v2 keys (distinct keys in the last 7 days)
- Share of top-N accounts migrated
- Support tickets tagged "v2 migration"

Gate the shutdown on thresholds you set up front. For example: active v2 keys below X, and no top-20 account still on v2. If the gate fails, the exception process from your shutdown policy decides. Don't improvise extensions in the final week. If you do extend, update the header date and send a new notice.

## Open questions for you

1. Do all ~3,000 keys map to a reachable email? What share are anonymous or tied to departed users?
2. How many of those keys were active in the last 90 days? The real audience is probably much smaller.
3. What do the ToS and enterprise contracts say about deprecation notice periods?
4. Does v3 cover every v2 endpoint?

With those answers I can turn this into dated calendar entries and draft the announcement email and the 410 response body.