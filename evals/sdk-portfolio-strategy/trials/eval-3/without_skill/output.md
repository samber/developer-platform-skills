**Mostly yes, with three changes.** Keep 3.0.0 across all five SDKs and keep the Node 16 and Go 1.21 drops. Change the same-day timing, the "numbers always match" promise, and how you handle a late SDK.

## What holds up

- **3.0.0 everywhere.** The API break is real, so a major bump is correct, and one number per release is easy to explain.
- **Dropping Node 16 and Go 1.21.** Both are long out of upstream support. Bundling them into this major costs readers little, because they must change code anyway. A runtime floor can only rise in a major, so this is the cheapest moment.

## What breaks

1. **"Same day" is the wrong deadline.** Publish SDK 3.0.0 no later than the flip, ideally a few days before it. If the SDKs land at the same moment as the API, nobody can test against v3 first. Ship pre-releases (rc) against a v3 sandbox from about week 3.
2. **"Numbers line up" only holds on day one.** After that, a Ruby 3.0.1 or a Python 3.1 will exist alone, and the promise looks broken. Don't promise equal numbers. Promise a compatibility matrix instead.
3. **Version numbers are the weak way to prevent confusion.** The strong way is for SDK 3 to pin the API version explicitly. SDK 3 should fail with a clear error if it reaches a v2 endpoint, and SDK 2 should do the same for v3. No version-matching guesswork is then needed.
4. **Go needs a new import path.** `/v3` is mandatory for a Go major, so every Go user edits imports. Ship a one-line `sed` or codemod in the guide. The upside is that Go v2 and v3 can coexist in one binary, which helps incremental migration.
5. **"Five at once, all or nothing" is fragile.** Decide now what happens when one language is late. My rule is below.
6. **Stranded users.** Anyone on Node 16 or Go 1.21 cannot reach v3 at all, so they need a supported 2.x line. Check your user-agent telemetry for their share before you commit.
7. **Rollback.** You cannot unpublish from Maven. Know the yank mechanism for each registry before release day: PyPI yank, npm deprecate, RubyGems yank, Go `retract`, and Maven fix-forward only.

## Plan for the five weeks

Today is 2026-10-10, so the flip is about 2026-11-14. That is a Saturday, so confirm the real date.

1. **Week 1.** Freeze the list of breaking changes. Pull the runtime-version share from telemetry. Fix the 2.x support end date, which depends on your API v2 sunset date.
2. **Weeks 1–2.** Ship 2.5.0 in all five languages. It is the last 2.x feature release, adds deprecation warnings for everything 3.0 removes, and links to the migration guide.
3. **Weeks 3–4.** Publish 3.0.0 pre-releases against the v3 sandbox. Registry formats differ (`3.0.0rc1`, `3.0.0.rc1`, `3.0.0-RC1`, `v3.0.0-rc.1`, and the npm `next` tag), so keep a mapping table. Run a cold migration of one real project per language with someone who did not write the guide.
4. **Week 5.** Publish the SDKs first, then flip the API, then make the docs default to v3.

## The policy to write down

> **SDK versioning policy**
>
> 1. **Scheme.** All SDKs follow SemVer. Minor and patch releases are independent per language, so the numbers can differ between languages after a major.
> 2. **API targeting.** Each SDK major targets exactly one API version, shown in a published compatibility matrix. 3.x targets API v3 and 2.x targets API v2. An SDK never falls back to another API version. It fails with an error that says which version it needs.
> 3. **Major releases.** A major is released for any breaking change, including raising a runtime floor. We aim to align SDK and API majors, but an SDK-only breaking change may take its own major, and the matrix is the source of truth.
> 4. **Runtime support.** We support a language runtime while its upstream maintainers support it. We raise a floor only in a major, announced in the previous minor. Floors for 3.0: Node ≥ 18 (check whether you want 20), Go ≥ 1.22 (check whether you want a newer floor), and Python, Java and Ruby floors to be set before launch.
> 5. **Deprecation.** We deprecate in a minor with a runtime warning and a migration link. We remove no earlier than the next major, and at least three months after the warning first shipped.
> 6. **2.x support.** 2.x receives security and critical fixes until the API v2 sunset date, which is [DATE]. Treat the end date as a commitment: do not shorten it, only extend it.
> 7. **Pre-releases.** Pre-releases are published against the sandbox and carry no stability promise. The first stable major release ships no later than the API flip.
> 8. **Late SDKs.** If one language is not ready, the API flip does not wait. That SDK ships as 3.0.0 when ready, the matrix shows the gap, and the other SDKs keep their numbers.
> 9. **Migration guide.** Every major ships with a migration guide. Each breaking change gets an entry with the search pattern, the exact error text, before and after code, and the fix.

Items 4 and 6 are choices, not facts. I picked the floors and the "support until API v2 sunset" rule as defaults, so change them if your constraints differ.

## Questions only you can answer

- What is the API v2 sunset date? Does v2 stay up alongside v3, or does the flip turn it off? This changes the plan the most, because a hard cutover strands every 2.4.x user at once.
- What share of traffic is on Node 16 and Go 1.21?
- What are the current Python, Java and Ruby minimums, and are they near end of life?

**Next:** answer the v2 sunset question. The 2.5.0 deprecation release and the support line in item 6 both depend on it.