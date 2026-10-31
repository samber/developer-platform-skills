# HubSpot pre-ship answer for Asklane: ticket writes and an MCP server

I could not ask you the interview questions, so I made these assumptions. Tell me which are wrong.
- The listed app is built on the developer platform (projects), not a legacy public app.
- It has at least 3 active unaffiliated installs.
- No launch date is set.
- The app has no classic CRM cards.

Every figure marked † (counts, durations, dates, versions) should be checked against the current HubSpot developer docs and changelog before you commit to it.

## Short answer

1. **Your current auth model is the main problem, and it's bigger than either feature.** Your assistant reads a request and decides which CRM actions to take. For that kind of AI, HubSpot requires the app to enforce the installing user's permissions. A standard admin-installed, account-wide OAuth token fails that rule.
2. **You can't add the MCP server to the listed app.** An MCP server lists as its own standalone app with its own listing, app ID and review.
3. **Ticket writes are a listing edit.** They add a scope, a row in the Shared data table, and a new review.
4. **HubSpot allows one app in review at a time.** The two changes must run in sequence, not in parallel.

## 1. The auth problem

- HubSpot's rule is to build on its MCP auth app, or set `isUserLevel: true` on platform 2026.09† or later. A standard OAuth token fails.
- Today, an admin installs your app once. Every rep then acts through the assistant with the admin's reach. A rep who can't write tickets or edit deals in HubSpot could do both by asking your assistant. That is the case the rule exists to block.
- `isUserLevel` covers only some features and APIs†. Before any build work, check whether it covers the tickets write API and the deal property updates you already do ("update the close dates"). If it doesn't cover tickets, the ticket-write feature may not be shippable on your own app yet. I haven't verified this coverage, so don't assume it.
- Moving to 2026.09† is a platform-version migration on an app that is already listed. Check your current `platformVersion` first, because the deadlines below depend on it.
- Your current listing may already be exposed on this point. It may not surface until your next review, so treat fixing it as a prerequisite for both features. Whether HubSpot would act on the existing listing is unknown. Ask your HubSpot contact before the next submission.
- A fixed sync that uses AI upstream is exempt. Yours is not that case, because the LLM chooses the calls at run time.

## 2. Ticket writes (listed app)

Every listing edit goes back through review, so batch changes into one submission.

| Scope (confirm exact name in the scope picker) | Feature | Object | Direction | Required? |
| --- | --- | --- | --- | --- |
| tickets read | Look up tickets in answers | Tickets | HubSpot to app | Optional |
| tickets write | Create and update tickets from the assistant | Tickets | App to HubSpot | Optional |

- Read plus write on an object counts as bi-directional. Add the Tickets row to the Shared data table so it matches the app configuration.
- Mark the ticket scopes optional or conditionally required. Only customers who use Service need them, and a subset-only scope must never be required.
- You must actually use every scope you request, because HubSpot checks your API logs. Don't add speculative scopes.
- Review your existing scopes for the same problem. "Account-wide scopes" in a listed app is where unused-scope rejections come from.
- Sensitive-data scopes are barred for apps with app cards, agent tools or MCP components. Check that nothing you request falls in that group.
- Ticket support is a front-office service use case, which is allowed.
- Update the listing's app features and setup guide, and the demo video or walkthrough for permission use†. Keep scopes and the setup guide frozen once you submit.
- Existing installs will probably have to re-consent to a new scope. I haven't confirmed how HubSpot handles that for optional scopes, so test it on one pilot portal first.
- Ask your support and CS teams to warn customers before the scope prompt appears.

## 3. The MCP server (standalone app)

- **Own app and listing.** Create a new app with its own app ID and OAuth client. Don't add `mcpUrl` to the listed Asklane app.
- **Tension with the "second app" rule.** HubSpot excludes a second app for the same use case, but the MCP listing requirements make MCP an explicit standalone exception. Confirm in writing with HubSpot before building, since the rule text conflicts.
- **Installs gate.** The playbook doesn't say whether the 3-active-install gate† applies to the MCP app. Assume it does until HubSpot says otherwise. If it does, you need 3 unaffiliated portals using the MCP app, and your existing customers are the fastest source.
- **Server requirements:**
  - `mcpUrl` on HTTPS, with no token in the URL.
  - The server must be one you own, or one its owner delegated to you.
  - The component name must name your brand ("Asklane MCP", never "MCP Server").
  - Provide 1-5 plain-language `mcpUseCases`.
  - Every `mcpTools` entry must match the server function name. Any tool that changes data, such as updating a deal close date or writing a ticket, must be `accessType: "write"`.
- **Permissions.** The MCP app must also enforce the installing user's permissions, which is the same issue as section 1. Building on HubSpot's MCP auth app is the supported route.
- **Demo.** The listing needs a demo of configuration, a connection test, and one successful tool call in Breeze.
- **Naming.** "HubSpot" and "Hub" are banned in the name, logo and card names. Write HubSpot with a capital S everywhere.

## 4. Sequencing and timeline

Listing edits go back to review, and a second submission while one is in review is rejected automatically.

1. Check the `platformVersion`, then fix the permission model (user-level or the MCP auth app) and confirm tickets coverage.
2. Submit the ticket-scope edit to the listed app and wait for approval.
3. Submit the MCP app afterward.

- Plan for an initial review of about 10 business days† per submission, plus one possible Draft bounce, counted as another 10 business days†.
- HubSpot says the feedback loop "should take" up to 60 days† from feedback shared. Practitioners report silent weeks after resubmitting; replying to the review email helps.
- Allow for at least two sequential reviews, so roughly 4-8 weeks† before the MCP app can go live. Add pilot time for the MCP app if the 3-install gate applies.
- Announce the features as "coming" until approval lands. Keep MCP pilots under 25† installs while unlisted.

## 5. Deadlines that touch you now

Today is 2026-10-31, so these are close.
- Classic CRM cards had to move to app cards by today†.
- From November 2, 2026†, new listings (including the MCP app) are accepted only on a supported platform version†.
- Legacy public apps are rejected for new listings from November 2, 2026†, and listed ones can be delisted after the September 2027† enforcement date.
- Projects on 2025.2 or older must migrate by March 2027†.
- v4 APIs become unsupported in March 2027†. Calling any v1-v4 API after September 2027† costs certification.
- Use date-based OAuth endpoints†.

## 6. Keep-the-listing checks

- Stay above 3 active installs†. HubSpot can terminate below that 90 days† after publication, and an app not installed in 180 days† is removed.
- Reply to every negative review†.
- Certification is not relevant yet. It needs 6 months listed† and 60 active installs†, and a rejection blocks re-applying for 6 months†. Don't make it a launch goal.

## 7. Questions to answer back

1. What `platformVersion` is the listed app on, and is it a projects app?
2. How many unaffiliated portals are active on it?
3. Does your HubSpot contact confirm that `isUserLevel` (or the MCP auth app) covers tickets writes and deal property updates?
4. Does the MCP app need the 3-install gate? (Ask your HubSpot contact.)

If you answer 1-3, I can turn this into a dated plan with owners.

† Verify against current HubSpot developer docs and changelog.