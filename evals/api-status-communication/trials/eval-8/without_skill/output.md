# Draftify database migration: communication plan

## Do this first (today, Sat Oct 3 to Mon Oct 5)

1. **Fix the date.** 12 days from today is Thursday Oct 15, not a Saturday. Candidates are Sat Oct 10 or Sat Oct 17.
   - Oct 10 is impossible. Five business days of notice would have had to go out by Oct 2.
   - **Oct 17 is the working assumption below.** Ops must confirm.
2. **Read the enterprise contract.** Confirm four things:
   - how "business days" are counted, and which holiday calendar applies (Mon Oct 12 is a US federal holiday and a Japanese one);
   - who must receive the notice, and by what method (named contact, email, certified);
   - whether the downtime counts against the uptime SLA;
   - whether the notice must state the time window.
3. **Pull write-call volume by hour for the last 4 weeks, split by customer region.** This settles the window debate with data instead of opinion (see below).
4. **Have Ops confirm the failure behavior.**
   - Write calls should return `503` with a `Retry-After` header. They should not hang or silently drop.
   - Decide what happens to async or queued generation jobs mid-flight.
   - Confirm that reads really are unaffected, including webhooks and status endpoints.

## Window: don't just accept "Saturday 8pm ET"

Sat Oct 17, 8:00 pm EDT is Sun Oct 18, 00:00 UTC. In local time:

| Region | Start |
|---|---|
| US Pacific | Sat 5:00 pm |
| UK | Sun 1:00 am |
| Central Europe | Sun 2:00 am |
| India | Sun 5:30 am |
| Singapore | Sun 8:00 am |
| Tokyo | Sun 9:00 am |
| Sydney | Sun 11:00 am |

- By my conversion, the window falls on Sunday morning or midday in Asia-Pacific. That is mostly after a typical overnight batch window (about 22:00 to 06:00 local), not in the middle of it.
- Whether it actually hits batch jobs depends on when customers' jobs run. Your hourly data will show that.
- Pick the 2-hour window with the lowest write volume across all regions, not the one that suits our office hours.
- Announce a **3-hour window** for a 2-hour expected outage. Migrations overrun. A wider announced window protects customers and the contract.
- If the data shows heavy APAC writes in the window, Ops should consider moving it. Do it before any notice goes out. Changing the date after notice restarts the contract clock.

## Do not bundle the v1 retirement

Reply to Marketing with these reasons:

- **The downtime notice needs an action in 2 weeks.** A retirement notice needs an action in 14+ months. Together, the long-dated item dilutes the urgent one.
- **The enterprise contract notice should be clean.** A mixed message muddies the record of what we gave notice of.
- **A retirement announcement needs its own material.** It needs a migration guide, a v1-to-v2 mapping, and a dated timeline. Sending it half-ready invites a wave of support tickets just as we need support capacity for the migration.
- **Customers who see "API down" and "v1 retired" together may read them as linked.** They aren't.

Offer instead:

- A separate deprecation announcement **about 1 to 2 weeks after the migration** (week of Oct 26), when the guide is ready.
- Before it ships, check whether any contract or published policy promises a longer v1 support period.
- Marketing still gets "we're emailing everyone anyway." The post-migration email can open with "migration complete, thanks for bearing with us."

## Timeline (target: Sat Oct 17)

| When | Action | Owner |
|---|---|---|
| Mon Oct 5 | Date, window and contract decisions locked | Ops + Legal |
| **Mon Oct 5 or Tue Oct 6** | **Formal notice to the enterprise customer.** Add an account-manager call and get written acknowledgment. This is well before the contract deadline, which falls around Fri Oct 9 depending on the holiday count. | Account manager |
| Tue Oct 6 | Personal note to the top write-volume customers, especially APAC batch users | Support / CSM |
| Tue Oct 6 | General email, status page scheduled maintenance, docs banner, changelog entry | Comms |
| Sat Oct 10 | Reminder 1 (T-7 days) | Comms |
| Thu Oct 15 | Ops dry-run results confirmed. Go/no-go. | Ops |
| Fri Oct 16 | Reminder 2 (T-1 day), email and status page | Comms |
| Sat Oct 17 | Status page "in progress" at start. Update every 30 minutes if it overruns. | Ops |
| End of window | "Complete" on the status page and email. If the window is missed, post an incident update immediately. | Ops |
| Week of Oct 26 | Separate v1 deprecation announcement | Marketing + Eng |

## The messages

### 1. Formal notice to the enterprise customer

> **Subject: Scheduled maintenance notice: Draftify document-write API, Sunday Oct 18, 2026 (00:00–03:00 UTC)**
>
> Hello [name],
>
> This is formal notice, under [section] of our agreement, of planned downtime.
>
> - **Window:** Sunday, October 18, 2026, 00:00 to 03:00 UTC (Saturday October 17, 8:00 pm to 11:00 pm US Eastern). We expect about 2 hours.
> - **Impact:** Document-write requests will fail with HTTP 503 and a `Retry-After` header. Read requests are not affected.
> - **Reason:** Migration of our primary database.
> - **What we suggest:** Pause scheduled generation jobs for this window, or retry with backoff on 503. [Idempotency guidance if applicable.]
>
> Live status: [status page URL]. Your contact during the window: [name, phone/email].
>
> Please confirm receipt by replying to this message.
>
> [Sender]

### 2. General announcement email

> **Subject: Scheduled maintenance: document writes unavailable for ~2 hours on Oct 18 (00:00 UTC)**
>
> **What's happening:** We're migrating our primary database. During the window, **document-write API calls will fail. Reads and downloads keep working.**
>
> **When:** Sunday, Oct 18, 2026, **00:00 to 03:00 UTC** (about 2 hours expected). Local start times:
> - US Eastern: Sat Oct 17, 8:00 pm
> - US Pacific: Sat Oct 17, 5:00 pm
> - London: Sun Oct 18, 1:00 am
> - Mumbai: Sun Oct 18, 5:30 am
> - Singapore: Sun Oct 18, 8:00 am
> - Tokyo: Sun Oct 18, 9:00 am
> - Sydney: Sun Oct 18, 11:00 am
>
> **What you should do:**
> - Pause or reschedule batch jobs that create or update documents during this window.
> - Make sure your integration retries on 503 responses, using the `Retry-After` header.
> - Jobs that run entirely on reads need no change.
>
> **Follow along:** [status page] (subscribe for updates). Questions: [support address].
>
> We'll confirm when it's complete. Thank you for planning around this.

### 3. Status page entry

> **Scheduled maintenance: Oct 18, 00:00–03:00 UTC.** Document-write API calls will return 503. Read calls are unaffected. Expected duration: about 2 hours.

### 4. Reminders (T-7, T-1)

> Reminder: write calls to the Draftify API will fail Sun Oct 18, 00:00–03:00 UTC (Sat 8:00 pm US Eastern). Reads unaffected. Details: [link].

## Why the current draft doesn't work

"Heads up - the API will be down for a couple hours Saturday night for maintenance."

- **Wrong scope:** only writes fail, so "the API will be down" overstates it.
- **Wrong "when":** "Saturday night" is ambiguous. For APAC customers it's Sunday morning.
- **No date, no timezone, no duration beyond "a couple hours."**
- **No instruction.** Customers don't know whether to pause jobs.
- **No status link or contact.**
- **It doesn't meet a contract notice.** It names no date, window or impact.

## Open decisions

1. Ops confirms the real date (Oct 17 is assumed).
2. The data-driven window, after the hourly write-volume pull.
3. Legal confirms the contract's notice method and business-day count.
4. Whether in-flight async jobs are queued or rejected during the window.
5. The sender and owner for each message.