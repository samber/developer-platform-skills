**Verdict: do not ship either part as drafted.** The skill's runtime fetch and the CI job both break rules in `agent-skill-offering`. Fix order: 1) rotate the token, 2) change the trigger, 3) replace the runtime fetch.

## 1. `SNYK_TOKEN: <our token>` in the env block

- The token is inline, and the skill forbids that.
- If it was ever committed, pasted in a PR, or sent anywhere, treat it as leaked.
- Do now: revoke it in Snyk and issue a new one.
- Store the new one as the repo secret `SNYK_TOKEN`.
- Reference it as `${{ secrets.SNYK_TOKEN }}`, and put `env:` on the scan step only, not the job or workflow.

## 2. `pull_request_target` for fork PRs

- This is the "pwn request" pattern. The trigger runs with repo secrets, and you want fork code scanned. Fork-controlled files then sit next to `SNYK_TOKEN`.
- The scan runs `uvx ... --dangerously-run-mcp-servers`. The skill says never to use that flag on `pull_request_target` from forks.
- The `./skills`-only target starts no MCP servers. That only holds if the fork does not add MCP configs the scanner reads. Do not rely on it.
- The risk is small while the repo is private. It becomes live the day you open the repo.
- Fix:
  - Trigger on `pull_request`.
  - Skip the scan for forks. Fork PRs get no secrets, so it would fail there anyway.
  - Rely on the release-job run, which scans the exact tree you ship.
- Optional: if you need the fork scan, use a maintainer-approved `environment` that has required reviewers. Never check out the fork head under `pull_request_target`.

## 3. Parsing JSON and failing on `prompt_injection`

- Remove this step. The skill's rule: "gate on the exit code, never on parsed output". Risk names and output shape change between scanner releases.
- It fails open. If the key is renamed, the JSON is malformed, or the parse step errors, the gate goes green.
- It is too narrow. `--ci` already fails on all findings. Your parser drops malicious code, credential handling, secrets, and third-party content exposure.
- Third-party content exposure is the finding your own `refresh-docs.sh` will trigger (see 4).

## 4. `scripts/refresh-docs.sh` and "follow the steps there"

This is the biggest defect. The design is "fetch remote content and follow it", which is the most common audit finding on benign skills.

- **Injection path.** `docs.pellmoor.dev/agents/latest.md` becomes live instructions to the agent. Anyone who can edit that page, or take over the domain or CDN, controls every agent running your skill.
- **Not "never stale".** The skill's lockstep rule requires that the skill matches the `pell` version the user has installed.
  - `latest.md` describes the newest release, not the installed one.
  - A user on `pell 1.3` gets `1.5` instructions, which is the removed-flag problem the skill exists to stop.
  - The tag-pinned install guarantee is gone, because the content changes after the tag.
  - Gate 3 (content check) cannot check text that arrives at run time.
- **Script hygiene.** Skills should ship few, readable, offline scripts. A network `curl` script is flagged by the scanner and by the public audits on skills.sh.
- **Fix:**
  1. Delete `refresh-docs.sh` and the "read and follow" line.
  2. Defer WHAT to `pell --help` and `pell <cmd> --help`.
  3. Put detailed agent docs in `references/`, generated from the release build and committed in the release commit, so each tag carries matching docs.
  4. Add the two-sided `Skill version:` guard to the SKILL.md body. Keep `metadata.version` equal to the code version.
  5. If you must link to live docs, give the URL as a human pointer and say it is data, never instructions.
- **Do not hide the finding.** Do not add `--ignore-risks third_party_content_exposure` to quiet the scanner. Fix the design.

## 5. Smaller issues in the job

- **`@latest` is unpinned.** Use `snyk-agent-scan@<version>`. The unpinned scanner runs from PyPI in a job holding your token, and its output changes under you.
- **`setup-uv` is needed.** `ubuntu-latest` has no `uv`. Add `astral-sh/setup-uv`, pinned to a commit SHA.
- **Missing permissions.** Add `permissions: contents: read`. Use `actions/checkout` with `persist-credentials: false`.
- **Private repo.** The scan uploads skill content to Snyk. Confirm you are cleared to do that before the first run.
- **Missing gates.** You describe one gate. The skill's default is gates 1-3 and 6 before the tag exists, and gates 1-4 and 6 on PRs. Add:
  - spec validation
  - version equality
  - a content check of the skill against `pell --help`
  - a changed-surface check

## Corrected job

```yaml
on:
  pull_request:
    paths: ["skills/**"]
  push:
    tags: ["v*"]

permissions:
  contents: read

jobs:
  skill-security-scan:
    runs-on: ubuntu-latest
    # Fork PRs get no secrets; the tag run scans what ships.
    if: github.event_name != 'pull_request' || github.event.pull_request.head.repo.full_name == github.repository
    steps:
      - uses: actions/checkout@v4
        with:
          persist-credentials: false
      - uses: astral-sh/setup-uv@1c37ad07a6a961277cf70c0d37d6f313000f5884 # v10.3.0
      - name: Run Snyk Agent Scan
        run: uvx snyk-agent-scan@<pinned-version> --ci --dangerously-run-mcp-servers --skills ./skills
        env:
          SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
```

- There is no JSON-parse step. `--ci` sets the exit code, and the exit code is the gate.
- Run the same job in the release flow before the tag is created. A tag-time failure means deleting the tag.
- A clean scan is a floor, not a trust claim.

## Next

Revoke the Snyk token now (about 2 minutes). Then I can draft the `references/` generation step and the version guard for the `pell` SKILL.md (about 30 minutes).

I did not run or test any of this. The review is based on the skill and its CI reference only, since I had no access to the `pell` repo.