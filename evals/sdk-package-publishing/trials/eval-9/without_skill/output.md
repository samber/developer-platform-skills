# Quillbrook: why only `_3` reached Central, and the correct setup

I haven't seen your `build.sbt` or workflow, so the cause below is inferred from the symptom. Section 3 has a check that confirms it in about 30 seconds.

## 1. What's wrong

**Most likely cause: nothing cross-builds, so only the default `scalaVersion` (3.x) gets published.**

- `sbt-ci-release` runs `+publishSigned`, and `+` loops over the **root project's** `crossScalaVersions`.
- If `crossScalaVersions` is set only on `core` and `http`, the aggregating root still has the default, which is just `scalaVersion`.
- `+` then runs once, for 3.x, and you get `_3` only.
- The same result happens if the blog's commands (`sbt publishSigned sonatypeRelease`) run in the workflow without the `+`.

**Second problem: you have two release flows.**

- `sbt-ci-release` already bundles `sbt-pgp`, `sbt-dynver` and `sbt-sonatype`. Its `ci-release` command runs `+publishSigned` and then the Sonatype bundle release.
- The blog's `sonatypeRelease` is the legacy staging-repo (OSSRH) flow. OSSRH was shut down in June 2025, so `sonatypeRelease` has no working target.
- Declaring `sbt-sonatype` yourself, or adding a `sonatypeRelease` step, either does nothing useful or fights with the plugin's own pinned version. Delete both.

**Smaller issue: don't compile the library on 3.5.**

- 3.5 is a "Next" release, not an LTS.
- TASTy from 3.5 can't be read by users on 3.3 LTS, so your `_3` artifact is unusable for them.
- Libraries should build `_3` on **3.3.x LTS**. Use a newer 3.x only if you accept that users must be on at least that version.

## 2. What the setup should be

**`project/plugins.sbt`**
```scala
addSbtPlugin("com.github.sbt" % "sbt-ci-release" % "1.11.0") // use the exact 1.11.x you installed
// No explicit sbt-sonatype, sbt-pgp or sbt-dynver.
```

**`build.sbt`**
```scala
val Scala213 = "2.13.16"
val Scala3   = "3.3.6" // LTS; pick the latest 3.3.x

ThisBuild / organization       := "dev.quillbrook" // must match your verified Central namespace
ThisBuild / scalaVersion       := Scala3
// Set on ThisBuild so the root sees it. `+` reads the root's value.
ThisBuild / crossScalaVersions := Seq(Scala213, Scala3)
ThisBuild / versionScheme      := Some("early-semver")

// Central rejects deployments without this metadata.
ThisBuild / homepage   := Some(url("https://github.com/<org>/quillbrook"))
ThisBuild / licenses   := List("Apache-2.0" -> url("https://www.apache.org/licenses/LICENSE-2.0"))
ThisBuild / developers := List(Developer("id", "Name", "email@example.com", url("https://github.com/<user>")))
ThisBuild / scmInfo    := Some(ScmInfo(
  url("https://github.com/<org>/quillbrook"),
  "scm:git@github.com:<org>/quillbrook.git"))

// Central Portal, not the retired OSSRH host.
ThisBuild / sonatypeCredentialHost := "central.sonatype.com"
// If your sbt-sonatype version has it, use sonatypeCentralHost instead of the string.

lazy val root = (project in file("."))
  .aggregate(core, http)
  .settings(publish / skip := true) // don't publish the empty aggregate; don't override crossScalaVersions here

lazy val core = (project in file("core")).settings(name := "quillbrook-core")
lazy val http = (project in file("http")).dependsOn(core).settings(name := "quillbrook-http")
```

**`.github/workflows/release.yml`**
```yaml
on:
  push:
    tags: ["v*"]          # tags only, so no snapshot publishing
jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with: { fetch-depth: 0 }   # dynver needs full history and tags
      - uses: actions/setup-java@v4
        with: { distribution: temurin, java-version: 17 }
      - uses: sbt/setup-sbt@v1
      - run: sbt ci-release
        env:
          PGP_PASSPHRASE: ${{ secrets.PGP_PASSPHRASE }}
          PGP_SECRET: ${{ secrets.PGP_SECRET }}                 # base64 of the exported secret key
          SONATYPE_USERNAME: ${{ secrets.SONATYPE_USERNAME }}   # Central Portal user-token name
          SONATYPE_PASSWORD: ${{ secrets.SONATYPE_PASSWORD }}   # Central Portal user-token password
```

Notes on the workflow:

- Use a **Central Portal user token** generated at central.sonatype.com. An old OSSRH login won't work.
- Don't add `sonatypeRelease`, `sonatypeBundleRelease` or `publishSigned` steps. `ci-release` does all of them.
- A tag push publishes straight to Central, as you wanted.

## 3. Verify before the next tag

1. Run `sbt "show crossScalaVersions"` at the root. You should see both versions. A single entry confirms the diagnosis above.
2. Run `sbt +publishLocal`. Check that `quillbrook-core_2.13`, `quillbrook-core_3`, `quillbrook-http_2.13` and `quillbrook-http_3` all appear under `~/.ivy2/local/`.
3. Check the secrets: `sbt ci-release` fails fast if `PGP_*` or `SONATYPE_*` are missing.

## 4. Fixing the release that's already out

- The `_2.13` artifacts have different coordinates from `_3`, for example `quillbrook-core_2.13` against `quillbrook-core_3`. You can therefore still publish them under the same version.
- To do that, fix the build, then re-run the workflow on the existing tag.
- A new patch release is cleaner and avoids confusion about a half-published version. Central releases can't be edited or deleted.