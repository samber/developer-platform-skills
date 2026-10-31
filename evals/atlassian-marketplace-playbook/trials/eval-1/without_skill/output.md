# Notebridge for Jira: plan

I didn't read anything under `skill-wip/` or any repo file. The Atlassian facts below come from my own knowledge, which runs to about mid-2026, so check each ⚠️ item against developer.atlassian.com before you commit.

## 1. Bottom line

- ❌ **Don't build on Atlassian Connect.** Atlassian announced the end of Connect: no new Connect apps on the Marketplace from late 2025, and end of support around the end of 2026. Today is 2026-10-31. A Connect app listed in December has weeks of life left, and the listing may be rejected outright.
- ✅ **Build on Forge with Forge Remote.** Forge Remote keeps your existing backend and OAuth flows. The Jira side becomes a thin Forge manifest, an issue panel module, and a signed call to your servers. This is closest to your original "just point at our servers" idea.
- ⚠️ **Treat "listing live in 6 weeks" as a stretch goal.** Forge build is about 3 weeks. Marketplace approval, security self-assessment and vendor setup are outside your control. Plan the conference demo so it doesn't depend on the listing.
- ⚠️ **Free listing plus Pro sold on your own Stripe page needs a policy check first.** Payment model rules and external-billing rules decide whether this is allowed. Get an answer in week 1, before you design the upsell UI.
- ⚠️ **Cloud Fortified is probably not the target anymore.** The program has been reported as replaced or renamed, and its requirements have shifted. Confirm the current name and criteria before promising it to enterprise prospects.

## 2. Problems with the current plan

| Assumption | Issue | Action |
|---|---|---|
| Connect "points at our servers" | Connect is being sunset. Forge Remote gives the same "use our servers" shape on the supported platform. | Move to Forge Remote. |
| List Free, sell Pro via Stripe | Marketplace has payment models (free, paid via Atlassian, paid via vendor). The choice may be locked after listing, and external paywalls may conflict with policy. | Ask Marketplace partner support in writing. Don't build the upsell before the answer. |
| Fortified right after launch | The program may have changed. Its requirements (security programs, reliability, support SLAs, bug bounty) are heavy for 14 people. | Verify the current program. Build the prerequisites during launch. |
| Listing live in 6 weeks | Vendor verification, security questionnaire and review run on Atlassian's clock. | Schedule submission by end of week 4. Keep a demo path that needs no listing. |
| Existing OAuth "already exists" | That is your Notebridge login. Jira needs its own authorization: Forge invocation tokens, or Atlassian OAuth 3LO for background sync. | Scope this in week 1. It is the likeliest hidden work. |

## 3. Recommended architecture

**Jira side (Forge app):**
- Issue panel module (`jira:issuePanel`) that shows the meeting summary, with Custom UI or UI Kit.
- Forge Remote for calls to the Notebridge backend. Verify the Forge Invocation Token (JWT) on your servers.
- Manifest permissions kept minimal: `read:jira-work`, `write:jira-work`, plus user read as needed. Scope breadth drives review friction and enterprise trust, so ask for the least you can.

**Notebridge side:**
- New endpoints: `create-issues-from-action-items`, `get-summary-for-issue`, plus an issue-to-meeting link table.
- Account linking: map the Jira `accountId` and cloud ID to a Notebridge workspace and user.
- Background sync (Pro bulk sync, webhooks) uses Atlassian OAuth 2.0 (3LO) tokens stored server-side, with refresh handling.
- Privacy: implement Atlassian's personal-data reporting and erasure obligations. Marketplace review checks for them.

**Flow:** meeting ends → action items extracted → user picks "Send to Jira" in Notebridge → issue created, with a link back to the meeting → issue panel loads the summary through Forge Remote.

## 4. Six-week timeline (2026-11-02 to 2026-12-11)

**Week 1: decisions and spikes (de-risk first)**
1. Confirm the Connect and Forge status and dates on Atlassian's developer site.
2. Email Marketplace partner support: Free listing + external Pro billing, payment model lock, and current Fortified/Enterprise-certification status.
3. Register the Marketplace vendor account and start company and tax verification. Do this now, because it has the longest lead time.
4. Spike: a Forge Remote "hello" panel calling your staging backend with a verified JWT.
5. Decide the account-linking model.

**Week 2: core build, issue creation**
- Create issues from action items with the field mapping: project, issue type, assignee, link back.
- Handle missing-permission and missing-field errors (required custom fields, closed projects).
- Tests: no connection, 401/403, 404 project, 429 rate limit, partial failure in a batch, malformed payload.

**Week 3: issue panel and linking**
- Summary panel with loading, empty and error states.
- Uninstall, reinstall and token-revocation paths.
- Run it on a Jira site with real data, not only a dev site.

**Week 4: Pro tier and submission**
- Pro features (auto-assign, bulk sync) gated by plan on your backend. The Stripe entitlement check stays server-side.
- Pricing page and the `$12/user/month` mapping. Decide what "user" means for Jira Pro: Notebridge seat or Jira user.
- **Submit to the Marketplace by end of week 4.** Include the listing copy, privacy policy, support contact, security self-assessment, and screenshots.
- Start the security prerequisites that Atlassian's programs ask for: bug bounty, vulnerability SLAs, incident process.

**Week 5: review buffer and demo hardening**
- Answer reviewer feedback within 24 hours.
- Record a backup demo video.
- Set up the demo Jira site with seeded meetings.

**Week 6: demo**
- Freeze features. Do rehearsals only.
- If the listing is approved, announce. If not, run the demo through a private install link (see section 7).

## 5. Pricing and billing

Pick one before week 4:

| Option | What it is | Tradeoff |
|---|---|---|
| A. Free connector, Pro on your plan | App is free. Jira Pro features unlock when the Notebridge workspace is on a plan that includes them, billed via Stripe. | Cleanest policy position (a companion app for an existing account). No Atlassian revenue share. Needs the written policy answer anyway. |
| B. Paid via vendor | Listed as paid, with billing on your side. | Matches your Stripe setup. May carry stricter requirements and a payment-model lock. |
| C. Paid via Atlassian | Atlassian bills and takes a revenue share. | Simplest for buyers and good for enterprise procurement. You give up your own pricing control and take on a revenue share, and the Pro price won't match your $12 page. |

My recommendation is **A**, pending the policy answer. Don't put checkout links inside the Jira UI until Atlassian confirms they're allowed. Link to your pricing page from the listing only if the policy permits.

## 6. Security and the enterprise path

Enterprise prospects asking about security is a good reason to start now, not after launch:
- Write a one-page data-flow doc: what meeting data reaches Jira, what Jira data reaches you, where it's stored, and retention.
- Keep Forge scopes minimal and document why each is needed.
- Set up a bug bounty or vulnerability disclosure program, since both Atlassian's programs and enterprise buyers ask for it.
- Define support hours and an SLA you can keep with 14 people. Fortified-style programs penalize promises you miss.
- Ask Atlassian whether Forge with Remote egress qualifies for the "Runs on Atlassian" badge. I expect not, because data leaves Atlassian, so your pitch should be your own security posture.
- SOC 2 or ISO 27001 status will matter more to your prospects than a badge. Tell me where you stand and I'll plan around it.

## 7. Risks and fallbacks

| Risk | Likelihood | Fallback |
|---|---|---|
| Marketplace approval slips past the demo | High | Demo via a private install link from your dev app, with the listing "coming soon". |
| Forge Remote needs more rework than a thin shell | Medium | Cut the panel to read-only summary for the demo. Issue creation stays in the Notebridge UI through 3LO. |
| Payment model conflict with Free + external Pro | Medium | Launch Free with Pro labelled "coming soon", or switch to option B or C. |
| Personal-data and privacy requirements are larger than expected | Medium | Start the reporting API work in week 2, not week 5. |
| Fortified or its successor not attainable quickly | High | Present your own security doc and bug bounty at the conference. |
| 14-person team, one or two engineers on this | High | Cut Pro features first (auto-assign, bulk sync). The core is create issue + summary panel. |

## 8. Questions to answer this week

1. Is the Atlassian Connect end-of-support date confirmed on the developer site, and does Forge Remote fit your auth model?
2. How many engineers can work on this for 6 weeks?
3. What does "user" mean for Pro billing: Notebridge seat or Jira user?
4. Do you hold SOC 2 or ISO 27001, and do you have a bug bounty?
5. Is the conference deadline fixed, and is a private-link demo acceptable?
6. Do you want Atlassian's revenue share (option C) in exchange for easier procurement?

If you answer 1, 2 and 6, I'll turn weeks 1 to 2 into tickets.