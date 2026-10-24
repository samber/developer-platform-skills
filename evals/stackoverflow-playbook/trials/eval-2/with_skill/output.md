# Tarnwick on Stack Overflow: keep it, spend about 90 minutes this week on one thread

## Direct answers

**Should you abandon Stack Overflow for docs?** No. The 41k-view thread is the strongest case against it.
- It still gets traffic, and it tells people to set a variable that no longer exists.
- The playbook cites third-party studies that find Stack Overflow among the domains AI assistants cite for how-to queries. Those studies are unconfirmed and I didn't re-check them.
- The 2019 answer is probably what assistants already know about Tarnwick. Correcting it is the most direct lever you have on your CTO's goal.
- I can't promise that ChatGPT will start giving your answer, or say when. You can only measure it with a monthly spot check (see Metrics).

**What's the minimum worth doing?** Three things:
1. One current answer on the x509 thread.
2. A neutral tag excerpt and wiki with routing.
3. About 15 minutes a week on the tag feed.

Once that's in place, steady state is about 45–60 minutes a week, and the rest can go to docs.

**Can I write the post for you?** Not the technical body. Stack Overflow bans content "crafted, in part or in whole" by an LLM. That means deletion with its reputation, and suspension on repeat. Below are the frame and the disclosure line, plus your own facts marked for you to rewrite and test.

## Posture: Maintain

- **Predicate:** 10 new questions in Q1 (about 3 a month), and 90 minutes a week is under the ~2-hour line.
- **Why not Exit:** the top thread alone has 41k views, so winding down isn't justified.
- **Why not Curate:** it needs a steady flow of new questions, and you don't have one.
- **Revisit** each quarter. Move to Curate if questions climb (my own threshold: more than about 10 a month) or you get hours to spare.

## Ranked actions

The owner is you for all of them. Account reputation is unknown, so I assumed a new account.

| # | Action | Hours | Rep gate | When |
| --- | --- | --- | --- | --- |
| 1 | Answer the x509 thread (details below) | 0.75 | 1 | Week 1 |
| 2 | Tag excerpt and wiki, with routing | 0.33 | any, peer-reviewed | Week 1 |
| 3 | Find the next outdated high-view threads (query below) | 0.25 | none | Week 1 |
| 4 | Remaining time: answer the next-highest outdated thread | ~0.2 | 1 | Week 1–2 |
| 5 | Feed `/feeds/tag/tarnwick` into chat, answer new questions within 48 hours | 0.25/wk | 1 | Ongoing |
| 6 | Batch all edits and answers into one weekly session, since each edit bumps a thread to Active | in #5 | n/a | Ongoing |

**Details for #1:**
- **If the accepted answer is from a Tarnwick staff account,** edit it in place. It keeps the score and the accepted mark.
- **If it's from anyone else,** post a new answer. Never rewrite another author's solution. Edits under 2,000 rep that change intent are rejected.
- **Don't retitle or retag their question.**
- **After 50 rep,** add a short comment on the old answer pointing to the new one.
- **Search first:** if another current thread already covers it, answer there instead of creating a duplicate.
- **Votes:** the new answer needs real votes to rise. Accepted answers are no longer pinned above higher-scored ones. Don't ask colleagues to upvote or accept. Coordinated votes are reversed and can suspend every account involved.

**Don't do:** clear the backlog oldest-first, paste one answer on several questions, or let anyone draft with AI.

## Backlog clusters

Clusters marked (assumed) are guesses until you run the query.

| Cluster | Canonical target |
| --- | --- |
| x509 / unknown authority | The top thread, with a v3 answer. |
| Other removed-in-v3 options, such as `TARNWICK_SKIP_VERIFY` (assumed) | One "removed in v3" migration answer. Flag the rest as duplicates (flagging needs 15 rep). |
| Bugs posted as questions (assumed) | Workaround, plus a disclosed link to the public issue. |
| Account or billing (assumed) | A 50+ rep steward comments the support route and flags to close. |

## Routing (your support page and tag excerpt)

| Question type | Where |
| --- | --- |
| How-to, error messages | Stack Overflow |
| Bugs | `<issue URL>` |
| Feature requests | `<URL>` |
| Account, billing | `<support URL>` |

## Templates

**Answer for the x509 thread.** Staff write everything in brackets, in their own words:

```
[Direct answer in one sentence: TARNWICK_SKIP_VERIFY was removed in v3.]

Fix (v3+):
    tarnwick config set ca-bundle <path-to-CA-bundle>      <- your fact; test it, then explain it yourself

Why it works: [mechanism, staff-written]
Verify: [command and expected output, tested on vX.Y]
For v2 and earlier: [staff decide what to say. Skipping verification is a security downgrade.]

Disclosure: I work at Tarnwick Labs, which maintains Tarnwick.
Reference: <docs page for this error>
```

**Comment on the old accepted answer** (needs 50 rep):

```
This no longer works on v3, where the variable was removed. See the answer below for the current fix. (I work at Tarnwick Labs.)
```

**Redirect comments** (from the playbook templates):

```
Bug:      Thanks, this looks like a bug rather than a usage question. Please file it at <issue URL> with the output above; I've posted the workaround below. (I work at Tarnwick Labs.)
Feature:  Tarnwick doesn't support this today. Feature requests are tracked at <URL>, where the team replies. (I work at Tarnwick Labs.)
Account:  This needs access to your account, which nobody here has. Please contact <support URL>. Flagging to close as not about programming. (I work at Tarnwick Labs.)
```

**Tag excerpt** (neutral, no marketing; reword it yourself):

```
Tarnwick is a secrets manager with a CLI. Use for questions about using the Tarnwick CLI. For bugs, feature requests or account issues, use Tarnwick Labs' own channels.
```

**Tag wiki:**

```
## About
[Two neutral sentences, current major version v3.]
## Before asking
Include the Tarnwick version, OS and full error output. Common problems: [link to the x509 answer, link to the v3 migration answer].
## Where else to ask
Bugs: <issue URL>. Feature requests: <URL>. Account and billing: <support URL>.
```

## Metrics

**Backlog query.** The playbook's Data Explorer query lists threads with no accepted answer, so it would miss your top thread, which has one. Use this variant instead. I adapted it and haven't run it. It lists the top 30 threads by views, accepted or not, so you can spot outdated accepted answers:

```sql
SELECT TOP 30 q.Id AS [Post Link], q.ViewCount, q.Score, q.AcceptedAnswerId, q.CreationDate
FROM Posts q
JOIN PostTags pt ON pt.PostId = q.Id
JOIN Tags t ON t.Id = pt.TagId
WHERE t.TagName = 'tarnwick' AND q.PostTypeId = 1
ORDER BY q.ViewCount DESC
```

Run it at data.stackexchange.com. Open the accepted answers on the top threads and look for removed v2 options.

**Baseline to record this week:**
- Views on the top thread.
- Answer rate under 30 days for the 10 Q1 questions. The target is 90%, which is self-set because Stack Overflow publishes no vendor benchmark.
- Median time to first answer. The target is one business day.
- A monthly spot check: ask three assistants "tarnwick login x509 certificate signed by unknown authority". Note whether each mentions `TARNWICK_SKIP_VERIFY` or `ca-bundle`.
- Hygiene must stay at zero: spam flags, AI deletions, undisclosed-affiliation comments, rejected edits.

## Disclosure and limits

- Every post, including comments, needs the disclosure line. The profile bio doesn't count.
- One person, one account.
- Rep thresholds move. Check the live privileges page.

## Docs follow-up

Mirror the same fix on your docs error page. Getting your docs cited by AI is a separate skill, `samber/developer-relations-skills@developer-docs-ai-visibility`, which I didn't run.

I relied on the playbook and didn't check live Stack Overflow policy or the thread itself.