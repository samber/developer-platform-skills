# Scala (sbt) to Maven Central

## Contents

- Library vs binary
- CI auto-publishing
- Cross-building Scala versions
- Removal

Scala libraries publish to Maven Central. Namespace proof, signing, POM rules, cost tiers and immutability come from maven-central.md; load both files.

## Library vs binary

- **Library:** jars per Scala binary version (`corp-sdk_2.13`, `corp-sdk_3`), plus Scala.js (`_sjs1_`) and Scala Native variants when built.
- **Application:** sbt-native-packager builds zip, deb, rpm, Docker and GraalVM native images. Native images compile only for the host OS, so build them on a runner per OS and ship them as release assets.
- **Developer tool:** publish the jar to Central and list it in a Coursier channel, so users run `cs install corp-cli`.

## CI auto-publishing

- **Trigger:** a protected `v*` tag. sbt-dynver derives the version from the tag, so the tag guard is built in. Pipeline shape: release-workflow.md.
- **No OIDC:** Maven Central has none. Store the Portal token pair as `SONATYPE_USERNAME` and `SONATYPE_PASSWORD`, and the signing key as `PGP_SECRET` with `PGP_PASSPHRASE`, in the protected `release` environment.
- **sbt 1.11+** publishes to the Central Portal natively:

```scala
ThisBuild / publishTo := {
  if (isSnapshot.value) Some("central-snapshots" at "https://central.sonatype.com/repository/maven-snapshots/")
  else localStaging.value
}
```

- `+publishSigned` stages every cross version locally. `sonaUpload` uploads one validated deployment for a maintainer to publish in the Portal; `sonaRelease` uploads and publishes. Use `sonaUpload` to keep the validate-then-publish gate.
- **sbt-ci-release** (1.11.0+) wraps this in one command on tag push, and by default publishes immediately. Set `CI_SONATYPE_RELEASE=sonaUpload` to keep the Portal gate. It runs build, signing and upload in one job holding every secret: keep that job behind the environment gate, with no restored caches.
- **Signing runs in-build:** sbt-pgp signs while sbt assembles the artifacts. Run tests in the unprivileged build job, then give only the publish job the signing subkey (with an expiry) and the Portal token.
- Guides that teach `sbt-sonatype` and `sonatypeRelease` target the shut-down OSSRH. Ignore them.
- Pin sbt 1.11.x for releases until every build plugin supports sbt 2.0.

## Cross-building Scala versions

- Set `crossScalaVersions := Seq("2.13.<x>", "3.3.<x>")` on each published module, and `crossScalaVersions := Nil` with `publish / skip := true` on the aggregating root, so nothing publishes twice.
- Set `crossPaths := false` on Java-only modules: they need no Scala suffix.
- Compile Scala 3 libraries against the Scala 3 LTS line. Code compiled with a newer minor cannot be read by consumers on an older one.
- Stage every Scala version before one upload. A deployment that holds all of them publishes together, so no release ships for `_2.13` but not `_3`.

## Removal

- Central is immutable, as maven-central.md describes. Rehearse with `sonaUpload`, then drop the validated deployment in the Portal.
