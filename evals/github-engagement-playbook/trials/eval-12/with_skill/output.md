# GitHub engagement plan for the official SDK repo

I couldn't see your repo, traffic, or registry numbers, and you asked for the plan without the interview. So the diagnosis below is a decision table, not a verdict. Every step is safe to start before the diagnosis lands.

Label key: `[documented]` means GitHub docs or policy. `[folklore]` means practitioner inference, not fact.

## 0. Assumptions to confirm

I assumed these where I had no answers. Correct any that are wrong and I'll re-rank.

| # | Assumption | What changes if wrong |
|---|---|---|
| 1 | Company SDK, compounding goal, no hard deadline. | A date inside 2 months promotes rungs 1-3. A one-off win cuts the plan to rungs 1-2. |
| 2 | Leadership reads stars. | If the decision hangs on stars, template 8 becomes the first conversation. |
| 3 | Usage questions arrive as issues or private channels. Count unknown. | If there are none, drop Discussions Q&A. |
| 4 | Nobody is yet named as public answerer. | Without a named answerer and backup, **do not open Discussions**. An unanswered tab reads as abandonment. |
| 5 | Effort ceiling is about 3-4 h/week. | Cut rung 4 first if it is lower. |

## 1. Diagnosis (do this week, about 1 h)

**Step 1: start archiving traffic.** GitHub keeps traffic for only 14 days, shows the top 10 only, and requires push access `[documented]`. Nothing recovers it later.
- Endpoints are `/repos/{owner}/{repo}/traffic/views`, `/clones`, `/popular/referrers` and `/popular/paths`.
- Create a Google Sheet with a tab `List GitHub repositories` (owner in column A, repo in column B, from row 2).
- In **Extensions > Apps Script**, paste the bundled files `github-repositories.gs`, `github-search.gs`, `github-dependents.gs`, `github-utils.gs` and `utils.gs`.
- Under Script properties, set `GITHUB_TOKENS` and `GITHUB_PROFILE`. Never put a token in code.
- The token needs push access on the repo: classic `repo` scope, or fine-grained Administration read.
- Run `mainGithubRepositories` once and approve the permissions prompt.
- Add a weekly time-driven trigger for each of `mainGithubRepositories`, `mainGithubSearch` and `mainGithubDependents`.
- Chart the sheet's columns except `code_unreliable`, which returns inconsistent totals on GitHub's side. The dependents script scrapes the public "Used by" page and breaks when GitHub changes it.

**Step 2:** Create Google Alerts (weekly, all results) for `"<project>"`, `"<owner>/<repo>"` and the package name. Open the repo's page on OSS Insight to date past star spikes against releases and posts.

**Step 3: pull the baseline.** Gather watchers, dependents ("Used by"), registry downloads, and unique visitors and referrers. Compare each against the same window a quarter earlier. No absolute threshold exists.

**Step 4: classify.** If two rows fit, run the metric swap first.

| What you see | Reading | First action |
|---|---|---|
| Unique visitors flat or falling, and the registry page or docs missing from referrers | No inflow. GitHub is not the bottleneck. | Fix the registry-to-repo link (`samber/developer-platform-skills@sdk-package-publishing`), then go off-platform via `samber/developer-relations-skills@oss-distribution-strategy`. |
| Visitors rise, stars and dependents do not | The page fails evaluators. | `samber/developer-relations-skills@readme-optimization`, then § 2. |
| Downloads or dependents grow, stars flat | Users install from the registry and never star. | Swap the reported metric (template 8). Stop chasing stars. |
| Usage questions pile up in issues | Support leaks into the tracker. | Name an answerer, then open Discussions Q&A. |

**For an official SDK, the third row is the most likely one.** Stars measure appreciation and bookmarking, and correlate only moderately with use (Borges and Valente 2018, He et al. 2026). I haven't verified that your numbers fit it, so check the data first.

## 2. Ranked surfaces (value per maintainer hour)

1. **Traffic archive and metric swap.** Near-zero effort. It tells you which problem you have. Compounding.
2. **Small, frequent releases as feed events.** Minutes to an hour per release.
   - Ship each merged fix or feature as its own GitHub Release with a written body.
   - Tick "Create a discussion for this release" and use an Announcement category.
   - This notifies release watchers and shows on stargazers' and watchers' Feed tab `[documented]`.
3. **Topics.** One hour, once. Use 5-10 accurate topics. Each feeds `github.com/topics/<name>` `[documented]`. Search weight is unpublished.
4. **Discussions Q&A.** Highest value, but a standing cost of hours per week. It builds an indexed, answered support archive.

**Re-rank stated:**
- Discussions moves up to rung 2 only if you have weekly usage questions and a named answerer plus backup.
- If you have no answerer, delete it from the plan.
- Under assumption 1 the order above stands.

## 3. Do more, do less

**Do more:**
- **Release small and often.** One real change plus a one-line body is enough. Never batch fixes to make a release look bigger.
- **Keep the repo visibly active.** The home feed shows activity from people and repos a user follows or stars `[documented]`. Recommendations lean toward recently active repos `[folklore]`.
- **Turn on Dependabot version updates.** Weekly PRs keep "last updated" fresh at near-zero effort, and the security patches are real value anyway `[folklore]` on the freshness effect.
- **Post release and roadmap notes in an Announcement category.** Only maintain or admin roles can open them `[documented]`.
- **Mark Q&A answers.** GitHub highlights the answer `[documented]`.
- **Ask for stars in content published elsewhere.** End each blog post, talk, newsletter or video with one line (template 14). Many GitHub rankings depend on star counts, and Explore lists popular repos by stars `[documented]`.

**Do less:**
- **Don't expect the feed to reach strangers.** It reaches followers, stargazers and watchers. Reach beyond them is earned off-platform.
- **Don't chase Trending day to day.** GitHub publishes no formula. "Star velocity against the repo's own baseline" is `[folklore]`. Trending needs a launch-sized burst, planned with `samber/developer-relations-skills@oss-launch`.
- **Never publish a release with an empty body.**

Treat any feed or ranking claim older than a year as stale until it's re-checked against GitHub's changelog.

## 4. Cadence

I used relative weeks because you gave no landing date. Week 1 starts the Monday after you read this. The owner is a role: the maintainer on duty unless noted.

| When | Actions | Owner |
|---|---|---|
| **Weeks 1-2: earn first** | Run the traffic archive (§ 1). Answer open usage questions in issues, oldest first, inside the effort ceiling. Set 5-10 topics (lowercase, digits and hyphens, max 20 topics). Back-fill bodies on the last 3 releases with template 1. | Maintainer, DevRel for the sheet |
| **Weeks 2-4** | Open Discussions with two categories, Announcements and Q&A. Add a `contact_links` entry in `.github/ISSUE_TEMPLATE/config.yml` pointing questions to Q&A. Convert 5-10 answered usage issues with template 5, which is well inside the rate limit. Pin the start-here post (template 3). Apply the label scheme from `references/labels.md` (about 15 labels, GitHub's default spellings). Enable Dependabot version updates. | Named answerer, with a backup |
| **Every release** | Write the release body (`samber/developer-relations-skills@changelog-writing`). Tick the auto-created Announcement. Then publish an off-platform post that ends with the star line. | Releaser |
| **Weekly** | Answer Q&A inside the stated target. Mark answers. Label new issues, PRs and discussions. Merge Dependabot PRs. Convert stray usage issues. Check that the traffic export ran. | Answerer |
| **Quarterly** | Read watchers, dependents, downloads and referrers against the baseline. Revise topics. Re-check any ranking claims. | DevRel |

**Where to ask for a watch:** only where the reader already wants release news. That means the start-here post, the docs changelog page, or a solved thread (template 6).

**Where to ask for a star:** at the end of content published elsewhere, with no reward. Never ask in other repos' issues.

### Limits to respect

- **Rank abuse is banned.** The Acceptable Use Policies ban "rank abuse, such as automated starring", fake accounts, bulk promotion, and engagement "incentivized by ... gifts or other give-aways". Enforced.
- **Rate limits are enforced.** Roughly 80 content-creating requests per minute and 500 per hour, web UI included. This bites on bulk issue conversion.
- **Repo limits are enforced.** Discussions allow 25 categories, with 4 global pins plus 4 per category.
- **Other repos' issues and PRs are policed.** No promotion there. Only post a disclosed answer to that exact issue.
- **`github/explore` is policed at review.** Self-promotion is "unlikely to be accepted".
- **Awesome lists set their own rules.** An author's PR that meets their criteria is usually accepted.
- **Star-for-star and "star to enter" asks are policed.** The give-away clause also applies.

### Never buy, trade or reward stars

StarScout (He et al., ICSE 2026) found 6.0 million suspected fake stars across 18,617 repos. They were about 5 times weaker than real stars and faded within 2 months. About 90% of the campaign repos were deleted. If anyone proposes it, send template 7.

## 5. Filled templates

I've left unknowns as `<placeholders>`. I haven't invented any facts.

### Template 1: release body

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

Delete any section that is empty for this release.

### Template 2: announcement discussion

Tick "Create a discussion for this release" and paste this as the body.

```markdown
**<SDK name> <version>: <the outcome from the release title>**

<What changed, in three lines a non-user can follow.>

- Release notes: <release URL>
- Upgrade guide: <URL, or delete this line>

Tell us what breaks or what you build with it in Q&A: <Q&A category URL>.
```

### Template 3: start-here pinned post

```markdown
Welcome to <SDK name> Discussions.

- **Q&A** - usage questions. Mark the reply that solved it as the answer so the next person finds it.
- **Announcements** - releases and roadmap notes, posted by the team.
- Bugs with a reproduction go to Issues: <issue form URL>.
- Security reports never go here: <SECURITY.md URL>.

The team answers Q&A within <target, e.g. two business days>.

Want release news without the issue noise? Click **Watch > Custom > Releases** on <repo URL>.
```

This version includes the watch ask (template 6). Set the response target only if the named answerer and backup can keep it.

### Template 8: leadership metric note

GitHub stars measure appreciation and bookmarks (Borges and Valente, 2018), and correlate only moderately with use (He et al., 2026). From this quarter we report:

- Unique visitors and top referrers (Traffic, archived weekly; GitHub keeps 14 days)
- Watchers (who receive release news)
- Dependents ("Used by") and <registry> downloads
- Q&A answered share and median time to answer, once Discussions has a month of history

Stars stay on the sheet as a trailing signal: <current> (<change> this quarter).

### Star ask for off-GitHub content (template 14)

Put this at the end of each blog post, talk, newsletter or video description. Ask once and offer nothing in return.

```markdown
If <SDK name> saved you time, a ⭐ on GitHub helps it grow and reach more people: <repo URL>
```

## 6. Metrics

Report these weekly from the sheet:
- Unique visitors
- Top referrers
- Watchers
- Dependents
- Registry downloads
- Q&A answered share
- Median time to answer (GraphQL `answer.createdAt` minus `createdAt`)

Cloners are diagnostic only, because CI inflates them. **Stars are never a target.** Keep them as a trailing signal.

## 7. Open questions

These would sharpen the plan. In a live session I'd ask them one at a time.

1. Is this repo owned by a company, a community, or a solo maintainer? I assumed a company SDK.
2. Which number does leadership read today, and what decision hangs on it?
3. How many usage questions arrive each week, and where (issues or private channels)?
4. Is there a date the result must land by?
5. Do you want a one-off win or a compounding asset?
6. What is your effort ceiling in hours per week, and who answers publicly, with what backup?

Also send me the sidebar, the Releases page, the Discussions tab, the `.github/` folder, and a traffic export. Then I can fill in the diagnosis with real numbers.

## 8. Pass check

- **Ranking claims:** every one carries a label.
- **Effort:** no rung needs hours your ceiling rules out, once you confirm assumption 5.
- **Rewards:** no star ask offers a reward or a trade.
- **Pending:** the diagnosis row is waiting on your numbers.