# Sprintlight: Free to Paid plan review

**Short answer:** yes, you're missing several things. Two of them may break the plan as written. I answered from general knowledge of the Atlassian Marketplace and Forge and did not check live docs, so confirm each ⚠️ item with Atlassian Marketplace partner support before committing to the date.

## Next action

Open a partner support ticket this week with three questions:
1. Can a Free-listed Forge app switch to "Paid via Atlassian"?
2. What happens to existing installs when it does?
3. What consent flow applies when a major version adds a scope and external egress?

The rest of the plan depends on those answers.

## 🔴 Blockers

1. **⚠️ You may not be able to flip the listing.**
   - As I recall, Atlassian locks an app's payment model once it's listed. Free to Paid via Atlassian may need a new listing, and for Forge possibly a new app ID.
   - A new listing means 3,000 installs don't carry over. It also resets reviews, ratings and search rank.
   - If a flip is allowed, Forge licensing still has to be enabled in the manifest and deployed. That is separate from the listing change.

2. **Existing customers can't be made to "just start paying".**
   - Atlassian bills through licenses tied to an install. Free installs have no paid license.
   - Customers have to opt in, either by upgrading or by installing the new listing. You can't charge them silently from the next billing cycle.
   - Forcing it also risks reviews and uninstalls from the users who made the traction you want to monetize.
   - Realistic options:
     - **Grandfather:** existing installs stay free for 6–12 months.
     - **Sunset:** end-of-free notice of 60–90 days, with a discounted first year.
     - **Split:** keep a free listing and put Slack in a paid "Pro" listing.
   - ⚠️ Check the Partner Agreement for required notice periods on pricing changes.

3. **Don't bundle the new scope and egress with the pricing change.**
   - Adding `write:jira-work` and external fetch to `hooks.slack.com` is a major Forge version. It needs admin consent, and installs don't auto-update until an admin approves.
   - Admins would see "new permissions + data leaves Atlassian + now costs money" in one prompt. That is the worst moment for a consent screen.
   - Many of the 3,000 will never approve it and stay on the old version. Plan for a long tail on v1.
   - **Recommendation:** ship Slack in release 1 and monetize in release 2, or at least as separate announcements.

## 🟠 Scope and security gaps

4. **Use granular scopes, not `write:jira-work`.**
   - The classic scope covers creating, editing and deleting issues. Posting comments needs only the granular comment scope (e.g. `write:comment:jira`, plus read scopes for the issues you reference).
   - A narrower scope makes a smaller consent prompt and a better security review.

5. **Egress changes your listing.**
   - Declare `hooks.slack.com` under `permissions.external.fetch.backend` in the manifest.
   - Your Marketplace Privacy and Security tab must now disclose that Jira data goes to Slack.
   - ⚠️ A Runs on Atlassian badge or claim likely doesn't survive external egress.

6. **Webhook URLs are secrets.**
   - An incoming-webhook URL grants posting rights to a channel. Store it in Forge secrets or encrypted storage, never in plain app storage or logs.
   - Incoming webhooks are one-way, per channel, and the customer must create a Slack app. That adds setup friction.
   - If "post status comments back" means Slack actions flowing back into Jira, you need Slack OAuth, `slack.com/api` egress, request-signature verification and a remote or inbound path. That is a bigger build than the webhook.

7. **Privacy and compliance updates.**
   - Update your privacy policy and DPA, and add Slack as a subprocessor.
   - Check data-residency commitments. Slack may not sit in the customer's pinned region.
   - If you store Atlassian account IDs, confirm you handle the personal-data reporting (deletion) obligation.
   - Add an admin toggle and per-project opt-in for Slack, so the new egress is off by default.

8. ⚠️ **Paid cloud apps carry extra obligations.** From memory: the Marketplace bug bounty and the cloud security self-assessment. Confirm which apply.

## 🟠 Commercial gaps

9. **$2/user isn't how Atlassian pricing works.** You set prices per user tier of the host product (10, 25, 50 users and so on), not a linear per-user rate. Define the tier table, the small-tier floor, annual vs monthly pricing, and what the largest tiers cost.

10. **Forecast revenue from real data.**
    - 3,000 installs is not 3,000 payers. Many are tiny teams, trials or dead installs.
    - Pull active installs, users per install and site-size distribution. Model conversion at 2%, 5% and 10%, net of Atlassian's revenue share (⚠️ check the current rate) and Forge platform consumption charges (⚠️ check the current terms).
    - Slack notifications add invocations per issue event, so model that cost per tier.

11. **Seller setup.** You need Marketplace partner payout details, tax forms, a legal entity and bank account, a refund policy, an EULA, a support URL and a support SLA. A paid app that takes weeks to answer tickets earns refund requests.

12. **Trials and promotion.** Decide the trial length for existing users, whether to offer a launch discount, and whether Slack is paid-only or free for the first N days.

## 🟢 Communication and rollout plan

1. **T−90 days:** announce in-app, on the listing, by email and on the community page. Explain why, what stays free, what changes, and the date.
2. **T−60 days:** ship Slack (release 1), off by default.
3. **T−30 days:** open the paid offer to existing users with the grandfather or discount terms.
4. **Cutover:** apply the confirmed mechanism (flip or new listing).
5. **After cutover:** track upgrade rate, uninstalls by cohort, ratings and support volume weekly. Set a rollback or extension rule in advance, for example "extend the grace period if uninstalls exceed X%".

## Questions for you

1. What is the active-install count, and the users-per-install distribution?
2. Is Slack meant to be paid-only, or free in v1?
3. Does "post status comments back" mean inbound Slack actions, or only outbound notifications?
4. Do you own the legal entity and payout setup in Marketplace already?
5. How long can you tolerate a period of reduced install growth during the transition?