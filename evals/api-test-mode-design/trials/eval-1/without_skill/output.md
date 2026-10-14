# Recommendation: build test mode inside your existing platform, in about 4 weeks

Don't build a separate sandbox, and don't just publish a doc. Ship a **test mode**, selected by API key, on your current API and checkout hosts. It should be isolated at the data and processor layers, and it should be self-serve.

I haven't seen your architecture. This rests on what you described, and the assumptions are listed at the end.

## Do this first, this week

Stop real corporate cards being used in staging. This is urgent whatever else you decide.

- Real card numbers in a shared environment put that environment in PCI scope.
- Partner developers' mistakes become real charges and real refunds on your card.
- Your biggest prospect's security review will find it.
- Block real PANs on staging, purge any stored ones, and rotate the card if it was shared with partners.

This is also why the "just write a doc" option fails. "Be careful with test data" is not a control, and a doc can't give a partner a way to test a failed payout.

## Why not the other two options

**A full separate sandbox with its own hosts and accounts (two quarters).**
- It misses the 6-week deadline by about three months.
- It duplicates infrastructure you'll then maintain forever, and it drifts from production.
- Large platforms built that after they had dedicated platform teams. Your goal is a safe place to integrate, not a copy of production.

**A doc telling partners to create a separate account.**
- Partners would still move real money, or use real cards, on real rails.
- Payment failures can't be tested. Declines, 3DS challenges, disputes, payout returns and vendor KYC failures are what integrators spend most of their time on.
- The logistics platform's compliance team will probably refuse to put real cards in its integration tests.

## What to build

Both engineers are right about something. The sandbox advocate is right that isolation matters. The doc advocate is right that you shouldn't build a parallel world. Test mode gives you both.

### 1. Mode is determined by the key

- Issue `test` and `live` key pairs per account, for example `sk_test_…` and `sk_live_…`. Both work against the same API host.
- Store a `livemode` flag on every resource: payments, vendors, payouts, ledger entries, webhooks.
- A test key can never read or write a live object, and the reverse holds too. Enforce this in one middleware layer plus a database-level check, not in each endpoint.
- Keep test data in separate tables or schemas. This is the hard requirement, because a leak between modes is the one failure you can't afford.

### 2. A simulated processor behind your existing adapter

- In test mode, route to a fake acquirer and bank-rails adapter. It has no live credentials and no network path to real rails, so test mode physically cannot move money.
- Support **magic values**, which are what integrators actually need:
  - **Card numbers:** success, generic decline, insufficient funds, 3DS required, 3DS fails, disputed later.
  - **Vendor onboarding:** KYC pass, fail, pending, needs more info.
  - **Payouts:** success, delayed, failed, returned.
- Reject real PANs in test mode, and reject test PANs in live mode.
- Add one endpoint or dashboard control to advance simulated time. Payout settlement then doesn't take days.

### 3. Hosted checkout in test mode

- Same page, driven by a test publishable key.
- Show a clear "Test mode" banner.
- Accept only test cards.

### 4. Webhooks and the dashboard

- Deliver webhooks for test events the same way as live ones.
- Add a "replay event" button.
- Let a partner sign up and get test keys instantly, without KYC.

### 5. Docs

- Write a quickstart that gets from zero to a successful test payment and a test vendor payout in under 30 minutes.
- Add a reference table of the magic values.
- This is where the doc advocate's work goes. It is a core part of the deliverable.

## Six-week plan with 4 engineers

| Weeks | Work | Owner |
|---|---|---|
| 1 | Block real cards on staging. Design `livemode` partitioning and key issuance. | Sandbox advocate leads, with CTO review |
| 1-3 | `livemode` flag, middleware enforcement, separate data partitions | Sandbox advocate + 1 backend engineer |
| 2-4 | Simulated processor, magic values, time-advance control | Backend engineer |
| 3-4 | Hosted checkout test mode, webhook delivery, self-serve test keys | Fourth engineer |
| 2-5 | Quickstart, magic-value reference, example integration | Doc advocate |
| 4 | **Hand the logistics platform's developers test keys** and start their integration. Fix what they find. | Whole team |
| 5-6 | Pilot feedback, hardening, a leak test between modes | Whole team |

The partner's developers should start in week 4, not at the end of week 6. That leaves two weeks of buffer against the deadline, and it makes the commitment measurable.

## Leave out of the first release

- Separate hosts and domains
- A full production-parity environment
- Load testing infrastructure
- A multi-region sandbox

Revisit these only if a concrete trigger appears. Examples are a partner contract that requires a separate hostname, a partner needing load tests, or evidence that mode leakage can't be contained at the data layer.

## Success checks before you call it done

- A test key fails against every live resource ID, and a live key fails against every test one. Automate this as a test over all endpoints.
- No code path from test mode can reach real acquirer or bank credentials.
- A developer outside your team, preferably from the prospect, completes the quickstart unaided.
- The staging card has been purged and rotated.

## Assumptions to check

- Your acquirer or bank integration sits behind an adapter you can swap. If it doesn't, add about one week for that refactor.
- Your datastore can partition by `livemode` without a migration of every table.
- The prospect needs card and payout testing only, not custom bank rails. If they need a specific rail simulated, scope that early.

If any of these are false, the plan still holds, but the estimate moves from 4 weeks to roughly 5 or 6. That is still inside the deadline, and it is still far shorter than a two-quarter sandbox.