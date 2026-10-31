# Ledgerline for Confluence: "Rejected - Timeout", Forbidden ECOHELP link, unexpected charge

**Short answer:** fix the ECOHELP access first, because it probably caused the Timeout. Then stop the billing and test in development. **Do not plan on being listed in 10 days.** Plan the summit around a fallback.

## Assumptions

I couldn't ask questions, so I assumed the following. Correct me if any is wrong.
- Ledgerline is a **Paid via Atlassian** Forge app. You said you "tested the paid flow", so licensing is on.
- The ticket is owned by your cofounder's personal Atlassian account, and no company-account contact is on it.
- You have not yet been told what the Timeout refers to.

## Do now (≈2 hours total)

1. **Get ECOHELP access for a company account.**
   - The Forbidden page almost certainly means your cofounder's account can't open tickets in the Developer and Marketplace Support portal (ECOHELP).
   - Request portal access for a company-domain account through a support request.
   - Then confirm it works by opening a test ticket. Don't assume.
   - A personal account that can't see its own ticket can't answer reviewer questions. That is a plausible cause of "Timeout", though not a confirmed one.
2. **Ask on the ticket what timed out.**
   - Practitioners report most Timeout rejections come from unfinished prerequisites, not from the reviewer.
   - The ask is: "What timed out: a question to the submitter, a scan, or a prerequisite? Please add [company contact] to this ticket."
   - Ask Atlassian whether to reopen the ticket or file a new one. I don't know which they require.
   - Mention the summit date. Expedited SLAs exist only for Platinum, Gold and Silver partners†, so expect no promise.
3. **Stop the charge. See the next section.**
4. **Check every prerequisite while you wait.** Resubmit once, with everything fixed in one pass.
   - Partner verification (KYC/KYB) is done.
   - The app security questionnaire passes, with no Fail answers.
   - The Privacy & Security tab is complete: data stored and where, one justification per scope, trust-center link.
   - The payment profile is set.
   - Privacy policy, End User Terms, a DPA if you process personal data, and documentation are published and linked from the listing.
   - The name reads "Ledgerline for Confluence".
   - You use a company email domain for PvA.
   - Test credentials and sample data for your SaaS are on the ticket.
   - You have a scope and egress list showing the feature behind each scope and the data sent to each host.
5. **Don't change scopes, egress, auth providers or licensing in the resubmission.** Each of those creates a major version and re-enters review, which restarts the clock.
6. **Request listing copy changes on the ticket.** The listing is locked while in review.

## The charge on your own Confluence

**Cause:** every production install of a paid app is billed, including your own. This is expected behavior, not a fault.

1. **Uninstall the production build** from your company site, once you've checked nothing depends on it. This stops further billing.
2. **Ask Atlassian billing or Marketplace support about the charge you already have.**
   - I can't confirm they will reverse it.
   - The playbook documents only a customer refund window: full refund within 30 days†.
   - Raise it quickly, while you are inside that window.
3. **Test in development or staging instead.** Run `forge install --license active` for the paid path, and `--license inactive` or `--license trial` for the other two states. These don't hit production billing.
4. **Check your testers.** Once an app is licensed or submitted, it can't be shared by installation link. Give testers a separate unlicensed copy.

## The 10-day deadline

**Be realistic.** Plan three weeks per review round, plus one returned round.
- Official figures are 10-15 business days† for approval and 5-10† for the security workflow.
- A resubmission is a new round. You can't reliably be listed in 10 days, even if everything goes well.

**Build the summit around what you control:**
- Demo from a development or staging install. Use `forge install --license active` to show the paid flow.
- Tell partners "in Marketplace review, submitted [date]". Don't say "listed".
- Put the resubmission date, the ticket status and the first-day-listed owner on one page.

## Irreversibles register for the resubmission

| Item | Rule | Owner | Date |
|---|---|---|---|
| Payment model (PvA, licensing on) | Switching later is a new version and re-review | Founder | Before resubmit |
| Scopes and egress | Any later addition is a major version needing admin consent | Eng lead | Before resubmit |
| App name | "Name for Confluence" | Founder | Before resubmit |
| Submitter account | A company-domain account with ECOHELP access | Cofounder + you | Today |

## After listing

- Check approval within two rounds.
- Check the share of installs on the latest major at 30 and 90 days.
- Check that no tickets are past due.
- Fix security findings in time†: Critical in 10 days, High in 4 weeks.

† Atlassian figures: verify against current Atlassian developer docs. Atlassian changed its framework, badge and revenue-share rules within one year.

**Questions that would change this advice:**
1. Is the ticket still open, or fully closed?
2. Is Ledgerline paid via Atlassian, or free with a paid account on your SaaS?
3. Which date can a partner at the summit actually use?