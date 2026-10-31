# Flagline GitHub plan to end of June (budget: $3,000)

## 1. Buying, trading and rewarding stars: decline all three

You asked for 2,500 stars. The skill I followed treats stars as a trailing signal, never a target. Of the three tactics the VP found, none is an option. Each one carries risk.

| Tactic | Verdict | Why |
|---|---|---|
| Vendor, 1,500 stars for $1,200 | No | GitHub's Acceptable Use Policies ban "rank abuse, such as automated starring or following" and fake accounts. This is enforced. |
| "Star flagline to enter the drone raffle" | No | GitHub's rules ban engagement "incentivized by ... gifts or other give-aways". Star-for-reward asks are policed. |
| Star swap with the partner | No | Star-for-star trades are policed, and they are rank abuse. |

- **What the research found:** StarScout (He et al., ICSE 2026) found 6.0 million suspected fake stars across 18,617 repositories. Those stars were about five times weaker than real ones and faded within two months. After that they were a liability. About 90% of the campaign repositories were deleted.
- **What that means for flagline:** buying 1,500 stars would take 640 to roughly 2,140 on paper. A fade inside two months would land in May or June, and it would leave a flagged repo behind. The target date is the worst moment for that.
- **What I could not check:** I had no access to the repo, so I could not look at the baseline curve. I made the interview assumptions in section 9 instead.

Reply to the partner, which is template 7 as written:

> Thanks, but we don't trade stars: GitHub treats exchanged stars as rank abuse, and they would make our numbers meaningless to us too. If flagline solved something for you, a short note in Q&A on what you built helps more.

Offer the partner something legitimate instead. Examples are a joint integration guide or a co-written post. Each side links the other's repo in the content and ends it with the star line from template 14, with nothing offered in return. Neither side stars the other's repo as part of the deal.

## 2. Diagnosis

I have no traffic data yet, so I cannot pick a row. Here is how each row of the diagnosis table would play out for flagline:

| If you see | Reading | First action |
|---|---|---|
| Unique visitors flat or falling; npm or docs missing from referrers | No inflow | Fix the registry-to-repo link, then off-platform distribution |
| Visitors rise, stars and dependents do not | The page fails evaluators | README work, then the surfaces in section 3 |
| Downloads or dependents grow, stars flat | Users install from the registry | Change the reported metric (template 8) |
| Usage questions pile up in issues | Support leaks into the tracker | Name an answerer, then open Discussions Q&A |

**Default first action:** archive traffic in week 1 and run the metric swap. When two rows fit, the metric swap goes first. A feature-flag SDK is likely to fit the "downloads grow, stars flat" row, but that is a guess until the numbers are in.

**Numbers to pull in week 1:**
- Views, clones, referrers and paths from the Traffic endpoints. GitHub keeps only 14 days, and nothing recovers older data.
- Watchers, dependents ("Used by") and registry downloads.
- Each of those against the same window one quarter earlier. No absolute threshold exists.
- Star history from OSS Insight, which gives the real baseline monthly star rate.

**The gap in the 2,500 target:** reaching 2,500 from 640 means about 1,860 more stars. That is roughly 230 a month if you count from now. The plan shows no basis for that rate, and nothing shows the target is reachable. I won't promise it.

## 3. Ranked surfaces

Order is value per maintainer hour.

1. **Traffic archive and metric swap.** Near-zero effort and compounding. It tells you which problem you actually have.
2. **Small, frequent releases as feed events.** Each merged fix ships as its own GitHub Release with a written body and "Create a discussion for this release" ticked in an Announcement category. This notifies release watchers and shows on stargazers' and watchers' Feed tab `[documented]`. Compounding.
3. **Topics.** An hour once. Use 5 to 10 accurate topics, each feeding `github.com/topics/<name>` `[documented]`. Search weight is unpublished.
4. **Discussions Q&A.** A standing job of hours per week. It builds an indexed support archive and credits helpers. Compounding.

**Re-rank:**
- If usage questions already arrive weekly in issues and you name an answerer plus a backup, Discussions Q&A moves to rung 2.
- If nobody can answer publicly, delete Discussions. An unanswered tab reads as abandonment.
- Your date is the end of June and the budget is for "this quarter". The deadline is about 8 months away, so no deadline promotion applies. Treat this as a compounding mandate.

**Off-platform reach.** The conference is the real reach event, so it gets its own track. The feed reaches followers, stargazers and watchers, not strangers `[documented]`. Reach beyond them is earned elsewhere.

**Trending.** Trending ranks stars gained inside a window, per language. GitHub publishes no formula, and "star velocity against the repo's own baseline" is `[folklore]`. Getting on it is a launch-sized burst, so plan that separately with the OSS launch skill if you want it.

## 4. Cadence, to end of June

I assumed the dates are 2027, with the conference in May. Owners are roles: DevRel (D), Maintainer (M), Marketing (K).

| When | Work | Owner |
|---|---|---|
| Weeks 1-2 (Nov) | Archive traffic with the Apps Script files. Set Google Alerts for "flagline", "kestrelbyte/flagline" and the package name. Read OSS Insight. Answer open usage questions in issues, oldest first. Set topics. Back-fill release bodies on the last 3 releases. Send the metric note (template 8) to the VP. | D |
| Weeks 2-4 | Open Discussions with two categories (Announcements, Q&A). Add a `contact_links` entry in `.github/ISSUE_TEMPLATE/config.yml` pointing questions to Q&A. Convert 5-10 answered usage issues. Pin the start-here post (template 3). Set labels. Enable Dependabot version updates. | D, M |
| Every release, Nov-Jun | Written release body (template 1), the auto-created Announcement (template 2), then an off-platform post ending with the star line (template 14). Cut a release as soon as one user-visible change merges. Never batch fixes to look bigger. | M, D |
| Weekly | Answer Q&A inside the stated target. Mark answers. Label new issues, PRs and discussions. Merge Dependabot PRs. Convert stray usage issues. Export traffic. | D |
| Jan-Mar | Publish the off-platform content: 3 pieces with one star line each (see budget). Agree the joint content piece with the partner. | D, K |
| Apr (pre-conference) | Booth collateral: QR code to the repo, plus a "Watch > Custom > Releases" line. Prepare the demo. Land a release the week before so the repo shows fresh activity. | D, K |
| May (conference) | Run the booth. Raffle entry is a booth action (scan to see the demo). It is never a GitHub action. Ship a release in the same week. | D, K |
| Post-conference | Post a recap with the template 14 line. Answer every new Q&A and issue the booth generated. | D, M |
| Quarterly (Jan, Apr, Jul) | Read watchers, dependents, downloads and referrers against the baseline. Revise topics. | D |

**Watch asks.** Ask for a watch only where a reader already wants release news: the start-here post, the docs changelog, a solved thread. Ask for a star at the end of content published elsewhere, with no reward and no trade.

## 5. Budget split ($3,000)

- **Vendor stars: $0.**
- **"Star to enter" raffle: $0.**
- **Star swap: $0.**

The skill's top rungs cost maintainer hours, not dollars, so the budget has little to buy. These are proposals with prices I haven't checked:

| Line | Amount | Buys |
|---|---|---|
| Off-platform content | $1,200 | A writer or video producer for 3 technical pieces on flagline. Each ends with the template 14 line and a repo link. |
| Q&A backup | $900 | Part-time contractor hours as the second public answerer, so Discussions never goes unanswered. Skip this line if the interview shows nobody can answer, and delete Discussions instead. |
| Booth collateral | $500 | QR cards and printed handouts with the repo link and the Watch > Releases line. No GitHub-action entry condition. |
| Partner joint content | $300 | Production costs of a co-written integration guide or post. No star exchange. |
| Reserve | $100 | Hold until the first quarterly review. |

**Unspent money:** if the Q&A line is cut, return that $900 or hold it. Don't spend it on stars.

**The drone:** it should come from the event budget, not from "GitHub growth". Keep entry conditional on a demo scan, a badge scan or a booth visit. If you want certainty, have legal or the GitHub terms read the raffle rules, because I'm interpreting the AUP give-away clause rather than quoting a ruling on raffles.

## 6. Templates (fill from your real data)

I left every unknown as a visible `<placeholder>`. I did not run them through a humanizer, so do that before posting.

**Template 1: release body**

```markdown
## <one-line outcome a user gets, not the version number>

<two sentences: who should upgrade, and what changes for them>

### Breaking changes

- <change> - migrate with <link to migration guide>

### New

- <capability> (#<PR>) - thanks @<external contributor>

### Fixed

- <symptom the user saw> (#<issue>)

Install: `<package manager command pinned to this version>`
Questions: <link to the Q&A category>
```

**Template 2: announcement discussion**

```markdown
**flagline <version>: <the outcome from the release title>**

<What changed, in three lines a non-user can follow.>

- Release notes: <release URL>
- Upgrade guide: <URL, or delete this line>

Tell us what breaks or what you build with it in Q&A: <Q&A category URL>.
```

Tick "Create a discussion for this release" on the release form and paste this as the discussion body.

**Template 3: start-here pinned post**

```markdown
Welcome to flagline Discussions.

- **Q&A** - usage questions. Mark the reply that solved it as the answer so the next person finds it.
- **Announcements** - releases and roadmap notes, posted by the team.
- Bugs with a reproduction go to Issues: <issue form URL>.
- Security reports never go here: <SECURITY.md URL>.

The team answers Q&A within <target, e.g. two business days>.
```

**Template 8: leadership metric note (for the VP)**

> GitHub stars measure appreciation and bookmarks (Borges and Valente, 2018), and correlate only moderately with use (He et al., 2026). From this quarter we report:
>
> - Unique visitors and top referrers (Traffic, archived weekly; GitHub keeps 14 days)
> - Watchers (who receive release news)
> - Dependents ("Used by") and <registry> downloads
> - Q&A answered share and median time to answer, once Discussions has a month of history
>
> Stars stay on the sheet as a trailing signal: <current: about 640, confirm> (<change> this quarter).

**Template 14: star ask for content published elsewhere (for posts, talks, booth handouts)**

```markdown
If flagline saved you time, a ⭐ on GitHub helps it grow and reach more people: https://github.com/kestrelbyte/flagline
```

Ask once. Offer nothing in return.

## 7. Metrics to report

- Unique visitors
- Top referrers
- Watchers
- Dependents
- Registry downloads
- Q&A answered share
- Median time to answer (GraphQL `answer.createdAt` minus `createdAt`)
- Cloners are diagnostic only, because CI inflates them.
- Stars appear as a trailing signal, never as a target.

**Reporting the target:** tell the VP that "2,500 stars by June" can't be a commitment. A fair replacement goal reads "watchers, dependents and downloads up against the same window a quarter earlier, with a Q&A median answer time under `<target>`."

**What the conference might add:** if 4,000 people attend and some small share of the people who reach the booth star the repo, that adds some stars. I can't give a number, because I have no conversion rate for this audience. Measure it with the weekly archive and compare it against the OSS Insight star history.

## 8. Pass-bar check

- **Labels:** every ranking or reach claim carries `[documented]` or `[folklore]` above.
- **Hours:** no rung needs more hours than the interview rules out. This rests on my assumptions, so confirm them.
- **Star asks:** none offers a reward or a trade.

## 9. Assumptions to confirm

The skill's interview asks one question per message. I couldn't ask, so I assumed these. Correct any that are wrong and I'll re-rank:

1. Flagline is a company SDK, owned by Kestrelbyte.
2. Leadership reads stars today, and the VP's budget decision hangs on the number.
3. Usage questions arrive as issues or private messages at an unknown rate.
4. The deadline is end of June 2027, and the conference is May 2027. "This quarter" for the budget conflicts with that, so please confirm.
5. You want a compounding asset, not a one-off win.
6. The effort ceiling, the named public answerer and the backup are all unknown.