# Update policy for Meridian Stack apps (draft for the partner docs)

The skill's interview asks ten questions one at a time. This was a single-shot request, so I made assumptions instead (listed after the policy). Two of them change the text. Square brackets mark values only you can set.

---

## App update policy

### 1. Two kinds of update

Every update is either a **routine update** or a **reviewed update**. You can decide which one yours is before you submit, using the checklist in section 2. No reviewer judgment is involved.

### 2. Routine update checklist

An update is routine only if **all** of these are true:

| # | Condition | What counts as a change |
|---|---|---|
| 1 | No new OAuth scopes | Any scope in the new version's manifest that the approved version did not request. This includes upgrading read to write. |
| 2 | No new external endpoints | Any hostname or domain, not declared in your approved listing, that receives data from the app or its backend. |
| 3 | No change to data handling | A new data category collected, a new destination or subprocessor, a longer retention period, or a changed purpose for data already collected. |
| 4 | No payment-model change | Free to paid, a new billing party, or a new pricing structure. |
| 5 | No new app type | A new surface, runtime, or edition (for example, adding a webhook receiver or an embedded UI to a data-sync app). |

If any row is "yes", the update is a **reviewed update**. Bug fixes, UI changes, performance work, new features that use already-approved scopes and endpoints, and dependency bumps are all routine.

These conditions are cumulative. Ten routine updates that together add up to a new capability are still routine, as long as each one passes the checklist.

### 3. What happens to each kind

**Routine update.** No resubmission and no waiting for human review. Automated checks run on every release: manifest diff against the approved version, dependency and secret scanning, and endpoint detection. If a check finds a condition from section 2, the update is held and converted to a reviewed update. [Auto-propagating marketplaces: a cleared update reaches installed tenants after a 24-hour hold. Security fixes can request expedited release.]

**Reviewed update.** Submit it for full review: [N] business days target from a complete submission. You get the specific policy cited for any rejection, and you can appeal under [appeal policy link].

### 4. Declare your changes in the manifest

The manifest diff is what we check. If your update adds a scope or endpoint, or changes data handling, declare it in the submission form. An undeclared change that our scanning later detects is a policy violation. It is not a reason to remove the update retroactively on its own; it starts the enforcement process in section 6.

### 5. Higher-sensitivity apps

An app that requests restricted scopes (mailbox, file, or CRM read-write) or write access to customer data is in the **elevated tier**. Reviewed updates in this tier get the full review. In addition, the app is re-reviewed [annually], even with no updates, because an app that never ships can still drift.

### 6. When we find a problem after approval

Findings are handled in this order. Which step applies depends on severity and how you respond.

1. Finding raised, with the evidence attached.
2. Remediation deadline, set by severity: [critical: 24h, high: 7d, medium: 30d].
3. Listing hidden.
4. New installs suspended.
5. Tokens revoked.
6. Delisting, with notice to affected customers.

Repeated unaddressed findings or undeclared changes lead to partner-level consequences, separate from any single app.

### 7. Changes to this policy

New requirements apply to already-listed apps no sooner than [6] months after we announce them.

---

## Notes for you (not for publication)

**Your suspicion is correct, and the cause is the sentence itself.** Your line is Slack's wording almost verbatim ("substantial changes or updates to the features, purpose or functionality"). "Substantial" can't be self-assessed. So the developer decides, the incentive is to say "not substantial", and your reviewers argue the edge cases. The skill classes subjective triggers as a deleted option, not a weak one. Don't try to fix "substantial" with a better definition. Replace the test with facts the platform can check.

**Why this should cut the arguing.** Two of the five triggers (scopes, endpoints) are decided by diffing the manifest, so there's nothing to argue. The other three are declarative and checkable after the fact. The dispute moves from "was this substantial?" to "did you declare it?", and a wrong answer there has a defined consequence.

**Confirm these before publishing, since I assumed them:**

- **Is your hosted backend visible to you?** The manifest can't show server-side behavior changes. Triggers 2 and 3 depend on endpoint detection and the declaration rule in section 4. If you can't detect undeclared endpoints, the policy leans on enforcement more than prevention. Say so internally.
- **Do updates auto-propagate to tenants?** If yes, the 24-hour hold is mandatory, not optional. Every major 2024-2026 marketplace incident rode an ungated update channel.
- **Do the continuous release scans exist today?** Don't publish "automated checks on every release" until they do. The fast path without scanning becomes the gap.
- **What data can apps reach?** If any app holds restricted or regulated data, section 5 is required. If apps only read metadata, you can drop it.
- **EU users?** If yes, the appeal path moves up in priority (P2B mediation rights).

**Capacity.** I can't size it without your trigger rate. At 140 updates a month, every update that fails the checklist lands on two people. Measure what share of the last three months' updates would have tripped a trigger. If it's under about 20%, two reviewers can carry it. If it's near 50%, the checklist is too tight or the review queue needs work.

**Legal.** The sign-off covers the old sentence. This is a different policy with different commitments (the hold, the annual floor, the enforcement ladder), so it needs a fresh pass. Point legal at sections 4 and 6 first.

**KPIs to track once live:** share of updates clearing the fast path, time to first decision, appeal overturn rate, and false-positive rate on the scanners.

**Optional addition beyond the skill:** a sixth trigger for publisher ownership or security-contact changes. It fits the account-compromise pattern behind the incidents, and it's checkable.