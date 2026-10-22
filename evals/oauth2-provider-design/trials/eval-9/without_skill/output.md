# Palisade Grid authorization server: launch pack

Target launch is about 2026-11-13 (five weeks out). Two parts: the QA go/no-go checklist, then the post-launch dashboard.

⚠️ **No public industry benchmark exists for most of these metrics.** I have no source for a standard reuse-detection rate, consent grant rate, or review-queue turnaround for a custom authorization server. I won't invent numbers. Each metric below separates two things:
- **Reference:** a real public anchor, where one exists.
- **Starting threshold:** my proposal, not an industry figure.

Replace the starting thresholds with your own p50 and p95 after 2 weeks of production data.

## Part 1: Go/no-go checklist for QA

Rule: every item is Pass or Fail with evidence attached. One Fail in sections A to C means **No-go**. Sections D to F can ship with a named owner and a dated fix.

### A. Refresh rotation and reuse detection (blocker)

- [ ] **A1.** Each refresh issues a new refresh token and invalidates the old one. Test: two sequential refreshes, then replay of the first token.
- [ ] **A2.** Replaying a rotated token revokes the whole token family and returns `invalid_grant`. The audit log records the event.
- [ ] **A3.** Concurrent refresh with the same token (two parallel requests) is handled. One request wins. The loser gets a defined result, and a legitimate client retry after a network drop does not kill the family unless you chose that policy on purpose. Document the grace window, if any.
- [ ] **A4.** Revoking a family also invalidates the access tokens issued from it, within the documented lag. This is checked at the token endpoint and at introspection or revocation endpoints (RFC 7009, RFC 7662).
- [ ] **A5.** Expiry holds for both idle and absolute lifetime. Test at the boundary: expiry minus 1s, expiry, expiry plus 1s.
- [ ] **A6.** Rotation stays correct when a request fails after the DB write and before the response. The client can recover, and no family is orphaned.

### B. Granular consent (blocker)

- [ ] **B1.** A token never carries a scope the user did not grant. Test: request scopes A+B, the user grants A only, and the token holds A only.
- [ ] **B2.** The consent screen lists every requested scope in plain language, with the correct app name and verified publisher status.
- [ ] **B3.** Revoking one scope takes effect on the next refresh and on resource-server checks. Other scopes keep working.
- [ ] **B4.** A scope-widening request after the first consent re-prompts the user. It never silently upgrades.
- [ ] **B5.** The user can see and revoke each app's grants. A revocation leaves an audit record with timestamp and actor.
- [ ] **B6.** Consent is bound to the exact client and redirect URI. Test with a mismatched `redirect_uri`, a changed `state`, and a missing PKCE verifier. All must fail.

### C. App review queue and partner enablement (blocker)

- [ ] **C1.** Unapproved apps cannot get production tokens, and cannot be promoted by direct API call, ID guessing, or an old session.
- [ ] **C2.** Every state transition (submitted, in review, approved, rejected, suspended) is logged with actor and time. Reviewer permissions are enforced.
- [ ] **C3.** Suspending an approved app stops new tokens at once and revokes existing ones. Test it with a live refresh token.
- [ ] **C4.** Changing scopes or redirect URIs on an approved app sends it back to review, or is blocked.
- [ ] **C5.** All ~30 launch partners are listed with status. Each has a named reviewer and a tested sandbox. No partner is blocked at the review step on launch day.

### D. Security baseline (blocker for the first three, fix-dated for the rest)

- [ ] **D1.** Conformance with RFC 9700 (OAuth 2.0 Security BCP): PKCE required for public clients, exact redirect URI matching, no implicit grant, no password grant.
- [ ] **D2.** Penetration test or security review done. No open critical or high findings.
- [ ] **D3.** Signing keys: rotation tested, `kid` handling verified, and the JWKS endpoint serves old and new keys during the overlap.
- [ ] **D4.** Rate limits on the token, authorize, and introspection endpoints. Brute-force and enumeration probes are throttled.
- [ ] **D5.** No tokens, secrets, or auth codes in logs. A grep of a full test run confirms it.

### E. Reliability and operations

- [ ] **E1.** Load test at 3x expected launch-week peak. p99 on `/token` stays within the SLO below, with no errors.
- [ ] **E2.** Failover test: kill the primary DB, cache, and one app node. Token issuance recovers inside the documented time.
- [ ] **E3.** Rollback plan tested: the previous version redeploys, and issued tokens stay valid.
- [ ] **E4.** Dashboards and alerts from Part 2 exist and have fired in a test. Runbooks are linked from each alert.
- [ ] **E5.** On-call rota is set for launch week, with an escalation path and a named incident commander.

### F. Launch readiness

- [ ] **F1.** Partner docs cover endpoints, scopes, rotation behavior (including what a client must do on `invalid_grant`), and consent UX.
- [ ] **F2.** Partners go live in waves, not all at once. Suggested: 5, then 10, then 15, with a hold point after each wave if any Part 2 metric is red.
- [ ] **F3.** A kill switch exists to pause new app approvals and new consent grants without taking down token refresh.
- [ ] **F4.** Privacy and legal sign-off on the consent text and data retention.

### Sign-off

| Role | Name | Decision | Date |
|---|---|---|---|
| QA lead | | Go / No-go | |
| Security | | Go / No-go | |
| Engineering lead | | Go / No-go | |
| On-call lead | | Go / No-go | |

## Part 2: Post-launch dashboard (5 metrics)

**Window.** Review hourly on launch day, daily in week 1, and weekly after that.

### 1. Token endpoint availability and latency
- **What:** the success rate of `/token` (non-5xx), and p99 latency.
- **Reference:** a 99.9% availability SLO is the common default for auth infrastructure. That is a convention, not a standard.
- **Starting threshold:** page below 99.9% over 30 min, or p99 above 500 ms for 10 min. Set the latency number from your load test (E1), not from me.
- **Off means:** every partner login and refresh is affected. Check this first.

### 2. Refresh success rate and reuse-detection rate
- **What:** (a) the share of refresh calls that succeed, and (b) reuse-detection events per 1,000 refreshes.
- **Reference:** RFC 9700 mandates rotation or sender-constraining for public clients. It gives **no** expected reuse rate.
- **Starting threshold:** page on a sudden spike, or on a single partner above 5x its own 7-day baseline. A rate near zero is expected. A rate that steadily climbs usually means a client bug, such as parallel refresh without locking, not an attack.
- **Off means:** a spike for one `client_id` points to a broken partner integration, so contact them. A spike across all clients points to a server bug, such as the A3 race, or a real token theft. Check the A3 grace window first.

### 3. Consent funnel: grant rate and scope-narrowing rate
- **What:** consent screens shown, then granted in full, granted in part, or denied. Also the share of grants where the user removed at least one scope.
- **Reference:** none that I can cite. Treat any "typical consent rate" figure from a vendor blog as unverified.
- **Starting threshold:** alert on a drop of more than 15 points against the 7-day baseline, or on one partner whose denial rate is more than double the median.
- **Off means:** a high denial rate usually means over-broad scopes or an unclear screen. A very high partial-grant rate means partners request more than users will give. Both are feedback for partners, not outages.

### 4. App review queue: age and throughput
- **What:** the p50 and p95 time from submission to decision, and the count of items waiting more than the target.
- **Reference (loose analog only):** Apple states that about 90% of App Store submissions are reviewed within 24 hours. Google OAuth app verification commonly takes days to weeks. Your queue is different (about 30 partners, human reviewers), so use these only as a sanity check.
- **Starting threshold:** target p95 within 2 business days at launch. Alert if any item is older than 3 business days, or the queue grows for 3 days running. Tune this to your reviewer headcount.
- **Off means:** partners stall at launch. Add reviewers or pause new intake (F3).

### 5. Authorization error mix
- **What:** the share of `/authorize` and `/token` responses by error code (`invalid_grant`, `invalid_client`, `invalid_scope`, `access_denied`, `redirect_uri` mismatch), per client.
- **Reference:** no standard rate. The useful comparison is each client against its own baseline.
- **Starting threshold:** alert when total 4xx on `/token` exceeds 5% for 15 min, or one error code jumps 3x. Calibrate the 5% on week 1 data.
- **Off means:** `invalid_grant` is the key one. Cross-check it with metric 2. `invalid_client` or `redirect_uri` spikes right after a partner deploy usually mean config drift.

## Next action

1. Fill in the **"Starting threshold"** values from your E1 load-test results.
2. Send the checklist to QA this week. Sections A to C carry the most risk, so start there.

I can write the A1 to A3 and B1 to B6 test cases as executable tests if you give me the repo path.