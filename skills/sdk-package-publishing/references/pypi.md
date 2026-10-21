# PyPI

## Contents

- Library vs binary: pure and platform wheels, CLI entry points
- CI auto-publishing: trusted publishers, attestations, token fallback
- Public publishing: namespace, package shape, versions, removal
- Private publishing
- Private consumption
- Dated changes

## Library vs binary

- **Pure-Python library:** one sdist and one `py3-none-any` wheel.
- **Compiled extension:** platform wheels (`manylinux_x_y`, `musllinux_x_y`, macOS, Windows) built with `pypa/cibuildwheel@<sha>  # v4` on a runner matrix. Each matrix job uploads its wheels as an artifact; the publish job downloads them all and uploads once. Build `abi3` wheels where the extension allows it: one wheel then covers every CPython version and shrinks the matrix.
- **Rust extension:** maturin; `maturin generate-ci github` writes the matrix workflow, and `[tool.maturin.generate-ci.github] trusted-publishing = true` makes it publish with OIDC.
- **CLI tool:** declare `[project.scripts]` entry points; users run `uv tool install corp-cli` or `uvx corp-cli`. The CLI ships as a normal wheel.
- **Frozen standalone executable** (PyInstaller and similar): release assets, never PyPI.

## CI auto-publishing

- **Trigger:** a protected tag push. Pipeline shape: release-workflow.md.

**Trusted publishers**

- Trusted publishers: GitHub Actions, GitLab CI/CD (GitLab.com; self-managed in beta), Google Cloud, ActiveState. No CircleCI. Minted upload tokens live 15 minutes.
- Publish with `pypa/gh-action-pypi-publish` pinned to a full commit SHA (`release/v1` is a mutable branch) or `uv publish`. Build in a separate job and pass the dists as an artifact; give `id-token: write` only to the upload job.
- Reusable workflows are not supported for trusted publishing: keep the upload job in the top-level workflow file the publisher names.
- Bind the publisher to a CI environment that only protected tags may deploy to, with required reviewers. Without it, any job of the named workflow, on any branch or trigger, can mint an upload token.
- Self-hosted or unsupported CI: a PyPI organization can register a custom OIDC issuer before falling back to tokens.
- GitLab: any job in the top-level pipeline can mint a token, so keep publish in its own protected pipeline.
- A pending publisher configures trusted publishing before the project exists, but does not reserve the name: someone else can register it first. Publish the first release promptly after creating it.
- 2FA is mandatory for every account. After migrating, delete every project and account API token: a forgotten token was the second compromise route in the Ultralytics incident.
- Token fallback (only where no trusted publisher fits): project-scoped token, username `__token__`, value from the CI secret store as `${PYPI_API_TOKEN}`.

**Attestations**

- PEP 740 attestations upload automatically under trusted publishing with the official action. PyPI accepts them only from trusted-publisher identities. Leave them on.

## Public publishing

**Namespace**

- Register the project under a PyPI organization so ownership survives staff changes. Corporate organizations pay a monthly fee.
- PEP 541 governs disputes: an abandoned project can transfer after failed contact attempts; pure name squatting is invalid. Requests go through PyPI support, not the owner.

**Package shape**

- Build the sdist and wheels in unprivileged jobs (`python -m build`, or the cibuildwheel matrix), then run `twine check --strict dist/*` on the merged set before the publish job.
- List the sdist contents (`tar tzf dist/*.tar.gz`) before release: sdists sweep in tests, fixtures and stray `.env` files unless the build backend excludes them.
- Set `requires-python` and project URLs; the README must render (`twine check` validates it).

**Versions and pre-releases**

- PEP 440: `1.4.0a1`, `1.4.0b1`, `1.4.0rc1`, `1.4.0.dev1`. pip and uv ignore pre-releases unless asked (`--pre`) or pinned.
- Local versions (`1.0+abc`) are rejected by PyPI.
- Upload every wheel within 14 days of the release: PyPI rejects new files on older releases. Late wheels for a new Python version need a new version.

**Removal**

- Yank (PEP 592) is the rollback primitive: installers skip a yanked release unless pinned with `==` or a lock file. An owner yanks from the release's options in the PyPI project management page, with a reason shown to users. Reversible.
- Delete is permanent and the filename can never be reused, even for a fixed build. Use it only for leaked secrets or malware.

## Private publishing

- Feeds with Python support: GitLab Package Registry, AWS CodeArtifact, Azure Artifacts, Google Artifact Registry, Artifactory, Nexus, or a self-hosted index. GitHub Packages has no Python registry.
- Upload with `twine upload --repository-url <feed-url>` or `uv publish --publish-url <feed-url>`, credentials from environment variables, never a committed `.pypirc` holding a secret.
- Do not publish empty placeholder projects on public PyPI to hold internal names: PEP 541 treats them as squatting. Prefix internal names (`corp-`) and enforce the consumption rules below.

## Private consumption

The dependency-confusion trap: `--extra-index-url` makes pip compare versions across all indexes with no priority, so a public package with the same name and a higher version wins.

```
# ✓ Good - one index that proxies PyPI and serves private packages
pip install --index-url https://pypi.internal.example.com/simple/ corp-sdk

# ✗ Bad - public PyPI can outbid the private name
pip install --extra-index-url https://pypi.internal.example.com/simple/ corp-sdk
```

- uv default `index-strategy = "first-index"` takes candidates only from the first index that has the name. With `explicit = true`, uv uses the private index only for packages pinned to it, so pin every internal name, transitive ones included, or an unpinned internal dependency resolves from PyPI:

```toml
[[tool.uv.index]]
name = "internal"
url = "https://pypi.internal.example.com/simple/"
explicit = true

[tool.uv.sources]
corp-sdk = { index = "internal" }
corp-auth = { index = "internal" }   # transitive dependency of corp-sdk
```

- Verify after `uv lock`: every `corp-*` entry's source in `uv.lock` is the internal index.
- Never switch uv to `unsafe-best-match` or `unsafe-first-match` to fix a resolution error.
- Credentials: `UV_INDEX_INTERNAL_USERNAME` / `UV_INDEX_INTERNAL_PASSWORD` or keyring. Avoid credentials embedded in `PIP_INDEX_URL`: tools echo that URL into logs. Never paste credentials into `pip.conf` in the repo.
- A local-only feed repository cannot serve public dependencies, which is what pushes teams to `--extra-index-url`. Point clients at the feed's merged (virtual) repository instead, and block internal names on its public remote.
- Lock with hashes (`uv lock`, `pip-compile --generate-hashes`) so a swapped artifact fails install.

## Dated changes

- 2024-01-01: 2FA mandatory for all users.
- 2024-11-14: PEP 740 attestations supported.
- 2025-11: organization-owned pending publishers; GitLab self-managed trusted publishing beta.
- 2026-07-08: new files rejected on releases older than 14 days.
