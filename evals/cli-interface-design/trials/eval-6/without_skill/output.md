# Harrowgate Mail CLI: agent-ready spec and launch-post guidance

I changed no code. The `hgm` source isn't in this repo, so this is a spec you can build from, plus the post guidance. Nothing below has been run or compiled.

## 1. The three incidents share one cause

The CLI trusts its caller. It assumes a human is at a terminal, that the raw escape hatch needs no guardrails, and that file arguments are honest. Agents break all three assumptions.

| Incident | Root cause | Fix |
|---|---|---|
| Stuck on type-the-domain prompt; customer asks for global `--yes` | Prompt blocks on stdin and has no machine path | Two-step confirm with a preview (§2). **Reject the global `--yes`.** |
| `hgm api delete /v1/domains/dom_7f21` ran instantly and emailed 40 senders | Guard lives in the curated command only. The escape hatch and the server have none. | Server-enforced confirmation, plus fail-closed classification in `hgm api` (§3) |
| `--template ../../.ssh/id_rsa` | No path validation. A private key was about to be uploaded to our API. | Confined file reads (§4) |

**Why not a global `--yes`:** it turns every guard into a flag the agent adds on its first retry. The agent gets unstuck, but only by skipping the check. The customer's real need is that agents don't hang and can still finish legitimate work. §2 delivers that.

## 2. Confirmation without prompts

Rules for every command:

- Never block on stdin when stdin or stdout isn't a TTY, or when `HGM_NO_INPUT=1`. Fail fast instead.
- Human on a TTY: unchanged. They still type the domain name.
- Non-interactive destructive command: exit with code `10` (`confirmation_required`) and print a JSON error on stderr. The error tells the agent exactly what to run next.

Flow:

```
$ hgm domains delete dom_7f21 --dry-run
{
  "action": "domains.delete",
  "target": {"id": "dom_7f21", "name": "mail.acme-corp.example"},
  "reversible": false,
  "side_effects": [
    {"kind": "email", "recipients": 40,
     "description": "'domain removed' notice to verified senders"}
  ],
  "confirm_token": "cfm_…",
  "expires_in_s": 300
}

$ hgm domains delete dom_7f21 --confirm cfm_…      # **deletes the domain, emails 40 senders**
```

- The token is bound to API key, method, path, and a hash of the impact preview.
- If impact changes between preview and confirm (for example, the sender count), the token is invalid.
- A 300 s TTL is a reasonable starting point: long enough for an agent to relay the preview to its user, short enough to prevent replay. Tune it.
- The preview resolves the ID to the name and lists side effects, so the agent and its user see what the delete really does. The `dom_7f21` incident came from an agent acting on an opaque ID.
- The agent can show the preview to its user. That is the human-in-the-loop step a `--yes` would remove.

Further controls:

- **Restricted API keys (server-side).** Customers can issue agent keys without `domains:delete` and similar scopes. This is the real answer to "let my agent do X but not Y," and nothing in the CLI can be flagged around it. Default new keys created via `hgm login --for-agent` to non-destructive scopes.
- **Side-effect notices (product decision).** Soft-delete domains with a grace period, and send the "domain removed" email when the grace period ends, not at request time. Alternatively, make the notice opt-in. This also helps humans, and it follows your own soft-delete convention for user-owned resources.
- **Remediation for the incident already in the field.** Ask the affected customer whether the 40 senders need a correction notice. Check whether the domain can be restored.

## 3. Close the `hgm api` bypass

The guard must be on the server, because `curl` bypasses any CLI check. `hgm api` then needs fail-closed behaviour on top.

**Server**
- Every endpoint annotated in the OpenAPI spec with `x-hgm-destructive` and `x-hgm-side-effects`.
- Unannotated `DELETE` endpoints default to destructive.
- Destructive calls without a valid `X-Hgm-Confirm` token return `428` with the same preview body as §2. Success is then only possible after a preview.

**CLI**
- `hgm api` reads the same annotations and honours `--dry-run`. It surfaces a `428` as exit code `10` with the identical JSON.
- Normalize method case (`delete` and `DELETE`).
- Accept only paths matching `^/v1/[A-Za-z0-9_./-]+$`.
- Reject `..`, `%2e`, `%2f`, `?`, `#`, CR/LF, and `//` in path segments. Pass query and body through separate flags.
- Add `hgm api --list` and `hgm schema <command>` so agents discover endpoints instead of guessing paths.

## 4. File arguments (`--template` and any other path flag)

Reading `../../.ssh/id_rsa` into an upload is exfiltration, not just a bug. Layered checks:

1. **Confine** reads to the working directory, or to an explicit `--allow-dir`. Resolve symlinks. A lexical `..` check alone is not enough.
2. **Allowlist** extensions (`.html`, `.mjml`, `.hbs`, `.txt`).
3. **Cap size** (for example 1 MiB; pick from your template limits).
4. **Require valid UTF-8 text** that parses as a template.
5. **Deny sensitive locations** as defense in depth: `~/.ssh`, `~/.aws`, `.env*`, `.git`.
6. **Echo** path, size, and SHA-256 in `--dry-run` output.
7. Support `-` for stdin, so agents have a safe route that needs no path.

If the CLI is Go 1.24+, `os.OpenRoot` gives (1) for free, including symlink escapes:

```go
// Sketch, not compiled. Confines reads to dir; ".." and escaping symlinks fail.
root, err := os.OpenRoot(dir)
if err != nil { return err }
defer root.Close()
f, err := root.Open(rel) // rel must be relative; reject absolute paths up front
```

Tests to write first (pivot values):
- `../x`, an absolute path, and an empty string.
- A symlink to `/etc/passwd`, and a symlink pointing inside the directory.
- A 0-byte file, a file of exactly the cap, and a file of cap + 1.
- A binary file and a `.pem` file.
- `%2e%2e/` in `hgm api` paths.

After they pass, temporarily remove each check and confirm the matching test fails.

## 5. Other agent-ready basics

- JSON output by default when not a TTY. Stable schema, versioned. Add `--fields` to trim output.
- Errors as JSON on stderr with `code`, `message`, `hint`, `next_command`. Documented exit codes (`0` ok, `2` usage, `3` auth, `10` confirmation required, and so on).
- No spinners or colour when not a TTY.
- Auth via `HGM_API_KEY` only, and never an interactive prompt. Offer a device-code login for humans.
- `--dry-run` on every mutation. `--idempotency-key` on sends.
- `--limit` and `--page-all` on lists.
- Ship a skill or `AGENTS.md` snippet through `hgm skills install`. It should state the preview, confirm, and key-scope rules.
- Treat message and event content from third parties as untrusted. Mark it in output so agents don't follow instructions embedded in an email body.

## 6. The launch post

**Do not publish "MCP costs 4-32x more tokens" or "MCP eats 55k tokens" as written.** I can't verify either figure, and neither can the reader, as written. Problems:

- **No stated basis.** Which MCP server (yours or a generic one)? Which client, model, and tokenizer? Which tasks? A 4-32x spread suggests several scenarios were folded together.
- **55k describes one configuration.** Tool-definition overhead scales with the number of tools loaded. Clients increasingly defer or lazy-load tool schemas, so the figure may already be stale for current clients.
- **Tokens are not cost.** Cached input is billed far below fresh input, so a token ratio can overstate the cost difference.
- **The CLI has costs too.** `--help` discovery, verbose output, and retries all count. Failed attempts count against success rate.
- **Timing.** Your last two weeks of incidents show MCP-style tools get client-side approval and destructive-action annotations that your CLI currently lacks. A post attacking MCP before §2-§4 ship invites a reply thread listing those incidents.

**Measure, then publish.**
1. Fix a task set of 8-10 real jobs, for example: send a test email, add a domain and fetch its DNS records, upload a template, list yesterday's bounces, rotate a key.
2. Same model and client version for both arms. Compare `hgm` against your own MCP server, or drop the MCP comparison.
3. Record API usage counts (input, cached input, output) for the whole task, including schema load and `--help` calls. 10+ runs per task.
4. Report the median and range per task, plus task success rate and cost, not tokens alone.
5. Publish the harness and raw data with the client, model, and date. The post's credibility comes from reproducibility.

**Claim shapes that are safe now (no numbers needed):**
- "A CLI loads nothing until the agent runs a command. You pay tokens only for what you use."
- "`hgm` is built for agents: JSON output, dry-run on every mutation, previewed confirmations, scoped keys."

**Template once you have data** (fill every blank from your harness, or cut the sentence):
- "On [N] tasks with [model] in [client + version], completing the job took a median of [X] tokens through `hgm` versus [Y] through [the Harrowgate MCP server]. Range [a-b]x. Harness and raw runs: [link]."
- "[Server]'s tool definitions measure [N] tokens in [client + version] as of [date]."

**Ask marketing** where 4-32x and 55k came from. If they came from a third-party benchmark, cite it and name the server it measured, or drop them.

**Order of work:** ship §2-§4 first, run the benchmark in parallel, then publish. The post can also describe the safety model (preview, confirm, scoped keys), which is more differentiating than the token claim.

Point me at the `hgm` repo and I can implement §2-§4 with the tests above.