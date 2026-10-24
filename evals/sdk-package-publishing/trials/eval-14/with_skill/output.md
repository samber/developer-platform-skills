# Cindervale: publishing plan for `cindervale-sdk` and `cindervale-cli`

Your plan has three problems:
- **The first release cannot be tokenless.** crates.io only lets you add a trusted publisher to a crate that already exists.
- **Empty placeholder crates are banned on crates.io.** An empty `cindervale-auth` would also break the SDK that depends on it.
- **`cindervale-auth` has to be public.** A public crate cannot depend on a crate from Artifactory.

Everything else below follows from those three points. Nothing here has been published, yanked or changed. Every registry-changing command is for you to run (marked **bold**).

## 0. Assumptions and decisions

I could not ask questions, so these are my assumptions. Correct any that are wrong.

- Everything is on GitHub Actions with hosted runners. The org is `cindervale`, and the monorepo holds `cindervale-auth`, `cindervale-sdk` and `cindervale-cli`.
- Versions move in lockstep through `[workspace.package] version`, with tags like `v0.1.0`.
- I have not seen your tag workflow, so section 4 is a reference draft. Diff it against yours.
- Rust is on Cargo 1.90 or newer.
- The packages are open source, and at least two people can be crates.io owners.

**Decision A, which blocks the first release: what is `cindervale-auth`?**
- Today it exists only on Artifactory. The public SDK needs it on crates.io, because crates.io rejects dependencies on other registries.
- Option 1 (recommended): publish it as a real crate containing the auth code the SDK needs. Make it the single source of truth, and have internal code consume the public version.
- Option 2: fold the auth code into `cindervale-sdk` as a module, so there is no separate crate.
- Whatever you pick, do not keep two unrelated crates named `cindervale-auth`, one public and one internal. Version numbers will collide and the Artifactory virtual repo will merge them.

**Decision B: does the SDK or CLI need `cindervale-telemetry`?**
- If yes, it also has to be a real public crate. Put it behind an optional Cargo feature, or define a small public trait the internal crate implements.
- If no, keep it internal, as in section 5.

## 1. Inventory

| Package | Registry | Publish path | Credential | Owners | Target model |
|---|---|---|---|---|---|
| `cindervale-auth` | crates.io | first release from a laptop, then CI | short-lived `publish-new` token for 0.1.0, then OIDC | team `github:cindervale:<team>` | trusted publishing, "Trusted Publishing only" on |
| `cindervale-sdk` | crates.io | same | same | same | same |
| `cindervale-cli` | crates.io (+ optional prebuilt binaries) | same | same | same | same |
| `cindervale-telemetry` | Artifactory local only | CI | OIDC to Artifactory | internal | `publish = ["corp"]`, never public |
| internal `cindervale-auth` | Artifactory | n/a | n/a | n/a | retire, or rename if it differs (Decision A) |

## 2. Per-registry decisions: crates.io

**Credential**
- Rung: trusted publishing bound to the `release` environment, plus hardened publish job, plus approval gate.
- A one-day token is acceptable for 0.1.0 only. If the crates.io changelog now offers pending trusted publishers, use them. My reference says it does not.

**Namespace**
- crates.io names are flat and permanent, with no prefix reservation.
- Do not publish an empty `cindervale-auth` or `cindervale-telemetry` to hold the names:
  - Name-only placeholders are banned.
  - The team does not reassign names on request.
  - An empty auth crate would break the SDK.
- Put all three crates under a team owner so access survives people leaving.

**Library vs binary**
- `cindervale-sdk` and `cindervale-auth` are libraries.
- `cindervale-cli` is a binary crate. `cargo install` compiles it on the user's machine and ignores your `Cargo.lock` unless the user passes `--locked`. Docs should say:

  ```sh
  cargo install --locked cindervale-cli
  ```

- Optional, but worth it for users without a Rust toolchain: `dist` for prebuilt binaries (shell, Homebrew, MSI installers).
  - Set `github-attestations = true`.
  - Add `[package.metadata.binstall]` so `cargo binstall cindervale-cli` fetches the prebuilt archive.
  - Review dist's generated workflow before adopting it: SHA-pin its actions and put its publish jobs behind the `release` environment.
  - Publish the crate and the binary release from the same tag.

**Versions and channel policy**
- crates.io has no dist-tags. A plain requirement like `"0.1"` never matches pre-releases.
- The SDK must not depend on a pre-release of `cindervale-auth`.
- Required metadata on each crate: `license`, `description`, `repository`, `readme`, `keywords`, `categories`. Add `rust-version`. Max crate size is 10 MB.

**Dependency shape**
- Dependencies between the three crates carry a version and a path: `cindervale-auth = { version = "0.1", path = "../auth" }`. Cargo strips the path on publish.
- Never put `registry = "corp"` on a dependency of a public crate.
- Publish order is always `cindervale-auth`, then `cindervale-sdk`, then `cindervale-cli`.

**Preflight** (run per release, in the build job)

```sh
cargo package --workspace --locked
cargo package -p cindervale-cli --list
```

## 3. First release (0.1.0), run by you

This is the only laptop publish. Do it once.

1. **Create an API token** on crates.io (account settings → API tokens):
   - scope `publish-new` only
   - crate pattern `cindervale-*`
   - expiry 1 day
2. Hold it in a credential provider (`cargo:macos-keychain`, `cargo:libsecret`, `cargo:wincred`), not plain-text `cargo login`. Never paste it into chat; if you do, revoke it.
3. Dry run:

   ```sh
   cargo publish --dry-run --locked -p cindervale-auth
   cargo package --workspace --locked
   ```

   A dry run of the dependents cannot resolve a brand-new `cindervale-auth` from the registry, so `cargo package --workspace` is the check for them.
4. **Publish in order.** Each command is public and cannot be undone:

   ```sh
   cargo publish --locked -p cindervale-auth
   cargo publish --locked -p cindervale-sdk
   cargo publish --locked -p cindervale-cli
   ```

   Cargo waits for each crate to appear in the index before returning.
5. **Add the team owner** to each crate, once the team has at least two members:

   ```sh
   cargo owner --add github:cindervale:<team> cindervale-auth
   cargo owner --add github:cindervale:<team> cindervale-sdk
   cargo owner --add github:cindervale:<team> cindervale-cli
   ```

   Remove your personal login afterwards with `cargo owner --remove <login> <crate>`. The GitHub org must allow the crates.io app to read team membership.
6. **Add the trusted publisher on each of the three crates** (crates.io crate settings → Trusted Publishing → GitHub):
   - repository `cindervale/<repo>`
   - workflow filename `release.yml`
   - environment `release`
7. **Validate with one real release.**
   - Land a real change, bump to 0.1.1 and push the tag. The `release` environment reviewers approve.
   - Confirm all three crates publish through OIDC.
   - A public rehearsal burns a version forever, so use a real version.
   - My assumption is that one `crates-io-auth-action` token covers all three crates. If a crate returns 403, recheck that crate's trusted publisher entry. Otherwise run one auth step per crate.
8. **Only after 0.1.1 succeeds, harden:**
   - Enable "Trusted Publishing only" on each crate.
   - Revoke the 0.1.0 token even if it has expired. Run `cargo logout` on the laptop that held it.
   - Delete any repository secret named like `CARGO_REGISTRY_TOKEN`.

## 4. Pipeline: `.github/workflows/release.yml` (draft, pending your approval)

Replace each `<sha>` with a full commit SHA. Resolve it with `git ls-remote https://github.com/<owner>/<action> refs/tags/<version>`, or let Dependabot pin it. I did not invent any.

```yaml
name: release
on:
  push:
    tags: ["v*"]            # tag ruleset and environment deployment rule list the same pattern
permissions: {}             # nothing by default

jobs:
  build:                    # unprivileged: no secrets, no id-token, no restored caches
    runs-on: ubuntu-latest
    permissions: { contents: read }
    steps:
      - uses: actions/checkout@<sha>  # v6
        with: { persist-credentials: false }
      - run: rustup toolchain install <pinned stable> --profile minimal && rustup default <pinned stable>
      - name: Tag must equal every crate version
        run: |
          set -euo pipefail
          tag="${GITHUB_REF_NAME#v}"
          meta="$(cargo metadata --no-deps --format-version 1 --locked)"
          for p in cindervale-auth cindervale-sdk cindervale-cli; do
            v="$(printf '%s' "$meta" | jq -r --arg p "$p" '.packages[] | select(.name==$p) | .version')"
            [ "$v" = "$tag" ] || { echo "tag $tag != $p $v"; exit 1; }
          done
      - name: No public crate may resolve an internal crate from crates.io
        run: |
          cargo metadata --format-version 1 --locked \
            | jq -e '[.packages[] | select(.name=="cindervale-telemetry")] | length == 0'
      - run: cargo test --workspace --locked
      - run: cargo package --workspace --locked   # verifies the packaged sources build

  publish:
    needs: build
    runs-on: ubuntu-latest
    environment: release    # must match the trusted-publisher environment exactly
    permissions:
      contents: read
      id-token: write       # OIDC, this job only
    steps:
      - uses: actions/checkout@<sha>  # v6
        with: { persist-credentials: false }
      - run: rustup toolchain install <pinned stable> --profile minimal && rustup default <pinned stable>
      - uses: rust-lang/crates-io-auth-action@<sha>  # v1
        id: auth
      - name: Publish in dependency order, skipping versions crates.io already holds
        env:
          CARGO_REGISTRY_TOKEN: ${{ steps.auth.outputs.token }}
        run: |
          set -euo pipefail
          version="${GITHUB_REF_NAME#v}"
          for crate in cindervale-auth cindervale-sdk cindervale-cli; do
            code="$(curl -s -o /dev/null -w '%{http_code}' -A 'cindervale-release (<contact email>)' \
              "https://crates.io/api/v1/crates/$crate/$version")"
            case "$code" in
              200) echo "$crate $version already published, skipping" ;;
              404) cargo publish --locked --no-verify -p "$crate" ;;   # build job already verified; skips build.rs with the token present
              *)   echo "unexpected status $code for $crate"; exit 1 ;;
            esac
          done
```

Review your own workflow against these rules:
- The publish job needs no secrets and holds the only `id-token: write`.
- Remove any `pull_request_target`, `workflow_run`, `workflow_dispatch` or branch trigger. crates.io rejects the first two for trusted publishing.
- Any `actions/cache` or `Swatinem/rust-cache` step on the publish path is a cache-poisoning risk. Remove it.
- The `release` environment needs a team as reviewer, or two or more people besides whoever cuts releases. Self-review must be blocked, and deployments restricted to `v*` tags.
- Add a tag ruleset on `v*` limited to release managers.
- A rerun after a partial failure completes the release, because the loop skips what is already published.
- Environment protection on private repositories needs a plan that supports it.
- Provenance: crates.io accepts no attestation upload. Attest prebuilt CLI binaries on the GitHub release if you add dist.

## 5. Private consumption (Artifactory)

**`cindervale-telemetry` and any other internal crate**

```toml
# internal crate Cargo.toml: this crate can never reach crates.io
[package]
publish = ["corp"]
```

```toml
# internal consumers
cindervale-telemetry = { version = "x.y", registry = "corp" }
```

```toml
# .cargo/config.toml, committed, no secret in it
[registries.corp]
index = "sparse+https://<host>/artifactory/api/cargo/<cargo-virtual>/index/"   # copy from Artifactory "Set Me Up"
credential-provider = "cargo:token"
```

- In CI, inject the read-only token as `CARGO_REGISTRIES_CORP_TOKEN` from the secret store. Artifactory may need the `Bearer <token>` form, so check "Set Me Up".
- Cargo never falls back from a named registry to crates.io. That is the dependency-confusion defense.
- The gap: a dependency written without `registry = "corp"` resolves from crates.io, where anyone can register `cindervale-telemetry`. The jq check in the build job above catches that case.

**Artifactory server side**
- Resolve through one virtual repository. Add an exclude pattern on the crates.io remote for each internal crate name, for example `cindervale-telemetry`.
- Do not exclude `cindervale-*` as a prefix. That would block the public `cindervale-sdk`, `cindervale-auth` and `cindervale-cli`.
- Priority Resolution is unavailable for Cargo, so exclude patterns are the only server-side control.
- Include and exclude patterns do not apply to admin users. CI and developers must never hold admin tokens.

**Mirror for internal builds** (optional)

```toml
[source.crates-io]
replace-with = "corp-mirror"
```

**Probe**
- Per release-workflow.md, the canary needs a public crate with an internal-looking name. You have none, and crates.io bans placeholders, so the canary probe does not apply here.
- The proof is therefore the exclude rules on the remote plus a lockfile check: every internal crate in `Cargo.lock` must show `source = "registry+sparse+https://<corp index>"`.
- Rerun both after any feed reconfiguration.
- Record that the canary probe was not applicable.

**Publishing internal crates**
- Create an OIDC integration in Artifactory, with an identity mapping on `environment: release` and deploy rights on the Cargo release local only. Build jobs get read-only mappings.
- Use `jfrog/setup-jfrog-cli@<sha>`, then `cargo publish --registry corp`.
- Deny Delete and Overwrite on release locals.

## 6. Rollback runbook

I will not run any of these. Removal commands have no dry run, so none is appended.

**crates.io**
1. Publish the fix as a new patch version, with a tag and approval through the same workflow.
2. **Yank the bad version.** The message and the changelog name the safe version:

   ```sh
   cargo yank --version 0.1.2 cindervale-sdk
   ```

   - Yank stops new resolutions only. Existing `Cargo.lock` files and installed binaries keep working.
   - `cargo yank --version 0.1.2 --undo cindervale-sdk` reverses it.
   - Yank dependents first or last as fits the bug. Never yank only `cindervale-auth` if released SDK versions pin it.
3. If you suspect compromise, isolate build hosts, then revoke and rotate everything the release job reached.
4. Whole-crate deletion is possible only within 72 hours, or with a single owner, under 500 downloads a month and no reverse dependencies. There is no per-version delete. After that, contact the crates.io security team.
5. Announce in the changelog and the GitHub security advisory.

**Artifactory.** Roll forward with a new version. Consumers have already cached and locked the bad one.

**Rehearsal.** Rehearse steps 1 and 2 on an Artifactory dev Cargo local repository, publishing with `cargo publish --registry corp-dev`. Never rehearse on the production crates.

## 7. Migration sequence (today 2026-10-23)

| When | Step | Evidence left |
|---|---|---|
| Before any publish | Decisions A and B; fix the SDK's dependencies; `rust-version` and metadata set | `cargo package --workspace --locked` output |
| Before any publish | GitHub: `release` environment, reviewer team, tag ruleset on `v*`, SHA-pinned workflow; crates.io team owner prepared | environment and ruleset settings screenshots |
| Day 1 | Section 3 steps 1-6: manual 0.1.0, owners, three trusted publishers | the three crate pages on crates.io |
| Day 1-3 | Section 3 step 7: release 0.1.1 through OIDC | the Actions run log: no token step, environment approval recorded |
| Right after 0.1.1 | Section 3 step 8: "Trusted Publishing only", revoke token, delete secrets | settings pages, token list empty |
| Next | Artifactory: exclude rules, OIDC publish for internal crates, lockfile check in CI | rule listing, CI log |
| Next | Rollback rehearsal on the dev local repository | rehearsal log |
| Docs | Install line `cargo install --locked cindervale-cli` | docs diff |

## Open questions

1. Decision A: is `cindervale-auth` going public as a real crate, or folded into the SDK?
2. Decision B: does anything public need `cindervale-telemetry`?
3. Is the CI GitHub-hosted, and is the monorepo layout as I assumed?
4. Do you want prebuilt CLI binaries through `dist` now, or only `cargo install`?