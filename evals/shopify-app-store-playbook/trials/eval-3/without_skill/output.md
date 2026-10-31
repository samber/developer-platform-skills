# Shopify app paused: fix all three, resubmit once

**Next action (10 min):** Open the review message and copy the exact wording of each note. Item 2 almost certainly maps to a numbered requirement, so quote it in your reply.

## Verdict on your plan

- **Item 2: don't push back.** Shopify's requirements bar asking merchants to type their `myshopify.com` domain. You'd be arguing against a hard rule, and a lost argument costs a review cycle you don't have.
- **Resubmit once, with all three fixed.** Fixing only the 500 tonight burns a cycle on a resubmission that is still rejected for items 1 and 2.
- **Timing:** Today is Saturday, so a resubmission tonight likely sits in the same queue as one on Sunday. Use the weekend to fix all three and resubmit Sunday night. I can't see Shopify's current review times, so check the Partner Dashboard for the stated turnaround.

## Item 2: remove the domain field without rebuilding onboarding

Your onboarding doesn't have to change. Only the way you learn the shop's domain has to.

1. **Website button:** Replace the domain form with a plain link to your App Store listing (or your install link).
2. **Shop identity:** Shopify sends your app the shop on install and launch, so you never ask for it. Check that the OAuth or session-token path reads it from there.
3. **Managed installation:** If you still use the legacy OAuth redirect flow, switch to Shopify-managed installation. Declare the scopes in `shopify.app.toml` and use token exchange. This is also the review-friendly default.
4. **Merchants who sign up on your website first:** Let them install from the listing, then link the shop to their website account inside the embedded app. For example, use an email match or a one-time claim code shown in the app. Nobody types a domain anywhere.
5. **Check the whole app:** Search it, including emails and help text, for any other place that asks for the domain.

**Estimate:** 2–4 hours if your backend already keys accounts by shop. Longer if the website account is created before the shop is known. Tell me which case you're in and I'll narrow this down.

## Item 1: Okta SSO blocks the reviewer

Reviewers can't pass your SSO. Give them a path that doesn't need it.

- **Best case:** If the app authenticates through Shopify only, remove the separate login from the reviewed path. Fixing item 2 may remove this blocker.
- **If you keep an external login:** Create a dedicated review account with a password. Use no SSO, no MFA, and no IP allowlist, and seed it with sample data.
- **Instructions:** Put the credentials and step-by-step testing notes in the submission's testing instructions. Add a short screencast.
- **Dry run:** Test it yourself in an incognito window on a fresh dev store, as a stranger would.

## Item 3: the 500 on the settings page

1. Pull the server log for the failing request and reproduce on a fresh dev store. Failures that only appear on a first install with empty settings are the usual cause.
2. Add a regression test for the empty-state case.
3. Return a handled error state instead of a raw 500.
4. Click through the full install → settings → save flow on a new store afterward.

## Schedule

| When | Do |
|---|---|
| Tonight | Fix and deploy the 500. Create the review account. Start the item 2 change. |
| Sunday | Finish item 2. Run a full fresh-store install test. Record the screencast. |
| Sunday night | Resubmit with a reply that answers each note and includes the credentials and testing steps. |
| Mon–Wed | Respond to the reviewer within hours. |

## Launch next Thursday

Approval by then isn't guaranteed. Decide now what you do if it isn't approved:

- **Soft launch:** Announce on Thursday with "available on the Shopify App Store shortly" and a waitlist.
- **Distribution switch:** Don't switch the app to custom distribution just to dodge review. That choice is hard to reverse, so check Shopify's docs and weigh it deliberately.

Do you want help with the reply to the reviewer, or with the install-flow change? For the install flow, tell me whether your backend keys accounts by shop or by website user.