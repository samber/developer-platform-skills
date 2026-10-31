# Quotely on the HubSpot Marketplace: plan for SaaStock (5 weeks)

I wrote this from memory of HubSpot's program rules, with no live lookup. Numbers marked ⚠️ change often, so check them on the current HubSpot listing and certification pages in week 1.

## Verdict

- ❌ **Certified badge by SaaStock is not realistic.** It needs a live listing and a minimum count of active installs from real customer accounts. It also needs reviews and API-health history. Your own portal, a dev test account and two design partners don't get there.
- ⚠️ **A live Marketplace listing in 5 weeks is possible but tight.** Your current setup blocks it, and you have to fix that first.
- 🎯 **Target for SaaStock:** a listed app, or a submitted app with review underway. For the badge, show a dated roadmap to Certified.

## Blocker 1: static token auth

A private app with a static token is bound to one account. HubSpot can't list it, because customers can't install it.

- Move the app to OAuth, set to distribute to multiple accounts, with redirect URLs.
- Rework token storage: per-install access and refresh tokens, with refresh handling.
- Handle the install, uninstall and reinstall flows.
- This is the critical path. Everything else follows from it.

## Blocker 2: scopes

HubSpot reviews requested scopes against what the app actually uses.

- Tickets and files scopes you don't use today are a likely rejection reason.
- **Required scopes:** contacts, companies, deals only.
- **Tickets and files:** leave them out, or declare them as optional if the new platform lets you. Add them in the release that ships the feature.
- Adding a required scope later forces existing installs to re-consent. Optional scopes avoid that. Decide this now.
- Confirm in the current docs how required vs optional scopes behave. Keep a one-line justification per scope for the review form.

## Blocker 3: active installs

- Listing requires a small minimum of active installs from accounts that aren't yours. ⚠️ I recall about 3. Check the current number.
- Your own portal and the dev test account don't count.
- Two design partners is one short, and installs must stay active. Recruit a third and a fourth now. Get all of them onto the OAuth build as soon as it's ready.

## Timeline

| Week | Work | Exit check |
|---|---|---|
| 1 | Confirm current listing and certification requirements. Start the OAuth migration. Trim scopes. Draft the privacy policy, terms and support channel. | Written checklist of listing requirements |
| 2 | OAuth works end to end. Install and uninstall flows. Reinstall design partners on the OAuth build. Recruit installs 3 and 4. | A clean install on a fresh test account |
| 3 | Listing assets: description, screenshots, demo video, setup docs, support email or page. Check API error handling and rate limits (certification looks at API health). | Listing draft complete |
| 4 | **Submit for review.** Keep the test account and credentials ready for the reviewer. | Submission accepted into the queue |
| 5 | Answer reviewer feedback within a day. Prepare SaaStock messaging for whichever outcome you reach. | Listed, or in review with a clear status |

Review turnaround is outside your control. Submit by the end of week 3 if you can.

## SaaStock messaging

- **If listed:** "Now on the HubSpot Marketplace."
- **If in review:** "Available to HubSpot customers now (direct install link). Marketplace listing in review."
- **Don't claim the Certified badge** until HubSpot grants it. Say "pursuing HubSpot certification" at most.

## Path to Certified, after launch

1. Get the listing live.
2. Grow active installs toward the certification minimum. ⚠️ I recall it being in the dozens.
3. Collect marketplace reviews from design partners and early customers.
4. Keep API error rates and latency healthy, and monitor them from day one.
5. Ship the tickets and files features, then add those scopes.

## Decisions I need from you

1. Do you have a third and fourth customer or friendly account who can install within 2 weeks?
2. How much of the app is built on the static token? That sets the OAuth effort. Is it one service or spread across several?
3. Does the new platform let you declare tickets and files as optional scopes? You can check this in week 1.

**Next action today:** open HubSpot's current marketplace listing requirements and certification pages. Write down the exact install minimum, scope rules and review steps. Then start the OAuth migration.