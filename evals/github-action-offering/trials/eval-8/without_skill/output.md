# Marrowfield `mfd` CI integrations: priorities and corrections

## Decision

Ship **GitLab, then Azure DevOps, on one shared installer**. Cover CircleCI, Bitbucket and Jenkins with documented snippets. Build the CircleCI orb only if there is quarter left over and demand evidence. Don't build a Bitbucket pipe or a Jenkins plugin this quarter.

## Why not all six

- **Coverage:** GitHub, GitLab and Azure DevOps cover 94% of paying customers. Adding CircleCI makes 97%. Bitbucket and Jenkins add 3% together.
- **Market size is the wrong test.** "Huge in the market" doesn't tell you who pays us. The survey covers only current customers, so it can undercount segments we sell badly into.
- **Cheap check before the PM decides:** count CircleCI and Jenkins in lost deals and open pipeline. If they show up repeatedly, move the orb up. If not, the survey stands.
- **Capacity:** one engineer for one quarter can't own six separate integrations. Each one means its own publishing flow, review gates, docs, and support.

## Main architectural correction

"Each integration owns its own logic" would put six copies of the same logic in six places. That logic is download, checksum verification, version pinning, OS/arch/libc detection, and exit-code mapping. It would also let them drift apart. The teams you'd split it across don't exist; it's one engineer.

**Do this instead:**

1. Write one installer/runner script (`install-mfd.sh` plus a PowerShell twin for Windows). Publish it as a versioned, checksummed release artifact.
2. Make every integration a thin wrapper. Each wrapper maps its platform's inputs onto the same flags and calls the shared script.
3. Refactor the live GitHub Action onto the same script first. That proves the script before anything else depends on it.
4. Pin the `mfd` version explicitly everywhere, with a documented default.
5. Verify the checksum on every download and fail closed on mismatch.

## The glibc problem

The Linux binary is glibc-linked. That breaks silently on Alpine and other musl images, which CI images and Docker-based pipes commonly use.

- The installer must detect libc and fail with a clear message, not a "file not found" from the loader.
- All wrapper images and defaults must be Debian or Ubuntu based.
- The better fix is a static or musl build. That is an upstream build decision, so put it to whoever owns the `mfd` release pipeline.
- Also confirm which architectures ship. If there's no arm64 Linux build, say so in the docs. GitLab and CircleCI both offer Arm runners.

## Corrections to the four drafts

### GitLab component (build this)

- **Empty `spec: inputs: {}` is a real gap.** Inputs are the component's public interface, and adding them later changes what users depend on. Ship at least `version` (pinned default), `stage`, `args`, and `image` (a glibc image by default), each with a default.
- Use `$[[ inputs.name ]]` interpolation.
- Publish to the CI/CD Catalog from a tagged semver release. Consumers pin `@1.0.0` or a major.
- Add a README and a component description, because the catalog needs both.
- Verify the exact catalog-publishing requirements against current GitLab docs before release.

### CircleCI orb (second tier, conditional)

- **`mfd/mfd@dev:latest` doesn't work as a hotfix path.** Dev orbs are mutable and expire after 90 days, so customers would break silently. A dev label is also an arbitrary string, not a "latest" alias.
- Publish production semver orbs, which are immutable. A hotfix is a new patch version. Customers pin `mfd/mfd@1.2.3`.
- The `mfd` namespace has to be registered by an org owner first.
- Customers whose orgs block uncertified orbs must opt in, or use a certified listing. Check this early, since it can block adoption.

### Azure DevOps task (build this)

- **Check the handler key.** I believe the Node 20 key in `task.json` is `Node20_1`, not `Node20`. Confirm against current Microsoft docs before shipping.
- **Node 20 is past end of life as of April 2026.** Declare a Node 24 handler as primary, with `Node20_1` as fallback while agents still run it. Confirm the current key name against Microsoft's docs.
- The task shells out to the shared installer, so the Node layer should stay minimal.
- Agents run on Windows, macOS and Linux, so the Windows and macOS builds matter here. This is the one place they all get exercised.
- Set Major/Minor/Patch in `task.json`, and bump Major for breaking changes. Auto-updates apply within a major, which makes patch hotfixes safe.
- You need a Marketplace publisher account. Share the extension privately first.

### Bitbucket pipe (docs only this quarter)

- **Re-pushing the `1.0.0` tag is the worst of the four ideas.** A mutable tag makes builds non-reproducible, hides which fix a customer is running, and defeats image caching. It also removes the ability to roll back.
- Publish immutable tags (`1.0.1` for the fix). If you want a floating `1` tag, announce it as floating.
- Base the image on Debian or Ubuntu because of the glibc binary.
- Until then, a 5-line snippet that runs the shared installer covers the 2%.

### Jenkins (docs only, no plugin)

A Jenkins plugin is a Java project with its own hosting and release process, and it serves 1% of customers. Document a `sh` step against the shared installer and a Docker-agent example.

## Quarter plan (13 weeks)

| Weeks | Work | Done when |
|---|---|---|
| 1–2 | Shared installer (sh and PowerShell), checksums, libc detection, release artifacts. Refactor the GitHub Action onto it. | Action passes existing tests on the new script. |
| 3–5 | GitLab component: real inputs, semver release, Catalog listing, docs. | A test project consumes it by pinned tag. |
| 6–9 | Azure DevOps task: Node 24 handler with `Node20_1` fallback, versioning, private share, Marketplace listing. | Passes on Windows, macOS and Linux agents. |
| 10–11 | CircleCI orb, only if the deal-data check justifies it. Otherwise docs and spare time. | Production semver orb, namespace registered. |
| 12 | Doc snippets for CircleCI (if skipped), Bitbucket and Jenkins. | One page per platform, tested once. |
| 13 | Buffer, support, and hotfix drills. | Cut a patch release on each platform. |

## Rules for all integrations

- Immutable semver releases everywhere. Fixes ship as new patch versions.
- Floating major tags are fine only where the platform convention expects them. GitHub Actions is the main case, and it already does this.
- Every wrapper fails loudly with a clear message on unsupported OS, arch, or libc.
- Run a hotfix drill per platform: cut a patch, confirm pinned users are unaffected and floating users update.

## Open questions for the PM

1. Do we have lost-deal or pipeline evidence for CircleCI or Jenkins?
2. Who owns a static or musl `mfd` build?
3. Is arm64 Linux supported?