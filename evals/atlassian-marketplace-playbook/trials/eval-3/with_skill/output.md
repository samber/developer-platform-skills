# Sprintlight: Free → Paid at $2/user, plus Slack

**Route:** Listed (Forge, Free). Rules touched: 3, 4, 5, 6, plus Payment and pricing, Versions and consent, Keep the listing.

Figures marked † come from the skill's reference and change often. Check them against current Atlassian developer docs before you quote them to anyone.

## Verdict

The plan has three problems.

1. **Existing customers cannot "just start paying next cycle".** Free → Paid via Atlassian (PvA) is a new version, a re-review and a major version that each site admin must accept. Installs on the new major count as unlicensed until the admin subscribes. Sites that never accept stay on the old free major. Nothing in the process bills a site automatically.
2. **Slack is a second major trigger.** `hooks.slack.com` is new egress, and `write:jira-work` is a new scope. Each is a major that waits for admin consent. Admins who see a paywall and a new write permission in one prompt are the hardest to convert.
3. **"Next month" is probably too tight.** Plan three weeks per review round plus one returned round†. Six weeks back from 30 Nov was 19 Oct, which has passed.

## Assumptions

Each is one missing answer. Correct any that is wrong, because several change the plan.

- **A1.** Sprintlight is Forge-only, with no Connect module or Connect scope. If not, the share drops from 83%† to 75%† and migration comes first.
- **A2.** Sprintlight has no external SaaS account. Everything works inside Jira today.
- **A3.** `write:jira-work` is not already granted. If it is, only the egress is new.
- **A4.** "Post status comments back" means Sprintlight posts a Jira comment when something happens in Slack. That needs an inbound path (see Open questions, #1).
- **A5.** $2 is per user per month. Annual is 10× monthly†. No editions at launch, because a new edition is a re-review.
- **A6.** The partner identity check, security questionnaire and payment profile were done for the 2024 listing. The payment profile may be missing, since a Free app never needed one.

## Decisions

**Release shape: one major, with Slack as the paid feature and today's features staying free for a stated period.**

- **Licensing, scope and egress go in one major.** Admins get one consent prompt instead of two, and you pay for one review instead of two. Do not bundle a security fix into it. A fix tied to a major waits for review while its deadline runs. Ship fixes as minors on the old major.
- **Slack notifications are the only licensed feature.** Existing features stay free for a grace date you publish, so the consent prompt costs the admin nothing today. Gate Slack in code with `context.license.active`, and use `filter.appIsLicensed` on triggers.
- **Ending the grace period later is a code change, not a new major.** It only reaches sites that moved to the new major. Sites on the old major keep today's free features, and you cannot gate them. Decide now how long you will keep the old major working, and ask Atlassian whether you may retire it.
- **Do not count on the 60-day price-change protection†.** It describes price changes inside PvA. Your protection for existing customers is the grace period you publish.
- **Do not use an external plan to unlock Jira features.** "Charge on our website" is not allowed without Atlassian's written ruling. If you consider it, get that ruling on the ticket first.

**Why $2 per user is not simple:** a PvA license matches the host site's licensed user count. A 2,000-user Jira site cannot license 40 Sprintlight users. Atlassian prices per host user count with lower per-user rates at higher counts†. Model revenue per site size, and expect large sites to push back or uninstall.

## What you are missing

| #   | Gap                                                                                                                                                                                                                                                                                               | Action                                                                                                                                                                                                         |
| --- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | Slack's incoming webhooks only send into Slack. They cannot trigger Jira comments, so "post status comments back" needs an inbound path (Slack interactivity, which needs a remote backend or a dynamic web trigger). A dynamic web trigger, a new remote or an auth provider is another major trigger† | Decide the exact data flow before writing the manifest. Declare every host, trigger and auth provider in this release. Anything added later is a new major with a new consent prompt.                          |
| 2   | `inScopeEUD` on `hooks.slack.com`. Issue data sent to Slack is end-user data. A false → true flip later is a major†.                                                                                                                                                                              | Set it correctly in this version. Declare no wildcards.                                                                                                                                                        |
| 3   | "Runs on Atlassian" badge. If Sprintlight has it today, adding egress removes it, because the badge allows no egress except analytics.                                                                                                                                                           | Check the listing. If buyers filter on it, weigh that loss against Slack.                                                                                                                                      |
| 4   | Scope justification. Reviewers check each scope against a feature, Ecoscanner flags unused ones, and Atlassian Enterprise Certified (AEC) fails them.                                                                                                                                             | Write one justification per scope and per remote host, naming the feature that calls it. Check whether a narrower comment-write scope covers the feature, since `write:jira-work` is broad (verify†).        |
| 5   | Webhook URLs are customer secrets.                                                                                                                                                                                                                                                                | Store them as Forge secrets, never in logs. Describe them on the Privacy & Security tab.                                                                                                                       |
| 6   | No collected Atlassian API tokens. Use OAuth 2.0 or Forge auth.                                                                                                                                                                                                                                   | Do not ask users for tokens to post comments.                                                                                                                                                                  |
| 7   | Forge consumption billing. Usage above the monthly free allowance is invoiced to you, paid apps included†. Notification fan-out across 3,000 installs is new usage.                                                                                                                              | Estimate cost per active site against $2/user and the 83%† share. Share is 100% until $1M lifetime Forge revenue†, and payout needs $500 profit accrued†.                                                       |
| 8   | The app name. "Name for Jira", never "Jira Name". Naming is on the irreversibles list.                                                                                                                                                                                                            | Check "Sprintlight" against the rule before submission.                                                                                                                                                        |
| 9   | Test installs are billed. Every production install of a paid app is billed, yours included. Once licensed or submitted, the app cannot be shared by install link.                                                                                                                                 | Test with `forge install --license active`, `inactive` and `trial` on development or staging. Give testers a separate unlicensed copy.                                                                         |
| 10  | Listing locked in review. Copy changes go through the ticket.                                                                                                                                                                                                                                     | Finalize the free/paid wording before submitting. Do not announce a price date until the review is approved.                                                                                                   |
| 11  | Customer communication. Admins see a consent prompt for a major, and the release notes are the only explanation.                                                                                                                                                                                  | Write notes that say: what is free and until when, what Slack costs, why the scope and egress are needed, and that the previous version keeps working.                                                         |
| 12  | The 18-month rule and the security SLAs now apply to a paid app with revenue at stake†.                                                                                                                                                                                                           | Critical fix in 10 days, High in 4 weeks. A missed Critical hides the app from new installs. Silence for 90 days hides the app. Report an incident within 24 hours. Put the contact on the Privacy & Security tab. |
| 13  | Consent lag. Sites stay on the old major until the admin consents, and you cannot bulk-upgrade a privilege-escalating major. Verify whether a licensing-only major may be bulk-upgraded†.                                                                                                         | Use rolling releases to ship code while consent is pending. Track the share of installs on the new major at 30 and 90 days.                                                                                        |

## Irreversibles register

| Item                                                  | Locked when                      | Owner  | Decide by                                |
| ----------------------------------------------------- | -------------------------------- | ------ | ---------------------------------------- |
| Payment model (PvA, no Paid via Vendor on Forge)      | First licensed version           | [name] | Before submission                        |
| Licensing enabled                                     | First licensed version           | [name] | Before submission                        |
| Scopes (`write:jira-work` or narrower)                | This major; later ones are majors | [name] | Before submission                        |
| Egress hosts and `inScopeEUD` flags                   | This major; false → true is a major | [name] | Before submission                      |
| Inbound path for Slack (remote, web trigger, auth provider) | This major; later ones are majors | [name] | Before submission                        |
| App name                                              | Listing                          | [name] | Before submission                        |
| Free-feature grace date and old-major support length  | Public promise                   | [name] | Before the release notes                 |

## Submission checklist

1. ECOHELP access confirmed by opening a test ticket. Owner: [name].
2. Partner identity verification and the security questionnaire (Forge variant) current. Payment profile completed. Company email domain on the account.
3. Privacy & Security tab updated: Slack as a subprocessor, data sent, where it is stored, one justification per scope, trust-center link.
4. Scope and egress list for the reviewer, each item with the feature that calls it.
5. Privacy policy, End User Terms, DPA and documentation URL updated for Slack.
6. Test credentials and a sample Slack workspace on the ticket.
7. Enable sharing in the developer console, then submit.

## Timeline

| Date (2026)    | Step                                                                                              |
| -------------- | ------------------------------------------------------------------------------------------------- |
| 31 Oct – 6 Nov | Decide the open questions. Fix the manifest and inbound path. Write justifications and notes.      |
| By 6 Nov       | Submit. Review is 10–15 business days for approval and 5–10 for the security workflow†.           |
| ~27 Nov        | Earliest approval if the first round is clean.                                                    |
| ~18 Dec        | Approval after one returned round. This is the safer planning date.                               |
| After approval | Release, then consent lag. Revenue starts only from sites that accept and subscribe.              |

Treat 30 Nov as a stretch target, not a promise. If a returned round pushes you into late December, consider holding the release to January so the consent prompt does not land during holidays.

## Post-listing calendar

- **Approval within two rounds.** If not, ask on the ticket what timed out.
- **Share of installs on the new major at 30 and 90 days.** Below your threshold, rework the release notes or the grace period.
- **Subscribed sites as a share of sites on the new major.** This is the conversion number that matters.
- **Zero AMS tickets past due.** Security SLAs apply from day one.
- **Forge consumption cost per active site, monthly.**

## Open questions (they move the plan)

1. What does "post status comments back" do exactly? Moves: inbound path, extra major triggers, review risk.
2. Does Sprintlight carry the Runs on Atlassian badge today? Moves: whether Slack is worth it now.
3. Is it Forge-only, with no Connect module or scope? Moves: revenue share and AEC.
4. Is $2 monthly or annual, and are editions planned? Moves: pricing model and review count.
5. Do any target buyers require data residency or no egress? Moves: Slack as a default-off feature, and AEC.
6. Is any event or announcement pinned to a date? Moves: whether to hold the release.

## Alternatives, ranked by effort

1. **Recommended: the single major above.** Lowest review cost. Slack carries the paywall and today's features stay free through the grace date.
2. **Split in two:** licensing first with no new scope or egress, then Slack. Two reviews and two prompts. Choose this if reviewers push back on Slack or the inbound path is not designed.
3. **Ship Slack free now, charge later.** Cheapest today, but the later switch is a new version, a re-review and another admin-consented major. The skill lists it as the "ship free now, switch later" trap.

Nothing here has been checked against live Atlassian docs. The skill's own rule is that Atlassian changed framework, badge and revenue-share rules inside a year, so confirm every † figure before it goes in the release notes or the customer email.