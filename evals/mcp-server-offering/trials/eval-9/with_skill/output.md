# Vestergaard Systems: MCP write-path exposure review

I applied the `mcp-server-offering` skill and its three references to what you described. I haven't seen your code, auth setup or audit logs, so each finding says what I'm assuming and how to check it. The questions I'd put to your team come at the end.

## Verdict

Your audience is the most demanding type the skill describes: unattended enterprise agent fleets behind the customer's own gateway, with a private registry mirror. For that audience the skill says server-side enforcement, attribution and audit matter most. You have a read-only switch and annotation hints. Those are the two weakest controls in the skill's taxonomy. The banks' question exposes the missing piece: **no server-side record ties a write to a specific agent, session and delegating principal.**

## Exposures, ranked

### 1. 🔴 Attribution and audit (what the banks asked about)

This is the skill's stage-2 gate ("zero unattributed writes, clean audit trail"). If you can't pass it, you shouldn't be offering write tools to these customers yet.

**What I suspect, to verify:** your writes are attributed to whatever credential reached the API. That is probably a shared API key or service account per bank, or per deployment. Behind a bank's gateway, every agent then looks like one caller.

**What each audit record needs:**
- The human or service principal who owns the delegation. In Cloudflare's WriteGuard model the human stays the principal, with no separate agent accounts.
- The agent or client identity, for example the gateway-supplied agent ID. Store it as claimed, and separately from the identity verified by the token.
- The session ID and a per-call request ID.
- Tool name and tool-surface version, with arguments scrubbed of secrets.
- Outcome, timestamp, and the idempotency key if there is one.

**How to build it:**
- Write it asynchronously so it adds no latency, and keep it immutable.
- Make request IDs correlatable with the bank's gateway logs. Their gateway will see calls you can't, and they'll want to join the two.
- Make audit write failures visible.
- Issue one credential per agent or workload, not per bank. If the bank's gateway collapses all agents into one upstream identity, only the bank's own logs can answer "who", and you can't fix that from your side.
- Don't forward the caller's bearer token to your API. The spec forbids it. Use token exchange so your upstream still sees a real principal.
- Consider letting banks pull their own audit trail, either through a log export or a read-only audit tool. A tool would count against the 5-15 tool budget.

**Honest limit:** undo and rollback are largely absent across the industry. For you, attribution and audit are the substitute for reversibility. Tell the two banks that plainly rather than implying writes can be undone.

### 2. 🔴 `READ_ONLY=true` is a deployment flag, not an enforced boundary

Four gaps, in order of severity:

1. **It's unverified.** The skill's own cautionary example is GitHub issue #2156, where the read-only flag failed to omit write tools in some configurations.
   - Test the actual behaviour. Call `tools/list` with the flag on, then try to call each write tool by name directly. Test every config combination, including any toolset selection and per-request overrides.
   - Run this as a CI test, not a one-off.
2. **It's global.** An env var applies to the whole process or deployment. If your server is multi-tenant, you either lock everyone down or no one. A bank can't say "this agent is read-only, that one can write."
   - The right unit is the credential. A scoped, read-only credential cannot write even if the server registers write tools.
3. **It may only hide tools.** If the same credential can still write at the API layer, the flag removes a convenience and not the capability. Check where enforcement actually happens.
4. **Who controls it?** If it's a server config, the bank's platform team may not control it. If a client can toggle it, it's not a control.

**Fix:** scoped and restricted credentials come first. The skill ranks them top for efficiency and notes they are near-zero friction once issued. Keep the flag as a lockdown layer on top, once it's verified.

### 3. 🟠 `readOnlyHint` is advisory, and some clients treat it as authorization

- The skill is explicit: annotations are hints, never security controls. Enforcement belongs server-side.
- Some clients now act on the hint. Goose's smart mode uses it to auto-approve low-risk calls. A bank gateway might do the same. A wrongly marked tool then runs without review.
- Audit the annotations:
  - Is every tool that sets the hint truly side-effect free?
  - Do any "read" tools mark items read, trigger exports, refresh caches or send notifications?
  - Per the skill, a tool that both reads and irreversibly writes is two tools.
- Check the unmarked tools too. Per the MCP spec defaults, an unset `readOnlyHint` is treated as not read-only and an unset `destructiveHint` as potentially destructive, but make sure the destructive and idempotent hints are set honestly on the write tools.

### 4. 🟠 Human approval can't be your control for overnight agents

- Your write controls today appear to be binary: the write tools exist or they don't.
- With nobody present at night, client-side confirmation prompts and elicitation don't work. They also fail the skill's central test: a user or operator can bypass them by switching clients.
- The skill's starved option, risk-tiered server-side policy gates, is the answer. It gets promoted the moment background agents run unattended. That is your situation now.
- Classify every tool into exactly one of four tiers:
  - Read Only and Minimal Impact: pass through.
  - Contained Write: attribute and audit.
  - Critical: block before the handler runs, disabled by default.
- For anything that needs a human, use durable approval waits. The call parks until a person approves in the morning and doesn't block the overnight run.
- Cloudflare built its tiers after an unattended agent closed thousands of tickets. Ask yourselves what the worst loop would do to a bank's data.

### 5. 🟠 No idempotency, dry-run or spend caps (if absent)

- Unattended agents retry. A gateway timeout leads to a retry, and a retry becomes a duplicate write.
- Add idempotency keys on every write.
- Add per-credential rate limits and spend caps on any financially consequential tool. See `api-rate-limit-policy` for the throttle model.
- Add `dry_run` on destructive tools where feasible. It's rare in the ecosystem, but it is the cheapest preview a bank's risk team can approve. Where dry-run isn't feasible, keep the tool behind an approval gate.

### 6. 🟠 Auth posture (unknown, and it decides a lot)

- An env-var feature switch suggests a local or config-driven deployment. Enterprise agent fleets consume hosted endpoints, so local stdio is ruled out for this audience.
- For a remote server, check against the spec's MUSTs:
  - Is the server an OAuth 2.1 resource server?
  - Does it publish protected-resource metadata (RFC 9728)?
  - Does it validate resource indicators and the token audience (RFC 8707)?
  - Does it validate the issuer (RFC 9207, per the 2026-07-28 revision)?
  - Is the design stateless, with instances interchangeable behind a plain load balancer?
- Attribution (item 1) depends on this. Per-agent identity requires real OAuth clients or tokens, not a shared key.

### 7. 🟠 The registry mirror turns your metadata into policy input

Banks mirror your entry into an allowlisted catalog, and machines then apply policy to it. That creates three risks:

- **Stale or inaccurate metadata.** Keep the registry entry accurate: declare the env var, the auth requirements, and which tools exist in which version.
- **Silent surface drift.** A description edit changes which tools models pick. A new write tool changes what the bank approved. Ship both through code-review gates. Hash the full surface (names, descriptions, schemas), run golden-prompt CI tests, add a version marker in the response envelope, and log it. Use a 90-day deprecation window and alias old names instead of renaming.
- **Overclaiming.** The official registry is a metadata catalog with namespace ownership proof. It certifies nothing about security. Don't use a listing as a trust claim to the banks.
- If a bank's approval is pinned to a version, adding write tools in that version will break their allowlist or bypass their review. Make write expansion explicit and visible in the version history.

### 8. 🟢 Measurement gaps (lower urgency)

- Instrument calls as OpenTelemetry spans (session, tool call, downstream operation). The banks' own observability stack is the audience for this data.
- Track the converged metric set: call volume, error rate, per-tool use, active users and client distribution.
- Registry downloads are install interest, not runtime usage. Don't use them as an adoption figure.

## Skill gates: where you likely stand

| Gate | Likely status | Why |
|---|---|---|
| Safety coverage | ❌ Probably fails | A write tool has no tier or named pattern except the lockdown flag, and I can't tell if irreversible tools are gated or disabled. |
| Auth conformance | ❓ Unknown | Needs the answers below. |
| Stage-2 gate (zero unattributed writes) | ❌ Not met | Attribution is the open gap. |
| Curation (5-15 tools) | ❓ Unknown | Need the tool count. |
| Evidence hygiene | Not applicable yet | Applies when you write the business case. |

## Order of work

1. **This week:** write the lockdown test described in item 2, and audit every tool's annotations (item 3).
2. **Attribution:** define the audit record, per-agent credentials and request-ID correlation (item 1). This answers the two banks.
3. **Scoped read-only credentials**, then tier every tool and disable or gate Critical tools (items 2 and 4).
4. **Idempotency keys, rate and spend caps, dry-run** (item 5).
5. **Registry and versioning hygiene:** surface hash, golden-prompt CI, and an accurate registry entry (item 7).
6. **Until step 2 ships**, consider offering read-only credentials to every bank. That is the skill's stage 1, and your reads are already in good shape.

The "who performed this write" reply to the two banks should wait for step 2. Until then, tell them which credential and gateway identity you can show, not a named agent.

## Questions I need answered

Answers to these would change the findings above:

1. How are writes authenticated today: a shared API key, a per-user OAuth token, or a service account? What does the current audit log record for a write?
2. Is the server remote or local? Is it multi-tenant? Who sets `READ_ONLY`?
3. Which tools write, and which of those are irreversible, financial, or send messages to people?
4. How many tools are there? Do any combine reading and writing?
5. Does your server currently speak OAuth 2.1 with audience validation, or does it use static credentials?
6. Do the two banks need proof of attribution by a date, and do any RFPs require it? A hard deadline pushes you toward managed hosting and a read-only launch first.