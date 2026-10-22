**First action:** Don't argue the three numbers. Ask for 5 working days to replace them with account-level data, and offer a sprint-sized alternative to archiving. Spend those days on the 6-step data pull below.

## Why the three numbers can't decide this

1. **Downloads count requests, not people.** npm counts every tarball fetch, CI runs and mirrors included. PyPI excludes known mirrors by default. Packagist has its own counting rules, so check them before you quote it either way. A 400k vs 180 comparison across registries doesn't measure users.
2. **The ecosystems differ in size.** PHP is a smaller slice of API-client developers than Python or Node, so a lower number is expected. That doesn't prove PHP is worth keeping.
3. **180 is small, and you shouldn't pretend otherwise.** If you defend 180 as secretly large, you lose credibility. Concede it. Most of the 180 is probably CI, so real users may number in the tens.
4. **Downloads don't show who depends on the SDK.** One customer paying a lot, a WordPress or Laravel integration that wraps it, or a contract clause can outweigh 400k anonymous installs.

## What to do

1. **Pull usage by account (1 day).** Break API traffic out by SDK user-agent, if the SDK sends one. List accounts, calls per month, and revenue or plan tier for the PHP SDK. If the SDK sends no user-agent, say so. That gap is a finding in itself.
2. **Check commitments (half a day).** Search contracts, SLAs, docs and sales decks for PHP support promises. Ask sales and support whether any open deal names PHP.
3. **Check dependents (1 hour).** Look at Packagist dependents and GitHub "used by" for packages that wrap your SDK.
4. **Measure real maintenance cost (1 hour).** Count hours the engineer spent on PHP over the last 3 months, from commits, PRs and tickets. If it's about 2 hours a month, "move them to Go" doesn't require archiving. If it's 40% of their time, the VP has a real point.
5. **Check health signals (1 hour).** Look at open issues, external PRs, last release date, and open security advisories. An unpatched CVE in an archived repo is the worst outcome.
6. **Find out what archiving breaks.** Existing `composer require` installs keep working. New fixes stop, Packagist should show the package as abandoned, and customers on PHP get no notice unless you send one.

## Decision rule (set it before you see the data)

These thresholds are my proposal, not an industry standard. Change them, but fix them before the pull so they aren't picked after the fact.

| Result | Action |
|---|---|
| Zero paying accounts use the PHP SDK, and no contract or dependent needs it | Make the case for archiving. Give 90 days' notice, flag the package abandoned on Packagist, and point to the REST docs. |
| A few accounts use it, or the revenue is small but real | **Maintenance mode** (recommended default). Security fixes only, capped at about 2 h/month, and publish a support end date. |
| Strategic accounts, a contractual promise, or a dependent integration | Keep it supported. Show the VP the revenue at risk. |

## Sprint-sized alternative to archiving

The VP wants the engineer on Go this sprint. Offer this instead:
1. Freeze new PHP features today.
2. Move the engineer to Go starting this sprint.
3. Cap PHP at security fixes, handled by a second person or a rotation.
4. Add a README banner: "maintenance mode, no new features."
5. Re-read the data in 90 days. If usage stays near zero, archive then, with notice.

This gives the VP what they asked for, which is the engineer's time, without an archive you can't cleanly undo. GitHub lets you unarchive, but customer trust doesn't come back as easily.

## Draft message to the VP

> The three numbers compare request counts across registries with different counting rules, and they include CI and mirror traffic. They don't tell us who depends on the PHP SDK. I'm pulling account-level usage, contract commitments, and the real maintenance hours this week, and I'll bring a recommendation by [date]. If the data shows low usage, I'll propose maintenance mode now and archiving after 90 days' notice. That frees the engineer for Go this sprint without a hard cutoff for any customer still on PHP.

## If the data supports the VP

Say so and make the case. A fair archive case has four parts:
1. Real usage is near zero, with account data to show it.
2. The REST API remains available for PHP users.
3. Notice period and migration docs are in place.
4. The engineer's time goes to a stated higher-value Go goal.

Don't defend PHP just because you maintain the team. A clean archive beats a neglected repo.

**Next:** Run step 1. Check whether the PHP SDK sends a user-agent header. That takes about 10 minutes and tells you if the account breakdown is possible at all.