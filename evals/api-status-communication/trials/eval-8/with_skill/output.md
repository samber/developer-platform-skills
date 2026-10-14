# Draftify: maintenance communication plan for the primary-database migration

I read the skill and its maintenance reference, and used steps 4 and 7 plus the SLA edge cases. I could not ask the batched clarifying questions, so the unknowns are marked **[CONFIRM]** below. Each one has a default so nothing blocks.

## 1. Decisions

| # | Issue | Decision |
|---|---|---|
| 1 | The draft says "down a couple hours Saturday night" | It has no date, no time zone, no scope and no guidance. Replace it with the notice in §5. |
| 2 | Window chosen "because the office is closed" | That is the provider's office hours, and the skill says to schedule against the **customers'** low-traffic hours. Re-pick the window from write-traffic data (§2). |
| 3 | Enterprise contract needs 5 business days | Send the contractual notice **Monday 2026-10-05**, which is about 8 business days before the window. This is separate from the broadcast and goes through the contract's notice method (§4). |
| 4 | Marketing wants to bundle the v1 retirement | **No.** A maintenance notice and a deprecation have different timelines and different asks. Bundling buries both, and the skill forbids blending them (§6). |
| 5 | Delivery | The status page plus email and RSS subscription for everyone, a webhook for integrators, and a direct notice for the enterprise customer. Never the page alone. |

**[CONFIRM] The date.** Today is Saturday 2026-10-03, so "12 days" lands on Thursday 2026-10-15. The nearest Saturday 8pm ET is **2026-10-17**, which is 14 days out, and 2026-10-10 is too soon. I assume 10-17 below. If the migration date is fixed at 10-15, shift every date accordingly. The enterprise notice still goes out Monday.

## 2. Window check against Asia-Pacific traffic

Saturday 2026-10-17 at 8pm EDT is **2026-10-18 00:00 UTC**. A 2-hour window then runs 00:00-02:00 UTC. In local time:

| Region | Local time |
|---|---|
| Singapore | Sun 08:00-10:00 |
| Tokyo | Sun 09:00-11:00 |
| Sydney (AEDT) | Sun 11:00-13:00 |
| India | Sun 05:30-07:30 |

I don't know when "overnight" batches actually fire. The window may land after they finish, or in the middle of the India or Australia runs.

**Action (owner: Ops/SRE, due before the notice is drafted):**
1. Pull write-request volume per hour in UTC for the last 8 weeks. Look at weekends, plus any weekly or monthly batch peaks.
2. Pick the contiguous 2-hour block with the lowest write volume and the fewest distinct customers. The block can fall on Friday night or Sunday if the data says so.
3. Keep Saturday 00:00 UTC only if it is within roughly 10-15% of the minimum. Ops's choice may turn out fine, but the data has to say so.
4. Name the top 10 write-heavy customers and their batch times. Reach out to them individually (§4).

I also recommend announcing a **3-hour window with a 2-hour expected duration**. Migrations overrun, and a notice that is exceeded costs more trust than a roomy one.

## 3. Scope

Draft this with Engineering. I need these answers to fill the notice:

- **[CONFIRM]** Which endpoints fail? The notice assumes all POST/PUT/PATCH/DELETE routes, including document generation if it persists a document.
- **[CONFIRM]** What do they return? I assume 503 with a `Retry-After` header.
- **[CONFIRM]** Do reads of previously generated documents work for the full window?
- **[CONFIRM]** Are webhooks, the dashboard and API keys unaffected? Do dashboard writes fail?
- **[CONFIRM]** Is there a cutover moment with a few seconds of read errors? If so, say so.
- **[CONFIRM]** Does the platform support idempotency keys? If so, tell customers to use them on retries.

## 4. Audience-specific actions

**Enterprise customer (contractual)**
- Read the contract clause first: the notice method (named contact, email address, portal), whether "business days" are counted in the customer's or the provider's time zone, and whether Columbus Day (Mon 10-12) counts.
- Send the formal notice **Mon 2026-10-05** through the named channel. This exceeds the floor, and 5 business days before 10-17 is at the latest Fri 10-09.
- The account owner follows up personally and asks whether the window works for their batch schedule. Offer a different window if it does not.
- Keep proof of delivery. Planned maintenance is excluded from SLA downtime only when adequate notice was given, so the paper trail protects you.
- **[CONFIRM]** Where is this customer based? If it is APAC, check them first against §2.

**Top write-heavy customers from the traffic pull**
- Send a direct heads-up with the same text as the public notice, from the account owner, in the week of 10-05.

**All API consumers**
- The public notice, through the channels in §7.

## 5. The notice

**Send:** Mon 2026-10-05. Post it as a scheduled maintenance on the status page, then email it to subscribers.

> **Subject: Scheduled maintenance: document writes unavailable Sat 2026-10-17, 00:00-03:00 UTC**
>
> On **Saturday 2026-10-17, from 00:00 to 03:00 UTC** (Friday 20:00-23:00 US Eastern; Saturday 08:00-11:00 Singapore; Saturday 09:00-12:00 Tokyo), we will migrate Draftify's primary database. We expect the work to take about 2 hours. The 3-hour window includes a safety margin.
>
> **What is affected:** every request that creates, updates or deletes documents (`POST`, `PUT`, `PATCH`, `DELETE`, including document generation) will return `503` with a `Retry-After` header.
>
> **What is not affected:** reads (`GET`) of existing documents, the dashboard, API authentication and webhook deliveries. *(confirm each before sending)*
>
> **What to do:**
> - If you run batch jobs in this window, pause them or schedule them outside it.
> - Retry on `503` with backoff, and honor `Retry-After`.
> - Use an idempotency key on retries so a retried write cannot create a duplicate. *(if supported)*
>
> **How to follow along:** we will post when the window starts and again when it completes, at status.draftify.example *(use the real URL)*. Subscribe there to get email, RSS or webhook notifications. Questions or conflicts with this window: reply to this email or contact support, and we will work with you.

I used UTC-first times, because ambiguous time zones are the most common cause of maintenance confusion. Update the times if §2 moves the window.

## 6. Why the v1 retirement is a separate communication

- The maintenance notice asks readers to **do something in 12 days**. The retirement asks them to **plan something over about 14 months**. Combined, one of the two gets skimmed. During a window that is already stressful, the retirement news reads as bad news piled on top of an outage.
- The deprecation runway of 6-12 months or more is the territory of `samber/developer-platform-skills@api-versioning-policy`. It needs its own content: migration path, sunset headers, the dates, and a migration guide.
- A retirement announcement that is thin on detail is worse than none. Customers cannot act on "legacy v1 endpoints retire at the end of next year" with no migration guide.
- Sending two emails a few days apart costs Marketing nothing. The first goes out Mon 10-05 and must stand alone.

**Suggested alternative for Marketing:** send the v1 retirement as its own announcement **after the window completes**, for example the week of 2026-10-26. By then the maintenance is behind us and the migration guide can be ready. Run it through the versioning-policy skill: dates, the `Sunset` and `Deprecation` headers, usage data for v1 callers, and per-customer outreach for the heaviest v1 users. Marketing can still reuse the mailing list.

## 7. Channels

| Channel | Use | Notes |
|---|---|---|
| Status page, scheduled-maintenance entry | The source of truth, posted Mon 10-05 | Hosted outside the platform's own infrastructure if possible **[CONFIRM]**, so it survives the window |
| Email subscription | Broadcast, plus reminders | Also reaches non-subscribers if you email the customer list for this purpose, which is a transactional-notice case |
| Webhook push | Status event for integrators | Only if the status tool supports it |
| Enterprise direct notice | Contractual | Named contact, proof of delivery |
| SMS | **Not needed** unless a contract specifies it | Per the skill, SMS with no contractual audience is deleted from the menu |

All channels say the same thing at the same time. Do not publish the broadcast before the enterprise notice goes out.

## 8. Timeline

| When | Action | Owner |
|---|---|---|
| Today to Sun 10-04 | Pull the traffic data. Confirm scope (§3). Confirm the contract clause. Confirm the date. | Ops, Eng, Account mgmt |
| Mon 10-05 (T-12 days) | Enterprise formal notice. Status-page entry. Public email. Direct notes to heavy writers. | Comms, Account owner |
| Wed 10-07 | Review replies, window conflicts and questions. Adjust if a conflict is serious. Any change restarts the enterprise notice clock, so decide by 10-09 at the latest. | Support, Ops |
| Fri 10-09 | Last date the enterprise floor is still met. Treat it as a hard decision point for any window change. | Ops |
| Fri 10-16 (T-24 h) | Reminder email, plus a status-page reminder. | Comms |
| Sat 10-17, T-1 h | Short reminder via webhook and status page. | Comms |
| 00:00 UTC | Post "maintenance started". Flip the page component to **Under maintenance** (partial: writes). | Ops |
| During | Update at least every 30 minutes with the time of the next update, even with nothing new. | On-call |
| End | Post "maintenance completed" with the actual duration. If it overruns past 03:00 UTC, post that immediately as an incident (status: Investigating, then Identified, Monitoring and Resolved). | Ops |
| Mon 10-19 | Short wrap-up email to the enterprise customer and heavy writers, noting actual downtime. | Account owner |
| Week of 10-26 | The separate v1 retirement announcement (§6). | Marketing, DevRel |

## 9. Risks and checks

- **Overrun:** the fallback is the 3-hour window. Beyond that, treat it as an incident, not as maintenance.
- **SLA text:** confirm that planned maintenance is excluded only with adequate notice. Even then, a badly communicated window still costs trust.
- **Rollback:** decide in advance who calls the abort, and at which point it is no longer possible. Tell the enterprise customer if the window might move.
- **Status page hosted on shared infrastructure:** if it shares DNS or CDN with the platform, move it, or make sure the email channel works independently.
- **Third-party first disclosure:** the notice must go out well before any customer discovers failures on their own.

## 10. Open questions (reply with defaults if unsure)

1. Is the date Saturday 2026-10-17, or is 12 days a hard constraint (Thursday 10-15)?
2. Is the write-traffic data by UTC hour available, and can Ops pull it today?
3. Which endpoints return 503, and what is unaffected (§3)?
4. What does the enterprise contract say about notice method and business-day counting, and where is that customer based?
5. Do you have a hosted status page with subscriptions, or is that greenfield?
6. Is Marketing OK with a separate v1 announcement in the week of 10-26?