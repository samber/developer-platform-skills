# AppExchange: 3.0.0 review, the re-review email, and the push plan

**Short answer:** plan for 3.0.0 to be submitted for its own security review. Don't count on it listing under 2.3.0's pass. Do the first two items below today. The push plan has three problems: its timing, its batch size, and the permission-set auto-assignment.

## Assumptions

- You are listed, as a managed 2GP package with an external app or service, and 2.3.0 is the passed version.
- The re-review email names a version, a deadline and a fee. I haven't seen it, so I can't say which.
- 3.0 adds new Apex or LWC that reads and writes records, since an approvals feature has to.
- 2.4.0 was built with 2.3.0 as its ancestor.

## Do first (today)

1. **Update the security contact on Company Info** in the Partner Console. A missed re-review expires every version, and the contact left in May.
2. **Check the email is real.** Confirm the re-review appears in the Partner Console or Partner Community, with its deadline. Don't act on the email alone.
3. **Look for notices missed since May.** Check the mailbox and the Partner Community for review-fee, revenue-share and COA notices. Unpaid review fees or revenue share also expire the review and pull the listing.
4. **Check the OAuth controls deadline.** It was May 11, 2026†, the same month the contact left. It applies to any Connected App or ECA used by more than two customer production orgs, and you have 1,400. The stated sanction is delisting or suspended access†.
   - Confirm PKCE, refresh-token rotation, 30-day idle expiry and the IP allowlist are enabled.
   - These controls can't be undone once on. If they aren't enabled, ship the client changes first, test in a sandbox, then enable them.

## 1. Re-review

- Pay the fee† and submit on time. Prepare it as in `security-review-prep.md`: fresh test org, working credentials, DAST on every in-scope endpoint, false-positive write-ups.
- If it fails, you get about 60 days†. Fix only the flagged issues, across every instance of each class. **Bundling 3.0 features into the fix forces a full initial review and a new fee.**
- Don't merge 3.0 work into whatever package goes through the re-review.

## 2. Listing 2.4.0

- It lists without a new review, because it was built on 2.3.0, which passed. Confirm in the Partner Console that 2.3.0 shows as passed and is 2.4.0's ancestor.
- A version cut during a re-review lists only until that re-review fails. So 2.4.0 is safe now but depends on the re-review outcome.

## 3. Does 3.0.0 need its own review?

The playbook gives two rules that pull in different directions:
- Major and minor versions are submitted for review.
- A version built on the last passed version lists without a new review.

Under the second rule, 3.0 would list on 2.3.0's pass, but 2.4.0 never passed on its own. I'd treat 3.0 as needing review, for three reasons:
- It is a major version.
- An approvals feature is new CRUD/FLS, sharing and SOQL surface. Those are the three most-cited failure classes.
- A re-review is open, so shipping unreviewed new surface now invites a failure.

Confirm with Partner Support or Product Security office hours before you commit. In both cases:
- Keep 3.0 on 2.4.0 or 2.3.0 as its ancestor, not a fork.
- Meet the 75% Apex coverage floor and Lightning Ready certification.
- Mark the approvals feature's internal custom settings, labels and metadata types **protected** before releasing. Once released unprotected, they stay.
- Keep new Apex `global` only where subscribers need it, because global classes can never be removed.

## 4. The push plan has three problems

- **Timing.** "The weekend after Winter" is too early. Push 3-4 weeks after a major Salesforce release†, so mid to late November at the earliest. Avoid customer quarter-end and the holiday freeze, and run a week in sandboxes first.
- **Batch size.** Pushing to all 1,400 at once skips the staged rollout. Start with your own test orgs, then 50-100 production orgs†, off-peak, and widen only on clean results.
- **Auto-assign.** Never auto-assign a new feature's permission set to existing users. A post-install script that does so changes access in 1,400 orgs without admin consent. Instead:
  - Ship the permission set unassigned, with an admin guide.
  - Or assign only on fresh installs, when `previousVersion()` is null.
  - Or gate the feature behind a custom permission.
  - Test the script on upgrade, including orgs where the licenses it needs are missing.

## Realistic timeline (counting forward from 2026-10-30)

| Step | Estimate |
|---|---|
| Re-review, submitted early November | 3-4 weeks to first result† |
| 3.0 review, submitted after the re-review | 3-4 weeks†, plus 2-4 weeks per retest† (about half of first submissions fail†) |
| 3.0 production push | roughly January to March 2027 if one retest is needed |

- The original date works only for 2.4.0, pushed in batches.
- I can't see your submission date or Salesforce's calendar, so treat these as estimates.
- Check the Spring '27 preview-sandbox window against the 3.0 push.

## Open questions

1. Which version does the re-review cover, and what is its deadline?
2. Do the 3.0 approvals touch Agentforce actions? If so, add prompt-injection testing.
3. Are the OAuth controls enabled today?

† Verify every Salesforce fee, duration, date and share against current Salesforce partner docs before quoting it.