**Answer: yes. Treat 3.0.0 as needing its own security review before you push it. Don't push unreviewed code to 1,400 orgs.**

I'm working from memory of Salesforce's ISV policy and didn't look anything up. Confirm each point below in the Partner Security Portal docs or in a Partner Support case.

## Do first (about 30 minutes)

1. Do not use the link in the email. Open the Partner Security Portal directly and check that the re-review request, its due date and its status are real.
2. Add a monitored shared alias, such as security@yourco, as the security contact in the portal and in your Partner Community profile. Remove the contact who left.
3. Open a Partner Support case. Say the notice went to a departed contact, give the dates, and ask for the real deadline. Ask the questions in the last section.

A missed re-review can lead to delisting or other restrictions on the listing. Reply fast, because the original notice has already been sitting unread.

## 1. Periodic re-review

- It is separate from version review. Salesforce re-checks listed solutions on a schedule.
- Ask whether you can submit your newest build as the re-review target instead of 2.3.0.
- Submit one package version, not three.

## 2. Listing 2.4.0

- The version Salesforce approved is 2.3.0. A new version may need approval before you list it or promote it as the installable version.
- Whether 2.4.0 needs a full review depends on what changed since 2.3.0. Small bug fixes may not need one. New features, objects, endpoints, callouts or Apex entry points usually do.
- Diff 2.3.0 to 2.4.0 and write down the security-relevant changes.
- If 2.4.0 has significant changes, don't spend a separate review on it. Skip it and submit the version you actually want everyone on.

## 3. The 3.0.0 push

**Reviewed first.** A new approvals feature is a significant change. It adds a new data-access surface and probably new Apex, UI and sharing logic. Submit it, then wait for approval before any push.

**Post-install script that assigns the permission set to every user.** This is the biggest problem. Reviewers and customers will both object.

- It grants access nobody asked for. In an approvals feature, that can break the customer's separation-of-duties and compliance rules, such as SOX.
- It breaks least privilege, and it is a classic review finding.
- It fails in many orgs:
  - The user may lack the required permission set license, so the assignment errors.
  - Orgs with many users hit governor limits in a single transaction.
  - Mixed DML between setup and non-setup objects can fail.
  - An unhandled error can roll back the install or upgrade, or leave the org half-configured.
- It re-runs on every upgrade. It will re-grant access that an admin deliberately removed.

Do this instead:

1. Ship the permission set unassigned.
2. Add a Setup page or a guided step where an admin picks who gets it.
3. If you must automate, assign only to the installing admin, and handle failures without aborting the install.
4. Test the script in orgs with 5,000 or more users, with no license available, and with the script run twice.

**Timing.** "Weekend after the Winter release" is a risky slot.

- Salesforce's release-window activity creates support noise and can mask your problems.
- Your support team will handle a major version and the platform release at once.
- Push in stages: your own sandboxes, then about 20 friendly orgs, then 10% of orgs, then everyone. Check error rates between stages.
- Send customers advance notice with release notes and a migration guide.
- If approval isn't in hand by that weekend, slip the date. Don't ship unreviewed.

**Rollback.** You can't undo a package upgrade, so write a rollback and hotfix plan before the first push. Fix forward with a 3.0.1.

## 4. Smaller risks

- Run Salesforce Code Analyzer and the portal scanner on 3.0 now. Fix findings before you submit, because each failed submission costs another queue wait.
- Write the test data and credentials a reviewer needs into the submission, so the review doesn't stall on questions.
- Review fees and queue time apply per submission. A rework cycle can take weeks, so plan the date around that.
- Check that every 2.3 to 3.0 upgrade path works, including orgs that skipped 2.4.

## Questions for the support case

1. Can the periodic re-review use my newest build?
2. Does 2.4.0 need a full review, given this diff?
3. Is 3.0 a full or an incremental review?
4. May I push-upgrade orgs to a version that hasn't passed yet?
5. What is the exact re-review deadline?

**Next:** open the Partner Security Portal and check the due date for this re-review (2 minutes). Then paste it here and I'll draft the support case.