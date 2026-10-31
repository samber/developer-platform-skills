# Ticketly Chrome extension: launch checklist

**Do first:** fix the manifest before you submit tomorrow. `<all_urls>` plus `tabs`, `cookies` and `scripting` is the combination most likely to trigger a slow, in-depth review or a "excessive permissions" rejection. You can't control how long review takes, so don't make the stage demo depend on it.

## 0. Plan around the review risk

I'm working from my general knowledge of Chrome Web Store policy, not live docs. Re-check the current review-time and policy pages before you commit to dates.

- Typical review takes a few days. Broad host permissions can push it to weeks, and each rejection restarts the clock.
- You have 9 days (SupportConf is Mon 2026-11-09). One rejection could consume most of that.
- **Demo path that doesn't need approval:** load the extension unpacked on the demo machine and a backup machine. Treat store publish as a bonus.
- Don't plan "publish the morning of the talk." Publish as soon as it's approved, ideally 2 or more days early. Store listings and search can take hours to update, and you want time to fix surprises.
- Submit with **deferred publishing** on. Then you control the go-live moment after approval, and you can still publish early.

## 1. Manifest and permissions (today)

1. Confirm Manifest V3. Confirm no remotely hosted code: all JS ships in the package.
2. Remove `<all_urls>` from `host_permissions`. Keep only your own domains there (Ticketly API and app).
3. Move customer portal access to **runtime-granted permissions**. Each customer has a different domain, so:
   - Declare `optional_host_permissions: ["https://*/*"]`.
   - On setup, the agent or admin enters the portal domain. Call `chrome.permissions.request({origins: [...]})` from a user click.
   - After the grant, register the sidebar with `chrome.scripting.registerContentScripts` for that origin only.
   - Persist the granted domains in `chrome.storage`.
   - If you need `https://*/*` as the optional pattern, expect a justification question. Per-origin requests keep the actual grant narrow.
4. Drop `tabs` unless you can name a feature that needs `tab.url` or `tab.title` on origins you don't have host access to. Granted host permissions already expose those for their origins. Consider `activeTab` for click-to-open.
5. Drop `cookies`, or justify it in one sentence. Prefer OAuth or a token in `chrome.storage` for Ticketly auth. Reading cookies is a red flag, and it's worse next to broad host access. If you keep it, scope it to your own Ticketly domain.
6. Keep `storage` and `scripting`. Add `sidePanel` only if you use the Side Panel API.
7. **Lock the permission set now.** Adding permissions in an update can disable the extension for existing users until they re-approve. Reducing permissions later is safe.
8. For enterprise customers, document an admin option. Force-install and pre-grant domains via managed policy so their agents see no prompts.

## 2. Store account (tomorrow morning, before submitting)

- [ ] Developer account registered ($5 fee) under the Ticketly company, not a personal account.
- [ ] 2-step verification on for the account.
- [ ] Publisher/trader info completed. For EU users, trader contact details are shown publicly.
- [ ] Support email and website set. Use a monitored shared address, not a person's inbox.
- [ ] A second owner or group publisher added, so one person's absence on talk day doesn't block you.

## 3. Listing content

- [ ] Single-purpose statement, one sentence: "Show Ticketly customer and ticket context in a sidebar on your support portal."
- [ ] Name, short description (132 chars max) and detailed description. Don't promise features you won't demo.
- [ ] Icon 128×128.
- [ ] 1–5 screenshots at 1280×800 or 640×400.
- [ ] Small promo tile 440×280.
- [ ] Category set, language set.
- [ ] Privacy policy URL, live and specific to the extension.
- [ ] Support URL and homepage URL.

## 4. Privacy tab (common rejection cause)

- [ ] Written justification for each permission. Name the feature that needs it.
- [ ] Data-usage disclosures match the code. The sidebar reads portal page content, which can include end-customer names, emails and ticket text. Declare it honestly, such as personal info and website content.
- [ ] Certify: no selling of data, no use unrelated to the single purpose, no creditworthiness or lending use.
- [ ] Privacy policy covers: what is read from portals, what goes to Ticketly servers, retention, deletion, and who the controller is.
- [ ] Network calls audited: only Ticketly endpoints, over HTTPS. No analytics or third-party SDK that collects page content.
- [ ] Remote-code answer is "No."

## 5. Reviewer access

Reviewers can't see your customers' portals.

- [ ] Add test instructions in the submission.
- [ ] Provide a demo portal URL and a test Ticketly account (credentials in the test-instructions field only).
- [ ] Include step-by-step usage and a short screen recording link.
- [ ] Keep the demo portal and account alive for the whole review window and for resubmissions.

## 6. Engineering checks (before upload)

- [ ] Test on 3–5 real customer-style portals: strict CSP, iframes blocked by `frame-ancestors`, SPA navigation, dark mode.
- [ ] Render the sidebar in a Shadow DOM or an extension-origin iframe so portal CSS can't break it, and the reverse.
- [ ] Verify the permission-grant flow end to end: grant, revoke from `chrome://extensions`, then grant again.
- [ ] Verify the extension does nothing on non-granted origins.
- [ ] Console clean: no errors, no leftover debug logging, no secrets in the bundle.
- [ ] Version number set and the zip built from a clean checkout.
- [ ] Run the package through a final scan for hard-coded keys or staging URLs.
- [ ] Test on a fresh Chrome profile and on a second OS if your agents use it.

## 7. Rollout beyond the stage (400 customers)

- [ ] Staged rollout: publish first as unlisted or to trusted testers, and onboard 3–5 friendly customers.
- [ ] Support-team briefing and an FAQ: "why does it ask for permission to my portal?"
- [ ] Kill switch on the Ticketly backend (feature flag) so you can disable sidebar data without waiting for store review.
- [ ] Monitoring and error reporting without collecting page content.

## 8. Timeline

| Date | Action |
|---|---|
| Sat 10-31 (today) | Fix manifest (§1). Build the permission-request flow. Draft listing and privacy text. |
| Sun 11-01 | Account checks (§2). Upload with deferred publish. Submit. |
| 11-02 to 11-05 | Watch email. Fix and resubmit within hours if rejected. Prep unpacked demo build. |
| Thu 11-05 | Decision point. If approved: publish. If not: commit to the unpacked demo path and tell no one the store is the dependency. |
| Fri–Sun 11-06 to 11-08 | Full demo rehearsal on the actual stage laptop and a backup. Offline fallback: screen recording. |
| Mon 11-09 | Demo. Publish only if already approved and rehearsed. Never push an untested update that morning. |

## 9. Demo-day safety

- [ ] Demo from a known-good unpacked build on two laptops, same version.
- [ ] Demo portal and test account verified the evening before. Wi-Fi fallback: phone hotspot.
- [ ] Pre-grant the portal permission before going on stage so no prompt appears mid-talk.
- [ ] Recorded video of the full flow as a backup.
- [ ] No store submission, update or publish action within 24 hours of the talk.

## Questions that change the plan

1. Which feature needs `cookies`, and which needs `tabs`? If none, drop both and the review gets easier.
2. Do agents enter their portal domain, or can Ticketly's backend supply each customer's domain? The latter allows a cleaner per-customer grant flow.
3. Does the sidebar read page content, or only the URL and a ticket ID? That changes the privacy disclosure.