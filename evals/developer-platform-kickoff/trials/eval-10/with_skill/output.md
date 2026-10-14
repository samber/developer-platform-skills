⚠️ **Check the date first.** Today is 2026-10-08, and 6 November is about 4 weeks away, not 11. The plan below uses your 11 weeks, and § 8 gives a 4-week cut. Tell me which is right.

## 1. Route

The routing result is `public-api-design-review`, run in week 1.

- **Why this skill:** the 90-endpoint spec is not published yet, so this is the last cheap moment to fix it. After GA, every field and status code becomes something integrators depend on.
- **The partner and marketplace questions:** none of those skills fits this window. They go in a separate, near-zero-engineering track (§ 5).

I assumed answers where I couldn't ask. I'm printing the questions here instead of asking them one at a time. Correct any wrong assumption, because it changes the ranking.

- **Audience:** the three design partners plus customer engineers. No third-party app builders.
- **Published surfaces:** none. GA is the first compatibility promise.
- **Decided:** REST, 90 endpoints, spec-generated docs, GA on 6 November.
- **Signer:** I don't know who signs off on a breaking change. If nobody is named, that is a week-1 task.
- **Effort:** a one-off 11-week push with the two engineers, then a standing review cadence.

## 2. Re-ranking against your answers

- **Nothing public yet:** this would normally delete the surface audit and promote strategy. I'm overriding it, because a 90-endpoint spec exists and the design partners have seen it. A review of a proposed surface is exactly what `public-api-design-review` covers.
- **GA inside a quarter:** this promotes the surface audit and the error contract. It demotes `connector-marketplace-strategy`, `integration-partnership-strategy` and the `app-marketplace-*` skills to "not now", with GA as the unblocking condition.
- **Two engineers:** this deletes webhooks, SDKs, the portal and the specialist protocol surfaces for this window.
- **REST is decided:** `api-integration-surface-strategy` is off the table.
- **Customer and partner engineers only:** `oauth2-provider-design` is deleted.

## 3. Short-list

Ordered by value per unit of effort.

1. **`public-api-design-review`**
   - **Attacks:** naming, status codes, pagination and field inconsistencies across 90 endpoints, found before they are frozen.
   - **Costs:** one session over the existing spec, plus the fixes. No deploy and no sign-off.
2. **`api-versioning-policy`** (promoted)
   - **Attacks:** GA with no written breaking-change definition, no notice windows and no named signer.
   - **Costs:** a writing session and one sign-off. It ships no code, so it doesn't compete with engineer time.
3. **`api-error-design`**
   - **Attacks:** integrators who can't self-diagnose, and the support tickets that follow. It also carries the correlation ID your partners will quote in tickets.
   - **Costs:** a design session plus an additive backend change per endpoint class.
4. **`api-idempotency-retry`**
   - **Attacks:** retried writes that duplicate clinical records.
   - **Costs:** a design session plus key storage on every non-idempotent write.
5. **`api-reference-quality`**
   - **Attacks:** undocumented operations, parameters and errors, and drift after freeze.
   - **Costs:** nearly free, because the spec is committed and the docs are generated. It adds a CI lint gate and contract tests.
6. **`api-rate-limit-policy`**
   - **Attacks:** noisy-neighbour incidents.
   - **Costs:** a policy session plus gateway configuration. A published limit can only be loosened later, so start conservative.
7. **`api-auth-key-management`**
   - **Attacks:** leaked or unrotatable credentials.
   - **Costs:** a session plus a rotation path. Skip it if key format, scoping and rotation already exist.

## 4. Chain

Dependency order:

1. `public-api-design-review` hands the error and idempotency work a list of what is wrong.
2. `api-error-design` fixes the error contract the review exposed.
3. `api-idempotency-retry` makes failing writes safe to retry.
4. `api-reference-quality` documents the result. Documenting first would freeze the flaws in prose.

`api-versioning-policy` runs in parallel in week 1, since it needs no engineering.

## 5. The partner and marketplace track

It costs about half a day of your time and zero engineer time.

**Answer to your director and the board:** the 11 weeks go to GA. The partner story and the marketplace are decisions that need data GA produces. The data comes from the three design partners.

1. **Weeks 5–8:** capture structured notes from each design partner. Record:
   - what they integrate;
   - which of their customers use it;
   - what they would build;
   - who else they would bring.
   
   This is the demand data `integration-partnership-strategy` needs.
2. **Proposed, not decided:** run `integration-partnership-strategy` about four weeks after GA, in early December.
3. **Marketplace:** run `connector-marketplace-strategy` only after that, and only if the evidence gate in that skill passes. A marketplace is not a roadmap item until then.
4. **"Should we be a platform at all?"** is DevRel-side strategy that this collection doesn't cover. Install `samber/developer-relations-skills` and use `developer-ecosystem-strategy`.

## 6. Eleven-week plan

- **Allocation:** about 22 engineer-weeks. These are my planning figures, to be replaced after the week-1 audit.
- **Compliance:** Ridgeway handles clinical data, so I assume patient data is in scope.
  - Error messages and logs must not echo patient identifiers.
  - Stored idempotency payloads count as retained data.
  - Limits and scopes need a data-protection review before they are published.

| Weeks | Work | Engineer-weeks |
|---|---|---|
| 1 | Design review. Versioning policy drafted. CI spec lint added. Tell the design partners what will change. | 2 |
| 2–3 | Fix the review's must-change items while still unpublished. | 3 |
| 4 | Spec freeze. After this, additive changes only. | — |
| 3–6 | Error taxonomy and RFC 9457 envelope on all endpoints. | 5 |
| 4–7 | Idempotency keys on writes. | 3 |
| 6–8 | Rate-limit policy and key management. | 3 |
| 6–9 | Reference gaps closed. Contract tests in CI. | 3 |
| 7–9 | Design partners run their integrations. Collect § 5 notes. | — |
| 9 | Slip absorber (see below). | 3 |
| 10 | Freeze. Final reference check. Publish the versioning policy and changelog. | — |
| 11 | GA on 6 November. On-call only, no features. | — |

The buffer row is where slippage lands. Put it in the plan so nothing else gets raided.

## 7. Not now

- **`integration-partnership-strategy`:** after GA, once the design-partner notes exist.
- **`connector-marketplace-strategy`:** after `integration-partnership-strategy`, and only if its evidence gate passes.
- **`app-marketplace-*` (all four):** after `connector-marketplace-strategy` returns a build verdict.
- **`api-test-mode-design`:** after GA. Confirm whether partners can safely test without real patient data. If they can't, this moves up.
- **`integration-error-observability`:** after GA. The correlation IDs from `api-error-design` cover the gap until then.
- **`webhook-platform-design`, `sdk-portfolio-strategy`, `developer-portal-design`, GraphQL, gRPC, SQL, bulk export, MCP:** when engineering capacity exists after GA.

## 8. If you really have 4 weeks

Keep only:

1. The design review's must-change items.
2. The versioning policy.
3. The error envelope on the busiest endpoints.
4. A published rate limit.
5. The CI docs gate.

Defer idempotency to a post-GA fast-follow. Tell the design partners that now.

## 9. Routines

These are dry-run proposals only, not installed.

1. **Pre-release API design review** (`public-api-design-review`)
   - **Trigger:** a pull request touching the spec.
   - **Channel:** a PR comment from the spec repo's CI.
2. **Quarterly kickoff re-run.** The first one is two to four weeks after GA, so the context file stays current.
   - **Channel:** an updated `developer-platform-context.md` committed to the repo, plus a note to your director.

Add the reference-drift audit once the spec starts changing after GA.

## 10. Gaps

The collection has no skill for these:

- API changelog automation.
- API monetization.
- Connector certification programs.

## 11. `developer-platform-context.md`

I couldn't write this into your repo. Commit it there:

```markdown
# Developer platform context
- Audience: customer engineers and three design partners (assumed).
- Surfaces: REST, 90 endpoints, spec in repo, generated docs. Compatibility promise starts at GA, 6 Nov 2026.
- Contract owner / breaking-change signer: TBD (week-1 action).
- In flight: design review, error contract, idempotency, reference gate.
- Decided: REST, GA date.
- Open: marketplace, partner strategy (post-GA, evidence-gated).
- Constraints: 2 engineers, 11 weeks, one-off push, then standing review.
- Stakeholders: director (partner story), board member (marketplace).
- Session log: 2026-10-08 kickoff, routed to public-api-design-review.
```

**Next action:** reply to your director and the board with the § 5 answer, and tell me the real runway.