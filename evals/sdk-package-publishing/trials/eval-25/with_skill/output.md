ⓘ Nothing from my earlier answer survived, so this is the full deliverable.

**Next action:** ask Security the one question in section 1. It decides whether you get OIDC trusted publishing or a token fallback.

## 1. Blocker: the mandate conflicts with the registries

I read `SKILL.md`, `npm.md`, `pypi.md` and `release-workflow.md`.

| Registry | Self-hosted runners | Reusable workflow |
|---|---|---|
| npm | OIDC trusted publishing does not support self-hosted runners. | The configuration names a workflow file. I would test this on a scratch package before relying on it. |
| PyPI | The reference lists GitHub as a trusted publisher but is silent on self-hosted runners. It says to try an org custom OIDC issuer, then fall back to tokens. | Reusable workflows are not supported for trusted publishing. The upload job must sit in the top-level workflow file. |

"Self-hosted for every workflow, no exceptions" therefore rules out npm OIDC. It probably rules out PyPI OIDC too. "One reusable workflow does everything" is also not possible for PyPI.

**Ask Security to choose one:**
- **Plan A (recommended):** a narrow exception for the two publish-only jobs, run on GitHub-hosted runners. Builds, tests and wheels stay self-hosted. This gives full OIDC, no stored publish tokens, and "disallow tokens" on both registries.
- **Plan B (complies as written):** everything self-hosted, with token fallbacks. These are the narrowest tokens each registry allows, on a bot account, in the protected `release` environment.

I drafted Plan B because it matches your stated mandate. Section 3 shows the diff to Plan A.

## 2. Assumptions

State any that are wrong and I will redo the affected files.

- The org is `veldtstream` on GitHub. The reusable workflow lives in a repo called `veldtstream/release-workflows`.
- Both packages already exist on their registries, published from the VM. The first-publish special case does not apply.
- One repo ships both packages under one `v*` tag, with equal versions in `package.json` and `pyproject.toml`.
- Self-hosted runners exist, or will exist, with labels `[self-hosted, linux]`, `[self-hosted, macos]` and `[self-hosted, windows]`. Macs and Windows boxes are needed for the C extension wheels. Linux needs Docker for `manylinux`. They must be ephemeral and just-in-time (JIT), meaning one job per fresh runner.
- The GitHub plan supports environment protection on private repos. Verify this first. Without it, the approval gate does not exist.
- A PyPI organization exists or can be created. Custom issuers need one.
- Who owns the npm and PyPI accounts, and their 2FA type, is unknown.
- There are no internal packages. If there are, say so and I will add the private-consumption config.

**Dated hazards for the current VM credentials:**
- Classic npm tokens were revoked on 2025-12-09. Granular write tokens last 90 days at most.
- Bypass-2FA tokens lost account actions on 2026-07-31. Direct publish with them is due to end around 2027-01.
- Check the VM's npm token now. It is probably expiring or already limited.

## 3. Inventory and target model

| Package | Registry | Today | Plan A target | Plan B target |
|---|---|---|---|---|
| `@veldtstream/sdk` | npm | VM token, expiry unknown | OIDC + `npm stage publish` + approval, tokens disallowed | Stage-only granular token (≤90 days) from the `release` environment + `npm stage publish` + 2FA approval |
| `veldtstream` (sdist + wheels) | PyPI | VM credential, unknown | Trusted publisher bound to `release` environment | Org custom OIDC issuer if PyPI accepts it. Otherwise a project-scoped token, username `__token__`, in the environment |

**Per-registry decisions**
- **npm:**
  - Staged publish: CI stages, a human approves with 2FA. The tag is fixed at staging.
  - Do not set `--provenance`. npm generates provenance only for public repos, and this repo is private. The packages stay verifiable by origin only through the approval trail.
  - Namespace: confirm `@veldtstream` is claimed, with at least two owners using phishing-resistant 2FA.
- **PyPI:**
  - Wheels are built by `cibuildwheel`. Use `abi3` wheels if the C extension allows it, which shrinks the matrix.
  - Run `twine check --strict` on the merged set before upload.
  - Upload all wheels in one publish step. PyPI rejects files on releases older than 14 days.
  - PEP 740 attestations only attach under a trusted-publisher identity. Plan B with a token ships none.
- **Channel policy:** SemVer. The tag must equal the manifest version. Pre-releases use `-alpha|beta|rc|next` on npm and PEP 440 suffixes (`a1`, `b1`, `rc1`) on PyPI. The CI guard rejects any other pre-release channel. The guard never moves `latest` backwards.

## 4. Pipeline files (drafts pending your approval)

Replace every `<sha>` with a real commit SHA. Resolve each with `git ls-remote https://github.com/<owner>/<action> refs/tags/<version>`. Let Dependabot or Renovate bump them.

### 4.1 `.github/workflows/publish.yml` in `veldtstream/release-workflows`

```yaml
name: publish
on:
  workflow_call:
    inputs:
      npm:        { type: boolean, default: false }
      python:     { type: boolean, default: false }
      npm-dir:    { type: string,  default: "." }
      python-dir: { type: string,  default: "." }
permissions: {}

jobs:
  guard:                               # unprivileged: no secrets, no id-token
    runs-on: [self-hosted, linux]
    permissions: { contents: read }
    outputs:
      dist_tag: ${{ steps.ver.outputs.dist_tag }}
    steps:
      - uses: actions/checkout@<sha>   # v6
        with: { persist-credentials: false }
      - name: Tag must equal manifest versions; derive the npm dist-tag
        id: ver
        env:
          WANT_NPM: ${{ inputs.npm }}
          WANT_PY: ${{ inputs.python }}
          NPM_DIR: ${{ inputs.npm-dir }}
          PY_DIR: ${{ inputs.python-dir }}
        run: |
          tag="${GITHUB_REF_NAME#v}"
          if [ "$WANT_PY" = true ]; then
            pyv="$(python3 -c 'import sys,tomllib; print(tomllib.load(open(sys.argv[1]+"/pyproject.toml","rb"))["project"]["version"])' "$PY_DIR")"
            pytag="$(python3 -c 'import sys,re; print(re.sub(r"-?(alpha|beta|rc)\.?", lambda m: {"alpha":"a","beta":"b","rc":"rc"}[m.group(1)], sys.argv[1]))' "$tag")"
            [ "$pytag" = "$pyv" ] || { echo "tag $tag != pyproject version $pyv"; exit 1; }
          fi
          channel=latest
          if [ "$WANT_NPM" = true ]; then
            version="$(node -p "require('./$NPM_DIR/package.json').version")"
            name="$(node -p "require('./$NPM_DIR/package.json').name")"
            [ "$tag" = "$version" ] || { echo "tag $tag != package.json version $version"; exit 1; }
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
          fi
          echo "dist_tag=$channel" >> "$GITHUB_OUTPUT"

  build-npm:
    if: inputs.npm
    needs: guard
    runs-on: [self-hosted, linux]
    permissions: { contents: read }
    steps:
      - uses: actions/checkout@<sha>   # v6
        with: { persist-credentials: false }
      - uses: actions/setup-node@<sha> # v6
        with: { node-version: "24", package-manager-cache: false }   # no restored caches
      - working-directory: ${{ inputs.npm-dir }}
        run: npm ci && npm run build && npm test && npm pack --pack-destination "$RUNNER_TEMP/npm" && mkdir -p "$GITHUB_WORKSPACE/out" && mv "$RUNNER_TEMP"/npm/*.tgz "$GITHUB_WORKSPACE/out/"
      - run: npx publint && npx @arethetypeswrong/cli --pack ${{ inputs.npm-dir }}   # preflight
      - uses: actions/upload-artifact@<sha>   # v5
        with: { name: npm-dist, path: out/*.tgz }

  sdist:
    if: inputs.python
    needs: guard
    runs-on: [self-hosted, linux]
    permissions: { contents: read }
    steps:
      - uses: actions/checkout@<sha>   # v6
        with: { persist-credentials: false }
      - working-directory: ${{ inputs.python-dir }}
        run: python3 -m pip install build && python3 -m build --sdist --outdir "$GITHUB_WORKSPACE/out"
      - uses: actions/upload-artifact@<sha>   # v5
        with: { name: py-sdist, path: out/* }

  wheels:
    if: inputs.python
    needs: guard
    strategy:
      fail-fast: true
      matrix:
        os: [linux, macos, windows]
    runs-on: [self-hosted, "${{ matrix.os }}"]
    permissions: { contents: read }
    steps:
      - uses: actions/checkout@<sha>   # v6
        with: { persist-credentials: false }
      - uses: pypa/cibuildwheel@<sha>  # v4
        with:
          package-dir: ${{ inputs.python-dir }}
          output-dir: wheelhouse
      - uses: actions/upload-artifact@<sha>   # v5
        with: { name: "py-wheels-${{ matrix.os }}", path: wheelhouse/*.whl }

  check-python:
    if: inputs.python
    needs: [sdist, wheels]
    runs-on: [self-hosted, linux]
    permissions: { contents: read }
    steps:
      - uses: actions/download-artifact@<sha>   # v5
        with: { pattern: "py-*", merge-multiple: true, path: dist }
      - run: |
          python3 -m pip install twine
          twine check --strict dist/*
          tar tzf dist/*.tar.gz      # read it: no tests, fixtures or .env in the sdist
          ls dist
      - uses: actions/upload-artifact@<sha>   # v5
        with: { name: python-dist, path: dist/* }

  publish-npm:                         # Plan B: holds the stage-only token; Plan A: see section 5
    if: inputs.npm
    needs: [guard, build-npm]
    runs-on: [self-hosted, linux]
    environment: release               # reviewers approve here
    permissions: { contents: read }
    env:
      DIST_TAG: ${{ needs.guard.outputs.dist_tag }}
    steps:
      - uses: actions/download-artifact@<sha>   # v5
        with: { name: npm-dist }
      - uses: actions/setup-node@<sha>  # v6
        with: { node-version: "24", registry-url: "https://registry.npmjs.org", package-manager-cache: false }
      - run: npm install -g npm@<pinned 11.15+ version>   # staged publishing needs 11.15.0+
      - env:
          NODE_AUTH_TOKEN: ${{ secrets.NPM_STAGE_TOKEN }}   # environment secret, stage-only granular token
        run: npm stage publish ./*.tgz --access public --tag "$DIST_TAG"
```

**Unverified:** I could not confirm that a reusable workflow's job reads *environment* secrets of the caller repo. Test it on a scratch repo first. If it fails, pass the token through `secrets:` on `workflow_call`.

### 4.2 Caller in each repo: `.github/workflows/release.yml`

```yaml
name: release
on:
  push:
    tags: ["v*"]
permissions: {}

jobs:
  build-and-npm:
    uses: veldtstream/release-workflows/.github/workflows/publish.yml@<sha>   # pin the SHA, never @main
    permissions: { contents: read }
    with: { npm: true, python: true }

  pypi:                                # must live here: PyPI trusted publishing rejects reusable workflows
    needs: build-and-npm
    runs-on: [self-hosted, linux]
    environment: release
    permissions: { contents: read }    # add id-token: write only if the custom issuer path works
    steps:
      - uses: actions/download-artifact@<sha>   # v5
        with: { name: python-dist, path: dist }
      - uses: astral-sh/setup-uv@<sha>  # v7
      - env:
          UV_PUBLISH_TOKEN: ${{ secrets.PYPI_API_TOKEN }}   # Plan B token fallback; drop if the custom issuer works
        run: uv publish dist/*
```

I used `uv publish` because `pypa/gh-action-pypi-publish` is a Docker container action. It then needs Docker on the self-hosted runner, and Linux only.

### 4.3 Repository protection (all repos)

1. **Tag ruleset:** only release managers may create, move or delete `v*` tags. The workflow trigger, the ruleset and the environment's deployment rule must all list the same pattern.
2. **`release` environment:**
   - Reviewers: a team, or at least two people besides whoever cuts releases. One approval is enough.
   - Block self-review.
   - Restrict deployments to `v*` tags.
3. **Reusable workflow access:** the `release-workflows` repo is private. In its Settings, Actions, Access, allow other repos in the organization to use it.
4. **Runners:** ephemeral JIT only, in a runner group limited to the release repos. Build jobs get no secrets. Restore no caches in build or publish jobs.
5. **Hardening:** SHA-pin every third-party action and set default permissions to none, as in the files above. Do not use `pull_request_target` or `workflow_run`. Never add `workflow_dispatch` to the publish jobs.

### 5. Diff for Plan A (if Security grants the exception)

- In `publish-npm`, set `runs-on: ubuntu-latest`, add `id-token: write`, and delete `NODE_AUTH_TOKEN`.
- In the `pypi` job, set `runs-on: ubuntu-latest` and add `id-token: write`. Drop `UV_PUBLISH_TOKEN` and use `pypa/gh-action-pypi-publish@<sha>`.
- On npm, run `npm trust` or use the web UI. The fields are owner, repo, workflow file name and environment `release`. Register it the day you do the first release: an unvalidated configuration expires after 48 hours.
- On PyPI, add a GitHub trusted publisher bound to environment `release`.
- Then set npm access to "Require two-factor authentication and disallow tokens" and revoke every remaining token.

## 6. Rollback runbook

I did not run any of these. Run them yourself.

**npm, `@veldtstream/sdk`**
1. Publish the fix as a new version: tag, stage, approve.
2. `npm deprecate "@veldtstream/sdk@1.4.3" "Broken auth refresh, use 1.4.4"`
3. Only if `latest` points at the bad version: `npm dist-tag add @veldtstream/sdk@1.4.2 latest`
4. If a staged build looks wrong before approval: `npm stage reject <stage-id>`. This costs nothing.
5. Hard unpublish is a last resort. It is allowed only within 72 hours and with no dependents, and the `name@version` can never be reused. It is only for leaked secrets or malware.

**PyPI, `veldtstream`**
1. Publish the fix as a new version.
2. Yank the bad release in the PyPI project management page, with a reason that names the safe version. This is reversible.
3. A missing wheel on a platform: upload it to the same release within 14 days. After that, cut a new version.
4. Delete only for leaked secrets or malware. The filename is then burned permanently.

**If compromise is suspected:**
- Isolate the build hosts first.
- Revoke and rotate every credential the release job could reach.
- Announce in the changelog and your security advisory channel.

**Rehearsal:** run steps 1 to 2 on a scratch scoped npm package and on TestPyPI, never on production. Each public rehearsal burns a version forever.

## 7. Migration sequence

Today is 2026-10-23.

1. **Day 0:** confirm the plan and decide A or B with Security. Check the GitHub plan supports environment protection on private repos. Check the VM's npm token expiry: it is the likely first thing to break.
2. **Days 1 to 3:**
   - Stand up ephemeral self-hosted runners on Linux, macOS and Windows.
   - Create the `release-workflows` repo.
   - Add the tag ruleset and `release` environment.
   - Create a bot account on each registry, with 2FA.
3. **Days 3 to 5:**
   - Plan B: mint the stage-only npm token and the PyPI token, each scoped to its one package. Store them in the `release` environment and record the expiry date.
   - Plan A: register the trusted publishers.
4. **Days 5 to 7:**
   - Rehearse on the scratch npm package and TestPyPI.
   - Check whether the environment-secrets assumption in 4.1 holds.
   - Check that the wheels build on all three OSes.
5. **Week 2:** cut one real release through the new pipeline. A maintainer approves the stage with 2FA.
6. **Week 2, after step 5 succeeds:**
   - Plan A: switch npm to disallow tokens.
   - Both plans: revoke every old VM token on both registries and decommission the VM publish path.
   - Evidence to keep: the workflow run URL, the environment approval record, the npm stage approval, and the token-revocation timestamps.
7. **Every ~80 days (Plan B only):** rotate the npm token, which expires within 90 days. Put a calendar reminder on it. I could not verify any API that automates npm token rotation, so I am not promising automation.
8. **Next:** onboard the other repos. Each one adds the 4.2 caller file, the tag ruleset and the `release` environment.

## 8. Gates this plan has to pass

- **Zero long-lived publish tokens:** achievable only under Plan A. Plan B keeps two scoped, expiring tokens.
- **No laptop publishes after the first release:** enforced by the tag ruleset plus the environment gate.
- **Rollback rehearsed on both rehearsal targets:** pending, week 1.
- **Private consumption and the dependency-confusion probe:** not applicable. The packages are public and I assumed no internal packages.

## 9. Open questions

1. Does Security grant the narrow hosted-runner exception (Plan A)?
2. Do self-hosted macOS and Windows runners exist? Without them, the Linux-only alternative drops two of the three wheel platforms.
3. Does your GitHub plan support environment reviewers on private repos?
4. Are the two packages in one repo or two?

Answer 1 first. It decides everything else.