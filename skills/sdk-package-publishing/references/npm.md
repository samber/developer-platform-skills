# npm

## Contents

- Library vs binary
- CI auto-publishing: trusted publishing, staged publishing, first publish, provenance, tokens
- Public publishing: namespace, package shape, dist-tags, removal
- Private publishing
- Private consumption
- Dated changes

## Library vs binary

- **Library:** one package; `exports`, `types` and `files` below.
- **JS CLI:** add `bin` (`{"corp": "dist/cli.js"}`) with a `#!/usr/bin/env node` shebang. Users run it with `npx @corp/cli` or a global install.
- **Native binary (Go, Rust, Zig CLI):** one package per platform (`@corp/cli-linux-x64`, `@corp/cli-darwin-arm64`) declaring `os`, `cpu` and, on Linux, `libc`; the main package lists them all as `optionalDependencies` pinned to the exact same version, and npm installs only the matching one.
  - Never download the binary in `postinstall`: npm 12 silently skips dependency install scripts the consumer has not approved, and `npx` and global installs have no project policy to approve them.
  - Each platform package needs its own trusted publisher configuration.
  - Publish platform packages first, the main package last, so the main package never points at missing versions.

## CI auto-publishing

- **Trigger:** a protected tag push. Pipeline shape, dist-tag guard and staged publish: release-workflow.md.

**Trusted publishing**

- Trusted publishing (OIDC) works from GitHub Actions on GitHub-hosted runners, GitLab CI/CD on GitLab.com shared runners, and CircleCI cloud. Self-hosted runners are not supported.
- Node 22.14.0+ and npm CLI 11.5.1+ for OIDC publish, 11.10.0+ for `npm trust`, 11.15.0+ for `npm stage`. Pin 11.15.0+ in the release job: Node's bundled npm may be older.
- GitHub workflows need `permissions: id-token: write` on the publish job only. `actions/setup-node` with `registry-url` is fine; set no `NODE_AUTH_TOKEN` for the publish step. If private dependencies need a read token, scope it to the `npm ci` step only.
- Identity fields (GitHub): owner, repository, workflow file name only (`release.yml`, not a path), optional environment. Always set the environment, matching the job's `environment:` name exactly.
- Up to 10 configurations per package. Permissions and environment can be edited in place; a new repository or project identity needs a new configuration. A configuration not validated by a publish within 48 hours expires and must be recreated, so register it the day you run the first release.
- npm rejects OIDC publishes triggered by `pull_request_target` and `issue_comment`. Trigger releases on a protected tag push.
- After migrating, set the package's publishing access to "Require two-factor authentication and disallow tokens", then revoke every remaining write token.

**Staged publishing**

- CI runs `npm stage publish <tarball> --access public --tag <channel>`. It never prompts for 2FA. The tag is fixed once staged, and pre-releases still need an explicit `--tag`.
- A maintainer runs `npm stage list`, inspects with `npm stage view <stage-id>` or `npm stage download <stage-id>`, then `npm stage approve <stage-id>` (2FA prompt) or `npm stage reject <stage-id>`. Approval waits for npm's malware scan.
- Configurations allow staging by default; direct `npm publish` and "Allow npm dist-tag" are separate opt-in permissions. Keep both off: a compromised workflow then cannot reach `latest`.

**First publish of a new package**

- OIDC cannot create a package. Create it with `npm stage publish` from a local `npm login` session or a granular token, approve it, add the trusted publisher, then revoke that token. Stage-only tokens can still move dist-tags and deprecate versions: they are write credentials.

**Provenance**

- Trusted publishing generates provenance automatically for a public package built from a public repository on GitHub Actions or GitLab. CircleCI publishes get none.
- Otherwise add `--provenance` (or `publishConfig.provenance: true`). The `repository` field in `package.json` must match the building repository exactly.
- Consumers verify with `npm audit signatures`. Provenance proves origin, not safety.

**Tokens**

- Classic and automation tokens no longer exist. Granular write tokens live 90 days at most.
- Tokens with "bypass 2FA" are losing account-management and direct-publish rights; plan any token-based pipeline as temporary.
- `npm login` issues short session tokens: they suit a human first publish, never CI.

## Public publishing

**Namespace**

- Publish SDKs under an org scope (`@corp/sdk`). Claim `@corp` on public npm even if every package is private: it blocks lookalike scopes and is the cheapest dependency-confusion defense.
- Unscoped names must not resemble an existing package. npm does not transfer squatted names on request; only trademark claims move a name.

**Package shape**

- Declare `exports` for every public entry point. Adding `exports` later is a breaking change: it blocks deep imports.
- Put the `types` condition first in each `exports` branch and `default` last.
- Ship ESM-only only when every consumer can import ESM. Dual ESM/CJS risks the dual-package hazard: two module instances break singletons and `instanceof`.
- Use `files` as an allow-list. `package.json`, `README`, `LICENSE`, the `main` file and `bin` files always ship; `.npmrc`, `package-lock.json`, `yarn.lock`, `pnpm-lock.yaml` and `bun.lockb` never do. `npm-shrinkwrap.json` does ship: never commit one in a library.
- Build in `prepack` so a stale `dist/` never ships. Mark internal workspace packages `"private": true`.
- Scoped packages: pass `--access public` (or `publishConfig.access: "public"`) explicitly; npm docs disagree on the default.
- Avoid `postinstall`: npm 12 skips dependency install scripts unless the consumer approves them.
- Preflight: `npm pack --dry-run`, `npx publint`, `npx @arethetypeswrong/cli --pack`.

```
// ✓ Good - ESM-only, types first, default last
"exports": { ".": { "types": "./dist/index.d.ts", "default": "./dist/index.js" } }

// ✗ Bad - types after default, never resolved
"exports": { ".": { "default": "./dist/index.js", "types": "./dist/index.d.ts" } }
```

**Dist-tags and pre-releases**

- `npm publish` tags `latest` by default. npm 11+ refuses a pre-release or a lower-than-latest version without `--tag`.
- Publish pre-releases with `--tag next` (or `beta`, `rc`). Never hard-code `--tag latest` in CI: a rerun of an old release job then moves `latest` backwards.
- Move tags with `npm dist-tag add @corp/sdk@1.4.2 latest`.
- A pre-release that already became `latest`: point `latest` back at the last stable version, add the pre-release under its channel tag (`npm dist-tag add @corp/sdk@3.2.0-beta.1 beta`), and deprecate it only if it is broken. Past 72 hours it cannot be unpublished anyway.

**Removal**

- `npm deprecate @corp/sdk@1.4.3 "Broken auth refresh, use 1.4.4"`: installs keep working with a warning. Clear it with an empty message.
- Unpublish: within 72 hours if no public package depends on it; later only with no dependents, under 300 downloads last week, and a single owner. A `name@version` can never be reused, and a full unpublish blocks the name for 24 hours.

## Private publishing

- npmjs.com private packages: scoped, paid plan, `--access restricted`.
- Private feeds with npm support: GitHub Packages, GitLab Package Registry, AWS CodeArtifact, Azure Artifacts, Google Artifact Registry, Artifactory, Nexus. Choose by where CI and identity already live.
- GitHub Packages npm: scoped only, scope equals the owning account; authenticate with the workflow's built-in token (`packages: write`) or a classic personal token. Fine-grained tokens are not accepted.
- GitLab forwards unknown npm names to npmjs.com by default. Disable forwarding on groups that host private packages.
- Set `publishConfig.registry` in every private package so a stray `npm publish` cannot reach the public registry.

## Private consumption

```
# .npmrc committed to the repo - no secret in the file
@corp:registry=https://npm.pkg.example.com/
//npm.pkg.example.com/:_authToken=${NPM_READ_TOKEN}
```

- Inject `NPM_READ_TOKEN` from the CI secret store with read-only scope. An unset variable makes npm fail at config load ("Failed to replace env in config"), never fall back to anonymous access.
- Keep internal packages inside the mapped scope. An unscoped internal name resolves from public npm whenever someone publishes it there.
- Install with `npm ci` against a committed lockfile.

## Dated changes

- 2025-07: trusted publishing GA (GitHub Actions, GitLab.com).
- 2025-12-09: all classic tokens revoked; granular write tokens capped at 90 days; 2FA enforced by default for new packages.
- 2026-04-06: CircleCI trusted publishing.
- 2026-05-22: staged publishing GA (CLI 11.15.0+).
- 2026-07-08: npm 12 GA, install scripts off by default.
- 2026-07-31: bypass-2FA tokens lose account and trust-configuration actions; direct publish with them targeted to end around 2027-01.
- 2026-09-03: multiple configurations per package; direct publish opt-in.
- 2026-09-18: stage-only granular tokens (still able to move dist-tags and deprecate).
- 2026-09-30: OIDC dist-tag permission opt-in.
- 2026-10-02: unvalidated configurations expire after 48 hours; `npm stage publish` can create new packages.
