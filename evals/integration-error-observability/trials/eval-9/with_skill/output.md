# Sanity check: 99.9% per-partner SLOs and the "capped below 99.7%" message

**Verdict: ⚠️ don't write the spec as asked.** It has one arithmetic error and two design problems. The skill's own failure-mode list names the second problem.

I checked this against `integration-error-observability` (SKILL.md, `fleet-view-and-health-scoring.md`, `alerting-and-notification.md`).

## 1. The arithmetic is wrong

- Three dependencies at 99.9% each compound to 0.999³ = **99.7003%**. That is on the 99.7% line, not below it.
- It only drops below 99.7% in two cases. One is if the other two vendors are worse than 99.9%. The other is if you add the partner's own code as a fourth link (0.999⁴ ≈ 99.60%).
- Her number is a rough ceiling for hard, serial, independent dependencies. Retries, caches, fallbacks and graceful degradation can beat it. Correlated outages (a shared cloud region) can undercut it.
- If a partner checks the claim, "capped below 99.7%" is the first thing they will find wrong.

| Target | Allowed downtime per 30 days |
| --- | --- |
| 99.9% | 43.2 min |
| 99.7% | 129.6 min |

## 2. The multi-vendor message is the wrong direction

- The skill says multi-vendor compounding "does not transfer" to the provider side. It is arithmetic about the consumer's position, and the literature it comes from (Nobl9, Stytch, the SRE Workbook) is written for a team measuring its own dependence on someone else's API.
- Telling partners their ceiling sits below your own promise is a disclaimer, not a service commitment. Partners will read it as "99.9% is a fiction", which defeats the point of publishing it.
- You also don't know the other two vendors' numbers per partner. Each partner's dependency set is different, so one message can't be accurate for all 40.
- ✅ Keep the idea, but reframe it. Publish a worksheet: "your availability is roughly the product of every hard dependency you have, including us, and here is our number and how it's measured." It helps partners reason about their own stack and doesn't assert a cap.

## 3. "Published per-partner reliability number" is a flagged failure mode

The skill is explicit on three points:

- 🔴 "Consumer-side SRE error-budget framing lifted wholesale into a partner-facing reliability promise the platform never designed to meet" is in the failure-mode list.
- 🔴 "Do not publish a per-partner reliability number until you can defend how it is computed." Once published, it gets quoted back in commercial conversations.
- 🔴 "An availability commitment derived from the fleet view" is on the do-not-publish list. The measurement includes the partner's own code and their customers' configs, so you'd be promising something you only partly control.
- ℹ️ Nothing in the published record defines what a provider-side integration SLO should contain. The skill calls the mirror-image framing (the platform as the trusted real-time source of integration health) its own construction, not an industry standard. Don't present it to partners as one.
- ℹ️ Formal SLA or uptime publication belongs to the sibling skill `samber/developer-platform-skills@api-status-communication`.

## 4. Design problems in the SLO itself

- **A per-partner SLO is mostly 40 copies of one platform SLO.** A platform outage burns all 40 budgets at once. It only differs per partner when failures are key-specific, and that case is the one the fleet view already handles.
- **Which errors count?** Per the skill's buckets:
  - Count 5xx against the budget.
  - Exclude 4xx (the integrator's payloads or auth).
  - Exclude 429 (a quota conversation, not a defect).
  - One blended rate makes the number meaningless, because you can't say whose fault it is.
- **Low-volume partners.** At 500 calls a month, one failed call is 0.2% and blows a 99.9% budget on its own. You need a minimum-volume rule, or a time-based SLI, before a monthly budget means anything.
- **Granularity.** Use per-endpoint SLIs, not one blended number. This part of the SRE literature does transfer.
- **Silent failures.** An integration that stopped calling produces no errors and burns no budget. A volume-drop signal is a separate design item.
- **Tagging.** Every request needs an API key or app ID at ingestion. Without it you can't compute a per-partner number for past periods.
- **Baseline.** Have you actually measured 99.9% over the last few quarters? If not, publishing it is a promise with no evidence behind it.
- **Month definition.** Calendar month or rolling 30 days? This changes how budget resets and how burn-rate windows work.

## 5. What does transfer (build this)

1. **Internal SLIs and SLOs per integration identity and per endpoint.** Use multi-window burn-rate alerting: a short window for sudden breaks, a long window for slow degradation. Compare each integration to its own baseline.
2. **Deploy-timeline overlay.** Don't blame a partner for a 5xx spike that lines up with your release.
3. **Partner-facing health view.** Show each partner their own measured error rates, split 4xx/5xx/429, with the counts, windows and install coverage behind them. Mark it informational, not a commitment.
4. **Published availability target.** Make it platform-level or endpoint-level, via `api-status-communication`, with legal and commercial sign-off. State the SLI definition, the exclusions, the measurement window and the remedy.

## 6. Questions to take back to the director before drafting

1. Is 99.9% a commitment (SLA, credits) or a goal (SLO)? Who signs off, legal and commercial included?
2. What was actual availability for the last 6 months, by endpoint? Does it clear 99.9%?
3. Is every request tagged with an integration identity today?
4. Which errors count against the budget? I'd propose 5xx and timeouts only.
5. What happens when a partner's budget is exhausted: a freeze, a review, credits, or nothing?
6. Is the capped-availability message meant to set expectations, or to deflect blame when partners' apps go down? The second use is a trust risk.
7. Are the other two vendors the same for all 40 partners? If not, one cap number is inaccurate.

## 7. Proposed spec shape (what I'd write this week)

1. **Scope.** An internal SLI/SLO and burn-rate system per integration identity, plus a partner-facing measured-health view. No new published commitment yet.
2. **SLI definitions.** Request-based and per-endpoint, with 5xx and timeouts as bad events, and 4xx and 429 excluded and shown separately. Add a minimum-volume rule and a volume-drop signal.
3. **Internal targets.** 99.9% as an internal objective with a 43.2 min monthly budget, with the window definition fixed.
4. **Alerting.** Multi-window burn rate, cooldown and recovery notification, per `alerting-and-notification.md`.
5. **Partner portal.** A health view with inspectable inputs and no ranking against other partners.
6. **Published commitment.** A separate workstream under `api-status-communication`, gated on questions 1 and 2 above.
7. **Dependency worksheet.** Replace the "capped below 99.7%" claim with a worked example: 99.9% × 99.9% × 99.9% ≈ 99.70% for three hard serial dependencies, before the partner's own code.

I haven't drafted the spec itself. Send me the answers to 1 and 2 first, because they decide whether section 6 can be more than a placeholder.