**Do now (5 min):** open `brambleq` → Insights → Traffic. Copy the 14-day views, clones, referrers and popular paths into a note. GitHub deletes this data after 14 days `[documented]`, and you have no archive yet.

## Verdict on Discussions

Friend is wrong for your setup. Don't enable Discussions Q&A.

- Q&A is a standing job: hours per week, with a named answerer and a backup. You are the only answerer, you have no backup, and you check notifications every two weeks.
- An unanswered Q&A tab reads as abandonment. This is the opposite of "looks alive".
- The start-here post promises a reply time. You can't honestly promise "two business days".
- Instead: answer the 11 question-issues in place, close them, and say plainly how fast you reply.
- Optional, week 3: an Announcements-only Discussions tab, so each release gets an auto-posted announcement. Only maintainers can open posts there `[documented]`. Check the settings let you delete the other default categories. If they don't, skip Discussions.

## Assumptions

I haven't asked the interview questions, so I assumed these:

- You are a solo maintainer, and the conference date is the deadline.
- Nobody reads a leadership number, so the metric swap becomes your talk-slide numbers.
- Your weekly capacity is 2 h.
- Interview Q2 (which number matters) and Q5 (one-off or compounding) are still open. Stars are never a target.

## Diagnosis

Row used: **"Usage questions pile up in issues"**. Evidence: 11 open question-issues. First action in the playbook is "name an answerer, then Discussions Q&A". The answerer condition fails, so I swapped in "answer in issues".

I can't classify any other row yet. No traffic, referrer, dependents or download numbers exist. Week 1 creates the baseline.

## Ranked surfaces

1. **Traffic archive and metric swap** `[documented]`. About 1 h once. Compounding.
2. **Small releases with real bodies, as feed events.** Releases reach stargazers' and watchers' Feed `[documented]`. About 30 min each. Compounding.
3. **Topics.** 10 min once. Each topic feeds `github.com/topics/<name>` `[documented]`. Search weight is unpublished.
4. **Discussions Q&A.** Deferred. It was the highest value but has a standing cost you can't pay.

Re-rank reasons:
- Your date is inside two months, which promotes rungs 1-3.
- Interview Q6 gave no backup answerer, so rung 4 is cut.
- Not on the list, but in the plan: Dependabot and labels. They are near-zero effort and keep the repo active `[folklore]`.

## Five-week plan (2 h per week; week 1 starts the week of 2026-11-02)

**Week 1: measure and fix the visible gaps (about 115 min)**
1. Build the KPI sheet from `scripts/`, 60 min. Add the weekly triggers.
2. Back-fill the 3 empty release bodies with template 1, 30 min. Edit them in place.
3. Set 5-10 accurate topics, 10 min.
4. Add Google Alerts for `"brambleq"` and the crate name, plus an OSS Insight bookmark, 10 min.
5. Put a recurring weekly 30-min "GitHub pass" on your calendar. Treat it as fixed.

**Week 2: clear the backlog (about 120 min)**
1. Answer the 11 question-issues, oldest first, about 8 min each (90 min).
2. Close each with the answer and the `question` label.
3. Enable Dependabot version updates for `cargo`, 15 min.
4. Create the minimal label set from `references/labels.md`, 15 min. Skip `area/` and priority labels.

**Week 3: set expectations and ship (about 110 min)**
1. Weekly pass: label new issues, merge Dependabot PRs, 35 min.
2. Add a question issue form with the reply-time line below, 15 min.
3. Add `.github/release.yml` from `labels.md`, so release notes draft themselves, 10 min.
4. Cut a release if a user-visible change is merged. Edit the draft body, 30 min.
5. Optional: Announcements-only Discussions, 10 min.

**Week 4: the page conference attendees land on (about 120 min)**
1. Weekly pass, 30 min.
2. Ship a release only for a real change, 30 min.
3. Rework the README first screen with `samber/developer-relations-skills@readme-optimization`, 45 min.
4. Read the first four weeks of traffic data, 15 min.

**Week 5: talk week (about 120 min)**
1. Cut the last release at least 3 days before the talk, only if a real change is merged `[folklore]`.
2. Add template 14 as the last slide's one-liner. Offer nothing in return.
3. Weekly pass, 30 min.
4. Calendar a 30-min pass for the day after the talk and another 7 days later. A talk usually brings a burst of issues, and a two-week silence there undoes the work.

Skipped on purpose: Trending (launch-sized, see `oss-launch`), a tracking issue, buying or trading stars (a risk only; StarScout found fake stars decayed within two months and became a liability).

Release rule: one release per merged user-visible change. Never batch fixes to look bigger. Dependabot merges are not releases. If `main` already has unreleased user-visible commits, release them now.

Reply-time line for the question form (my adaptation, not a playbook template):

```markdown
Questions are answered in batches, usually within two weeks. Confirmed bugs with a reproduction are looked at first.
```

## Filled templates

**1. Release body** (use for the 3 back-fills and every new release)

```markdown
## <one-line outcome a user gets, not the version number>

<Two sentences: who should upgrade, and what changes for them.>

### Breaking changes

- <change> - migrate with <link to migration guide>

### New

- <capability> (#<PR>) - thanks @<external contributor>

### Fixed

- <symptom the user saw> (#<issue>)

Install: `cargo add brambleq@<version>`
Questions: <link to the question issue form>
```

Cut any section that is empty for that release.

**2. Announcement discussion** (only if you enable the Announcements-only tab)

```markdown
**brambleq <version>: <the outcome from the release title>**

<What changed, in three lines a non-user can follow.>

- Release notes: <release URL>
- Upgrade guide: <URL, or delete this line>

Found a bug? Open an issue with a reproduction: <issue form URL>.
```

I cut the Q&A line because there is no Q&A category.

**3. Start-here pinned post** (same condition as template 2)

```markdown
Welcome to brambleq Discussions.

- **Announcements** - releases and roadmap notes, posted by the maintainer.
- Usage questions go to Issues with the `question` label: <question form URL>. Replies come in batches, usually within two weeks.
- Bugs with a reproduction go to Issues: <issue form URL>.
- Security reports never go here: <SECURITY.md URL>.
```

If you skip Discussions, don't post this. Put the same question line in the README or `CONTRIBUTING.md`.

**8. Metric note** (for your talk slide or abstract; there is no leadership reader)

GitHub stars measure appreciation and bookmarks (Borges and Valente, 2018). They correlate only moderately with use (He et al., 2026). From this quarter I report:

- Unique visitors and top referrers (Traffic, archived weekly; GitHub keeps 14 days)
- Watchers (who receive release news)
- Dependents ("Used by") and crates.io downloads
- Share of question-issues answered and median time to first response (OSS Insight)

Stars stay on the sheet as a trailing signal: about 900 (<change> this quarter).

## Metrics to track

- Unique visitors and top referrers
- Watchers, dependents and crates.io downloads
- Share of question-issues answered, and median time to first response
- Cloners are diagnostic only, because CI inflates them. Stars are never a target.
- Week 1 sets the baseline. Re-read quarterly against the same window a quarter earlier.

Ranking and reach labels are `[documented]` or `[folklore]`. No rung exceeds 2 h per week, and no star ask offers a reward or a trade.

**Next:** do the 5-minute Traffic copy above. Then reply with one fact: does `main` hold unreleased user-visible commits? That decides whether week 1 includes a release.