**Next action:** open repo Settings, About (gear icon), and set Website to your docs URL. Takes 2 minutes.

## Order

1. **About sidebar** (15 min). Do it first: it is the only step that puts docs in front of every visitor.
   - Website = docs URL. You get one link, so use docs. pkg.go.dev goes in the README.
   - Description = one line: what it does, and for which DBs.
   - Topics = `go`, `cli`, `database-migrations`, `schema-migrations`, plus each supported DB (`postgresql`, `mysql`, `sqlite`).
2. **README links** (30 min). You didn't list this, but it is the real fix for the missing referrers. Add badges for pkg.go.dev, docs, and Homebrew install. Put a "Docs" link above the fold. No link in the repo means no click from the repo to those sites, which matches what you see.
3. **Pin repo on org** (2 min). Cheap, do it now. It only helps people who already reach your org page, so expect little traffic from it.
4. **Discussions tips** (1 h to seed, 20 min/week after). Enable Discussions. Write 3 to 4 tips first, so the tab is not empty. Each tip links to a docs page, which creates docs referrers. Start once step 1 is done.
5. **Sponsors button** (last, trimmed). It does not drive visits. Skip it until steps 1 to 4 show movement.

## Fix the Sponsors plan before you do it

- ⚠️ `FUNDING.yml` accepts at most 4 GitHub Sponsors usernames. Verify in GitHub's docs. You have 6 contributors, so you cannot list all of them.
- Each listed contributor must enroll in GitHub Sponsors themselves.
- Four platforms (Open Collective, Patreon, Ko-fi, Liberapay) is a menu, not a call to action. Pick one. Open Collective fits a project with several contributors.
- With ~90 visitors a week, expect close to zero sponsor conversions. Revisit when traffic moves.

## Measure

- GitHub keeps only 14 days of traffic data. Open Insights, then Traffic, every Monday. Write down uniques and the referrer list.
- Baseline: ~90 uniques/week, referrers Google and github.com only.
- Check after steps 1 and 2 have been live 2 to 3 weeks. Success = pkg.go.dev or docs appear in referrers. Uniques should rise past 90.
- If referrers appear but uniques stay flat, the bottleneck is discovery (search, posts, awesome lists), not the repo page. Then the next lever is outside the repo.

**Next:** do step 1 now, then paste your docs URL here if you want a one-line description and topic list drafted.