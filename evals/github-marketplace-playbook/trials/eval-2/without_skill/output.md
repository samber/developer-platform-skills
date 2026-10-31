# Marketplace plan for March 18

**Short answer:** you can probably hit March 18 with a Marketplace listing. You probably can't count on the bank and insurer buying the paid plan through Marketplace. Plan on two separate tracks.

⚠️ I'm working from memory of GitHub's Marketplace rules. I did not check current docs. Confirm the four items marked ⚠️ with GitHub before you commit to anything.

## Why the sales lead's plan is risky

1. **Invoice billing may not work for Marketplace.** ⚠️ As I recall, Marketplace paid plans bill through GitHub's own payment methods, typically a card or PayPal on the buying account. A GHEC customer who pays GitHub by invoice may not be able to put a third-party app on that invoice. If so, the bank and insurer would need a card, which most bank procurement teams won't use.
2. **Paid plans have gates, and you haven't started any of them.** ⚠️ As I recall, a paid GitHub App listing needs all of these:
   - a verified publisher (organization verification)
   - financial onboarding for payouts
   - a minimum install count, which I recall as about 100 for GitHub Apps
   - GitHub's review and approval of the listing
3. **Review time is not in your control.** Five weeks leaves little slack if the listing isn't submitted yet.
4. **Banks and insurers buy through a security review and a contract.** That process usually runs longer than five weeks, whichever channel you use.

## Recommended structure

**Track A: Marketplace listing (marketing and self-serve)**
- List the app with a **free plan** or free trial. This is the lowest-risk path to "available on Marketplace."
- Add a paid self-serve plan for small teams only if you already meet the install and verification gates.
- Use the listing for discovery and low-friction installs.

**Track B: Bank and insurer (direct deal)**
- Sell through a direct contract and invoice. Procurement already knows how to handle that.
- Have them install the same GitHub App from the listing or from a direct link. This gives the sales lead what they want: a simple install path and a clean procurement path.
- Start the security packet now. Put these in it:
  - a permissions justification
  - a data-flow diagram
  - a statement that you don't store source code, if that is true
  - SOC 2 status
  - your DPA and subprocessor list

**Confirm with GitHub before you promise "buy on Marketplace" to anyone** ⚠️
- Whether invoice-billed GHEC accounts can buy paid Marketplace apps at all.
- Whether you may sell a custom enterprise contract off-platform while the Marketplace listing has a free plan or a smaller paid plan. I believe you can, but check the policy wording.
- Your install count against the paid-plan threshold.
- Current review turnaround.

## Five-week timeline

| Week | Action |
|---|---|
| 1 (now) | Check install count, org verification and payout setup status. Email GitHub Marketplace support with the four questions above. Decide free-only or free plus paid. |
| 1 | Draft the listing: logo, description, screenshots, pricing plans, support and privacy URLs, webhook and permissions review. Trim permissions to the minimum. |
| 2 | **Submit the listing.** Submitting is the critical path, so do this by the end of week 2. Start the bank and insurer security packets in parallel. |
| 3–4 | Answer reviewer feedback within a day. Finish the direct-contract order form and the pricing for the two prospects. |
| 5 | Make a go/no-go call on the announcement, based on approval status. |
| March 18 | Announce. |

## What to say on stage

- **If approved:** "Tessellate is now on GitHub Marketplace." Show the install flow. Mention enterprise licensing separately and don't tie it to Marketplace billing.
- **If still in review:** say "Listing submitted, available soon" and give a link to a direct install. Don't promise a date you don't control.
- **Either way:** don't say "buy through Marketplace on your GitHub invoice" until GitHub confirms in writing that it works for invoice-billed GHEC accounts.

## Questions for you

1. How many installs do you have today, and is your GitHub org verified?
2. Do you have Stripe or payout onboarding set up?
3. Is the sales lead's goal a simpler purchase, or does it specifically have to go through Marketplace? If it's simpler purchase, a direct invoice deal already delivers that.