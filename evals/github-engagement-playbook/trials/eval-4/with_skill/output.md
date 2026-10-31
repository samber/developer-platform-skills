**Next action:** list the PRs merged since v4.2 that are still unreleased. Cut the first one as its own GitHub Release this week, with a written body. About 30 minutes.

## 1. Diagnosis

Your process is the problem. GitHub is not the bottleneck yet. No traffic data exists yet, so I can't classify the curve in § 1 with real numbers. I'll fill that in after the first traffic export.

- **One release per quarter gives one feed event per quarter.** Each release is a feed event for stargazers and watchers [documented]. Ten small releases reach them ten times. v4.2 with 31 PRs reached them once.
- **A tag-only body wastes that event.** A release is only worth its slot when the body says what changed. Your watchers' notification currently reads like "v4.2".
- **Batching delays fixes.** In a payments SDK, users wait for fixes that are already merged.
- **Squashing Dependabot hides maintenance.** Weekly dependency merges keep the repo visibly active at near-zero effort [folklore]. Security patches have real value on their own. Squashing them into one commit removes the activity signal. It also delays dependency patches, which is a security cost for a payments SDK.
- **Watchers are about 6% of stars** (140 of 2,300, my calculation). The people who already use you but don't watch won't see a release notification.
  - Releases alone won't reach them.
  - Registry downloads and dependents show real usage better than stars.

First action: stop batching, stop squashing, and stop empty bodies.

## 2. Ranked surfaces (re-ranked)

Re-rank against the interview. I haven't asked the questions yet, so I assume the following:
- Your date is 7 weeks out, which is inside two months. That promotes rungs 1-3.
- Discussions opens but carries no deadline metric.
- Discussions stays at rung 4 until you name a public answerer and a backup.

1. **Traffic archive and metric swap.** One hour of setup, then nothing. Do it first, because GitHub deletes traffic after 14 days [documented].
2. **Small releases with written bodies, each with a Discussion in an Announcements category.** 15-30 minutes per release. This is the main fix.
3. **Topics.** One hour for 5-10 accurate topics [documented]; search weight is unpublished.
4. **Discussions Q&A.** A standing job of hours per week. Delete it if nobody answers publicly, because an unanswered tab reads as abandonment.

Stars are never a target. Don't buy, trade or reward them.

## 3. Cadence to the landing date (7 weeks)

**Weeks 1-2, earn first.** Owner: maintainer.
1. Archive traffic weekly with the `scripts/` Apps Script files (setup in `references/tracking-tools.md`). Add a Google Alert for `"tallowick-ruby"`.
2. Cut the first unreleased fixes now, one release per user-visible change. A fix that touches payment behavior ships first.
3. Back-fill bodies on the last three releases, v4.2 included. Group the 31 PRs by user outcome and use template 1.
4. Set 5-10 topics.
5. Turn on Dependabot version updates and merge its PRs weekly. Do not squash them.

**Weeks 2-4.** Owner: maintainer plus the named public answerer.
1. Open Discussions with two categories: Announcements and Q&A. Post template 3 and pin it.
2. Add a `contact_links` entry in `.github/ISSUE_TEMPLATE/config.yml` that points questions to Q&A.
3. Convert 5-10 answered usage issues to discussions.
4. Add the watch ask (template 6) in the start-here post and the docs changelog page.

**Every release.** Owner: whoever merges.
1. Write the body (see `changelog-writing`).
2. Tick "Create a discussion for this release" with an Announcements category, using template 2.
3. Post off-platform.
4. Cut a release as soon as one user-visible change is merged. Never batch fixes to make a release look bigger.

**Week 7, the roll-up.** Instead of a release that looks big, publish a quarter-summary Announcement that links every small release.
- It is a feed event in its own right.
- It carries the "look how much shipped" effect, and each linked change was already shipped and noticed.
- Use template 2.

**Weekly.** Owner: maintainer.
1. Answer Q&A and mark answers.
2. Label new issues and PRs.
3. Merge Dependabot PRs.
4. Export traffic.

## 4. Reaching existing users who don't watch GitHub

GitHub's feed reaches only followers, stargazers and watchers [documented]. Reach beyond them is earned off-platform. That work belongs to `samber/developer-relations-skills@oss-distribution-strategy`, not this playbook.

Worth considering for a payments API:
- A note in the API dashboard or developer email.
- A link from the docs changelog page.
- A one-line star ask (template 14) in blog or newsletter content, never with a reward.

Check that your RubyGems page links back to the repo. Fix that before anything else off-platform (`samber/developer-platform-skills@sdk-package-publishing`).

## 5. Filled templates

I left unknown facts as `<placeholders>`. These are not yet run through a humanizer pass.

### Template 1: release body

```markdown
## <One-line outcome a user gets, e.g. "Idempotency keys now retry safely on timeout">

<Two sentences: who should upgrade (e.g. "Anyone using `<method>` on a flaky network"), and what changes for them.>

### Breaking changes

- <change> - migrate with <link to migration guide>   <!-- delete this section if none -->

### New

- <capability> (#<PR>) - thanks @<external contributor>

### Fixed

- <symptom the user saw> (#<issue>)

Install: `gem install tallowick -v <version>`   <!-- or: bundle add tallowick --version "<version>" -->
Questions: <link to the Q&A category>
Full history: CHANGELOG.md
```

### Template 2: Announcement discussion

```markdown
**Tallowick Ruby SDK <version>: <the outcome from the release title>**

<What changed, in three lines a non-user can follow.>

- Release notes: <release URL>
- Upgrade guide: <URL, or delete this line>

Tell us what breaks or what you build with it in Q&A: <Q&A category URL>.
```

### Template 3: start-here pinned post

```markdown
Welcome to tallowick-ruby Discussions.

- **Q&A** - usage questions. Mark the reply that solved it as the answer so the next person finds it.
- **Announcements** - releases and roadmap notes, posted by the team.
- Bugs with a reproduction go to Issues: <issue form URL>.
- Security reports never go here: <SECURITY.md URL>.

The team answers Q&A within <target, e.g. two business days>.

Want release news without the issue noise? Click **Watch > Custom > Releases** on https://github.com/tallowick/tallowick-ruby.
```

### Template 8: leadership metric note

GitHub stars measure appreciation and bookmarks (Borges and Valente, 2018), and correlate only moderately with use (He et al., 2026). From this quarter we report:

- Unique visitors and top referrers (Traffic, archived weekly; GitHub keeps 14 days)
- Watchers (who receive release news): 140 today
- Dependents ("Used by") and RubyGems downloads
- Q&A answered share and median time to answer, once Discussions has a month of history

Stars stay on the sheet as a trailing signal: 2,300 (<change> this quarter).

## 6. Metrics

- Unique visitors and top referrers.
- Watchers: the 140 baseline, as a trend against the same window last quarter.
- Dependents and RubyGems downloads.
- Q&A answered share and median time to answer (GraphQL `answer.createdAt` minus `createdAt`).
- Cloners are diagnostic only, because CI inflates them.
- Stars are never a target.

## 7. Open questions

I skipped the playbook's interview. These answers could change the ranking:
1. Who answers Q&A publicly, with what backup, and how many hours per week can they spend?
2. Do usage questions already arrive as issues or in private channels?
3. Which number does leadership read today, and what decision hangs on it?

**Next:** answer question 1. If nobody can answer publicly, skip Discussions and keep rungs 1-3.