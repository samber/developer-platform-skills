# Inglewick `ing` skill: what to tell users and what to change

I read `agent-skill-offering` and its channel and manifest references. I haven't inspected the Inglewick repo or tested a Cursor or Codex install. The diagnosis below comes from the skill's channel table, so confirm it with the checks in step 0.

## Diagnosis

The two reports have different causes.

| Group | Symptom | Likely cause |
| --- | --- | --- |
| Cursor | Skill documents unreleased commands | Cursor follows git commits, not the manifest `version`. Those users are on `main`, which you develop on. `main` documents features the last release doesn't have. |
| Codex | Stuck on an old copy | Codex keys on the ref (default `main`) and the manifest `version`, and re-installing at a new ref is manual. If they install via the community marketplace, they are frozen at a sha set three months ago, roughly six releases back. |

**The marketplace sha is the biggest problem.** Every user of that listing is frozen at one commit, whatever you bump.

The skill makes a related point: a curated marketplace pins exact commits, so make each tag's commit the one worth pinning.

### On the proposal to stop bumping the Cursor manifest

**Reject it.** It changes nothing for Cursor users, because their problem is the ref and not the version.

It would also break the lockstep rule. A manifest that skips a version fails the equality gate and reads as stale. Your release script already bumps all five manifests, so leaving one out only adds a special case.

The skill says to keep Cursor's `version` bumped anyway. Cursor ignoring it today is an undocumented behaviour that could change.

## What to do first

**0. Confirm the channels (10 minutes).**
- Ask each reporter how they installed the skill and what `ing --version` and the skill's version say.
- If Cursor users added the repo without a ref, that explains their symptom.
- If Codex users came through the community marketplace, that explains theirs.

## What to tell each group

**Cursor users**
> The extra commands come from our development branch. They aren't in your installed `ing` yet, and they ship in the next release. Until then, trust `ing --help` over the skill. To fix it, reinstall the skill from the tag matching `ing --version`. The release notes now print that exact command. We're also adding a `stable` branch that only moves at release, so a plain install stops showing unreleased features.

**Codex users**
> Your skill copy is frozen at an old commit and doesn't update itself. Reinstall at the current release tag. If you installed through the community marketplace, that listing points at a commit from about three months ago. We've asked the curators to update it. Until they do, install directly from our repo at the tag. The skill's version guard will tell you when its major.minor differs from your `ing`. In that case trust `ing --help`.

Test the exact install syntax for each client yourselves before you publish it. The reference says Codex pin support is "less documented" and installer flags change fast.

## What to change

1. **Fix the marketplace listing.**
   - Ask the curators to bump the `sha` to the latest release tag's commit, and to say how often they re-pin.
   - If they can't commit to a cadence, publish your own marketplace (`source: "./"`, no `version` in the entry) and recommend that one.
   - Don't tell users the curated listing is current until the sha moves.

2. **Add a `stable` branch, moved only by the release script.**
   - Do it after the tag, as a fast-forward to the tagged commit.
   - Point default installs and any directory submission at it. The Claude directory's "Branch or tag" field should be `stable`. Left empty, it follows the default branch, and every merge becomes a candidate version.
   - The alternative is a `dev` branch with `main` equal to the last release. `stable` is cheaper because you keep developing on `main`.

3. **Extend the release script.** Today it only bumps five manifests. In this order it should:
   - Bump all five manifests, each `SKILL.md` `metadata.version` and the `Skill version:` body line from one source of truth. Run `check-skill-version.py x.y.z --write --manifest ...`.
   - Run the gates, then commit and tag.
   - Move `stable`.
   - Generate the release-note install block with tag-pinned commands for each channel.

4. **Add a content gate before the tag.**
   - Every command and flag the skill names must exist in `ing help --json`, and every new public command must be mentioned or allowlisted.
   - Version equality alone can't catch this. Between releases, `main` carries the last released version with newer content, so the guard sees a match.
   - Also check that the packaged artifact contains `skills/`.

5. **Pin the README.** Show install commands with a `v<your-installed-version>` placeholder next to `ing --version`, so it never goes stale.

6. **Optional, if most users install via Homebrew or another package manager.**
   - Those users get the binary and no skill, so they hit exactly these install problems.
   - Add `ing skills install` and a one-line drift notice, for example `skill ing 1.3.0 differs from ing 1.4.0; run: ing skills update`. This gives a version match by construction. It costs more effort, so it depends on your effort ceiling.

Keep prereleases off every default install. Cut them from a `next` branch, mark them as GitHub prereleases, and move `stable` only on final releases.

## Verify the fix

- A release with a deliberately stale skill fails before its tag exists.
- All five manifests equal the tag on the next three releases.
- A fresh Cursor install and a fresh Codex install, each from the documented command, both report the skill version that matches `ing --version`.
- After the curator updates the listing, a fresh install from it lands on the current tag's commit.

Two questions would sharpen this. How do your users mainly install `ing` (Homebrew, release download or a language registry)? And what is the effort ceiling for step 6?