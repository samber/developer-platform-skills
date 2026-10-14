# Webhooks: build vs. buy

## Call

**Build it in-house, as a deliberately narrow v1. Don't buy a hosted service.** Design it against the Standard Webhooks spec so you can swap in a self-hosted engine later without breaking partners.

## Why not buy

- **Hosted webhook services are out.** Svix Cloud, Hookdeck, and Convoy Cloud all put payroll event payloads through a third party's infrastructure. Legal has said that isn't allowed this quarter, and it isn't something to work around on a deadline.
- **Don't re-scope Legal's position.** One idea is to send "thin" events (an ID only) through a vendor so the payload isn't payroll data. That is a reinterpretation of Legal's wording, and only Legal can make it. Don't build the plan on it.
- **Self-hosting an open-source engine (Svix OSS, Convoy) is the only real "buy" path.** It saves less than it seems:
  - You still run, patch, and get paged for a new stateful service, and you have no on-call today.
  - You still build the event outbox, tenant and auth mapping, and partner-facing endpoint management around it.
  - Its extra datastores (Redis, a queue) add risk to the launch.
  - Legal hasn't confirmed that self-hosted third-party software sits outside "third-party processor". That is a likely yes, but it is a dependency on Legal that you don't control.

## Why build works in seven weeks

- A first version is small and well understood. It needs only these pieces:
  1. A transactional outbox in your existing database, so events are never lost.
  2. A delivery worker with HMAC signing, timeouts, and exponential-backoff retries over about 24 to 72 hours.
  3. Per-endpoint auto-disable after sustained failure.
  4. SSRF protection: block private and link-local ranges, pin DNS resolution, and allow HTTPS only.
  5. A delivery log, manual replay, and secret rotation.
  6. A small partner-facing API to register endpoints and see delivery status.
- **Payroll data never leaves your infrastructure.** That satisfies Legal by construction.
- **It reuses what you already run.** There is no new datastore or vendor. That matters most with no on-call rotation.
- **Staffing:** put 2 engineers on it, with a third part-time for security review and docs. The other 3 to 4 keep the roadmap moving.

## Cut from v1 to protect the date

The date is fixed, so scope is the lever. Defer these:

- Partner self-serve portal UI (use API plus docs).
- Fan-out transforms and payload filtering.
- Per-partner rate shaping beyond a simple concurrency cap.
- Event-type versioning beyond a `v1` field.
- Multi-region delivery.

## Rough plan

| Weeks | Work |
|---|---|
| 1 | Event catalog and payload contract with the partner. Ask Legal for sign-off on the payload field list. |
| 2–3 | Outbox, worker, signing, retries |
| 4 | SSRF hardening, endpoint management API, delivery log, replay |
| 5 | Load and failure testing (slow endpoints, 5xx storms, a partner down for 24h), security review |
| 6 | Pilot with one partner in staging, then production |
| 7 | Buffer, runbook, docs. No new features. |

## On-call (the real risk)

Delivery to partners is an external promise, so someone must own failures after launch. Don't leave this open.

- **Set the SLA to match the support you can give.** Promise at-least-once delivery with retries for up to 72 hours, and publish that. Then most failures are not 3 a.m. pages.
- **Set up a minimal rotation before launch.** One person at a time, business hours plus best-effort evenings, rotating weekly across the 6 engineers.
- **Page only on a few signals:** outbox lag above a threshold, worker down, and delivery success rate below a threshold.
- **Write a one-page runbook** covering replay, pausing an endpoint, and draining the outbox.

## Conditions that change the call

- **Switch to self-hosted open source** if Legal confirms in writing that it is allowed and the team already runs the datastores it needs. Even then, wait until after Q1 and run it in parallel first.
- **Descope further** if the week 3 checkpoint slips by more than a few days. Drop manual replay to an internal-only tool, not the date.
- **Escalate** if Legal's blocker also covers partner endpoints receiving payloads. That is a product question beyond tooling.

## Decisions needed this week

1. **Board and CTO:** approve a build with 2 dedicated engineers for 7 weeks, with the deferral list above.
2. **Engineering:** commit to the minimal on-call rotation before launch.
3. **Legal:** confirm which payload fields partners may receive. This is a scope question, not a reopening of their position.
4. **Product:** lock the event catalog and v1 payload schema by the end of week 1.

I didn't read anything under `skill-wip/`. I also don't know your current infrastructure, so the hosting and database assumptions above are unverified.