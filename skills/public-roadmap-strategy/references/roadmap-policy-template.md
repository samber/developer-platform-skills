# Roadmap policy, item and slip-notice templates

Read during SKILL.md steps 8-9. Draft the policy section by section; validate each with the user before writing the next.

## Contents

- Policy document template
- Roadmap item template
- Slip notice template, with good and bad examples
- Slip rationalization table
- Format-change notice template

## Policy document template

```markdown
# <Company> public roadmap policy

## 1. Purpose

What the roadmap is for (one sentence tied to the diagnosed problem) and what it is not.

## 2. Posture

Chosen posture, and the postures rejected with one reason each.

## 3. Vocabulary

Each state, what a customer may rely on in it, and whether it carries a time label.
Rule: a quarter appears only with a phase, and only from private preview onward.

## 4. Exclusion gate

Categories never published: security work, unannounced deprecations, pricing and
financials, partner and M&A items, competitive bets, customer-specific commitments,
internal plumbing. Who decides edge cases.

## 5. Legal and sales guardrails

Page disclaimer (counsel-approved text), MSA and self-serve terms clause status,
inventory of existing contracts naming roadmap items, citation rules (link the signed
one-pager), order-form approval path, finance review of dated commitments.

## 6. Feedback surface

Locked items / reactions / frozen board / separate board. Triage owner if any. Exit
plan for a board. Where the untriaged backlog goes.

## 7. Lifecycle

Owner and backup, review cadence, stable IDs, per-item subscription channel, surface,
how items are marked public in the internal tool, changelog close rule, deprecation
links, snapshot at each review.

## 8. Slip playbook

The six steps, who tells contract-dependent customers and how far ahead, legal check
of contractual notices, how long cancelled items stay visible, and pre-page commitments
handled before launch.

## 9. Measurement

Freshness, silent removals, slip rate, close rate, sales incidents, "when will X ship"
volume: baseline, target, owner and review date for each.

## 10. Approvals

Product, sales leadership and CEO (citation rule), counsel, finance where dates appear,
with dates.
```

## Roadmap item template

```markdown
**<Problem-first title>** `<ID>`
Status: <phase or bucket> Timing: <quarter, only if phase >= private preview, else none>
What it solves: <one or two sentences, from the user's side>
Who it's for: <segment or product area>
Discuss: <link to the community thread, not comments here>
Updates: <dated log of status changes, newest first>
Shipped: <changelog link, added when closed>
```

Input: internal ticket "Key rotation v2 - Q3 - committed to Acme renewal".
Output: "**Rotate API keys without downtime** `RM-142` / Status: in design / Timing: none / What it solves: replace a leaked or expiring key while both old and new keys work during the overlap." The Acme commitment lives in Acme's order form under legal review, never on the public item.

## Slip notice template

```markdown
**Update <date>: <item title> is <delayed / descoped / not planned>.**
What changed: <one paragraph, plain reason>
What this means for you: <new status and timing, or none>
Workaround: <what to use meanwhile>
What would change this: <condition, for not planned>
Questions: <thread link>
```

```
// ✓ Good - status changed on the item, reason, workaround, condition to revisit
Update: Webhook replay API is delayed from Q3 (public preview) to Q1 (private
preview). Load testing showed replay can starve live delivery; we are
redesigning the queue first. Meanwhile, the dashboard "Resend" button replays
single events. We'll move back to public preview once replay runs on an
isolated queue.

// ✗ Bad - item silently moved, no reason, no workaround, date reissued
Webhook replay API: Coming Q1!
```

Send the private version to customers with an order-form dependency before the public update.

## Slip rationalization table

The shortcuts teams reach for when an item slips, and why each fails.

| Rationalization                                    | Why it is wrong                                                                                                                                           |
| -------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "Just move it from Next to Later quietly."         | Watchers notice; a silent demotion reads as a broken promise hidden. Mark it `delayed` with a reason.                                                     |
| "Delete it, fewer questions."                      | Deletion erases the record people already cited in deals and plans. Keep it visible as `not planned`.                                                     |
| "We'll clean everything up in one big refresh."    | GitHub's roadmap relaunch removed many items at once with generic notes, and commenters listed tracked features they had lost. Explain each removed item. |
| "Announce the slip in the next newsletter."        | Customers with a contractual dependency learn it in public. Tell them first.                                                                              |
| "It's only a small slip, no need to say anything." | Repeated small silent slips teach readers to ignore every date. Update the item.                                                                          |

## Format-change notice template

Use when the posture or vocabulary itself changes (new site, new phases, retiring a board).

```markdown
## What's changing

| Date   | Change                                    |
| ------ | ----------------------------------------- |
| <date> | <old surface frozen>                      |
| <date> | <new surface live>                        |
| <date> | <old surface archived, redirect in place> |

## What's not changing

<commitments that survive the move: open items migrate with their IDs, history stays readable>

## What happens to open requests

<migrated / closed with reasons / archived read-only, and where>
```
