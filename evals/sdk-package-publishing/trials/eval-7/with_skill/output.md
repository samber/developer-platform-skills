# Tidewater Payments Java SDK: resuming releases for `com.tidewater:payments-sdk` 2.0.0

## What changes

The npm model does not carry over. Maven Central has no trusted publishing (OIDC), so the pipeline uses a Portal token and a signing key. You still get the same safety properties: a protected tag, a separate publish job, an approval gate, and no credential on laptops. Three other things change.

1. **OSSRH is gone.** `oss.sonatype.org` shut down on 2025-06-30. Your old OSSRH credentials can't authenticate an upload, so generate a new Portal token.
2. **The build config changes.** Replace `nexus-staging-maven-plugin` with `central-publishing-maven-plugin`.
3. **Publisher Pro is probably required.** An SDK for a paid API is a "commercial-nature artifact". Since 2026-10-01 that needs the paid Maven Central Publisher Pro tier for every release, including 2.0.0. This is the schedule risk for next week.

Do not try to avoid the fee by calling the SDK non-commercial. Sonatype's definition explicitly covers service-dependent SDKs, open source or not.

## Assumptions

I can't ask questions here, so I assumed the following. Correct me on any that are wrong.

- CI is GitHub Actions on hosted runners.
- The build is plain Maven with a single module.
- The last release was signed with a PGP key I haven't seen.
- `com.tidewater` was migrated to the Portal in the 2025 namespace migration.
- Two or more people besides the release cutter can approve releases.
- This is a standing process that will run for years.

## Inventory

| Item | Today | Target |
|---|---|---|
| `com.tidewater:payments-sdk` library | Last published mid-2025 via OSSRH | Portal, from CI on a protected `v*` tag |
| Publish credential | OSSRH token, now dead | Portal user token on a bot account, with an expiry, in the `release` environment |
| Signing key | Unknown, last used mid-2025 | Dedicated subkey with an expiry, public key on a keyserver |
| Namespace `com.tidewater` | Assumed migrated | Verified in the Portal, at least 2 owners |
| Publish path | Unknown, probably a laptop | CI only |

## Decisions

### Before any pipeline work

1. **Procurement.** Start the Publisher Pro purchase today, since 2.0.0 depends on it. Treat it as a blocker until Sonatype confirms the tier on your Portal account.
2. **Namespace.** Log in to the Portal and confirm `com.tidewater` shows as verified. If it doesn't, re-verify with a DNS TXT record on the exact domain.
3. **Accounts.** Create a bot Portal account, or use a shared role account. Keep at least two human owners with phishing-resistant 2FA on the namespace. Generate the user token there, with an expiry, and calendar the rotation. A token can't be viewed again after creation.
4. **Signing key.**
   - Check whether the mid-2025 key has expired or has no subkey: `gpg --list-keys --keyid-format long`.
   - If it is unusable, generate a signing subkey with an expiry and publish the public key to a keyserver.
   - Store the key and its passphrase as separate secrets in the `release` environment.

### Optional stopgap (not recommended)

You could keep `nexus-staging-maven-plugin` by pointing it at Sonatype's OSSRH Staging API compatibility service with a new Portal token. Take the exact URL from Sonatype's docs. This only delays the migration and keeps a deprecated plugin, so I'd skip it.

### Release gate

- Keep `autoPublish=false`, the default.
- The deployment validates, then waits for a maintainer to inspect it in the Portal and click publish or drop.
- This replaces the npm team's `npm stage approve`.
- Drop only works while the deployment is VALIDATED or FAILED. After you publish, the release is permanent.

### Version policy

- Tag `v2.0.0` must equal the pom `<version>`, and the version must not end in `-SNAPSHOT`. CI enforces both.
- Because 2.0.0 is a major bump, publish a migration guide with it (`samber/developer-relations-skills@version-migration-guide`).

## Files (drafts pending your approval)

Secrets are placeholders. SHAs are placeholders too: resolve each with `git ls-remote https://github.com/<owner>/<action> refs/tags/<version>`, or let Dependabot pin them.

### `pom.xml` changes

Remove these:
- `nexus-staging-maven-plugin`
- any OSSRH `distributionManagement`
- any OSSRH `<repository>` entries

Add these:

```xml
<build>
  <plugins>
    <plugin>
      <groupId>org.sonatype.central</groupId>
      <artifactId>central-publishing-maven-plugin</artifactId>
      <version><!-- pin latest from the plugin's docs --></version>
      <extensions>true</extensions>
      <configuration>
        <publishingServerId>central</publishingServerId>
        <autoPublish>false</autoPublish>
      </configuration>
    </plugin>
    <plugin>
      <groupId>org.apache.maven.plugins</groupId>
      <artifactId>maven-source-plugin</artifactId>
      <!-- attach sources.jar -->
    </plugin>
    <plugin>
      <groupId>org.apache.maven.plugins</groupId>
      <artifactId>maven-javadoc-plugin</artifactId>
      <!-- attach javadoc.jar -->
    </plugin>
    <plugin>
      <groupId>org.apache.maven.plugins</groupId>
      <artifactId>maven-gpg-plugin</artifactId>
      <configuration>
        <gpgArguments>
          <arg>--batch</arg>
          <arg>--pinentry-mode</arg>
          <arg>loopback</arg>
        </gpgArguments>
      </configuration>
      <!-- sign goal bound to verify, inside a release profile -->
    </plugin>
  </plugins>
</build>
```

- The publishing plugin generates checksums but not signatures or javadoc, so you need the source, javadoc and gpg plugins.
- Put the gpg plugin in a `release` profile so local builds don't need a key.
- Make sure the POM carries `name`, `description`, `url`, `licenses` (Apache-2.0), `developers` and `scm`.
- Add `maven-enforcer-plugin` with a no-SNAPSHOT rule.

### `settings.xml` (committed, holds no secret)

```xml
<settings>
  <servers>
    <server>
      <id>central</id>
      <username>${env.CENTRAL_TOKEN_USER}</username>
      <password>${env.CENTRAL_TOKEN_PASS}</password>
    </server>
  </servers>
</settings>
```

Never pass `-Dgpg.passphrase` on the command line. The plugin reads `MAVEN_GPG_PASSPHRASE`.

### `.github/workflows/release.yml`

```yaml
name: release
on:
  push:
    tags: ["v*"]
permissions: {}

jobs:
  build:                              # unprivileged: no secrets, no id-token
    runs-on: ubuntu-latest
    permissions: { contents: read }
    steps:
      - uses: actions/checkout@<sha>  # v6
        with: { persist-credentials: false }
      - uses: actions/setup-java@<sha>  # v5
        with: { distribution: temurin, java-version: "17", cache: "" }  # no restored caches
      - name: Tag must equal pom version, no SNAPSHOT
        run: |
          tag="${GITHUB_REF_NAME#v}"
          version="$(mvn -q -B -DforceStdout help:evaluate -Dexpression=project.version)"
          [ "$tag" = "$version" ] || { echo "tag $tag != version $version"; exit 1; }
          case "$version" in *-SNAPSHOT) echo "snapshot"; exit 1 ;; esac
      - run: mvn -B verify            # tests here, no key

  publish:
    needs: build
    runs-on: ubuntu-latest
    environment: release              # reviewers approve here
    permissions: { contents: read }   # no id-token: Central has no OIDC
    env:
      CENTRAL_TOKEN_USER: ${{ secrets.CENTRAL_TOKEN_USER }}
      CENTRAL_TOKEN_PASS: ${{ secrets.CENTRAL_TOKEN_PASS }}
      MAVEN_GPG_PASSPHRASE: ${{ secrets.GPG_PASSPHRASE }}
      GPG_PRIVATE_KEY: ${{ secrets.GPG_PRIVATE_KEY }}
    steps:
      - uses: actions/checkout@<sha>  # v6
        with: { persist-credentials: false }
      - uses: actions/setup-java@<sha>  # v5
        with: { distribution: temurin, java-version: "17", cache: "" }
      - name: Import signing subkey
        run: printf '%s' "$GPG_PRIVATE_KEY" | gpg --batch --import
      - name: Deploy (sign in-build, upload, wait for manual publish)
        run: mvn -B -s .mvn/settings.xml -Prelease -DskipTests deploy
```

Three things to know about this workflow:

- **Secrets live in the environment.** `secrets.*` come from the `release` environment, not from repository or org secrets.
- **The publish job rebuilds.** `mvn deploy` is privileged build code behind the gate, so it runs no tests. The signing subkey's expiry limits the damage if it leaks.
- **Don't add a trigger.** Never add `workflow_dispatch` or a branch trigger without the same environment gate.

### Repository protection

1. **Tag ruleset.** Only release managers may create, move or delete `v*` tags.
2. **`release` environment.**
   - Reviewers are a team, or two or more people besides whoever cuts releases.
   - Any one reviewer can approve.
   - Self-review is blocked.
   - Deployments are restricted to `v*` tags.
3. **Secrets.** Remove every old OSSRH secret from the repo and org.
4. **Plan check.** Confirm your GitHub plan supports environment protection on this repository.
5. **Actions hardening.**
   - SHA-pin every action.
   - Default permissions to none.
   - No `pull_request_target` or `workflow_run` triggers.

## Rollback

Maven Central has no rollback primitive. Released components are immutable. Treat every publish click as permanent.

1. **If 2.0.0 is bad:** release 2.0.1 immediately and announce it in the changelog and release notes. Do not wait on a delete.
2. **Malware or a leaked secret in a release:** contact Sonatype support. That is the only removal path.
3. **If compromise is suspected:** isolate the build hosts first. Then revoke and rotate the Portal token and the signing key.
4. **Rehearsal.** Run the validate-then-drop path only. Cut a test tag in the pipeline and drop the VALIDATED deployment in the Portal instead of publishing. Never rehearse on a real publish.

The commands, all left for you to run: `git tag v2.0.0` and the push of that tag, plus the Portal publish or drop click. I run none of them.

## Private consumption

Not applicable here. If you later add internal artifacts, follow the `mirrorOf *` plus blocking-rule pattern in `references/maven-central.md`.

## Migration sequence

| When | Step | Evidence it leaves |
|---|---|---|
| Today, 2026-10-23 | Start Publisher Pro procurement. Verify the Portal namespace. | Sonatype confirmation of the tier. |
| Mon 10-26 | Create the bot account and Portal token. Check or generate the signing subkey and publish it to a keyserver. | Token expiry date in a calendar; `gpg --list-keys` output. |
| Tue 10-27 | Update the pom. Add the settings and workflow files. Set up the tag ruleset and `release` environment. Delete the old OSSRH secrets. | PR with the pipeline files. |
| Wed 10-28 | Rehearse: push a test tag, let CI validate, then drop the deployment in the Portal. | Workflow run and a dropped deployment. |
| Thu 10-29 | Tag `v2.0.0`. A reviewer approves the environment. A maintainer inspects the validated deployment and publishes it. | Signed artifacts on Central; release notes and migration guide. |
| After release | Confirm resolution: `mvn dependency:get -Dartifact=com.tidewater:payments-sdk:2.0.0`. | Successful fetch from Central. |

If Publisher Pro isn't active by Thursday, the release slips. Don't work around it.

## Done when

- No OSSRH token exists anywhere.
- The Portal token is scoped, has an expiry and is on a rotation schedule.
- Every publish runs from CI on a protected tag.
- The validate-then-drop rehearsal has been done.
- A written rollback plan exists: release a fix and announce it.