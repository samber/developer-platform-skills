# Verdict: don't ship this as a minor, and don't move `v2` with it

Five of the seven items break existing workflows. Moving `v2` pushes the change to about 900 repos at once, with no opt-in and no pin to hold them back. Semver and the Actions convention both say this is a v3.

## Item by item

| # | Change | Breaks `@v2` users? | What happens |
|---|---|---|---|
| 1 | `api_key` → `api-key` | **Yes** | Workflows that set `api_key:` get an "unexpected input" warning and an empty key, so auth fails. |
| 2 | `severity-threshold` default `high` → `medium` | **Yes, silently** | Repos that never set it start getting more findings with no change on their side. |
| 3 | `license-findings` warns → fails | **Yes** | Steps that were green go red. This stacks with #2, because `medium` surfaces more license findings too. |
| 4 | `node20` → `node24` | **Maybe** | It is fine on GitHub-hosted runners. Self-hosted and GHES runners below the minimum runner version for node24 can't run the action. Check the minimum version in GitHub's docs and name it in the notes. |
| 5 | CLI 4.x → 5.0 | **Unverified** | "We never called `--format table`" covers one removal. Check the 5.0 notes for exit codes, output and SARIF/JSON shape, config file, flag defaults, and any user-supplied args passthrough. Customers may use flags you don't. |
| 6 | Drop `verbose` | **Low risk, still breaking** | It only produces an "unexpected input" warning. But telemetry can't prove "nobody sets it" if private repos or opted-out runs don't report. |
| 7 | New `output-file`, default empty | No | Additive. Ship it. |

## Recommended split

**v2.4.0 (minor, safe to move `v2`):**
- Add `api-key` and keep `api_key` as a fallback. Read `core.getInput('api-key') || core.getInput('api_key')`. Don't set a default on either input in `action.yml`, or you can't tell which one the user set. Put a `deprecationMessage` on `api_key`.
- Mark `verbose` deprecated and make it a no-op with a warning. Don't remove it.
- Add `output-file`.
- Add an opt-in input for license failure, for example `fail-on-license-findings: false`. Add `medium` as an opt-in value of `severity-threshold`, but leave the default at `high`.
- Take the CLI 5.0 bump only if a review of its notes and a canary run show no output or exit-code change. Otherwise defer it.
- Take `node24` only if you are happy to set a minimum runner version for self-hosted users. Otherwise defer it.

**v3.0.0 (new major, new `v3` tag):**
- Flip `severity-threshold` to `medium`.
- Make `license-findings` fail by default.
- Remove `api_key` and `verbose`.
- Move to `node24` and the CLI 5.0 bundle, if you deferred them from 2.4.0.
- Write a migration guide with the cases ordered by blast radius, each with a detection signal and a before/after example. Dependabot and Renovate will then raise `v2` → `v3` bump PRs, so users choose when to move.

This still gives you the kebab-case rename, the new `output-file` input and the deprecation path on Thursday, with no red builds. Product still gets `medium` and fail-on-license, just opt-in now and default in v3.

## If you ship it as planned anyway

1. Call the release 3.0.0, not 2.4.0. Don't move `v2`.
2. Put a "Breaking changes" section at the top of the release notes. Announce it at least a week before Thursday, since users can't see a default change in their diff.
3. Run a canary first: tag `v2.4.0` or `v3.0.0-rc.1` and run it against about 10 real consumer repos, including one self-hosted runner, before any floating tag moves.
4. Keep `v2.3.1` ready as the rollback target. If it goes wrong, repoint `v2` back to it. Runs that already happened can't be undone.

## Questions for you

- Does the action pass user-supplied flags or args to the CLI?
- Do you know the share of self-hosted or GHES users among the 900 repos?
- Does telemetry cover private repos?

The first two decide whether `node24` and CLI 5.0 can go in 2.4.0.

I didn't inspect the action's repo, so this plan is based only on your changelog.