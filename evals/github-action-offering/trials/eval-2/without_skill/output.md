# Tallowick CI offering: GitHub Actions (draft)

## Verdict on the platform-meeting plan

Ship the goal (customers in CI, two lines of YAML, latest fixes). Change the mechanism: the plan as written fails on about 40% of the customer base.

| Plan item | Problem | Change |
|---|---|---|
| ❌ Docker container action | Runs on Linux runners only. It excludes the Windows self-hosted cluster and the macOS account. GHES runners also need Docker. | Composite action (bash), runs on Linux, Windows and macOS. |
| ❌ `curl ... install.sh \| bash` at runtime | No checksum, and no `-f`, so an HTML error page gets piped into bash. A new `tlw` can silently change behavior. Proxied GHES runners may not reach `get.tallowick.io`. Enterprise security reviews will reject it. | Download the pinned release from GitHub Releases, verify SHA-256, and allow a mirror URL. |
| ❌ Fetching `tlw` inside the image | The image we already publish can bake `tlw` in. | Keep the image as a Linux/`docker://` alternative only. No new work. |
| ⚠️ Reusable workflow at `@main` | A mutable ref is a supply-chain finding for enterprises. GHES cannot resolve `tallowick/workflows` unless an admin enables GitHub Connect or syncs the repo. A reusable workflow also fixes `runs-on` and is job-level, so it cannot be a step in a customer's Terraform job. | Version tags (`@v1`). Put the workflow in the same repo as the action. Treat the action as the product and the workflow as sugar. |

Exit code 2 also needs handling. A raw nonzero exit makes drift look like a crashed step. The action must separate "drift found" (a result) from 1 and 3 (errors).

## Product

One public repo, `tallowick/tlw-action`, with the action at the repo root and the reusable workflow in `.github/workflows/scan.yml`. It has no dependency on any other action or repo, so GHES admins can mirror it with `actions-sync` in one step.

**Step form** (the main path, used inside the customer's existing job):

```yaml
- uses: tallowick/tlw-action@v1
  with:
    token: ${{ secrets.TLW_TOKEN }}
```

**Workflow form** (a whole job):

```yaml
jobs:
  drift:
    uses: tallowick/tlw-action/.github/workflows/scan.yml@v1
    secrets: inherit
```

### Inputs

- `token`: Tallowick credential. ❓ Confirm how `tlw` authenticates (see open questions).
- `version`: defaults to the `tlw` version this action release pins. `latest` is opt-in.
- `args`: passed through to `tlw`.
- `working-directory`.
- `fail-on-drift`: default `true`.
- `download-url`: mirror base URL for proxied or air-gapped runners.
- `tlw-path`: use a preinstalled binary and skip the download.
- Workflow form only: `runs-on` (label or JSON array).

### Behavior

1. Detect OS and arch. Download `tlw` for that target and verify the checksum.
2. Run `tlw`, capturing the exit code into a variable. Do not use `set -e` before mapping it.
3. Map exit codes:

| Code | Meaning | Action result |
|---|---|---|
| 0 | clean | pass |
| 2 | drift | `drift=true` output, job summary, annotation; fails unless `fail-on-drift: false` |
| 1 | runtime error | always fails |
| 3 | auth error | always fails, with a hint about the token or OIDC setup |

4. Outputs: `drift`, `exit-code`, `tlw-version`.
5. Write a job summary with the drift list.
6. Cache the binary in the runner tool cache.

### How "latest fixes" still works

- Each action release pins a `tlw` version and its SHA-256 values.
- We cut a patch release and move the `v1` tag when `tlw` ships a fix. Customers on `@v1` get it automatically.
- Security-conscious customers pin an action SHA and update it with Dependabot.
- `version: latest` is there for people who want to opt in.

## Platform matrix

| Segment | Support | Notes |
|---|---|---|
| GitHub.com, Linux | ✅ | Primary path. |
| GitHub.com, Windows / macOS | ✅ | Bash step shell. Git for Windows ships bash, and checkout needs git anyway. |
| GHES 3.14 to 3.16, proxied | ⚠️ | Admin mirrors the repo with `actions-sync` (we document the recipe). Use `download-url` pointing at an internal mirror. Honor `HTTPS_PROXY` and custom CA. Test on real GHES 3.14 and 3.16. |
| Windows self-hosted (Azure Terraform) | ✅ | Needs `tlw` Windows binary, Git Bash on the runner, and an Azure OIDC example. |
| Large macOS account | ✅ | Needs an arm64 and amd64 `tlw` darwin build. |

## Prerequisites to check in week 1 (blockers)

- Release assets for linux, darwin and windows on amd64 and arm64, plus a published `checksums.txt`.
- Whether the Windows and macOS binaries are signed or notarized. Gatekeeper and SmartScreen can block them.

## Seven-week plan (1.5 engineers)

| Week | Work |
|---|---|
| 1 | Audit release assets and checksums. Confirm the auth model. Build test rigs: GHES trial (3.14 and 3.16) behind a squid proxy, a Windows self-hosted runner, and a macOS runner. |
| 2-3 | Action v0.x: install, verify, run, exit-code mapping, outputs, summary. CI matrix on 3 OSes with fixtures that force exits 0, 2, 1 and 3. |
| 4 | GHES and proxy hardening: mirror input, CA and proxy handling, `actions-sync` recipe. Windows self-hosted validation. |
| 5 | Reusable workflow wrapper. Docs and examples: GitHub.com, GHES, Azure OIDC on Windows, macOS. |
| 6 | Pilot with 3 design partners (one GHES, one Azure/Windows, the macOS account). Fix what they hit. |
| 7 | GA `v1`, Marketplace listing, sales one-pager, support runbook. Buffer for slips. |

**Cut first if late:** the reusable workflow, then the job summary polish. **Stretch, not committed:** SARIF upload to code scanning.

## Out of scope

- GitLab CI, Azure DevOps and other CI systems.
- A JavaScript action (better proxy handling and tool-cache, but needs JS skills and a committed `dist/`). Revisit in v2 if the bash action hits proxy limits.

## Open questions

1. How does `tlw` authenticate (static token, OIDC, cloud credentials)? This drives the Azure and GHES story.
2. What are the other ~15% of the CRM on (GitLab, Azure DevOps)? The Azure accounts might be on Azure DevOps rather than GitHub.
3. Do the Windows and macOS accounts sit inside the 60% or the 25%?
4. Is `tallowick/tlw-action` allowed to be public?
5. Can we get a GHES 3.14 to 3.16 test instance and proxy for week 1?
6. Who are the three design partners, and will they commit in week 1?