# GitHub engagement templates

Replace every `<placeholder>`. Cut any line that would be false for this release or repository.

## 1. Release body

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

## 2. Announcement discussion

```markdown
**<Project> <version>: <the outcome from the release title>**

<What changed, in three lines a non-user can follow.>

- Release notes: <release URL>
- Upgrade guide: <URL, or delete this line>

Tell us what breaks or what you build with it in Q&A: <Q&A category URL>.
```

Tick "Create a discussion for this release" on the release form and paste this as the discussion body.

## 3. Start-here pinned post

```markdown
Welcome to <project> Discussions.

- **Q&A** - usage questions. Mark the reply that solved it as the answer so the next person finds it.
- **Announcements** - releases and roadmap notes, posted by the team.
- Bugs with a reproduction go to Issues: <issue form URL>.
- Security reports never go here: <SECURITY.md URL>.

The team answers Q&A within <target, e.g. two business days>.
```

## 4. Q&A answer

```markdown
<Direct answer in the first line.>

<Code or config, minimal and runnable.>

Docs for this: <deep link>. If this solved it, please mark it as the answer so others searching for "<their error text>" land here.
```

## 5. Issue-to-discussion redirect

```markdown
Thanks for the question. Converting this to a discussion in Q&A, where answers stay searchable and other users can help: <discussion URL>. Issues here track confirmed bugs. If this turns out to be one, we will reopen it with your reproduction.
```

## 6. Watch ask

Place it only where the reader already wants release news: the start-here post, the docs changelog page, or a solved support thread. Never in cold outreach, never paired with a star request.

```markdown
Want release news without the issue noise? Click **Watch > Custom > Releases** on <repo URL>.
```

## 7. Star-for-star decline

```markdown
Thanks, but we don't trade stars: GitHub treats exchanged stars as rank abuse, and they would make our numbers meaningless to us too. If <project> solved something for you, a short note in Q&A on what you built helps more.
```

## 8. Leadership metric note

```markdown
GitHub stars measure appreciation and bookmarks (Borges and Valente, 2018), and correlate only moderately with use (He et al., 2026). From this quarter we report:
- Unique visitors and top referrers (Traffic, archived weekly; GitHub keeps 14 days)
- Watchers (who receive release news)
- Dependents ("Used by") and <registry> downloads
- Q&A answered share and median time to answer, once Discussions has a month of history
Stars stay on the sheet as a trailing signal: <current> (<change> this quarter).
```
