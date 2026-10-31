# Hollowmere Python client: the Discussions plan

**Verdict: half of it works.** The diagnosis is right: usage questions are leaking into the tracker, and you have two named answerers. Three parts of the plan will hurt you: the one-shot bulk conversion, the email line, and the competitor-repo posts. Two others need changes: the seven categories and "close the rest".

I couldn't ask the interview questions, so I've marked what I assumed.

## 1. Diagnosis

| Pattern | Evidence | Reading | First action |
|---|---|---|---|
| Usage questions pile up in issues | 52 of 74 open issues (70%) are "how do I..." | Support leaks into the tracker | Name an answerer, then Discussions Q&A |

- **What I don't know:** weekly inflow of new questions, unique visitors, registry downloads, and what number leadership reads. 52 is a backlog, not a rate. Send me the rate and a traffic export and I'll confirm the row.
- **Do this today:** archive traffic. GitHub keeps only 14 days and nothing recovers older data `[documented]`. Use the bundled Apps Script (`references/tracking-tools.md`), which needs a token with push access.

## 2. Ranked surfaces and the re-rank

1. **Traffic archive and metric swap.** Near-zero effort.
2. **Discussions Q&A.** Promoted from rung 4 to rung 2, because question 3 found weekly usage questions and question 6 found Dana and Yusuf. This holds only if both confirm hours per week and cover for each other.
3. **Small, frequent releases as feed events.** Tick "Create a discussion for this release" in an Announcements category. This notifies release watchers and shows on stargazers' Feed `[documented]`.
4. **Topics.** 5-10 accurate ones, about an hour.

## 3. Your plan, item by item

| Your step | Verdict | Why | Do instead |
|---|---|---|---|
| Convert all 52 in one script on Friday | ❌ Change | See below | Answer first, convert in batches of about 10 |
| Close the rest (22) | ⚠️ Don't blanket-close | See below | Triage with labels; close only duplicates and invalid |
| Enable 7 categories | ⚠️ Start with 2 | See below | Add more later |
| "Email support@hollowmere.io" in the issue template | ❌ Replace | See below | Use a `contact_links` entry to Q&A |
| Post in competitor repos' issues | ❌ Don't | See below | Off-platform routes |

**Bulk conversion.**
- An unanswered Q&A tab reads as abandonment. You'd launch with 52 unanswered threads, and two people can't clear them at once.
- Platform limits are about 80 content-creating requests per minute and 500 per hour, web UI included `[documented]`. Converting plus a template 5 comment is about 104 writes. A naive script can trip the per-minute limit. Pace it with sleeps.
- I haven't verified that a supported API call exists for converting an issue to a discussion. Check before you build the script around it.
- A Friday afternoon launch means 52 notifications go out and nobody replies until Monday.
- The cadence in the skill converts 5-10 answered issues first, then pins a start-here post.

**"Close the rest."** I read the 22 as bugs, and you may have meant something else. Mass-closing real bugs loses reproductions and contradicts "Issues track confirmed bugs".
- Label them `needs-triage`, `needs-reproduction` or `confirmed` using `references/labels.md`.
- Close true duplicates with template 12 and "Close as duplicate".
- Close invalid ones with a one-line reason.

**Seven categories.** Two answerers can't keep Ideas, Show-and-tell, Polls, General and Random alive. Empty tabs read as abandonment too. The 25-category limit isn't the constraint. Open **Announcements and Q&A** now. Add Ideas or Show-and-tell when Q&A runs on its own. Announcements can only be opened by maintain or admin roles `[documented]`.

**Email line.**
- Email creates a private, unsearchable support channel on top of the one you're building. It also adds a third queue for the same two people.
- Replace it with a `contact_links` entry in `.github/ISSUE_TEMPLATE/config.yml` that points questions to Q&A.
- Keep email only for security reports, via `SECURITY.md`.

**Competitor-repo posts.** This is the only hard no.
- The Acceptable Use Policies ban bulk promotion, and maintainers hide promotion in other repositories' issues as spam. This is policed `[documented]`. Your company org's account is the one at risk.
- The one allowed form is a disclosed answer to that exact issue. It must solve the person's problem and state your affiliation. Do it one issue at a time, never as a campaign.
- Better routes, from `samber/developer-relations-skills@oss-distribution-strategy`:
  - A "Coming from <competitor>" docs page.
  - A blog post.
  - A PR to awesome lists that fits their criteria.
  - Template 14 at the end of off-GitHub content: one star ask, no reward.

## 4. Cadence

Dates are unknown, so I used week numbers. Dana and Yusuf cover each other. I assumed about 15 minutes per answer, so about 13 hours for the 52 across both of them. That is an estimate, not a measurement.

| When | Action | Owner |
|---|---|---|
| Today | Start the traffic archive; set topics | Maintainer with push access |
| Week 1 | Answer the 52 in the issues, oldest first, inside the agreed hours; triage the 22; back-fill bodies on the last three releases | Dana, Yusuf |
| Week 2 | Enable Discussions (Announcements, Q&A). Add the `contact_links` entry. Pin template 3. Convert answered issues in batches of about 10, mid-week, with a pause between writes. Enable Dependabot version updates | Yusuf (setup), Dana (conversion) |
| Every release | Release body, auto-created Announcement, off-platform post | Release owner |
| Weekly | Answer Q&A inside the target, mark answers, label new items, merge Dependabot PRs, export traffic | Dana, Yusuf |
| Quarterly | Read watchers, dependents, downloads and referrers against the baseline | Maintainer |

## 5. Templates

**Issue template `config.yml`:**
```yaml
blank_issues_enabled: false
contact_links:
  - name: Usage question
    url: <Q&A category URL>
    about: How-do-I questions get searchable answers in Discussions.
  - name: Security report
    url: <SECURITY.md URL>
    about: Never post security issues publicly.
```

**Template 5, issue-to-discussion comment, posted on each issue:**
> Thanks for the question. Converting this to a discussion in Q&A, where answers stay searchable and other users can help: `<discussion URL>`. Issues here track confirmed bugs. If this turns out to be one, we will reopen it with your reproduction.

**Template 3, pinned start-here post:**
> Welcome to Hollowmere Python Discussions.
> - **Q&A** - usage questions. Mark the reply that solved it as the answer so the next person finds it.
> - **Announcements** - releases and roadmap notes, posted by the team.
> - Bugs with a reproduction go to Issues: `<issue form URL>`.
> - Security reports never go here: `<SECURITY.md URL>`.
>
> The team answers Q&A within `<target, e.g. two business days>`.

**Template 1, release body:**
> ## `<one-line outcome a user gets, not the version number>`
>
> `<two sentences: who should upgrade, and what changes for them>`
>
> ### Breaking changes
> - `<change>` - migrate with `<link to migration guide>`
>
> ### New
> - `<capability>` (#`<PR>`) - thanks @`<external contributor>`
>
> ### Fixed
> - `<symptom the user saw>` (#`<issue>`)
>
> Install: `<package manager command pinned to this version>`
> Questions: `<link to the Q&A category>`

**Template 2, announcement discussion, pasted when you tick "Create a discussion for this release":**
> **Hollowmere Python `<version>`: `<the outcome from the release title>`**
>
> `<What changed, in three lines a non-user can follow.>`
> - Release notes: `<release URL>`
> - Upgrade guide: `<URL, or delete this line>`
>
> Tell us what breaks or what you build with it in Q&A: `<Q&A category URL>`.

**Template 8, leadership metric note:**
> GitHub stars measure appreciation and bookmarks (Borges and Valente, 2018), and correlate only moderately with use (He et al., 2026). From this quarter we report:
> - Unique visitors and top referrers (Traffic, archived weekly; GitHub keeps 14 days)
> - Watchers (who receive release news)
> - Dependents ("Used by") and `<registry>` downloads
> - Q&A answered share and median time to answer, once Discussions has a month of history
>
> Stars stay on the sheet as a trailing signal: `<current>` (`<change>` this quarter).

## 6. Metrics

- Unique visitors and top referrers
- Watchers
- Dependents ("Used by")
- Registry downloads
- Q&A answered share
- Median time to answer, from GraphQL `answer.createdAt` minus `createdAt`

Cloners are diagnostic only, because CI inflates them. Stars are never a target.

## 7. Questions I need answered

1. What is the weekly inflow of new usage questions?
2. How many hours per week can Dana and Yusuf each give?
3. What public response target will you commit to?
4. What number does leadership read today, and what decision hangs on it?
5. What is the deadline, and do you want a one-off win or a standing asset? A deadline inside two months would promote the traffic archive, topics and releases above Discussions.

The pass bar is met: every ranking claim carries a label, no rung needs hours I'm unsure you have, and no star ask offers a reward or trade. The hours check depends on your answer to question 2.