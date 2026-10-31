# Ticketly Chrome extension: launch checklist for SupportConf (Mon 9 Nov)

**Read this first:** with today's manifest, don't plan on a live store listing by the demo. Plan on a local build for the stage and treat the store publish as a bonus.

- `<all_urls>` plus `tabs` and `cookies` gets the slowest review and the scariest install warning. It also likely triggers **Purple Potassium** (unused or too-broad permission) on the first pass.
- Google states review takes a few days to a few weeks†. Queues hit 3-4 weeks† in April 2026.
- Even a clean 7-day review leaves no room for a rejection round before Nov 9.
- Items marked † are figures or practitioner-reported behaviour. Verify them against current Chrome Web Store docs, which changed the item limit and badges in 2026.

I couldn't ask questions, so I made these assumptions. Tell me which are wrong:
- This is your first publisher account.
- The sidebar is injected by a content script on each customer's portal.
- The sidebar shows Ticketly data fetched from your API, possibly in an iframe of your app.
- `tabs` is used to match the portal URL.
- `cookies` is used to read your Ticketly session.
- You haven't confirmed whether customer IT will force-install the extension.

## 1. Fix the manifest (today, before any submission)

The goal is narrow access. Customer domains are optional and requested one at a time.

```json
{
  "permissions": ["storage", "scripting"],
  "host_permissions": ["https://app.ticketly.example/*"],
  "optional_host_permissions": ["https://*/*"]
}
```

Use your real Ticketly origins in `host_permissions`, and nothing else.

| Item | Decision | Why |
|---|---|---|
| `<all_urls>` | Remove | Replace with your own origins as required hosts. Customer portals become optional hosts. |
| `tabs` | Remove | Host access already exposes URL and title on matched pages. An unused `tabs` is a classic Purple Potassium. |
| `cookies` | Remove | Sign in through your own flow and keep the token in `chrome.storage`. If you truly read a Ticketly cookie, scope it to your own origin and justify it row by row. |
| `scripting` | Keep | Needed for `scripting.registerContentScripts`. |
| `storage` | Keep | Disclose it in the Privacy tab. |

Other manifest rules:
- **No broad `content_scripts.matches`.** `content_scripts.matches` counts as host access, so moving `<all_urls>` there narrows nothing. Register the content script dynamically after the user grants a domain.
- **Request exact origins at runtime.** The extension loads the tenant's portal domain from your API after sign-in. An "Enable on support.customer.com" button then calls `permissions.request` for that origin only, from a user gesture. Don't request `https://*/*` at runtime.
- **Never add a permission for an unshipped feature.** A permission that adds an install warning later disables the extension for every user until they accept. Optional permissions don't.

Open question: does your product need the sidebar to run without any click? If it does, optional hosts mean one Enable click per user. See the force-install section below.

## 2. Permission-to-feature map (paste into the dashboard justifications)

Describe how the extension uses each permission, not what the permission does.

| Permission | Required or optional | Feature | Justification |
|---|---|---|---|
| `https://app.ticketly.example/*` | required | Sign-in and Ticketly context | Signs the agent in to their Ticketly workspace and loads ticket context for the sidebar. |
| `https://*/*` | optional | Sidebar on the customer's own support portal | Requested only when an agent or admin enables the sidebar for their portal's domain. One exact origin is requested at a time. |
| `scripting` | required | Sidebar injection | Registers the sidebar content script on portal domains the user has enabled. |
| `storage` | required | Settings and session | Stores the sign-in token, the enabled-domain list and UI preferences. |

## 3. Privacy tab answers

All three of the Privacy tab, the privacy policy and the code must say the same thing. A mismatch is a rejection.

- **Single purpose (one sentence):** "Shows Ticketly ticket and customer context in a sidebar on the user's own support portal."
- **Remote code:**
  - Answer "No, I am not using remote code".
  - All logic must ship in the package. No CDN scripts, no `eval` of fetched code, no SDK that lazy-loads scripts.
  - An iframe showing your web app is exempt, but describe it in the single purpose and justifications.
  - Check that no analytics or error-reporting SDK lazy-loads scripts (**Blue Argon**).
  - Minify at most, never obfuscate (**Red Titanium**). Target modern Chrome.
- **Data types:** tick everything the code collects, stores locally or sends.
  - Include analytics, error reports and any `chrome.storage.sync` use.
  - **Page URLs count as browsing activity.** Say whether portal URLs or ticket IDs are sent to Ticketly, and tie that to the sidebar feature.
  - Disclose before collecting, get consent, send over HTTPS only (**Purple Nickel**, **Purple Magnesium**, **Purple Copper**).
- **Limited Use:** certify all three statements. Publish this sentence on your own site: "The use of information received from Google APIs will adhere to the Chrome Web Store User Data Policy, including the Limited Use requirements."
- **Privacy policy URL:** a working page that is not the listing description and says what the extension collects (**Purple Lithium**).

## 4. Test instructions (the most common avoidable rejection)

The sidebar only appears on a support portal, so the reviewer needs one. A login wall with no credentials returns **Yellow Magnesium**.

- A permanent seeded demo tenant. No SSO, MFA or expiring trial.
- A live demo portal URL with seeded tickets, so the reviewer can see the sidebar.
- Credentials in the Test instructions field only.
- Server allowlists open to any IP.
- Numbered steps, ending with the enable-domain permission prompt.
- A video walkthrough link.
- An "account required, sign in" state inside the extension.

Template:

```
Account: reviewer@ticketly-demo.example / <password in this field only>
Tenant: permanent demo workspace, seeded with sample tickets; no SSO, no MFA, no expiry.
1. Click the toolbar icon and sign in.
2. Settings > Portals > Enable on demo-portal.ticketly-demo.example, accept the host permission prompt.
3. Open https://demo-portal.ticketly-demo.example/ticket/42; the Ticketly sidebar appears.
Server allowlists accept any IP. Video walkthrough: <URL>
```

Before uploading, test the packed CRX, not only the unpacked folder.

## 5. Account and listing checklist (start today; some of it may take days)

1. Create a dedicated company mailbox for the developer email. It never changes later.
2. Turn on mandatory 2-Step Verification.
3. Declare Trader status with company details. These are shown publicly in the EU.
4. Add teammates as members with roles. Never share one login.
5. Know your slot limit: new publishers get two extension slots† by default. Ticketly needs one, so you're fine, but don't plan a second item.
6. Complete the listing: icon, screenshots, description (a missing one returns **Yellow Zinc**). For listing copy, use `integration-listing-optimization`.
7. Build the package in CI with the manifest at the root and a version higher than the last. Fix any pre-submission install test failures before submitting.
8. **Untick auto-publish.** An approved build waits up to 30 days†, then reverts to draft.

Account security, as soon as the first version publishes:
- Opt in to **Verified CRX Uploads** and keep the private key in CI secrets, never in the Google account. A lost key takes up to a week† to replace.
- Publish from CI through the Chrome Web Store API with a dedicated service account, not a person's OAuth token.
- Restrict third-party app access in your Workspace, and alert on any published version CI didn't produce.
- Keep a rollback runbook. Rollback republishes the previous version under a new version number within minutes, with no review.

## 6. Timeline back from Mon 9 Nov

Assume one rejection round. The honest outcome is that approval before Nov 9 is possible but unlikely.

| Date | Action |
|---|---|
| Sat 31 Oct (today) | Rewrite the manifest, build the optional-host flow, open the publisher account. |
| Sun 1 Nov | Finish test tenant, demo portal and privacy policy. Submit with auto-publish unticked. |
| Mon 2 - Wed 4 Nov | Wait. **Don't cancel and resubmit.** Google staff warned in 2026 that cancelling resets your queue position†. Cancel only to replace a broken package. |
| Thu 5 Nov (decision point) | If still pending, the local build is the demo, full stop. If rejected, fix every cited point in one resubmission. |
| Fri 6 Nov | Freeze the stage build and rehearse on the stage laptop. |
| Sun 8 Nov | If approved, publish. Don't rely on a morning-of publish: I can't confirm from the skill how fast a published listing becomes visible, so leave margin. |
| Mon 9 Nov | Demo. |

Escalate to Chrome Web Store support only after three weeks† pending.

## 7. Stage plan (independent of the store)

- Load the unpacked or packed build into a clean Chrome profile on the stage laptop.
- Pre-enable your demo portal domain and pre-sign-in to the demo tenant.
- Keep a screen recording as backup in case conference wifi fails.
- Say "coming to the Chrome Web Store" unless the listing is live and visible to you on Nov 8.

## 8. Customer rollout (the 400 customers)

- **Default:** one public or unlisted item for every tenant. Your brand is in the store, and the extension loads each tenant's portal domain after sign-in. Customer IT can force-install it by extension ID with any browser management tool.
- **Force-install and optional hosts:** force-install grants required permissions silently, but optional hosts still prompt each user. If customer IT wants zero clicks, choose between one Enable click per user and a per-customer build. Test the choice on a managed profile before promising customers.
- **Per-customer builds:** 400 builds would mean 400 reviews and 400 items. Avoid them unless a contract requires the customer's name in Chrome, then use an unlisted white-label build with the labelled text.
- **Never publish one public listing per customer.** It's banned as repetitive content and can cost the account.

## 9. If it goes wrong

- **Rejected:** the live version stays, if any. Fix every cited point in one resubmission. Clarify with support first, then appeal each violation once† with the permission-to-feature map, code references and a screen recording. A frivolous appeal can cost future appeal rights.
- **Warning:** 7-30 days† to ship a fix while the item stays live.
- **Takedown:** the listing 404s. Ship the fix through a normal submission.

Appeal template:

```
Item: <extension ID>, violation <ID>, version <x.y.z>.
The flagged <permission or code> is used by <feature>: <file:line>.
User flow: <steps>, recording: <URL>. Test account: see Test instructions.
We request reinstatement of version <x.y.z>.
```

## Open questions that change this plan

1. Why does the extension use `cookies` and `tabs`? If a real feature needs them, I'll rewrite the justifications instead of dropping them.
2. Does the sidebar have to run with no click? If so, we need to pick between the Enable click and the per-customer build.
3. Do your customers manage Chrome through Google Admin? If yes, private publishing is an option. Whether private or unlisted items count against the item limit is undocumented, so ask support before scaling it.
4. Is Nov 9 a hard "live in store" requirement for marketing? If yes, move the announcement to "coming soon".