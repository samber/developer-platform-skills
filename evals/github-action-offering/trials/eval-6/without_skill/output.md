**No on both.** Keep immutable releases on. The PAT incident isn't closed.

## 1. v1 push failure

Don't turn immutable releases off. Security asked for that setting. It would also remove protection for your versioned tags, such as `v2.1.0`, which are the ones pinned consumers rely on. Turning it off doesn't unlock a release that is already immutable, because the setting only affects releases published after it's on.

The real problem is that `v1` is a moving tag and also a GitHub Release. Immutability locks a release's tag, so a force-move of `v1` is refused once that release is immutable. Immutability should only cover fully versioned releases, not floating major tags.

Fix:
1. Read the exact push error first. Look for "immutable" in it.
   - Immutability should only apply to releases published after the setting was enabled.
   - If your 2024 `v1` release is affected, something probably republished or recreated it.
   - If the error mentions a ruleset or tag protection instead, the cause is different and the fix below won't help.
2. If `v1` is still a mutable release, delete the **Release** object but keep the tag. Do this with `gh release delete v1` without `--cleanup-tag`. If the release is already immutable, it can't be re-pointed. In that case, ask GitHub Support, or use a new major-tag scheme.
3. Publish releases only for full versions (`v2.1.0`), and let those be immutable. Marketplace shows the latest published release, so your listing still looks good.
4. Change the script so it stops pushing every tag. `git push -f --tags` force-pushes all tags, including ones that must never move. Use:
   ```
   git tag -f v1 <sha>
   git push -f origin refs/tags/v1
   ```
   Do the same for `v2`.

## 2. PAT leak

Matching tag SHAs is a snapshot. It doesn't show what happened while the token was exposed. A tag can be moved and moved back. Note that the Slack export may have contained the PAT well before last Tuesday.

Do these now:
1. Pin down the exposure window.
   - Find the earliest Slack message containing the PAT.
   - Find the time you revoked it.
   - Treat that whole span as compromised.
2. Audit everything the bot could write to in that window. Use the org audit log, the repo's push and tag events, and the Actions run history.
   - Pushes, branch and tag creates, deletes and moves.
   - Releases and release assets.
   - Changes to workflow files, Actions secrets and variables, webhooks, deploy keys and collaborators.
3. Check the PAT's scope.
   - Was it classic, with access to all your repos? Or fine-grained and limited to `setup-sorrel`?
   - Audit every repo it could reach, not just this one.
4. Check whether `v1` or `v2` ever pointed at a different commit. Consumers using `@v1` would have run that code. If either tag moved, notify consumers.
5. Check for other secrets in the same Slack export, and rotate them. Ask the recipient to delete their copy. Assume it was already copied.

Then reduce the risk of a repeat:
- Replace the PAT with a GitHub App installation token or an OIDC-based flow. Give it only contents-write on this repo, with a short expiry if you must keep a PAT.
- Add a tag ruleset on `v*` that only the release bot can update, and that blocks deleting tags.
- Tell consumers to pin by SHA. Immutable `vX.Y.Z` releases protect them only if they pin to those or to a SHA.

Next: open the audit log, filter on the bot actor from the earliest Slack timestamp onward, and check for any tag event other than your own release pushes. That takes about 20 minutes.