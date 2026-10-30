# Flagline: 640 → 2,500 stars by end of June

**Decision needed first:** two of the three ideas break GitHub's rules, and the third works if you change its mechanism. Details are below.

## What to do with the three ideas

| Idea | Verdict | Why | Replace with |
|---|---|---|---|
| Vendor, 1,500 stars for $1,200 | ❌ Don't buy | Paid stars violate GitHub's inauthentic-activity policy. Fake accounts get purged, and your count drops after you've paid. Researchers and scanners (the 2024 StarScout study, Socket-style tools) flag star spikes from empty accounts. Buyers see it, and a feature-flag SDK sells on trust. | $0 here. |
| "Star to enter the drone raffle" | ⚠️ Change the mechanic | Rewarding a star is incentivized starring, which is the same policy problem. It also yields stars from people who never install. | Raffle entry = finish the 5-minute quickstart (a flag evaluated in the SDK). Star ask stays on the screen, unrewarded. |
| Star swap with partner | ❌ Don't do it | Reciprocal starring is inauthentic by the same policy. It's also traceable: both repos get the same cluster of accounts. | Joint integration (below). Real users from the partner's audience star on their own. |

Stars from people who skip the quickstart don't turn into SDK users. The raffle change still counts them as activations, so the VP can report both numbers.

## Target math

- Gap: 2,500 − 640 = **1,860 stars**.
- Honest channels rarely add that evenly. One big Hacker News or trending hit does most of the work.
- My estimate by scenario (assumptions, not benchmarks):

| Scenario | Stars by June 30 | Condition |
|---|---|---|
| Floor | ~1,100–1,400 | Steady content, conference, listings, no breakout |
| Likely | ~1,600–2,100 | One Show HN or trending day lands (300–800 stars) |
| Target | 2,500 | Breakout launch plus a partner integration that ships |

So 2,500 is a stretch goal. Tell the VP the plan gives roughly 60–70% odds of ~1,800+ and needs luck for 2,500. I'd rather say that now than after the fact.

**Timing assumption:** today is Oct 30, so I read "end of June" as June 2027 with the May conference inside the window. If "this quarter" means a Q1 deadline, the plan compresses. Confirm which.

## Plan by phase

1. **Now → Dec: make the repo convertible ($0–300).**
   - Rewrite the README: one-line pitch, 60-second quickstart, a GIF of a flag flipping live, a comparison table vs. alternatives.
   - Add a "Star if useful" line at the bottom of the README. No reward attached.
   - Label 20 `good first issue` tickets. Add a docs site quickstart.
   - Ship an examples repo (Next.js, Go, Python).
2. **Jan → Mar: build the launch asset (~$900).**
   - Publish one benchmark post, for example "flag evaluation latency across SDKs, with a reproducible harness". Developers share these.
   - Cut a 3-minute demo video.
   - Write the Show HN draft and rehearse the first-hour reply plan with engineers.
3. **Mar → Apr: partner integration (~$300).**
   - Ship a joint example repo or plugin with the partner. Both sides cross-link from READMEs and publish a joint post.
   - Run a joint webinar to the partner's audience.
4. **Late Apr: Show HN launch.** Pick a Tuesday–Thursday morning US time. All hands reply for 4 hours. Post to relevant subreddits and Lobsters at the same time. Don't ask anyone to upvote or star.
5. **May: conference (~$1,000).**
   - Booth demo shows a live flag toggle.
   - QR code leads to the quickstart. Raffle entry = quickstart completed, verified by an SDK telemetry event or a form with the API key prefix.
   - Staff ask people to star only after they've seen it work.
6. **May → Jun: compounding ($0–400).** Submit to awesome-lists, directory listings and newsletters (Console, TLDR). Run two talks or meetups off the benchmark. Reply to every issue within 24h.

## Budget split ($3,000)

| Line | $ | Use |
|---|---|---|
| Conference activation | 1,000 | Drone and prizes, QR signage, demo hardware, printed quickstart cards |
| Benchmark and video production | 700 | Cloud compute for benchmarks, video editor |
| Partner integration and webinar | 300 | Design, hosting, promo |
| Contributor program | 400 | Swag and small bounties for `good first issue` fixes |
| Docs and README polish | 200 | GIFs, diagrams, comparison page design |
| Reserve | 400 | Newsletter slots, a second launch attempt, anything that works |
| Vendor stars | **0** | |

If the Show HN fails in April, spend the reserve on a second launch angle (a different post, same repo) in early June.

## Measure it honestly

- Report weekly: stars, **quickstart completions**, SDK installs, and issues opened by non-employees. Stars alone is the metric a buyer would discount.
- Tag every source (UTM on links) so you know which channel produced stars. Cut spend on the ones that don't.
- Don't promise 2,500 to the board. Promise the quickstart-completion and install numbers, and report stars against the 1,100–2,100 range.

## For the VP, one paragraph

Purchased stars and star-for-prize or star-swap schemes break GitHub's policy, risk the count being wiped, and signal weakness to the developers we're trying to win. We can keep her raffle and her partner idea by changing what they reward. Her $3k goes to the launch, the demo and the integration, which produce real stars and real users.

**Open questions:**
1. Is the end of June deadline June 2027? (changes the phases)
2. Does Kestrelbyte have SDK telemetry to verify quickstart completion for the raffle?
3. Which partner, and is a joint integration realistic by March?