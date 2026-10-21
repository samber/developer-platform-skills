# Security hardening

Contents: injection pairs (shell, secrets, downloads, outputs), repo hardening, scanners, incidents, compromised-tag runbook.

## Injection pairs

```yaml
# ✗ Bad - a caller passing a PR title as `message` runs arbitrary shell
runs:
  using: composite
  steps:
    - shell: bash
      run: vendor-cli report --message "${{ inputs.message }}"

# ✓ Good - the value reaches the shell as data, quoted
runs:
  using: composite
  steps:
    - shell: bash
      env:
        MESSAGE: ${{ inputs.message }}
      run: vendor-cli report --message "$MESSAGE"
```

```yaml
# ✗ Bad - secrets context is empty inside a composite action
      env:
        VENDOR_TOKEN: ${{ secrets.VENDOR_TOKEN }}

# ✓ Good - the caller passes the secret as an input; the action masks it
      env:
        VENDOR_TOKEN: ${{ inputs.api-key }}
      run: |
        echo "::add-mask::$VENDOR_TOKEN"
        vendor-cli login --token-stdin <<< "$VENDOR_TOKEN"
```

```yaml
# ✗ Bad - SHA-pinning this action pins nothing it fetches
      run: curl -sSL https://get.vendor.dev/install.sh | bash

# ✗ Bad - a checksum fetched from the same origin as the binary proves nothing
      run: |
        curl -sSLO "https://dl.vendor.dev/$CLI_VERSION/vendor-cli"
        curl -sSLO "https://dl.vendor.dev/$CLI_VERSION/vendor-cli.sha256"
        sha256sum --check vendor-cli.sha256

# ✓ Good - digest committed in the action repo at release time; unknown versions refused (Linux and macOS path; Windows steps use pwsh and Get-FileHash)
      env:
        CLI_VERSION: ${{ inputs.cli-version }}
      run: |
        platform="$(echo "$RUNNER_OS-$RUNNER_ARCH" | tr '[:upper:]' '[:lower:]')"   # e.g. linux-x64
        expected=$(awk -v v="$CLI_VERSION" -v p="$platform" '$1==v && $2==p {print $3}' "$GITHUB_ACTION_PATH/checksums.txt")
        [ -n "$expected" ] || { echo "::error::cli-version $CLI_VERSION is not supported by this action release"; exit 1; }
        curl -sSLo vendor-cli "https://dl.vendor.dev/$CLI_VERSION/vendor-cli-$platform"
        echo "$expected  vendor-cli" | shasum -a 256 --check
```

Alternative to the committed table: verify a build attestation or signature against a pinned signer identity, for example `gh attestation verify vendor-cli --repo <org>/<cli-repo> --signer-workflow <org>/<cli-repo>/.github/workflows/release.yml`, or cosign with a fixed certificate identity and issuer. `gh attestation verify` needs `gh` on the runner and `GH_TOKEN` in the step env, which self-hosted and GHES runners may lack. `shasum -a 256` exists on Linux and macOS runners; Windows steps need `Get-FileHash`.

```bash
# ✗ Bad - a value containing a newline injects extra outputs
echo "summary=$SUMMARY" >> "$GITHUB_OUTPUT"

# ✓ Good - random delimiter for multi-line values; never write untrusted data to GITHUB_ENV
delim="EOF_$(openssl rand -hex 8)"
{ echo "summary<<$delim"; echo "$SUMMARY"; echo "$delim"; } >> "$GITHUB_OUTPUT"
```

Writing untrusted text to `$GITHUB_ENV` lets it set variables such as `NODE_OPTIONS` or `LD_PRELOAD` for every later step. In JavaScript, use `core.setOutput`.

Also apply to JavaScript actions: never build a shell string from inputs; pass arguments as an array to the exec call.

## Repo hardening

- Enable immutable releases; protect `v*` tags with a ruleset that only the release workflow's GitHub App can bypass.
- Require 2FA, keep write access to a few named maintainers, enable private vulnerability reporting.
- Release from a protected environment with required reviewers; prefer short-lived GitHub App tokens over bot PATs.
- Scope `GITHUB_TOKEN` per job, starting from `permissions: {}`.
- Never use `pull_request_target`, `workflow_run` over fork code, or `issue_comment` triggers in the action repo's own CI. Customer-side split workflows for fork PRs are a separate pattern, see the vendor OIDC reference.
- Pin every third-party action in the repo's own workflows by SHA; let Dependabot update them with version comments.
- Sign release tags and commits; forged tags in past incidents were unsigned with impossible parent dates.
- Keep no long-lived registry or cloud credentials in the repo; use OIDC for anything the release job publishes.

## Scanners

- zizmor (online mode): `template-injection`, `dangerous-triggers`, `excessive-permissions`, `unpinned-uses`, `artipacked`, `impostor-commit`, `known-vulnerable-actions`. Run it on the repo and on the README example workflow.
- actionlint for workflow and expression errors.
- OpenSSF Scorecard (`Pinned-Dependencies`, `Token-Permissions`, `Dangerous-Workflow`, `Branch-Protection`, `Signed-Releases`) as a public signal to security-reviewing customers.

## Incidents

- reviewdog/action-setup, 2025-03: `v1` repointed to a malicious commit (CVE-2025-30154); used to steal another project's bot token.
- tj-actions/changed-files, 2025-03: every tag repointed with a stolen PAT; payload printed runner memory, including secrets, to public logs; 23,000+ repositories exposed (CVE-2025-30066).
- aquasecurity/trivy-action and setup-trivy, 2026-03: 76 of 77 and all 7 tags force-pushed to impostor commits after a first intrusion whose credential rotation was incomplete; the payload stole credentials before running the real scan, so pipelines stayed green (CVE-2026-33634).
- Common lesson: SHA-pinned consumers were unaffected; tag-push credentials are the target; incomplete rotation re-opens the door.

## Compromised-tag runbook

1. Revoke every credential with write access to the repo: maintainer sessions, PATs, App keys, deploy keys. Rotate all of them, not only the suspected one.
2. Freeze releases; restrict the tag ruleset to nobody.
3. Identify every tag whose target changed (compare against the release record and signed tags).
4. Repoint mutable tags to known-good commits; publish a new patch release on each supported major.
5. Publish a GitHub security advisory with affected tags, exposure window, the known-good SHAs, and the instruction to rotate any secret exposed to the action during the window.
6. Notify customers through the vendor's own channels and the `User-Agent` list of repositories that ran affected versions.
7. Write the post-mortem; fix the entry point before unfreezing.
