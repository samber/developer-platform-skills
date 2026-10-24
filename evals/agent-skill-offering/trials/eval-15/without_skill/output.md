# Inglewick skill: what to tell users and what to change

I haven't verified how Cursor and Codex resolve and cache plugins. Treat the diagnosis below as a hypothesis until you run the check in step 1.

## Diagnosis

The two symptoms have different causes.

- **Cursor users see unreleased commands.** They are getting `main`, not a release. Your dev branch is acting as a distribution channel.
- **Codex users are stuck on an old copy.** The community marketplace pins a sha from three months ago, so anyone installing through it gets that frozen snapshot. Your release script can't reach it, because the pin lives in their repo.

## Next actions

1. **Reproduce (about 30 minutes).** On a clean machine, install through each route in each client. Record which commit or version lands.
   - Routes: community marketplace, direct repo install, and your own marketplace file if you have one.
   - Clients: Cursor and Codex.
   - This tells you which route each user group is really on. Don't send the messages below until it's done.
2. **Ask the marketplace maintainers to bump the sha to the latest release tag now.** Open a PR if they take PRs. Ask them to track a tag or a `stable` branch instead of a raw sha.
3. **Ship the changes below.**

## What to tell each group

**Cursor users**
> The skill you installed tracks our development branch, so it can describe commands that haven't shipped. Those commands arrive in the next release (vX.Y, on DATE). Until then, run `ing --help` to see what your binary supports. To get only released content, install from tag `vX.Y.Z` [instructions]. We're changing how releases are published so a default install no longer follows `main`.

**Codex users**
> You're on an older copy because the community marketplace pins a snapshot from about three months ago. Remove and re-add the plugin from [our release tag or our own marketplace] to get the current version. We've asked the marketplace to update, and we're moving to a release-tracking setup so this stops depending on them.

**Community marketplace maintainers**
> Please bump to tag vX.Y.Z, or point the entry at our `stable` ref. We'll send a PR with every release if you prefer.

## What to change

1. **Make releases the default install target.**
   - Have the release script move a `stable` branch, or tag each release.
   - Document installs from that ref only. Nothing user-facing should point at `main`.
2. **Keep unreleased commands out of the shipped skill.**
   - Land skill text for a new command in the release PR, not alongside the feature.
   - If that's too rigid, mark each command with the CLI version that introduced it. Add a rule to the skill: "if `ing --version` is older, don't use it."
3. **Host your own marketplace entry in your repo, pinned to `stable`.**
   - Make it the primary install route.
   - Treat the community listing as a mirror you nudge on each release, not a dependency.
4. **Keep bumping all five manifests. Do not drop the Cursor one.**
   - Cursor ignoring versions today isn't a contract. If that changes, or another tool reads the field, an unbumped manifest becomes a silent bug.
   - The real Cursor problem is tracking `main`, which an unbumped manifest wouldn't fix anyway.
   - Add a CI check that all five manifests carry the same version as the tag. This makes drift fail loudly.
5. **Add a post-release canary.**
   - After each release, install via each route and assert that the installed skill matches the released version.
   - Include the community marketplace route. When it lags, you'll find out the same day rather than from a user report.
6. **Open a release-day checklist item: "ping the community marketplace."**
   - Automate it with a PR if they accept them.

## Why this order

Steps 1–2 fix users within days without any code. Changes 1–3 remove the root cause. Changes 4–6 stop it recurring unnoticed.