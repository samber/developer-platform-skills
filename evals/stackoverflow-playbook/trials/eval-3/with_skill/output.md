# Ferrostack on Stack Overflow: what to do on the three items

All three of his plans break published rules. Each has a safer route that gets the same result. He sits at 212 rep after six spam flags. Another deletion or downvoted post can trigger an automatic answer ban, so he should post slowly and only post correct, disclosed answers.

## 1. The three deleted answers and the rest of his list

**Do not repost or restore the deleted answers, and do not appeal through other accounts or colleagues.** The pattern behind the flags is a rule violation, not bad luck:

- "See our migration guide: <link>" with no disclosure in the post breaks the disclosure rule. His profile line "Core engineer @ Ferrostack" does not count, because the disclosure has to be in the post.
- The two link-only answers are deleted on sight, whatever the link points to.
- Tying every answer to the product breaks the "some but not all" limit on own-product answers.

Steps:

1. **Audit his remaining answers once.** He can edit his own posts at any rep.
   - Any answer that is only a link, or whose substance is "see our guide", gets the working solution written into the post.
   - Every answer that names Ferrostack gets the disclosure line in the post.
   - He should batch these edits over a week, because every edit bumps the thread.
2. **Rewrite any worthwhile deleted answer as a new, complete answer.** Use this shape, with the technical body written by him:

   ```
   <One-sentence direct answer.>

   <Code or steps, runnable as written, with the Ferrostack version tested.>

   Why it works: <mechanism>.
   Disclosure: I work at Ferrostack, which maintains Ferrostack.

   Reference: <link to the docs page this answer summarizes>
   ```

   The link goes last, as a reference. It never replaces the answer.
3. **No generative AI** for any of the drafting, not even a first draft that he checks. Content "in part or in whole" from an LLM is banned, and it is deleted with its reputation.
4. **Do not ask teammates to upvote the rewrites.** Coordinated votes are reversed automatically and can suspend every account involved.
5. **Send the migration-guide traffic through a canonical instead.** The skill ranks a self-answered canonical Q&A for each recurring support theme well above scattered answers. It needs 15 rep, which he has. Use the "Canonical self-answered Q&A" template in `references/templates.md`. Put the disclosure in both the question and the answer. The deprecation question in item 2 is the first candidate.
6. **Check the share of Ferrostack-centred answers.** Most of his history is own-product answers. Going forward he should answer general Rust and database questions in the tag where Ferrostack is not the point.

## 2. The 2021 accepted answer recommending `ferro::migrate::auto()`

**Do not edit it.** The answer belongs to another author, and below 2,000 rep his edit goes to review. Edits that change the intent of an answer are rejected, and rewrites get rolled back. Swapping the recommended API is exactly that kind of edit, and a rejected edit counts against his hygiene metrics.

**Post a new answer on that thread instead.** This needs 1 rep and is the skill's highest-value action: a new answer on a high-view thread with outdated answers. Accepted answers are no longer pinned above higher-scored ones, so a correct new answer can rise on its merits.

1. **Write the answer.**
   - Open with the direct fix: `ferro::migrate::plan().apply()`.
   - Show runnable code and the Ferrostack version tested (0.9 or later).
   - Explain why `auto()` is deprecated.
   - Say what to do on versions before 0.9.
   - Add the disclosure line and a link to the docs page as a closing reference.
2. **Optionally leave a short comment on the 2021 answer.** Comments need 50 rep, which he has. Keep it factual and disclosed, for example: "`auto()` is deprecated since 0.9; see the newer answer below for `plan().apply()`. (I work at Ferrostack.)" He should write it himself, without AI help.
3. **Do not post the same text on other threads.** If other questions hit the same deprecation, flag them as duplicates of one migration canonical. He can flag at 15 rep, but duplicate votes need 3,000 rep or a gold tag badge. Until then, comment with the link or ask an uninvolved high-rep user.
4. **Do not ask colleagues to upvote the new answer or accept it.** Only the asker can accept.

## 3. The competing ORM's answers claiming Ferrostack has no async support

**Do not downvote them. Do not flag them as spam.** The rule is to never downvote, flag, or retag a competitor's posts. A false spam flag is abusive. This is also the same behaviour that got his own account flagged. If the community or moderators later see a vendor engineer mass-targeting a competitor, the response will fall on him.

What he can do, which is more effective anyway:

1. **Post a correct answer on each of the two threads.**
   - Lead with the fact: async has been supported since 0.7.
   - Show a short working async example with the version tested.
   - Link to the changelog or docs section for 0.7 async as a reference.
   - Add the disclosure line.
2. **Optionally leave one factual comment under each competing answer.** Something like "Ferrostack has had async support since 0.7, see <link>. (I work at Ferrostack.)" The comment should correct the false claim, not attack the person or the competitor.
3. **Leave judgement of the competitor's posts to others.** If those answers have undisclosed affiliation or heavy self-promotion, that is a matter for uninvolved community members. Neither he nor any Ferrostack colleague should flag, downvote, or organise others to do it.
4. **Do not brigade.** Colleagues should not vote on these threads at all.

## Order of work for him

| # | Action | Owner | Time | Rep gate |
|---|---|---|---|---|
| 1 | Stop all link-only and undisclosed answers, and pause new posting for a day or two | him | now | none |
| 2 | Post the new `plan().apply()` answer on the 18k-view thread | him | 1 h | 1 |
| 3 | Post the two corrective async answers | him | 1 h | 1 |
| 4 | Edit his remaining answers to add substance and disclosure, in one weekly batch | him | 1 to 2 h | own posts, any rep |
| 5 | Write the migration canonical Q&A | him | 2 h | 15 |

## Hygiene targets

The pass threshold for each of these is zero:

- spam flags on his posts
- AI-drafted deletions
- undisclosed-affiliation comments
- rejected edits

If any of these recurs, stop posting and review before the next answer.

I did not write the technical bodies of the answers, because the staff member needs to write them himself with no generative AI involved.