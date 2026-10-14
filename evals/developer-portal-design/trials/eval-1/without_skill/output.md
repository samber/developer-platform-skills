**Start with funnel instrumentation this week. Then fix the earliest stage that leaks, probably credentials-to-first-call. Fix webhooks second. Skip everything that adds signups.**

**Date check:** today is 2026-10-08, so March 15 is about 23 weeks away. I assumed the work window is six weeks and starts about Feb 1. If the review is sooner, the plan below still holds. Week 1 just gets squeezed.

## What the numbers say

- 212 / 1,840 = **11.5%** of signups reach a successful call.
- 1,628 developers stopped somewhere between signup and call. Nobody knows where. That unknown decides the order, so measure it first.
- Your docs, catalog and pricing are public. Many signups are therefore evaluators, not integrators. Some of the 88% were never going to integrate.
- Don't compare 11.5% to any benchmark. No trustworthy public rate exists for this. The only valid comparison is your own number after the fix.

## Order

### Week 1: find the leak (engineer A plus you, about 3 to 4 days)

1. **Instrument seven events per signup**, by account and not just by person:
   1. signup
   2. credentials created
   3. token issued
   4. first authenticated call, any status
   5. first 2xx
   6. webhook endpoint registered
   7. first settlement event delivered and acknowledged

   Your auth and API gateway logs probably hold most of this already. Start there before building anything.
2. **Group failures by error code** for signups from the last 90 days. A pile of `invalid_client`, `invalid_scope` or redirect errors means OAuth is the wall. If there are no calls at all, people never got as far as credentials.
3. **Walk the path yourself, cold.** Use a fresh account and write down every stall. This takes 2 to 3 hours and catches what nobody reports.
4. **Interview 3 who quit and 5 who succeeded.** 30 minutes each. Quitters are harder to recruit but worth more. These counts are a working default, not a standard.
5. **Re-cut the baseline as a 7-day window.** Signup to first 2xx within 7 days, by signup week. The current 11.5% is quarter-wide and mixes cohorts.

By Friday you pick **one** leak. Not three.

### Weeks 2–3: fix the earliest stage that leaks

My bet, as hypotheses only until week 1 confirms them: the biggest drop is credentials to first successful call. OAuth2 has several failure points, and a reconciliation API gives a new developer no bank data to reconcile.

| If week 1 shows… | Fix | Engineer |
|---|---|---|
| Stalls before first token | Auto-issue sandbox credentials at signup. Add a dashboard "copy this curl" with a live token already in it. Make OAuth errors say what to change. | A |
| Token works, no successful call | Add a sandbox seeded with realistic bank transactions and a one-call "reconcile this sample" example. Ship a Postman collection or OpenAPI import and one minimal SDK snippet per language. | A |
| Stalls at webhooks | Add a "send test settlement event" button. Add a delivery log with status and replay. Publish a signature-verification snippet and a local-tunnel guide. | B |

Order logic:
- Earliest leaking stage wins, because every later fix is diluted by losses above it.
- Ability fixes come before motivation fixes. Remove steps, don't rewrite copy.

### Weeks 4–5: second stage plus nudges

1. **Do the next-earliest leaking stage.** Webhooks, if first call is already fixed.
2. **Add stall-triggered emails.** Send them on day 1, 3 and 7, keyed to the last event the account completed. A prompt fixes people who could continue but weren't told how.
3. **Alert your team on stuck accounts.** Flag any company domain with a token but no 2xx after 48 hours. A human can reach out.

### Week 6: measure and write the board story

- Compare the new cohort's 7-day rate against the week-1 baseline.
- Below roughly 30 events in a stage, show the raw counts with dates. Don't show a rate.
- At about 140 signups a week, you get roughly 840 in six weeks. That is enough for first-call rate. It is thin for webhook rate.

## What to skip before March 15

- More top-of-funnel spend or content. It lowers the rate and tells the board nothing.
- Pricing changes. Pricing is public and nothing says it blocks anyone.
- A docs rewrite. Fix the stage that leaks and don't rewrite everything.
- Gating docs. They're already public, and that isn't your problem.
- An SDK in every language. Do one or two, chosen from the signups' stack.

## What to tell the board

- **Metric:** share of new accounts that make a successful call within 7 days, plus median time to first call.
- **Target:** don't commit to a number yet. Set it after week 1, once you know which stage leaks and how much is recoverable.
- **Ownership:** the platform team owns this stage, not DevRel. That is correct, since the fixes are product work.
- **Honest caveat:** the first-call rate should move within six weeks. Webhook-to-production rate probably won't, because there is too little volume and integrations take longer.

## Three answers that would change this order

1. Are the 212 counted by any 2xx or by a real endpoint, like a reconciliation call? If a trivial endpoint counts, the true rate is lower.
2. Do you have a sandbox with seeded data today? If not, it jumps to the top of weeks 2–3.
3. Roughly how many of the 1,840 are from company domains, compared with personal email? That tells you how much of the 88% was never going to integrate.

**Next action (10 minutes):** ask engineer A to run a query on the gateway logs. It should count, for the last 90 days of signups, how many reached each of the seven events. Paste me the counts and I'll name the leak.