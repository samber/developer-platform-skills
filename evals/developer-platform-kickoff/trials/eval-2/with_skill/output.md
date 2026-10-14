# Developer platform kickoff: warm start, 2026-10-08

**Next action:** run `integration-error-observability` on the three silent partners. Before the session, pull the evidence listed under Route.

I took the project state from your message, not from a file. `developer-platform-context.md` is not in the working directory I ran in (`example-repo`), so I could not read it or patch it. The ready-to-paste update is at the end.

## 1. State summary

1. **Audience:** technology partners building for shared customers.
2. **Published surfaces:** REST v1 and outbound webhooks, both under a compatibility promise.
3. **In-flight work:** none recorded. You were away two sprints, and today's work is the silent-partner investigation.
4. **Top open decision:** whether partner apps get OAuth.
5. **Active constraints:**
   - SOC 2 Type II window closes in March, about 5 months out.
   - Standing work at a few hours a week.
   - Two-engineer ceiling.
   - Contract owner is Priya (platform). The breaking-change signer is the VP Eng, so a signer exists.

## 2. Route

**`samber/developer-platform-skills@integration-error-observability`**

- **Why it fits:** its scope covers alerting partners when their integration breaks and a provider-side fleet view. Silent partner breakage matches its "partners don't know their integration is broken" signal.
- **Altitude and side:** this is tactical work, and the decisions it needs already exist. You sit on the provider side.
- **Not routed to `api-error-design`:** that skill covers one response body. Not routed to `api-status-communication` either: that skill covers platform-wide health. Three partners going quiet is per-integration.

**Evidence to bring, collected from your own logs and gateway:**

- Each partner key's last successful call date and the response codes it received just before the stop.
- Whether any of the three keys were rotated, expired or revoked in that window.
- Any deploy, spec change or limit change dated near the stop.
- Whether their webhook subscriptions were still being delivered to or had been disabled.

**Two things to settle in the session:**

- **Attribution.** You can only find the cause if you can attribute calls to a partner key. If the keys are shared or unscoped, `api-auth-key-management` runs first (see the chain).
- **Follow-through.** A fleet view is only useful if a named person contacts the partner it flags. Decide who that is.

## 3. Short-list

Ordered by value per unit of effort.

1. **`integration-error-observability`**
   - **Attacks:** partners breaking silently, which your own error rate cannot show.
   - **Cost:** a session of 2–3 hours. The log store and alerting need real engineering from your two engineers. Payload retention needs a SOC 2 retention basis.
   - **Re-rank:** it moved up from class 4 because partners are the audience (Q1b) and it is today's goal.
2. **`public-api-design-review`**
   - **Attacks:** inconsistent status codes, error shapes and Hyrum's-Law risk in REST v1. Any of these could have made a partner client misread failures.
   - **Cost:** one session over the existing spec. It needs no deploy and no sign-off.
3. **`api-reference-quality`**
   - **Attacks:** undocumented operations and error responses that partners had to guess at.
   - **Cost:** near zero if an OpenAPI spec is committed. If none exists, step 2 comes first.
4. **`api-error-design`**
   - **Attacks:** errors a partner cannot read or retry correctly. They produce silent drop-off and support tickets.
   - **Cost:** a design session plus an additive change per endpoint class. It ships behind responses already published.
5. **`api-auth-key-management`**
   - **Attacks:** key lifecycle and scoping, and the unresolved "keys or OAuth?" question, which this skill owns.
   - **Cost:** a policy session plus credential-store and rotation work, which needs a control owner for SOC 2.
   - **Re-rank:** the SOC 2 window (Q5c) moved it up. Its answer unblocks your top open decision.
6. **`api-rate-limit-policy`**
   - **Attacks:** undocumented limits or 429 behaviour that can stop a partner without a visible error.
   - **Cost:** a policy session plus gateway configuration. A published limit can only be loosened later, so get it right first time.
   - **Re-rank:** the SOC 2 window (Q5c) moved it up.
7. **`integration-partnership-strategy`**
   - **Attacks:** deciding which partners deserve depth and attention from demand data, not from whoever shouts loudest.
   - **Cost:** coordination with product and sales. It ships no code, so the two-engineer ceiling does not limit it.
   - **Re-rank:** the partner audience (Q1b) promoted it.

**Removed because of your answers:**

- The two-engineer ceiling (Q5d) removed second surfaces and specialist protocol surfaces. They are under "Not now".
- A partner audience removed `oauth2-provider-design` as a prerequisite. A third-party app builder ecosystem (Q1c) would have made it one, and that is not your audience.

## 4. Chain

Run this chain only if the first link shows you cannot attribute calls to a partner. Otherwise run link 3 alone.

1. **`api-auth-key-management`** hands the next link a per-partner identity (a scoped, attributable key).
2. **`api-rate-limit-policy`** hands the next link limits expressed per that identity.
3. **`integration-error-observability`** splits error rates and alerts by that identity.

## 5. Not now

- **`oauth2-provider-design`**: unblocked when `api-auth-key-management` returns an "OAuth needed" verdict for partner apps. The SOC 2 window promotes this skill, but the open decision gates it. If the verdict is yes, start soon: the consent screen and scope taxonomy each need a data-protection review before March.
- **`api-versioning-policy`**: unblocked if triage shows a change broke the three partners, or if you announce a sunset. A signer already exists, so it does not jump to rung 1.
- **`webhook-platform-design`, `sdk-portfolio-strategy`, `developer-portal-design`, `public-graphql-api-design`, `public-grpc-api-design`, `sql-jdbc-access-design`, `bulk-data-sharing-design`, `mcp-server-offering`**: unblocked when engineering capacity exceeds two engineers, or after the March SOC 2 window.
- **`api-test-mode-design`, `api-status-communication`**: unblocked once the observability work has shipped.
- **`partner-app-onboarding`, `integration-listing-optimization` and the four `app-marketplace-*` skills**: unblocked once the OAuth decision lands and `integration-partnership-strategy` names the partner set.

## 6. Gap

The collection has no skill for the root-cause investigation of these three partners. That is an incident dig through your own logs. `integration-error-observability` builds the visibility that would have caught it, but it does not diagnose these three after the fact.

Its coverage gap also names deployed-integration health monitoring: version drift and deprecated-API usage across the fleet. If the cause turns out to be partners stuck on old clients, the collection has no skill for tracking that. Win-back outreach to the three partners is partner management, which no skill here covers.

## 7. Routines (dry-run, nothing scheduled)

A harness with scheduled routines would show these first. They rank by value per unit of effort, and I re-ranked for your answers.

1. **Pre-release API design review** → `public-api-design-review`.
   - **Trigger:** a spec diff on REST v1.
   - **Output channel:** a review comment on the pull request that carries the diff, in your git host.
   - **Cost:** attention only when a diff exists.
2. **Quarterly kickoff re-invocation** → `developer-platform-kickoff`.
   - **Cadence:** quarterly, matched to the project's pace. A standing, few-hours-a-week project suits a quarterly cadence.
   - **Output channel:** a patched `developer-platform-context.md` plus a summary to the platform channel.
3. **Integration fleet-health review** → `integration-error-observability`. Install it only once someone owns partner follow-through.
   - **Re-rank:** the partner audience (Q1b) places it above the deprecation sweep.
   - **Compliance cost:** the output names partners and their traffic. The channel must be covered by your data policy and SOC 2 scope, so use a restricted channel and never a public one.

Not proposed:

- The deprecation sweep, until you announce a sunset date.
- The reference-drift audit, until spec churn is real. With your capacity ceiling it would be quarterly anyway.
- The listing defend cycle, because no live listing exists.

If your harness has no routines, use one calendar reminder: "Platform check-in: re-run the developer platform kickoff."

## 8. Update to `developer-platform-context.md`

Paste this into your repo's file. Add the dated task section, patch the constraints and append the log line. The artifact is committed, so it must not contain partner or customer names tied to their API traffic. Refer to "three partners" and nothing more.

```markdown
## Current task (2026-10-08)
- Goal: find out why three partners stopped calling the API in September 2026.
- Route: integration-error-observability.
- Evidence to gather: last successful call and final response codes per partner key;
  key rotation or revocation in the window; deploys or spec changes near the stop;
  webhook delivery status for the same partners.
- Open sub-question: can calls be attributed to a partner key? If not, run
  api-auth-key-management first.
- Owner for partner follow-through: TBD.

## Constraints (patch)
- Compliance: SOC 2 Type II window closes March 2027.
- Horizon: standing, a few hours per week.
- Effort ceiling: two engineers.

## Session log
- 2026-10-08: warm start after two sprints away. Session goal: three silent partners.
  Routed to integration-error-observability. Short-list re-ranked: partner audience,
  SOC 2 window and capacity ceiling. Second and specialist surfaces moved to not-now.
  OAuth for partner apps stays open, gated on api-auth-key-management.
```

I wrote no memory entry. If you add one, derive it from this file, and keep out partner names tied to traffic, keys and secrets, negotiated terms, unannounced sunset dates and unpatched security findings. If memory goes into the git repo, review the diff before committing.

**Pass-bar status:**

- **Met:** routes match declared scopes, no skill name falls outside the table, the interview stayed within the warm-start limit, and both the short-list and routines are ordered by value per effort with their re-ranks stated.
- **Not met:** the context file update (bar item 4) is unwritten because I could not reach that repo. Paste the block above to close it.