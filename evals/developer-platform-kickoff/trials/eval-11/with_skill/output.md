# Coppermill Inventory: where to point your team

**Next action:** start `api-error-design` this week. All three signals depend on it: the agent-reconciliation request, the MCP question and the unusable-SDK complaint. An agent can only recover from errors it can parse, and today's `bad request` gives it nothing to parse.

ℹ️ This was a single-shot run, so I didn't run the tap interview. I filled in answers from your message and marked each one. Correct any ⚠️ item and I'll re-rank.

## Detection and assumptions

- **Start type:** cold. No `developer-platform-context.md` exists. I didn't write one into this repo, which is example-repo and not Coppermill. The proposed file is at the bottom.
- **Q1, who integrates:** (a) customers' own engineers, plus (d) AI agents acting on customer data. Both come from your message. No third-party app builders are mentioned.
- **Q2, session goal:** pick where the team's effort goes, given the agent demand, the MCP question and the SDK complaint.
- **Q3, published surfaces:** a REST API and an SDK, both live. ⚠️ I don't know whether a spec (OpenAPI) is committed, whether a compatibility promise exists, or whether there is a CLI. There is no MCP.
- **Q4, contract owner and breaking-change signer:** ⚠️ unknown. This is the one answer that could reorder the list (see Not now).
- **Q5, constraints:** agents arrive "next year", so no hard date yet. ⚠️ Capacity is unknown.
- **Q6, horizon and effort ceiling:** ⚠️ unknown. I assumed a standing effort with modest engineering capacity.
- **Q7, already decided:** nothing.

## Route

**Route to `api-error-design`.**

It covers a machine-readable error-code taxonomy, the RFC 9457 problem-details envelope, actionable messages and retryability signalling. It is a better fit than `public-api-design-review` because the problem is already named. You don't need an audit to learn that the errors are bare strings.

**Re-rank, stated out loud:**
- AI agents (Q1d) promote `mcp-server-offering` to rung 2 and pull `api-error-design` up with it.
- Customers' own engineers only (Q1a) delete third-party app execution and `oauth2-provider-design`. Nobody is building apps that act on your users' behalf, so they are gone from this plan.
- An existing REST API (Q3) keeps the surface audit at rung 1.

## Short-list

Ordered by value per unit of effort, highest first.

1. **`public-api-design-review`**
   - **Attacks:** the question of what else is wrong beyond error bodies. It gives a named, evidenced list for `bad request` and for any similar problems in naming, pagination or field consistency.
   - **Cost:** one session over the existing surface. There is no deploy, no sign-off and nothing to roll back.
2. **`api-reference-quality`**
   - **Attacks:** undocumented endpoints, parameters, response codes and errors. It also sets up CI gates so the reference stops drifting.
   - **Cost:** nearly free if an OpenAPI file is committed. It is useful only after the error contract exists, because it has to document those errors.
3. **`api-error-design`**
   - **Attacks:** the `bad request` problem, and it is the prerequisite for the agent story.
   - **Cost:** one design session, then a backend change per endpoint class. The change is additive.
4. **`mcp-server-offering`**
   - **Attacks:** the account that asked whether you have "an MCP thing". It sizes the build, picks a curated 5-15 workflow-tool set for reconciliation, and covers write safety and remote hosting with OAuth 2.1.
   - **Cost:** a new surface with its own versioning, limits and on-call. Run it after the error contract, and let that question decide how big the build is.
5. **`api-idempotency-retry`**
   - **Attacks:** an agent retrying a reconciliation write and doing it twice. If agents only read stock, this drops down.
   - **Cost:** a design session plus an idempotency-key store and replay window.
6. **`api-auth-key-management`**
   - **Attacks:** giving an unattended agent a least-privilege, read-only or scoped key with clean rotation and offboarding, instead of a full-access key.
   - **Cost:** a policy session plus credential-store work and a rotation path.
7. **`api-rate-limit-policy`**
   - **Attacks:** an agent reconciliation loop turning into a noisy neighbour. It publishes quota numbers, headers and the 429/`Retry-After` contract.
   - **Cost:** a policy session plus gateway configuration. A published limit can only be loosened afterwards, never tightened.

## Chain

Dependency order, not an efficiency ranking:

1. `public-api-design-review` hands `api-error-design` the list of inconsistent error shapes and fields.
2. `api-error-design` hands `api-idempotency-retry` the retryability signal that tells a client when it is safe to retry.
3. `api-idempotency-retry` hands `api-reference-quality` an error and retry contract that is finished and stable enough to document.
4. `mcp-server-offering` runs after step 2 and consumes the error contract. Its tools return those same errors, which is what lets an agent recover.

## Not now

- **`api-versioning-policy`**
  - Promoted to rung 1 if Q4 comes back empty, meaning nobody can say what counts as a breaking change or who signs it off.
  - Replacing `bad request` bodies changes responses integrators may already parse.
  - Unblocking condition: Q4 answered.
- **`webhook-platform-design`**
  - Push-based stock events would beat agents polling for changes.
  - Unblocking condition: the first agent customers report polling load or staleness.
- **`integration-error-observability`**
  - Per-key error rates and replayable logs for the agent customers.
  - Unblocking condition: key scoping from `api-auth-key-management` is in place, so errors can be attributed.
- **`developer-portal-design`**
  - Unblocking condition: key dashboard, logs and sandbox are being built and need a home.

I dropped the ecosystem-execution class and `oauth2-provider-design` entirely. They are ruled out by the audience and have no unblocking condition.

## Gap

The SDK complaint is not covered here: the README never names the auth environment variable, and the examples live on a docs site an agent can't reach. That is making an existing SDK usable by a coding agent unattended. No skill in `developer-platform-skills` covers it.

**Recommendation:** install `samber/developer-relations-skills` and use `coding-agent-docs-optimization`. It is the sibling that documents an existing SDK for agent consumption, and it is a different job from `mcp-server-offering`, which builds a new agent-facing tool surface. This is a recommendation only, since this collection works standalone.

You can do the fix before the skill if you want a quick win. Put the auth variable name and one complete runnable example in the README itself. That is hours of work, and it makes a coding agent usable with your SDK.

## Routines (dry-run only, nothing scheduled)

| Routine | Trigger | Output channel |
|---|---|---|
| Pre-release API design review (`public-api-design-review`) | Event: spec diff on a release candidate | Comment on the PR that carries the spec diff |
| Quarterly re-run of this kickoff | Calendar: once a quarter | Updated `developer-platform-context.md` plus a short summary in the team's platform channel |

Not installed yet:
- The deprecation sweep needs an announced sunset date.
- The reference-drift audit needs real spec churn.
- The fleet-health review needs a named owner for the follow-through.

If the harness has no scheduled routines, fall back to one recurring calendar reminder: "Platform check-in — re-run the developer platform kickoff".

## Proposed `developer-platform-context.md`

I did not write this file. It belongs in the Coppermill repo, and its contents need your corrections first.

```markdown
# Developer platform context — Coppermill Inventory

## Audience
Customers' own engineers; AI agents acting on customer data (2 large accounts, reconciliation, next year).

## Published surfaces
- REST API — compat promise: ? (open); version scheme: ? (open)
- SDK — language(s): ? (open)
- MCP — none

## Spec locations
? (open — OpenAPI committed?)

## Owners
Contract owner: ? | Breaking-change signer: ?

## In-flight work (2026-10-08)
- Error contract (api-error-design): starting
- Agent-readable SDK README: gap, see developer-relations-skills

## Decided / Open
Decided: none. Open: MCP scope; versioning policy; breaking-change signer.

## Constraints
Landing date: none stated (agents "next year"). Horizon: standing (assumed). Effort ceiling: ? (open).

## Stakeholders
Two large accounts (names held out of memory); engineer who reported the SDK problem.

## Session log
- 2026-10-08 — cold start. Route: api-error-design. Re-rank: AI agents.
```

## Memory

I wrote nothing to memory. If you want it kept, the default is a `memories/` directory in the Coppermill git repo, committed only after you approve the diff.

**Never put these in memory:**
- The two accounts' names tied to their API traffic.
- Keys, client secrets or signing keys.
- Negotiated terms.
- Unannounced sunset dates.
- Unpatched security findings.

## Pass-bar status

- ❌ The context artifact is not written to disk. It is inline above.
- ❌ The interview was not run interactively. The ⚠️ items are the unanswered ones.
- ✅ All other checks hold: every route is a name in the table, the routines have output channels, and the short-list is ordered by ratio with each re-rank stated.

## Questions for you

**Do you have a named breaking-change signer, and is an OpenAPI spec committed?** If the signer is missing, `api-versioning-policy` jumps to rung 1 ahead of everything above. If there's no spec, `public-api-design-review` moves up and `api-reference-quality` drops.