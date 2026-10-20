# Release workflow

## Contents

- Repository protection setup
- Two-job skeleton (GitHub Actions)
- Publish steps per registry
- GitLab CI differences
- Monorepos and multi-package releases
- Dependency-confusion probe

## Repository protection setup

1. Tag ruleset: only release managers may create, move or delete tags matching `v*` (or `<package>/v*`). On Go this rule is the publish credential.
2. Publish environment (`release`): reviewers listed as a team, or at least two people besides whoever usually cuts releases; any one approves; self-review blocked; deployments restricted to `v*` tags. Environment protection on private repositories needs a plan that supports it; check before designing around it.
3. The environment name in the job must match the environment named in the registry's trusted-publisher configuration exactly.
4. Repository and organization secrets: none for publishing once trusted publishing works. Read-only feed credentials live in the environment of the jobs that install private dependencies.

## Two-job skeleton (GitHub Actions)

Pin every action to a full commit SHA with the version as a comment. Resolve a SHA with `git ls-remote https://github.com/<owner>/<action> refs/tags/<version>` or let Dependabot or Renovate pin and bump it; never invent one.

```yaml
name: release
on:
  push:
    tags: ["v*"]
permissions: {}                      # nothing by default

jobs:
  build:                             # unprivileged: no secrets, no id-token
    runs-on: ubuntu-latest
    permissions: { contents: read }
    outputs:
      dist_tag: ${{ steps.ver.outputs.dist_tag }}
    steps:
      - uses: actions/checkout@<sha>  # v6
        with: { persist-credentials: false }
      - name: Tag must equal manifest version; derive the dist-tag
        id: ver
        run: |
          tag="${GITHUB_REF_NAME##*/}"; tag="${tag#v}"
          pkg="${GITHUB_REF_NAME%/*}"                          # monorepo tags: <package>/vX.Y.Z
          if [ "$pkg" = "$GITHUB_REF_NAME" ]; then dir=.; else dir="packages/$pkg"; fi
          version="$(node -p "require('./$dir/package.json').version")"
          name="$(node -p "require('./$dir/package.json').name")"
          [ "$tag" = "$version" ] || { echo "tag $tag != version $version"; exit 1; }
          case "$version" in
            *-*) channel="${version#*-}"; channel="${channel%%.*}"
                 case "$channel" in alpha|beta|rc|next) ;; *) echo "unknown channel $channel"; exit 1 ;; esac ;;
            *)   # default to 0.0.0 only on a genuine not-found; any other error stops the release
                 if out="$(npm view "$name" dist-tags.latest 2>err.log)"; then current="$out"
                 elif grep -q E404 err.log; then current=0.0.0
                 else cat err.log; exit 1; fi
                 highest="$(printf '%s\n%s\n' "$current" "$version" | sort -V | tail -n1)"
                 if [ "$highest" = "$version" ]; then channel=latest
                 else channel="latest-${version%%.*}"; fi ;;      # backport: never move latest backwards
          esac
          echo "dist_tag=$channel" >> "$GITHUB_OUTPUT"
          echo "DIR=$dir" >> "$GITHUB_ENV"                      # same job only
      - run: npm ci && npm run build && npm test && npm pack "./${DIR:-.}"   # build once; no restored caches
      - uses: actions/upload-artifact@<sha>  # v5
        with: { name: dist, path: "*.tgz" }

  publish:
    needs: build
    runs-on: ubuntu-latest
    environment: release              # reviewers approve here
    permissions:
      contents: read
      id-token: write                 # OIDC, this job only
    env:
      DIST_TAG: ${{ needs.build.outputs.dist_tag }}
    steps:
      - uses: actions/download-artifact@<sha>  # v5
        with: { name: dist }
      - uses: actions/setup-node@<sha>  # v6
        with: { node-version: "24", registry-url: "https://registry.npmjs.org", package-manager-cache: false }
      - run: npm install -g npm@<pinned 11.15+ version>   # staged publishing needs 11.15.0+
      - run: npm stage publish ./*.tgz --access public --tag "$DIST_TAG"
```

- A restricted npmjs package returns 404 to an anonymous `npm view`: give that step a read-only token, or the guard treats every release as the first.
- The publish job installs nothing from the network except the registry client, and runs no project scripts.
- Never add `workflow_dispatch` or a branch trigger to the publish job without the same environment gate.

## Publish steps per registry

The publish job uploads an artifact the build job produced. Where a registry client rebuilds during publish, move that build out or treat the publish job as privileged build code behind the environment gate.

| Registry | Build job | Publish job |
|---|---|---|
| npm | `npm pack` | `npm stage publish <tarball> --access public --tag <channel>`; a maintainer runs `npm stage approve <stage-id>` with 2FA |
| PyPI | `python -m build`, `twine check --strict` | `pypa/gh-action-pypi-publish@<sha>` with `dist/`; no token input |
| crates.io | `cargo publish --dry-run` | `rust-lang/crates-io-auth-action@<sha>`, then `cargo publish --no-verify` from the same commit (skips re-running `build.rs` with the token present) |
| NuGet | `dotnet pack` | `NuGet/login@<sha>`, then `dotnet nuget push` with its output key |
| Maven Central | build the bundle (`central-publishing-maven-plugin` with `skipPublishing=true`); a separate signing job adds the `.asc` files | upload the bundle to the Portal Publisher API with the token; a maintainer publishes or drops the validated deployment |
| Docker Hub | build to an OCI layout, no push | push the prebuilt layout (`crane push <layout-dir> <ref>`, `oras cp --from-oci-layout`, or `buildx imagetools create` from buildx 0.33+), then `cosign sign <image>@<digest>` |
| Go | tests only | no publish job: the protected tag is the release; a follow-up job only warms the proxy with `go list -m` |

Sign in a dedicated job that downloads the unsigned artifact, holds only the signing key in its own protected environment, and runs no project code. Never put a long-lived signing key in the build job (it runs every dependency and test) or in the job holding the upload token.

## GitLab CI differences

- OIDC tokens come from `id_tokens` with a registry-specific `aud`. Every job in the pipeline can mint one, so put publishing in a protected pipeline that runs only for protected tags or branches.
- NuGet requires a branch `ref`: publish from a protected release branch pipeline, not a tag pipeline.
- Use protected environments with approval rules as the review gate.

## Monorepos and multi-package releases

- Publish in dependency order, leaves first.
- Make the job idempotent: skip any `name@version` the registry already holds, so a rerun after a partial failure completes the release instead of failing on the first package.
- Treat a partial release as roll-forward: finish publishing, never unpublish the packages that made it.
- Release tools that wrap the registry client (changesets, semantic-release, release-please, pnpm or yarn publish) may not support staged publishing or OIDC yet. Let the tool version and pack, then run the registry's own publish command per tarball, or keep direct publish enabled only for that configuration behind the environment gate.

## Dependency-confusion probe

A probe only proves something if a public package with an internal-looking name actually exists upstream. Removing the internal source and watching installs fail proves nothing: everything fails.

1. **Canary.** npm: publish one harmless canary in your own public scope (`@corp/confusion-canary`), never internally. Other registries: use an existing public package whose name matches an internal prefix rule. Never publish a canary to Maven Central or nuget.org (permanent), and PyPI and crates.io ban placeholders.
2. **Query the internal endpoint's metadata only.** Never download or install the probe target: a misconfigured endpoint would serve squatter code, and building an sdist runs it.

Authenticate with the read-only credential CI uses, prove the request can see the feed, then assert the exact status. A 401, 403, 5xx or DNS error is inconclusive, never a pass.

```sh
# credentials from a netrc file, never argv
code() { curl -s -o /dev/null -w '%{http_code}' --netrc-file "$FEED_NETRC" "$1"; }
[ "$(code "$INTERNAL_INDEX/corp-sdk/")" = 200 ] || { echo "probe cannot see the feed"; exit 1; }
[ "$(code "$INTERNAL_INDEX/<public corp-* name>/")" = 404 ] || { echo "probe FAILED or inconclusive"; exit 1; }
# npm: `npm view "@corp/confusion-canary" --registry "$INTERNAL_NPM"` must fail with E404, not E401/E403
```

3. **Check the blocking rule itself** on the feed: the exclude pattern, routing rule, origin control or disabled forwarding covers every internal prefix. Use the feed's rule-test feature where it has one.
4. **Check client resolution:** every internal entry in the lockfile points at the internal host (`uv.lock` source, `package-lock.json` resolved URL, `packages.lock.json` source).
5. When no public name exists to probe with, steps 3 and 4 are the proof; record that step 2 did not apply.
6. Repeat after any feed reconfiguration: deleting a private package while public forwarding is on reopens the hole.
