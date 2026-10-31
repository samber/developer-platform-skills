# Quotely on the HubSpot Marketplace: plan for SaaStock

Figures marked † come from the HubSpot playbook and change often. Verify them against current HubSpot developer docs and the changelog.

## Bottom line

- ❌ **Certified badge by SaaStock is impossible.** Certification opens only after 6 months† listed and 60† active installs. The earliest realistic date is mid-2027, assuming you list in December 2026. A rejected application also blocks re-applying for 6 months†. Don't announce "Certified".
- ⚠️ **A live listing by about Dec 5 is possible but tight.** It works only if you rebuild auth this week and get 3 unaffiliated customer portals actively using the app by mid-November.
- ❌ **The current setup cannot list.** A static-token private app serves one portal and never lists. Your own portal and the dev test account don't count toward the install gate. Two design partners are also one short of the gate.

## Assumptions (you can correct me)

- Quotely is a CPQ that reads and writes quotes against HubSpot deals, and reads contacts and companies. It's a fixed integration, not an AI agent acting on CRM data, so the user-level-permission rule doesn't apply.
- It has no browser extension, no MCP server and no classic CRM cards.
- The platform version is unknown. I assume it's the new developer platform (projects) and need the exact `platformVersion` from you.
- Nobody has seen Quotely's real scope usage, so the scope table below is a guess.

## Eligibility verdict

✅ A CPQ with a real HubSpot workflow is a normal listable app. None of the exclusions apply: no credential brokering, no white-label embedding, no list loading, no restricted industry.

## Do this week (by Nov 6)

1. **Rebuild auth as OAuth with `distribution: "marketplace"`.**
   - Marketplace distribution allows up to 25 installs† before listing.
   - Existing token-based installs (your portal, the test account) must reinstall.
   - Keep the same app ID and OAuth client. HubSpot allows one app per listing.
2. **Confirm the platform version before Nov 2†.** From Nov 2 2026†, new listings need a supported version (2025.2 or later when announced). Build on the newest version. Projects on 2025.2 and older must migrate by March 2027†.
3. **Check API versions and cards.**
   - Use date-based OAuth endpoints†.
   - Use app cards only, never classic CRM cards.
   - Move off v4 APIs before March 2027†.
4. **Cut scopes to what you use today.**
   - Drop tickets and files. HubSpot checks API logs, and unused scopes reject the listing and later fail certification.
   - Adding them later means a listing edit, which goes back to review, plus customer reauthorization. That is cheaper than a rejection.

| HubSpot object | Quotely object | Direction | Scopes | Required? |
| --- | --- | --- | --- | --- |
| Deals | Quotes | Bi-directional (assumed) | `crm.objects.deals.read`, `.write` | Required |
| Contacts | Quote recipients | HubSpot to app | `crm.objects.contacts.read` | Required |
| Companies | Accounts | HubSpot to app | `crm.objects.companies.read` | Required |
| Line items | Quote lines | App to HubSpot | `crm.objects.line_items.write` | Optional, only if you write them |
| Tickets, files | n/a | n/a | none | Not requested until a shipped feature uses them |

Read plus write on deals advertises a bi-directional sync. Mirror every row in the _Shared data_ table of the listing.

5. **Get the pilot to 3 active installs in parallel (see next section).**

## Pilot plan: 3 active installs

Order by efficiency:
1. Existing Quotely customers already on HubSpot, installing the marketplace-distribution app themselves.
2. Your two design partners, each running one real quote-to-deal workflow.
3. A HubSpot Solutions Partner (agency) installing in a client's own portal, with consent.

- **Why the order changed:** your 5-week deadline makes design-partner recruiting run in parallel with the first rung. Start both this week.
- **Line up a third portal plus a spare.** Two design partners never reach the gate, and a partner can drop out.
- **Active means** successful API calls, webhooks or app-card requests in the last 30 days†. OAuth alone doesn't count. Schedule one sync or webhook per portal so activity never lapses.
- **The install counter lags by days**, so install early.
- **Warn pilots in advance.** They'll see an "unverified app" warning and must type "I accept the risk". Only listing approval removes it.

## Submission packet (owners are suggestions)

| Item | Owner |
| --- | --- |
| Allowlist the "HubSpot Crawler" user agent; a blocked URL bounces the listing | CTO |
| Public HubSpot-specific setup guide (install and configure), not behind login and not your docs homepage | CTO / docs |
| Install experience: Seamless install, with an endpoint HubSpot can frame that redirects to `returnUrl` (otherwise installs loop) | CTO |
| Demo video or guided walkthrough of install, configuration and permission use (replaces test credentials†) | CTO |
| Listing fields: name "Quotely" (never "HubSpot" or "Hub"), 800×800 icon without text, ≤8 screenshots with alt text and placeholder data, pricing identical to your website with only plans that include the integration, support email, ToS and privacy URLs | Founder / marketing |
| Choose the Free plan only if you have free-forever or freemium; a free trial alone is not Free | Founder |
| App cards: one primary button per surface, no HubSpot sprocket, no sensitive data | CTO |
| Submit as a Super Admin of the developer account | Account owner |

For copy and screenshots, use `samber/developer-platform-skills@integration-listing-optimization`.

## Timeline back from SaaStock (about Dec 5)

Dates assume the plan holds.

| Date | Milestone |
| --- | --- |
| Oct 31–Nov 6 | OAuth rebuild, version check, scope trim, packet work started, pilot outreach |
| Nov 9–13 | 3 unaffiliated portals installed and a sync running in each |
| about Nov 16 | Submit, with any app-card review done first (a listing resubmitted before app-card approval is rejected) |
| about Nov 30 | Initial review answer (10 business days†) |
| about Dec 14 | Result if the listing bounces to Draft once (another 10 business days†) |

- **If it's approved first pass,** you go live around Nov 30, before SaaStock.
- **If it bounces once, or the third portal slips a week,** approval lands after SaaStock.
- **Decide now what you'll say on stage.** Plan on "HubSpot integration, marketplace listing in review" unless approval has landed.
- **Keep pilots under the 25-install cap** while waiting.
- **Fix every feedback point in one pass.** Freeze scopes and the setup guide during review, and reply to the review email to chase silent weeks.
- **Reuse your pilots.** Keep them installed. They count after listing.

## After listing

- **Stay above 3 installs.** HubSpot can terminate below that 90 days† after publication, and an app not installed in 180 days† is removed.
- **Reviews:** HubSpot's review email starts at day 30. Don't offer incentives, including discounts or gift cards. Reply to every negative review (two replies† per review). Stars show from 10 reviews†.
- **Certification (go/no-go around June 2027):** you need 60† active installs, average API success above 95†%, a verified domain, a security questionnaire, the Uninstall App API and a 3-minute† demo video. Fix 429s, 401s and 403s first. Do it only if enterprise buyers ask or you're aiming for Leading or Premier tier.
- **Tickets and files later:** ship the feature first, then add the scope as an edit to the listing. This returns the listing to review and needs customer reauthorization.

## Questions I need answered

1. Which `platformVersion` is the app on?
2. Do the two design partners already use HubSpot, and are they unaffiliated companies (not investors, friends or partner employees)?
3. Which quote fields does Quotely write back, so I can finalize the scope table?
4. Do you already have a Solutions Partner contact or other HubSpot customers for the third portal?

† Verify against current HubSpot developer docs and changelog.