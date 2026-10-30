**Verdict: not good to cut Dec 1 on this evidence. Keep Jan 15 and cut the on-call cost another way.**

**Next action (today, about 1 hour):** query v1 logs for the last 180 days. Group by account and API key, with absolute request counts per day. Look for spikes on the last day of each month and quarter.

## Why 0.4% does not clear it

1. **Share is not count.** v1 fell from 31% to 0.4% partly because v2 grew. Absolute requests and distinct callers matter more. Ten marketplaces could be 0.4% and still be your biggest customers.
2. **The 30-day window hides periodic callers.** Today is Oct 30, so the window barely holds the Sep 30 quarter-end. It holds no month-end that is still ahead. Settlement exports run monthly or quarterly and may show as a single day of spikes.
3. **Dec 1 is the worst date.**
   - Black Friday and Cyber Monday run Nov 27–30. Cyber Monday is also month-end, one day before the cut.
   - Many customers freeze code in December, so they cannot migrate then.
   - Dec 31 year-end close falls between Dec 1 and Jan 15. The new date removes exactly that run.
4. **About 60 partner apps are third-party code.** Each has its own release cycle and directory review. Their end users will not know why charges failed.
5. **Cutting a public sunset early breaks a promise.** Check your ToS, contracts, and SLAs for a notice period. Ask legal before anyone says "Dec 1" to customers.
6. **The saving is about 6 weeks of on-call.** The risk is a payments outage for your biggest accounts. The trade is poor.

I do not know your data, so the gates below are what I would require.

## Plan, Oct 30 to Jan 15

1. **Week of Nov 2: build the caller list.** Check that the Grafana 0.4% covers all v1 charge traffic and not only one route. Tag each caller as marketplace customer, partner app, internal, or unknown. Estimate 1 day.
2. **Week of Nov 2: notify every remaining caller.**
   - Send a named email to each one.
   - Add a dashboard banner.
   - Add `Deprecation` and `Sunset` headers to v1 responses.
   - Notify all 60 app owners through the app directory. Mark v1 callers as "action needed".
3. **Nov 9–20: run brownouts.**
   - Use short windows of 1 hour on weekdays.
   - Return a clear error that names the v2 migration guide.
   - Skip Nov 23–30.
   - Brownouts surface callers the logs and emails miss.
4. **Nov 20: decision gate.** Pull in the date only if all of these hold:
   - Every caller above a set volume has been contacted and has confirmed a migration date.
   - Brownouts surfaced no new callers.
   - Legal confirms the notice period.
   - Support agrees to handle the cutover.
5. **Dec 1: default-deny with an allowlist.** Block v1 for accounts with zero v1 traffic in 90 days. Keep it open for everyone else until Jan 15. This gives the VP a real cut at almost no risk.
6. **Dec 1 to Jan 15: chase stragglers.** Offer per-account extensions to named stragglers instead of moving the global date.

## Cut on-call cost without moving the date

- Freeze the v1 code: no features and no refactors.
- Route v1 alerts to tickets, not pages. Page only if v2 or shared infrastructure breaks.
- Give the VP a number: pages from v1 in the last 90 days, with their cost. If that cost is small, the early cut saves little.

## Open question

Do your marketplace customers close their year in early January? If so, Jan 15 may be tight for them too. Ask the top 5 callers when their year-end export runs.

**Next:** run the 180-day query by account and key. Paste the top 10 callers and any month-end spikes. I will turn it into the Nov 20 gate.