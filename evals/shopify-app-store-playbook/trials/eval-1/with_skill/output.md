# Ticketly Shopify App Store go-to-market plan

**Legend:** `†` = published on shopify.dev. Shopify changes these without notice, so re-check the live requirements page before each step. "Reported" = forum or practitioner figures, not Shopify commitments.

## Verdict

**⚠️ As planned, the app is closed to the App Store.** A free app that connects to Ticketly while everyone keeps paying through Stripe is the case Shopify staff rejected (reported). Anything the Shopify integration delivers must be charged through Shopify App Pricing or the Billing API.

**⚠️ The 5-week date cannot include a live listing.** Shopify publishes no review SLA. Plan for 2-3 review rounds and 6-14 weeks to Published (reported). The conference is about 2026-12-05, so it needs a "coming to the Shopify App Store" story, not a live listing.

## Assumptions

I couldn't ask questions, so each gap below has one stated assumption. Correct any that are wrong. Items 4 and 5 change the plan most.

1. The app is an embedded sidebar that reads orders and customers (name and email) to show order lookup inside Ticketly. It needs a Ticketly account to deliver value.
2. Today every Ticketly customer pays $49/agent/month through your Stripe. Some new customers would arrive from Shopify, but I have no count.
3. You are at the building stage, with no existing Shopify app.
4. Nobody needs a real merchant store running the app before approval. If the booth must show a customer's live store, see the custom-app note under Distribution.
5. You have about 3 engineer-weeks for the embedded UI and Shopify billing, and someone who can answer review emails within days.

## Distribution: public app, limited visibility first

- **Rung:** a public app with limited visibility, flipped to fully visible after launch.
  - It goes through one review and installs from its App Store URL.
  - It stays hidden from search until you flip it, and you can switch at any time.
  - This rung wins because assumptions 4 and 5 point to one review and a short engineering budget. A fully visible launch can't happen on your date anyway.
- **Fully visible at approval:** flip it when you want App Store discovery. That fits after approval, not at the booth.
- **Custom app (starved):** promote it only if a real merchant must run the app before approval.
  - A custom app is locked to one store or one Plus organization, skips review, and cannot use Shopify billing.
  - Your 300 customers are 300 separate stores. That means one app per customer, then a second public app and a second review later.
- **Distribution is a one-time choice.** Shopify never lets you switch it, so keep a separate development app and create the production app only when you are ready.
- **Limited visibility does not avoid the billing rule.** It still installs from an App Store URL and gets the same review and billing check.

## Billing plan

1. **Price the Shopify integration as its own line.** A free sidebar is not a plan Shopify will accept.
   - Shopify publishes no formula for splitting a bundled plan. You set the line and explain it in the review notes.
   - Decision for you: what a merchant arriving from Shopify pays for Ticketly plus the sidebar. I haven't invented a number.
2. **Make the Stripe path unreachable from a Shopify install.**
   - A merchant who arrives with no Ticketly account never sees your Stripe checkout.
   - Reviewers fail apps where they can reach it (reported).
3. **Existing customers: get it in writing.** Earlier staff replies said they could keep their Stripe plan, and the latest clarification says no (reported).
   - Open a Partner Support case this week for both questions:
     - Do your 300 existing customers pay the Shopify portion through Shopify?
     - Can your non-Shopify integrations stay on Stripe?
   - Restate the answer in your review notes.
   - Do not rebuild billing or promise customers anything until that answer arrives.
   - Charges for non-Shopify integrations stay on your billing.
4. **Pick App Pricing or the Billing API before you opt in.**
   - App Pricing is the default for a new app: plans live in the Partner Dashboard and Shopify handles the plan page, trials and proration. Once you opt in, you cannot create new recurring Billing API charges†.
   - If you need per-agent usage caps, local-currency prices or one-time charges, choose manual pricing (Billing API) for the whole app instead†. Per-agent pricing is the likely trigger, so settle this in week 1.
   - Merchants must be able to change plans without contacting support or reinstalling.
5. **Pricing text goes only in the Pricing details section** (requirement 4.2†). Keep prices out of images, avoid "billed separately", and don't link to your pricing page. A suspension over "billed separately" wording was reported.
6. **Fees:**
   - $19† one-time registration, which needs a Manage financials role.
   - 0%† on the first $1M† of lifetime gross app revenue earned since 2025, counted across associated developer accounts. After that, 15%.
   - 2.9%† processing plus tax, plus a regulatory fee in some countries.

## Protected customer data

- **Request it before you submit.** Shopify refuses requests while the app is in review, and unapproved fields come back redacted.
- Reading orders or customers is **Level 1**, which needs review.
- Name and email add **Level 2** with data-protection review. Add address and phone only if the sidebar truly shows them.
- Write a one-line reason per field.
- Explain `read_all_orders` in the review notes if you need orders older than 60 days†.

## Submission packet

Roles are placeholders, so assign names.

| Item | Owner |
|---|---|
| Name: "Ticketly Order Lookup" (21 characters). Brand first, category term within 30 characters†, and it must not start with Shopify. Keep "Shopify" out of app URLs and the API contact email. The TOML app name and listing name must be similar. | Marketing |
| Install flow: Shopify-managed install with token exchange, authenticate before any UI, then land in the app. Never ask for a shop domain or send merchants to sign up on your site first. | Engineering |
| App Bridge latest, session tokens (works in incognito and with third-party cookies blocked), GraphQL Admin API only, expiring offline tokens (`expiring=1`) | Engineering |
| Compliance webhooks: customer data request, customer redact, shop redact | Engineering |
| Plan change from inside the app, with charges appearing in the merchant's charge history | Engineering |
| Uninstall then reinstall: OAuth runs again, no duplicate-record errors | Engineering |
| Icon 1200 x 1200 px†; 3-6 screenshots at 1600 x 900 px† of real UI, with no pricing, reviews, browser chrome or Shopify logo | Design |
| Listing copy: subtitle states the merchant benefit with no stats or keywords. Details avoid "first/best/only" and testimonials. Up to five search terms†. | Marketing |
| Test access: step-by-step instructions reaching every feature, plus a Ticketly test account exempt from 2FA, OTP and SSO that keeps working after publish | Support |
| English screencast: install, onboarding, core features, plan change | Product |
| Review notes: why each scope is needed, why a Ticketly account is required, and the Partner Support billing answer | Engineering lead |
| Emergency contact and a support email on file (Shopify does not support third-party apps) | Support |
| One owner on the submission inbox, with `noreply@shopify.com` allowed | Support |

Before pressing Submit, run Shopify's AI self-review. Then install from scratch on a development store, uninstall, reinstall, and change plans.

**Missing test login is the common pause cause.** A missing or SSO-gated login pauses the submission.

## Timeline

Today is 2026-10-31. The dates after submission are estimates built from the reported 6-14 weeks, not Shopify commitments.

| Date | Milestone |
|---|---|
| Nov 2 | Open the Partner Support billing case. Choose App Pricing or Billing API. Request protected-data access. |
| Nov 2-20 | Build the embedded app, billing and webhooks. Use expiring tokens from the start, since non-compliant apps lose listing and new installs after 2027-01-01†. |
| Nov 20 | Complete the packet and self-review. |
| Nov 23 | **Submit.** |
| Dec 5 | **Conference: "coming to the Shopify App Store" with a live demo on a development store.** |
| ~Dec 21 to Jan 4 | Round 1 returned, assuming roughly 30 days per review (reported). Fix every flagged requirement in one pass and resubmit. Resubmitting while queued sends you to the back. |
| ~Jan 20 to Feb 10 | Round 2 returned. Fix again and resubmit. |
| ~Jan 4 to late Feb | Published, if 2-3 rounds hold. Flip to fully visible then. |

**Reading a Paused banner:**
- **No date:** core requirements blocked testing. Fix every flagged item, mark each resolved (the dashboard blocks resubmission until then), then click Submit fixes.
- **A date:** a cooldown, and you resubmit on that date. Triggers are issues unfixed after two exchanges, growing issue counts, silence, or disputing an exemption refusal. Reported cooldowns run 2 weeks to a month.

If the status is Reviewed, answer the reviewer's email. Billing fixes need no resubmission†.

## Booth plan (about Dec 5)

- **Message:** "Order lookup inside Ticketly. Coming to the Shopify App Store." Don't show a listing screenshot or claim availability.
- **Demo:** run it on a development store with seeded orders. Have a backup screencast.
- **Capture:** collect a waitlist of Shopify store URLs and Ticketly account emails from your 300 Shopify-running customers. Tell them install will go through Shopify, and don't promise billing terms until Partner Support answers.
- **Pilots:** onboard them on development stores. If a real store must run it earlier, that is the custom-app trade-off above.
- **Reviews:** don't offer booth swag, discounts or features for reviews, and don't ask only happy users. Shopify removes reviews and demotes or delists apps for that†.

## After launch

- **Reviews:** ask only through App Bridge's `shopify.reviews.request()`, after a real milestone such as a first successful order sync.
  - It shows at most once per 60 days and 3 times a year†, never on mobile, and is never tied to a button.
  - Reply publicly to every review, negative ones first.
- **Ranking:**
  - Published: Built for Shopify and the "increased visibility" achievement boost search†. Keyword-stuffed subtitles and "best" claims are banned†.
  - Reported: an exact phrase in the app title outweighs review count early. Engagement, uninstall rate and install velocity count.
- **Store Ads:** use them for launch weeks only, never as a ranking strategy.
- **Built for Shopify:** apply only when the Partner Dashboard Distribution page shows the prerequisites passing:
  - 50 net installs from active paid-plan shops†
  - 5 reviews†
  - the rating floor
  - admin Web Vitals at p75: LCP 2.5 s, CLS 0.1, INP 200 ms†, with 100 calls in 28 days
  - Blockers for a SaaS connector: an app home that is your web app shown unchanged, workflows left on your site, or a separate sign-up. The contract-based B2B exception applies only if onboarding first asks merchants to connect their existing Ticketly credentials.
  - Failing one criterion three times in a row suspends the application for three months†.
- **Keep the listing:** answer a quality-check email within 7 days† and ship required changes within 30 days†.

## Risks

- **🔴 Billing answer arrives late or says existing customers must pay through Shopify.** Mitigation: ask this week and avoid customer-facing promises.
- **🟠 Review runs past 14 weeks or hits a cooldown.** The conference story doesn't depend on approval.
- **🟠 Protected-data request is slow.** It must be approved before you submit, so start day 1.
- **🟠 Per-agent pricing doesn't fit App Pricing.** It would push you to manual pricing for the whole app, so decide before opting in.

## Decisions I need from you

1. Do you accept that Shopify-arriving merchants and, depending on Partner Support, existing customers pay the Shopify portion through Shopify?
2. What is the Shopify-integration price line?
3. Must any real store run the app before approval? If yes, I'd cost the custom-app route.