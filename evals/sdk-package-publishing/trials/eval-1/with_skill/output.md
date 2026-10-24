# Publishing plan for `@keelharbor/sdk`

**Do not use `NPM_TOKEN`.** A token from early 2024 can't work. npm revoked every classic and automation token on 2025-12-09, and granular write tokens now expire within 90 days. The workflow below uses npm trusted publishing (OIDC), so it needs no secret. It also adds a human approval step, because two paying enterprise customers build against the package.

The workflow is a draft. I haven't run it or touched npm. The action SHAs and the pinned npm version are placeholders you must fill in.

## 1. Assumptions and inventory

| Item | Value |
|---|---|
| Package | `@keelharbor/sdk`, a single TypeScript library, no binaries |
| Registry | public npm, already published from your laptop |
| CI | GitHub Actions on GitHub-hosted runners, so OIDC is available |
| Current credential | the 2024 token in 1Password, which is dead and counts as compromised |
| Target | trusted publisher bound to a protected `release` environment, plus npm staged publishing, with no tokens at all |

I assumed:
- The package is public, the repo is public (so provenance is generated automatically), and the build needs no private dependency token.
- The `@keelharbor` scope is already claimed.
- You and one other person can approve releases, and a few minutes of approval latency per release is fine.

If any of these is wrong, tell me. A private repo changes the provenance and environment-protection details. A private dependency needs a read-only token scoped to the `npm ci` step only.

## 2. Pipeline file: `.github/workflows/release.yml`

The file name must be exactly `release.yml`, because the npm trusted-publisher configuration matches on it.

```yaml
name: release
on:
  push:
    tags: ["v*"]                       # same pattern as the tag ruleset and environment rule
permissions: {}                        # nothing by default

jobs:
  build:                               # unprivileged: no secrets, no id-token
    runs-on: ubuntu-latest
    permissions: { contents: read }
    outputs:
      dist_tag: ${{ steps.ver.outputs.dist_tag }}
    steps:
      - uses: actions/checkout@<sha>   # v6
        with: { persist-credentials: false }
      - uses: actions/setup-node@<sha> # v6
        with: { node-version: "24", package-manager-cache: false }   # no restored caches
      - name: Tag must equal manifest version; derive the dist-tag
        id: ver
        run: |
          tag="${GITHUB_REF_NAME#v}"
          version="$(node -p "require('./package.json').version")"
          name="$(node -p "require('./package.json').name")"
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
                 else channel="latest-${version%%.*}"; fi ;;   # backport: never move latest backwards
          esac
          echo "dist_tag=$channel" >> "$GITHUB_OUTPUT"
      - run: npm ci && npm run build && npm test && npm pack
      - uses: actions/upload-artifact@<sha>  # v5
        with: { name: dist, path: "*.tgz" }

  publish:
    needs: build
    runs-on: ubuntu-latest
    environment: release               # reviewers approve here; name must match the npm trusted-publisher config
    permissions:
      contents: read
      id-token: write                  # OIDC, this job only
    env:
      DIST_TAG: ${{ needs.build.outputs.dist_tag }}
    steps:
      - uses: actions/download-artifact@<sha>  # v5
        with: { name: dist }
      - uses: actions/setup-node@<sha> # v6
        with: { node-version: "24", registry-url: "https://registry.npmjs.org", package-manager-cache: false }
      - run: npm install -g npm@<pinned 11.15+ version>   # staged publishing needs 11.15.0+
      # No NODE_AUTH_TOKEN anywhere. Provenance is automatic for a public repo.
      - run: npm stage publish ./*.tgz --access public --tag "$DIST_TAG"
```

Why it is built this way:
- **Two jobs.** The build job runs your dependencies and tests, so it has no secrets and no `id-token`. The publish job holds the only publish identity and installs nothing except the npm client.
- **Tag guard.** The tag must equal the `package.json` version. Pre-releases go to a channel tag (`next`, `beta`, `rc`), and a backport release never moves `latest` backwards.
- **`npm stage publish` instead of `npm publish`.** CI uploads the tarball for review and never reaches `latest` on its own, so a compromised workflow can't ship malware to your customers.
- **No pull-request triggers and no `workflow_dispatch`.** npm rejects OIDC from `pull_request_target`, and a manual trigger would bypass the gate.

## 3. One-time setup

Setup steps 1 to 5 change repo settings or npm, so I've left them for you to run. Do them in this order:

1. **Repo, tag ruleset.** Only release managers may create, move or delete `v*` tags.
2. **Repo, environment.** Create `release` with these settings:
   - Reviewers: a team, or at least two people besides whoever cuts releases (any one approves).
   - Self-review: blocked.
   - Deployments: restricted to `v*` tags.
   - Check that your GitHub plan supports environment protection on this repo.
3. **Repo, secrets.** Add no `NPM_TOKEN`.
4. **npm, trusted publisher on `@keelharbor/sdk`.** Use the package Settings page, or `npm trust` (needs npm 11.10.0+; check `npm trust --help`). Set these fields:
   - Owner and repository: your GitHub org and repo.
   - Workflow file: `release.yml`, not a path.
   - Environment: `release`.
   - Permissions: staging allowed. Leave direct publish and "Allow npm dist-tag" off.
5. **Cut the first release the same day.** npm expires a configuration that no publish has validated within 48 hours.
6. **After that release is validated:**
   - Set the package's publishing access to "Require two-factor authentication and disallow tokens".
   - Revoke every remaining npm write token.
   - Delete the stale entry from 1Password.

   A live token would leave the old attack path open.

Optionally, pin actions with Dependabot or Renovate. Resolve each SHA with `git ls-remote https://github.com/<owner>/<action> refs/tags/<version>`, and don't invent one.

## 4. Release flow

1. Bump the version in `package.json` and merge.
2. Push the tag `vX.Y.Z`.
3. The build job runs the tests and packs the tarball.
4. A reviewer approves the `release` environment, and the publish job stages the tarball.
5. A maintainer runs `npm stage list`, then `npm stage view <stage-id>` (or `npm stage download <stage-id>`) to inspect it, then **`npm stage approve <stage-id>`** (2FA prompt). Use `npm stage reject <stage-id>` to refuse it. Approval waits for npm's malware scan.

Before the first release, run `npm pack --dry-run`, `npx publint` and `npx @arethetypeswrong/cli --pack` locally. Confirm that `files` is an allow-list, `exports` lists `types` first and `default` last, and `prepack` builds.

## 5. Rollback runbook

Run these commands yourself. I haven't run them.

1. Publish the fix as a new version through the normal tag flow.
2. Soft-remove the bad version: **`npm deprecate @keelharbor/sdk@X.Y.Z "Broken <thing>, use X.Y.(Z+1)"`**.
3. Move `latest` only if it points at the bad version: **`npm dist-tag add @keelharbor/sdk@<last-good> latest`**.
4. If you suspect compromise, isolate the build hosts first. Then revoke and rotate everything the release job could reach.
5. Reserve unpublish for leaked secrets or malware. It is allowed only within 72 hours if no public package depends on it, and the version number can never be reused.
6. Announce the problem in the changelog and your security advisory channel.

Rehearse steps 2 and 3 on a scratch scoped package, never on `@keelharbor/sdk`. Every public rehearsal burns a version number forever.

## 6. Migration sequence

| Step | When | Evidence it leaves |
|---|---|---|
| Add the tag ruleset and `release` environment | today | repo settings screenshot |
| Merge `release.yml` and register the trusted publisher | release day | workflow run log |
| First tag release, staged and approved | within 48 hours of registering | npm provenance badge, `npm audit signatures` |
| Disallow tokens, revoke old tokens, delete the vault entry | right after that release works | npm settings page |
| Stop laptop publishes | after the first successful CI release | none needed |

Two things to expect:
- Releases now wait on a human approval. That is deliberate for these customers.
- Release tools that wrap `npm publish` (changesets, semantic-release, release-please) may not support OIDC or staged publishing yet. Let them version and pack, and keep `npm stage publish` as the publish step.