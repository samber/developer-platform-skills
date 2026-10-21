# Hex (Elixir and Erlang)

## Contents

- Library vs binary
- CI auto-publishing
- Public publishing: names and owners, removal
- Private publishing and consumption
- Dated changes

## Library vs binary

- **Library:** a source package on hex.pm; `mix hex.publish` uploads the package and its docs to hexdocs.pm.
- **Native code (NIFs):** keep the package source-only and download precompiled binaries at compile time with `rustler_precompiled` or an `elixir_make` precompiler. Host the artifacts on the GitHub release, generate the checksum file (`mix rustler_precompiled.download <Module> --all --print`) before publishing, and list it in the package `files`, or the package fails to compile for every user.
- **Developer CLI:** an escript, installable with `mix escript.install hex <package>`. It needs Erlang/OTP on the user's machine.
- **Standalone app:** a Mix release (or Burrito for a single binary) shipped as release assets or a container image, never through Hex.

## CI auto-publishing

- **Trigger:** a protected tag push. Publish with `mix hex.publish --yes` in the publish job, behind the `release` environment. Pipeline shape: release-workflow.md.
- **Credential:** `HEX_API_KEY` from the secret store.
  - For organization-owned packages, generate an organization key: `mix hex.organization key corp generate --key-name ci-publish --permission api:write`.
  - Otherwise use a dedicated user key with the narrowest permission, owned by a bot account with 2FA.
  - Pass the key through the environment only. Hex 2.6 stops accepting user-owned keys stored with `mix hex.organization auth`; organization-owned keys are unaffected.
- **Trusted publishing** (workload identity for GitHub Actions) is in Hex 2.6 development and not yet released. When it ships, configure it on the package, give the publish job `id-token: write`, and revoke the key.
- **Provenance:** Hex accepts no attestation upload. Hex signs its registry, and `mix.lock` pins package checksums.

## Public publishing

**Names and owners**

- Prefix extension packages with the base name (`corp_sdk_phoenix`) and never claim another package's module namespace.
- Keep at least two owners with level `full`; give CI-adjacent humans `maintainer`, which cannot manage owners.

**Removal**

- `mix hex.publish --revert 1.4.3` removes a version within 1 hour of publishing it, or within 24 hours of a brand-new package's first release. It has no safe dry run: every released Hex ignores `--dry-run` on `--revert` and deletes the release (the rejection exists only in unreleased Hex 2.6). Never append `--dry-run` to it; hand the command to the user.
- After that window the repository is immutable. Retire instead: `mix hex.retire corp_sdk 1.4.3 security --message "Use 1.4.4"` (reasons `renamed`, `deprecated`, `security`, `invalid`, `other`). Retired versions still resolve, with a warning.

## Private publishing and consumption

- **Hex organizations** (paid) host private packages: publish with `organization: "corp"` in the package config, depend with `{:corp_auth, "~> 1.4", organization: "corp"}`. Fetch with an organization key holding the `repository:corp` permission.
- **Self-hosted repository:** build it with `mix hex.registry build public --name=corp --private-key=private_key.pem`, serve it over HTTPS, add it with `mix hex.repo add corp https://hex.internal.example.com --public-key=public_key.pem --auth-key "$HEX_READ_KEY"`, and depend with `repo: "corp"`.
- A dependency without `organization:` or `repo:` resolves from public hex.pm. Name the repository on every internal dependency, transitive ones included.
- Never set `HEX_UNSAFE_REGISTRY`: it disables registry signature checks.

## Dated changes

- Hex 2.6 (in development; check the Hex changelog for its release): workload identity (trusted publishing) for GitHub Actions; `--revert` with `--dry-run` rejected; stored user-owned organization keys stop working.
