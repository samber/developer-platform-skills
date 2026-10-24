Next action (5 min): check whether the publisher ID `tollbridge` is free at marketplace.visualstudio.com/manage. If it is, create it today.

**Verdict:** the plan has 4 blockers and 4 fixes. Do the blockers before launch.

## Blockers

1. **Publisher ID is permanent.**
   - Publisher ID plus extension name forms the extension ID, `tollbridge-dev.tollbridge`. You can't rename it.
   - A "rename" means a new extension: you lose installs, ratings, and recommendations, and 3,000 teams must reinstall.
   - Fix: create the final publisher now, and publish under it from day one. Don't launch under `tollbridge-dev`.
   - If marketing can't decide in time, delay launch. Don't ship under a throwaway ID.

2. **Verified badge can't come on launch day.**
   - Verification needs a verified domain, and the publisher must have existed for a while. Microsoft's docs state 6 months. Re-check the current rule.
   - Fix: register the final publisher now and start the domain verification (DNS TXT record). The clock then runs while you prepare.
   - The badge lands months after launch. Don't promise it in launch copy.

3. **`1.0.0-beta.1` is rejected.**
   - The Marketplace accepts only `major.minor.patch`. It has no semver prerelease tags.
   - Fix: use a plain version such as `0.1.0` and publish with `vsce publish --pre-release`. That puts it on the pre-release channel. Marketplace convention is that pre-releases use a different minor from stable.
   - Cut `1.0.0` stable at GA. Versions never go down, so pick the numbering once.

4. **`vsce publish minor` on every tag is wrong.**
   - It bumps `package.json`, then makes a commit and a tag.
   - So the version published differs from the version in the tag. Your CI can also re-trigger on the tag it just created.
   - It bumps on every tag, even a patch hotfix tag.
   - Fix: set the version in the tag and in `package.json` by PR. CI then does `vsce package` once and publishes that exact `.vsix`.
   - Publish the same `.vsix` everywhere with `vsce publish --packagePath tollbridge.vsix`.
   - Before packaging, run `npm ci`, the tests, and a bundle step (esbuild). Add a `.vscodeignore`. Don't publish "straight from source".

## Fixes

5. **Cursor and VSCodium users should not sideload.**
   - Both pull from **Open VSX**, not the Microsoft Marketplace. Microsoft's terms bar its Marketplace from non-Microsoft products.
   - A sideloaded `.vsix` has no auto-update. Your paying teams would run stale migration code.
   - Fix: also run `ovsx publish tollbridge.vsix`. Set up an Eclipse account, sign the publisher agreement, and claim the namespace. Allow about 1 to 3 days.
   - Keep the `.vsix` on the GitHub release as a fallback.
   - Cursor tracks older VS Code builds. Set `engines.vscode` to the lowest version you need, and test the build in Cursor and VSCodium.

6. **The PAT is a single point of failure.**
   - "All accessible organizations" is what `vsce` requires, so the scope is fine. But the token is tied to the CTO's personal account.
   - If the CTO leaves, loses access, or forgets the 90-day expiry, publishing breaks. A hotfix at that moment is the worst case.
   - Fix, in order of preference:
     - Use `vsce publish --azure-credential` with Entra ID workload identity from GitHub OIDC. There's no long-lived secret and nothing to renew.
     - If you keep the PAT, add a second publisher owner or member now. Put the renewal in a shared calendar with an alert 14 days ahead. Store the PAT in a protected GitHub environment that only tag builds can reach, and require approval.
   - The same applies to the Open VSX token.

7. **The icon can't be SVG.**
   - The Marketplace needs a PNG for `icon`, at least 128x128. Use 256x256.
   - SVG is also rejected in the README images, unless it comes from a trusted source.
   - Fix: export the PNG from the logo. Keep the SVG elsewhere in the repo.

8. **Dry-run before launch day.**
   - Publish the pre-release privately first. Use a test publisher, or ship to a small group on the pre-release channel.
   - Check four things: install on a clean machine, the upgrade path from `0.1.0` to the next version, Cursor install from Open VSX, and the Marketplace page render (icon, README, categories, license).

## Two-week order

1. Day 1: reserve the final publisher, start domain verification, switch to a plain version number. (~1 hour)
2. Days 1 to 3: Open VSX account and namespace, PNG icon. (~2 hours plus wait time)
3. Days 2 to 4: rewrite the CI job (package once, publish to both registries, attach to release). Move to OIDC, or set up the PAT secret with a second owner. (~half a day)
4. Days 5 to 8: private dry run, including Cursor and VSCodium. (~half a day)
5. Days 9 to 14: fix findings, then launch. Add the badge to your roadmap, not your launch copy.

**Next:** open the Marketplace publisher page and check if `tollbridge` is free. Paste the result here if you want help drafting the new CI workflow.