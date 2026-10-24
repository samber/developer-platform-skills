# Cindervale: crates.io release plan

Two parts of the plan won't work as described. The OIDC-only first release fails, and the placeholder crates would break the SDK for users.

## 1. ❌ The first release cannot use OIDC with zero tokens

- crates.io Trusted Publishing is configured per existing crate. You add the trusted publisher (repo, workflow file, optional environment) in that crate's settings, so the crate must already exist.
- On a brand-new name, `crates-io-auth-action` can't get a token that is allowed to create the crate. The first publish of `cindervale-sdk` and `cindervale-cli` needs a normal API token.
- I'm going from my knowledge of the crates.io docs here. I haven't re-checked them today, so confirm against the current Trusted Publishing page before relying on it.

**Fix: one short-lived token, then OIDC for everything after.**

1. Create a crates.io token scoped to `publish-new` only, crate pattern `cindervale-*`, expiring within 24 h.
2. Publish the first versions from a clean checkout of the tag (the real `0.1.0`s, not placeholders). Use the order in section 3.
3. On each crate's Settings → Trusted Publishing page, add the GitHub repo, the tag workflow filename, and the environment if you use one.
4. Enable the "trusted publishing only" option on each crate if it's offered, so tokens can no longer publish.
5. Revoke the bootstrap token.
6. Make sure the tag workflow has `permissions: id-token: write`. From the second release on, it runs token-free.

## 2. ❌ Empty `cindervale-auth` / `cindervale-telemetry` placeholders

**Problem A: the SDK breaks for users.**
- crates.io rejects published crates whose dependencies point at another registry (Artifactory) or at a bare `path`.
- Every dependency of `cindervale-sdk` must therefore resolve on crates.io. If the SDK depends on `cindervale-auth`, users get whatever is on crates.io under that name, which would be an empty crate. The SDK won't compile, or it will compile and do nothing.
- Cargo requires that a published dependency exist on crates.io at the version named in the manifest.

**Problem B: dependency confusion on your internal builds.**
- Internal crates with the same names as public ones can be resolved from the wrong source. This happens if Artifactory's virtual Cargo repo proxies crates.io, or if a manifest omits `registry = "..."`.
- If a public version number ends up higher than the internal one, internal builds can silently pull the empty crate.

**Problem C: policy.**
- crates.io's usage policy treats name reservation with empty crates as squatting, and the team may remove such crates. You'd be spending effort on a hold that can be revoked.

**Decide per crate:**

| Crate | Used by public SDK? | Do this |
|---|---|---|
| `cindervale-auth` | Yes | Make it genuinely public. Publish a real crate with the public auth surface, and keep anything private behind a separate internal crate. No placeholder. |
| `cindervale-telemetry` | Ask | If the SDK doesn't need it, keep it internal and don't claim the name with an empty crate. If you want it protected anyway, publish a minimal but real crate. Its README should say it's the public subset. |

If you must keep an internal crate internal and also protect the name:
- Rename the internal one (e.g. `cindervale-internal-telemetry`), so the public name is free for the real thing later.
- Or keep the same name but exclude it from the Artifactory virtual-repo remote (crates.io) via include/exclude patterns, and use `registry = "artifactory"` on every internal dependency edge.
- Add a CI check on internal workspaces that every `cindervale-*` dependency names its registry.

## 3. Publish order and `cargo install cindervale-cli`

- `cargo install cindervale-cli` resolves the whole tree from crates.io. All transitive dependencies must therefore be public.
- Publish in dependency order: `cindervale-auth` → (`cindervale-telemetry`, if public and used) → `cindervale-sdk` → `cindervale-cli`.
- Between publishes, wait until the index shows the new version. A `cargo publish` of a dependent crate can fail in the seconds before then. Newer cargo can publish a workspace in dependency order with `cargo publish --workspace`, which handles the waiting.
- Every inter-crate dependency needs both `path` (for local builds) and `version` (for publishing). A version-less path dependency fails `cargo publish`.
- Docs should say `cargo install cindervale-cli --locked`. Without `--locked`, cargo ignores your lockfile and may pick newer dependencies than you tested.
- The CLI crate needs a `[[bin]]` entry (or `src/main.rs`) whose name is the command you document. Check `rust-version` (MSRV) and `description`, `license`, `repository`, and `readme`, since crates.io rejects a crate without a description and license.
- Run `cargo publish --dry-run -p <crate>` for each crate before the real publish.
- A bad publish can only be yanked, not deleted. Do the dry run and, if possible, a `cargo install --path` smoke test from the packaged tarball first.

## 4. Checklist

1. Decide the fate of `cindervale-auth` (public, real) and `cindervale-telemetry` (public-real, renamed internal, or Artifactory-excluded).
2. Add `version` next to every `path` dependency.
3. Create the 24 h `publish-new` token scoped to `cindervale-*`.
4. Run `cargo publish --dry-run` for each crate.
5. Publish in order, waiting for the index between crates.
6. Add the trusted publisher on each crate, enable trusted-publishing-only if offered, and revoke the token.
7. Confirm the tag workflow has `id-token: write` and uses `rust-lang/crates-io-auth-action`.
8. Test `cargo install cindervale-cli --locked` in a clean container or a fresh `CARGO_HOME`.
9. Add the CI check that internal dependencies always name `registry = "..."`.

If you tell me whether the SDK really needs `cindervale-telemetry`, I can give a final recommendation for that crate.