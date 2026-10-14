**No-go on "partner mode on live account."** Go on a dedicated test tenancy for partners. Hand-provision it for the 6 waiting partners first, and automate it after.

I could not run the skill's 9-question interview in this one-shot task, so I assumed the answers below. Tell me if any is wrong and I will re-rank.

## Why no-go

1. The skill's rule for this case is explicit: once apps touch money, irreversible actions, or other tenants' data, delete the own-account-as-sandbox rung. Do not demote it. Partner apps here move money between customers' sub-accounts, which is all three.
2. A flag on a live account is a safety boundary made of one boolean. A flag bug, a misrouted call, or a partner who forgets the flag moves real money. The impact is financial and also hits customer trust.
3. "Build proper sandboxes later" is the failure the skill warns about. Six partners will write code against live-account behavior and live credentials. When real sandboxes ship, they must migrate. The parked option comes back as scope, and costs more then.
4. Slack's own-account shape works because a bad app message is reversible. A payout is not.
5. "Zero infra" is not true. Partner mode on live still needs flag enforcement, payment-rail blocking, fee and ledger exclusion, and support triage for partner-mode transactions. That is isolation work on the riskiest surface.

## Assumptions (re-rank if wrong)

| # | Question | Assumed answer | Effect |
|---|----------|----------------|--------|
| 1 | What partners build | Marketplace apps | Gate and tenancy below |
| 3 | Time to first app | Days | Self-service entry, no guided stages |
| 4 | Data sensitivity | High (money, KYC) | Deletes own-account rung |
| 5 | Partners | Mix, 6 are likely commercial ISVs | Named contact for the 6 only |
| 7 | Deadline | Hard and tight | Promotes low-effort rungs |
| 8 | Goal | Both: 6 waiting, ecosystem later | Manual now, automated later |
| 9 | Effort ceiling | Small, a few engineer-weeks | Rules out production-mirror sandboxes |

## Recommended design

**Stage model (name them, each gets an owner and a metric):** Plan, Build, Launch, Grow. This is Atlassian's model, and it fits an hours-to-days platform. Do not copy Salesforce's pre-launch ladder.

**Entry gate: agreement-split.**
- Anyone builds with a self-service signup and a click-through program agreement. No human review.
- Going live is a separate verified track: agreement signature plus KYB. It gates selling and moving real money, never building. Atlassian formalized this split in 2025.
- Reason: your apps move money, so the real trust control belongs at go-live. Registration review would only slow the 6 partners.

**Provisioning: instant dedicated dev tenancy.**
- Each partner gets their own test-mode account with test keys. It has no real payment rails, simulated processor and bank behavior, and fake sub-accounts. This follows Shopify's fake payment gateway.
- Create it at signup, free, with no time limit and no card. Do not put it behind review.
- Isolation architecture, key prefixes, magic test values, and graduation to live belong to `samber/developer-platform-skills@api-test-mode-design`. Hand that design there.
- Production-mirror sandboxes stay starved. They are too heavy for your deadline and effort ceiling. Promote them later only if enterprise partners cannot validate without realistic scale.

**Deadline plan: concierge first, automation second.**
1. Week 1: your team creates 6 test tenants by hand for the 6 partners. Put a minimal simulated money-movement layer behind them, with no real rails.
2. Weeks 2-4: automate provisioning to self-service signup.
3. The 6 partners are unblocked early. Nobody builds against live.
4. If even a simulated ledger is too much for week 1, ship the 6 tenants with canned responses for the core sub-account transfer flows only, and widen coverage after.

**Education: optional parallel track.** Quickstart, docs, and sample apps from day one. Nothing gates submission. Move to a credentialed loop only if buyers start asking for partner credibility signals.

**Support ladder (stacking):**
1. Docs plus a community forum for everyone.
2. A shared channel and a named contact for the 6 waiting partners only. This is the commercial-ISV exception, and it is cheap at 6.
3. Office hours, if questions on money-movement flows cluster.

**Commercial decisions late.** Do not ask for pricing, fee share, or payout terms at signup. Ask at first listing, as the monetization choice is the last gate before launch. Put the seller agreement and KYB there too. Disclose every post-launch threshold and review requirement in the onboarding docs, so partners do not hit a surprise wall.

**Instrument the funnel before the 6 partners start:**
1. Signup to tenant provisioned.
2. Provisioned to first API call. Target under about 10 minutes. If it is higher, fix friction before anything else.
3. First call to first app submitted. Call this time-to-first-submitted-app and label it self-defined in every report.
4. Submission to approval.

Also track first-review fail rate. Above 30-40%, build a pre-submission validator before adding any education mandate. Baseline against your first quarter and track the trend. Set no absolute pass bar.

## What to tell engineering

- The speed they want is real, and the concierge-then-automate plan keeps it.
- The risk is not "partners can't start fast." It is "a flag stands between a partner and real customer money."
- Their "minutes to start" goal is met by instant test tenancy. The 10-minute checkpoint 2 target measures exactly that.
- The part you can't trade away is separate test credentials with no path to real rails.

## Open points for you

- ⚠️ Confirm assumption 4. If partner apps only simulate money and never move it, the answer changes. I doubt that, given "move money between sub-accounts."
- ⚠️ I did not read `api-test-mode-design`. I only cite it as the owner of the isolation decisions.
- ℹ️ Review-gate mechanics, listing standards, and tier design are out of scope here. They belong to `app-marketplace-review`, `app-marketplace-listing-standards`, and `connector-marketplace-strategy`.

Next: tell me which assumptions in the table are wrong. Then I will re-rank, and I can save the chosen gate, tenancy, and promotion conditions to `developer-platform-context.md`.