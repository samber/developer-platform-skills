# Hatchbill incident notification channels: what to build, in what order

I read the skill and its three references. Your SMS instinct changes the most, so start there.

## Short answer

1. **Move the status page off your own infrastructure**, with email and RSS subscriptions on. This is the first task. It covers the email you wanted, and it should be a hosted tool's built-in subscriptions, not email you build yourselves.
2. **Wire the page to external monitoring**, so the first public update is automatic. This isn't a channel, but every channel sends nothing useful without it.
3. **Add status webhooks.** Your integrators are developers and already consume your webhooks, so this rung is cheap and valuable.
4. **Drop SMS.** Don't park it as "later".
5. **Mobile push isn't on the menu.** The skill has no such rung, and nothing you described suggests Hatchbill has a mobile app. If you meant dashboard notifications, say so and I'll re-rank.

## Why this order

| Your answer | Effect on ranking |
|---|---|
| Page shares the AWS account and Route53 zone with the product | Redundancy goes from last to first. A page that dies with the platform is worth nothing during the outage it should report. |
| Developers who already consume your webhooks | Webhook push moves up and gets cheap. |
| Credit-card signups only, no enterprise contracts, no penalty SLAs | SMS is deleted. Per-message cost and deliverability work would serve no one. |
| Two engineers, two weeks | Use hosted tooling for the rungs it provides nearly free, and build only the webhook event yourselves. |

**SMS stays out of scope.** "We could add SMS later" tends to return as scope every time an incident feels loud. The re-promotion trigger is the first contract that specifies a notification channel.

## Plan: 10 working days, 2 engineers

### Days 1–3: out-of-band page plus email and RSS

- **Host the page on a hosted status tool** that sends its own email and RSS. Don't send the emails from SES in your AWS account.
- **Use a separate domain, registrar and DNS provider.** A delegated `status.` subdomain still depends on your Route53 parent zone for the delegation lookup, so I'd use a separate domain. That reasoning is mine, not from the skill.
- **Model the components** on consumer mental models, not your architecture. Start with 4–5, for example API, Dashboard, Webhooks, Invoice delivery and Docs.
- **Set component severity by breadth of impact, not felt severity.**
  - Degraded Performance: works but slow for everyone.
  - Partial Outage: broken for a subset, such as one region.
  - Major Outage: unavailable for everyone.
- **Write down the rule that the page shows the worst component state.**
- **Enable per-component subscriptions.** Subscribers who can answer their own question also cut your support tickets during incidents.
- **Link the page from the docs, the dashboard footer and the API error responses.**

### Days 3–6: monitoring-driven status (the trust step)

- **Run the probes from outside your AWS account.** Otherwise monitoring goes dark with the platform. That's my inference from your shared-infrastructure answer.
- **Auto-open an Investigating incident from the alert.** Humans add detail afterwards, but they never decide whether customers get told.
- **Add one workflow probe**, a real journey such as create a customer, create an invoice and send it. It catches infrastructure that is green while the product is broken.
- **Write the mapping from your internal severity levels to public component states once**, so responders don't debate it mid-incident. The SEV1–SEV4 table in the incident-update reference is a workable default.
- **Write the escalation rule** for when an alert becomes a public update, and set your own thresholds.

### Days 6–10: status webhooks

- **Define the status events only:** incident created, incident updated, incident resolved, and maintenance scheduled, started and completed.
- **Put these fields in the payload:**
  - incident id and plain-language title
  - lifecycle status
  - affected components with their state and region
  - `next_update_at`
  - page URL
- **Reuse your existing webhook signing and payload conventions.** The delivery machinery belongs to `webhook-platform-design`. You only define the status event.
- **Ship the hosted tool's own webhook subscription first**, because it works when your platform is down.
- **Optionally fan out to integrators' existing Hatchbill webhook endpoints.** This depends on your platform, so it fails exactly when the platform is fully down. It still helps for the more common partial and regional incidents. Label it supplementary and never make it the only push channel.

### Days 9–10: dry run, in parallel with the webhook work

- **Run a game day.** Break something in staging or simulate a probe failure, then time it. Pass the gates below before you call the work done.
- **Use the four statuses:** Investigating, Identified, Monitoring, Resolved.
- **Keep the update discipline:** every update names the time of the next one. Use the templates in `references/incident-update-templates.md`.
- **Set the default postmortem rung** to a status-page summary: impact, cause, fix and prevention. Promote to a full engineering-blog post only for P1-class incidents.
- **Put these conventions on the page for planned work:**
  - notice of roughly 24 hours for minor work
  - exact start and end times with a time zone
  - precise scope
  - at least one push channel, never the page alone

## Gates to pass before calling it done

1. **Detection-to-disclosure lag:** the alert fires, and the page updates within minutes with no human involved. Tens of minutes means a human gate is still in the loop.
2. **No third-party-first disclosures:** DownDetector or social media never reports an outage before your page does. Check this on every incident.
3. **Lifecycle completeness:** every incident shows all four statuses with timestamps, and every promised next-update time was kept.

Two trends to watch afterwards, not gates: the share of public postmortem action items completed (below about 50% means they've become theater), and support tickets during incidents (baseline on your next incident).

## What I assumed

These are guesses. Tell me if any is wrong, because each would change the plan:

- **How status is set today.** If someone flips it by hand, days 3–6 get bigger and may take most of week 1. If you already have external probes, they get shorter.
- **How consumers learned about the last incidents.** If a third party reported one first, that raises the urgency of the monitoring step.
- **One-off fix or long-term asset.** I assumed a fix you may grow later. If you'd rather build a lasting practice, add the deeper postmortem habit now.
- **Page audience.** I assumed one public developer-facing page and no second audience. Without enterprise customers or an end-user audience, extra page tiers would only add surfaces to keep consistent mid-incident.