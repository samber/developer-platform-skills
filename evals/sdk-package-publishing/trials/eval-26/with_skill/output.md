**Next action (10 min):** In Artifactory, find who sent `PUT` for `nimbuslane-core` 3.1.0 twice. Check the audit and access log. Then create a temporary non-admin deploy token and revoke the admin token. Steps are in section 6, Day 0.

The Artifactory host, repository names, `com.nimbuslane` and `@nimbuslane` below are my guesses. Fix them in section 1 before you apply anything. Pipeline files are drafts pending your approval. I ran nothing against Artifactory.

---

## 1. Assumptions and inventory

**Assumptions** (no one was available to confirm):
- GitHub-hosted runners.
- Maven build. For Gradle, add `kotlin-gradle.md` mechanics.
- Branch `dev` is the integration branch. Release tags are `vX.Y.Z`.
- Java groupId is `com.nimbuslane`. npm scope is `@nimbuslane`. Artifactory host is `nimbuslane.jfrog.io`.
- The local repository behind virtual `libs-release` is `libs-release-local`. I did not check this.
- Effort ceiling is about 3 engineer-days. Release latency from one approval gate is acceptable.
- Internal libraries only. Nothing goes to Maven Central or public npm.

| Item | Registry | Publish path today | Credential | Expiry | Owner | Target |
|---|---|---|---|---|---|---|
| Java libs (`nimbuslane-core`, ...) | Artifactory, via virtual `libs-release` | CI, rebuild from tag | Admin access token | none (2023) | unknown | OIDC, promote dev → release |
| npm libs | Artifactory, npm repo | CI | same admin token | none | unknown | same |

**Findings:**
- Treat the admin token as compromised. It is old, never expires and has no owner. Admin tokens ignore include/exclude patterns, so no dependency-confusion rule ever applied to CI.
- Admin rights include overwrite and delete. That is the likely cause of the 3.1.0 overwrite.
- Deploying to a virtual repository hides which local repository receives the bytes. Release repositories should accept deploys only from the release job.
- "Rebuild from the tag on release day" means the shipped bytes differ from the tested bytes.

## 2. Decisions

- **Credential rung.** Use Artifactory OIDC from GitHub Actions with scoped tokens that live under 24 hours.
  - Two identity mappings: dev deploy, and release promote (bound to the `release` environment).
  - Add an approval gate (reviewers on the `release` environment). This is justified by the incident.
  - Provenance and signing are deferred. Artifactory build info links each artifact to its CI run.
- **Immutability.** CI gets deploy rights on release repositories without Delete/Overwrite. Humans do not hold admin tokens. One break-glass admin is kept, outside CI.
- **No rebuild.** Build and test once per `dev` commit, then deploy to a dev local repository. The tag only promotes that exact build with `jf rt build-promote`. Release bytes are byte-identical to tested bytes.
- **Channels.** Use SemVer with one immutable version per release. A CI guard checks that the tag equals the pom or `package.json` version and rejects `-SNAPSHOT`. Pre-releases (`-rc.N`) are promoted like any release and pinned by exact version.
- **Namespace.** Claim the `@nimbuslane` npm scope on public npm now, even though every package is private. Maven Central needs no claim here.
- **Preflight.** Run `mvn verify` plus `maven-enforcer-plugin` with `bannedRepositories` before deploying. For npm, run `npm pack --dry-run`.

## 3. Files and Artifactory config

### 3a. Artifactory configuration (UI, Terraform or REST — you run it)

1. **Local repositories.**
   - Create `libs-dev-local`, `npm-dev-local` and `npm-release-local`.
   - `libs-release-local` already exists.
   - Dev locals allow overwrite. Release locals are immutable through permissions.
2. **Virtual repositories.**
   - `libs-release`: `libs-release-local` plus the Central remote only. No dev locals.
   - `npm`: `npm-release-local` plus the npm remote.
   - Create `libs-dev` and `npm-dev` for integration tests. They include the dev locals, the release locals and the remotes.
   - **Clear "Default Deployment Repository" on every virtual.** Nobody should deploy through a virtual.
3. **Remote repositories.** Add exclude patterns on every Maven remote and the npm remote: `com/nimbuslane/**` and `@nimbuslane/**`. Enable Priority Resolution on the release locals.
4. **Groups and permission targets.**
   - `ci-dev-deploy`:
     - Read on the virtuals and remotes.
     - Deploy, annotate and delete/overwrite on `*-dev-local`.
   - `ci-release-promote`:
     - Read on the dev locals.
     - Deploy, cache and annotate on the release locals. **No Delete/Overwrite.**
   - Humans:
     - Read only, through SSO personal tokens.
     - Give no one delete rights on release locals except the break-glass admin.
5. **OIDC.** Create one OpenID Connect integration, provider name `github-nimbuslane`, issuer `https://token.actions.githubusercontent.com`. Add two identity mappings:

| Mapping | Claims | Group | Token expiry |
|---|---|---|---|
| dev | `{"repository":"nimbuslane/nimbuslane-core","ref":"refs/heads/dev"}` | `ci-dev-deploy` | 1 h |
| release | `{"repository":"nimbuslane/nimbuslane-core","environment":"release"}` | `ci-release-promote` | 30 min |

   Confirm the claim syntax in Artifactory's mapping UI. Add one mapping pair per repository.

6. **GitHub repository settings.**
   - Tag ruleset on `v*`: only release managers create, move or delete tags.
   - Environment `release`:
     - Reviewers are a team, or at least two people besides whoever cuts releases.
     - Self-review is blocked.
     - Deployments are restricted to `v*` tags.
   - Protect branch `dev`.
   - Delete repository and organization secrets used for publishing after step 6 of the migration. Keep `JF_URL` as a variable.

### 3b. `.github/workflows/dev-build.yml` (Maven)

```yaml
name: dev-build
on:
  push:
    branches: [dev]
permissions: {}                       # nothing by default
concurrency: { group: dev-build, cancel-in-progress: false }

jobs:
  build:
    runs-on: ubuntu-latest
    permissions: { contents: read, id-token: write }   # id-token mints dev-local rights only, never release
    env:
      JFROG_CLI_BUILD_NAME: nimbuslane-core
      JFROG_CLI_BUILD_NUMBER: ${{ github.sha }}         # tag -> SHA -> build lookup at release
    steps:
      - uses: actions/checkout@<sha>  # v6
        with: { persist-credentials: false }
      - uses: actions/setup-java@<sha>  # v5
        with: { distribution: temurin, java-version: "21" }   # no cache input: no restored caches
      - uses: jfrog/setup-jfrog-cli@<sha>  # v4
        env: { JF_URL: "${{ vars.JF_URL }}" }
        with: { oidc-provider-name: github-nimbuslane }
      - name: Test, build and deploy once to dev local
        run: |
          jf mvn-config \
            --repo-resolve-releases=libs-dev --repo-resolve-snapshots=libs-dev \
            --repo-deploy-releases=libs-dev-local --repo-deploy-snapshots=libs-dev-local
          jf mvn deploy -B          # tests run in the lifecycle; deploy only if they pass
          jf rt build-collect-env
          jf rt build-publish
```

npm variant of the run step:

```yaml
        run: |
          jf npm-config --repo-resolve=npm-dev --repo-deploy=npm-dev-local
          jf npm ci && npm test
          jf npm publish            # add --tag next for pre-releases
          jf rt build-publish
```

### 3c. `.github/workflows/release.yml`

```yaml
name: release
on:
  push:
    tags: ["v*"]                       # same pattern as the tag ruleset and the environment rule
permissions: {}

jobs:
  guard:                               # unprivileged: no id-token, no secrets
    runs-on: ubuntu-latest
    permissions: { contents: read }
    steps:
      - uses: actions/checkout@<sha>  # v6
        with: { fetch-depth: 0, persist-credentials: false }
      - name: Tag commit is on dev, tag equals pom version, no SNAPSHOT
        run: |
          git merge-base --is-ancestor "$GITHUB_SHA" origin/dev || { echo "tag not on dev"; exit 1; }
          version="$(xmllint --xpath "/*[local-name()='project']/*[local-name()='version']/text()" pom.xml)"
          [ "${GITHUB_REF_NAME#v}" = "$version" ] || { echo "tag != pom version $version"; exit 1; }
          case "$version" in *-SNAPSHOT) echo "SNAPSHOT cannot be released"; exit 1 ;; esac

  promote:                             # runs no project code, no checkout
    needs: guard
    runs-on: ubuntu-latest
    environment: release               # reviewers approve here
    permissions: { id-token: write }
    env:
      BUILD_NAME: nimbuslane-core
      RELEASE_REPO: libs-release-local
    steps:
      - uses: jfrog/setup-jfrog-cli@<sha>  # v4
        env: { JF_URL: "${{ vars.JF_URL }}" }
        with: { oidc-provider-name: github-nimbuslane }
      - name: Promote the tested build, no rebuild
        run: |
          jf rt build-promote --dry-run "$BUILD_NAME" "$GITHUB_SHA" "$RELEASE_REPO" --status=Released --copy
          jf rt build-promote "$BUILD_NAME" "$GITHUB_SHA" "$RELEASE_REPO" --status=Released --copy
```

Behavior to confirm in rehearsal:
- Promoting a version that already exists in the release repository must fail. That failure is the intended overwrite block.
- A tag whose commit has no dev build must fail.
- Do not add `workflow_dispatch` or a branch trigger to `promote` without the same environment gate.

## 4. Rollback runbook

You run every command. I ran none.

**For the 3.1.0 incident:**
1. Find the good bytes. Compare the checksums of 3.1.0 now against the build info of the tag's original build (`jf rt build-info` or the UI). Your services' lockfiles or `~/.m2` caches hold the other copy.
2. Release the fix as a new version, 3.1.1, from the intended commit. Do this first, before any delete.
3. Mark 3.1.0 as bad and name the safe version in the property value:
   `jf rt set-props "libs-release-local/com/nimbuslane/nimbuslane-core/3.1.0/" "quarantine=overwritten-bytes;use=3.1.1"`
   Artifactory has no deprecate primitive for Maven. Do not delete 3.1.0 while services still pin it.
4. Notify the teams that own the two broken services. Tell them to bump to 3.1.1 and clear cached 3.1.0 (`~/.m2/repository/com/nimbuslane/...` and CI caches).
5. Delete the bad 3.1.0 only after every service moved. Use the break-glass admin, and only outside CI.

**Standing runbook:**
1. Release the fix as a new version.
2. Set the `quarantine` property on the bad version.
3. If compromise is suspected, isolate build hosts, then revoke every credential the job could reach.
4. Reserve deletion for leaked secrets or malware.
5. Record the incident in the changelog and the internal advisory channel.

**Rehearse** steps 1–2 on `libs-dev-local` with a scratch artifact. Never rehearse on `nimbuslane-core`.

## 5. Private consumption config

`settings.xml` (CI and developers; secrets come from environment variables):

```xml
<servers>
  <server>
    <id>nimbuslane-mirror</id>
    <username>${env.REPO_USER}</username>
    <password>${env.REPO_TOKEN}</password>
  </server>
</servers>
<mirrors>
  <mirror>
    <id>nimbuslane-mirror</id>
    <mirrorOf>*</mirrorOf>
    <url>https://nimbuslane.jfrog.io/artifactory/libs-release</url>
  </mirror>
</mirrors>
```

In the POM, add `maven-enforcer-plugin` with `bannedRepositories`. Never declare `<repositories>`. For integration tests, point the mirror URL at `libs-dev` through a CI profile.

`.npmrc` (committed; no secret in the file):

```
registry=https://nimbuslane.jfrog.io/artifactory/api/npm/npm/
@nimbuslane:registry=https://nimbuslane.jfrog.io/artifactory/api/npm/npm/
//nimbuslane.jfrog.io/artifactory/api/npm/npm/:_authToken=${NPM_READ_TOKEN}
```

- Set `publishConfig.registry` in every internal `package.json` to the `npm-dev-local` URL.
- Use `npm ci` against a committed lockfile.
- Inject `NPM_READ_TOKEN`, `REPO_USER` and `REPO_TOKEN` as read-only, non-admin tokens that CI gets from the secret store.

**Probe (npm).** Publish one harmless canary, `@nimbuslane/confusion-canary`, to public npm. Never publish it internally. Run this with the read-only CI credential. `$FEED_NETRC` is a netrc file:

```sh
code() { curl -s -o /dev/null -w '%{http_code}' --netrc-file "$FEED_NETRC" "$1"; }
[ "$(code "$INTERNAL_NPM/@nimbuslane%2fnimbuslane-ui")" = 200 ] || { echo "probe cannot see the feed"; exit 1; }
[ "$(code "$INTERNAL_NPM/@nimbuslane%2fconfusion-canary")" = 404 ] || { echo "probe FAILED or inconclusive"; exit 1; }
```

Replace `nimbuslane-ui` with a real internal package. Confirm the probe identity is not admin. Admin ignores exclude patterns, so an admin 404 would prove nothing.

**Probe (Maven).** No public canary applies. Never publish one to Central. Use the blocking-rule and lockfile checks as proof, and record that the canary step did not apply:
1. Assert each Maven remote's `excludesPattern` contains `com/nimbuslane/**`. Read it with an admin credential from a laptop, not CI:
   `curl -s -H "Authorization: Bearer ${ADMIN_TOKEN}" https://nimbuslane.jfrog.io/artifactory/api/repositories/<remote-key>`
2. Check that the dependency tree resolves every `com.nimbuslane` artifact from the internal host.

Repeat the probes after any cleanup or reconfiguration. Deleting an internal package while public forwarding is on reopens the hole.

## 6. Migration sequence

Today is Fri 2026-10-23.

| When | Step | Evidence |
|---|---|---|
| **Day 0, Fri 10-23** | Pull audit and access log entries for the 3.1.0 `PUT`s. Create a temporary token: non-admin, deploy to `libs-release-local` only, expiry 7 days. Put it in the old CI job. Revoke the admin token. Remove delete/overwrite from every non-break-glass permission target. | Log export. Token list showing the admin token gone. A test overwrite attempt returning 403. |
| Mon 10-26 | Release 3.1.1 through the old CI job with the temporary token. Set the `quarantine` property on 3.1.0. Notify the service owners. | 3.1.1 checksum. Property visible on 3.1.0. Both services green. |
| Mon–Tue 10-26/27 | Apply section 3a: repositories, virtuals, remote excludes, permissions, OIDC. Claim `@nimbuslane` on public npm. | Exported repository and permission config. |
| Tue–Wed 10-27/28 | Rehearse on `libs-dev-local` with a scratch artifact: dev build, promote, repeat promote (must fail), overwrite attempt (must fail), roll-forward drill. | Run logs with the expected failures. |
| Wed 10-28 | Merge both workflows. Cut the first real release `v3.1.2` through the gate. | Run URL. Build info. Dev vs release checksum match. |
| Fri 10-30 | Delete the temporary token and any publish secrets in GitHub. Run the probes. Clear the old virtual's deployment default if it is still set. | Empty secrets list. Probe output (npm 404 after the positive 200). Config export. |

**Gates to hold:**
- No admin or non-expiring token in CI.
- Every release is a promotion of a tested build, and its checksums match the dev build.
- Release locals reject overwrite.
- Internal names resolve only from the internal source.
- The rollback runbook is rehearsed.

**Open questions that change the files:** the real groupId and scope, Maven versus Gradle, any self-hosted runners, whether services outside Java and npm consume these libraries, and who owned the admin token.

**Next:** run the Day 0 audit-log search and tell me what you find. I'll adjust section 6 if the overwrite came from a person and not from CI.