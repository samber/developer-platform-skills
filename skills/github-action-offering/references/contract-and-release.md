# Contract and release

Contents: breaking-change table, deprecation sequence, runtime timeline, release workflow, test matrix, bundling.

## Breaking-change table

| Change | Class | Why |
| --- | --- | --- |
| Add an optional input with a default that keeps old behaviour | minor | Old workflows behave the same. |
| Add an output | minor | Nobody reads it yet. |
| Add a value to an enum-like input | minor | Old values still accepted. |
| Change a default value | major | Pinned workflows change behaviour without an edit. |
| Rename or remove an input | major | The old name is silently ignored. |
| Rename or remove an output, or change its format (scalar to JSON, units) | major | Downstream `steps.x.outputs.y` reads break. |
| Make an optional input required | major | Workflows without it fail. |
| Change `runs.using` (node20 to node24, or to a JavaScript runtime) | major | Raises the minimum runner; GHES and old self-hosted runners fail. |
| Raise the minimum runner version, OS or architecture | major | Same reason. |
| Turn a warning into a failure by default | major | Green pipelines go red with no change on the customer side. |
| Bump the wrapped CLI to a version with a breaking flag change | major | The action's contract includes what the CLI does. |
| Bump the wrapped CLI within its own compatible range | patch or minor | Follows the CLI's semver. |

## Deprecation sequence

1. Add the replacement input; keep the old one working and mapped to the new behaviour.
2. Set `deprecationMessage` on the old input; the runner prints it as a warning whenever a workflow sets it.
3. State the removal major in the release notes and README.
4. Count runs that still set the old input from the deprecated-input flag the action sends with its API calls.
5. Remove it in the next major, together with any runtime bump scheduled for that major.

```yaml
# ✗ Bad - rename shipped in v2.4.0; every v2 workflow sending api_key now runs unauthenticated
inputs:
  api-key:
    required: true

# ✓ Good - v2.4.0 adds the new name, keeps the old one warning, v3.0.0 deletes it
inputs:
  api-key:
    description: Vendor API key. Prefer OIDC (see README).
    required: false
  api_key:
    description: Deprecated alias of api-key.
    required: false
    deprecationMessage: "api_key is deprecated; use api-key. Removed in v3."
```

## Runtime timeline (dated)

- `runs.using` accepts `node20`, `node24`, `composite`, `docker`.
- GitHub forced node12 to node16, node16 to node20 (transition from 2023-09), node20 to node24: deprecation announced 2025-09-19, node24 default 2026-06-16, node20 removed 2026-09-23 with the opt-out gone. After removal, actions still declaring node20 run on node24 with a job warning, untested by their authors.
- Runner v2.328.0 supports both node20 and node24. Node 24 does not run on macOS 13.4 and earlier or on ARM32 self-hosted runners.
- GitHub Enterprise Cloud refuses self-hosted runners below v2.329.0 since 2026-09-29; GHES is not covered by that enforcement, so GHES instances are where old runners and old runtimes survive. Check which GHES releases ship a node24-capable runner before declaring the GHES floor.
- Vendors shipped node24 as a major and deleted deprecated inputs in it: `actions/checkout` v5, `google-github-actions/auth` v3 (2025-08-28, removed `retries`, `backoff`, `backoff_limit`), `docker/build-push-action` v7, `aws-actions/configure-aws-credentials` v6, `codecov/codecov-action` v6.
- Floating majors did not save consumers: weeks after removal, several first-party v4 majors still declared node20.

## Pinned and locked consumers

- SHA-pinned customers and customers with a workflow lockfile (`.github/workflows/actions.lock`, preview from 2026-10-14) run the exact commits they locked, nested `uses:` and reusable workflows included. A moved `vX` reaches none of them.
- Dependabot proposes the next `vX.Y.Z` tag and regenerates the lockfile entry; a `uses: org/action@<sha> # vX.Y.Z` comment is what lets it update a SHA pin.
- A change to a nested `uses:` shows up as a lockfile diff in customer PRs: keep nested dependencies few and explain changes in release notes.

## Release workflow

1. Merge to the default branch with the contract check and test matrix green.
2. A maintainer starts the release workflow; it runs in a protected environment with required reviewers.
3. The workflow builds `dist/` or binaries, attests them (`actions/attest` or equivalent), creates a draft `vX.Y.Z` release, attaches assets, publishes it (immutable).
4. The same job moves `vX` to the released commit with a short-lived GitHub App token allowed by the tag ruleset: `git tag -f vX <sha>` then `git push -f origin refs/tags/vX`.
5. Release notes list: full commit SHA, the copy-paste `uses: org/action@<sha> # vX.Y.Z` line, breaking changes, deprecations with their removal major, minimum runner version.

GitHub's own documentation shows `git push -f --tags`; it pushes every local tag. Push the one tag you moved.

## Test matrix

- Self-test with `uses: ./` in the action's own CI.
- Run on `ubuntu-latest`, `windows-latest`, `macos-latest` and an ARM runner for every OS the README claims.
- Run one job on a self-hosted runner pinned to the oldest supported runner version; this catches the runtime-floor break hosted runners hide.
- Run against a real sandbox account of the vendor product, with OIDC on, not only against mocks.
- Use `act` for local iteration only: it does not reproduce OIDC or hosted runner images.

## Bundling (JavaScript actions)

- Commit the bundled `dist/`: the runner installs no dependencies.
- Bundle as ESM: `@actions/*` toolkit packages are ESM-only from v3, and GitHub's own TypeScript action template bundles with Rollup.
- Add check-dist: rebuild in CI and fail when `git diff --ignore-space-at-eol --text dist/` is non-empty, so reviewed source and shipped code cannot drift.
