# Verdict

The core idea is sound: move "how do I" questions out of the issue tracker. Three parts of the plan are risky as written, and one shouldn't happen at all.

| Part | Verdict |
|---|---|
| Convert the 52 questions to Discussions | ✅ Yes, but pilot first and don't run it Friday afternoon |
| "Close the rest" (22) | ⚠️ Only after you triage them |
| Enable Discussions with 7 categories | ⚠️ Too many |
| "Email support@hollowmere.io" in the issue template | ❌ Replace with a link to Discussions |
| Post in competitor repos to pull people over | ❌ Don't |

## 1. Converting the 52 issues

- **Check the classification.** Sample about 10 of the 52 before trusting it. "How do I..." issues often hide a docs gap, a confusing API, or a missing feature. Tag each one with its root cause. Docs gaps become doc fixes, which cut future questions.
- **Don't run it Friday afternoon.** Every author and subscriber gets a notification, and replies arrive over the weekend. Dana and Yusuf will be offline. Run it Tuesday or Wednesday morning, with both of them on call.
- **Pilot on 3–5 issues.** Confirm what the conversion preserves (comments yes, labels and assignees no, and the issue number is gone) and where links redirect. Confirm the target category is Q&A, since only Q&A supports "mark as answer".
- **Back up first.** Run `gh issue list --state open --limit 200 --json number,title,body,labels,author,comments > backup.json`. Then add a dry-run mode, a log of every issue number and discussion URL, and sleeps between calls. GitHub's secondary rate limits throttle bursts of mutations.
- **Announce it.** Pin a short note first: why this is happening, where questions go, and that nothing was lost. A silent mass move feels like being dismissed, and it's a 1,600-star repo.

## 2. "Close the rest"

You said 52 are questions, so the other 22 are presumably bugs, feature requests, or duplicates. Closing real bugs is the biggest risk in the plan. Triage the 22 individually:

- Real bug: keep it open, add the `bug` label, and ask for a repro if it's missing.
- Feature request: convert it to an Ideas discussion, or keep it open if you track features as issues.
- Duplicate: close it with a link to the original.
- Stale and unreproducible: close it with a comment inviting a reopen.

Never close with a bare comment. If you really do mean to close all 22, tell me what they are and I'll reassess.

## 3. Discussions categories

Start with **Announcements** (maintainers only), **Q&A**, **Ideas**, and **Show and tell**. Add **General** only if people ask for it. Skip **Polls** (it's a discussion format, not something you need a category for) and **Random**. Seven categories on a two-person support team means empty categories, which look dead, and miscategorized posts that someone has to sort.

Write down what Dana and Yusuf commit to before launch:

- A first-response target. Given their capacity, something like 2 business days is realistic.
- A rotation with a named backup, so the load doesn't depend on one person.
- A weekly skim for unanswered questions.
- A canned reply for questions that are actually bugs, so they get moved to Issues.

## 4. The issue template

Don't make email the support channel. Email is private, so each answer helps one person instead of the next hundred who search for the same error. It also turns a shared inbox into a ticket system that someone has to run. And it makes the tracker's redirect look like a closed door.

Do this instead:

- Add `.github/ISSUE_TEMPLATE/config.yml` with `blank_issues_enabled: false`.
- Add `contact_links` that point to the Discussions Q&A category: "Questions and help go here".
- Make the bug template a form that requires version, Python version, a minimal repro, and expected vs. actual behavior.
- Use the email address only for what must be private: security reports (better, enable GitHub private vulnerability reporting) and commercial or account matters.

## 5. Posting in competitor repos

Don't do this, for three reasons:

- **It's unsolicited promotion in someone else's space.** GitHub treats this as spam, and maintainers will hide or delete the comments and may block your account. Screenshots of "Hollowmere is recruiting from our issues" travel fast in a small ecosystem.
- **It damages the project you're trying to build.** A friendly Python client community is your asset. Showing up uninvited to pitch is the wrong first impression.
- **Your support queue isn't ready for a surge.** You're launching the queue this week, and two engineers are the entire capacity.

Better options for the same goal:

- Write a "Migrating from X" guide or a comparison page on your own docs. People searching for alternatives will find it.
- Answer a competitor-repo thread only when you can solve that person's problem. Say you maintain Hollowmere, give the answer, and mention the project only if it's directly relevant. Do it rarely, and check that repo's rules first.
- Post in your own channels once Discussions has a few weeks of good answers to point to.

## Suggested order

1. Triage the 74 issues, sampling the 52 and labeling each root cause.
2. Enable Discussions with 4 categories, a pinned welcome post, and a short FAQ.
3. Rewrite the issue template and `config.yml`.
4. Pilot-convert 3–5 issues and check the results.
5. Convert the rest on a weekday morning, in batches, with a log.
6. Handle the remaining issues individually, not in bulk.
7. After 30 days, review first-response time, the share of questions answered, and what's still unanswered after 7 days. Then decide whether any outreach is worth doing.

Two questions would change the plan:

- What are the other 22 issues?
- Is there an existing support@ inbox with an owner, or is it new?