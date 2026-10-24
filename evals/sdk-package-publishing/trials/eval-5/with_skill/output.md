# Larkspur Data: locking down `larkspur-auth`, `larkspur-core` and `larkspur-sdk`

**Do not register the three empty packages on public PyPI.** PEP 541 treats placeholder projects as name squatting. PyPI can remove them and hand the names to anyone who asks, so this wouldn't lock anything down. It also doesn't fix the real hole, which is `--extra-index-url`. The fix is to change how installs resolve, and the config for that is below.

## 1. Assumptions and inventory

I'm assuming the following, so correct any that are wrong:
- CI is GitHub Actions on hosted runners.
- Artifactory has a PyPI **remote** repo that proxies pypi.org. Call it `pypi-remote` here.
- Artifactory has a PyPI **virtual** repo that includes `pypi-local` and `pypi-remote`. Call it `pypi`. The virtual repo doesn't exist yet if devs only use `pypi-local` today.
- The packages are internal-only, so none of them has a public release.

| Package | Registry | Publish path today | Target model |
|---|---|---|---|
| `larkspur-auth`, `larkspur-core`, `larkspur-sdk` | Artifactory `pypi-local` | Unknown (laptop or CI) | CI-only deploy to `pypi-local` with an OIDC-minted token |

**The current hole.** `pip install --extra-index-url …/pypi-local/simple larkspur-sdk` makes pip merge candidates from public PyPI and the internal index and take the highest version. Anyone can upload `larkspur-sdk 99.0` to public PyPI and every developer machine and CI job installs it. It also applies to `larkspur-auth` and `larkspur-core`, which pip resolves as transitive dependencies. Registering empty packages doesn't close this: you can't claim names you don't control for every future version, and the lookup still merges both indexes.

**Check first.** Open `https://pypi.org/simple/larkspur-auth/`, then the same for `-core` and `-sdk`. A 200 means someone already holds the name. Treat that as an incident: tell Security, and don't install those names from any machine until step 2 is live.

## 2. Artifactory server-side config (the actual lock)

An admin does this in the Artifactory UI. These are registry setting changes, so I haven't run them.

1. On `pypi-remote`, add **Excluded Patterns** that cover every internal name. The simple index normalizes names, so cover the variants:
   ```
   larkspur-*,larkspur_*,larkspur.*
   ```
   Now the remote can never serve any `larkspur-*` name from public PyPI.
2. Create or confirm the virtual repo `pypi` with these members, local first: `pypi-local`, then `pypi-remote`.
3. Test the exclude rule with Artifactory's pattern/rule test, using each variant above.
4. Don't use admin tokens for developers or CI. Include and exclude patterns don't apply to admins, so an admin sees merged results and misreads the behavior.
5. Create three scoped identities:
   - **Read-only** on the `pypi` virtual, for developers and CI.
   - **Deploy-only** on `pypi-local`, for the publish job. Leave Delete/Overwrite off so released versions can't be replaced.
   - **No** write access for anyone else.

## 3. Client config to hand the team

### uv (target state)

Put this in each consuming project's `pyproject.toml`. There is no secret in it:

```toml
[tool.uv]
exclude-newer = "7 days"          # cooldown on brand-new public releases

[[tool.uv.index]]
name = "internal"
url = "https://artifactory.larkspur.internal/artifactory/api/pypi/pypi/simple"
default = true                     # ALL installs go through the blocking endpoint; public PyPI is not contacted directly

[tool.uv.sources]
larkspur-sdk  = { index = "internal" }
larkspur-auth = { index = "internal" }   # transitive dependency of larkspur-sdk
larkspur-core = { index = "internal" }   # transitive dependency of larkspur-sdk
```

- `default = true` sends public dependencies through Artifactory as well. Nothing bypasses the `larkspur-*` exclude rule.
- The `sources` pins are defense in depth. Pin all three names, including the transitive ones, in every project that depends on any of them.
- The pins live in the consumer's `pyproject.toml`. They aren't published inside `larkspur-sdk`, so each consumer needs them.
- **Credentials** come from the environment: `UV_INDEX_INTERNAL_USERNAME` and `UV_INDEX_INTERNAL_PASSWORD`, or the keyring. Never put them in the URL or commit them.
- Never set `index-strategy = unsafe-best-match` or `unsafe-first-match` to get past a resolution error. That recreates the original hole.
- Commit `uv.lock`. It records hashes, so a swapped artifact fails install. After every `uv lock`, check that each `larkspur-*` entry has `source = { registry = "https://artifactory.larkspur.internal/…" }`.

```sh
uv add larkspur-sdk
uv lock --check
# every larkspur-* package in uv.lock must name the internal registry:
/usr/bin/grep -A3 -E '^name = "larkspur-' uv.lock | /usr/bin/grep -E 'name =|source ='
```

### pip (until uv rollout finishes)

Remove every `--extra-index-url`. Use one index, the virtual repo:

```ini
# ~/.config/pip/pip.conf  (no credentials in this file)
[global]
index-url = https://artifactory.larkspur.internal/artifactory/api/pypi/pypi/simple
```

Put credentials in `~/.netrc` (`chmod 600`) with the read-only identity. Don't embed them in `PIP_INDEX_URL`, because tools echo that URL into logs.

pip has no per-package mapping, so for pip users the server-side exclude rule in section 2 is the only protection. That's why it comes first.

### CI

- Inject the read-only credential as environment variables from the secret store. The repo only ever holds the config above.
- Install from the lockfile with `uv sync --frozen`. For pip, use `pip install --require-hashes -r requirements.txt` with a hash-pinned file.

## 4. Publishing the three packages (CI-only, draft pending your approval)

Artifactory's OIDC integration lets GitHub mint a short-lived deploy token. Nothing long-lived is stored.

Setup in Artifactory:
- Create an OIDC integration for GitHub.
- Add an identity mapping for repo `larkspur/<repo>` on the `v*` tags, with `environment: release`.
- That mapping gets deploy-only rights on `pypi-local`.

In GitHub:
- Create a protected environment `release`.
- Reviewers are a team, or two people besides whoever cuts releases.
- Self-review is blocked.
- Deployments are restricted to `v*` tags, with a matching tag ruleset.

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
    steps:
      - uses: actions/checkout@<sha>  # v6
        with: { persist-credentials: false }
      - uses: astral-sh/setup-uv@<sha>
        with: { enable-cache: false }
      - run: |
          ver="$(uv version --short)"
          [ "${GITHUB_REF_NAME#v}" = "$ver" ] || { echo "tag != version"; exit 1; }
      - run: uv build && uvx twine check --strict dist/*
      - run: tar tzf dist/*.tar.gz     # review: no tests, fixtures or .env in the sdist
      - uses: actions/upload-artifact@<sha>  # v5
        with: { name: dist, path: dist/ }

  publish:
    needs: build
    runs-on: ubuntu-latest
    environment: release
    permissions: { contents: read, id-token: write }
    steps:
      - uses: actions/download-artifact@<sha>  # v5
        with: { name: dist, path: dist/ }
      - uses: jfrog/setup-jfrog-cli@<sha>
        id: jfrog
        env: { JF_URL: "https://artifactory.larkspur.internal" }
        with: { oidc-provider-name: "<provider name from the Artifactory integration>" }
      - run: uv publish --publish-url "https://artifactory.larkspur.internal/artifactory/api/pypi/pypi-local" dist/*
        env:
          UV_PUBLISH_USERNAME: ${{ steps.jfrog.outputs.oidc-user }}
          UV_PUBLISH_PASSWORD: ${{ steps.jfrog.outputs.oidc-token }}
```

- Pin the action SHAs with `git ls-remote https://github.com/<owner>/<action> refs/tags/<version>`, or let Renovate do it. Don't invent SHAs.
- Publish in dependency order: `larkspur-auth` and `larkspur-core` first, then `larkspur-sdk`. Make reruns idempotent by skipping any version Artifactory already holds.
- Keep this publish identity separate from the read-only consumer identity.

## 5. Rollback

- **Bad version:** roll forward by publishing a fixed version immediately. Artifactory could delete or overwrite, but consumers have already cached and locked the bad one. Because CI lacks Delete/Overwrite, a released version can't be replaced silently.
- **Pull a bad version from resolution:** a Larkspur admin (not CI) removes or blocks it in `pypi-local`. They then re-run the probe in section 6, because deleting an internal package while a public name could be forwarded reopens the hole.
- **Suspected compromise:** isolate build hosts, then revoke the OIDC mapping and any read or deploy tokens the release job could reach. Rotate them.
- **Rehearse** on a scratch `pypi-dev-local` repo with a throwaway `larkspur-rehearsal` name. Don't rehearse on production packages.

## 6. Proof that it works

1. **Rule check.** In the Artifactory exclude-pattern test, `larkspur-auth`, `larkspur_auth` and `larkspur.auth` must all match.
2. **Probe, metadata only.** Never download or install the probe target. Use the read-only credential and assert exact statuses:
   ```sh
   # credentials from a netrc file, never argv
   code() { curl -s -o /dev/null -w '%{http_code}' --netrc-file "$FEED_NETRC" "$1"; }
   IDX=https://artifactory.larkspur.internal/artifactory/api/pypi/pypi/simple
   [ "$(code "$IDX/larkspur-sdk/")" = 200 ] || { echo "probe cannot see the feed"; exit 1; }
   [ "$(code "$IDX/<existing public package named larkspur-*>/")" = 404 ] || { echo "FAILED or inconclusive"; exit 1; }
   ```
   - The first assertion is the positive control: it shows the probe can see the feed.
   - The second needs a public `larkspur-*` package that already exists. Don't create one, because PyPI bans placeholders.
   - A 401, 403, 5xx or DNS error is inconclusive, not a pass.
   - Confirm the probe identity is non-admin. Exclude rules don't apply to admins.
3. **If no public `larkspur-*` name exists to probe with,** the rule test (1) and the lockfile check (4) are the proof. Record that the probe didn't apply.
4. **Client check.** `uv.lock` shows the internal registry for all three packages.
5. **Repeat the probe** after any change to the feed configuration.

## 7. Migration sequence

| When | Step | Evidence |
|---|---|---|
| Day 0 (2026-10-23) | Check whether public PyPI already has any of the three names | Status codes from the three URLs |
| Day 0-1 | Create the exclude rules and the virtual repo, then run the rule test and the probe | Rule-test screenshot, probe output |
| Day 1-2 | Publish the `pip.conf` change, so no `--extra-index-url` is left. Search repos, CI files, Dockerfiles and docs. | `/usr/bin/grep -rE 'extra-index-url' .` returns nothing |
| Week 1-2 | Add the uv config to each project, run `uv lock`, check sources, commit `uv.lock` | Lockfile source check per repo |
| Week 2-3 | Move publishing to the OIDC pipeline, then delete laptop deploy credentials and any legacy API keys | Last deploy came from CI; keys revoked |
| Quarterly | Re-run the probe and the lockfile check | Dated probe output |

## What to tell Security

- No placeholder packages on public PyPI.
- The block is server-side: the PyPI remote can't serve any `larkspur-*` name, and every client uses one Artifactory endpoint.
- Clients pin the three names and commit hash-locked lockfiles.
- Publishing is CI-only, with short-lived OIDC tokens, and CI can't overwrite released versions.