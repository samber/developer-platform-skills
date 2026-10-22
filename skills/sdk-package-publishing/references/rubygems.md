# RubyGems

## Contents

- Library vs binary: plain gems, executables, native extensions
- CI auto-publishing
- Public publishing: MFA and keys, namespace, removal
- Private publishing and consumption
- Dated changes

## Library vs binary

- **Library:** one source gem (platform `ruby`).
- **CLI tool:** the same gem with `spec.bindir = "exe"` and `spec.executables`. List only Ruby scripts there: RubyGems wraps each in a Ruby binstub, so a raw binary fails at run time.
- **Native CLI through RubyGems:** put the prebuilt binary in per-platform gems and have a Ruby wrapper in `exe/` `exec` it. Otherwise ship it as release assets (release-workflow.md).
- **Native extension:** publish the source gem plus precompiled platform gems built with rake-compiler-dock (`x86_64-linux-gnu`, `aarch64-linux-gnu`, `x86_64-linux-musl`, `arm64-darwin`, `x86_64-darwin`, `x64-mingw-ucrt`; `java` only for JRuby-compatible gems, never a C extension). Build them with `rake-compiler-dock bash -c "bundle && rake cross native gem"` per platform. Rust extensions use `rb_sys` and the oxidize-rb `cross-gem` action.
  - Push every gem of a version from one job. A missing platform gem silently makes those users compile from source, which fails without a toolchain.
  - Set `required_ruby_version` to the ABIs the precompiled gems actually cover.

## CI auto-publishing

- **Trigger:** a protected tag push (`v*`). Pipeline shape: release-workflow.md.
- **Trusted publishing** works from GitHub Actions only.
  1. Existing gem: gem page > Trusted publishers > create, with repository owner, repository, workflow file name and environment `release`.
  2. New gem: create a pending trusted publisher under the profile's OIDC settings; the first successful push creates the gem and makes you its owner.
  3. Publish job: `permissions: id-token: write`, `environment: release`.
- **Two publish shapes:**
  - `rubygems/release-gem@<sha>` runs `rake release`: it builds, pushes the tag (needs `contents: write`) and uploads experimental Sigstore attestations by default. Simple, but it builds inside the privileged job.
  - Hardened: `gem build` in the unprivileged build job, then `rubygems/configure-rubygems-credentials@<sha>` and `gem push pkg/*.gem` in the publish job. No `contents: write` and no project code with the credential. For attestations on stable RubyGems 4.0, sign with sigstore-ruby and pass `--attestation <file>`. RubyGems 4.1 (beta) attests automatically, but pushes unattested when sigstore-cli fails. Either way, check the gem page for the attestation after release.
- Choose release-gem for small gems; choose the hardened shape for SDKs with many dependents.
- **Fallback (other CI):** an API key with only the push scope, limited to the one gem, with an expiry, stored as `GEM_HOST_API_KEY`.

## Public publishing

**MFA and keys**

- Set human accounts to MFA level "UI and API".
- Add `spec.metadata["rubygems_mfa_required"] = "true"`: every later version then needs MFA to push. API keys on such gems need an OTP per push, so unattended CI needs trusted publishing.
- Owners of gems above the popularity threshold must use MFA.

**Namespace**

- Names are flat and first-come; there is no prefix reservation. Organizations are in private beta, not generally available: keep at least two owners per gem.
- Convention: underscores separate words, dashes mark extensions of another gem (`corp_sdk-rails`).

**Removal**

- `gem yank corp_sdk -v 1.4.3` deletes the file from the CDN, and the version number can never be published again.
- Yank breaks consumers whose `Gemfile.lock` pins that version: fresh installs fail. Reserve it for malware, leaked secrets or a release nobody can have installed yet. For an ordinary bad release, publish the fix and announce it.
- Rotate any secret that shipped in a gem: mirrors and webhooks have already copied it.

## Private publishing and consumption

- Hosts: GitHub Packages (classic personal token only), GitLab, Artifactory, Nexus, Gemfury, or a self-hosted gem server.
- Set `spec.metadata["allowed_push_host"] = "https://gems.internal.example.com"` in every private gem, so `gem push` refuses rubygems.org.
- Scope internal gems to their source with a block. Multiple global `source` lines let any source serve any name:

```ruby
# ✓ Good - corp gems resolve only from the internal source
source "https://rubygems.org"
source "https://gems.internal.example.com" do
  gem "corp_sdk"
  gem "corp_auth"   # transitive dependency of corp_sdk
end

# ✗ Bad - two global sources, either may serve corp_sdk
source "https://rubygems.org"
source "https://gems.internal.example.com"
```

- Credentials: `BUNDLE_GEMS__INTERNAL__EXAMPLE__COM="ci:${GEM_READ_TOKEN}"` in the CI environment (dots become `__`), never inside the Gemfile URL.
- Bundler 4.0.13+ supports a `cooldown` per source to delay brand-new public versions.

## Dated changes

- 2015-04: yank deletes the gem file; version numbers are never reusable.
- 2022-08-15: MFA mandatory for owners of gems above 180 million downloads.
- 2023-12: trusted publishing (GitHub Actions).
- 2026-02-16: organizations private beta.
- 2026-06-03: Bundler `cooldown` (4.0.13).
