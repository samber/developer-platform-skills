**Do this first (about 2 hours):** pull the last 3 months of the 600 monthly updates and mark each one against five tests. Does it add scopes, add external endpoints, change data handling, change the payment model, or change the app type? The share that fails none of the five is your fast-path share. Every number below depends on it.

Step 1 of 8 is design inputs. The interview questions about data grant, update propagation, EU exposure and deadline are open. I proceed on stated assumptions and say where an answer would change the design.

## Verdict

Hiring is not the fix. A uniform full review of 640 submissions a month is the problem, and a third reviewer does not change that. Do four things in this order:

1. Stop reviewing minor updates by hand.
2. Make the SAST tool gate developers instead of ticketing reviewers.
3. Cut the 50% first-pass failure with a pre-check tool.
4. Close the update channel, because the fast path opens it.

Use the headcount last, on a security engineer.

## 1. Inputs and assumptions

- Max data grant: assumed (c) read-write business records. If (d) regulated data, keep the hard gate for that tier whatever the volume. If (a) metadata only, loosen everything below.
- Volume: 40 new apps and 600 updates a month. Updates are 94% of submissions.
- Propagation: assumed auto-propagate to installed tenants. If each customer admin upgrades explicitly, the propagation hold in section 5 becomes optional.
- Curation rung: single hard gate today. The skill says to promote it to a **staged gate with fast-path** once update volume makes reviewer cost the binding constraint. Your 6-week queue shows it has.
- Existing SAST moves automation up a rung. The 6-week queue and partner threats are the trigger for promotion.

## 2. Pipeline shape: staged gate with fast-path

- **Full review:** new apps and major versions only. About 40 per month, plus resubmissions.
- **Fast path:** minor updates clear on automated checks, in minutes to hours.
- **Continuous scanning:** covers what the fast path skips.
- **Load estimate:** full reviews per month = 40 + 600 × (1 − minor share). If 80% of updates are minor, that is about 160 a month. At 90% it is about 100. At 50% it is about 340. Compare with 640 today.
- **Fast-path share:** if it comes in under 50%, the staged gate alone will not clear your queue. Come back for a second pass.

## 3. Admission review (new apps and major versions)

Each step is marked automated (A) or human (H).

1. **Intake gate (A):** reject at submission if the SAST run has any open critical or high finding, a secret-scan hit, or an incomplete manifest. The developer gets the reason in minutes. No reviewer sees it.
2. **Permission audit (A, then H):** diff requested scopes against the declared features. A human checks only the scopes flagged as high-risk. High-risk scopes need demonstrated necessity, not declared intent.
3. **Data-access review (H):** external endpoints, subprocessors, retention. Secrets in source, URLs or logs are prohibited outright.
4. **Flow tracing (H):** trace the OAuth, billing and install flow, and check the UI.
5. **Tier escalation (A):** any restricted scope or any write access to customer data moves the app up one tier. Publish this so a developer can self-assess before submitting.

**Pre-check tool.** Give developers the same SAST ruleset and the same manifest checker you run. Require a clean run attached to every submission. This is the direct attack on the first-pass failure rate. About half of first submissions fail at Salesforce's strict gate, and your rate matches. Every rejection must cite the specific violated policy.

## 4. SAST: fix the ticket flood now (week 1)

The reviewers ignore 1,900 tickets a quarter because most are noise. Re-route, don't replace.

- **Developers:** all findings go to the developer, not the review team.
- **Reviewers:** auto-ticket critical and high only, to the developer, with a remediation SLA.
- **Humans:** secret-scan hits are the only signal class routed to a human, for false-positive control.
- **Cadence:** cheap checks daily, per-version checks on release, slow checks monthly.
- **Backlog:** bulk-close the existing medium and low tickets into a dashboard. Triage the open critical and high tickets against listed apps using the enforcement ladder in section 7. Do this first, since listed apps are exposed today.
- **Metric:** track the false-positive rate. If it rises, reviewers learn to ignore the scanner again.

## 5. Re-review on update and publish channel

**Minor update**, objectively defined. It clears the fast path only if it has:

- no new OAuth scopes,
- no new external endpoints,
- no change to data handling,
- no payment-model change,
- no new app type.

The first two are diffable by machine from the manifest. Data handling is declared by the developer. Audit a random sample of declarations (start at 10%). A false declaration triggers publisher-level consequences. Any other change gets full review.

Add an **annual re-review floor for the restricted-scope tier**, to catch drift in apps that never ship an update.

**The fast path becomes the gap unless you harden the channel.** Required controls:

1. Phishing-resistant (FIDO) 2FA on every publisher account.
2. Short-lived scoped publish tokens (7-day default, 90-day max, the model npm shipped after its 2025 worm).
3. A 24 to 48 hour hold between clearance and auto-propagation, with a kill switch inside the window and an expedite path for security fixes. This is mandatory because updates auto-propagate. It costs no reviewer time.
4. Defer OIDC trusted publishing until publisher count outgrows token hygiene.
5. Defer signed artifacts enforced at install. Promote them only if clients execute auto-updated code.

Do not bypass these for your three large partners. Large publishers are the highest-value credential-theft targets. Their updates qualify for the fast path under the same rules as everyone else.

## 6. Appeal path

Stand up a human-reviewed appeal with a stated turnaround, distinct from resubmission, decided by someone who did not make the original call. With two reviewers, independence is the hard part. The new hire or a rotating engineer outside the team can fill it. An appeal channel is cheap to add now. Promote it to a dashboard-integrated button if you serve EU business users (mediation rights under P2B rules) or appeal volume grows.

## 7. Enforcement ladder

Each rung needs an owner, a developer-notice period and the evidence that fires it. Proposed rungs:

1. Finding raised.
2. Remediation SLA by severity.
3. Listing hidden.
4. New installs suspended.
5. Tokens revoked / kill switch.
6. Delisting, with notice to affected customers.

Also write:

- a required security contact per partner,
- graduated publisher-level consequences for chronic or non-responsive submitters, separate from single-app rejection,
- a notice runway of at least 6 months for any new requirement applied to listed apps. This change set needs one, since you are adding pre-checks and publisher 2FA.

## 8. The headcount

Hire a **security engineer who builds automation**, not a third generalist reviewer. Their first jobs are the manifest diff, the SAST tuning and the pre-check tool. Their ongoing jobs are the appeal reviews and the enforcement ladder. Open the requisition now, since hiring takes months, but do not wait for them to ship steps 1 to 3.

## Sequence

- **Week 1:** publish the minor-update definition as policy. Apply it to the current queue, so the queued minor updates clear on automated scan. Re-route the SAST tickets. Tell the three partners this plan with dates, and no promise on the queue length until you have the fast-path share.
- **Weeks 2-4:** intake gate, manifest diff, publisher FIDO 2FA, propagation hold.
- **Weeks 4-8:** pre-check tool, appeal path, enforcement ladder text.
- **Month 3 onward:** annual re-review floor, bounty or disclosure program.

## Gates to check before you ship this

1. Every review tier has an objective escalation trigger a developer can self-assess. Yes (section 3).
2. "Minor update" is defined by objective criteria. Yes (section 5).
3. Every enforcement rung has an owner, a notice period and the evidence that fires it. Fill in the owner and notice period per rung. The rungs are named, the owners are not.
4. The publish channel has FIDO plus short-lived tokens, and a propagation hold if updates auto-propagate. Yes.

## KPIs

- First-pass approval rate. Baseline about 50%.
- Time to first decision against a published SLA.
- Share of updates clearing the fast path.
- Appeal overturn rate.
- Post-approval security findings per quarter, with time to remediation.
- SAST false-positive rate.

## Open questions that would change this

- What can an app touch at its maximum grant? Regulated data keeps the hard gate. Metadata only loosens it.
- Do updates auto-propagate? If not, the propagation hold is optional.
- Do you serve EU business users? If so, the appeal path needs the dashboard-integrated build.
- What is the real fast-path share? Under 50%, the plan needs a second pass.

**Next:** run the five-test pass on the last 3 months of updates and send me the minor-update share.