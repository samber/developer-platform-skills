# Allocating the 4 partner-manager hires

## Recommendation

Put 2 hires on the ~40 ISVs and 1 on the long tail. Gate the 4th on a metric and don't fill it yet. The 12 repeat questions are a content and tooling problem, so fix that first, before hiring anyone to answer them.

| # | Role | Owns | Start |
|---|------|------|-------|
| 1 | Strategic ISV partner manager | Top ~10 ISVs by sales through you. Named relationship, roadmap input, co-sell, schema-migration planning, renewal risk. | Now |
| 2 | Growth ISV partner manager | Other ~30 ISVs. Onboarding, review and certification liaison, activation, tiering. Pipeline from long tail into ISVs. | Now |
| 3 | Developer success (long tail) | The ~860 non-ISV developers. Owns Discussions triage, the FAQ-to-docs loop, review-checklist clarity, and office hours. | Now |
| 4 | Technical partner engineer | Schema versioning tooling, migration support, and the pre-submission checker. | Gated, see below |

## Why this split

1. **Revenue sits in 5% of your developers.** The 40 ISVs are the ones that sell through you, so human relationship time pays back there. One manager per ~15-20 ISVs is workable, and two managers cover 40 with a tier split.
2. **The long tail doesn't get named managers.** 860 developers building private integrations for their own employers can't be covered 1:1. They do matter, because they make your customers' accounts stickier, and some will become ISVs. Cover them with self-serve content and one owner for the system.
3. **Hire 3 owns the leak, not the questions.** Their job is to make each repeated question disappear permanently. Each answered thread becomes a docs fix, a checklist rewrite, or a lint rule, and then the thread is closed and linked. If they spend their days answering, the role has failed.
4. **ISVs feel schema-versioning pain more than anyone.** They run production integrations that break on a version change. This is also why the 4th role is technical, since a generalist can't resolve those questions.

## Do this before the hires land (zero headcount, 2-4 weeks)

1. Pull the top 12 questions from Discussions, ranked by thread count. Write one canonical answer per question.
2. Publish a schema versioning page covering the compatibility promise, deprecation window, a changelog, and a migration example per breaking change.
3. Rewrite the review checklist as pass/fail items, each with a rejected-example and an accepted-example. Add the common rejection reasons.
4. Pin the 12 answers in Discussions. Add a Discussions category template that asks the asker to confirm they checked those pages first.
5. Track the repeat-question share of new threads weekly. That's your baseline.

Hire 3 inherits this work and continues it. Hires 1 and 2 shouldn't spend their first months doing it.

## Gate for the 4th hire

Open the technical partner engineer role only if one of these holds after two quarters:

- Repeat questions are still above ~30% of new threads, despite the docs fixes.
- ISV schema-migration issues cause missed deadlines or escalations on 3 or more ISVs.
- The ISV count passes ~60, which pushes manager load beyond ~25 each.

If the first trigger fires, make the hire the technical engineer. If the third does, add a third ISV manager instead. If none fire, return the headcount to Finance.

## Hiring profile

- **Hires 1 and 2:** commercial and technical enough to read an event schema and a diff. Prefer people who've run ISV or marketplace programs. A pure relationship-manager background will leave you where you are now.
- **Hire 3:** a developer-relations or support-engineering background who writes well and enjoys closing loops. Avoid someone who'd rather be a community host.
- **Title check:** Finance approved "partner manager" roles. Confirm that retitling hires 3 and 4 doesn't need a new approval.

## Success measures (review at 90 and 180 days)

- **Repeat-question share** of new Discussions threads, down from the baseline.
- **Median time to first answer** on Discussions.
- **Review pass rate on first submission**, and median days from submission to approval.
- **ISV revenue through the directory**, plus churn or at-risk ISVs flagged early by hires 1 and 2.
- **Long-tail to ISV conversions** per quarter.

## What would change this

- **Revenue is extremely concentrated.** If 5 ISVs make 80% of sales, give hire 1 only those 5, since they justify a near-dedicated manager.
- **Many of the 40 are dormant.** Then you have fewer real ISVs than you think, and one ISV manager might be enough. Move that headcount to the technical role.
- **Employers of the long-tail developers are your top customers.** Then raise hire 3's priority and consider a second developer-success hire.
- **Schema breaks are frequent.** If you ship them often, the real fix is a deprecation policy from product. No hire solves that.

## Open questions

1. How is sales through the directory split across the 40 ISVs?
2. How many of the 860 developers were active in the last 90 days?
3. How often do you ship breaking schema changes?

I'd verify these numbers before locking the split.