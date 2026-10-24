**Do not run the plan as written.** Each of its three parts fails on a Stack Overflow rule or a mechanic that makes it unworkable. Below is what breaks, then a version that works.

## 1. Mass-close 80 as duplicates and edit each

- **Priya cannot close anything alone.** 3,000 rep gives her one close vote. A question needs 5 votes. Only a gold tag badge holder can close as a duplicate with one vote, and a tag with 80 questions almost certainly has no such person. Her 3,100 rep is also only a 100 margin, which matters in section 2.
- **These are probably not all the same question.** "Webhook signature mismatch" has many root causes:
  - the body was parsed before verification, so the raw body no longer matches
  - the wrong secret was used, such as test vs live
  - the timestamp tolerance was exceeded or the clock is skewed
  - a proxy or CDN rewrote the body
  - an encoding problem
  - an SDK version difference

  A question is a valid duplicate only if the canonical answer fixes that asker's cause. Wrong closes get reopened, and askers get angry.
- **The v1 questions are not duplicates of a v2 canonical.** They describe an SDK that no longer exists. Leave them alone, or point them at a separate "v1 sunset, how to migrate" canonical. Old does not mean closeable.
- **The weekend blitz looks like abuse.** Staff of the vendor serially closing one tag's questions to a vendor-written canonical is exactly what moderators and the voting-pattern detectors look for. Expect reversals and a moderator message. Do not ask colleagues to join the votes either, because coordinated voting is reversed too.
- **Do not edit the 80 questions to add a pointer.**
  - Closing as a duplicate already shows a banner linking to the canonical, so the edit is redundant.
  - Every edit bumps the question to the top of the Active list, so 80 edits flood the front page.
  - Adding your own link to someone else's question reads as self-promotion, and edits like that get rolled back.
- **Disclose the affiliation.** Priya's profile and any post that mentions Oakhollow must say she works there.

## 2. Bounties of 100 to 200 rep on 15 questions

- **The $2,000 cannot buy anything here.** Bounties are paid in the offerer's own rep, deducted immediately. Rep cannot be bought, so the budget does not apply.
- **The rep arithmetic breaks Priya.** 15 bounties at 100 to 200 rep cost 1,500 to 3,000 rep. She would drop from 3,100 to somewhere between 100 and 1,600. She would lose the close vote (3,000) and direct editing (2,000), which the plan depends on.
- **Bounties cannot go on closed questions.** The plan closes 80 questions and bounties 15 in the same tag. The two parts contradict each other.
- **"Hardest" is unclear.** In section 1 the premise is that everything in the tag is the same problem. If 15 are truly hard, they are probably product-specific, and outside answerers cannot see your internals. Your engineers should answer those. A bounty only attracts people guessing.
- **Do not pay people off-site to answer on Stack Overflow.** That is rep and vote manipulation territory.

## 3. An Oakhollow Collective

- **It is not a self-serve feature.** Collectives are a partnership deal with Stack Overflow, historically with large vendors. My knowledge of the program's current status may be stale. Ask Stack Overflow before you plan around it.
- **It does not give you your own space.** A Collective sits on the same site, with the same tags, rules and moderation. You get a badge, curated content, and recommended members.
- **80 questions in the tag is too small a base** to justify a paid partnership.
- **For your own space, use your own channel.** GitHub Discussions on the `oakhollow-node` repo is the cheapest. A forum or Discord also works.

## What to do instead

1. **Sample first (about 1 hour).** Read 15 of the 80 and label each by root cause and by SDK version. This tells you how many are true duplicates.
2. **Write one strong canonical answer (about half a day).**
   - Make it a debugging decision tree, one section per root cause.
   - Cover v2 only, with a short note on v1 and a link to the migration guide.
   - Disclose in it that Priya works at Oakhollow.
3. **Fix the cause at the source (1 to 3 days of engineering).**
   - Make the SDK's signature error message list the top three causes and link to the canonical.
   - Add a `verify` helper or CLI command.
   - Fix the docs page.
   - Eighty questions means the product gives poor feedback. This cuts new questions better than any closing.
4. **Close selectively, paced (about 10 minutes a day).**
   - Only close questions whose cause matches the canonical, and only with organic votes.
   - Aim for 3 to 5 a day, not 80 in a weekend.
   - Write a one-sentence custom comment on each.
   - Skip the edits.
5. **Answer the genuinely hard open questions yourselves.** An engineer answers, discloses the affiliation, and no bounty is needed. Keep Priya's rep above 3,000.
6. **Spend the $2,000 on things that move the problem.**
   - a technical writer or contractor for the troubleshooting docs and migration guide
   - test fixtures or a replay tool for webhooks
   - prizes for GitHub issue contributions
   - Do not spend it on Stack Overflow.
7. **Update the tag wiki.** State that SDK v1 is sunset and link to the migration guide. The wiki edit privilege is gated by rep, so Priya can do it.

**Next action:** do step 1. Open the tag sorted by votes, read 15 questions, and label each as one of the root causes above, or "v1". The tally decides how big the canonical must be and how many questions can truly be closed.