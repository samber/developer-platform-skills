# Nooklet partner notification design

**Short answer:** Don't add severity levels to the email stream. The fix is to stop alerting per failure and alert per incident. Then pick the channel by what each partner loses, not by how bad Nooklet thinks a failure is.

I read the skill and its references and applied them without a clarifying round. The assumptions are at the end.

## Diagnosis

- The problem is volume, not missing severity. One failed delivery produces one email, so one outage produces a flood. Six of your top ten have muted the channel.
- Nooklet's Slack would not reach partners. If "route to Slack" means an internal Nooklet channel, it doesn't fix the partner side at all.
- Failure type can't tell you severity. The same 500 on a webhook is noise for a weekly reconciler and costly for the payment-adjacent partners. Importance depends on the partner, so a severity label on the failure would be wrong for most of the 340.
- The email has nowhere to send the reader. There is no link to a delivery log, no top error codes, and no recovery message.

## The design

Three notification types, all keyed on an **incident**, meaning one integration with one failure signature, with a state of open, ongoing or recovered.

| Type | Who gets it | Trigger | Channel |
|---|---|---|---|
| **Daily digest** (default) | All 340 | Scheduled, per integration. Skip it when there were zero failures. | Email to a role address |
| **State-change alert** | All 340 | Endpoint auto-disabled, secret or credential expired or revoked, subscription lapsed. One event, no cooldown. | Email, plus the partner's Slack if configured |
| **Threshold alert with cooldown** | The two payment-adjacent partners, plus any partner that opts in | Error rate above that integration's own baseline in a short window (5–10 min), or webhook volume dropping to zero | Partner-owned Slack or paging channel, plus email |

**Digest content.** Calls and failures, split into 4xx (theirs), 5xx (ours) and 429, then top error codes. Link into the delivery-attempt log.

**Threshold alert rules**
- One alert per incident, then a cooldown. Start at 30 minutes (Salesforce's default) and tune from your real incident durations.
- Send a recovery message. Silence isn't an all-clear.
- Check your own deploy timeline first. If the cause is your release, say so, and don't phrase it as their fix.
- State the top error code, how many installs are affected, and when the next alert can arrive.
- Add an escalation path: if nobody acknowledges within N minutes, the alert goes to your partner team and your on-call. For the two payment partners, agree N with them, because they lose money inside an hour.

**Where "severity" fits.** Derive it from the incident, using partner tier × share of installs affected × duration. Don't assign it per failure.
- Tier is set at onboarding. The partner declares "money-at-risk" or "reconcile later", and Nooklet confirms.
- The tier then picks the row in the table above.
- Slack is a destination the partner configures, not a severity level. Nooklet doesn't need a Slack integration per severity.

## Prerequisites (otherwise the alerts have nothing to point at)

1. **Expose the delivery-attempt log you already write.** It needs actual failure reasons, attempt numbers and next retry time. Every message links to it, filtered to the incident.
2. **Retention must outlast weekly reconciliation.** Most partners notice breakage at the next weekly reconcile, so a 24-hour or 7-day window expires the evidence first. Aim for 30 days or more and publish the window.
3. **Open access to the partner engineer.** Don't limit it to the account owner.
4. **Consider replay for the weekly reconcilers.** Their real loss is events that exhausted retries while they weren't looking. Replay must not fight your retry schedule, and it needs stable event IDs.

## Nooklet-side fleet view

The six muted partners won't see email whatever you do, so you need an out-of-band path.
- Build a ranked queue across the 340, ordered by blast radius: installs affected over total installs, then error rate against baseline.
- Include silent integrations whose volume dropped.
- Show first-seen against your last deploy, so "broken since our release" goes to your regression queue and "broken since theirs" goes to partner outreach.
- Give each row a named contact. For the top ten, an account manager reaches the six muted ones directly during a real incident.

## Why not what the VP proposed

- **Severity levels on the existing per-failure email.** This keeps the flood and only changes labels. It's the alert-fatigue failure mode.
- **Everything important to Slack, for everyone.** Nooklet would have to guess importance for 340 partners. At scale, that's a second muted channel. Reserve push for partners who need it (two now, others opt in), and make sure someone at Nooklet is staffed to answer what you send.
- **Alert on every failure for the two payment partners.** They need speed, not volume. Cooldown and one alert per incident give them both.

## How to know it worked

- **Alert action rate.** Share of alerts a partner acts on. A sustained fall means widen thresholds or lengthen the cooldown before adding channels.
- **Time from first failure to partner action** (not to alert sent), tracked per rung. This is the number that justifies promoting a partner to the threshold tier.
- **Failure-class coverage.** For the last 20 partner tickets, how many could the partner have answered from the log? Re-run this on a fresh batch after shipping.
- **A before-and-after on the six muted partners.** Ask them why they filter the emails and which address and channel they'd actually watch. This is the quickest check on whether the digest lands.

## Assumptions to confirm

I didn't ask these, and each answer moves the design:
1. Partners today get webhook-failure emails only. If they also make inbound API calls, add the request log and a volume-drop signal.
2. The delivery machinery already records per-attempt outcomes. If it doesn't, that becomes step one.
3. Every inbound call and delivery is tagged with an app or client ID.
4. You can staff on-call for the threshold tier. Two partners is manageable. Opt-in for all 340 is not, without an effort ceiling.
5. Your legal answer on exposing payloads. If bodies can't leave your tenancy boundary, the log is metadata-only.
6. The two payment-adjacent partners should agree their own thresholds, escalation contacts and Slack destination, as a short onboarding conversation rather than a config flag.