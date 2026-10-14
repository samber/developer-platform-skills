# Recommendation: contain now, rotate within about two weeks, and don't wait for next quarter

Your boss is right that nothing is broken today. The problem is that "nothing is broken" and "nothing is wrong" are different things.

## Why "clean it up next quarter" is the wrong call

- **Someone outside the company holds valid credentials.** He knows those keys, and you can't prove he didn't copy them. Keys tied to his account may also reach customer data and billing.
- **The outage risk is on someone else's schedule.** If IT or HR deactivates his account (standard offboarding), many platforms kill every key that user created. Then the billing cron, the Salesforce sync, and both customer integrations fail together, at an unplanned time.
- **You can't scope the exposure.** With no view of which keys he created or could see, you can't say what he had access to.
- **It's likely an audit finding.** Offboarding without credential revocation fails SOC 2, ISO 27001, and most customer security reviews. Customer-facing integrations make this a contractual matter too.

The fix is cheap and can be done in a controlled way. Waiting a quarter means carrying the risk for ~90 days for no benefit.

## What to do

**Today**

1. **Ask what his account status is.** Is it disabled, or scheduled to be? If it's about to be, tell IT to pause the deletion (not the login lockout) until the keys are rotated. Test on a non-critical key first if you can.
2. **Freeze the account without deleting it.**
   - Disable interactive login and SSO.
   - Revoke sessions and tokens.
   - Strip admin roles.
   - Keep the user object so the four keys keep working. Confirm with each vendor that disabling login doesn't kill the keys.
3. **Pull audit logs for his last 90 days.** Look for key creation, key exports, and logins from unusual IPs. Also look at use of the four known keys. If anything looks anomalous, or he left on bad terms, this becomes a security incident. In that case rotate immediately and accept a short planned outage.
4. **Add alerting on those four keys.** Flag use from any new IP or at an unusual volume.
5. **Ask for a handover.** Ask him, through HR or legal, for a list of what he created. Don't treat the list as complete, but it speeds up the inventory.

**Days 1–3: build the inventory from the consumer side**

There is no screen showing his keys, so find them by who uses them.

- Check each vendor's admin console, API, or audit log for credentials created by or owned by his user. Examples: Salesforce connected apps and OAuth usage, cloud IAM credential reports and last-used dates, and your billing provider's API key list.
- Search repos, CI/CD variables, secrets managers, cron hosts, and config management for key prefixes and references.
- List every customer integration that holds a credential from us or for us.
- Treat anything he *could see* as exposed, not just what he created. That includes the shared vault, CI secrets, and env vars on boxes he could reach. Rotate those too.
- Recover his laptop and devices.

**Week 1–2: rotate in this order**

1. **Billing cron.** It's internal and fully under your control, so it's the safest to cut over first. Make sure the job is idempotent so an overlap can't double-charge.
2. **Salesforce sync.** Internal, with a moderate blast radius.
3. **Customer-facing integrations last.** Some may need customer coordination, so give notice and an overlap window.

For each key:

1. Create a replacement owned by a **service account or machine identity**, not a person.
2. Use least privilege and store it in a secrets manager.
3. Deploy the replacement and verify it works.
4. Revoke the old key.
5. Record the owner, purpose, and rotation date.

**After the keys are rotated**

- Delete his account fully.
- Write a short post-mortem.
- Add a credential inventory step to the offboarding checklist.
- Add a quarterly access review.
- Set expiry and rotation on all service keys.

## How to put it to your boss

> "The keys work today, but they're owned by someone who no longer works here. If IT deactivates his account, billing, Salesforce sync, and two customer integrations go down at once, on a day we don't choose. If he or anyone with his credentials misuses them, we can't see it. A two-week controlled rotation costs a few engineer-days. The alternative is an unplanned outage or an audit finding."

Ask for a decision on two things:

- A named owner for the inventory.
- A two-week deadline for rotating the four known keys, with the inventory done in parallel.

## Things to avoid

- **Don't revoke his keys right now.** It would cause the outage you're trying to prevent.
- **Don't assume the four keys are the complete set.** Treat them as the ones you've found so far.
- **Don't rotate customer keys without notice.** Coordinate with the customers first.
- **Don't accept "next quarter."** A fixed date two weeks out is a reasonable compromise if your boss wants to schedule it, as long as the freeze and alerting happen today.