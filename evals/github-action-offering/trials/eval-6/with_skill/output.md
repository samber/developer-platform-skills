**No, you're not done. Don't turn immutable releases off, and the PAT incident isn't closed.**

## 1. The v1 push failure

Keep immutable releases on. They're your only protection for `vX.Y.Z` tags if a credential leaks again.

**Cause.** `v1` is a GitHub release and also a tag you move. Immutable releases lock a release's tag, so `git tag -f v1 <sha>` can't be pushed. Major tags must be plain Git tags with no GitHub release. The `vX.Y.Z` releases carry the immutability.

**Check first.** GitHub normally applies immutability only to releases published after you turned it on. Your 2024 release should predate that. Read the exact rejection message and confirm it names `refs/tags/v1`. The release may have been edited or republished since, or `--tags` may be tripping on a different tag.

**Fix, in order:**

1. Run `gh release view v1` on the repo and check whether it's flagged immutable.
2. If it is not immutable, delete the `v1` release and leave the tag. The Marketplace page shows your latest release, so cutting a `vX.Y.Z` release keeps that look.
3. If it is immutable, `v1` is frozen at its current commit and can't be moved or reused. Tell `v1` users to move to the next major. Publish fixes for them as `v1.x.y` releases and say so in the README. Don't weaken the setting.
4. Change the script so it pushes one tag at a time: `git tag -f v1 <sha> && git push -f origin refs/tags/v1`. `--tags` pushes every local tag, which is a bug even when it works.
5. Make every fix a new immutable `vX.Y.Z` release. Move `vX` only to a released commit. Put the SHA-pinned `uses: sorrelby/setup-sorrel@<sha> # vX.Y.Z` line in the release notes so Dependabot can follow it.

## 2. The leaked PAT

**Why you're not done.** Revoking the PAT and seeing `v1` and `v2` where you expect them proves little, for these reasons:

- **Tags can be moved back.** An attacker can repoint a tag, let it run, and restore it. The tj-actions and trivy-action incidents (2025-03 and 2026-03) both came from stolen tag-push credentials, and trivy came back after incomplete rotation.
- **Your check may not be independent.** "Where we expected" must mean compared against your release record and signed tags, not memory.
- **You looked at two tags.** There may be others.
- **The PAT could do more than move tags.** Anything it could push or change is in scope.

**Do now:**

1. **Fix the window.** Find when the PAT was created and when the Slack export was shared. Find who has the export. Treat everything between those dates as exposed.
2. **Pull the audit trail.** In the org audit log, filter for this token's actions, including `git.push`, ref and tag events, release events and workflow changes. Cover the whole exposure window.
3. **Check scope.** A classic PAT may reach every repo the bot can. Audit all of them, not just `setup-sorrel`.
4. **Verify tags properly.**
   - List every tag and compare each against the release record and signed tags.
   - Any `vX.Y.Z` created through immutable releases is trustworthy.
   - Treat pre-immutability tags, `v1`, `v2` and any `vX.Y` as unverified until proven. Check their commit dates and parents, since forged tags in past incidents had impossible parent dates.
5. **Check what else it could change:**
   - **Code:** commits on `main` and other branches, and any change to workflow files or the release script. The release script handles your new PAT, so a poisoned script would steal it.
   - **Release artifacts:** releases and their assets.
   - **Access and config:** collaborators, deploy keys, webhooks, Actions secrets and environments.
6. **Rotate everything with write access.** That means all PATs, App keys and deploy keys the repo has, not only this one. Incomplete rotation is how trivy was hit twice.
7. **Check the Slack export for other secrets.** If one leaked, others probably did.
8. **If any tag or release changed without you, run the compromised-tag runbook:**
   - Freeze releases.
   - Repoint tags to known-good commits.
   - Cut patch releases.
   - Publish a security advisory with the exposure window and known-good SHAs.
   - Tell customers to rotate any secret the action touched during the window.

   If the audit finds nothing, write that down with the evidence. Customers who pin by SHA are unaffected either way.

## Then remove the cause

- Replace the bot PAT with a short-lived GitHub App token.
- Add a `v*` tag ruleset that only the release App can bypass.
- Run releases from a protected environment with required reviewers.
- Sign release tags.

That ends the "PAT in a Slack export can retag `v2`" risk, and the immutable `vX.Y.Z` releases would stay safe even if it happened again.

**Next action:** open the audit log filtered to the revoked PAT's token, over the full exposure window.