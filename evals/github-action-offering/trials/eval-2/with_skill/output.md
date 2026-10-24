# Tallowick CI offering: draft v1

**Verdict:** ship two composite actions, `setup-tlw` and `tlw-action`. Do not ship the container action, the `curl | bash` install or the `@main` reusable workflow. Each of the three fails a contract rule or a customer segment.

## 0. Assumptions (provisional)

I have no human to answer these. The plan is provisional on every row.

| # | Assumption | Drives | Who confirms |
|---|---|---|---|
| A1 | `tlw` auth (exit 3) means a Tallowick key or token. Cloud credentials come from the customer's own step, such as `azure/login` OIDC. | §4 | Backend lead |
| A2 | The Tallowick backend does not validate OIDC today. | §4 | Backend lead |
| A3 | No community action exists for `tlw`. | §1 | Platform |
| A4 | v1 runs on push, schedule and same-repo PRs. It does not run on fork PRs and does not write PR comments. | §4, §8 | Product |
| A5 | GitHub Releases ships `tlw` for linux x64/arm64, macOS x64/arm64 and windows x64, with a Windows `.zip` or `.exe`. | §3 | CLI owner |
| A6 | The Windows self-hosted runners have `pwsh` (PowerShell 7). | §3 | Azure account team |
| A7 | The 15% of customers not on GitHub or GHES are mostly Azure DevOps. | §7 | Sales ops, from the CRM |
| A8 | The team stays 1.5 engineers after launch. A different owner after launch changes §7 and §8. | §8 | Eng manager |

## 1. Platform plan vs. contract rules

| Plan item | Problem | Replacement |
|---|---|---|
| Docker container action | Runs on Linux only. Windows runners cannot run it (the Azure cluster). macOS runners cannot run it (the large account). GHES runners behind proxies often lack Docker or cannot pull the image. | Composite action with logic in the CLI. Keep the image for a Bitbucket Pipe later. |
| `curl -sSL .../install.sh \| bash` in the container | Breaks contract rule 5. SHA-pinning the action pins nothing the script fetches. Whoever controls `get.tallowick.io` runs code in the customer's most privileged automation. | Download a versioned release asset. Verify it against a digest committed in the action repo. |
| "Always latest fixes" via `latest` | Customers who SHA-pin never see a moved tag. | Each CLI release triggers a new action release (§5). Dependabot then delivers it. |
| Reusable workflow `scan.yml@main` as the product | Callers will not hand `runs-on` and permissions to a third party. Marketplace cannot list it. `@main` is a mutable ref that breaks rule 3 and never reaches SHA pinners. GHES needs the repo synced too. | Delete it as the product. Put a copy-paste workflow in the docs instead. |

## 2. Offering shape

- **Repo 1: `tallowick/setup-tlw`.** Installs a pinned `tlw`, verifies it, adds it to `PATH`.
- **Repo 2: `tallowick/tlw-action`.** Runs `tlw scan` with typed inputs and outputs. It calls `setup-tlw` through a SHA-pinned nested `uses:`.
- Both repos get a root `action.yml`, which Marketplace requires. Fix the org and repo names now. A later transfer drops the verified badge.
- **Not in v1:** PR comments, annotations and job summaries (the "rich" action). Add them in a minor release after launch.
- **Dependency risk:** GHES customers must sync both repos with `actions-sync`. State this in the README. If the sync burden hurts, inline the install step in `tlw-action` and drop the nested `uses:`.

## 3. Action type: composite

- `runs.using: composite`. It needs no Node, so the GHES 3.14-3.16 runtime floor and the Node 24 deadline do not apply.
- Install steps need a Windows path. Use `shell: pwsh` with `Get-FileHash`, and `if: runner.os == 'Windows'` on the pwsh step. The bash step covers Linux and macOS and uses `shasum -a 256`.
- Cache in `$RUNNER_TOOL_CACHE/tlw/<version>/<os-arch>`. Do not use `actions/cache`: it is a Node action and needs its own sync on GHES.
- Proxy and air-gap inputs:
  - Honour `HTTPS_PROXY`.
  - `mirror-url` swaps the download base.
  - `tlw-path` uses a pre-installed binary and skips the download.
- **Version rule.** `version` defaults to the newest `tlw` this action release ships digests for. A version not in `checksums.txt` fails with a named error. `latest` is allowed only once signature verification exists (attestation or cosign). Resolve it from Tallowick's own endpoint, never the GitHub API.

`setup-tlw/action.yml` (sketch):

```yaml
name: Setup tlw
description: Install a verified Tallowick CLI and add it to PATH.
branding: { icon: shield, color: blue }
inputs:
  version:
    description: tlw version. Must be listed in checksums.txt of this action release.
    required: false
    default: "<newest-version-with-digests>"
  mirror-url:
    description: Base URL of an internal mirror of the release assets. Empty uses GitHub Releases.
    required: false
    default: ""
  tlw-path:
    description: Path to a pre-installed tlw. Skips the download.
    required: false
    default: ""
outputs:
  version:
    description: Installed tlw version.
    value: ${{ steps.install-unix.outputs.version || steps.install-win.outputs.version }}
runs:
  using: composite
  steps:
    - id: install-unix
      if: runner.os != 'Windows'
      shell: bash
      env:
        TLW_VERSION: ${{ inputs.version }}
        MIRROR_URL: ${{ inputs.mirror-url }}
        TLW_PATH: ${{ inputs.tlw-path }}
      run: |
        # look up the digest in $GITHUB_ACTION_PATH/checksums.txt, refuse unknown
        # versions, download, shasum -a 256 --check, install under $RUNNER_TOOL_CACHE
    - id: install-win
      if: runner.os == 'Windows'
      shell: pwsh
      env:
        TLW_VERSION: ${{ inputs.version }}
        MIRROR_URL: ${{ inputs.mirror-url }}
        TLW_PATH: ${{ inputs.tlw-path }}
      run: |
        # same steps with Get-FileHash and the .exe asset
```

Every input reaches the shell through `env:` and is quoted (rule 4).

## 4. Contract and auth (`tlw-action`)

Inputs, all kebab-case and string-typed. Booleans accept only `true` or `false`.

| Input | Default | Note |
|---|---|---|
| `path` | `.` | Directory to scan. |
| `fail-on-drift` | `true` | `false` downgrades exit 2 to a warning. |
| `auth` | `auto` | One of `auto`, `oidc`, `key`. |
| `api-key` | empty | Optional from v1. |
| `version`, `mirror-url`, `tlw-path` | as in §3 | Passed to `setup-tlw`. |
| `extra-args` | empty | Passed as data, never concatenated into a shell string. |

Outputs: `drift-detected` (`true` or `false`) and `exit-code`.

**Exit-code mapping** (the step decides; the CLI exit code is also exposed):

| `tlw` exit | Step result |
|---|---|
| 0 | Pass. |
| 2 | Fail. With `fail-on-drift: false`: pass plus `::warning::`. |
| 1 | Always fail, with a named error. |
| 3 | Always fail, with a named error. |

Do not set a job-level `continue-on-error` as a workaround. The input is the supported path.

**Auth, per A1 and A2:**
- v1 takes a masked `api-key` input. Call `::add-mask::` before any use. Document `secrets.TLW_API_KEY` in the README.
- An empty key fails with `api-key is empty`. This is a named error, not a fallback to anonymous mode.
- Keep `auth: auto|oidc|key` and the optional key in the contract now, so OIDC lands as a minor release. Until the backend accepts OIDC, `oidc` fails with "not yet supported".
- When the backend does accept OIDC:
  - Request a Tallowick-specific audience.
  - Bind on numeric `repository_owner_id` and `repository_id`, plus a ref or environment.
  - If both the key and `ACTIONS_ID_TOKEN_REQUEST_URL` are absent, fail naming both causes.
- **Ask the backend lead this week:** can the backend validate OIDC, and by when? A date inside the seven weeks moves OIDC into scope.
- **GHES:** its OIDC issuer is usually unreachable from SaaS. Document GHES as key-only unless customers register a JWKS.
- **Fork PRs (A4):** they receive no secrets, so the action exits with a message naming that limit. Never tell customers to use `pull_request_target`.

## 5. Versioning and release

1. Turn on immutable releases before the first public tag.
2. Ship `v1.0.0` for both repos. Reuse no version number from any prior community action (A3).
3. Each fix is a `vX.Y.Z` immutable release. The moving `v1` tag points at a released commit only and carries no GitHub release.
4. Release from a protected environment with required reviewers. Move the tag as `refs/tags/v1`, never with `--tags`.
5. Release notes include the full SHA and the line `uses: tallowick/tlw-action@<sha> # v1.x.y`.
6. **"Latest fixes" automation.** A `tlw` release triggers a job in `setup-tlw` that opens a PR adding the new version's digests to `checksums.txt` and bumping the default version. A reviewer approves. The release publishes `v1.x.y`.
7. A `tlw` change that breaks flags or exit codes is a new action major.
8. Raising the runner floor or changing a default is also a major.
9. Add a contract-diff job in CI that diffs `action.yml` inputs and outputs against the last release.

## 6. Hardening

- Use the `env:` pattern for every input. Do not interpolate `${{ inputs.* }}` into `run:`.
- Write outputs to `$GITHUB_OUTPUT` with a random delimiter. Never write untrusted data to `$GITHUB_ENV`.
- Pin every nested `uses:` by full SHA. Pin tool images by digest. Pin every downloaded binary by a committed digest.
- Protect `v*` tags with a ruleset that only the release App can bypass. Require 2FA. Sign release tags.
- Keep the action repos' own CI off `pull_request_target`.
- Send a versioned `User-Agent`: `tlw-action/1.0.0 (github-actions; <OS-ARCH>)`. Put any extra telemetry behind an input that turns it off, and document both in the README.
- Write the compromised-tag runbook before launch (revoke all write credentials, freeze, repoint, advisory, rotate secrets).

## 7. Listing, GHES and ports

- Marketplace: unique name, branding, one category. Request the verified creator badge now. Enterprise allowlists key on it, and it takes calendar time.
- README opens with a copy-paste workflow:
  - SHA-pinned `uses:` line with a version comment.
  - `permissions: contents: read`.
  - Every input and output, with defaults.
  - Minimum runner and GHES versions: GHES 3.14-3.16 (composite, no Node). Test the oldest runner shipped with 3.14.
- Put the same snippet in the docs quickstart. That page drives adoption.
- **GHES, 25% of customers:** access comes through GitHub Connect or `actions-sync` for both repos. Behind proxies, customers use `mirror-url` or `tlw-path`.
- Ports: ship documented CLI snippets for GitLab, Azure DevOps and the rest. Each snippet downloads a pinned `tlw`, verifies it and maps the exit codes. No native package in v1.
- If A7 holds, an Azure DevOps task is the first port to fund after launch. Reuse the existing Linux image only for a Bitbucket Pipe.

## 8. Plan: 7 weeks, 1.5 engineers

Week and exit criterion:

1. Close A1, A2, A5 and A6. Build the `checksums.txt` generator. Create the repos with rulesets and immutable releases on.
2. `setup-tlw` on Linux and macOS: download, digest check, tool cache, `mirror-url`, `tlw-path`.
3. `setup-tlw` on Windows (`pwsh`). Add the self-hosted Windows job to CI.
4. `tlw-action`: inputs, exit mapping, outputs, key auth, `fail-on-drift`. Contract-diff job.
5. Test matrix: hosted ubuntu, windows and macos; an ARM runner; oldest self-hosted runner; a GHES 3.14 instance behind a proxy. Run zizmor and actionlint. Gates must be green.
6. README, docs quickstart, GHES and proxy guide, snippets for other CI. Release `v1.0.0`. Submit the Marketplace listing.
7. Pilot with one customer on GHES and one on Windows self-hosted. Add the telemetry dashboard. Fix first-run failures. Buffer.

Cut order if time slips: documented snippets, then the Marketplace listing, then the macOS ARM job. Never cut the digest check, the contract-diff job or the Windows path.

## 9. Measurement

Track weekly active repositories by CI and action version, first-run failure rate by error class, and the share of runs on exit 2 versus 1 and 3. Add a header flag whenever a deprecated input is set. Watch Dependabot PR adoption of each `vX.Y.Z`.

## 10. Release gates

A release ships only when all of these pass:

- Contract diff is clean, or the release is a major.
- The integration matrix is green on every OS the README claims, the oldest self-hosted runner and GHES 3.14, against a real sandbox account.
- zizmor shows no finding at medium severity or above on the action repo and the README example. actionlint is clean.
- Every nested `uses:` is SHA-pinned, and every downloaded binary is verified against a committed digest.

## Questions for the platform meeting

1. Can the backend validate OIDC, and by what date? (§4)
2. Does `tlw` exit 3 cover Tallowick auth, cloud auth, or both? (A1)
3. Does the CLI release ship Windows and macOS ARM builds with stable asset names? (A5)
4. Do the Azure customers run Azure DevOps or GitHub-hosted workflows on their Windows runners, and do the runners have `pwsh`? (A6, A7)
5. Must v1 support fork PRs or PR comments? (A4)

**Next action:** send questions 1-3 to the backend and CLI owners today. Their answers change §3 and §4.