# Copperfen SDK publishing: the 1.3.0 hand-off, then the plan

**I did not run `npm publish`.** The publishing rules I follow forbid me from running a publish, unpublish, deprecate, dist-tag move or any registry change. A published version is public and permanent, and nobody can replace it. Below are the exact preflight and publish commands for you to run.

I also couldn't check your package. This session is in a different repository with no `packages/sdk-js`, so I have not seen your `package.json`. Everything about the package is marked as an assumption.

## Part 1: ship 1.3.0 today (you run these)

Run these from `packages/sdk-js` on the commit you want to release. Only the last step changes the registry.

1. **Check the version and tag.** Replace `<name>` with the `name` field in `package.json`.
   ```sh
   node -p "require('./package.json').version"        # must print 1.3.0
   npm view <name> dist-tags --json                    # note what "latest" is today
   ```
   - If `latest` is already above 1.3.0, stop and tell me. npm 11+ refuses a lower version without `--tag`, and a backport must not move `latest`.
   - If `<name>` returns E404, the package does not exist yet. Tell me, because the first-publish path differs.
2. **Preflight the package shape.** These are read-only.
   ```sh
   npm pack --dry-run                    # check the file list: no .env, no tests, no secrets
   npx publint
   npx @arethetypeswrong/cli --pack
   ```
   - Add a `prepack` build script so a stale `dist/` can't ship.
   - Set `files` as an allow-list.
   - For a scoped package, pass `--access public` (or set `publishConfig.access`) explicitly.
3. **Log in as a human.** Run `npm login` in your own terminal with your own 2FA. Do not paste a token into this chat or into a file. Classic npm tokens were revoked on 2025-12-09. Granular write tokens last 90 days at most, so a laptop session is the right credential for a one-off.
4. **Publish.** This step is **public and irreversible**.
   ```sh
   npm publish --access public
   ```
   - Do not hard-code `--tag latest`.
   - For a pre-release, add `--tag next`.
5. **If 1.3.0 turns out to be bad,** don't unpublish. Publish 1.3.1, then run `npm deprecate <name>@1.3.0 "Broken X, use 1.3.1"`.

**Make this the last laptop publish.** Anyone with publish rights on the package today can still push from a laptop. Part 2 closes that.

## Part 2: standing publishing process (draft, pending your approval)

### 1. Assumptions and inventory

I have not been able to confirm any of these. Please correct the table.

| Package | Registry | Publish path today | Credential | Expiry | Owners | Target |
|---|---|---|---|---|---|---|
| `packages/sdk-js` (assumed library) | npm | engineer laptop | personal 2FA session or an unknown token | unknown | unknown | CI on a protected tag, trusted publishing (OIDC) |
| other SDKs ("some SDKs") | unknown | laptops | unknown | unknown | unknown | decided per registry once known |

Assumptions:
- GitHub Actions on GitHub-hosted runners, in a monorepo.
- npm is the only registry for this package.
- Library only, no binaries.
- A standing process, not a one-off.

Any npm token that nobody can locate counts as compromised. Please list every token and every account with write access to the package.

### 2. Questions for you

Answer these and I will finalize the plan.
1. What are the other SDKs and their registries (PyPI, Maven, NuGet, Go, …)? I need this to load the right per-registry rules.
2. Is CI GitHub Actions on hosted runners? Self-hosted runners can't use npm OIDC.
3. Who owns the npm org and the `@copperfen` scope, and which 2FA type do they use?
4. Are the SDKs tied to a paid product? Maven Central charges for commercial-nature artifacts.
5. Do you have private packages or an internal feed?
6. Is there an audit, incident or deadline driving this? Also, who can approve releases, and how much extra release latency is acceptable?

### 3. npm decisions

- **Credential:** trusted publishing, bound to a protected `release` environment. Order of work:
  1. Configure the trusted publisher.
  2. Validate it with one real release.
  3. Set the package to "Require two-factor authentication and disallow tokens".
  4. Revoke every remaining write token.
- **Register the trusted publisher the day you run the first CI release.** npm expires a configuration that isn't validated by a publish within 48 hours.
- **Trusted publisher fields:**
  - owner and repository
  - workflow file name only (`release.yml`, not a path)
  - environment `release`
- **Approval gate:** use `npm stage publish`. CI stages the tarball and a maintainer approves it with 2FA.
  - Keep direct publish and "Allow npm dist-tag" off, so a compromised workflow can't reach `latest`.
  - Make a team the reviewer, or name at least two people besides whoever cuts releases. Block self-review.
- **Namespace:** claim the `@copperfen` org scope on public npm if it isn't claimed. Keep at least two owners with phishing-resistant 2FA.
- **Versioning:** SemVer per package. One immutable version per release. Pre-releases go on a non-default tag (`next`, `beta`, `rc`). CI checks that the tag equals the manifest version.
- **Provenance:** trusted publishing generates it automatically for a public package from a public repository. Provenance proves which workflow built the package, not that it is safe.

### 4. Pipeline files (drafts)

**Repository setup**, to be done by an org admin:
1. Add a tag ruleset so only release managers can create, move or delete `*/v*` tags.
2. Create a `release` environment with team reviewers, self-review blocked, and deployments restricted to release tags.
3. Set no publishing secrets in the repository.

Check that your plan supports environment protection on private repositories.

**`.github/workflows/release.yml`.** Release by pushing a tag like `sdk-js/v1.3.1`. Replace every `<sha>` with a full commit SHA. Resolve each with `git ls-remote https://github.com/<owner>/<action> refs/tags/<version>`, or let Dependabot pin them. Replace `<pinned 11.15+ version>` with a pinned npm version of 11.15.0 or later.

```yaml
name: release
on:
  push:
    tags: ["*/v*"]                      # monorepo tags: <package>/vX.Y.Z
permissions: {}

jobs:
  build:                                # unprivileged: no secrets, no id-token
    runs-on: ubuntu-latest
    permissions: { contents: read }
    outputs:
      dist_tag: ${{ steps.ver.outputs.dist_tag }}
    steps:
      - uses: actions/checkout@<sha>  # v6
        with: { persist-credentials: false }
      - uses: actions/setup-node@<sha>  # v6
        with: { node-version: "24", package-manager-cache: false }
      - name: Tag must equal manifest version; derive the dist-tag
        id: ver
        run: |
          tag="${GITHUB_REF_NAME##*/}"; tag="${tag#v}"
          pkg="${GITHUB_REF_NAME%/*}"
          dir="packages/$pkg"
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
                 else channel="latest-${version%%.*}"; fi ;;   # backport: never move latest backwards
          esac
          echo "dist_tag=$channel" >> "$GITHUB_OUTPUT"
          echo "DIR=$dir" >> "$GITHUB_ENV"
      - run: npm ci && npm run build && npm test && npm pack "./${DIR}"
      - uses: actions/upload-artifact@<sha>  # v5
        with: { name: dist, path: "*.tgz" }

  publish:
    needs: build
    runs-on: ubuntu-latest
    environment: release                # reviewers approve here; name must match npm config
    permissions:
      contents: read
      id-token: write                   # OIDC, this job only
    env:
      DIST_TAG: ${{ needs.build.outputs.dist_tag }}
    steps:
      - uses: actions/download-artifact@<sha>  # v5
        with: { name: dist }
      - uses: actions/setup-node@<sha>  # v6
        with: { node-version: "24", registry-url: "https://registry.npmjs.org", package-manager-cache: false }
      - run: npm install -g npm@<pinned 11.15+ version>
      - run: npm stage publish ./*.tgz --access public --tag "$DIST_TAG"
```

Notes:
- Set no `NODE_AUTH_TOKEN` in the publish job.
- Add no `workflow_dispatch`, `pull_request_target` or branch trigger. npm rejects OIDC from `pull_request_target`.
- Use no restored caches.
- If your private dependencies need a read token, scope it to the `npm ci` step only.
- A maintainer then runs `npm stage list`, `npm stage view <id>` and `npm stage approve <id>`.
- If you use changesets, semantic-release or pnpm publish, let the tool version and pack. Then run `npm stage publish` per tarball.

### 5. Rollback runbook (commands for you to run)

1. Publish the fix as a new version immediately. Never wait on a delete.
2. Soft-remove the bad version:
   ```sh
   npm deprecate <name>@<bad> "Broken <what>, use <good>"
   ```
3. If `latest` points at the bad version, move it back:
   ```sh
   npm dist-tag add <name>@<good> latest
   ```
4. Compromise suspected: isolate build hosts first, then revoke and rotate every credential the release job could reach.
5. Hard unpublish only for leaked secrets or malware. It is allowed within 72 hours if no public package depends on it. The `name@version` is never reusable.
6. Announce in the changelog and the security advisory channel.

Rehearse steps 1–3 on a scratch scoped package, never on `@copperfen/sdk-js`. Every public rehearsal burns a version forever.

### 6. Private packages

I can't tell whether you have any. If you do, tell me the feed. The default is one internal endpoint that refuses internal names from public upstreams, plus a committed `.npmrc` mapping `@copperfen` to it. Set `publishConfig.registry` on every private package so a stray `npm publish` can't reach npmjs.com. Prove the block works with the canary probe in the skill. A 401, 403 or 5xx response is inconclusive and does not count as a pass.

### 7. Migration sequence

| When | Step | Evidence it leaves |
|---|---|---|
| Today, 2026-10-23 | Part 1 (1.3.0 from a laptop) | version on npm |
| Today | Inventory every token, owner and 2FA type. Revoke anything you can't locate. | inventory table |
| Next 1–2 days | Claim the scope. Add the tag ruleset and the `release` environment. | repository settings |
| Release day for 1.3.1 | Merge `release.yml`. Register the trusted publisher. Run one real release with a patch or pre-release. | green run, provenance on the package page |
| Right after validation | Set the package to disallow tokens. Revoke all write tokens. | npm package settings |
| Within 2 weeks | Rehearse the rollback on a scratch package. Repeat for the other SDKs. | rehearsal notes |

**Done when:**
- No long-lived publish tokens remain on registries that offer OIDC.
- Every publish runs from CI on a protected tag, with no laptop publishes after the first release.
- The rollback has been rehearsed.

I'll finalize the files once you answer the questions in section 2 and give me the package name.