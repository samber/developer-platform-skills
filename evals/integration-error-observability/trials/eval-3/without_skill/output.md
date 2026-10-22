# Webhook failure notifications: proposed design

## Recommendation

Don't add severity levels by event type. Three changes fix this:

1. Alert on **endpoint state changes**, not on single failed deliveries.
2. Set the urgency **per partner**, based on what a failure costs them.
3. Make the channel **partner-chosen**. Slack is one destination option, not a severity tier.

## Why the VP's plan doesn't fit

- **The problem is volume, not missing severity.** Six of your top ten partners filter these emails because one email per failure trains people to ignore them. Severity labels on the same stream won't change that.
- **Severity by failure type is the wrong axis.** A 500 on a weekly reconciler is a non-event. The same 500 on a payment-adjacent partner costs money within the hour. Urgency depends on who the partner is, not on what failed.
- **The routing target is unclear.** "Route to Slack" could mean our internal Slack, which doesn't reach partners. It could also mean partners' Slack, which means 340 Slack Connect channels or a per-partner incoming webhook. Confirm which one the VP means before anything else.

## Core mechanism: state-based alerts

Retries absorb transient errors, so a single failure never notifies anyone. Each endpoint moves through four states:

| State | Trigger (starting values, tune with data) | Who is told |
|---|---|---|
| Healthy | default | no one |
| Degraded | failure rate above 20% over 15 min, with at least 10 attempts | dashboard only |
| Failing | 100% failures for 1 hour, or 5 or more consecutive failures after retries are exhausted | tier-dependent (below) |
| Recovered | first success after Failing | one "resolved" message, with the count of events pending replay |

Failure class changes the wording:

- **401, 403, 404, 410, or an expired TLS cert** means a human must fix something. The message names the likely cause.
- **5xx or timeout** means the partner's side is probably down, and it should auto-recover.

## Two tiers, per partner

### Standard tier (about 338 partners)

- **Weekly digest email** with delivery success rate, failures, and anything still unreplayed. This matches how they reconcile.
- **One "Failing" email** after 24 hours of sustained failure. This is rare, so it's worth opening.
- **One warning before auto-disable.** Disable the endpoint after N days of failure and tell them first.
- **Make the weekly reconciliation safe:**
  - Retain failed events for at least 7 days, longer than their cycle.
  - Add a one-click replay in the dashboard.
  - Add a pull endpoint (`GET /events?since=cursor`) so they can backfill regardless of what we pushed.

With replay in place, a missed email costs them little, which is what these partners need.

### Critical tier (the two payment-adjacent partners, opt-in, contract-backed)

Their loss window is 60 minutes, so the budget is detection within about 5–10 minutes and a human notified within about 15.

- **Tighter thresholds:** Failing at 3 consecutive failures, or above 20% failures over 5 minutes.
- **Paging channels, not email:** PagerDuty/Opsgenie, SMS, or a Slack channel they own. Email is a fallback only.
- **At least two named contacts** and an escalation order.
- **Acknowledgement required.** If no one acknowledges within 10 minutes, re-alert and escalate to their second contact.
- **Our side pages too.** Our on-call and their account manager get the same alert, so we can phone them if they don't respond.
- **Recovery notice** plus an automatic replay of the backlog.
- **Quarterly drill:** send a synthetic failure to prove the channel works.

Name the criteria for joining this tier. I'd suggest a partner is critical if they declare they lose money within an hour, or if the contract includes an SLA. Then partner 3 can opt in through a documented path instead of a negotiation.

## Channels (partner-configured, per endpoint)

- **Destinations:** email list (role address, not one person), Slack app or incoming webhook, PagerDuty/Opsgenie, SMS (critical only).
- **Subscriptions:** each destination picks which states it receives.
- **Verified at setup:** send a test alert and require a click to confirm it arrived. Re-verify when the technical contact changes, or on a bounce.
- **Email hygiene:**
  - The subject names the endpoint and state, for example `[Nooklet] Webhook failing: bookings-prod since 14:02 UTC`.
  - The body gives the cause, the fix, and the replay link.
  - Use a stable sender so partners can whitelist it instead of filtering it.

## Rollout

1. **Week 1–2:** Interview the six filtering partners and the two critical ones. Ask where they would actually see an alert.
2. **Week 2–4:** Ship state-based alerts and the digest to everyone. Pilot the Critical tier with the two partners.
3. **Week 4+:** Add self-serve destinations (Slack and others).
4. **Measure:**
   - Alert volume per partner (should drop sharply).
   - Open and click rate on Failing emails.
   - Time from failure to acknowledgement.
   - Number of endpoints auto-disabled with no response.
   - Time to recovery for the two critical partners.

## Open questions

1. Whose Slack does the VP mean: ours, or the partners'?
2. Do the two critical partners have a contractual SLA or a named escalation contact today?
3. Do we already compute per-endpoint failure rates, or only per-delivery results? State alerts depend on it.
4. Are failed events retained and replayable today? The standard tier depends on that.