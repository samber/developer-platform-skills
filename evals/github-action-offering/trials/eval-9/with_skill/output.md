# Sanity check: Oxleaf `oxleaf-action` node24 plan

Three of your five items need to change. Two are fine as they are.

| # | Your plan | Verdict | Fix |
|---|---|---|---|
| 1 | `node24` in v3.4.0, then move the v3 tag | ❌ Breaking change in a minor | Ship it as **v4.0.0** and leave `v3` where it is |
| 2 | Delete the v1 tags | ❌ Breaks every pinned workflow at once | Keep the tags and retire v1 by announcement |
| 3 | Keep the deprecated `token` input | ✅ Fine, with two additions | Add `deprecationMessage` and a removal major |
| 4 | Board numbers: installs, "Used by", code search | ⚠️ Two of the three are weak | Add server-side counts and label the public ones as lower bounds |
| 5 | Keep the README line on macOS and ARM self-hosted | ⚠️ Not true as written for node24 | Qualify the line and test those runners |

## 1. Ship node24 as v4.0.0

- A `runs.using` change is a major, because it raises the minimum runner.
- Node 24 doesn't run on macOS 13.4 and earlier or on ARM32 self-hosted runners.
- GHES instances without a node24-capable runner would fail too.
- If you move `v3` to node24, those v3 users go red with no edit on their side.
- Other vendors did the same: `actions/checkout` v5, `codecov-action` v6 and `docker/build-push-action` v7 all shipped node24 as a major.

What to do:

1. Release v4.0.0 with `node24` as a new immutable `v4.0.0` GitHub release. Move `v4` only to that released commit. Push just that tag (`refs/tags/v4`), never `--tags`.
2. Leave `v3` on node20. Keep patching v3 while GHES releases you support can't run node24.
3. Put the full commit SHA and a `uses: oxleaf/oxleaf-action@<sha> # v4.0.0` line in the release notes. SHA pinners and Dependabot only see new semver tags, never a moved major.
4. Make `/oxleaf-action@v3` and v4 changes pass these gates before release:
   - contract diff against 3.3.1 (only the intended breaks);
   - check-dist clean;
   - test matrix green on the OSes the README claims, plus one self-hosted runner at the oldest supported runner version;
   - zizmor and actionlint clean;
   - nested `uses:` SHA-pinned.

The v3 warning is real, but it comes from GitHub forcing node24 on your node20 action. Since 2026-09-23, v3 already runs on node24 with a warning, untested by you. v4 is the fix, so the "next week" date is fine for v4.0.0, not for v3.4.0.

## 2. Don't delete the v1 tags

- v1 still has users. Deleting the tags breaks every pinned workflow at once.
- Retire it instead:
  - announce the retirement in the README and the release notes;
  - ship a final v1 patch that prints a warning;
  - leave the tags in place;
  - write a short migration guide from v1 to v4.
- Apply the same retirement to v2 later, once v4 is out.

## 3. Keep `token`, but make the deprecation explicit

Keeping it in v3 is correct, because removing an input needs a major. Two additions:

- Set `deprecationMessage` on `token`, for example `"token is deprecated; use api-key. Removed in v4."`. Check whether v3.1 already did.
- Send a deprecated-input flag with your API calls, so you can count how many runs still set `token`.

v4.0.0 is already a breaking release, so it's the cheapest place to delete `token`. Decide from the flag count. If few runs still set it, remove it in v4. If many do, keep it and name a later major in the README.

## 4. Usage numbers for the board deck

- **Marketplace installs:** I'm not aware of an install count that Marketplace shows for actions. I haven't fetched your listing, so I can't give you a figure. Don't put an "installs" number on a slide unless you can point to where it comes from.
- **"Used by":** this counts public repositories that declare the dependency. It misses private repos, which is likely most of your paying users.
- **Code search `uses: oxleaf/oxleaf-action@`:** this also matches forks, docs, examples, archived repos and commented-out lines. It is a public signal, not usage.

Label all three as public lower bounds and never as "users". For real numbers, use server-side data:

- Send a versioned `User-Agent` from the action, for example `oxleaf-action/3.3.1 (github-actions; Linux-X64)`.
- Count weekly active repositories by version, deduplicated by `run_id`. Add the share of runs on supported majors and the count of runs still setting `token`.
- If OIDC exists, use the server-validated `repository_id` and `repository_owner_id` claims.

This also tells you how many v1 and v2 users remain, which is what you need to retire them. The numbers won't exist for past weeks. Say so on the slide, and start collecting with the next release.

## 5. The README support line

"macOS and ARM self-hosted runners supported" is no longer true unconditionally once you ship node24:

- macOS 13.4 and earlier can't run node24, so v4 isn't supported there.
- ARM32 self-hosted runners can't run it either. ARM64 is fine.
- Rewrite the line to state the floor, for example "macOS 13.5 or later, ARM64 self-hosted runners". Check the exact floor against GitHub's runner docs before you publish it.
- Add macOS and ARM jobs to the CI matrix so the claim is tested. Keep one self-hosted job at the oldest supported runner version.
- Point users on older macOS or ARM32 to `@v3`, which stays on node20.

## Open questions

- Does your backend accept OIDC yet? If it does, v4 is also the place to add an `auth` input. If it doesn't, ignore this.
- Which GHES releases do your customers run? That sets how long v3 must keep getting patches.