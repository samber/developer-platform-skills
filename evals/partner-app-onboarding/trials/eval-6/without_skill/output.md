# Decision: no-go on "live account + partner-mode flag". Go on a minimum-viable sandbox.

## Why the proposal fails

The "zero infra" saving is real, but the cost moves onto the thing Brindle sells: trust in how money moves.

1. **Partners will test on real rails.** Apps that move money between customers' sub-accounts need transfers, reversals, failed payouts and disputes tested. In a live account, each test is a real or near-real ledger entry. A partner's bug in a loop becomes a production incident.
2. **A flag is a policy, not an isolation boundary.** If "partner mode" is a column checked in application code, one missed check lets test activity reach a real customer's sub-account or a real PSP/bank call. Any such leak is a customer-money incident, and probably a compliance one.
3. **Partners can't test the failures that matter.** On live rails you can't force a declined transfer, an insufficient balance, a delayed settlement or a webhook retry storm. Partners will ship without testing those paths and find out in production, with your customers' money.
4. **Production gets polluted.** Test traffic lands in your ledger, reconciliation, reporting, fraud models, rate limits and audit trails. Finance and compliance will want it filtered out, and that work is hard to do retroactively.
5. **Access to live data.** Six outside teams working in live accounts raises the question of what real customer data they can see. That is a security review and contract question, not a quick launch.
6. **"Build proper sandboxes later" is the expensive part.** Once 6 partners have integrated against live keys, live URLs and live behavior, the later sandbox is a migration, not a launch. Partners won't love it and you'll carry both modes.

## What to do instead: a thin sandbox, scoped to about the same effort as the flag

You don't need Stripe-grade test mode on day one. You need the flag to be enforced where money actually moves.

**Minimum bar. If engineering can't commit to all five, it stays no-go:**

1. **Separate credentials.** Test keys can't authenticate against live resources, and the reverse.
2. **Rail-level enforcement.** The flag is checked in the adapter that calls the PSP/bank, not in business logic. In test mode that adapter routes to a simulator and cannot make a real call.
3. **Separate ledger partition.** Test entries are physically or logically segregated and excluded from reconciliation and reporting.
4. **Partner-owned fake data only.** Partners get synthetic customers and sub-accounts, never your real customers' accounts.
5. **A simulator with scripted outcomes.** At minimum: success, decline, insufficient funds, delayed settlement, reversal, and webhook retry/duplicate. Magic amounts or magic account IDs are fine.

This is deliberately small: no dashboard, no self-serve provisioning, and no fidelity beyond the five behaviors above. A fixed-response simulator is days to a few weeks, not a quarter. The "partner mode" flag then becomes the on-switch for this path, which keeps the part of engineering's idea that is cheap and good.

## Handling the deadline and the 6 waiting partners

- **Start now:** onboard 1–2 partners on docs, API schemas and a mock server (a hosted stub or OpenAPI-driven mock) for UI and flow work. This costs almost nothing and is safe.
- **Staggered release:** open the remaining partners when the minimum bar above is met. Tell them the date.
- **Message to partners:** "Sandbox access opens on <date>. Until then, here's the API spec and a mock server so you can start building." Partners accept a short, dated wait. They don't accept a leak into customer funds.
- **Fallback if engineering can't hit the bar in time:** run a controlled pilot with 1–2 partners, with all of these in place:
  - written agreement and a security review
  - a dedicated internal partner org holding only your own funds, with low hard caps on amount and volume
  - monitoring on that org
  - no access to any real customer's sub-accounts

  This is a last resort, not the plan.

## Decision rule for leadership

- **Go** if engineering confirms the five-point bar and a date. This keeps the "start in minutes" feel for partners.
- **No-go** on any version where partners transact in accounts that can touch real customer sub-accounts or real rails.
- **Reopen the decision** if engineering shows the live-account design already satisfies items 1–5. At that point it is a sandbox under another name.

## Assumptions to confirm

- Brindle has no existing test mode or simulator. If one exists, this gets much cheaper.
- Real PSP/bank calls happen behind a single adapter layer. If they're scattered, item 2 gets harder.
- A licensed money-movement entity is involved, which makes the compliance risk in point 2 more severe.

Confirming the adapter-layer assumption with engineering is the most useful next step, because it sets the timeline.