# Fennwick on Zapier: plan to Dec 4

I didn't open `skill-wip/` and haven't checked Zapier's current docs. Zapier rules and review times change, so verify the items marked **(verify)** against the Platform docs before you rely on them.

## 1. Read this first

1. **You have six weeks, not five.** Oct 23 to Dec 4 is 42 days. That is your only slack, and US Thanksgiving (Nov 26) falls inside it.
2. **The critical path is Zapier's review, which you don't control.** It has no guaranteed turnaround, and rounds of feedback each take days. Submit by **Fri Nov 6**, not later.
3. **Five things will block approval or the launch claim:**
   - **Name:** "Fennwick for Zapier" will likely be rejected **(verify)**. Zapier's guidelines expect the integration to carry your app's name. Register it as **Fennwick**. You can still call the marketing page "Fennwick for Zapier".
   - **Test account:** the 14-day trial will expire during review. Reviewers need a permanent, working account.
   - **Admin:** your only Zapier admin is on a personal Gmail. If he leaves or loses access, you lose the integration.
   - **Invite-only product:** users who find the listing can't sign up. Zapier may object, and your announcement claim is affected.
   - **No outside users:** nobody has run it yet. Expect bugs, and expect Zapier to want evidence of real use **(verify the exact usage requirement)**.
4. **"Available on Zapier" is only true when the public directory listing is live.** An invite link to a private integration doesn't count. Decide your fallback wording now (section 4).

## 2. Today (Fri Oct 23): five actions

1. Create a **permanent** Fennwick test account. Don't use a trial. Pre-load it with sample contracts, and add a test payment provider so no real money moves.
2. Add 2 company-domain admins to the Zapier developer account. Then transfer ownership off the personal Gmail.
3. Decide the invite-only question: open a self-serve signup for Zapier users, or keep invite-only and plan the fallback wording. See section 4.
4. Confirm the integration name is **Fennwick** in the CLI (`zapier-platform` `package.json` and the developer dashboard).
5. Pick 5 to 8 design-partner customers who will run real Zaps. Ask them now.

## 3. Week by week

### Week 1 (Oct 26–30): fix the foundations

- Finish the account and ownership work from section 2.
- Run all 7 steps end to end with the CLI's `zapier test`. Then run them in a real Zap in the editor. Nobody outside the team has done this yet.
- **Harden "Send Payment Link"**, since it emails a customer:
  - Make the recipient the contract's counterparty, not a free-text address. This stops it being used for spam.
  - Make it idempotent, so a Zap replay or retry doesn't email the customer twice.
  - Rename it to something like "Send Payment Link Email", and state in the description that it emails a customer.
  - Make the editor's "Test action" safe. It really executes, so on the test account it must go to a sandbox address.
- Check naming against Zapier's conventions **(verify)**. Triggers read "New …", searches read "Find …", and actions read "Create/Send …".
- Check each trigger for sample data, deduplication, and a sensible polling interval.
- Draft the listing assets: description, logo, categories, help-doc link, and a support contact.
- **Exit check:** all 7 steps pass in a real Zap, and the payment-link safeguards are merged.

### Week 2 (Nov 2–6): real users, then submit

- Share the private-integration invite link with the design partners. Get at least 3 live Zaps running **(verify the minimum)**.
- Fix whatever breaks. Real users will find auth, pagination, and field-mapping problems.
- Write the reviewer notes for submission:
  - Test credentials.
  - How the invite-only gate works.
  - What "Send Payment Link" does and how it's protected.
- **Submit for review by Fri Nov 6.**
- Start building 3 to 5 Zap templates in draft. Pick pairings with popular apps, such as Slack, Gmail, Google Sheets, and your CRM.
- **Exit check:** submitted, with at least 3 live Zaps from outside the team.

### Week 3 (Nov 9–13): review round 1

- Expect feedback on naming, field labels, sample data, and error messages. Turn each round around within 24 hours.
- Finish the templates. Each one needs a working, tested Zap.
- Write the help docs: one page per trigger, action, and search.
- Check that the test account is still alive and its data is intact.
- **Exit check:** review feedback addressed, templates drafted.

### Week 4 (Nov 16–20): review round 2 and templates

- Answer any second round of review feedback.
- Submit the templates for approval. Template publishing may require the integration to be public first **(verify)**. If so, queue them immediately after approval.
- Prepare the announcement page and the "Available on Zapier" badge and link, but don't publish them yet.
- **Exit check:** integration approved, or only minor feedback left.

### Week 5 (Nov 23–27): go/no-go

- **Tue Nov 24: go/no-go.** Is the listing public, or confirmed to go public before Dec 4?
- Thanksgiving week is slow on Zapier's side. Don't plan on new review rounds landing between Nov 25 and Nov 29.
- Freeze the integration code. Don't ship changes that restart review.
- Prepare both versions of the announcement copy (section 4).
- **Exit check:** decision made and recorded.

### Week 6 (Nov 30–Dec 4): launch

- **Mon Nov 30:** confirm the listing is live at its public URL. Install it from a clean Zapier account that isn't tied to your team, and run a Zap.
- **Tue to Wed:** confirm the templates are visible and clickable, and that the links in the announcement resolve.
- **Thu Dec 3:** final copy check against what is actually live.
- **Fri Dec 4:** announce.

## 4. Fallback wording, decided by Nov 24

| State on Nov 24 | What you can say |
|---|---|
| Public listing live, templates live | "Available on Zapier" with template links |
| Public listing live, templates pending | "Available on Zapier", with templates promised for a date |
| Approved but not yet public, or still in review | "Zapier integration available now for Fennwick customers", with an invite link, and "coming to the Zapier directory" |
| Not approved | Leave Zapier out of the announcement, and post it as its own update when it is live |

Don't write "Available on Zapier" in the announcement until you can click through to the live listing.

## 5. Decisions only you can make

1. **Invite-only vs the directory:** will Zapier users be able to sign up, or does the listing say "existing customers only"? Zapier may require a public signup path **(verify)**.
2. **Who owns the Zapier account long term:** a shared company account with role-based admins is safest.
3. **Whether to ship "Send Payment Link" at launch:** it is the highest review risk. If it slips, ship 6 of 7 steps and add it after launch.

## 6. Top risks

- **Review takes longer than expected.** Mitigation: submit by Nov 6 and answer within 24 hours.
- **Real users find bugs late.** Mitigation: bring design partners in during Week 2, not Week 4.
- **Trial expires or the admin is lost mid-review.** Mitigation: both are fixed this week.
- **Naming rejection forces a rename late.** Mitigation: use "Fennwick" from the start.
- **Post-approval change restarts review.** Mitigation: code freeze in Week 5.

I can also draft the reviewer notes, the listing description, or the design-partner invite email.