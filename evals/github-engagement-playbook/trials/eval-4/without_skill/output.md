# Getting the next Tallowick Ruby SDK release noticed

**Do first:** write real GitHub Release notes. The rest depends on that.

## Diagnosis

Your current process hides releases from the people you want to reach.

- **Empty release body.** Most existing users never see your tag. They see a Dependabot or Renovate PR in their own repo, and that PR shows the GitHub Release body. A bare "v4.2" gives them nothing to read, so they skim and merge, or ignore it.
- **The 140 watchers** only get a notification at release time. An empty notice teaches them to ignore you.
- **One release per quarter.** Users sit on known bugs for up to 3 months. A 31-PR upgrade is also scarier to adopt, which is bad for a payments SDK.
- **The squashed "bump deps" commit.** Security teams at your customers want to know which dependency CVEs you fixed. One squashed commit hides that.
- **Looking substantial.** For a payments SDK, users read a regular cadence as reliability. A big batch reads as "rarely maintained, then a dump".

## Plan for the next 7 weeks

**Week 1: fix the plumbing (about half a day)**
1. Add `.github/release.yml` with categories: Breaking, Features, Fixes, Security, Dependencies.
2. Write a release-notes template: a 3-line highlight, a breaking-changes list, an "upgrade in 1 minute" snippet, and a link to CHANGELOG.md.
3. Switch Dependabot to grouped updates (`groups:` in `dependabot.yml`) and stop squashing. List changed dependencies, and any CVEs they fix, in the notes.
4. Add an SDK-version field to the API `User-Agent` if it isn't there already. Check whether you can already segment customers by SDK version. Everything below relies on it.

**Weeks 2–3: ship early, don't wait for week 7**
1. Cut a patch or minor release now with the fixes already merged. Security fixes should never wait for a batch.
2. Move to a monthly or per-fix cadence. If you still want a "big moment", keep a quarterly themed announcement (blog post, docs page) that rolls up the small releases.

**Week 4: preview**
1. Publish `4.3.0.rc1` (`gem install tallowick --pre`).
2. Open a pinned GitHub Discussion titled "4.3 preview: what's changing, please test".
3. Email 20–50 of your heaviest API users directly and ask them to try it. They become your early adopters and your quotes.

**Week 6: pre-announce**
1. Email customers on SDK versions older than the current one: "4.3 lands on <date>. Here's what you get, and here's what breaks."
2. Add deprecation warnings to the current version for anything that changes, linking to a migration guide.
3. Put a dashboard banner on any account that sees traffic from old SDK versions.

**Week 7: release day**
1. **GitHub Release** with full notes, plus a pinned Discussion linking to it.
2. **RubyGems** changelog and homepage links set in the gemspec (`changelog_uri` metadata).
3. **Email** to API customers, segmented by SDK version. Subject line: what changes for them, not "v4.3 released".
4. **Docs and dashboard.** Put a "latest SDK version" note in your docs and developer dashboard, and add a changelog entry to your API changelog page.
5. **Community.** Post to your developer Slack/Discord. Submit to Ruby Weekly and r/ruby only if there is something real to say.

**Weeks 8–10: follow-up**
1. Re-email accounts still on old versions.
2. Chart API traffic by SDK version. Your target is the weeks to reach 50% adoption.

## Release-notes skeleton

```
## Highlights
- <one user-visible benefit per line, not PR titles>

## Breaking changes
- <what breaks, who is affected, how to fix it in one line>

## Security
- <CVE or dependency bump, and what it fixes>

## Upgrade
gem "tallowick", "~> 4.3"
Migration guide: <link>

Full changelog: CHANGELOG.md
```

## Assumptions to check

- **Telemetry.** I assumed you can read the SDK version from API traffic. If you can't, add it now. Without it, you can't target old-version users or measure adoption.
- **Customer email list.** I assumed API account emails are usable for product updates. Check your terms before sending marketing-style mail. A release or security notice is usually fine.
- **Cadence.** I'm recommending a change to your cadence, which is your call. If a quarterly cadence stays for other reasons, the notes, the preview and the segmented email still apply.

**Metric to watch:** the share of API traffic on the newest SDK version after 4 weeks, compared with v4.2.