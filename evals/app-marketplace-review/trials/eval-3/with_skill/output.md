# Appeal path for Tessellate's app marketplace

## Verdict

Tessellate has no appeals process today. Two partners told your VP they cannot contest a decision, and they are right. The call is a good escalation channel, but the review skill is explicit that an escalation channel is "guidance, not an independent re-review of the decision. Never label one an appeal." The rejection email also fails the prerequisite for any appeal: it cites no specific policy, so a developer has nothing to argue against. For a marketplace where about 40% of partners are EU-based, the gap is also a regulatory exposure.

## What exists vs. what is missing

| Element | Today | Needed |
|---|---|---|
| Rejection reason | "did not meet quality standards" (no policy cited) | Specific policy and evidence per finding |
| Independent re-review | None | A human who did not make the original decision |
| Turnaround commitment | None | Published SLA |
| Office hours (every 2nd Tuesday) | Called "appeals" | Keep it, relabeled as an escalation and guidance channel |
| Outcome record | None | Logged outcome per appeal, to feed the overturn-rate KPI |

## Recommended design

The skill's default rung is a defined, human-reviewed appeal with a stated turnaround, distinct from resubmission. Build the first two items below this month.

### 1. Rewrite the rejection notice (week 1)

This is the prerequisite for everything else. Every rejection must contain:

- Each finding, with the specific policy or guideline clause it violates.
- The evidence: the scope requested, the endpoint, the screenshot, or the scan result.
- Whether the finding is fixable by resubmission or contestable by appeal.
- The appeal deadline and the route to appeal.
- A statement that EU-based partners can also use the complaint and mediation routes (see the EU section).

Example replacement for the current email:

> Your submission was rejected on 2 findings. (1) Policy 3.2 (scope minimization): the app requests `employee.compensation.write` but no declared feature uses it. (2) Policy 5.1 (data handling): data is sent to an undeclared endpoint, `api.example.com`. You can fix both and resubmit, or contest either finding by appeal within 30 days. Appeal route: [link].

### 2. Stand up the appeal (weeks 1-3)

Rules, written as policy text:

- **Who can appeal:** any rejection, any delisting, and any listing restriction. The developer can contest individual findings.
- **How:** a form or a dedicated mailbox with a case ID. Require the finding, the reason for contesting, and any new evidence. Start with a form and a ticket queue, not new product tooling.
- **Independence:** the reviewer must not be the original decision-maker. Preferably a senior reviewer or a small panel of two.
- **SLA:** acknowledge within 2 business days and decide within 10 business days. Chrome developers report 1-2 weeks, so 10 is a defensible commitment. Publish the number only if you can meet it.
- **Outcomes:** upheld, overturned, or partially overturned. Every outcome gets written reasons tied to the cited policy.
- **While an appeal is open:** the developer may still resubmit a fixed version in parallel. Do not make them choose.
- **Final step:** after one appeal, a documented path to the VP-level or Head of Trust for exceptional cases only, so escalations stop arriving ad hoc.

### 3. Relabel the office hours

Keep the bi-weekly call. It is useful for guidance, pre-submission questions, and walking through findings. Retitle it "Partner office hours" and say on the page that it is not a decision review. Any partner who raises a contested decision there gets pointed to the appeal form.

## EU exposure (40% of partners)

The skill moves the dashboard-integrated appeal up a rung for EU-facing marketplaces because of the EU Platform-to-Business Regulation (P2B, 2019/1150). Its relevant obligations are:

- A statement of reasons when a business user's listing is restricted, suspended, or terminated.
- An internal complaint-handling system.
- Named mediators for the terms and conditions.

I am not certain P2B applies to Tessellate as drafted. It covers intermediation services that let business users offer goods or services to consumers. Your marketplace connects apps to HR platform customers, which are businesses, so applicability may be arguable. It is also unclear how far the statement-of-reasons duty extends to initial rejections rather than suspensions and delistings. **Ask counsel before relying on either reading.** The design above is cheap enough that I would build it regardless.

Two decisions to take with counsel:

- **Whether to name mediators** in the terms, which P2B requires for in-scope services and which is good practice for the rest.
- **Whether to keep complaint records** for a defined period, as P2B-style complaint systems usually require.

## Phasing

| When | Deliverable | Why |
|---|---|---|
| Week 1 | New rejection template with cited policy and evidence | Prerequisite; zero engineering |
| Weeks 1-3 | Appeal policy text, form/mailbox, queue, named reviewers | Closes the gap the two partners raised |
| Week 3 | Reply to both escalating partners with the new route, and offer them a first review | Resolves the immediate escalation |
| Month 2 | Counsel review of the P2B position, and mediator decision | Settles EU exposure |
| Later | Dashboard-integrated appeal (button on the rejection, pre-populated with the violation context) | Build it when appeal volume or EU exposure justifies the engineering. This is the highest-effort rung. |

Until the dashboard exists, the fix-and-resubmit-only rung is not acceptable for you: the skill allows it solely pre-launch at trivial volume.

## What to measure

Add these to the review KPIs:

- Appeal overturn rate. A high rate means reviewers or policies are inconsistent. A near-zero rate means the appeal is a rubber stamp.
- Time to decision against the published SLA.
- Share of rejections that cite a specific policy. The target is 100%.
- Appeals per 100 rejections. Rising volume is the signal to build the dashboard rung.

## Open questions

The skill's interview asks about the following, and I did not have the answers. Each one could shift this design:

1. What can a listed app touch at its maximum grant? HR data is likely regulated personal data. If so, your review gate stays heavy, and the cost of a wrong rejection or a wrong approval both rise.
2. How many rejections and how many updates per month? This sets reviewer load for the appeal queue.
3. Who reviews today? An independent second reviewer needs at least two people, or a rotation with an external escalation.
4. Do updates auto-propagate to customers? That affects the review rungs elsewhere in the process, not the appeal, but it is worth checking while you are redesigning.

## Update-review questions I did not cover

This answer covers only the appeal path, which is what your VP asked about. The skill also covers re-review on update, publish-channel hardening, and a revocation ladder. If you want those designed too, I can continue from the interview.