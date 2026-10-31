# Which listing first: the GitHub App on Marketplace. The Copilot Extension listing no longer exists.

Figures marked `†` come from the playbook. Check them against current GitHub Marketplace docs before anyone plans around them. I read the playbook and its reference file only. I did not check GitHub's live docs.

## Answer

1. **Do the GitHub App listing first.** It is the only one of the two that can ship.
2. **Don't plan a Copilot Marketplace listing for next month.** GitHub App-based Copilot Extensions ended on 2025-11-10†, along with their Marketplace category. Build the AI team's work as an MCP server instead. See `samber/developer-platform-skills@mcp-server-offering`. If the AI team means a VS Code Copilot extension, see `samber/developer-platform-skills@ide-extension-offering`.
3. **Free-only is the riskiest way to list the app.** The reason is below. You should decide before submitting whether to list free and accept that risk, or list with a paid plan.

## Assumptions

I could not ask, so I made one assumption per gap:

- **Ownership:** the app is public and owned by an organization. If a personal account owns it, transfer it first (app settings > Advanced).
- **Capacity:** you have 2–4 engineer-weeks for `marketplace_purchase` handling. A free listing still requires it.
- **Buyers:** they pay by card on Stripe today. Any enterprise or invoiced customers are unknown.
- **Launch:** no event is pinned to a date.

If capacity is zero, list nothing yet. Keep the app unlisted and public, with your own Install button. That path needs no review and no fee, but customers find it only through your docs.

## Why free-only is risky

- **Install count:** 150 installs is above the 100† threshold for paid plans. GitHub documents two notes on free plans for products sold elsewhere. One bans them. The other tolerates them until the paid-plan requirements are met, and you have now met the install requirement.
- **Enforcement:** large vendors list free-only and no enforcement is documented. A new submission still carries the risk, so plan the paid plan.
- **Listing copy:** you may not steer users away from GitHub in the listing. Copy that sends people to your Stripe checkout is the likeliest way to get rejected.

## What each option costs

| Option | Effort | Cost | Billing stays on Stripe? | Main risk |
|---|---|---|---|---|
| Unlisted public app | Near zero | None | Yes | No Marketplace search, so no discovery. |
| Free listing | Purchase and cancel handling, Setup URL flow, 30-day† data deletion, assets, onboarding review | None | Yes | Free-plan policy risk above. |
| Paid plans on Marketplace | Publisher verification, full billing flows, financial onboarding | 5%† fee; payouts only once a month reaches $500† | No, GitHub bills those buyers | Two entitlement sources to reconcile. Published prices are permanent. |

I recommend the free listing, with the policy risk accepted and the listing copy kept neutral. You asked for discovery with all billing on Stripe, and the free listing is the only option that gives you both. Revisit the paid plan if card-paying teams start self-serving through Marketplace.

## Gates before you submit

| # | Gate | Owner |
|---|---|---|
| 1 | App installable by any account, public and generally available | Engineering |
| 2 | An organization owner creates the listing (the GitHub App manager role cannot) | Org owner |
| 3 | Integration goes beyond sign-in (GitHub rejects apps that only authenticate) | Engineering |
| 4 | Support URL, privacy URL and named contact emails filled in | Product |
| 5 | Setup URL set, buyer identified through the user OAuth flow | Engineering |
| 6 | `marketplace_purchase` handling: `purchased` and `cancelled` at minimum | Engineering |
| 7 | Webhook signature check, dedupe by delivery ID, daily sync against `GET /marketplace_listing/plans/{plan_id}/accounts` | Engineering |
| 8 | On `cancelled`: deactivate, revoke the token, delete customer data within 30 days† | Engineering |
| 9 | Listing copy to GitHub's field rules: 150–250 character intro starting with the app name, 3–5 value propositions, "people" or "teams" instead of "users", logo at least 200×200 px, up to five screenshots at least 1,200 px wide | Product |
| 10 | Test on a second public development app with a draft listing, never on the live one | Engineering |

Adding paid plans to a live free listing triggers verification and financial onboarding again. Budget a second review if you go that way.

## Timeline

Review time is not published. The playbook says to plan eight weeks for a free listing.

- **Now, 2026-10-30 to about 2026-11-13:** build billing-event handling and test it on the development app.
- **About 2026-11-13:** click "Request publish".
- **Around 2027-01-08:** realistic approval at eight weeks.
- **Four weeks of silence:** open a GitHub Support ticket with the app name, app ID, owner and submission date. File it under Billing or Account. Never click "Withdraw request", because practitioners report it resets your place.

Make sure the Install button works on your own site before then. If the listing is late, announce the app as "coming to GitHub Marketplace" and list it on approval.

## Enterprise buyers

Invoiced enterprises cannot buy paid apps through GitHub. In any enterprise, only an enterprise owner who is also an org owner can buy, through the enterprise account. Your Stripe path stays the contract route for them, which is another reason a free listing fits you.

## Copilot work next month

- **Don't file or announce a "Copilot Extension listing".** The category is gone.
- **MCP server:** build it, and treat it as its own offering with its own distribution. See `samber/developer-platform-skills@mcp-server-offering`.
- **Wording:** if the AI team promised a Copilot-category listing internally, correct that expectation now.

## Questions only you can answer

1. Do you have engineering capacity for billing-event handling? If not, stay unlisted.
2. Are any customers enterprise or invoiced buyers?
3. Does the AI team mean the MCP server, or a VS Code Copilot extension?