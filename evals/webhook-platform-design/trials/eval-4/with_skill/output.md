# Kestrelpay webhooks: build vs buy

**Call: self-host an open-source webhook gateway. Don't buy managed, and don't build in-house.**

## 1. Managed is off the menu

Legal's position is that payroll event data may not transit a third-party processor, and they aren't reopening it. That deletes the managed rung (Svix, Hookdeck or Convoy as hosted services) instead of ranking it last.

A managed option parked at the bottom tends to come back as scope the next time the deadline bites, and without the legal review that ruled it out. The skill gives one re-promotion trigger: a signed DPA and a residency posture that covers the vendor. Neither exists, and legal won't work on it this quarter.

Write this in the decision record: "Managed deleted, not demoted. Re-open only with a signed DPA and residency cover."

## 2. Gateway vs in-house

Two options remain.

| | Self-hosted gateway | In-house build |
|---|---|---|
| Effort | Moderate: deploy, operate, integrate | Highest. The skill's vendor-sourced estimate is 3-5 engineers for 6-12 months plus a standing on-call. That figure is vendor self-interest, but the order of magnitude holds. |
| Working pipeline on day one | Yes: queue, retries, DLQ, signing, logs | No |
| Data stays on your infrastructure | Yes | Yes |
| Custom semantics | Good enough | Full control |
| Fits 7 weeks with 6 engineers | Tight but plausible | No |

In-house only wins when delivery is the product you sell, or when third-party code is also ruled out. Neither applies. Legal's rule covers data transit, not open-source software running on your own infrastructure.

**Confirm that last point with legal in writing this week.** "Self-hosted OSS on our own infrastructure is not a third-party processor" is my reading, not theirs. If it's wrong, the fallback is in-house and the date moves. You'd tell the board that now, not in week 6.

## 3. What a gateway doesn't buy you

The skill is explicit that buying or hosting infrastructure gets you the machinery, not the design. Your six engineers still own all of this:

- **Event taxonomy and catalog**: `resource.action`, past tense (`payslip.finalized`), with a schema for each event.
- **Envelope and versioning**: pick one versioning camp. Additive-only evolution is simpler for a launch.
- **Signing**: Standard Webhooks (`webhook-id`, `webhook-timestamp`, `webhook-signature`), HMAC-SHA256 over `id.timestamp.body`, multiple active secrets for rotation.
- **Delivery contract**: at-least-once, best-effort ordering, a stable event ID across retries, a ~10s ack timeout.
- **Retries**: a fixed exponential schedule spanning about a day. Svix's 8 attempts over ~27.5h is the reference. Non-retriable 4xx go straight to the DLQ, and `Retry-After` on 429 is honored.
- **Subscription states**: active, paused, disabled.
- **Portal**: delivery logs, replay, send-test-event.
- **Docs**: five-element rubric.

Check whether the gateway you pick supports each of these. Anything it lacks becomes a gap you build in front of it.

## 4. Risks to plan for

- **No on-call is the real constraint.** A self-hosted gateway is a stateful production system: a queue plus a database. Webhook delivery failures in payroll are customer-visible. Before launch, set up a minimal on-call, even a 6-person weekly rotation with a short runbook. Without that, "self-hosted" really means "unowned".
- **Seven weeks is tight.** Scope the launch to a small event set. The catalog design and docs are likely the critical path, not the deploy.
- **The managed fallback is closed.** If the gateway disappoints in week 3, the only way out is in-house, which doesn't fit the date. Run a one-week spike first (see the plan below) and treat its result as the go/no-go.
- **Thin payloads (my judgment, not the skill's).** For German payroll data, consider IDs only plus an authenticated API fetch. This keeps personal data off partner endpoints and logs. It also sidesteps payload versioning. Check with legal and your DPO.

## 5. Seven-week shape

1. **Week 1**: legal sign-off on self-hosted OSS. Spike two gateway candidates against the contract above, covering retries, DLQ, signing, per-endpoint isolation, and the license. Pick one.
2. **Weeks 2-3**: deploy to staging, define the catalog and signing, and stand up the on-call rotation and runbook.
3. **Weeks 3-5**: integrate event emission, the subscription API, and the portal (logs, replay, test events).
4. **Weeks 5-6**: docs against the rubric, partner beta, and a failure-injection test of the DLQ and replay path.
5. **Week 7**: buffer. Don't plan to use it up.

## 6. Questions I assumed answers to

I didn't have these, so my assumptions could be wrong:

- Is this greenfield? I assumed yes.
- How many partner endpoints at launch? I assumed tens, not thousands. At thousands, the circuit-breaker rung comes into play.
- Which consumer types? I assumed enterprise partners, so they will ask for a written contract and asymmetric signing later.
- Is any of the need real-time client push? I assumed no.

**Re-rank triggers**:

- If endpoints grow into the thousands or partners negotiate delivery SLAs, move to configurable retries plus a circuit breaker.
- If legal later signs a DPA, re-open managed.