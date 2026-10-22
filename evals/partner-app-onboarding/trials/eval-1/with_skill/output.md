# Kettleworth partner onboarding: sanity check

**Verdict: ⚠️ don't take the VP's design to eng as written.** Move the hand review from registration to app submission. Drop application-based tiers and let Bronze/Silver/Gold be earned after launch.

I followed the `partner-app-onboarding` skill. It says to interview first, but you asked for one complete answer, so I set the interview answers from what you told me. Questions 6, 8 and 9 are still open and are listed at the end. Please correct anything I got wrong. A correction can change a recommendation.

## Interview answers I used

| # | Question | Answer used | Source |
|---|---|---|---|
| 1 | What do partners build? | (a) marketplace apps | You said "app marketplace" |
| 2 | What exists today? | (a) no program, designing from zero | Implied |
| 3 | Time to first working app | **Hours** (about 2h) | You said so |
| 4 | Data sensitivity | **Low** (shift schedules, staff first names, no payments) | You said so |
| 5 | Who are the partners? | (a) indie devs and small teams | You said so |
| 6 | Standing support capacity | ❓ unknown | Open |
| 7 | Deadline | Next quarter. Hard or soft? | Partly open |
| 8 | One-off win or compounding asset | Marketplace implies compounding | ❓ assumed |
| 9 | Effort ceiling | ❓ unknown | Open |

## What's wrong with the plan

1. **The entry gate is the most expensive option, and nothing here justifies it.**
   - The skill ranks hand-reviewed registration last on efficiency. Its cost grows with every applicant.
   - It promotes this gate in two cases only:
     - It's promoted if a competent developer needs weeks to months to build a first app. Yours needs hours.
     - It's promoted if you must know who is building before granting access to sensitive data. Your data is low sensitivity.
   - Neither case applies, so this is the default call: **self-service signup**.
   - The default is a form plus a click-through program agreement. It needs one legal sign-off, then none per partner.
   - Four of the five ecosystems studied use this model (Shopify, Atlassian, Slack, HubSpot). Salesforce is the application-gated outlier, and its build complexity is the reason.

2. **The "reference customer" field blocks your own audience.**
   - Indie devs and two-person shops have no app yet, so they have no reference customer.
   - The form asks for proof of something the program exists to help them build.
   - You'll reject or lose the partners you expect most of.

3. **Tiering at registration gates nothing real.**
   - At four of the five platforms studied, entry tiers gate nothing. Real tiers are earned after launch on performance (installs, revenue, quality).
   - Salesforce's pre-launch ladder is the one exception, and it's justified by its complex multi-org build model. The skill says not to copy it.
   - Tiers set from a written application rate how well someone writes an application. They don't rate the app.

4. **"Gold gets API access first, Bronze waits" is the skill's top failure mode: sandbox behind the review gate.**
   - Partners who are approved to build but can't test churn silently in the gap.
   - Your expected majority (indies) would be Bronze, so most of your ecosystem waits while a minority builds.
   - Your API is read/write on shift schedules, so there's no money or PII risk that would justify rationing access.
   - If the real reason is launch-day load or a founding cohort, see "If the VP has a real concern" below.

5. **Human review is placed before the partner has produced anything worth reviewing.**
   - The skill's rule is to decouple "start building" from "get approved". Accounts, sandboxes and credentials are instant and free. Human review sits at app submission, where it protects restaurants.
   - Your VP wants review for trust, and that is a fair goal. Review at the submission gate serves it better, because you see the actual app and its actual data behavior.

6. **Your two-hour hello-world is itself a finding.**
   - The skill's working threshold is a first API call within about 10 minutes of signup. Above that, fix onboarding friction before anything else.
   - Two hours is for a competent developer, so it likely includes setup, auth and docs hunting.
   - Cutting that time will do more for partner count than any gate design.

## Recommended design

Each step below assumes the gate chosen in step 2.

**1. Stage model.** Name the stages so each gets an owner and a metric. A simple set: Sign up → Build → Submit → Launch → Grow. Atlassian's Plan/Build/Launch/Grow model is a citable template.

**2. Entry gate: self-service signup.**
- Use a form plus a program-agreement checkbox, with no human in the loop.
- If you later let partners sell through Kettleworth, add a separate verified seller track at that point: agreement signature plus KYC/KYB. That track gates selling, never building (the Atlassian 2025 split).
- Optional: collect company name and use case as non-gating profile fields, for your own segmentation. Don't review them.

**3. Provisioning: instant dedicated dev tenancy.**
- At signup, create a free dev tenant with no time limit, no payment info, and seeded fake restaurant and shift data. Issue credentials immediately.
- I'd skip the own-account-as-sandbox shortcut. Your API writes shifts that real staff read, so test writes in a customer's live tenant are not safely reversible.
- Isolation, test-key prefixes and graduation to live belong to `api-test-mode-design`, which is out of scope here.

**4. Education: an optional parallel track.**
- Docs and a quickstart are available from day one and required by nothing, as at all five platforms studied.
- Promote to a credentialed education loop only if partner credibility becomes a signal restaurants look at.
- Skip mandatory certification. No major marketplace requires it.
- Publish the review checklist inside the onboarding docs, and build a pre-submission validator. Partners who find requirements at first rejection tend to need 2-3 rejection cycles.

**5. Support: docs plus a community forum.**
- That's the default, and it fits indies. Add real-time chat once repeated questions cluster. Add office hours if the review gate generates questions that need an engineer.
- Skip named partner managers for now. Platforms assign them to commercial partners only, never to every individual developer.

**6. Commercial decisions come late.**
- Don't ask about pricing or monetization at registration. Ask Free / Paid-via-platform / Paid-via-vendor at launch, as the last gate before listing.
- Keep performance tiers and featured placement out of the entry path. Link to them from the docs. They belong to `connector-marketplace-strategy`.

**7. Instrument the funnel before launch**, at four checkpoints:
1. Signup → sandbox and credentials provisioned.
2. Provisioned → first API call (target under about 10 minutes).
3. First API call → first app submitted.
4. Submission → approval.

- Time-to-first-submitted-app is a metric you'd be coining, so label it self-defined wherever you report it.
- Baseline against your first quarter. Don't set an absolute pass bar.
- If the first-review fail rate exceeds about 30-40% (a self-set threshold, not an industry standard), build the pre-submission validator before considering mandatory education.

## Where the hand review goes

Your VP's review instinct survives, moved to the submission gate:
- A human, or automation plus a human, reviews each app before it reaches a restaurant.
- Typical checks are scope and permissions, behavior on schedule data, handling of staff first names, and a working support contact.
- Gate mechanics belong to `app-marketplace-review`, so use that skill to design it.
- Other marketplaces take roughly 1-2 weeks to about 2.5 months for this stage. Plan reviewer capacity and a published review time before launch.
- Publish any post-launch thresholds (for example a minimum install count for certification or featured placement) in the onboarding docs. Hidden walls are a known failure mode.

## If the VP has a real concern behind the tiers

- **Launch-day load or support capacity.** Use a founding-cohort invite list, with the cohort chosen by outreach and not by application. Self-service opens to everyone after a set date. Cohort recruitment belongs to `app-marketplace-launch-marketing`.
- **Quality and trust.** Enforce it at submission review, with a published checklist and a validator.
- **Rewarding the best partners.** Use post-launch tiers (Bronze/Silver/Gold) earned on installs, retention and review pass rate, with benefits like placement and co-marketing.
- **Knowing who is building.** The signup record, a program agreement and the verified seller track cover this. One thing to confirm: staff first names are personal data under GDPR if you have EU customers. A click-through program agreement with data-processing terms is likely enough, but have legal confirm it.

## Open questions to settle before eng

1. **Support capacity (Q6).** How many docs writers, community moderators and partner managers are committed long-term? This sets how far down the support ladder you can go.
2. **Deadline (Q7).** Is "next quarter" a hard date? A hard date favors the low-effort rungs (dedicated tenancy with minimal seed data, docs plus forum).
3. **Goal (Q8).** Is this a one-off win with partners already waiting, or a growing ecosystem? Waiting partners argue for a founding cohort. A growing ecosystem argues for the compounding rungs.
4. **Effort ceiling (Q9).** What are the engineering hours for provisioning automation, the content budget, and support headcount? A low ceiling deletes rungs outright, such as the tenant seeding automation.
5. **VP's real driver.** Which of the concerns above is it: load, quality, or trust? Ask before the meeting. It decides whether the answer is a cohort, a stronger review, or post-launch tiers.

## Caveats

- Platform figures come from the skill's reference files and are platform-documented or developer-community-reported. Program rules change often, so re-verify any specific before quoting it to your VP.
- The ~10-minute and 30-40% thresholds are self-set starting points, not industry standards.
- I didn't run the skill's per-step validation with you, since you asked for one answer. If you disagree with step 2, tell me before step 3 onward, because every later step builds on the gate.