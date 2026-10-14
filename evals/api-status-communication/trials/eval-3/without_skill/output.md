# Incident notification channels for Hatchbill: what to build, in what order

**Recommendation:** build webhooks first, then email, and skip SMS and push. Before any of that, move the notification path out of the product's failure domain.

## Step 0 (days 1-3): Decouple the status page

Your status page shares an AWS account and Route53 zone with the product. Anything that breaks the product can also break the status page and the notifications sent from it. That includes a bad deploy, an IAM or account problem, a DNS change, a regional outage, or a billing lock. Customers then get silence at the moment they most need an update. Adding channels on top of that setup doesn't help.

- Put the status page on a different provider, or at least a different AWS account, region and DNS zone. A hosted status product is the fastest route for two engineers in two weeks.
- Use a separate domain or registrar for the status hostname, for example `hatchbillstatus.com` rather than `status.hatchbill.com`. Then a mistake in your zone can't take it down.
- Make sure the tool that publishes incident updates, and anything that sends notifications, doesn't depend on Hatchbill infrastructure.
- If you stay on AWS, SES in the same account and region is not independent either. Send from another account or region, or from an outside vendor.

## Channel order

| Order | Channel | Why | Effort |
|---|---|---|---|
| 1 | **Incident webhooks** | Your integrators are developers and already consume your webhooks, so this reuses code they've written. It's the only channel that lets them automate a response, such as pausing retries, queuing invoices or alerting their own on-call. | ~4 days |
| 2 | **Email subscriptions** | Universal fallback. Subscribers opt in on the status page. | ~3 days (or free with a hosted status vendor) |
| 3 | **RSS/Atom and a JSON status API** | Nearly free, and developers like them. It also gives a polling fallback if webhooks fail. | ~1 day |
| 4 | **In-band signals** | Add a link to the status page in 5xx and 503 error bodies and an `X-Hatchbill-Incident` response header during incidents. Add a dashboard banner. This reaches developers exactly where they notice the problem. | ~2 days |
| Later | Slack or Teams incoming-webhook templates | A small add-on to the webhook work. | ~1 day |
| Skip | **SMS** | See below. | n/a |
| Skip | **Push** | See below. | n/a |

### 1. Incident webhooks

- Use a **separate event family**, such as `incident.created`, `incident.updated` and `incident.resolved`. Don't mix these into product events. Integrators can then subscribe to them separately, and your existing handlers won't see surprise payloads.
- Reuse your existing signing scheme, so integrators can verify signatures with code they already have.
- **Send them from the independent path, not the product's webhook dispatcher.** If the product is down, its dispatcher is probably down too. Run a small sender, such as a Lambda in a separate account or the status vendor's webhook feature, that reads the same subscriber endpoints. Sync the endpoint list periodically to somewhere the sender can reach.
- Include `incident_id`, `status`, `affected_components`, `started_at`, a human-readable message and the status page URL.
- Retry with backoff, and log delivery failures. You can't assume the integrator's endpoint is up either.

### 2. Email

- Make it opt-in on the status page, with component-level subscription if the tool supports it.
- Also consider emailing the account owner on major incidents only. You already have an email on file for every customer, because sign-up needs a card and an account. Check the compliance side before you do this.
- Keep the content short: what's affected, current status, the next update time and the link.

### Why not SMS

- Sign-up is credit-card only, so you probably don't hold a verified phone number for most customers. You'd have to collect numbers first.
- US A2P 10DLC registration, plus carrier rules for other countries, can take weeks. That alone eats your two-week budget.
- It adds per-message cost and an abuse and opt-out burden.
- Nothing contractual pushes you toward it. You have no SLAs with penalties and no enterprise on-call contracts, which are the situations where SMS pays for itself.
- If customers ask for pager-style alerts later, offer a PagerDuty or Opsgenie-compatible webhook or Slack feed instead.

### Why not push

- You have no mobile app, and web push has poor opt-in and unreliable delivery for this use. Skip it.

## Two-week schedule (two engineers)

| Days | Engineer A | Engineer B |
|---|---|---|
| 1-3 | Stand up the independent status page, domain and DNS | Define the incident event schema and the independent sender architecture |
| 4-7 | Email subscriptions, RSS and JSON API | Incident webhooks: subscription, signing, delivery and retries |
| 8-9 | In-band headers, error-body link and dashboard banner | Docs page for integrators with payload examples and a test-fire button |
| 10 | **Game day:** simulate a full product outage in the product account. Confirm the status page, email and webhooks still go out. | Same drill, and fix whatever breaks |

Also write a one-page runbook covering who can publish, the update cadence (for example every 30 minutes for major incidents) and a template. The tooling is only half of "getting notifications right."

## Assumptions to confirm

- I assumed webhook subscriber endpoints can be read by a sender outside the product. If that's hard, run the sender in the same account but a different region, and say so in the docs.
- I assumed you can add a new event family without breaking existing consumers. If integrators use strict schemas, version it.