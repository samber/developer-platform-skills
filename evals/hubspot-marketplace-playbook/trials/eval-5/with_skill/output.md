**Next action:** open the HubSpot developer account and run an API log query for contact calls on `HubSpot Sync by Fieldnote` over the last 30 days. That query decides fix 1.

## Assumptions

These are my own guesses. Correct any that are wrong.

1. Sync is a developer-platform (projects) app on platform version 2025.2† or later, with no classic CRM cards. If it is a legacy public app, stop. HubSpot rejects legacy apps for new listings from 2026-11-02†, which is Monday. Go to the legacy route instead.
2. "One-way to HubSpot" means your app writes contacts into HubSpot.
3. Fieldnote Forms is a different use case from Sync. It has its own app ID and OAuth client, and you have not submitted it.
4. Forms has not yet reached 3 active installs.

## Fix all four in one pass

Keep scopes and the setup guide frozen after you resubmit.

**1. Contacts scope mismatch**

HubSpot checks your API logs. Read plus write on an object means a bi-directional sync, so your Shared data row has to match the scopes you request.

- If the logs show only writes, drop `crm.objects.contacts.read`. Mark the row "App to HubSpot".
- If the logs show real reads, keep both scopes. Change the row to "Bi-directional" and rewrite the listing copy to say so.
- Search and dedupe lookups before an upsert count as reads. A scope that never appears in the logs fails the review.
- If only some customers need contacts, mark the scope optional, not required.
- Removing a scope is safe for installs. Adding one makes existing pilot installs re-consent. Tell your pilots.

**2. Pricing shows Starter**

- Delete Starter from the Pricing tab.
- List only plans that include the integration, priced exactly as on your website.
- Make the website pricing page say which plans include the integration. If the two differ, HubSpot bounces the listing again.

**3. Setup URL not accessible**

You have two faults: the URL is behind SSO, and bot protection blocks the crawler.

- Publish a new public page, "Set up Fieldnote Sync with HubSpot". It must not be the docs homepage and must not need login. For listing it needs install and configure steps.
- Put that URL in the Setup documentation field.
- Allowlist the `HubSpot Crawler` user agent in your bot protection. HubSpot crawls every listing URL: setup guide, support, ToS, privacy and demo.
- Test from a network outside yours, with no cookies, using the exact user-agent string from HubSpot's docs. Check the response body for the real page, not just the status code. Many bot challenges return 200 with a challenge page.
- Keep each URL field at 250 characters or fewer†.
- Replace testing credentials with a demo video or guided walkthrough of install, configuration and permission use†.

**4. Branding**

The app name breaks rule 6: never put "HubSpot" or "Hub" in an app name, logo or app-card name.

- Rename the app to your brand, for example **Fieldnote Sync**. Change it in the app config and the listing together.
- Remove "HubSpot" from the tagline too. Say what the customer gets from connecting, for example "Syncs Fieldnote notes to HubSpot contacts".
- Search the listing, app-card names, screenshots, setup guide and website for "Hubspot" or "HUBSPOT". Write HubSpot with a capital S.
- Check the icon: 800x800 px† JPG or PNG, filling the square, no text or wordmark, no HubSpot sprocket or other companies' logos.
- Remove any statistics from the listing unless you link a case study.
- I could not confirm from the playbook how a rename affects existing pilot installs. Test it on one pilot portal.

## Free plan: no

The 14-day trial does not make the plan Free. Free is only for free-forever or freemium plans. A Free entry that your website does not show as free is a price mismatch, and HubSpot bounces it again. List your paid plans that include the integration, at their website prices. Mention the trial only if the plan description field allows it, and only if the website says the same.

## Second app: cannot queue both

Rule 5 says one app is in review at a time, and HubSpot rejects the second submission automatically. If you submit Forms now, your Sync resubmission may be rejected as the second submission.

1. Fix and resubmit Sync first.
2. Meanwhile, build Forms as `distribution: "marketplace"` with OAuth from the first pilot. It installs in up to 25 accounts† before listing.
3. Recruit 3 unaffiliated customer portals for Forms, plus a spare. Sync installs do not count for Forms, because each listing has its own app ID. This is my inference, not a stated rule.
4. Drive one scheduled sync or webhook per portal so the 30-day activity never lapses. OAuth alone is not activity.
5. Submit Forms only after Sync is approved and Forms has 3 active installs.
6. Check one excluded case. HubSpot refuses a second app for the same use case, and a listing that redirects to or needs another app. If Forms duplicates Sync's use case, fold it into the Sync listing.

## Timeline

These dates assume 10 business days† per review and ignore holidays.

- Fix work: about 1 working day, mostly the setup guide. Done Thu 2026-11-05.
- Resubmit Sync: Fri 2026-11-06.
- Sync decision: about Fri 2026-11-20 if it passes.
- Sync decision if it bounces once more: about Fri 2026-12-04.
- Forms submission: Mon 2026-11-23 at the earliest.
- Forms decision: about Mon 2026-12-07 if there is no bounce. Add 10 business days per bounce.
- If HubSpot is silent after you resubmit, reply to the review email to chase.
- The 60-day† feedback-loop limit starts when HubSpot shared the feedback.

## Deadline checks before Nov 6

- A resubmission after 2026-11-02† needs a supported platform version.
- Classic CRM cards had to move to app cards by 2026-10-31†, which is today. If Sync has any, migrate them. A listing resubmitted before app-card approval is rejected.
- Platform 2025.2 and older: migrate by March 2027†.

† Verify every HubSpot figure (counts, durations, dates, versions) against current HubSpot developer docs and changelog.

**Questions for you (answer to tighten the plan):**

1. Is Sync on the developer platform, and which `platformVersion`?
2. How many unaffiliated portals are active on Forms today?