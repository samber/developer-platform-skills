# HubSpot listing fixes for HubSpot Sync by Fieldnote, and the Fieldnote Forms submission

I didn't open the repo, `skill-wip/`, or HubSpot's current docs. HubSpot specifics below come from general knowledge, so check them against their branding and listing requirements before you resubmit.

## Answer to the Free question

**No, don't set the plan to Free.** Free means no payment is ever needed. A 14-day trial still ends in a paid plan, so Free would misstate your pricing and likely get a second bounce.

List your real paid plan with its real price. Put "14-day free trial" in the plan description or feature text.

## Fix order

1. Fix the setup URL (item 3). It blocks everything else.
2. Fix the scopes and the Shared data declaration (item 1).
3. Fix pricing (item 2).
4. Rename the app and clean up branding (item 4).
5. Resubmit. Submit Fieldnote Forms the same day, after the same checklist.

## 1. Scopes versus Shared data

HubSpot checks that the scopes you request match the data flow you declare. You request contacts read and write but declare one-way, so one of the two is wrong.

Search your code for every HubSpot contacts API call, then decide:

| What the code does | Fix |
|---|---|
| Only creates or updates contacts in HubSpot | Remove `crm.objects.contacts.read`. Keep write. Batch upsert by email works with write only. |
| Reads contacts too (dedupe lookups, search, sync back to Fieldnote) | Keep both scopes. Change Shared data to two-way and say what you read and why. |
| Reads only in an optional feature | Move read to optional scopes. Document which feature needs it. |

- Search and list calls need read. If you use them to dedupe, you are two-way.
- Changing scopes forces existing installs to re-authorize. Plan a customer notice and a release note.
- Make the consent screen, Shared data, setup doc, and privacy policy all say the same thing.

## 2. Pricing

List only plans that include the HubSpot integration. Remove Starter.

- Match plan names and prices exactly to your public pricing page.
- Make that pricing page reachable without login or a bot challenge (see item 3).
- If Starter customers ask, say in the setup doc that the integration requires the paid plan. Don't list Starter as a listing plan.

## 3. Setup documentation URL

Your docs homepage sits behind SSO, and your bot protection challenges automated and unfamiliar visitors. A reviewer sees a redirect or a challenge page, so the URL "could not be accessed". A homepage is also not a setup guide.

1. **Publish** a public page for this app only, for example `/docs/hubspot-setup`. No login, no SSO redirect.
2. Include these sections:
   - Prerequisites (HubSpot plan, Fieldnote plan, admin rights).
   - Connect steps, with screenshots.
   - Why each scope is requested. This also supports item 1.
   - Field mapping and sync direction.
   - Troubleshooting.
   - Disconnect and uninstall.
   - Support contact.
3. **Exclude that path** from bot protection with a WAF rule that skips the challenge for it. Don't turn protection off site-wide. HubSpot reviewers don't come from a published IP list, so a path rule is safer than an IP allowlist.
4. Apply the same exemption to your pricing, privacy, terms, and support URLs.
5. **Test** from a clean network with no cookies. Run `curl -sIL <url>` and expect `200` with no `302` to an SSO host and no `403` or challenge page. Also open it in a private window on a phone hotspot.
6. If reviewers need to log in to your product, give them a demo account in the submission notes. Don't use the docs URL for that.

## 4. Branding

"HubSpot Sync by Fieldnote" almost certainly breaks the rule. HubSpot's guidelines, as I know them, don't let partner app names start with "HubSpot" or imply HubSpot made the app.

- **Rename** to a form such as "Fieldnote for HubSpot" or "Fieldnote Sync for HubSpot". Your brand comes first, and "for HubSpot" is the descriptive part.
- Use your own logo as the app icon. Don't use the HubSpot sprocket or a recolored version of it.
- Write "HubSpot" with that exact capitalization in the listing copy, screenshots, and docs.
- Don't use language that suggests HubSpot endorses, certifies, or built your app.
- Update the new name everywhere: app settings, listing, setup doc title, OAuth consent screen, in-app UI, and website.

## 5. Fieldnote Forms

Submit it now only if it passes this checklist. Otherwise it will bounce for the same four reasons.

- [ ] Requested scopes are the minimum, and they match the declared Shared data.
- [ ] Pricing lists only plans that include the integration.
- [ ] Its own public setup page exists, outside SSO and bot protection, and returns 200 from a clean curl.
- [ ] Name and icon follow HubSpot's branding rules.
- [ ] The description says it is by Fieldnote and not HubSpot's own Forms tool. "Forms" is also a HubSpot product name, so there is a small confusion risk.

Forms probably needs different scopes, such as forms access and contacts write. Decide them from its code, not by copying the first app.

I can't confirm how HubSpot's review queue treats two submissions at once. Resubmitting the first app and submitting Forms the same day, both clean, is the safest sequence.

## Resubmission note for HubSpot

> Thanks for the feedback. We have: (1) aligned requested scopes with the declared data flow [one-way: removed contacts.read / two-way: updated Shared data to two-way]; (2) removed the Starter plan from pricing, so only plans that include the integration are listed; (3) published a public setup guide at [URL], reachable without login and exempt from bot protection; (4) renamed the app to [new name] and replaced the icon to follow your branding guidelines.

Fill in the bracketed choices from item 1 before sending.

## What I need from you

1. Does the app ever read HubSpot contacts, including search, dedupe, or sync back? That decides item 1.
2. What name do you want: "Fieldnote for HubSpot" or another form?