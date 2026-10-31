# Order for qmig engagement: fix inflow first, Sponsors last

Your plan is mostly the wrong order, and one piece doesn't fit GitHub's limits. I followed the `github-engagement-playbook` skill. You haven't answered its six interview questions, so I list the assumptions I made.

## 1. Diagnosis

**Row matched: "Unique visitors flat; registry page and docs missing from referrers."** The skill reads that as no inflow, so GitHub is not the bottleneck.

- **Numbers behind it:** about 90 unique visitors a week for four months, referrers are only Google and `github.com`, and neither pkg.go.dev nor your docs appears. 520 stars sit on that base.
- **First action:** make the registry and docs link to the repo. Then move off-platform using `samber/developer-relations-skills@oss-distribution-strategy`.
- **Traffic data:** GitHub keeps only 14 days of traffic, and only the top 10 referrers [documented]. So "four months flat" means you already have an archive. If you don't, start one now (§ 2, rung 1).
- **Second row to check:** if Homebrew installs or Go module imports are growing while stars are flat, run the metric swap (template 8) before anything else. I have no numbers for that, so check it.
- **Why your plan can't fix this:** a Sponsors button, an org pin and a Discussions tip only reach people who are already on the page or already follow the repo.
  - The feed reaches followers, stargazers and watchers, not strangers [documented].
  - So none of the four items in your plan fixes "no one arrives".

## 2. Ranked surfaces and re-rank

Your four items map onto the skill's ranking like this:

| Your item | Skill surface | Verdict |
|---|---|---|
| Fill About sidebar | Topics (rung 3) plus the website field | Do now, about 1 hour |
| Weekly Discussions tip | Discussions (rung 4) | Conditional, standing cost |
| Pin repo on org | Not ranked | 5 minutes, no reach claim, do any time |
| Sponsors button | Not an engagement surface | Last |
| *Missing from your plan* | Traffic archive, and small releases as feed events (rungs 1 and 2) | Add first |

**Default order is value per maintainer hour**, labelled as the skill labels it:

1. **Traffic archive and metric swap.** About 1 hour once, then nothing.
2. **Small, frequent releases with real bodies.**
   - Minutes to an hour per release.
   - Tick "Create a discussion for this release" on each.
   - This notifies release watchers and shows on stargazers' and watchers' Feed tab [documented].
3. **Topics and the About sidebar.**
   - Use 5-10 topics, lowercase letters, digits and hyphens, 50 characters each, 20 maximum [documented].
   - Topic search weight is unpublished.
4. **Discussions Q&A.** Highest value, standing cost of hours per week.

**Re-rank.** The skill's rule: Discussions moves to rung 2 only if you get weekly usage questions (Q3) and have a named answerer plus a backup (Q6). If nobody answers publicly, delete it, because an unanswered tab reads as abandonment. I don't have Q3 or Q6, so Discussions stays at rung 4.

- A deadline inside two months would promote rungs 1-3.
- A compounding mandate plus an answerer would promote Discussions.
- A one-off win would cut the list to rungs 1-2.

**Your weekly tip.**
- It is a maintainer-only post, so it belongs in an Announcements-style category (only maintain and admin roles can open it [documented]).
- It reaches existing followers, not new visitors.
- Start it only once Q&A has an answerer, and no faster than your effort ceiling allows.
- A tip tied to each release costs less than a fixed weekly one.

**Sponsors button.**
- **It does not fit.** `FUNDING.yml` allows 1 organization plus 4 developers on GitHub Sponsors, 4 custom URLs, and 1 account per other platform [documented, enforced]. Six contributors on GitHub Sponsors cannot all be listed.
- **The platforms fit.** Open Collective, Patreon, Ko-fi and Liberapay are one account each, but they do not need to all be there.
- **The button does not appear on its own.** It stays off until you enable it in settings.
- **It carries no engagement claim.** I found nothing in the skill that links funding to visitors, and I won't invent one.
- **Funding choices are out of scope here.** Take them to `samber/developer-relations-skills@oss-sponsors-fundraising`. Ask each contributor first before listing them.

## 3. Cadence

Owner roles: **Maintainer** (you), **Answerer** (named public responder), **Backup** (covers the Answerer). Landing date: `<date, unknown>`. Hours are my estimates, not your ceiling.

1. **Weeks 1-2, earn first (about 4 hours total)**
   - Maintainer: set up the KPI sheet (`references/tracking-tools.md`, about 1 hour). Also add Google Alerts for `"qmig"`, `"quartzline/qmig"` and the module path.
   - Maintainer: check that the pkg.go.dev page, the docs site and the Homebrew formula each link to the repo. Fix whichever doesn't.
   - Maintainer: fill the About sidebar. Put the docs URL in Website and add 5-10 accurate topics.
   - Maintainer: back-fill bodies on the last three releases using template 1.
   - Maintainer: answer open usage questions in issues, oldest first.
2. **Weeks 2-4, only if an Answerer and Backup exist**
   - Open Discussions with two categories, Announcements and Q&A.
   - Add a `contact_links` entry in `.github/ISSUE_TEMPLATE/config.yml` pointing questions to Q&A.
   - Convert 5-10 answered usage issues to discussions.
   - Pin the start-here post (template 3).
   - Set the label scheme from `references/labels.md`.
   - Turn on Dependabot version updates.
   - Pin the repo on the org (5 minutes).
3. **Every release (Maintainer)**
   - Publish the Release body (template 1) and let the Announcement post (template 2) be created.
   - Add one off-platform post, using `samber/developer-relations-skills@changelog-writing`.
   - Cut a release as soon as one user-visible change merges. Don't batch fixes.
4. **Weekly**
   - Answerer: answer Q&A inside the stated target and mark answers.
   - Maintainer: label new items, merge Dependabot PRs, export traffic.
   - Optional: one tip in Announcements, attached to a release.
5. **Quarterly**
   - Maintainer: read watchers, dependents, downloads and referrers against the baseline. Revise topics.
6. **Sponsors button**
   - After the above, once `oss-sponsors-fundraising` has picked the platforms and contributors have agreed.
   - Fit `FUNDING.yml` to the limits.

## 4. Filled templates

Facts I don't have stay as visible `<placeholders>`.

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

Install: `go install github.com/quartzline/qmig@<version>` or `brew upgrade qmig`
Questions: <link to the Q&A category>
```

Check the install commands and module path against the real ones before using this. Cut any section that is empty for this release.

### Template 2: announcement discussion

```markdown
**qmig <version>: <the outcome from the release title>**

<What changed, in three lines a non-user can follow.>

- Release notes: <release URL>
- Upgrade guide: <URL, or delete this line>

Tell us what breaks or what you build with it in Q&A: <Q&A category URL>.
```

Tick "Create a discussion for this release" on the release form and paste this as the discussion body.

### Template 3: start-here pinned post

```markdown
Welcome to qmig Discussions.

- **Q&A** - usage questions. Mark the reply that solved it as the answer so the next person finds it.
- **Announcements** - releases and roadmap notes, posted by the team.
- Bugs with a reproduction go to Issues: <issue form URL>.
- Security reports never go here: <SECURITY.md URL>.

The team answers Q&A within <target, e.g. two business days>.
```

### Template 8: leadership metric note

GitHub stars measure appreciation and bookmarks (Borges and Valente, 2018), and correlate only moderately with use (He et al., 2026). From this quarter we report:

- Unique visitors and top referrers (Traffic, archived weekly; GitHub keeps 14 days)
- Watchers (who receive release news)
- Dependents ("Used by") and `<Go module imports / Homebrew installs, whichever you can read>`
- Q&A answered share and median time to answer, once Discussions has a month of history

Stars stay on the sheet as a trailing signal: 520 (`<change>` this quarter).

I left the downloads source open on purpose. I can't confirm which counts you can read for a Go module or your Homebrew formula.

## 5. Metrics to track

- Unique visitors (target: movement off the ~90/week baseline, no absolute number)
- Top referrers, especially whether pkg.go.dev and the docs appear
- Watchers
- Dependents ("Used by")
- Downloads, from whichever source you can read
- Q&A answered share, and median time to answer (GraphQL `answer.createdAt` minus `createdAt`), once Discussions has a month of history

Cloners are diagnostic only, because CI inflates them. Stars are never a target.

## 6. Questions I still need answered

These would change the order above:

1. Is qmig a company project or a solo one, and who is the Answerer plus Backup?
2. Which number does leadership read today, and what decision hangs on it?
3. How many usage questions arrive per week, and where do they land (issues or private channels)?
4. What is the landing date?
5. Is this a one-off win or a compounding asset?
6. What is your effort ceiling in hours per week?

Two things I could not check from here: whether pkg.go.dev and Homebrew currently link to the repo, and your real traffic archive.