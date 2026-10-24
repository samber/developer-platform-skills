# Locking down `larkspur-*` installs (pip → uv)

## Your plan

Registering the three names on public PyPI is worth doing, but it is a backstop, not the fix.

- **The bug:** `pip --extra-index-url` merges both indexes and takes the highest version, wherever it lives. Any client that can see PyPI is exposed to dependency confusion.
- **What the placeholders do:** they stop a stranger publishing `larkspur-core 99.0` on PyPI. That helps clients you don't control, such as old pip, CI images and contractors' laptops.
- **What they don't do:** they leave the install path unchanged, so don't rely on them alone.

The fix is to make PyPI unreachable for these names. Do steps 1 to 3, and keep the placeholders as step 4.

## 1. Artifactory (one-time, whoever owns it)

1. Create a remote repo `pypi-remote` pointing to `https://pypi.org`.
2. In `pypi-remote`, set **Excluded Patterns** to `larkspur*` so it never serves or caches those names. Add the underscore spelling too if your version needs it.
3. Create a virtual repo `pypi` that aggregates `pypi-local` and `pypi-remote`.
4. Devs and CI use only the virtual repo, with a single index URL:
   `https://artifactory.larkspur.internal/artifactory/api/pypi/pypi/simple`
5. Run a check that can fail. I haven't tested this against your instance.
   - **Positive control:** `curl -s -o /dev/null -w '%{http_code}\n' <virtual>/larkspur-sdk/` should return `200`.
   - **Exclusion check:** once the placeholders exist on PyPI, the file list for `larkspur-core` through the virtual repo must contain only your internal artifacts.
   - **Don't trust "command errored":** only an exact status, or a file list you inspected, counts as a pass.

## 2. uv config

### Option A: virtual repo exists (recommended)

Put this in each project's `pyproject.toml`:

```toml
[[tool.uv.index]]
name = "larkspur"
url = "https://artifactory.larkspur.internal/artifactory/api/pypi/pypi/simple"
default = true   # replaces PyPI; Artifactory proxies it
```

For every dev machine, put this in `~/.config/uv/uv.toml`, which has no `tool.uv` prefix:

```toml
[[index]]
name = "larkspur"
url = "https://artifactory.larkspur.internal/artifactory/api/pypi/pypi/simple"
default = true
```

### Option B: no virtual repo yet (interim)

Pin each internal package to the local repo and mark the index `explicit`. An explicit index is consulted only for packages pinned to it.

```toml
[project]
dependencies = [
  "larkspur-sdk",
  "larkspur-auth",   # list the transitive internals too, see below
  "larkspur-core",
]

[[tool.uv.index]]
name = "larkspur"
url = "https://artifactory.larkspur.internal/artifactory/api/pypi/pypi-local/simple"
explicit = true

[tool.uv.sources]
larkspur-sdk  = { index = "larkspur" }
larkspur-auth = { index = "larkspur" }
larkspur-core = { index = "larkspur" }
```

`larkspur-sdk` depends on the other two. As far as I know, uv applies `tool.uv.sources` only to packages your own project declares. Without the extra entries, `larkspur-auth` and `larkspur-core` could be resolved from PyPI. Run `uv lock` and check the `source` lines in `uv.lock` to confirm.

### Rules for both options

- **Never** set `--index-strategy unsafe-best-match` or `UV_INDEX_STRATEGY=unsafe-best-match`. It restores pip's highest-version-wins behavior. The default, `first-index`, is the safe one.
- **Commit `uv.lock`.** It records the source and hashes of every package.
- **In CI use `uv sync --locked`** (or `--frozen`).

## 3. Credentials

Don't put credentials in files. For an index named `larkspur`, uv reads these environment variables:

```bash
export UV_INDEX_LARKSPUR_USERNAME="<user>"
export UV_INDEX_LARKSPUR_PASSWORD="<token>"   # Artifactory identity token; CI secret store
```

The other options are `~/.netrc` or a keyring.

## 4. Placeholders on PyPI (defense in depth)

1. **Check that the names are free first.** If any is already taken by someone else, treat it as a live incident and tell security.
2. Publish from an org-owned PyPI account with 2FA, using a trusted publisher or a scoped token.
3. Use a version far below your real ones, for example `0.0.0.dev0`. The README should say it is a reserved name for Larkspur internal use and carry no code.
4. Names normalize (`larkspur_auth` is the same as `larkspur-auth`), so one registration each is enough.
5. Publishing makes the three internal names public. That is usually fine, but tell security.

## 5. Legacy pip (until the uv migration is done)

Replace the flag in `pip.conf` or `PIP_INDEX_URL`:

```ini
[global]
index-url = https://artifactory.larkspur.internal/artifactory/api/pypi/pypi/simple
```

Ban `--extra-index-url` in docs, Dockerfiles and CI. Grep the repos for it.

## 6. Publishing (optional)

```bash
uv publish \
  --publish-url https://artifactory.larkspur.internal/artifactory/api/pypi/pypi-local \
  --username "$ARTIFACTORY_USER" --password "$ARTIFACTORY_TOKEN"
```

Publish to the local repo, never to the virtual one.

## Rollout order

1. Artifactory steps 1 to 5.
2. Placeholders on PyPI.
3. Team config: Option A, or Option B if there is no virtual repo yet.
4. Grep the repos for `extra-index-url` and remove every hit.