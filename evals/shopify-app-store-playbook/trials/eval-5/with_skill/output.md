# Mailwise: Built for Shopify within 6 weeks

**Verdict:** the 6-week deadline is at risk, and the install and review counts are not the main reason. The app home is the Mailwise dashboard in an iframe behind a Mailwise login. That is a named Built for Shopify blocker, and fixing it is an engineering rebuild. Plan the press push so it does not depend on the badge landing.

Legend: `†` = published by shopify.dev, which changes requirements without notice. "Reported" = forum or practitioner figure.

## Assumptions

These are the questions I would ask. I could not ask, so I assumed:
- The app is published on the App Store, because it has 20 installs and 2 reviews. If it is still in review, the timeline below does not apply.
- Mailwise sells self-serve and is not contract-based B2B. The skill's exception for connecting existing credentials therefore does not apply.
- The app reads customer name and email, and syncs customers or segments.
- The 20 installs are not all on paid plans, and the app has not been through a Shopify quality check yet.
- Nobody has measured admin Web Vitals yet.

## 1. Eligibility gaps (what the Distribution page checks)

| Prerequisite | Required | Mailwise now | Gap |
|---|---|---|---|
| Net installs from active paid-plan shops† | 50 | 20 installs, paid share unknown | 30+ more, and only paid-plan shops count |
| Reviews† | 5 | 2 | 3 more |
| Rating floor | unpublished | unknown | Read the Distribution page |
| Admin Web Vitals at p75† | LCP 2.5 s, CLS 0.1, INP 200 ms, 100 calls in 28 days | unmeasured | The 28-day window must fill with real traffic, so it cannot be compressed |

Installs went from 0 to 20 in 3 weeks. Reaching 50 paid-plan installs in 6 weeks needs about 3 times that pace, and only paid-plan shops count. Reviews can only come as fast as merchants have a real milestone to review.

## 2. Product blockers (the larger problem)

**Reasoning:** the skill lists "an app home that is your existing web app shown unchanged, primary workflows or connection settings left on your site, a separate sign-up" as the SaaS-connector blockers. Mailwise hits all three.

1. **Iframed dashboard as app home.** Rebuild the app home as native embedded UI. It needs the latest App Bridge and session tokens, and it must work with third-party cookies blocked. A cross-site iframe of your own dashboard will likely break there.
2. **Mailwise login.** Merchants must be able to onboard with Shopify credentials. Remove the separate sign-up from the Shopify install path. Authenticate on install through Shopify-managed install with token exchange, then land in the app.
3. **Primary workflows on your site.** Campaign creation, sending and the core settings must work inside Shopify admin. Sending a merchant out to mailwise.com for the main job is a fail.
4. **Email category rules†:**
   - Use Web Pixel extensions, never script tags.
   - Sync customers both ways.
   - Accept Shopify segments.
5. **Plan changes.** Merchants must be able to change plans inside the app without contacting support.

Cheapest scoping: keep the heavy editor on your site only if the reviewer can reach the full job from inside Shopify. I would not rely on that reading. Ask Partner Support before building.

## 3. Billing check

Rule 1 says anything the Shopify integration delivers must be charged through Shopify App Pricing or the Billing API. This includes existing customers and the Shopify portion of a bundled plan (a Shopify staff forum post).

1. Confirm what a Shopify-arriving merchant pays today. If any Shopify merchant can reach Mailwise's own Stripe checkout, that is a review fail (reported) and puts the listing at risk.
2. Price the Shopify integration as its own line, and explain the split in review notes. Shopify publishes no formula.
3. Make the Stripe path unreachable from a Shopify install.
4. For existing Mailwise customers who install the app, get Partner Support's answer in writing. Staff replies conflict on this (reported).
5. Default to Shopify App Pricing. Once opted in, you cannot create new recurring Billing API charges†. Only apps without active paid merchants can opt in†. If the app already has paying merchants, check which model it is on before choosing.

Also confirm that pricing appears only in the Pricing details section. No prices in images, no "billed separately", no link to your pricing page.

## 4. Data

Email apps read customer data, so confirm protected customer data approval is in place. Level 1 covers orders and customers. Name, email, address and phone are Level 2 and need data-protection reviews. Unapproved fields come back redacted. Shopify refuses requests while the app is in review, so file any missing request before resubmitting.

## 5. Getting reviews and installs without breaking rules

- Ask only through App Bridge `shopify.reviews.request()`, after a real milestone such as the first successful send or sync. It shows at most once per 60 days and 3 times a year†, never on mobile. Do not wire it to a button.
- Use neutral wording only. No incentives, no gated features, no filtering for happy users. Shopify removes reviews and demotes or delists apps for it†.
- Reply publicly to every review, negative ones first.
- Store Ads can buy launch-week traffic. Do not treat them as a ranking strategy.

## 6. Timeline

Every date assumes work starts now.

| Week | Action | Gate |
|---|---|---|
| 0 | Open the Distribution page, record each criterion. Ask Partner Support the billing and existing-customer questions in writing. Measure Web Vitals. Check expiring offline tokens. | Written baseline |
| 0-1 | Decide scope: native embedded app home, Shopify-credential onboarding, in-admin core workflow. | Engineering estimate |
| 1-4 | Build and ship the rebuild. Fix Web Vitals. Add the Web Pixel extension and two-way sync. | Installs from a fresh development store pass the whole path |
| 2-6 | Run review requests via the Reviews API at real milestones. | 5 reviews |
| 4-6 | Wait for 50 paid-plan net installs and a full 28-day Web Vitals window on the new UI. | Prerequisites all passing |
| ~6+ | Apply only when the Distribution page shows every prerequisite passing. | Application filed |

Shopify publishes no SLA for the Built for Shopify review. Failing one criterion three times in a row suspends the application for three months†. Never apply early to "see what fails". Status also lapses after 60 days† of failing automated criteria, and annual reviews give you 60 days to fix.

The Web Vitals window starts when real traffic hits the new UI, not when you ship it. A rebuild finished in week 4 gives only about 2 weeks of the 28-day window by week 6. So the badge is unlikely before about week 8-9 even if everything else goes well.

## 7. Listing upkeep that can derail the badge

- Answer any quality-check email within 7 days† and ship required changes within 30 days†.
- Migrate to expiring offline access tokens before 2027-01-01†. Non-compliant apps then lose their listing and new installs, and old tokens get 403 errors from 2027-04-01†. That is about 2 months away, so schedule it with the rebuild.
- If any resubmission is needed, each one slows review† and resubmitting while queued sends you to the back (reported). Plan 2-3 rounds at roughly 30 days each (reported).

## 8. What to tell leadership

1. The badge is a pass/fail check on product shape, not a marketing request. Today's iframe-plus-login setup fails it by design.
2. Six weeks is possible only if the rebuild is done by about week 3-4 and paid installs grow about 3 times faster. Present it as a stretch target.
3. Press options that do not depend on the badge: a launch story about the native Shopify experience, or "applying for Built for Shopify". Do not announce the badge before the Distribution page shows it.
4. Two decisions needed from leadership this week: engineer-weeks for the rebuild, and the Shopify billing split for existing customers.

## Open questions I could not resolve

- Is the app published or still in review? This changes everything in section 6.
- How many of the 20 installs are on paid plans, and what is the current rating?
- Do existing Mailwise customers install the app, and how are they billed?
- Which engineers own the embedded UI, and how many weeks can they commit?