**Next action: this week, write to HubSpot about the 25-install cap. Do not run `hs app migrate` until you have their answer in writing.**

Your order was migrate, add agent tools, then list. I'd change it in two ways:

- **A gate goes first.** You have about 140 installs and a legacy app. The cap on unlisted migrated apps is 25†, and it may hit you the moment you migrate.
- **The listing shouldn't wait for agent tools.** They carry their own review and the most open questions. Submit the listing once the app cards are approved, then add the tools as an update.

## Assumptions

I couldn't ask, so these are my assumptions. Correct any that are wrong.

| # | Assumption | If wrong |
|---|---|---|
| 1 | "Next quarter" means Jan–Mar 2027. | The dates below shift. |
| 2 | The app uses OAuth, not a static token. | A static-token app serves one portal, so 140 installs can't be true. Tell me what happened. |
| 3 | At least 3 unaffiliated customer portals made successful API calls, webhook requests or app-card requests in the last 30 days†. Pull the evidence this week. | You need a pilot step before listing. |
| 4 | Trackpoint is your own product, not a credential broker, embedded integration or restricted-industry app. | That would be an eligibility refusal. |
| 5 | You haven't audited scopes or API versions yet. | See Phase 1. |

**Eligibility:** nothing in your description is excluded. Field-service scheduling is a service use case, so it qualifies for agent tools.

## Timing facts

- **Legacy apps can't list.** From November 2, 2026†, HubSpot rejects legacy public apps for new listings. That is two days from now. Migration is mandatory, not optional.
- **Classic CRM cards can't list either.** They are banned for new listings†, so they must become app cards.
- **App cards and agent tools exist only on the developer platform (projects),** never on legacy apps. So migration comes first.
- **Target platform version 2026.09†.** It is the latest version I'm aware of, and it supports `isUserLevel: true`, which the agent tools need.
- **Don't chase 2027.03.** It ships in March 2027†. Budget one version migration a year, and the next one comes after you are listed.
- **The cap is the unknown.** Migrating an unlisted app enforces the 25-install cap†, and you have about 115 installs above it. HubSpot's docs don't say what happens to those installs.
- **You can't rehearse the migration.** Legacy public apps can no longer be created†, so there is no throwaway legacy app to test on unless you hold a spare. That makes the written answer matter more.

## Phase 0: this week (Nov 2–6)

1. Open a support request, or write to your Technology Partner Manager if you have one (App Listings > More > View listing details). Quote:
   - the install count: about 140 against the 25 cap†;
   - that you plan `hs app migrate` to 2026.09, then a marketplace listing.
2. Ask these questions:
   - What happens to existing installs above 25?
   - Do new installs error once you are above the cap?
   - Is there a cap exception for an app heading to listing?
   - If migration isn't safe, what is the supported path to list?
   - Can app-card, agent-tool and listing reviews run concurrently?
3. Export the active-install evidence: portal IDs and last-30-day call counts, with your own, test and partner-employee portals removed. Drive one scheduled sync or webhook so activity never lapses.

## Phase 1: Nov–Dec, no migration needed

These are all no-regret work. Run them in parallel while HubSpot answers.

1. **Scope audit.** Compare the scopes you request against the scopes your API logs actually use. HubSpot checks logs, and unused scopes reject the listing.
   - Mark scopes only some customers need as optional or conditionally required.
   - Check for sensitive-data scopes. They are barred for apps with app cards or agent tools.
   - Build the Shared data table now. Read plus write on one object counts as a bi-directional sync.
2. **API version audit.** Find every v1–v4 call. v4 APIs lose support from March 2027†, and any v1–v4 call after September 2027† costs certification. Plan to move off them during the migration.
3. **App-card design.** Replace each classic CRM card with an app card.
   - One primary button per surface.
   - No sensitive data shown.
   - No HubSpot sprocket or other companies' logos.
4. **Submission packet drafts:**
   - Allowlist the "HubSpot Crawler" user agent.
   - Publish a public HubSpot-specific setup guide that isn't behind login.
   - Choose the install experience. You currently install from your own settings page, so "Login via partner site" fits. Seamless install is recommended, but it needs an endpoint HubSpot can frame that redirects to `returnUrl`.
   - Pricing must match your website exactly, with only plans that include the integration.
   - Support email, ToS and privacy URLs.
   - A demo video or guided walkthrough of install, configuration and permission use†.
   - Your name is fine, as long as nothing says "HubSpot" or "Hub".
5. **Warn your customers.** Tell them to expect a reinstall or re-auth, in case the migration needs one. Don't promise anything until HubSpot answers.

## Gate A: the written answer

Decide only after the answer arrives, and re-plan if HubSpot is silent past about Nov 20 (my estimate, not an SLA).

| HubSpot's answer | Action |
|---|---|
| Existing installs keep working and new installs are allowed, or an exception is granted | Migrate in the week of Jan 11. |
| Existing installs survive, but new installs error until listing | Migrate anyway, because legacy can't list. Agree with sales how to pause or waitlist new Trackpoint installs for roughly the review window. |
| Installs above 25 would break or be removed | Do not migrate. Ask HubSpot, in writing, for the supported path. A new app can't simply replace the old one: a second app for the same use case is excluded from listing. Get explicit permission before building one. |
| No answer | Keep chasing. Do not migrate on silence. |

## Phase 2: Jan 11–29, migrate and submit app cards

1. Run `hs app migrate` to a 2026.09† project with date-based OAuth endpoints† and `distribution: "marketplace"`.
2. Immediately check that all installs still show successful calls, and watch for 401s and 403s. Expect some re-auth.
3. Ship the app cards and submit them for review. A listing resubmitted before app-card approval is rejected, so this blocks Phase 4.
4. Verify that no classic CRM card remains.

## Phase 3: Jan 18–Feb 12, agent tools

This runs in parallel with the app-card review.

- **Start small.** Two or three tools are enough:
  - one booking tool, for example "Book field service job";
  - one read tool, for example "Find open technician time slots";
  - optionally a reschedule tool.
- **Naming and descriptions:**
  - Names start with a verb and run 3–7 words, with no company attribution. "Book Trackpoint job" would fail.
  - Descriptions run 50–150 characters†.
  - Front-office use cases only. Service qualifies.
- **Scopes:** every object a tool reads as input needs its `.read` scope in the app's required scopes. No sensitive-data scopes.
- **Permissions:** booking is a write action that Breeze decides to take, so it must respect the installing user's permissions. Set `isUserLevel: true`. It covers only some features and APIs†, so confirm the HubSpot calls your booking flow makes are covered. Also make sure your own backend authorizes by the HubSpot user, not only by a portal-wide token.
- **Submission:** the review form is separate, and it needs a testing video of 3+ minutes† covering the runs you tested.

## Phase 4: week of Feb 15, submit the listing

Submit the listing as a Super Admin of the developer account, once the app cards are approved.

- **Don't hold the listing for agent tools** unless HubSpot says they must go together.
- **Only one app can be in review at a time.** A second submission is auto-rejected.
- **Plan for a bounce.** First feedback should arrive around Mar 2 (10 business days†). One Draft bounce adds another 10† business days, which puts approval around Mar 16–30. A second bounce pushes it into April.
- **Freeze scopes and the setup guide during review.**
- **Announce the integration as "coming"** until HubSpot approves it.
- **Edits return to review.** Adding the agent tools later is a listing update, which costs one more review cycle.

## Phase 5: after listing

- Add the agent tools as an update once their review passes.
- Stay above 3 installs†. An app not installed in 180 days† is removed.
- Reply to negative reviews (two replies† per review). Don't incentivize reviews: no gift cards, discounts or refunds.
- Don't plan certification yet. It needs 6 months listed†, 60 active installs†, a verified domain, a security questionnaire, the Uninstall App API and a demo video. A rejection blocks re-applying for 6 months†. The earliest realistic date is Q3–Q4 2027, by which time the v1–v4 API cutoff in September 2027† matters.
- Tier thresholds (Rising $400K attached MRR† and up) are not a Q1 goal.

## Summary

| When | Step |
|---|---|
| Nov 2–6 | Written ask to HubSpot, active-install evidence |
| Nov–Dec | Scope and API audits, app-card design, packet drafts |
| About Nov 20 | Gate A: written answer on the cap |
| Jan 11–29 | Migrate to 2026.09†, submit app cards |
| Jan 18–Feb 12 | Build and submit agent tools |
| Week of Feb 15 | Submit listing once app cards are approved |
| Mar 2–30 | First feedback and one Draft bounce, then approval |
| After listing | Agent-tool update, then certification planning (Q3–Q4 2027) |

† Verify every HubSpot figure here (counts, durations, dates, versions) against current HubSpot developer docs and the changelog before you rely on it. The week-by-week dates are my estimates, not HubSpot's commitments.