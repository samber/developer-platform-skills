# Plan: grow engagement on the SDK repo

I haven't seen the repo, the language, or the product, so this plan rests on a few assumptions. Run the baseline in step 0 first, and send me the results if you want the plan tuned.

**Next action (30 min):** do step 0 below.

## Principle

Stars follow discovery. They are a lagging, vanity signal for an SDK. Flat stars usually mean one of three things:
- People don't find the repo.
- People find it but the README doesn't convert.
- Nothing newsworthy has happened lately.

The plan fixes all three, in that order of cost. It tracks adoption (installs, dependents, issues, PRs) next to stars, because adoption is what the SDK is for.

⚠️ Don't buy stars, run star-for-star swaps, or nag users with in-code popups. These get repos flagged, and they poison the signal you need.

## Step 0: baseline (week 0, ~30 min)

Record these numbers in a sheet, dated:
1. Stars, forks and watchers.
2. GitHub Insights → Traffic: views, unique visitors, clones, and top referrers. This only keeps 14 days, so screenshot it now.
3. Package downloads (npm, PyPI, pkg.go.dev, or whatever applies).
4. "Used by" / dependents count.
5. Open issues and PRs, median time to first maintainer response, and how many outside contributors in the last 90 days.
6. Last release date and release cadence.

The referrers list tells you where traffic really comes from. Double down on those sources.

## Phase 1: fix the storefront (week 1, ~1–2 days)

Do this before any promotion. Otherwise you send people to a weak page.

1. **Repo metadata (15 min).**
   - Write a one-line description that says what the SDK does for whom.
   - Add 10–15 topics: language, product category, and the frameworks it integrates with.
   - Set the website field to the docs.
   - Upload a social preview image (1280×640) that shows the product name and the one-line value.
2. **README (half a day).**
   - Put the value in one sentence and a code snippet that works above the fold.
   - Add install and a "hello world" that runs in under 5 minutes.
   - Show a GIF or screenshot of real output.
   - Add a short feature list, links to docs, examples, and support, and a few badges (CI, version, license, downloads). Keep badges to 4–6.
   - Cut internal jargon and long history.
3. **Examples (half a day).**
   - Add an `examples/` directory with 3–5 runnable examples for the most common use cases, each with its own README.
   - Add one starter template per popular framework.
4. **Community files (1–2 h).**
   - Add CONTRIBUTING.md, CODE_OF_CONDUCT.md, SECURITY.md, issue forms, and a PR template.
   - Turn on Discussions (Q&A and Show and tell categories).
5. **Contributor on-ramp (1–2 h).**
   - Label 10–15 issues `good first issue` and `help wanted`, with a clear scope and a pointer to the files involved.
   - Aim to have these open at all times.
6. **Releases.**
   - Use semver, tagged GitHub Releases, and human-written notes (what changed, why it matters, upgrade steps).
   - Keep a CHANGELOG.

## Phase 2: wire the repo into your own funnel (weeks 2–3)

You already own the traffic. Use it, honestly and without gimmicks.

1. **Docs.** Add a visible "View on GitHub" link in the docs header and on the quickstart page. Add a "Star us" or "Contribute" line only in the footer or at the end of the quickstart.
2. **Dashboard and onboarding.** Add one link to the repo on the post-signup or "first API call succeeded" screen. A single link at a moment of success converts well. Don't use modals.
3. **Package registries.** Make sure the repo URL, README, and keywords are set in the package metadata.
4. **Emails and changelog.** Link new SDK releases from product release emails and the product changelog.
5. **Support.** When support answers an SDK question, link the relevant example or issue. Point bug reports at the repo's issue tracker so the activity is public.
6. **Dogfood.** Link the SDK repo from every sample app, tutorial, and blog post the company publishes.
7. **"Used by" / Built with.** Ask 5–10 friendly customers if you can list them in the README. Real logos and names are strong social proof.

## Phase 3: distribution (weeks 3–8)

Give each push a reason to exist, such as a release, a tutorial, or an integration. Don't post "please star us".

1. **Ship something newsworthy.** Pick one release (a new capability, a big performance gain, or a new language or framework integration) and make it the anchor for the next steps. If you have nothing to announce, build it first.
2. **Technical post (one per 2–3 weeks).** Write walkthroughs of real use cases with working code, such as "Build X with <SDK> in 15 minutes". Publish on your blog first, then cross-post to dev.to and Hashnode with a canonical link.
3. **Community posts.** Share in the relevant subreddits, Hacker News, and X/LinkedIn.
   - Show HN only for something novel, with a working demo, no signup wall, and the founders or engineers around to answer for the first few hours.
   - Reddit gets a real story, not a link drop.
4. **Awesome lists and directories.** Open PRs to relevant `awesome-*` lists, framework ecosystem pages, and "integrations" pages of adjacent tools. This is slow but compounds, because it drives repeat traffic from search.
5. **Integration PRs.** Add your SDK to the docs or examples of frameworks and tools your users already use.
6. **Video.** Record one 5–10 minute screencast per example (a quickstart and one advanced case) and embed it in the README.
7. **Talks and meetups.** Submit the tutorial as a talk or workshop to relevant meetups and conferences, and link the repo in slides.
8. **Cross-link partners.** Do a co-written post or joint example with a complementary project. Both sides send the other traffic.

## Ongoing habits (the real engine)

- **Respond fast.** Aim for a first response within 1–2 business days on issues and PRs. Set up a weekly 30-minute triage slot and give it an owner.
- **Release regularly.** Ship at least monthly, with notes.
- **Thank contributors.** Name them in release notes. Merge small first PRs quickly.
- **Close the loop.** When you fix something a user reported, comment on the issue with the release.
- **Make it easy to cite or share.** Keep the README tagline short and quotable.
- **Review quarterly.** Rerun step 0 and compare.

## Timeline

| When | Work | Effort |
|---|---|---|
| Week 0 | Baseline | 30 min |
| Week 1 | Storefront (Phase 1) | 1–2 days |
| Weeks 2–3 | Funnel wiring (Phase 2) | 1–2 days |
| Weeks 3–8 | Release + posts + directories (Phase 3) | ~2–3 h/week |
| Ongoing | Triage + monthly release | ~2 h/week |

## Metrics

Track weekly, review monthly:

| Metric | Why it matters |
|---|---|
| Unique visitors (Traffic) | Discovery |
| Visitor → star rate | README conversion |
| Package downloads, dependents | Real adoption |
| Issues and PRs from outside the team | Engagement depth |
| Median first-response time | Health signal |
| Discussions activity | Community |

I'd set targets after step 0, using your own baseline. A sensible first goal is to lift the visitor-to-star rate and outside issue/PR volume, and to treat any star bump as a side effect.

## Decisions I need from you

1. Which language and package registry is this SDK in, and what does it do?
2. Is there a launch-worthy release in the next 4–6 weeks?
3. Who owns weekly triage? Without an owner, the plan stalls at the ongoing habits.
4. Can you ask customers for permission to be named in the README?

Send me the step 0 numbers and the repo link and I'll turn this into a concrete checklist with draft README, topics, and post outlines.