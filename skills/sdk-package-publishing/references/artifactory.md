# JFrog Artifactory (private registry for every ecosystem)

## Contents

- Repository types and the default layout
- Virtual-repository ordering and dependency confusion
- CI auto-publishing and auth
- Library vs binary
- Client configuration
- Rollback

Artifactory hosts private packages and proxies public registries for npm, PyPI, Maven, Gradle, NuGet, Go, Cargo, Docker, RubyGems, Composer, pub, CocoaPods, Swift and many more types. It never publishes to the public registries: public releases still follow each registry's own reference.

## Repository types and the default layout

- **Local:** packages you deploy. **Remote:** a caching proxy of one public registry. **Virtual:** one URL that aggregates locals and remotes. **Federated:** a local repository mirrored across sites.
- Default layout per ecosystem: `npm-local` (internal packages), `npm-remote` (proxies npmjs), `npm` virtual (local plus remote). Clients resolve only from the virtual; CI deploys only to the local.
- Split locals by maturity (`npm-dev-local`, `npm-release-local`) when releases are promoted rather than rebuilt.

## Virtual-repository ordering and dependency confusion

- A virtual resolves a fixed version from local repositories first, then remote caches, then remotes, each group in its listed order.
- "Latest" and version-listing requests (npm metadata, the PyPI simple index, Maven metadata) merge every included repository. A higher public version of an internal name then wins: ordering alone does not stop dependency confusion.
- **Block internal names on every remote** with exclude patterns covering each internal prefix (`@corp/**` on npm, `corp-*` on PyPI, `com/corp/**` on Maven). This is the "blocks internal names upstream" rule of the main workflow.
- **Priority Resolution** on the local repository makes its metadata win over the others. It is unavailable for several covered types, including Cargo, NuGet, pub and Swift: on those, exclude patterns are the only server-side control.
- Include and exclude patterns do not apply to admin users. Never give CI or developers admin tokens: an admin debugging resolution sees internal and public names merged and "fixes" ordering instead. Confirm the probe's identity is non-admin before trusting its 404.
- Deleting an internal package from the local while the remote can serve that name reopens the hole: rerun the probe after every cleanup.

## CI auto-publishing and auth

- **OIDC (GitHub Actions):** create an OpenID Connect integration in Artifactory, then identity mappings that match token claims (`repository`, `ref`, `environment`) to a scoped token, capped at 24 hours.
  1. Build jobs: a mapping to read-only access on the virtuals.
  2. Publish job: a mapping matched on `environment: release` with deploy rights on `*-release-local` only.
  3. Workflow: `permissions: id-token: write`, then `jfrog/setup-jfrog-cli@<sha>` with `oidc-provider-name` equal to the integration's provider name. Feed its `oidc-user` and `oidc-token` outputs to the ecosystem client (`npm publish`, `gem push --host`, `twine upload`) so package metadata gets indexed; a raw file upload skips that for some types.
- **Other CI:** scoped access tokens with an expiry, one for read and one for deploy, from the secret store. Prefer access tokens to legacy API keys.
- **Provenance:** record build info (`jf rt build-publish`) so each artifact links to its CI run; sign with the registry-native method where one exists (cosign for images).

## Library vs binary

- Libraries go to the ecosystem's local repository (`npm-local`, `maven-release-local`).
- Binaries, CLI archives and installers go to a `generic` local repository, or to `docker-local` for images, with checksums beside them.
- Promote instead of rebuilding: deploy once to the dev local, test, then `jf rt build-promote <build> <number> <release-repo>`. The released artifact is then byte-identical to the tested one.

## Client configuration

Point every client at the virtual URL and keep the mapping from each registry reference:

- npm: `@corp:registry=https://corp.jfrog.io/artifactory/api/npm/npm/`
- pip and uv: one index, `https://corp.jfrog.io/artifactory/api/pypi/pypi/simple`
- Maven: `mirrorOf *` to the Maven virtual
- NuGet: the virtual as the only source, plus `packageSourceMapping`
- Go: `GOPROXY` at the Go virtual, `GONOSUMDB` scoped to internal prefixes
- Cargo, RubyGems, Composer, pub, CocoaPods, Swift: the virtual as the named internal source in each client's config

## Rollback

- Artifactory can delete or overwrite an internal version, but consumers have already cached and locked it. Roll forward with a new version, as on public registries.
- Block overwrites of released versions: grant CI deploy rights on release locals without the Delete/Overwrite permission.
