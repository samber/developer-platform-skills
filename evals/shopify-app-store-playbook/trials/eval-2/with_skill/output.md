# Shopify inventory sync: pre-kickoff review

**Verdict: don't start Monday on this plan.** The flip from custom to public doesn't exist. Shopify locks the distribution method when you create the app, so the Q1 flip is a second app. Fix the plan before engineering starts, or the Q1 date quietly turns into a rebuild.

Legend: `†` is a shopify.dev figure that Shopify changes without notice. "reported" means a forum or practitioner figure, not Shopify-published.

## Assumptions

Skipped the interview, so each gap gets one assumption. Tell me which are wrong.

1. The app reads inventory, locations and orders, so it needs protected customer data Level 1. It doesn't read customer name, email or address.
2. Your customers pay you by contract or invoice (or Stripe), not through Shopify.
3. The three brands are three separate Plus organizations, not one. Custom apps serve one store or one Plus organization, so this would mean three custom apps.
4. The brands need to run it on live stores **before** any App Store approval could land.
5. Build effort is about 6 engineer-weeks for embedded UI plus Shopify billing, with someone answering review emails within days.

## Concerns, most serious first

### 1. "Custom first, public later" is a different app
- Shopify never lets you switch distribution method†. Custom apps skip review, can't use Shopify billing, and never list.
- "Flipping" in Q1 means a second app, a second review (6-14 weeks reported), and the three brands uninstalling and reinstalling.
- The feedback you collect in Q1 is still useful. The custom app's install, auth and billing paths are not.
- Fix: build one public-grade codebase from day one. Use the latest App Bridge with session tokens, GraphQL Admin API only, expiring offline tokens, and Shopify-managed install. The custom app is then a throwaway configuration of the same code.
- Keep a separate development app so the lock lands on the production app.

### 2. Your billing plan has to change
- Anything the Shopify integration delivers must be charged through Shopify App Pricing or the Billing API.
- A Shopify staff forum post (reported) applies this to existing customers and to the Shopify portion of a bundled plan.
- It also rejects "free connector into our paid service".
- Earlier staff replies said existing customers could keep their own billing. The latest says no (reported). Get Partner Support's answer in writing before you rely on either.
- Price the Shopify integration as its own line, and write down how you set it. Shopify publishes no formula for splitting a bundled plan.
- Make your own checkout unreachable from a Shopify install.
- Default to Shopify App Pricing. Choose manual pricing (Billing API) for the whole app instead if you need local-currency prices, usage caps† or one-time charges†. Decide before opting in, because opting in can't be undone†.
- Keep pricing only in the Pricing details section. No prices in images, no "billed separately", no links to your pricing page. A suspension over "billed separately" wording was reported.
- Fees: $19† registration, then 0%† on the first $1M† of lifetime app revenue, then 15%. Add 2.9%† processing plus tax.
- The three pilot brands may see a price change when they move from the custom app to the public app. Warn their account owners now.

### 3. The Q1 date has no slack
- Your first fixed date is submission, after about 6 weeks of build. Assume Monday Nov 2 kickoff and submission on Fri Dec 18.
- Shopify publishes no SLA. Plan 2-3 rounds and 6-14 weeks to Published (reported), at about 30 days per review (reported). Every resubmission slows review†, and resubmitting while queued sends you to the back.
- Best case is about Jan 29. Planned case, with two returned rounds, is about Mar 26. A third round misses Q1.
- Don't promise "public in Q1" externally. Promise "coming to the Shopify App Store".

### 4. Live pilots before approval are the one legitimate reason for a custom app
- A public app can't install on the brands' production stores until it's approved. If the brands truly need live stores before approval, a custom app is the only route.
- If they can pilot on development stores, use the public-app path alone, with no second app.
- If they can't, build the custom app as a bridge. Cost: one custom app per Plus organization, no Shopify billing, and a reinstall on the public app later. Write a sunset date into the contract.
- Ask the three brands today: dev-store pilot, or live stores from December?

### 5. Protected customer data must be requested before you submit
- Reading orders or customers is Level 1 and needs review. Name, address, phone and email add Level 2 with data-protection reviews.
- Shopify refuses the request while the app is in review, and unapproved fields come back redacted. Request it in week 1.

### 6. Review failures that will cost you a round
- Reviewers need test credentials exempt from 2FA, OTP and SSO that keep working after publish. A missing login pauses the submission.
- Install must authenticate before any UI and land in the app. Never ask for a shop domain, and never send merchants to your site to sign up first.
- Don't ship your existing ERP web UI as the app home. That is also a Built for Shopify blocker, though contract-based B2B has an exception.
- Migrate to expiring offline tokens before 2027-01-01†. Non-compliant apps then lose their listing and new installs. Old tokens get 403 errors from 2027-04-01†.

## Recommended plan

**Distribution:** a public app with limited visibility for the pilot, flipped to fully visible after launch.
- It's one review, installable from its App Store URL, and hidden from search.
- Switching to fully visible is allowed at any time.
- Go fully visible at approval if you want App Store discovery on launch day.
- Fall back to a custom app only per concern 4, as a bridge.

**Billing:** as in concern 2. Name one owner for the Partner Support written answer.

**Protected data:** request Level 1 now. Skip Level 2 unless the design needs a customer field, and give a one-line reason per field if it does.

## Timeline

| Date | Step | Owner |
|---|---|---|
| Mon Nov 2 | Kickoff. Create the dev app and the production public app (limited visibility). Send Partner Support the billing question. Request Level 1 protected data. | PM, eng lead |
| Nov 2 – Dec 11 | Build: embedded UI, Shopify billing, compliance webhooks, uninstall and reinstall flow. | Engineering |
| Dec 14–18 | Packet from the checklist below. Run Shopify's AI self-review. Install from scratch on a dev store, uninstall, reinstall, change plans. Submit Dec 18. | Engineering, PM |
| ~Jan 18 | Round 1 returned. Fix every flagged item in one pass, answer misreads in that requirement's notes, retest the whole path. Resubmit ~Jan 22. | Engineering, review-inbox owner |
| ~Feb 21 | Round 2 returned. Same discipline. Resubmit ~Feb 25. | Same |
| ~Mar 26 | Published in the planned case. Switch to fully visible. | PM |

Read the Paused banner when it shows up:
- **No date** means core requirements blocked testing. Fix every flagged item and mark each resolved. Then click Submit fixes.
- **A date** means a cooldown, reported at 2 weeks to a month. Don't dispute an exemption refusal, because that triggers one.

## Submission packet owners

The full item list is in `references/submission-packet.md`.

- **Configuration:** app URL and redirects tested, no "Shopify" in domains or the API contact email, compliance webhooks, 1200×1200† icon, emergency contact. *Engineering.*
- **Listing:** name leads with your brand, the category term fits in 30 characters†, and the TOML name matches the listing name. Subtitle, details and the 3-6 screenshots at 1600×900† follow Shopify's rules (no stats, no "best", no testimonials). *PM, with marketing.*
- **Test access:** step-by-step instructions, a 2FA/SSO-exempt test account that survives publish, and dummy data for third-party services. *Engineering.*
- **Screencast:** English, covering install, onboarding, core features and plan change. *PM.*
- **Pricing details:** every plan and trial, matching billing exactly. *PM.*
- **Protected data:** per concern 5. *Engineering lead, security.*
- **Review notes and inbox:** the billing rationale and Partner Support's written answer. One owner, with `noreply@shopify.com` allowed. *PM.*

## Decide before Monday

1. Dev-store pilot, or live stores before approval? This decides whether a custom app exists at all.
2. Are the three brands one Plus organization or three?
3. Who owns the Partner Support billing question and the review inbox?
4. Does the billing change for the three pilot brands need sign-off from sales or finance?

If you tell me the answers to 1 and 2, I'll re-rank the distribution options and say which answer moved it.