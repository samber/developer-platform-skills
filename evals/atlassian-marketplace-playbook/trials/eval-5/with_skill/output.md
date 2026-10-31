# Verdict: neither option is OK

Ship a standalone minor-version fix inside the 4-week High deadline†. That deadline is almost certainly already running.

## Why the 9-week plan fails

- **CVSS 7.6 is High.** The fix deadline is 4 weeks†.
- **Your badge makes a miss worse.** With the bug bounty badge, a missed High deadline removes your badges. The app is then hidden after 15 days†.
- **9 weeks is past the hard stop.** 4 weeks plus 15 days is about 6 weeks, and that is counting from today. The AMS ticket is probably older than today.
- **"No exploitation seen" does not change the SLA.** The deadline is set by severity. Extensions are granted only for a breaking change for customers, an Atlassian platform cause or dependency, a third-party block, or a changed risk†. A booked sprint is not on that list.
- **The clock may have started before the ticket.** Bug-bounty findings get two weeks of triage, then count as accepted†. Read the due date on the AMS ticket today.

## Why bundling into the launch release also fails

- **The launch release is a major version.** It adds egress to the AI backend and the `read:confluence-content` scope. Every added scope or egress domain creates a major, and each major re-enters Marketplace review (5-10 business days†).
- **The fix waits behind that review** while the deadline keeps running.
- **Sites stay on the old major until their admin consents.** About 900 paying sites would stay on the vulnerable version, and an XSS fix that most sites never receive does not close the finding.
- **A delay in review or consent puts you past the deadline.** One returned review round would do it.

## Plan

1. **Today:** open the AMS ticket and note the due date. If it is unclear, ask on the ticket when the clock started. Treat the earliest plausible date as the deadline.
2. **Ship the XSS fix as a minor on the current major.**
   - Cloud minor versions publish instantly with no security checks†.
   - Keep the fix free of any new scope, egress domain, remote or auth provider, or it becomes a major.
   - Sweep the issue panel's sibling surfaces for the same unescaped-output pattern, so one fix closes the class.
3. **Get the fix into this sprint.** A stored XSS fix is usually small. Carve a few days out of the AI-feature sprint, because the launch can slip while the deadline cannot.
4. **Close the ticket with evidence:** the version number, a description of the fix, and a re-test against the Bugcrowd report steps.
5. **Then ship the launch major.**
   - Batch the egress and the new scope into it, with release notes telling admins why.
   - Keep the previous major working and backport any later security fix as a minor.
   - Check the scope is justified against a shipped feature. Reviewers check each scope against features, and Ecoscanner flags unused ones.
6. **Watch the launch rollout:** the share of installs on the latest major at 30 and 90 days, and zero AMS tickets past due.

## Assumptions

- The app is Forge (Connect is closed to new submissions and ends support on 31 Jan 2027†). If it is still Connect, the same minor-fix path applies, but check the Connect-era revenue share and migration plan separately.
- The fix needs no new scope or egress.
- The 4-week clock runs from triage acceptance or ticket creation, which I could not confirm.

† Verify against current Atlassian developer docs. Atlassian changed its framework, badge and revenue-share rules within one year. The SLA table is in `references/submission-and-upkeep.md`.