# Recommendation: list the GitHub App first, and check whether the Copilot Extension can be listed at all

**Next action:** this week, submit the GitHub App as a free-only listing. Before the AI team commits to next month, have them confirm the Copilot Extension category still accepts new listings.

I didn't open anything under `skill-wip/`, as you asked. I also didn't check GitHub's live docs. The platform claims below come from memory, so confirm them first.

## Why the App goes first

1. **It is ready now.** The App has about 150 installs and a working product. The listing is mostly a submission and review task, not engineering work.
2. **Free-only fits your billing.** Stripe stays your billing system and GitHub takes no cut. You get discovery without migrating anyone's billing.
3. **The Copilot listing may not exist.** As far as I recall, GitHub announced the sunset of GitHub-App-based Copilot Extensions in late 2025. It moved the Copilot category toward MCP servers. If that holds on 2026-10-30, a "Copilot Extension" listing next month may be impossible or need a rebuild. Treat the AI team's timeline as unconfirmed until they check.
4. **The App listing helps the other one.** If you do ship a Copilot-category listing, you'll already have a verified publisher, a reviewed listing and a support URL.

## Check before you submit the App

- ⚠️ **The free plan must be a real plan.** If "Free" only redirects to a Stripe paywall, review is likely to reject it or users will complain. Decide what the Marketplace free plan includes. For example: public repos only, or a seat or repo cap. Bramblework's free tier today (if any) is the natural candidate.
- ⚠️ **Check GitHub's rules on off-platform payment.** Free-only with paid features sold elsewhere is common, but read the current Marketplace developer agreement and listing guidelines. Look at what a listing may say about paid upgrades, and whether a "Contact" or "Visit website" CTA is allowed. Do this before you design the listing copy.
- ⚠️ **Publisher requirements.** I believe free listings have lighter requirements than paid ones. Paid plans need a verified publisher and a minimum install count, and 150 installs would clear that bar. Confirm what applies to free-only, and start publisher verification now if it's missing, since it can take time.
- ℹ️ **Reversibility.** You can't easily switch the same listing to GitHub billing later. Moving to paid plans later is possible but means GitHub-managed billing. Decide now that you won't want that.
- ℹ️ **Listing assets.** Prepare the logo, description, screenshots, support and privacy URLs, the webhook and permissions justification, and the least-privilege permissions review. Reviewers check the permissions, so trim any you don't use.

## Copilot Extension: what to ask the AI team this week

1. Is the extension a GitHub App-based Copilot Extension or an MCP server?
2. Does GitHub's current Marketplace still accept the Copilot category for it? Link the doc or changelog entry that says so.
3. If the answer is no, what is the replacement distribution path (MCP registry, VS Code, or other)? Plan that for next month instead.
4. If the answer is yes, what are the review requirements and lead time? Then list it second, after the App listing is submitted. The two reviews can run in parallel and don't depend on each other.

## Order

| Step | When | What |
|---|---|---|
| 1 | This week | Decide the free-plan scope. Read the Marketplace billing and listing rules. |
| 2 | This week | Start publisher verification if needed. Submit the App free-only. |
| 3 | This week | AI team confirms the Copilot category status (questions above). |
| 4 | Next month | List the Copilot Extension if it's still supported. Otherwise use its replacement channel. |

**One caveat:** I'm confident in the order (App first) because it is the lower-risk, ready item. I'm less sure of the Copilot Extension sunset details, so verify those before you tell the AI team.