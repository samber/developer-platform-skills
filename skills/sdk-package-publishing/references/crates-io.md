# crates.io

## Contents

- Library vs binary: library crates, `cargo install`, dist for prebuilt binaries
- CI auto-publishing
- Public publishing: namespace, versions, removal
- Private publishing
- Private consumption
- Dated changes

## Library vs binary

- **Library crate:** published to crates.io; consumers compile it.
- **Binary crate on crates.io:** `cargo install corp-cli` builds from source on the user's machine; tell users to pass `--locked`, or Cargo ignores your `Cargo.lock`.
- **Prebuilt binaries:** dist (formerly cargo-dist). `dist init` generates a release workflow (plan, build per target, host on the GitHub release, announce) and installers: shell, PowerShell, Homebrew, npm, MSI. Set `github-attestations = true` (off by default, labelled experimental) to attest the archives.
  - Review the generated workflow against release-workflow.md before adopting it: SHA-pin its actions and put its publish jobs behind the `release` environment.
  - Add `[package.metadata.binstall]` (or keep dist's default asset names) so `cargo binstall corp-cli` fetches the prebuilt archive instead of compiling.
- Publish the crate and the binary release from the same tag.

## CI auto-publishing

- **Trigger:** a protected tag push. Pipeline shape: release-workflow.md.
- Trusted publishing from GitHub Actions and GitLab.com (not self-managed). Use `rust-lang/crates-io-auth-action@<sha>  # v1` with `permissions: id-token: write`, then pass `steps.auth.outputs.token` as `CARGO_REGISTRY_TOKEN` to `cargo publish`. The token is revoked at job end.
- The first release of a crate must be published manually with an API token; add the trusted publisher afterwards.
- Then enable the crate's "Trusted Publishing only" setting so tokens can no longer publish it.
- `pull_request_target` and `workflow_run` triggers are rejected for trusted publishing.
- API tokens (first release, fallback): scope to `publish-new`/`publish-update` and a crate-name pattern; default expiry 90 days. `cargo login` stores tokens in plain text: prefer a credential provider (`cargo:macos-keychain`, `cargo:wincred`, `cargo:libsecret`) on laptops.
- Provenance: crates.io accepts no attestation upload. Attest prebuilt binaries on the GitHub release.

## Public publishing

**Namespace**

- Flat, first-come, permanent names; no prefix reservation. Name-only placeholder crates are banned, and the team never reassigns a name on request alone.
- Publish under a team owner (`cargo owner --add github:corp:sdk-maintainers`) so access survives people leaving.

**Versions**

- A plain requirement (`corp-sdk = "1.4"`) never matches pre-releases; consumers must name `1.5.0-beta.1` explicitly. Libraries should not depend on pre-releases.
- Required metadata: `license` (or `license-file`) and `description`; set `repository`, `readme`, `keywords`, `categories`. Max crate size 10 MB.
- Preflight: `cargo publish --dry-run`, then `cargo package --list` to check contents.

**Removal**

- `cargo yank --version 1.4.3` stops new resolutions; existing `Cargo.lock` files keep working; `--undo` reverses it.
- Whole-crate deletion only within 72 hours, or with a single owner, under 500 downloads per month and no reverse dependencies. No per-version delete.

## Private publishing

- Alternate registries: AWS CodeArtifact, Azure Artifacts, Artifactory, Nexus, or a self-hosted sparse index. GitHub Packages and GitLab have no Cargo registry.
- Restrict where a crate may go, so a private crate can never reach crates.io:

```toml
[package]
publish = ["corp"]
```

- Crates on crates.io cannot depend on crates from other registries: a public SDK cannot pull an internal crate.

## Private consumption

```toml
# .cargo/config.toml committed to the repo
[registries.corp]
index = "sparse+https://cargo.internal.example.com/index/"
credential-provider = "cargo:token"
```

- In CI, supply the token as `CARGO_REGISTRIES_CORP_TOKEN` from the secret store.
- Each internal dependency names its registry (`corp-sdk = { version = "1.4", registry = "corp" }`). Cargo never falls back from a named registry to crates.io, so this is the dependency-confusion defense.
- Mirroring crates.io through the internal feed uses `[source.crates-io] replace-with = "corp-mirror"`.

## Dated changes

- 2024-09: new API tokens expire after 90 days by default.
- 2025-02: crate deletion under the 72-hour or low-usage rule.
- 2025-07-11: trusted publishing for GitHub Actions.
- 2026-01: GitLab.com trusted publishing; "Trusted Publishing only" mode.
