# Brownout plan review and changelog post

## Assumptions to confirm

- **Dates:** Today is Fri 2026-10-30. "Monday" is Nov 2, "next week" is Nov 3–9, and "the 30th" is Mon Nov 30.
- **Details I couldn't see:** The header name, the docs URL and the contact address are `[BRACKETED]` placeholders.
- **Usage data:** I haven't seen any data on how many keys still use query strings. If you have it, it changes the advice below.

## Verdict: don't run a 72-hour brownout next week

The direction is right. Keys in URLs leak into access logs, proxies and browser history, and header auth has existed for two years. The timing and shape are the problems.

1. **The replacement path is under postmortem.** A brownout sends every remaining client to header auth. If header auth fails again, those clients have no fallback, and you can't tell a brownout failure from a real outage. Gate the first brownout on the postmortem being closed and its action items shipped. Also keep a kill switch that restores query-string auth in minutes.
2. **The notice is too short.** The brownout would start 1–2 days after the changelog post. Most integrators won't read a changelog in that time. The removal gets 28 days' notice, which is tight for a credential change. Many customers need a ticket, a deploy and sometimes a secrets rotation.
3. **72 hours straight is an outage, not a brownout.** A brownout works by short, escalating, business-hours windows. Someone notices, fixes it, and the windows get longer. One 72-hour block gives no way to learn from the first window, and weekend on-call teams will be hit hardest.
4. **A 410 is cacheable by default.** It means "gone", and intermediaries may cache it. A brownout 410 must not stick after the window ends. Send `Cache-Control: no-store` on every brownout response.
5. **Enforcement should follow measurement.** Don't start hard enforcement until the count of query-string callers has visibly flattened. You need a per-key count of query-string callers first, so you can contact the stragglers by name.

## Recommended plan

| Date | Action |
| --- | --- |
| Mon Nov 2 | Publish the changelog entry. Email the owners of every key seen using query-string auth. Start returning `Deprecation` and `Sunset` headers plus a warning in the response body on every query-string call. |
| Before Nov 10 | Close the header-auth postmortem and ship its action items. Confirm the kill switch works. Re-count remaining query-string callers. |
| Tue Nov 10 | 1-hour brownout, midday. |
| Tue Nov 17 | 4-hour brownout. |
| Tue Nov 24 | 24-hour brownout. Avoid the US Thanksgiving week for anything longer. |
| Mon Nov 30 | Permanent removal, only if the remaining-caller count has flattened. If it hasn't, slip the date and say so publicly. |

For each brownout response:
- **Status and headers:** `410 Gone`, `Cache-Control: no-store`.
- **Body:** a JSON error with a stable code, such as `query_string_auth_removed`. It should say how to fix the call and link to the docs.
- **Logging:** never log the key from the URL.
- **Monitoring:** watch header-auth latency and error rate during each window. Abort if either degrades.

If you must keep the brownout next week, make it a single 1–2 hour window on Thu Nov 5, after the postmortem items are done. I'd still push back on that, because the notice would be 3 days.

## Changelog post

Written for the recommended schedule. Times are UTC placeholders, so edit them if you change the plan.

````markdown
## API keys in query strings are being removed

**Breaking, action required by November 30, 2026.**

Ferrowell's API will stop accepting API keys in the URL query string
(for example `?api_key=...`). Send the key in the `[HEADER_NAME]` request
header instead. Header authentication has been supported for two years and
needs no other changes.

### Who is affected

Any integration that authenticates with `api_key` (or `[PARAM_NAME]`) in the
URL. If you already send your key in the `[HEADER_NAME]` header, you don't need to do anything.

### What to change

```bash
# Before
curl "https://api.ferrowell.com/v1/[ENDPOINT]?api_key=YOUR_KEY"

# After
curl -H "[HEADER_NAME]: YOUR_KEY" "https://api.ferrowell.com/v1/[ENDPOINT]"
```

To find affected calls, search your code and config for `api_key=`. Any
request that still uses a query-string key now receives `Deprecation` and
`Sunset` response headers.

### Timeline

| Date | What happens |
| --- | --- |
| Nov 2 | This notice. Query-string calls keep working and return deprecation headers. |
| Nov 10, 14:00–15:00 UTC | Test window 1: query-string calls return `410 Gone`. |
| Nov 17, 14:00–18:00 UTC | Test window 2: query-string calls return `410 Gone`. |
| Nov 24, 00:00–24:00 UTC | Test window 3: query-string calls return `410 Gone`. |
| Nov 30 | Query-string authentication is removed permanently. |

During a test window, affected calls fail with `410 Gone` and the error code
`query_string_auth_removed`. Calls with header authentication are not
affected. Use the windows to confirm your migration.

### Recommended: rotate keys that were sent in URLs

URLs are often recorded in proxy, CDN and application logs. If a key has ever
been sent in a query string, consider rotating it after you switch to the header.

### Questions

Contact [SUPPORT_CONTACT] or see [DOCS_LINK].
````

## Open items

- **Per-key usage data:** Pull it before Monday and use it to decide who gets a direct email.
- **Postmortem:** Don't mention it in the public post unless you've published it. The post says nothing about it.
- **Dates:** If you keep the original "72 hours next week", tell me and I'll rewrite the timeline table. I'd still add the `Cache-Control` and kill-switch requirements.