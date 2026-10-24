# `orn` CLI: fix CI hangs and make it agent-safe

Your two problems share one root cause. `orn` decides how to behave from what it assumes about the caller, and it should decide from what it can detect. A CI job and a Claude Code session both have no terminal, so one set of fixes covers both.

## Verdict on your fix idea

- **`--yes`: keep it, but it isn't enough.** Without a terminal, `orn` must never wait for input. It should exit at once with a clear error. `--yes` then becomes the explicit opt-in, not the only thing standing between your users and a 6h hang.
- **"CI must set `PAGER=cat`": drop it.** Documented workarounds are a bug you've pushed onto customers. `orn` should page only when stdout is a terminal. Nobody should have to set an env var to stop a hang.

## 1. Terminal detection (fixes the CI hangs)

| Condition | Behavior |
|---|---|
| stdin is not a TTY | Never prompt. If confirmation is needed and `--yes` is absent, exit **6** immediately. |
| stdout is not a TTY | Never page. No spinner, no ANSI color, no cursor control. Progress is plain lines on stderr. |
| `NO_COLOR` set | No color. |
| `--no-pager` or `--no-input` | Force the above even on a TTY. |

The non-interactive error for the prompt in your report:

```
$ orn deploy api-gateway --env production < /dev/null
error: confirmation required to deploy api-gateway to production.
Not running in a terminal, so I can't ask.
Re-run with --yes to confirm:  orn deploy api-gateway --env production --yes
```

Optional guard for production: `--confirm api-gateway` takes the service name instead of a blanket yes. Agents tend to append `--yes` to everything, so a typed name is a stronger check.

## 2. `--json` on every command, with a stable contract

- `--json` goes on every command, starting with `deploy` and `deployments *`. It is not just on `services list` and `services get`.
- With `--json`, **stdout contains exactly one JSON document**, either the result or an error envelope. All human text goes to stderr.
- Tables are for humans and carry no compatibility promise. Say so in the docs.
- The JSON schema is the contract. Fields are added, never renamed or removed within a major version. Every document carries `"schema_version": 1`.

**Deployment object**

```json
{
  "schema_version": 1,
  "id": "dep_8f3k2",
  "service": "api-gateway",
  "environment": "production",
  "state": "rolling_out",
  "terminal": false,
  "created_at": "2026-10-24T09:12:03Z",
  "updated_at": "2026-10-24T09:14:41Z",
  "url": "https://console.orrinfield.example/deployments/dep_8f3k2",
  "error": null,
  "poll_after_seconds": 10
}
```

- `state` is a documented enum: `queued`, `building`, `rolling_out`, `succeeded`, `failed`, `canceled`, `rolled_back`.
- `terminal` tells the caller when to stop polling, so nobody hard-codes the state list.
- `poll_after_seconds` is a hint that spares the state endpoint from tight polling loops.

**Error envelope** (non-zero exit, on stdout under `--json`)

```json
{
  "schema_version": 1,
  "error": {
    "code": "confirmation_required",
    "message": "Confirmation required to deploy api-gateway to production.",
    "hint": "Re-run with --yes.",
    "retryable": false,
    "docs": "https://docs.orrinfield.example/cli/errors#confirmation_required"
  }
}
```

- `code` is a stable machine string such as `auth.invalid_token`, `service.not_found`, `deploy.failed`, or `rate_limited`. Callers branch on `code`, never on `message`.
- `hint` holds the exact next command or fix.
- `retryable` tells an agent whether trying again can help.

## 3. Exit codes (replace "1 for everything")

| Code | Meaning |
|---|---|
| 0 | Success. |
| 1 | Unclassified error. |
| 2 | Usage error (bad flags or arguments). |
| 3 | Authentication or permission failure. |
| 4 | Not found (service, deployment). |
| 5 | Validation or conflict (including a deploy already in progress). |
| 6 | Confirmation required, non-interactive. |
| 7 | Deployment ended `failed`, `canceled`, or `rolled_back`. |
| 8 | Timed out waiting. The deployment is still running server-side. |
| 9 | Transient error, safe to retry (rate limit, 5xx, network). |

Document the table in `orn help exit-codes` and on the docs site. Exit 1 stays as the fallback, so existing `!= 0` checks still work.

## 4. Async deploys (2–10 min)

The deploy command becomes create, then optionally wait, using the deployment ID the API already returns immediately.

```
orn deploy <service> --env <env> [--yes] [--no-wait] [--timeout 15m] [--json]
orn deployments get  <id> [--json]
orn deployments wait <id> [--timeout 15m] [--json]
orn deployments cancel <id> [--json]
```

- **Default is to wait.** CI wants the exit code to reflect the outcome, so a green job means a live deploy. State changes print as plain lines on stderr, one per change, with no spinner. The final deployment document goes to stdout. Exit is 0 on `succeeded`, 7 on a failed terminal state, and 8 on timeout.
- **`--no-wait` returns the deployment object immediately** with exit 0 once the deploy is accepted.
- **Agents should use `--no-wait` and poll.** Claude Code's shell tool has its own timeout, shorter than a 10-minute deploy. The agent loop is `deploy --no-wait --json`, then `deployments get <id> --json` every `poll_after_seconds` until `terminal` is true. Put this loop in your agent docs.
- **`--timeout` is only about how long the CLI waits.** On timeout it prints the ID and `orn deployments wait <id>` as the way to resume. It does not cancel the deploy.
- **Retries must not double-deploy.** An agent or CI retry after a timeout can create a second deployment. Accept `--idempotency-key <key>`, passed through to the API. If the same service and environment already has a deployment in progress, return that deployment with a `deploy.already_in_progress` code and exit 5. The `--json` payload includes the existing ID.
- **Add `--dry-run`** (`orn deploy ... --dry-run --json`). It returns the plan (service, environment, image, diff summary) without creating anything. Agents can show it to their user before asking for `--yes`.

## 5. Agent-facing documentation

- Add `orn help agents`, or an `AGENTS.md` snippet customers can paste into their repo:
  - always use `--json`
  - never parse tables
  - the non-interactive rules from section 1
  - the exit-code table
  - the `--no-wait` and polling loop
- Put `--help` examples on `deploy` showing the CI form and the agent form.
- Add a GitHub Actions snippet to the docs, with no `PAGER` line:

```yaml
- run: orn deploy api-gateway --env production --yes --timeout 15m
  env:
    ORN_TOKEN: ${{ secrets.ORN_TOKEN }}
```

## 6. Rollout and compatibility

1. Ship the TTY fixes first, in a patch release. They only turn a hang into a fast failure, so nothing that worked can break.
2. Ship `--json`, the error envelope, exit codes, `--no-wait`, and `deployments *` in the next minor release. The new exit codes are a behavior change for scripts that tested `== 1`. List it prominently in the changelog.
3. Leave the human table output as it is for now. Once agents read JSON, your column tweaks stop mattering to them.

## 7. Tests (this is what keeps the contract from drifting)

- Run `orn deploy` with stdin closed and with `< /dev/null`, without `--yes`. Assert exit 6 within one second and no pager process.
- Run it with stdout piped. Assert no ANSI sequences and no pager.
- Snapshot the JSON schema for each command, and fail CI if a field is removed or renamed.
- Run each terminal state against a mocked state endpoint, and assert the exit code.
- Retry a deploy with the same `--idempotency-key` and assert a single deployment.

## Open questions

- Should `--yes` be enough for production, or do you want `--confirm <service>` required there?
- Does the API already support idempotency keys, or does the server side need work first?
- Do you want a streaming event output (`--json-events`, one JSON object per line) in addition to polling? I'd skip it for v1.