# Quillbrook Scala SDK: why only `_3` reached Central, and the correct publish setup

## Assumptions

- **CI:** GitHub Actions on hosted runners. Tell me if it's GitLab or self-hosted, because the environment gate changes.
- **Namespace:** your Central namespace is already verified and you already hold a Portal token.
- **Build files:** I haven't seen your `build.sbt`. The cross-build cause below is the most likely one, not a confirmed one. Run the check in section 1 to confirm it.
- **Commercial status:** I'm assuming this SDK depends on a paid service. If so, Central's Publisher Pro tier applies (see section 5).

## 1. What's wrong

### Why `_2.13` is missing

`sbt-ci-release` publishes with `+publishSigned`, which loops over each project's `crossScalaVersions`. A modules-only-on-`3.5` build produces only `_3`. The usual causes:

- **Modules without `crossScalaVersions`:** `core` and `http` set `scalaVersion := "3.5.x"` and never declare `crossScalaVersions`. `+` then has one version to loop over, so only `_3` is staged.
- **Cross-versions set only on the root:** the root aggregates both modules, but a root that isn't set to `Nil` can publish its own jar or skew the loop.

To check, run this locally, with no upload:

```sh
sbt "show core/crossScalaVersions" "show http/crossScalaVersions" "show crossScalaVersions"
```

Expect both Scala versions on `core` and `http`, and `List()` on the root. Anything else confirms the cause.

### Other problems in your setup

- **The blog post is out of date.** `sbt-sonatype` and `sonatypeRelease` target OSSRH, which shut down on 2025-06-30. Don't call `sonatypeRelease` yourself, and remove `sbt-sonatype` from `plugins.sbt` if you added it separately. Remove any `sonatypeCredentialHost` and `sonatypeProfileName` settings too. sbt-ci-release 1.11 uses the Central Portal path and does everything in one command.
- **"Straight to Central" is the risky part.** sbt-ci-release publishes immediately by default. Central releases are permanent, and only Sonatype support can remove one. Your missing `_2.13` shows the risk: nobody got to inspect the deployment first.
- **Scala 3.5 is the wrong compile target.** Code compiled with a newer Scala 3 minor can't be read by consumers on an older one. Compile against the Scala 3 LTS line (3.3.x), not 3.5.

### Recommendation on "straight to Central"

You asked for tag push to go straight to Central. I recommend against it, so set `CI_SONATYPE_RELEASE=sonaUpload` instead:

- The tag uploads one validated deployment containing every cross version.
- A maintainer inspects it in the Portal, then clicks Publish or Drop.
- One click per release is the cost, and it is the only way to catch a `_2.13` gap before it ships.

If you still want fully automatic releases, use `CI_SONATYPE_RELEASE=sonaRelease`, which is the command that uploads and publishes. Accept that every mistake becomes permanent.

## 2. Fix the already-released version

Central can't replace or delete the version that shipped `_3` only. Don't try to unpublish it.

1. **Roll forward.** Fix the build, then tag the next patch (e.g. `v1.4.1`) so it publishes both `_2.13` and `_3` for `core` and `http`.
2. **Announce it.** In the changelog and release notes, name the previous version as incomplete and the new one as the replacement.
3. **Backfilling `_2.13` under the same version:** `_2.13` is a different artifact from `_3`, so uploading it alone may be accepted. The Quillbrook reference doesn't confirm this, so treat it as unverified and don't rely on it.

I haven't run, and won't run, any publish. The commands below are for you to run.

## 3. `build.sbt` (draft)

```scala
ThisBuild / organization := "com.quillbrook"            // your verified namespace
ThisBuild / scalaVersion := "3.3.<x>"                    // LTS; pin the exact patch
ThisBuild / versionScheme := Some("early-semver")
ThisBuild / publishTo := {
  if (isSnapshot.value)
    Some("central-snapshots" at "https://central.sonatype.com/repository/maven-snapshots/")
  else localStaging.value
}

val crossVersions = Seq("2.13.<x>", "3.3.<x>")           // fill in exact patches

lazy val core = project
  .settings(crossScalaVersions := crossVersions)

lazy val http = project
  .dependsOn(core)
  .settings(crossScalaVersions := crossVersions)

lazy val root = (project in file("."))
  .aggregate(core, http)
  .settings(
    crossScalaVersions := Nil,   // root never publishes its own jar
    publish / skip := true       // nothing is published twice
  )
```

Also check:

- The POM needs `name`, `description`, `url`, `licenses`, `developers` and `scm`.
- Sources and javadoc jars are generated for every module.
- sbt is pinned to 1.11.x (`project/build.properties`) until all your plugins support sbt 2.0.
- `plugins.sbt` holds `sbt-ci-release` 1.11.x and nothing from `sbt-sonatype`. sbt-dynver comes with it and derives the version from the tag.

## 4. Pipeline (draft, pending your approval)

Maven Central has no OIDC. Credentials are therefore a Portal token and a signing key in a protected `release` environment, behind approvers.

Before enabling it:

1. **Tag ruleset:** only release managers may create `v*` tags.
2. **`release` environment:** reviewers are a team, or two or more people besides whoever cuts releases. Self-review is blocked, and deployments are limited to release tags.
3. **Secrets:** in the `release` environment only, add `SONATYPE_USERNAME`, `SONATYPE_PASSWORD`, `PGP_SECRET` and `PGP_PASSPHRASE`.
4. **Token and key hygiene:** use a bot account's Portal token with an expiry and a rotation date. Use a dedicated signing subkey with an expiry, and publish its public key to a keyserver. Revoke any old OSSRH token, because it won't authenticate against the Portal anyway.

```yaml
name: release
on:
  push:
    tags: ["v*"]
permissions: {}

jobs:
  build:                              # unprivileged: no secrets
    runs-on: ubuntu-latest
    permissions: { contents: read }
    steps:
      - uses: actions/checkout@<sha>  # v6
        with: { fetch-depth: 0, persist-credentials: false }   # dynver needs tags
      - uses: actions/setup-java@<sha>
        with: { distribution: temurin, java-version: "21" }    # pin to your JDK
      - uses: sbt/setup-sbt@<sha>
      - run: sbt +test                # all cross versions, no key

  publish:
    needs: build
    runs-on: ubuntu-latest
    environment: release              # reviewers approve here
    permissions: { contents: read }
    env:
      PGP_SECRET: ${{ secrets.PGP_SECRET }}
      PGP_PASSPHRASE: ${{ secrets.PGP_PASSPHRASE }}
      SONATYPE_USERNAME: ${{ secrets.SONATYPE_USERNAME }}
      SONATYPE_PASSWORD: ${{ secrets.SONATYPE_PASSWORD }}
      CI_SONATYPE_RELEASE: sonaUpload  # upload one validated deployment, human publishes
    steps:
      - uses: actions/checkout@<sha>
        with: { fetch-depth: 0, persist-credentials: false }
      - uses: actions/setup-java@<sha>
        with: { distribution: temurin, java-version: "21" }
      - uses: sbt/setup-sbt@<sha>
      - run: sbt ci-release
```

Rules for this file:

- Resolve every `<sha>` with `git ls-remote https://github.com/<owner>/<action> refs/tags/<version>`, or let Dependabot or Renovate pin them. Never invent one.
- Don't add `workflow_dispatch`, `pull_request_target` or restored caches to either job.
- The publish job runs build, signing and upload while holding every secret. That's why the environment gate and the no-cache rule matter.
- sbt-dynver derives the version from the tag, so no tag-equals-version guard is needed.

## 5. Cost and Publisher Pro

If the SDK needs a Quillbrook service to function, Sonatype counts it as commercial-nature. That applies to every release from 2026-10-01, including the next version of an SDK already on Central. Raise it with procurement before you tag, or the upload will be refused. A plain community-only library stays free.

## 6. Rehearsal and rollback

1. **Rehearse without publishing:** push a throwaway tag in a scratch fork or set `CI_SONATYPE_RELEASE=sonaUpload`. In the Portal, check the validated deployment lists both `core_2.13`, `core_3`, `http_2.13` and `http_3`, then **drop** it. Dropping works only while the deployment is VALIDATED or FAILED.
2. **Go-live checklist:** no `_2.13` in the deployment means don't click Publish. Fix the build and re-tag.
3. **After any bad real release:** publish a fixed version straight away and announce it. Central has no soft-removal, so contact Sonatype support only for malware or a leaked secret. If a secret leaked, revoke and rotate the Portal token and the signing subkey first.

## 7. Migration order

1. Run the section 1 check and confirm the missing cross-versions.
2. Raise Publisher Pro with procurement.
3. Apply the `build.sbt` changes and drop `sbt-sonatype` and its settings.
4. Set up the protected tag ruleset, the `release` environment and the secrets.
5. Merge the workflow, push a pre-release tag with `sonaUpload`, check four artifacts in the deployment, then drop or publish.
6. Cut the real patch release, and a maintainer publishes it.
7. Revoke the old tokens.

Sending `sonaUpload` vs `sonaRelease` back to me is the one open decision.