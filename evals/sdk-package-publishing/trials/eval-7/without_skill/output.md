# Resuming `com.tidewater:payments-sdk` releases from GitHub Actions

I couldn't check live docs: web search was denied, and I didn't read `skill-wip/`. This answer comes from my own knowledge, which runs to about June 2026. One claim below needs checking before next week: whether Maven Central now supports OIDC.

## Summary

- **The old publishing path no longer exists.** OSSRH (`oss.sonatype.org`) was shut down on 2025-06-30. Your mid-2025 release was probably one of the last that could use it. The old credentials, the staging URLs and `nexus-staging-maven-plugin` all stop working.
- **Publishing now goes through the Central Portal** (`central.sonatype.com`).
- **As far as I know, Maven Central has no OIDC trusted publishing.** npm added it in 2025, but the Central Portal only accepts a user token (username and password pair). You will still store a long-lived secret in GitHub, unlike the npm team. Please check the Central Portal docs for a trusted-publishing feature before you commit to a design.
- **GPG signing is still mandatory.** You also need a GPG key, and OIDC doesn't replace it.

## Changes, in order

### 1. Central Portal account and namespace (do first, needs a human)

1. Log in at `central.sonatype.com`. Check whether `com.tidewater` appears under Namespaces as verified.
   - Sonatype migrated existing OSSRH namespaces automatically, so it may already be there.
   - If it isn't, verify it with a DNS TXT record on `tidewater.com`. This needs whoever controls DNS.
2. Account menu → **Generate User Token**. This produces a username and password pair. The old OSSRH password does not work.
3. Store the token as GitHub secrets, ideally in a protected `release` environment.

### 2. `pom.xml`

- **Remove** `nexus-staging-maven-plugin`.
- **Remove** the `<distributionManagement>` entries that point to `oss.sonatype.org` or `s01.oss.sonatype.org`.
- **Remove** any `autoReleaseAfterClose` configuration.
- **Add** the Central publishing plugin:

```xml
<plugin>
  <groupId>org.sonatype.central</groupId>
  <artifactId>central-publishing-maven-plugin</artifactId>
  <version><!-- check latest --></version>
  <extensions>true</extensions>
  <configuration>
    <publishingServerId>central</publishingServerId>
    <autoPublish>false</autoPublish> <!-- true once you trust the pipeline -->
    <waitUntil>published</waitUntil>
  </configuration>
</plugin>
```

- **Keep or confirm** these plugins, which Central requires:
  - `maven-source-plugin`, for the sources jar.
  - `maven-javadoc-plugin`, for the javadoc jar.
  - `maven-gpg-plugin`, for signing. Use `--pinentry-mode loopback` in CI.
- **Check the required POM metadata:** name, description, url, licenses (Apache-2.0), developers and scm.
- Put the source, javadoc and signing plugins in a `release` profile. Then ordinary builds don't sign.

### 3. GPG key

- Confirm last year's key has **not expired**. Central rejects bad signatures and validates them against public keyservers.
- Make sure the public key is on `keys.openpgp.org` or `keyserver.ubuntu.com`.
- Export the private key and store it as secrets: `GPG_PRIVATE_KEY` and `GPG_PASSPHRASE`.
- A key without an expiry date, or a dedicated release subkey, is the least fragile option.

### 4. GitHub Actions workflow

Trigger on a tag, use a protected environment, and give it minimal permissions:

```yaml
name: release
on:
  push:
    tags: ['v*']
permissions:
  contents: read
jobs:
  publish:
    runs-on: ubuntu-latest
    environment: release   # required reviewers = human gate
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with:
          distribution: temurin
          java-version: '17'   # match your build baseline
          server-id: central
          server-username: CENTRAL_USERNAME
          server-password: CENTRAL_PASSWORD
          gpg-private-key: ${{ secrets.GPG_PRIVATE_KEY }}
          gpg-passphrase: GPG_PASSPHRASE
      - run: mvn -B -Prelease clean deploy
        env:
          CENTRAL_USERNAME: ${{ secrets.CENTRAL_USERNAME }}
          CENTRAL_PASSWORD: ${{ secrets.CENTRAL_PASSWORD }}
          GPG_PASSPHRASE: ${{ secrets.GPG_PASSPHRASE }}
```

Pin the actions to commit SHAs. Restrict the tag pattern with a tag ruleset, so only maintainers can push `v*` tags.

### 5. If you want to approximate OIDC

You can't remove the long-lived secret, but you can keep it out of GitHub:

- Store the Central token and GPG key in a cloud secret manager (AWS, GCP or Vault).
- Have the workflow fetch them using GitHub's OIDC identity (`id-token: write`).
- That adds moving parts. It makes sense only if your security policy bans stored secrets.

### 6. Release 2.0.0

- **Versions cannot be republished.** A version on Central is permanent. Dry-run first with `autoPublish=false`, which uploads and validates the bundle. Then inspect it and press **Publish** in the portal.
- Test the pipeline on a throwaway `2.0.0-rc1` first if you can. It costs one permanent version number.
- **Snapshots:** Central doesn't serve them unless you enable that per namespace. Don't rely on them.
- 2.0.0 is a major version, so:
  - Write a migration guide.
  - Tag it, and create the GitHub release with notes.
  - Keep the groupId and artifactId the same, unless the 2.0.0 break includes a rename.
- Propagation to `repo1.maven.org` takes minutes, but search indexing can take hours.

## Checklist for next week

1. ⏳ Verify the namespace and generate the token (needs DNS if unverified).
2. ⏳ Check the GPG key's expiry and publish it.
3. Edit the pom: remove the staging plugin, add the Central plugin, fix the metadata.
4. Add the workflow and secrets, with a protected environment.
5. Run a dry run with `autoPublish=false`, check the bundle, then publish 2.0.0.

I can draft the exact pom diff and workflow against your repo. Send me the repo path, since I haven't looked at it.