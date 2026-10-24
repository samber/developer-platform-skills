# Nimbuslane artifact pipeline: make releases immutable

## Root cause

The overwrite is the symptom. Three design flaws allowed it:

1. **CI uses an admin token.** Admin bypasses every permission rule, so nothing can block an overwrite. The token never expires and dates from 2023, so you should assume it has leaked to laptops, old CI jobs, or former staff.
2. **CI publishes to the virtual repo `libs-release`.** Virtual repos mix write and read paths. Anyone who can deploy there can hit a mutable target.
3. **Releases are rebuilt from the tag, not promoted.** The bytes you tested on dev are not the bytes you ship. Rebuilds are rarely byte-identical, because timestamps, dependency drift, and JDK or Node patch versions all change the output. Tests prove nothing about the released artifact.

## Target design

```
PR / dev branch ──► libs-snapshot-local   (mutable, SNAPSHOT versions only)

tag vX.Y.Z ──► build once + test ──► libs-staging-local   (+ build-info, checksums)
                                              │
                    release day: manual approval (GitHub Environment "release")
                                              ▼
                              promote same bytes ──► libs-release-local   (immutable)
                                                              │
consumers resolve only from:  libs-release (virtual, read-only) = release-local + remotes
```

Rules:

- A release is built once, from a protected tag.
- Release day promotes the tested bytes and rebuilds nothing.
- `libs-release-local` rejects any overwrite or delete, for every identity except a human break-glass admin with SSO and MFA.
- CI never holds a long-lived credential. It uses OIDC and gets a token that lives minutes.

## Artifactory configuration

**Repositories**

| Repo | Type | Who writes | Overwrite |
|---|---|---|---|
| `libs-snapshot-local` | local (Maven + npm variants) | `ci-snapshot` group | allowed (snapshots are mutable by definition) |
| `libs-staging-local` | local | `ci-staging` group | allowed (never consumed by services, so a failed tag build can retry) |
| `libs-release-local` | local | `release-promoters` group only | **denied** |
| `libs-release` | virtual | nobody | n/a |

Do the same for npm: `npm-staging-local`, `npm-release-local`, and a virtual `npm-release`.

**Virtual repo**

- Clear the "Default Deployment Repository" on `libs-release`, and grant no deploy permission on it.
- Consumers keep the same resolve URL, so no service changes are needed.
- Put `libs-release-local` first in the resolution order.
- Add an exclude pattern for `com/nimbuslane/**` to every remote repo, and for the `@nimbuslane` scope on npm. This stops dependency confusion, where a public package with your name wins resolution.

**Permission targets**

Create one permission target per repo, bound to groups. For `libs-release-local`, grant only Read and Deploy/Cache to `release-promoters`. Leave Delete/Overwrite and Manage off for everyone.

Admins bypass permission targets, so no configuration makes admin immutable. The mitigation is to keep admin off CI entirely and limit it to a few SSO+MFA humans. Verify the block with a negative test in Phase 1: deploy a file, then deploy different bytes to the same path, and assert HTTP 403.

**OIDC integration (replaces the admin token)**

- Provider: GitHub, issuer `https://token.actions.githubusercontent.com`.
- Name it `nimbuslane-github` and set the audience to your Artifactory URL.
- Identity mappings, each producing a token that expires in 5 to 10 minutes:

| Mapping | Claims to match | Token scope |
|---|---|---|
| `snapshot` | `repository_owner=nimbuslane`, `ref=refs/heads/dev` | group `ci-snapshot` |
| `staging` | `repository_owner=nimbuslane`, `ref_type=tag` | group `ci-staging` |
| `promote` | `repository=nimbuslane/<release-repo>`, `environment=release` | group `release-promoters` |

Check the claim names against a real decoded token before relying on them. A mapping that silently matches nothing fails closed, which is the safe direction, but it will block your first run.

## GitHub configuration

- **Tag ruleset** on `v*`: restrict creation to release managers, and block updates and deletions. A moved tag silently changes what "vX.Y.Z" means.
- **Branch ruleset** on `dev` and `main`: require a PR, require status checks, and block force-push.
- **Environment `release`**: required reviewers (two people), restricted to tags matching `v*`, no admin bypass.
- **Actions policy**: pin third-party actions by commit SHA, and set the default `GITHUB_TOKEN` permission to read-only.

## Workflows

All workflows below use the JFrog CLI with OIDC. Maven is shown. For Gradle, swap in `jf gradle`. For npm, use `jf npm publish`.

**`.github/workflows/ci.yml` (dev branch and PRs)**

```yaml
name: ci
on:
  pull_request:
  push:
    branches: [dev]
permissions:
  contents: read
  id-token: write
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@<sha>
      - uses: actions/setup-java@<sha>
        with: { distribution: temurin, java-version: '21', cache: maven }
      - uses: jfrog/setup-jfrog-cli@<sha>
        env:
          JF_URL: ${{ vars.ARTIFACTORY_URL }}
        with:
          oidc-provider-name: nimbuslane-github
      - name: Build and test
        run: mvn -B verify
      - name: Publish snapshot
        if: github.ref == 'refs/heads/dev'
        run: |
          jf mvn-config --repo-resolve-releases=libs-release --repo-resolve-snapshots=libs-snapshot \
            --repo-deploy-releases=libs-snapshot-local --repo-deploy-snapshots=libs-snapshot-local
          jf mvn -B deploy -DskipTests --build-name="${{ github.repository }}" --build-number="${{ github.run_number }}"
          jf rt build-publish "${{ github.repository }}" "${{ github.run_number }}"
```

PR builds run without the publish step, so forks and PR authors never get a deploy token.

**`.github/workflows/release.yml` (tag: build once, test, stage)**

```yaml
name: release-build
on:
  push:
    tags: ['v[0-9]+.[0-9]+.[0-9]+']
permissions:
  contents: read
  id-token: write
  attestations: write
jobs:
  stage:
    runs-on: ubuntu-latest
    env:
      BUILD_NAME: ${{ github.repository }}
      BUILD_NUMBER: ${{ github.ref_name }}
    steps:
      - uses: actions/checkout@<sha>
      - name: Check the tag matches the POM version
        run: |
          v=$(mvn -q -DforceStdout help:evaluate -Dexpression=project.version)
          [ "v$v" = "$GITHUB_REF_NAME" ] || { echo "tag/pom mismatch: $GITHUB_REF_NAME vs $v"; exit 1; }
          case "$v" in *SNAPSHOT*) echo "snapshot on release tag"; exit 1;; esac
      - uses: actions/setup-java@<sha>
        with: { distribution: temurin, java-version: '21', cache: maven }
      - uses: jfrog/setup-jfrog-cli@<sha>
        env: { JF_URL: "${{ vars.ARTIFACTORY_URL }}" }
        with: { oidc-provider-name: nimbuslane-github }
      - name: Test
        run: mvn -B verify
      - name: Publish to staging with build-info
        run: |
          jf mvn-config --repo-resolve-releases=libs-release --repo-resolve-snapshots=libs-snapshot \
            --repo-deploy-releases=libs-staging-local --repo-deploy-snapshots=libs-staging-local
          jf mvn -B deploy -DskipTests --build-name="$BUILD_NAME" --build-number="$BUILD_NUMBER"
          jf rt build-collect-env "$BUILD_NAME" "$BUILD_NUMBER"
          jf rt build-add-git "$BUILD_NAME" "$BUILD_NUMBER"
          jf rt build-publish "$BUILD_NAME" "$BUILD_NUMBER"
      - uses: actions/attest-build-provenance@<sha>
        with: { subject-path: 'target/*.jar' }
```

Add an integration-test job here that resolves the staged artifact from `libs-staging-local`, if you have one. That tests the exact bytes you will promote.

**`.github/workflows/promote.yml` (release day)**

```yaml
name: release-promote
on:
  workflow_dispatch:
    inputs:
      version: { description: 'Tag to promote, e.g. v3.1.1', required: true }
permissions:
  contents: read
  id-token: write
jobs:
  promote:
    runs-on: ubuntu-latest
    environment: release            # two required reviewers gate this job
    if: startsWith(github.ref, 'refs/tags/v') || github.ref_type == 'tag'
    steps:
      - uses: jfrog/setup-jfrog-cli@<sha>
        env: { JF_URL: "${{ vars.ARTIFACTORY_URL }}" }
        with: { oidc-provider-name: nimbuslane-github }
      - name: Promote staged build to release-local
        run: |
          jf rt build-promote "${{ vars.BUILD_NAME }}" "${{ inputs.version }}" libs-release-local \
            --status=released --copy=true --props="released.by=${{ github.actor }}"
```

Dispatch it from the tag (`gh workflow run promote.yml --ref v3.1.1 -f version=v3.1.1`) so the `environment` branch and tag restriction applies. If `build-promote` hits a path that already exists, the block-overwrite setting rejects it and the job fails. That failure is the desired behavior. Never add `--overwrite` or delete-then-retry.

## Consumer-side protection

Server-side immutability protects future releases. These controls catch tampering and cache drift:

- **Gradle:** commit `gradle/verification-metadata.xml` with SHA-256 entries for internal artifacts, and run with `--dependency-verification=strict`.
- **Maven:** use `-C` (strict checksums) in CI. Use `maven-enforcer-plugin` to ban SNAPSHOT dependencies in release builds.
- **npm:** commit `package-lock.json`, and use `npm ci` in CI. It fails on an integrity mismatch.
- Run `jf rt curl`, or a scheduled job, that re-checks `libs-release-local` checksums against recorded build-info. It alerts on any difference, so tampering is detected rather than only prevented.

## Rollout

**Day 0: stop the bleeding (about 2 hours)**

1. Create a scoped token for the existing CI jobs: deploy-only, on `libs-staging-local`. Put it in GitHub secrets and revoke the admin token. Look for other consumers of that token first. Search CI configs, laptops (`~/.jfrog`, `~/.m2/settings.xml`, `.npmrc`), and other CI systems. List active tokens under Administration, Access Tokens.
2. Pull the Artifactory audit and request logs for `nimbuslane-core` 3.1.0. Find who or what wrote the second upload. Item properties show `lastModified` and `modifiedBy`, and the request log shows the client IP and token subject.
3. Treat the old admin token as compromised until the audit says otherwise.

**Fix 3.1.0**

1. Compare the SHA-256 of the current `nimbuslane-core-3.1.0.jar` with the first build's recorded checksum, if build-info or CI logs retain it.
2. If the original bytes are gone, an overwritten Artifactory file does not appear in the trash can, so you cannot restore it. Do not rebuild 3.1.0.
3. Cut **3.1.1** from the 3.1.0 tag commit through the new pipeline. Ask affected services to bump.
4. Quarantine 3.1.0: move it out of `libs-release-local` into a `quarantine-local` repo that the virtual does not include. Never reuse the version number.
5. Tell consumers to clear caches. Maven and Gradle keep a `3.1.0` copy locally, so CI runners with warm caches may still hold either variant.

**Phase 1: repos and permissions (day 1 to 2)**

1. Create the repos and groups, set the permission targets, and clear the virtual's deploy default.
2. Run the negative overwrite test against `libs-release-local`: expect 403. Run a positive control first (the first deploy returns 201), or the test proves nothing.
3. Add the remote-repo exclude patterns.

**Phase 2: OIDC and workflows (week 1)**

1. Set up the OIDC integration and mappings.
2. Land `ci.yml`, `release.yml`, and `promote.yml` on one pilot library, such as `nimbuslane-core`.
3. Cut `3.1.1` through them, end to end.
4. Add the GitHub rulesets and the `release` environment.

**Phase 3: roll out and clean up (weeks 2 to 3)**

1. Roll out to the remaining Java libraries, then the npm libraries.
2. Remove every remaining static token, and confirm in the token list that none is left.
3. Turn on the consumer-side checks per service.
4. Add the scheduled checksum audit.

**Phase 4 (optional)**

- Sign artifacts with Sigstore, using the provenance attestation already in `release.yml`, and verify it in consumers.
- Add Xray policies to block unsigned artifacts or known-vulnerable versions.

## Decisions for you

1. **Quarantine vs. delete 3.1.0.** I recommend quarantine plus 3.1.1 (above). Deleting is simpler, but you lose the evidence for the audit.
2. **Two reviewers on `release`.** Cheap with a small team, and it removes the single point of compromise. Say so if the team is too small for it.
3. **Gradle or Maven, and which npm tooling.** The YAML assumes Maven and `jf`. I can adapt it to your actual build files if you share one representative library repo.

## Residual risk

- A human with Artifactory admin can still overwrite releases. Reduce that group to two or three people, require SSO+MFA, and alert on any admin write to `libs-release-local`.
- Compromised workflow code on a tag can still publish bad bytes to staging. The tag ruleset, required-reviewer promotion, and build provenance are the controls against that.
- I haven't seen your Artifactory version or your repo layouts. The permission names, OIDC claim names, and `build-promote` flags above match current Artifactory 7.x and JFrog CLI 2.x docs as I know them. Confirm each against your instance in Phase 1 before relying on it.