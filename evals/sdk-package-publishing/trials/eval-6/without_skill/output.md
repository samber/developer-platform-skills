**No, don't submit it.** A SOC 2 auditor will reject it, and it also doesn't show you're safe.

## Why the test fails

1. **It removed the control, then tested the gap.** Dependency confusion needs a public package with an internal name and a higher version, and the installer has to pick it. He removed the virtual repo, so npm fell back to npmjs.org. The install failed because nothing with that name is public right now. That tells you nothing about what happens when an attacker publishes one.
2. **No attack was simulated.** The test never published a higher-version package under an internal name. It never showed the virtual repo resolving to the internal copy anyway.
3. **No positive control.** The note doesn't say why the install failed. It could be a 404, a 401, or a network error. Without a known-good install through the virtual, "it failed" proves nothing.
4. **Admin token.** Admin rights bypass the permissions, include/exclude patterns, and curation that real developers and CI run under. The result doesn't represent the real attack path.
5. **No evidence.** A one-line "confirmed" has no commands, output, date, config snapshot, or independent reviewer. Auditors test operating effectiveness from artifacts.
6. **The admin token use is itself a finding.** Log it in a ticket, and rotate the token if it sat in shell history or a shared terminal.

## What to check

- **Virtual repo resolution.** The risk is in the virtual `npm`: it aggregates `npm-local` and `npm-remote`. If both hold the same name, check how it picks one. Look at the repository order and the "priority resolution" setting on `npm-local`.
- **Remote exclude patterns.** Set `npm-remote` to exclude your internal names, for example `@hollowpine/**` and any unscoped internal names. This is the standard fix, because the remote then never serves those names at all.
- **Scope ownership on npmjs.** Check whether anyone owns the `@hollowpine` scope on npmjs.org. If not, register it. A scope you don't own is a gap.
- **Unscoped internal package names.** These are the highest-risk case, since the scope mapping in `.npmrc` doesn't protect them.
- **Every consumer path.** Check CI runners, Dockerfiles, and new laptops, not only the one `.npmrc`. Check that lockfiles carry integrity hashes and resolved URLs that point at Artifactory.
- **Optional hardening.** Artifactory Curation or Xray policies can block newly published public packages that shadow internal names.

## Evidence package for the auditor

1. **Control statement.** One paragraph: internal names resolve only from `npm-local`, and `npm-remote` excludes them.
2. **Config snapshot.** Export the JSON for `npm`, `npm-local`, and `npm-remote` via the Artifactory REST API (`GET /api/repositories/<key>`), with the date and who ran it. The `excludesPattern`, the virtual's repo list, and the priority settings are the design evidence.
3. **Canary test with a non-admin account.**
   - Pick a throwaway unscoped name, such as `hollowpine-canary-<random>`.
   - Publish version `1.0.0` to `npm-local`.
   - Publish `99.0.0` of the same name to public npm from a controlled account.
   - Install through the virtual with a normal CI-role or developer token.
   - **Pass:** `1.0.0` installs. Also run the positive control (a real internal package installs fine) and the negative control (the same name with the exclude pattern disabled in a sandbox repo shows the test can fail).
   - Unpublish the canary afterward, which npm allows within its unpublish window.
4. **Captured output.** Save commands, full logs, timestamps, tester name, and reviewer sign-off. The reviewer should not be the tester.
5. **Ongoing control.** A scheduled CI job that reruns the canary and a ticket for any new internal package name added to the exclude list. SOC 2 Type II looks at operation over time.

## Timeline

Doing the canary test and pulling the config exports is roughly a day of work. That fits before next week's audit. If the test fails, you've found a real exposure, so fix the exclude patterns first and then rerun it.

I haven't seen your Artifactory configuration, so I can't say whether you're currently exposed. The steps above show how to find out.