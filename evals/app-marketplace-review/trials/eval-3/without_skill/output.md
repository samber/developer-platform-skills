# Tessellate marketplace appeals process: what it should look like

**Do these three things this week:**
1. Reply to the two escalated partners. Tell them their decision will be re-reviewed by someone who was not on the original review, with a written answer by a date you commit to.
2. Stop calling office hours "the appeals process", internally and externally.
3. Ask legal whether the EU rules below apply to Tessellate (details in section 7).

## 1. Diagnosis

Office hours is not an appeals process. The two partners were right.

| Needed for an appeal | Office hours today |
|---|---|
| A way to file a specific decision | A call that anyone can join |
| A deadline you commit to | Every second Tuesday, so up to 13 days before anyone looks at it |
| A reviewer independent of the original decision | None |
| Authority to overturn | None, since nobody present owns the decision |
| A written outcome | None |
| A record | None |

The rejection email makes this worse. It cites no specific reason, so a developer cannot tell what to fix or what to contest. It also never mentions office hours, so most partners don't know the call is the only route.

## 2. Three separate paths

Partners currently mix these up, so name them separately:

1. **Fix and resubmit.** The decision was right, and the developer fixes the problem. This is the default path. It needs a specific rejection reason.
2. **Appeal.** The developer argues the decision was wrong, for example a misread guideline, an inconsistent application, or a factual error. This is a formal path with a deadline and a written outcome.
3. **Office hours.** The developer wants guidance, such as pre-submission questions or "what does guideline 4.2 mean". It is not a decision channel. It also feeds the first two paths.

## 3. Rejection notice (fixes the root cause)

Most appeals come from vague rejections, so fix this first. Every rejection should include:

- The decision and its date.
- **Each failed guideline, by clause number and title.**
- **Specific evidence for each.** For example: "Your app requests the `employee.compensation.read` scope but the listing doesn't describe a use for it" (see guideline 3.1). Include a screenshot, log, or test step where relevant.
- What would resolve each finding.
- Which path applies: resubmit, appeal, or both.
- The appeal deadline, a link to the appeal form, and the committed response time.
- A reply-to address that reaches a person, not a no-reply mailbox.

Template:

> Your submission **[App name]** (ID [x]) was not approved on [date].
>
> **Reasons**
> 1. Guideline [n.n] – [title]: [what we observed, with evidence]. *To resolve:* [action].
> 2. …
>
> **Your options**
> - **Fix and resubmit:** address the items above. Re-review takes up to [N] business days.
> - **Appeal:** if you believe this decision was wrong, file an appeal at [link] within **60 days**. A reviewer who was not involved in this decision will respond in writing within **10 business days**.
> - **Questions about the guidelines:** partner office hours, every second Tuesday [link]. Office hours cannot change a decision. Appeals can.

Add a rule for the reviewers: no rejection ships without a clause number and evidence. Reviewers can't do this well from a free-text box, so give them a structured reason list with required fields.

## 4. Appeal process

**Scope.** Appeals cover rejections, delistings, suspensions, and listing restrictions. They do not cover pricing, ranking, or featuring decisions unless you choose to include them.

**Steps**

1. **File.** The developer uses an in-portal form tied to the submission ID. Required fields are which finding they contest and why, and optional supporting material. Email-only appeals are accepted but get logged into the same system.
2. **Acknowledge** within 2 business days, with a case ID and the expected decision date.
3. **Review** by someone who did not make the original decision. They have the authority to overturn it and are a senior reviewer or marketplace policy owner. They check the original evidence against the guideline and the developer's argument. If the original decision looks right, they check whether it matches how similar cases were decided.
4. **Decide** within 10 business days. The outcome is one of:
   - Upheld.
   - Overturned, and the app is approved or listed.
   - Partially overturned, with some findings dropped and others standing.
   - Sent back for re-review because new evidence changes the picture.
5. **Notify in writing.** The notice gives the outcome and the reasoning for each contested finding. It names the guideline interpretation used, so the developer can see the logic.
6. **Second look (optional).** One further review by a person or small panel outside the marketplace review team, for example the marketplace lead plus someone from legal or policy. Allow it only on a new argument or a procedural error, and limit it to one pass. Without this tier, the first reviewer is still judging their own team's work. Even a light version signals fairness.

**While an appeal is pending**
- A **new** submission stays unlisted.
- An **already-listed** app stays live unless it poses a security, privacy, or legal risk. If you suspend it, say why in the notice.
- A pending appeal never blocks resubmission.

**Guardrails**
- No retaliation. Filing an appeal never counts against a partner in later reviews.
- The appeal reviewer can't be the original reviewer or their direct manager when that is avoidable.
- Keep a case log: decision, reviewer, evidence, outcome, and time taken.

## 5. Office hours

Keep it, but treat it as a feeder rather than a decision venue:

- Rename it to "Partner office hours – guidelines Q&A". Say plainly that it cannot change decisions.
- Move the appeal route to the portal, so no partner has to wait for a Tuesday.
- Log recurring questions and feed them back into the guidelines and the rejection reason text.
- If someone raises a decision problem on the call, the host files an appeal with them on the spot. The host does not try to resolve it live.

## 6. Metrics

Review these monthly:
- Appeals filed as a share of rejections.
- Median time to acknowledge and to decide, plus the share inside the 10-day commitment.
- Overturn rate, broken down by guideline clause.
- Repeat reasons: clauses that generate the most rejections and the most overturns.

Read the overturn rate both ways. Near zero suggests the appeal is a rubber stamp. A high rate on one clause suggests that guideline is unclear or reviewers apply it inconsistently, so fix the guideline.

## 7. EU exposure (needs legal confirmation)

About 40% of your partners are EU-based, which makes this worth a legal check. I haven't verified that any of the following applies to Tessellate:

- **EU Platform-to-Business Regulation (2019/1150)** requires intermediation services to state the reasons for restricting or suspending a business user, and to run an internal complaint-handling system. It is aimed at business users who offer goods or services to *consumers*. Whether a B2B marketplace for HR platforms falls inside that scope is the open question.
- **Digital Services Act**: statements of reasons (Art. 17) and internal complaint handling (Art. 20) for online platforms. Scope is also uncertain for a B2B marketplace.

Either way, the process above is designed to meet the spirit of those rules, which are specific reasons, a complaint route with deadlines, human review, and a written outcome. Legal should confirm whether any of this is legally required, and whether a stricter timeline or a longer filing window applies. Under the DSA, for example, complaint windows are measured in months, not weeks. Don't promise EU partners anything legal hasn't signed off on.

## 8. Rollout

| When | What |
|---|---|
| Week 1 | Handle the two escalated partners through the new process. Stop calling office hours an appeals process. Start the legal check. |
| Weeks 2–3 | Build the structured rejection reasons and the new email. A simple form plus a tracked inbox or ticket queue is enough to start. |
| Week 4 | Launch the appeal path and announce it to all partners. Set the owner and the 10-day SLA. |
| Quarter 1 | Review the metrics, fix the clauses causing the most overturns, and decide whether the second-look tier needs formalising. |

**Decisions needed from you or your VP**
1. Who owns appeals? I'd recommend the marketplace policy lead, not the reviewer team.
2. Is the 10-business-day commitment realistic with current staffing?
3. Is a second-look tier worth building from day one, or only if volume warrants it?