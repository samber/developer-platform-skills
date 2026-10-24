# Fennel Labs: fix `@fennel/client` `latest`, and stop the workflow publishing a beta to `latest`

## Assumptions

I couldn't ask you anything, so these are my assumptions. Correct me if any are wrong.

- CI is GitHub Actions on GitHub-hosted runners.
- Releases run from a tag push.
- It's a single package, `@fennel/client`, under the `@fennel` npm scope.
- Publishing uses `NPM_TOKEN` or a similar static token. I don't know which, so check this first (see "Credentials" below).

I haven't run anything against the registry. Every command that changes npm state is yours to run.

## 1. Don't unpublish. Move `latest` back.

Unpublishing is the wrong fix for three reasons:

- **Removing it doesn't help people who already have it.** `3.0.0-beta.1` has been live for hours. Anyone who installed it has it in their lockfile or cache, and removing it only breaks those lockfiles. npm never lets you reuse a version number either, so `3.0.0-beta.1` can't be re-published.
- **It's riskier than it looks.** Your 72-hour window is still open, but it only works if no public package depends on the beta. You'd also be deleting a build you say mostly works, and you'd likely want that build as the real beta later.
- **The actual problem is the tag.** `latest` points at the wrong version. That's fixed by moving the tag. The result is the same for new installs, it's reversible, and it doesn't break lockfiles.

Run these in order:

```sh
# 0. Read-only: confirm the current state
npm view @fennel/client dist-tags
npm view @fennel/client versions --json

# 1. Point latest back at stable (changes the registry, needs 2FA)
npm dist-tag add @fennel/client@2.9.4 latest

# 2. Give the beta its own channel
npm dist-tag add @fennel/client@3.0.0-beta.1 beta

# 3. Verify
npm view @fennel/client dist-tags     # latest = 2.9.4, beta = 3.0.0-beta.1
npm view @fennel/client version       # 2.9.4
```

Steps 1 and 2 are the only changes. A plain `npm install @fennel/client` gets 2.9.4 again immediately.

**Deprecate the beta only if it's actually broken.** You said the rough edges are minor, so skip this by default. If you decide the beta is unsafe, run:

```sh
npm deprecate @fennel/client@3.0.0-beta.1 "Pre-release published by mistake. Use 2.9.4, or @beta for the 3.x preview."
```

Installs keep working and show a warning. Clear it later with an empty message.

**Who is still affected:**

- Anyone who installed during the window and committed a lockfile stays on the beta until they update.
- A `^3.0.0-beta.1` range in their `package.json` also keeps them there.
- Post a short note in your changelog or release channel telling them to pin `2.9.4` or run `npm install @fennel/client@latest`.

**If you still want to unpublish** (for example because the beta leaked a secret), do it inside the 72-hour window with `npm unpublish @fennel/client@3.0.0-beta.1`. This is a real deletion with no dry run. Only do it if no public package depends on the beta, and run it yourself. For a leaked secret, rotate the secret first.

## 2. Why it happened

`--tag latest` is hard-coded in the publish step. npm 11 refuses to publish a pre-release without a tag, but an explicit `--tag latest` overrides that safety. The same line causes the second bug: re-running an old release job, or backporting a fix to 2.x, would move `latest` backwards.

## 3. Fix the workflow

The tag is derived from the version, and the pipeline stops if the tag and `package.json` disagree.

| Version published | Dist-tag | Why |
|---|---|---|
| `3.0.0-beta.1` | `beta` | Pre-release channel comes from the version string. |
| `3.1.0` while `latest` is 3.0.0 | `latest` | Highest stable version. |
| `2.9.5` backport while `latest` is 3.x | `latest-2` | Never moves `latest` backwards. |
| `2.9.5` while `latest` is 2.9.4 | `latest` | It is the highest stable version. |
| Unknown suffix (e.g. `-foo.1`) | Fails | Forces a deliberate decision. |

**Draft, pending your approval.** Replace `<sha>` with real commit SHAs (resolve with `git ls-remote https://github.com/<owner>/<action> refs/tags/<version>`, or let Renovate pin them). Pin the npm version to a real 11.15.0 or later.

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
    outputs:
      dist_tag: ${{ steps.ver.outputs.dist_tag }}
    steps:
      - uses: actions/checkout@<sha>  # v6
        with: { persist-credentials: false }
      - name: Tag must equal package.json version; derive the dist-tag
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
      - run: npm install -g npm@<pinned 11.15+ version>
      - run: npm stage publish ./*.tgz --access public --tag "$DIST_TAG"
```

Notes on this workflow:

- **Stage-then-approve.** `npm stage publish` stages the release. A maintainer then runs `npm stage list`, then `npm stage approve <stage-id>` (this needs 2FA). Even a wrong tag therefore gets a human look before it reaches `latest`. Pre-releases still need the explicit `--tag`, which is why the guard derives it.
- **The release job only trusts tags.** Add no `workflow_dispatch` or branch trigger to the publish job.
- **Tag trigger.** The protected tag pattern `v*` must match your repository's tag ruleset and the environment's allowed deployment tags.
- **Backport tags.** Backports tag as `latest-2` (`latest-${major}`). For example, 2.9.5 shipped while `latest` is 3.x is installable with `npm install @fennel/client@latest-2`. Cut backport releases from a `2.x` branch tag the same way.
- **Backport rule.** The guard compares against the registry's current `latest`. If you tag `v2.9.5` before 3.0.0 goes stable, it gets `latest`. After 3.0.0 is stable, it gets `latest-2`.

## 4. Credentials

Check how CI authenticates today. Trusted publishing is the better fix than a token.

1. **Check for tokens.** Classic npm tokens no longer exist. Granular write tokens expire within 90 days at most. If `NPM_TOKEN` is in use, it's temporary and will break on a schedule.
2. **Set up trusted publishing.** On npmjs.com, add a trusted publisher for `@fennel/client`. Fill in the GitHub owner, repository, workflow file name only (`release.yml`, not a path), and environment `release`. The environment must exactly match the job's `environment:` name.
3. **Validate it within 48 hours.** An unvalidated configuration expires after that, so register it the day you do a real release.
4. **Then lock it down.** In the package's publishing access, choose "Require two-factor authentication and disallow tokens". Revoke every remaining write token afterwards. Do the revocation last, once one real release has succeeded via OIDC.
5. **Allow staging only.** Keep direct `npm publish` and "Allow npm dist-tag" off in the trusted-publisher configuration. A compromised workflow then can't reach `latest`.

**Protect the environment.** Create a `release` environment with two or more reviewers besides whoever cuts releases (any one approves), self-review blocked, and deployments restricted to release tags. Restrict who can create `v*` tags with a tag ruleset.

**Harden while you're in there:**

- SHA-pin every third-party action.
- Default permissions to none.
- Use no restored caches in build or publish jobs.
- Use no `pull_request_target` or `workflow_run` triggers on the release workflow.

## 5. Rollback runbook for future mistakes

1. **Publish the fix as a new version.** Don't wait on a delete.
2. **Move the tag only if it points at the bad version.** `npm dist-tag add @fennel/client@<good> latest`. Then `npm deprecate @fennel/client@<bad> "<message naming the safe version>"`.
3. **Suspected compromise?** Isolate build hosts first, then revoke and rotate every credential the release job could reach.
4. **Hard deletion** (unpublish) is for leaked secrets or malware inside the 72-hour window. Past that, contact npm security.
5. **Announce** in your changelog and advisory channel.

**Rehearse steps 1 and 2 on a scratch scoped package**, never on `@fennel/client`. Every public rehearsal burns a version number forever.

## 6. Order of work

1. **Today:** run the three `dist-tag` commands in section 1 and verify. This stops the damage.
2. **Today:** post a short note for users who got the beta.
3. **Before the next release:** merge the workflow fix and test the guard. Push a throwaway tag against a scratch package (`v0.0.1-beta.1`) and confirm it resolves to `beta`.
4. **This week:** set up trusted publishing and the protected `release` environment, run one real release through it, then disallow tokens and revoke the old ones.
5. **Later:** ship `3.0.0-beta.2` through the new pipeline with `--tag beta`. Promote 3.0.0 to `latest` when you're ready.