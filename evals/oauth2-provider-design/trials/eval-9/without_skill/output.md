# Palisade Grid authorization server: launch pack

**Caveat on benchmarks (read first):** public industry benchmarks exist for only some of these metrics. Where I have none, I mark the threshold **Proposed**. That means it is my engineering judgment, not a published figure. Replace each one with your own p50/p95 from two weeks of beta traffic before launch. I did not invent statistics to fill the column.

---

## Part 1: Go/no-go checklist (QA sign-off)

Rule: any ❌ in sections A–D blocks launch. Sections E–F can ship with a written waiver from the owner.

### A. Refresh rotation and reuse detection 🔐
| # | Check | Pass criteria |
|---|---|---|
| A1 | Rotation on every refresh | Each use returns a new refresh token and invalidates the old one. |
| A2 | Reuse detection | Replaying a rotated token revokes the whole token family (the refresh chain and its access tokens). The test reports the revocation and its audit event. |
| A3 | Concurrent-retry grace | Two parallel refreshes with the same token (client retry, network drop) behave as designed. The window is documented, and the response to the second request is deterministic. |
| A4 | Race under load | The same token sent N times in parallel across replicas yields exactly one success. Run with at least 2 server instances. |
| A5 | Lost-response case | The client misses the new token because the response was dropped. The documented recovery works (grace window or re-auth), not a permanent lockout. |
| A6 | Expiry and absolute lifetime | Idle timeout and absolute lifetime are enforced. Both are tested at the boundary: 1 second before and 1 second after. |
| A7 | Revocation propagation | Revoking a family or a user's grant takes effect within the stated bound across all instances and caches. Measure the bound. |
| A8 | Scope can't widen | A refresh request asking for more scope than originally granted is rejected. |
| A9 | Client binding | A refresh token presented by a different `client_id` is rejected. Public clients: confirm the rotation-only protection is documented, since RFC 9700 allows rotation or sender-constraint for public clients. |
| A10 | Storage | Only hashes of refresh tokens are stored. No tokens appear in logs, traces, or error payloads. Grep the log output from the test run. |

### B. Granular consent
| # | Check | Pass criteria |
|---|---|---|
| B1 | Per-scope grant/deny | The user can approve a subset of scopes. The issued token contains exactly that subset. |
| B2 | Token reflects consent | The `scope` response parameter is accurate when the grant is narrower than requested. |
| B3 | Consent persistence | A repeat authorization with the same or fewer scopes skips the prompt. More scopes triggers incremental consent for the delta only. |
| B4 | Revocation | The user can revoke one app, or one scope, from the UI. Existing access and refresh tokens die within the bound from A7. |
| B5 | Prompt integrity | The consent screen shows the verified app name, publisher, and scope descriptions. `prompt=consent` is honored. Clickjacking protections (frame-ancestors, CSP) are in place. |
| B6 | Redirect safety | Exact-match redirect URIs only. Wildcards, open redirects, and `state` tampering tests all fail safely. |
| B7 | PKCE | Required for all clients. Downgrade attempts (missing verifier, `plain`) are rejected. |
| B8 | Audit trail | Every grant, denial, and revocation produces an immutable event with actor, client, scopes, and time. |
| B9 | Accessibility and i18n | The consent screen passes keyboard-only and screen-reader checks. Every supported locale renders without truncated scope text. |

### C. App review queue
| # | Check | Pass criteria |
|---|---|---|
| C1 | State machine | Submitted → in review → approved / rejected / changes requested. Every transition is tested, including illegal ones. |
| C2 | Gating | An unapproved app cannot get production scopes. Test by calling the authorize endpoint directly. |
| C3 | Scope-level approval | Sensitive scopes need explicit reviewer approval. Approving an app doesn't silently approve later scope additions. |
| C4 | Re-review triggers | A changed redirect URI, newly requested scope, or ownership change sends the app back to review. |
| C5 | Reviewer access control | Role separation and audit log. A submitter can't approve their own app. |
| C6 | Queue visibility | The oldest-item-age metric and alert are live (see Part 2). A named reviewer owns the queue each day. |
| C7 | Takedown | A reviewer or on-call can suspend an approved app in under 5 minutes. This kills its tokens and is rehearsed once. |
| C8 | Notifications | Partners get submitted / approved / rejected emails with actionable reasons. |

### D. Security and platform 🔐
| # | Check | Pass criteria |
|---|---|---|
| D1 | External pen test | No open critical or high findings. Mediums have owners and dates. |
| D2 | Protocol conformance | Authorization code + PKCE flow tested against RFC 6749, RFC 7636, and RFC 9700 (OAuth Security BCP). Use the OpenID conformance suite if you issue OIDC. |
| D3 | Key management | Signing key rotation rehearsed. JWKS caching behaves correctly through a rotation. Old-key retirement is tested. |
| D4 | Rate limits and abuse | Per-client and per-IP limits on `/token` and `/authorize`. Credential stuffing and token-guessing tests are throttled. |
| D5 | Secrets | Client secrets are hashed at rest. No secrets in repos, logs, or images. |
| D6 | Load test | At least 3x expected launch peak on `/token` for 30 minutes. p99 and error rate stay inside the Part 2 thresholds. |
| D7 | Failure drills | Primary DB failover, cache loss, and one dependency down. The server fails closed, never open. |
| D8 | Backup/restore | A restore is tested. Token and consent tables are covered. |

### E. Partner readiness (about 30 partners)
| # | Check | Pass criteria |
|---|---|---|
| E1 | Cohorting | Partners onboard in waves (suggest 5 → 10 → 15), not all at once. |
| E2 | Integration verification | Every partner has passed a sandbox run of: auth code + PKCE, refresh rotation, handling `invalid_grant`, and consent downscoping. |
| E3 | Rotation guidance | Docs state how clients must store and replace refresh tokens, and what to do on a revoked family. Most reuse-detection incidents come from partners that retry without persisting the new token. |
| E4 | Contacts | Named technical contact and escalation path per partner. |
| E5 | Comms | Launch notice, incident channel, and a status page with subscriptions. |
| E6 | Per-partner kill switch | You can disable one partner without affecting others. |

### F. Operations
| # | Check | Pass criteria |
|---|---|---|
| F1 | Dashboards and alerts | Part 2 metrics live in prod. Each alert has been fired once in staging. |
| F2 | Runbooks | One per alert. On-call has done a dry run. |
| F3 | Rollback | A tested plan exists. Rolling back must not invalidate valid refresh families unexpectedly. |
| F4 | On-call | Rota covers launch day plus the first 2 weeks. |
| F5 | Data protection | Privacy review done. Consent records have a defined retention period. |
| F6 | Sign-offs | Security, QA, SRE, product, and the review-queue owner each sign in writing. |

---

## Part 2: Post-launch dashboard (5 metrics)

| # | Metric | Definition | Industry benchmark | Page / investigate when |
|---|---|---|---|---|
| 1 | **Token endpoint availability and latency** | Share of non-5xx responses on `/token` and `/authorize`, plus p95/p99 latency | **Availability:** major identity providers publish SLAs in the 99.9%–99.99% range. **Latency:** no published standard. | Availability under **99.9%** over 5 min, or p99 over **500 ms** for 10 min (**Proposed**; p95 target 200 ms) |
| 2 | **Refresh success rate** | Successful refresh ÷ refresh attempts, with `invalid_grant` split by cause (expired, revoked, reused, client mismatch) | None published. | Success rate drops more than **2 points** below your 7-day baseline, or one partner exceeds **3x** its own baseline (**Proposed**) |
| 3 | **Reuse-detection triggers** | Family revocations caused by reuse per 1,000 refreshes, split into inside the grace window and outside it, and by partner | None published. Treat any non-zero rate as signal. | Rate above **3x** baseline, or a burst from a single client (usually a retry bug in a partner). A spike across many partners at once suggests a server-side race or a real attack. (**Proposed**) |
| 4 | **Consent completion** | Consent screens shown → grant. Track also the share of grants that are partial (downscoped) and revocations per 1,000 active grants | None authoritative. Public acceptance rates vary too much by audience and product. | A move of more than **10 points** from the 2-week beta baseline, or a partner whose partial-grant share jumps. Both usually mean a broken prompt or an over-asking app. (**Proposed**) |
| 5 | **App review queue age** | Age of the oldest item, p90 time-to-decision, and queue depth | Apple states that about 90% of App Store submissions are reviewed within 24 hours. Google OAuth verification commonly takes days to weeks. These are loose reference points, not standards. | Oldest item beyond your published review SLA (set it, for example 3 business days). Depth alone isn't alarming with about 30 partners. (**Proposed**) |

**On-call rule of thumb:** compare against your own trailing baseline first, and use the benchmark column only as a sanity check. For metrics 2 to 5, the benchmark is your first two weeks of data. Declare those two weeks "baseline mode" in the runbook, and finalize thresholds at the end of week 2.

**Where to look when one is off:**
- Metric 1 red → check DB, cache, and key/JWKS health first.
- Metric 2 or 3 red → check whether it is one partner (client bug, contact them) or all (server regression, consider rollback per F3).
- Metric 4 red → check the last consent UI or scope-text change.
- Metric 5 red → page the review-queue owner, not engineering.

---

## Open questions for you

1. Do you issue OIDC ID tokens too? If so, add conformance-suite results to D2.
2. Are your clients public (native/SPA), confidential, or both? This changes A9.
3. What review SLA have you promised partners? It sets the metric 5 threshold.