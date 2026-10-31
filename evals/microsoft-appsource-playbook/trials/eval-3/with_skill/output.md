# Shiftlane Teams validation: fix order and the 10-day launch date

**Next action:** pick one app name today, before touching anything else. Every other fix and the resubmission wait on it.

## Verdict

- **Free Teams app only:** 10 days is possible but not safe. It works only if the next report comes back clean.
- **Paid or Teams-linked SaaS in the launch:** 10 days is not realistic. See the last section.
- **Date to give marketing:** don't give them "day 10". Give the date the app goes live, plus attestation on that day.

## Assumptions

I couldn't ask questions, so these are my assumptions. Tell me if any is wrong.

- Shiftlane is a free Teams app with no linked SaaS offer yet.
- Publisher Verification is done. If it isn't, it is a Must fix and comes first.
- The two reports list everything that is wrong.
- The bot code and the Partner Center listing are yours to change this week.

## What to fix, in order

Any manifest, screenshot or Partner Center change sends the app back through validation. Batch all the changes below into one resubmission.

1. **Decide the name today: use "Shiftlane" everywhere.**
   - The skill requires the app name to be identical in the manifest and Partner Center. A mismatch fails validation.
   - The name rule bans "Teams" in the name, so "Shiftlane for Teams" would fail on its own. Change Partner Center to match the manifest, not the other way round.
   - Drop "Shifts" as a listing name. Its rule is to prefix or suffix a common noun with your brand ("Acme Tasks", not "Tasks"), so bare "Shifts" breaks it.
   - My inference, not in the skill: "Shifts" is also the name of a Microsoft app, which would make it a clash with an existing app name.
   - Ask marketing to remove "Shifts" as the product name from the listing title, short description and screenshot captions. Plain use of "shifts" as a noun in prose is fine.
   - Check that developer name, descriptions, terms and privacy URLs, and icons match between manifest and Partner Center too.

2. **Remove `staging.shiftlane.io` from `validDomains`.**
   - `validDomains` and `messageHandlers` may list only production domains you control. Check both fields.
   - Keep staging in a separate dev manifest with its own app ID, never in the submitted package. Don't put "Dev", "Beta", "Preview" or "UAT" in the submitted name.

3. **Fix the bot, deploy it to production, then test it.**
   - It must send a welcome message and answer "Hi", "Hello" and "Help". It must never dead-end on irrelevant input.
   - Test all three phrases on desktop, web and mobile. A bot code change alone doesn't re-enter validation, but the testers must see it live when they check.

4. **Audit the rest of the checklist now.** Each failed round costs days, so don't wait for report #3 to find these:
   - Screenshots: at least three, captioned, showing the app inside Teams on each supported client.
   - Description: no bare "Teams", "MS" or "O365", no "#1" or "best", and every external account or admin consent disclosed.
   - Notes for certification: two or more test accounts with no MFA and no need for your team online, setup steps, and a demo video if the flows are complex.
   - Support, privacy and EULA links must resolve without login. Missing links are a top rejection cause.
   - Tab value (the tab must do more than host your website) and mobile (hide unsupported features).
   - Manifest: latest schema. Channel-enabled apps need 1.25 or later for new submissions†.

5. **Resubmit once.** Reply to the concierge email, wait for confirmation, then resubmit.

## Publisher Attestation: stop trying to complete it

- It is a post-listing duty, not a listing gate. A new app can't attest before it is listed, so the form refusing you is expected.
- The Partner Center nag is not a blocker. Do the attestation the day the app goes live, and renew it yearly.
- Put it in the launch-day checklist with an owner.
- If the form still refuses you after the app is live, raise it with Partner Center support.

## Is 10 days realistic?

Today is Saturday 2026-10-31, so day 10 is Tuesday 2026-11-10. That leaves 7 working days.

| Date | Step |
| --- | --- |
| Mon Nov 2 | Decide the name, fix the manifest, bot and listing, deploy the bot |
| Tue Nov 3 | Resubmit |
| ~Wed Nov 4 to Thu Nov 5 | Report #3 arrives (24 working hours† target) |
| Fri Nov 6 | **Best case:** clean report, app live, attest the same day |
| Mon Nov 9 to Tue Nov 10 | **If another "Attention needed":** fix, resubmit, and the next report lands at or after day 10 |

- The skill budgets three to six weeks† for the whole validation, not one day. You are in round 2 already, so the remaining time is probably shorter. That is my inference.
- The 24-hour figure is a target for the report, not for the full fix, reply and resubmit cycle.
- Only a clean third report meets the date. I would call that possible, not likely. Round 2 returned three separate defects, and I can't see whether round 1's issues are all closed.

## If the launch includes paid or Teams-linked SaaS

- Linking needs a live SaaS offer, per-user pricing, and `subscriptionOffer` added to the manifest. That manifest update goes through validation again.
- The SaaS offer needs its own build: landing page, Fulfillment API v2, webhook, Entra SSO, and certification.
- That can't finish in 10 days. Launch the free Teams app on the date, and announce the paid path later.

## What to tell marketing

- "Launch is when validation approves, not a fixed date." Offer Nov 6 as the best case and mid-to-late November as the plan.
- If they must keep Nov 10, ask them to hold it as a soft date and prepare a "coming this week" fallback.

## Questions for you

- What did the first report flag, and is any of it still open?
- Is Publisher Verification complete?
- Is any paid SaaS offer, or a Teams link to one, part of the launch?

† Verify every Microsoft figure in Partner Center before quoting it. Microsoft changes program criteria and timings often.