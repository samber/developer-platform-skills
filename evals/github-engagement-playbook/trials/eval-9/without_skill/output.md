**Next action (10 min):** open the repo's Insights → Traffic. Pull unique cloners and the referrer table for the last 12 weeks. Everything below depends on those numbers.

## Verdict

Awareness is not the bottleneck. Traffic went from ~400 to ~1,100 unique visitors/week, so the podcasts and the talk worked. The leak is after the visit: people arrive, then don't star, install or adopt. Doubling down on awareness would send more people into the same leak.

I haven't seen the repo or README, so this is a diagnosis from your numbers. Step 1 tests it.

Rough math:
- Extra visitors: ~700/week above baseline, so a few thousand since launch.
- Extra stars: ~35.
- Star rate on that traffic is well under 1%.

That is low, but I can't call it bad without the baseline conversion from before the campaign.

## Plan

**Step 1. Diagnose the funnel (about 2 hours, Mon).**
1. Chart weekly unique visitors, unique cloners, and release/container-image downloads together. Stars and "Used by" are lagging and weak signals.
2. Split by referrer: podcast show notes, conference site, and everything else. Compare cloners per visitor across them.
3. Open the show-notes links and check where they point. A bare repo link is a weak landing for an audio listener.
4. Check what "Used by" counts. It is GitHub's dependency graph, which only counts repos that declare your package in a manifest. An agent installed as a binary or container image may never move that number, however well it adopts. If so, "stuck at 12" is the wrong metric, not a failure. I'm flagging this as a hypothesis to confirm.
5. Ask an engineer: do podcast listeners match the people who deploy this agent? Audio reaches broad audiences, but buyers of observability tooling often evaluate for weeks or months.

**Step 2. Pick the metric (30 min).**
- Use conversion rate: unique cloners (or release/image downloads) ÷ unique visitors.
- Drop stars as the success measure. They only go up, so they can't show a regression.
- Add a support-load count: issues per month asking "how do I install" or "what does this do".
- Record today's value as the baseline.

**Step 3. Audit the README before rewriting (half a day, Tue).**
1. Score it as a stranger would. Ask someone outside the project to read it for 60 seconds, then answer five questions: what is it, who is it for, how do I install it, what state is it in, why this over alternatives.
2. Get an engineer to run the install and first example from a clean machine, exactly as written. Note every undocumented step. This usually returns the most.
3. Check every claim against the code: flags, defaults, performance numbers, "production ready". Cut anything unverifiable.

**Step 4. Fix three things first (Wed–Thu).**
1. **Status line.** Maintained, beta, or stable, with the release cadence. Only ~21% of READMEs state this, and evaluators look for it.
2. **Install path.** Make it run end to end from clean, with prerequisites listed.
3. **Differentiation paragraph.** Why this agent over the alternatives, plus what it deliberately doesn't do and when to use something else. It must be true and specific; do not use superlatives such as "fast" or "lightweight" without a number. If the founder can't name the alternatives in one sentence, that is a finding in itself.

Other points:
- Draft three one-liner options (what it does, what problem it removes, what it lets you stop using). Let the founder pick, because the line also goes into the repo description and link previews.
- Cap the badge row at about four. Keep only badges backed by a real check, such as CI status or the published version.
- Keep contributing, security and conduct text in their own files.
- You can lead the rewrite, but an engineer must verify every command and claim. That is the one part marketing can't do alone.
- Skip a terminal demo for now unless the CLI output is the product. If it is, generate the demo from a script.

**Step 5. Redirect podcast traffic (Fri, 1 hour).** Where hosts allow edits, point show-note links to a quickstart page with per-show tracking (UTM or a short link per show), not the bare repo. Then you can see which show converts.

**Step 6. Re-measure (4–6 weeks after the README ships).**
- Compare the full period before and after, and note confounders such as releases or new episodes.
- Pass: conversion rate rises and install-question issues fall.
- If conversion is flat after a README that passes the cold-reader test, the audience or product-fit may be the issue, and that is a different conversation.

## What to tell the founder

1. "Awareness worked: traffic is ~2.75×. The test now is conversion. We'll fix the page those visitors land on, then re-measure."
2. Keep already-booked podcasts. Pause new bookings for ~6 weeks, until the conversion number exists.

## The founder's three tactics

- **More podcasts:** later, not now. Each one currently sends traffic into the same leak. Revisit after Step 6, or for a dated milestone such as a 1.0.
- **Submitting to GitHub Explore collections:** don't self-submit. Curated surfaces tend to reject self-promotion. Earn a place through community users or contributors, which is slower but sticks.
- **Posting in popular repos' issues:** don't. It reads as spam, can get the account blocked, and damages the brand with the exact engineers you want. A better route is answering observability questions in forums and issues where your agent is directly relevant, with disclosure and no pitch.

## Estimated effort

About 2 days of your time, plus ~2 hours of engineer time for the clean-install test and claim checks. Then a 4–6 week wait for results.

**Open question for you:** is the agent installed as a library (Go module, npm package) or as a binary/container? That decides whether "Used by" can move at all. Reply with that and your Step 1 numbers, and I'll refine the plan.