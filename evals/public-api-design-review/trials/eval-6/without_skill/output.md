# Unsticking the Quilsworth API PR

**Short version:** the three comments are three different kinds of disagreement, and "BLOCKING" is covering all of them. Split them, settle each by the rule that fits it, and get a human conversation going today. Then add a few process rules so "blocking" has to mean something.

## Part 1: Unstick it (next 2 days)

### Step 1: Check the record before you talk to anyone (30 min)

- Find the written style guide, if one exists. Does it say anything about casing, pagination, or resource nesting?
- Find the review from 14 months ago. Read it literally.
- Check what the existing APIs at Quilsworth actually do for casing.

The reviewer's pagination sentence is garbled: "settled differently last year, so going back to cursors." Before you cite that old sign-off, confirm what it chose and what this PR uses. The reviewer may remember it correctly and you may not. Don't walk into the conversation holding a wrong fact.

### Step 2: Triage the three comments

| Comment | Kind | How to settle it |
|---|---|---|
| camelCase | Style preference | A written standard decides. If none exists, internal consistency and consistency with Quilsworth's existing APIs win. The PR is consistent, so this is **not a blocker**. If your existing APIs are camelCase, that changes the answer, so check first. |
| Nest `/refunds` under `/payments` | Real design trade-off | The author owns it unless the reviewer shows concrete harm. Top-level `/refunds?payment_id=` is defensible. It supports listing refunds across payments, and a refund can outlive or detach from a single payment view. The reviewer should name a specific problem, not just say it reads better. |
| Pagination | Reopening a decision | A signed-off decision stands until someone brings new evidence through the decision process. Taste or memory isn't enough. |

### Step 3: Talk to the reviewer first, privately and with curiosity

Do this today, by call or DM, not in the PR thread. Staff engineers often have context the PR lacks, such as a client SDK convention, a platform migration, or an incident. Ask:

- "What is the concern behind each of these? Is any of them something that breaks if we ship as is?"
- "Which of these would you still hold the PR for if it were the only comment?"

Expect most of it to downgrade once it's said out loud. Don't open with "the author is right." Open with "help me understand what must change before merge."

### Step 4: Run one 20-minute sync with the reviewer, author, and you

- The reviewer states what is truly blocking.
- The author states their rationale for each point.
- You decide anything still open, on the spot. Say plainly: "This is my call, here's why."
- Write the outcome in the PR as one comment, so the thread ends cleanly.

### Step 5: Protect the author

Eight days of limbo is the real cost. Tell them directly that the PR is not their failure and that you're handling the escalation. Don't let them negotiate alone against a more senior person.

### Draft message to the reviewer

> Hey, I want to unblock the payments API PR. Can we take 20 minutes today? Three things in your comment: casing, refunds nesting, pagination. I'd like to understand what's a hard blocker and what's a preference. The design is internally consistent, and I found the pagination sign-off from [date], so I'd like to check whether we're reopening that deliberately or whether there's new information. Happy to hear what I'm missing.

### Draft reply for the PR once decided (adjust to the outcome)

> Outcome of sync with @reviewer and @author:
> - **Casing:** stays snake_case, consistent with [style guide / existing APIs]. Not blocking. Follow-up: [owner] proposes an org-wide convention by [date].
> - **/refunds:** stays top-level with a `payment_id` filter. Rationale: [one line]. Not blocking.
> - **Pagination:** stays as signed off in [link]. Reopen via [process] if there's new evidence.
> - Approved by [name], merging.

If the sync turns up a real issue, such as an existing camelCase client convention, change the outcome and say so. Being wrong in the author's favor is also possible.

### Time box

If the sync doesn't happen by end of tomorrow, you decide and post the outcome. Stalled reviews need a tiebreaker with a deadline.

## Part 2: Stop it happening again

1. **Write the API style guide (one page).** Cover casing, pagination, resource hierarchy, error format, and versioning. Most of this fight was about missing rules. Without them, every review re-litigates preference.
2. **Automate what's mechanical.** Run a linter such as Spectral on the OpenAPI spec for casing and pagination shape. Machines argue about snake_case, not staff engineers.
3. **Keep a decision log (ADRs).** Record the pagination decision with its date and rationale. Add a rule: reopening a decision requires a new ADR with new evidence, not a review comment.
4. **Define what "blocking" means.** A blocking comment must cite one of these:
   - a correctness, security, or compatibility defect
   - a violation of a written standard
   - a violation of a recorded decision

   Everything else is a suggestion or nit, and the author may decline with a reason.
5. **Label comments.** Use `blocking:`, `suggestion:`, and `nit:`, plus a "why" on every blocking one. This takes two seconds and removes most ambiguity.
6. **Add a review SLA and an escalation clock.** For example, first response within 2 business days. If a PR is blocked on a disagreement for 3 days, the two parties get on a call, and on day 5 the named tiebreaker decides. The clock should have fired on day 3 here, not day 8.
7. **Name an API design owner or small API guild.** They are the tiebreaker for API design disputes, so escalations don't land on you ad hoc.
8. **Move design debate before the code.** For new APIs, write a short design proposal, one page or less, and review it before the implementation PR. Casing and hierarchy arguments are cheap at that stage and expensive in a finished PR.
9. **Hold a short blameless retro.** Include the reviewer and the author. Focus on what let this sit for 8 days and which rules above would have prevented it. Don't frame it as being about the staff engineer.

## What to do first

1. Pull the style guide, the old pagination review, and the existing APIs' casing (30 min).
2. DM the reviewer and book the sync for today or tomorrow.
3. Tell the author you're on it.
4. Post the outcome in the PR after the sync.
5. This week, draft the style guide and the "blocking" definition, and bring them to the next eng leads meeting.