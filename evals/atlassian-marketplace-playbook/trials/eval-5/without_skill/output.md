**Short answer: neither plan is OK. Fix it inside the existing SLA window, as a separate hotfix. Don't wait 9 weeks, and don't bundle it into the launch.**

I couldn't check Atlassian's current policy text (web access was denied). The Atlassian-specific points below are from memory, so confirm them against your AMS ticket.

## 1. Why waiting 9 weeks fails

- **The AMS ticket has its own due date.** Atlassian's Marketplace security bug fix policy sets remediation windows by severity. I recall High findings being measured in weeks, not quarters, but I can't confirm the exact number. Read the due date on the ticket today. That date, not your sprint plan, is your deadline.
- **A 9-week plan almost certainly misses the High window.** The same policy ties the Marketplace Bug Bounty badge to meeting these windows. Missed deadlines can mean badge removal, listing restrictions, or, for repeated misses, delisting. Your 900 paying sites depend on that listing.
- **"No exploitation seen" is weak evidence.** Stored XSS in a Jira issue panel runs as the viewing user. Usually that is a project admin or site admin, so it can lead to session abuse, issue-data theft, or actions taken as that user. The report is now in at least two parties' hands (the researcher's and Bugcrowd's), and the bug is trivially re-discoverable. You probably can't detect exploitation after the fact, so the absence of signals tells you little.
- **CVSS 7.6 is a floor.** If the stored payload fires for admins, your own scoring may come out higher.

## 2. Why bundling into the launch release is also wrong

- **It couples the fix to a risky release.** The launch adds egress to a new AI backend and a new `read:confluence-content` scope. Any rollback, Marketplace review delay, or launch slip now also delays the security fix.
- **The new scope triggers an upgrade consent step.** Customers must re-approve the scope before the new version takes effect, and some admins will not approve it quickly. The fix then reaches those sites only as fast as they consent, which could be weeks or never. A security fix should not sit behind a consent prompt.
- **The new egress means a new review.** Egress to a new AI backend changes your data-residency and "Runs on Atlassian" or data-handling posture. It needs updated privacy and security disclosures, and may need a re-review. The fix shouldn't wait on that review either.
- **It adds data-theft impact to the bug until the fix lands.** The new scope and new egress path enlarge what a successful XSS could reach. A stored XSS that can read Confluence content and send it to an AI backend is worse than the one reported. The vulnerable code must not ship alongside the new scope, so at minimum, fix before or with the launch, never after.
- **It mixes a security fix with a feature.** That makes the fix harder to test, to verify with the researcher, and to roll back on its own.

## 3. What to do (in order)

1. **Today:** open the AMS ticket and note the due date. Reply to acknowledge it. Ask the Bugcrowd triager for the exact payload and reproduction steps. If you expect any slip, request a documented extension now, before the deadline, not after.
2. **This sprint:** carve out a small fix. A typical fix is output-encoding the user-controlled field in the issue panel, plus a regression test with the researcher's payload and a few variants. Stored XSS fixes are usually small. Trade one unit of AI-feature scope for it if you must, and tell stakeholders the reason: a High finding with a deadline outranks launch scope.
3. **Ship it as its own minimal release**, with no new scopes, no new egress, and no feature changes. That means no consent prompt, so most sites get it on the normal update path.
4. **Check for existing exploitation.** Search stored issue and panel data for script tags, event handlers, and `javascript:` URIs in the affected field. Check logs for odd admin-session activity. Record what you checked and found.
5. **Ask the researcher to verify the fix** and close out the ticket and bounty.
6. **Hold the launch** until the fixed version is released. The launch version must contain the fix regardless.
7. **Customer communication:** if your policy or contract requires notice, or the data search finds anything, prepare a short advisory after the fix ships. Don't publish details before most sites have updated.

## 4. If the sprint truly can't fit it

Ask for the extension in writing, with a dated fix plan. Then ship a stopgap this sprint, such as disabling or sanitizing the affected field server-side. Even a blunt sanitizer or a feature flag that hides the panel field beats waiting.

## 5. Decision summary

| Option | Verdict | Main problem |
|---|---|---|
| Fix in 9 weeks | ❌ | Likely misses the AMS deadline, so you risk the badge and the listing |
| Bundle into launch | ⚠️ | Fix gated by consent, review, and launch risk; wider blast radius |
| Dedicated hotfix this sprint | ✅ | Small, fast, independently testable |

First step: open the ticket and read the due date. If it's inside your 9 weeks, option 3 is the only choice.