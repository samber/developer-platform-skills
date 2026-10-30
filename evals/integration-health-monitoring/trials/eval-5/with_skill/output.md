# Verdict: don't run the brownout as planned

The Monday notice and the 30th removal can stand. The brownout needs two changes before it is safe.

Today is Fri 2026-10-30, so I read "the 30th" as Mon 2026-11-30. I haven't seen your traffic, so every call or integration count below is still unknown. Nothing here claims how many integrations are affected.

## Sanity check

**1. The replacement failed two weeks ago, and the postmortem is open. This is the blocker.**
- A brownout moves every query-string caller onto header auth, the system that just had an outage.
- Readiness gate line 4 needs the replacement to have met its service objective for several weeks, with no open incident. It also needs headroom for the extra load.
- A brownout "next week" is about three weeks after the outage with the postmortem unfinished, so the gate fails today.
- If header auth falls over during the window, you break partners with your own defect, not theirs.
- **Gate for the first window:** postmortem closed, remediation shipped, SLO met since the fix, and a load check. The check should show header-auth capacity covering today's header traffic plus all query-string traffic.
- **If the gate isn't met:** move the brownouts, not the notice. Send Monday's notice anyway. Slip the cutoff only if line 4 still fails near the end. Don't slip it for everyone because of a few laggards.

**2. A single 72-hour window is the wrong shape.**
- Brownouts should escalate, hours first and then longer. GitHub ran 12, 24, then 48 hours before it removed query-parameter auth.
- A first-ever 72-hour outage covers a weekend and every timezone, and it's the harshest signal you can send. It gives callers no smaller warning to react to.
- I suggest three windows instead, 76 hours in total, each starting at 14:00 UTC on a weekday:

| Window | Start (UTC) | Length | Ends |
|---|---|---|---|
| 1 | Tue 2026-11-10 14:00 | 4 h | Tue 18:00 |
| 2 | Tue 2026-11-17 14:00 | 24 h | Wed 14:00 |
| 3 | Mon 2026-11-23 14:00 | 48 h | Wed 2026-11-25 14:00 |

- The third window ends before US Thanksgiving (Thu 11-26) and leaves four days before removal.
- Each window returns `410 Gone`, the same status as after removal.
  - The body marks it as a temporary brownout and lists the schedule.
  - The response carries `Cache-Control: no-store`, because 410 is heuristically cacheable and a cached failure outlives its window.
- Pause the series on any incident in header auth. Check the gate again before each window.

**3. A changelog post doesn't reach the integration owners.**
- Changelog and policy pages are owned by `api-versioning-policy`, and they reach nobody in particular.
- From Monday, also send a targeted email to every contact on file for each credential that has used query-string auth.
  - The email carries the credential, call count, last seen, one sample request ID, the dates and the migration guide.
  - It asks the recipient to confirm ownership or name the owner. Don't hold the notice for verification.
- From Monday, add `Deprecation` and `Sunset` headers to every query-string response (see the end of this answer).
- Pick the top tier by outreach hours available. Give those integrations named outreach this week, before the brownouts. Pick them by end customers affected, not by call volume.
- Customer-admin notices are optional. Use them for fleet apps or plugins whose end customers never hear from you, and clear them with legal first.

**4. The four-week window is short, so compress the cadence.**
- Monday to the 30th is under three monthly notice intervals. Send at once, at the midpoint, and one week before each brownout.
- Is the date fixed by a security or contractual reason? If so, say so in the post, because that is the justification for a short window. If not, a four-week window is a policy question for `api-versioning-policy`. Header auth has existed for two years, which helps.
- Don't shorten it further because "few callers are left". That would be a policy change, not a burn-down result.

**5. Do these before Monday.**
- **Lookback:** use the longest business cycle, not 30 days. Quarterly or year-end jobs call once and go quiet, and a 30-day window counts them as migrated. If log retention is shorter than that cycle, mark those rows "unknown", not "migrated".
- **Dormant keys:** list live keys with no recent calls, with their last-seen date. Don't expire them inside this program, because seasonal jobs would break. Send confirmed-abandoned keys to the key-revocation flow.
- **New integrations:** stop them from starting on query-string auth on notice day.
  - New accounts, apps and keys default to header auth.
  - Rotated keys and existing apps keep working until the cutoff.
- **Unattributed share:** every accepted query-string call carries a key. Any unattributed share above zero is a logging gap, so fix that first.
- **Key logging:** log the key ID, never the secret. Query-string keys already sit in URLs, so check that your own gateway and access logs don't store the full query.
- **Cutoff:** keep the old code path deployable behind a per-credential allowlist for one lookback. A top-tier caller you missed gets a two-week exception, never a global rollback.

## Go/no-go gate

Fill this in one week before each window and before the cutoff:

| Line | Check | Today |
|---|---|---|
| 1 | Top-tier integrations migrated or under exception | unknown, run the census |
| 2 | Long tail notified at a verified contact or customer admin | unknown |
| 3 | Unattributed query-string calls | must be 0 |
| 4 | Header auth met its SLO for several weeks, no open incident, headroom | **fails today** (postmortem open) |
| 5 | Exceptions have owner, reason and expiry | none yet |

## Changelog post

Edit the bracketed items, then publish Monday 2026-11-02. This post replaces the old guidance, so don't also publish a separate announcement.

---

**Title: Query-string API keys will stop working on November 30**

**Published:** 2 November 2026

We're removing API key authentication via the query string (`[?api_key=…]`) on **30 November 2026 at 00:00 UTC**. After that, requests that authenticate this way return `410 Gone`. Header authentication has been available for two years, and it is the only supported method from that date.

**Why:** [One sentence, only if true: keys in URLs end up in access logs, proxies and browser history.]

**What you need to do**
1. Find requests that send the key in the URL.
2. Send the key in the `[Authorization]` header instead. [Link: migration guide, with before/after examples]
3. Redeploy and check that calls still succeed.

No new keys are needed. Existing keys work unchanged in the header.

**Dates (all UTC)**

| Date | What happens |
|---|---|
| 2 Nov | This notice. Query-string responses now carry `Deprecation` and `Sunset` headers. |
| 10 Nov, 14:00–18:00 | Brownout 1 (4 hours) |
| 17 Nov, 14:00 → 18 Nov, 14:00 | Brownout 2 (24 hours) |
| 23 Nov, 14:00 → 25 Nov, 14:00 | Brownout 3 (48 hours) |
| 30 Nov, 00:00 | Query-string authentication removed permanently |

**What a brownout looks like.** During each window, requests that authenticate through the query string return `410 Gone`, exactly as they will after removal. The error body says it is a temporary brownout and repeats this schedule. Header-authenticated requests are unaffected. If we have an incident on header authentication, we will postpone a window and update this post.

**Check whether you're affected.** Look in your own logs for the key in the URL. If you have a client that calls us once a quarter or once a year, check that one too. We are emailing the contacts on file for every key that has used query-string auth. If that email isn't reaching you, or it names an integration you don't own, reply to it.

**Need more time?** If you have a specific constraint, such as a year-end job, contact us at [support address] before 16 November. We can grant per-integration exceptions. We are not moving the date for everyone.

Questions: [support address] · [migration guide]

---

## Headers and brownout error body

**Headers from Monday** on every query-string response:
```
Deprecation: @1762041600
Sunset: Mon, 30 Nov 2026 00:00:00 GMT
Link: <[migration guide URL]>; rel="deprecation"
```

**Brownout response:**
```
HTTP/1.1 410 Gone
Cache-Control: no-store

{"error": "query_string_auth_removed",
 "message": "Temporary brownout: query-string API keys are being removed. Send the key in the [Authorization] header instead. This window ends [time] UTC.",
 "schedule": ["2026-11-10T14:00Z/4h", "2026-11-17T14:00Z/24h", "2026-11-23T14:00Z/48h"],
 "removal": "2026-11-30T00:00:00Z",
 "guide": "[migration guide URL]"}
```

## Decisions I need from you

1. Is the 30 November date fixed by a contract or security reason, or is it a choice? That decides whether the date can move and whether the post should say why.
2. When does the postmortem close, and can you show the SLO and load numbers for header auth? Without them, window 1 slips.
3. How many outreach hours do you have this week? That sets the size of the top tier.