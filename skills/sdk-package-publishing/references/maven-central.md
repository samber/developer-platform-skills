# Maven Central (Java with Maven; shared JVM rules)

## Contents

- Library vs binary
- CI auto-publishing: Portal token, signing, release gate
- Public publishing: cost, namespace, artifact requirements, removal
- Private publishing
- Private consumption
- Dated changes

This file holds the Central Portal rules every JVM language shares, plus the Maven build. Gradle builds (Java or Kotlin) add kotlin-gradle.md; sbt builds add scala-sbt.md.

## Library vs binary

- **Library:** jar (or AAR) with `-sources.jar`, `-javadoc.jar`, POM and signatures on Central.
- **Application:** jlink runtime images, jpackage installers or GraalVM native images, built on a runner per OS (none cross-compiles), shipped as release assets or through JReleaser packagers (Homebrew, SDKMAN, Scoop, winget, JBang). Never deploy a fat application jar to Central as if it were a library.

## CI auto-publishing

- **Check cost first:** commercial-nature artifacts need Publisher Pro (Cost, below) before any pipeline work.
- **Old tokens:** a token issued for OSSRH before its 2025-06-30 shutdown does not authenticate a Portal upload; generate a Portal token.
- **Trigger:** a protected `v*` tag; the publish job runs behind the `release` environment. Pipeline shape: release-workflow.md.
- **Signing runs in-build:** `maven-gpg-plugin` signs while Maven assembles the bundle. Run tests in the unprivileged build job, then run `deploy` with the signing subkey (with an expiry) and the Portal token only in the publish job.
- **Credential:** no trusted publishing (OIDC). Authenticate with a Portal user token from the CI secret store (`${env.CENTRAL_TOKEN_USER}` / `${env.CENTRAL_TOKEN_PASS}`). A token cannot be viewed again after creation; set an expiry and calendar the rotation.
- **Signing:** `maven-gpg-plugin` reads the passphrase from `MAVEN_GPG_PASSPHRASE`; never pass `-Dgpg.passphrase` on the command line or store it in `settings.xml`.
- **Provenance:** PGP signatures are mandatory; Sigstore bundles uploaded next to them are optional extra evidence.
- Publishing goes through the Central Publisher Portal. OSSRH (`oss.sonatype.org`, `s01.oss.sonatype.org`) is shut down; old Nexus-staging configs work only through the Portal's OSSRH Staging API compatibility service with a new Portal token.

## Public publishing

**Cost**

- Commercial-nature artifacts need the paid Maven Central Publisher Pro tier at any volume. Sonatype's definition explicitly includes service-dependent SDKs, generated clients, drivers, agents and integrations, open source or not. It applies to every release from 2026-10-01, including the next version of an SDK already on Central; raise it with procurement now. Plain community open source stays free, and mixed organizations can ask Sonatype for per-namespace review.
- Free publishers have monthly per-organization volume thresholds (files, size, releases); exceeding them opens a grace period, then rate limits.

**Namespace**

- Domain namespace (`com.corp`): prove ownership with a DNS TXT record on the exact domain.
- Code-host namespace (`io.github.<user>`): create a temporary public repository named after the verification key.
- Prefer the domain namespace for a company SDK: it survives repository renames and signals the vendor.

**Artifact requirements**

- Every file signed with PGP (`.asc`); `.md5` and `.sha1` checksums mandatory.
- `-sources.jar` and `-javadoc.jar` for jar packaging.
- POM: `name`, `description`, `url`, `licenses`, `developers`, `scm`; version must not end in `-SNAPSHOT`.
- Keep the signing key as a dedicated subkey in the CI secret store, passphrase separate, and publish the public key to a keyserver.
- Maven: `central-publishing-maven-plugin` with `<extensions>true</extensions>`; it generates checksums but not signatures or javadoc. Gradle and sbt builds: kotlin-gradle.md and scala-sbt.md.

**Release gate**

- Deployments validate, then wait for a manual publish by default (`autoPublish=false`). Keep that default: inspect the validated deployment, then publish or drop it. Drop is allowed only while VALIDATED or FAILED.
- SNAPSHOTs work on the Portal only after enabling them per namespace; they expire after 90 days.

**Removal**

- Released components are immutable; only Sonatype support removes one, for malware or leaked secrets. Rollback means releasing a fixed version and announcing it in the changelog and release notes. Treat every publish click as permanent, and rehearse only the validate-then-drop path.
## Private publishing

- Feeds with Maven support: GitHub Packages (repository-scoped permissions only), GitLab Package Registry, AWS CodeArtifact, Azure Artifacts, Google Artifact Registry, Artifactory, Nexus.
- Deploy with `distributionManagement` pointing at the feed; credentials in `settings.xml` `<server>` entries whose `id` matches the repository `id`.

## Private consumption

```xml
<!-- settings.xml in CI - values come from environment variables -->
<servers>
  <server>
    <id>corp-mirror</id>
    <username>${env.REPO_USER}</username>
    <password>${env.REPO_TOKEN}</password>
  </server>
</servers>
<mirrors>
  <mirror>
    <id>corp-mirror</id>
    <mirrorOf>*</mirrorOf>
    <url>https://maven.internal.example.com/repository/all/</url>
  </mirror>
</mirrors>
```

- Route every request through one repository manager with `mirrorOf *`; the manager decides which upstream may serve which `groupId`. Never declare extra `<repositories>` in POMs.
- Block your internal `groupId` prefixes from public upstreams on the repository manager (exclude patterns or routing rules).
- Maven Resolver remote repository filtering speeds and privatizes resolution, but its own docs say it is not a security control; enforce with `maven-enforcer-plugin` rules.
- Never mirror all of Central with a scraper: Sonatype bans it. Proxy through a repository manager.

## Dated changes

- 2025-06-30: OSSRH shut down; all namespaces migrated to the Portal.
- 2026-10-01: Publisher Pro required for commercial-nature artifacts; rate limits enforced.
