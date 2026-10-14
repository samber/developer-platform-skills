I did not inspect your server code. This repo is not the Vestergaard codebase, and I didn't touch `skill-wip/`. This is a threat-model answer from how MCP, gateways, and registry mirroring behave, so each item has a check you can run against your code.

## Verdict

The two banks' question exposes your biggest gap. Read-only support is a configuration switch, so it stops writes only on deployments that are correctly configured. Nothing in your setup yet proves who made a write.

## 1. No attributable write identity (🔴, the banks' question)

You probably cannot answer "who performed this write" today, for four reasons:

- **Shared credential.** Your server most likely calls your backend with one service credential per deployment. Your backend's audit log then says "the Vestergaard MCP service account" for every write, from every agent and human.
- **Gateway identity.** Behind the bank's MCP gateway, your server sees the gateway's identity, not the agent or the person who delegated to it. Per-bank API keys give the same result: you can say which bank, but not which actor.
- **Self-asserted fields.** MCP `clientInfo` and session IDs are not identities. Anyone can spoof them, and an auditor will reject them.
- **No attribution chain.** Overnight runs have no human in the loop. The bank needs the chain: agent run ID → delegating principal → gateway → your tool call → your backend write.

Fixes, in order:

1. **Per-request principal.** Accept an OAuth 2.1 bearer token on every call, bound to your server's audience (RFC 8707). Take `sub` plus an actor claim (`act`) from it: `sub` is the human or service who delegated, `act` is the agent.
2. **No token passthrough.** The MCP authorization spec forbids passing the client's token to your backend, which is the confused-deputy problem. Use token exchange (RFC 8693) so the backend receives an identity that carries the actor.
3. **Backend records the actor.** Add a `performed_by` / `on_behalf_of` field on every mutation in your backend, not just in the MCP layer. An MCP-only log can be bypassed and is weak evidence.
4. **Server-side audit record per tool call.** Log it for allowed calls and for denied ones:
   - timestamp
   - tenant
   - subject and actor
   - gateway or client ID
   - tool name
   - SHA-256 of the arguments (plus the arguments themselves, redacted)
   - result status
   - resource IDs touched
   - `READ_ONLY` state
   - server version and tool-manifest hash
   - the incoming `traceparent` / request ID, so the bank can join your log to its gateway log
5. **Tamper-evident export.** Use append-only storage with a defined retention period, and export to the bank's SIEM (OTLP or a structured JSON stream).
6. **Idempotency keys on writes.** Overnight retries otherwise produce duplicate writes that muddy the audit trail. Record the key in the audit entry.

Check: run one write through a test gateway and ask "who did this?" using only your backend's records. If the answer is a service account, the gap is confirmed.

## 2. `READ_ONLY=true` is a deployment setting, not a guarantee (🟠)

- **Unverifiable.** The operator who starts the process controls the variable, and a bank cannot confirm from outside that it was set. A restart with the wrong env, or a copied config, silently re-enables writes.
- **Wrong layer.** It removes tools from the list, but the credential behind them may still hold write scope. Enforce read-only in the credential, not in the process.
- **Default matters.** If the default is `false`, one forgotten variable gives write access. Writes should be opt-in.
- **Other write paths.** Check that `tools/call` for a skipped tool name is rejected, since handlers kept in a dispatch map can stay callable. Also check for:
  - tools registered later via `listChanged`
  - generic "run query" or "call API" proxy tools
  - long-running or task-style operations
  - resources or prompts with side effects
- **Process-wide only.** One flag cannot express "agent A may write, agent B may not".

Fixes:

- Issue read-only-scoped tokens and enforce scope at the backend, so the token decides.
- Ship a separate registry entry for the read-only build, for example `vestergaard-readonly`, with no write code path. Banks allowlist by entry, so their allowlist then enforces the policy for them.
- Put the `READ_ONLY` state in startup logs and in every audit record.
- Add a test that starts the server with `READ_ONLY=true`, lists tools, calls every known write tool name directly, and asserts rejection.

## 3. `readOnlyHint` is advisory, and your gateways may rely on it (🟠)

- The MCP spec says clients must treat annotations as untrusted unless the server is trusted. A bank gateway that auto-approves tools hinted read-only is trusting a label that nobody verifies. A wrong label means a write passes as a read.
- The hint covers more than "doesn't change data". Review every hinted tool for hidden side effects:
  - mark-as-read or last-seen updates
  - export or report jobs
  - token or URL creation
  - quota consumption
  - cache writes
  - outbound fetches (SSRF, `openWorldHint`)
- Read tools still leak data. In an unattended agent, prompt injection in returned content can steer later calls, which is why the write controls above matter.
- Spec defaults treat unannotated tools as non-read-only and destructive, which is the safe direction. Keep it that way, and never infer safety from a missing annotation.

Fix: add a CI contract test that every tool hinted `readOnlyHint: true` calls only non-mutating backend endpoints, and that every tool registered under `READ_ONLY` has the hint. Annotations should be derived from the same scope table the backend enforces, not hand-set.

## 4. Registry mirroring and allowlist drift (🟠)

- **Silent surface changes.** The bank approves a snapshot of your entry. If a later version adds a write tool or changes a tool description (a tool-poisoning vector), the allowlist may not notice. Publish a per-version tool manifest (names, schemas, descriptions, annotations, hash), and treat a new write tool as a major version.
- **Provenance.** Banks will want:
  - immutable versions
  - signed artifacts with pinned digests
  - an SBOM
  - build attestation
  - a check that the registry metadata matches what the binary actually does
- **Config surface.** Document in the registry entry every env var that changes security behavior (`READ_ONLY`, auth settings, endpoints). The mirrored entry is what the bank's platform team reviews, so omissions there become approved blind spots.
- **Transport.** If the stdio package can run unauthenticated, document that it is not for unattended bank use. Prefer the authenticated remote (streamable HTTP) path for these customers.

## 5. Unattended, overnight operation (🟡)

- No human approves destructive calls, and elicitation has nobody to answer it.
- Add per-principal rate limits and change budgets (maximum writes per run).
- Add a dry-run mode for writes.
- Add a kill switch the bank can use to revoke a principal quickly.
- Keep destructive operations behind a separate scope that unattended agents never receive by default.

## Priority order

1. Per-request actor identity plus backend `performed_by` (answers the two banks directly).
2. Server-side audit records with gateway correlation IDs.
3. Scoped read-only tokens, a separate read-only registry entry, and writes off by default.
4. A tool manifest per version, plus the hint-versus-behavior CI test.
5. Idempotency keys, rate limits, and write budgets.

For the banks now, send a short statement of what you can and cannot attribute today, and a date for the fix. Don't claim attribution you can't produce.

## Questions that change the plan

- Does your backend already record an actor on mutations, or only the calling credential?
- Is your server remote (HTTP) or local (stdio) for these banks, and do you already accept OAuth tokens?
- Is the `READ_ONLY` default `true` or `false`?