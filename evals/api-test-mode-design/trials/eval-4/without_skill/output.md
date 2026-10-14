# Ledgerlink sandbox v2: seeding and error testing

**Recommendation:** don't seed from production records. Generate synthetic personas, isolate each integrator in its own sandbox tenant, and replace the global `/sandbox/force_error` with per-request error simulation.

## 1. Seeding: replace the production export with synthetic data

### Why the export plan fails

- **Scrubbing names and emails is pseudonymization, not anonymization.**
  - Transaction histories identify people on their own: employer names in payroll deposits, rent amounts, recurring merchants, and home and work geography.
  - Free-text memos often contain names (P2P transfers, "Rent - J. Smith").
  - Account and routing fragments can survive in descriptions.
  - A unique income-and-merchant pattern re-identifies someone to anyone who knows them.
- **The consent and purpose problem is separate.** Those users shared data so their own fintech app could work. Handing 50,000 of their histories to every integrator is a new disclosure to third parties for a new purpose. It likely breaks your end-user terms, your upstream bank and data-provider contracts, and GDPR/GLBA/CCPA-style purpose limitation. Legal should confirm, but assume the answer is no.
- **The blast radius is high.** Sandboxes get weaker auth, loose logging, and screenshots in public issues. A leak here is a reportable breach of real people's financial data.
- **It doesn't solve the actual ask.** Integrators want gig workers, small businesses, joint accounts, and thin-file students. A random 50,000-account sample under-represents those shapes, and you can't select for them without profiling real customers.

### What to do instead

1. **Build a scenario-driven generator.** Each persona is a declarative spec, and the generator is seeded so output is deterministic.
2. **Calibrate with aggregates, never records.** Pull only distribution statistics from production: income cadence, balance percentiles, transactions per month by category, overdraft frequency. Apply minimum-cohort thresholds (for example, suppress any cell with fewer than 50 accounts) before using them.
3. **Validate by comparison.** Check that synthetic aggregate statistics roughly match production aggregates, and that no synthetic record has a production counterpart.
4. **Generate dates relative to "now"**, so histories never look stale. Otherwise "last 90 days" quietly becomes "last 90 days as of 2026".

### Persona catalog (v1)

| Persona | Shape to generate |
|---|---|
| Gig worker | 3 irregular income streams (platform payouts weekly, a freelance invoice monthly, occasional cash-app deposits), lumpy balances, fees and instant-cashout charges, quarterly tax transfers |
| Small business | Separate operating and tax accounts; payroll out, customer deposits in, card processor settlements with fees, a seasonal revenue dip, an occasional NSF or returned item |
| Joint account | Two account holders with distinct ownership records, each with their own deposits and spending, shared bills, one holder removed mid-history |
| Thin-file student | Under 6 months of history, small balances, few transactions, family transfers, a stipend, no credit products |

Add edge-case traits that apply to any persona:

- pending-to-posted transitions
- reversals and duplicate postings
- overdraft
- multi-currency
- a dormant account
- an account with a closed status

### How integrators consume it

- **Named golden accounts.** These are fixed, documented, and identical for everyone: `gig_worker_01`, `student_thin_01`, and so on. They give reproducible docs examples and bug reports.
- **On-demand generation.** `POST /sandbox/accounts` with `{persona, seed, months, traits[]}` returns a new account with deterministic data for that seed. This is the answer to the recurring "accounts shaped like our end users" request. Integrators can also submit a custom spec (income streams, cadence, amounts) without waiting on you.
- **Version the generator.** Pin `generator_version` so a seed keeps producing the same data after you improve it.

## 2. Tenancy and cleanup: don't share one sandbox

"One shared sandbox, no cleanup" breaks as soon as integrators write. Linking accounts, creating transfers, and registering webhooks are all writes. Without isolation:

- One integrator's test run changes another's balances.
- A forced error can hit someone else's request (see section 3).
- One integrator can read another's data, which is a tenant-isolation bug in a product you sell on security.
- Storage and noise grow without bound.

Do this instead:

1. **Keep an immutable seed snapshot** of the golden accounts and persona templates.
2. **Give each integrator a sandbox tenant** with copy-on-write over the snapshot. Per-tenant API keys, per-tenant data, and per-tenant webhooks.
3. **Add a cheap reset:** `POST /sandbox/reset` drops the tenant's overlay and returns it to the snapshot.
4. **Set a TTL and quotas.** Expire generated accounts after about 30 days idle, and cap accounts, requests, and webhook endpoints per tenant. A small sweeper job is still needed. Read-mostly doesn't mean read-only.

## 3. Error testing: replace `/sandbox/force_error?code=X`

### Problems with the current design

- **"Whatever call comes next" is a global race.** With a shared sandbox, the next call may be a stranger's. Even per-tenant, a background webhook or retry can consume the armed error instead of the call under test.
- **A GET that changes state** gets cached, prefetched, and retried by clients and proxies.
- **There is no scoping.** Integrators can't say which endpoint, which account, or how many times.
- **An open `code=X` is unvalidated.** It invites codes that production never emits.

### Proposed design

Offer two mechanisms, in this order of preference:

1. **A per-request header (stateless, best default).** Example: `Ledgerlink-Sandbox-Simulate: error=ITEM_LOGIN_REQUIRED`. It applies to that single request only. There is no race, no state, and it's trivially parallel-safe.
2. **Magic test accounts and values (works from UI-driven flows).** Dedicated golden accounts behave deterministically: `err_login_required`, `err_institution_down`, `err_rate_limited`, `err_partial_data`. This is the Stripe-test-card pattern. It covers cases where integrators can't set headers, such as hosted link flows.

For multi-step scenarios, such as "fail the next 2 balance calls, then succeed", add a **scoped, armed rule**:

```
POST /sandbox/error_rules
{ "endpoint": "/accounts/balance", "account_id": "...", "code": "RATE_LIMITED",
  "count": 2, "ttl_seconds": 300 }
```

Rules are tenant-scoped, matched on endpoint and account, consumed by count, auto-expiring, listable, and deletable.

### The error catalog

- **Allowlist the codes.** Allow only codes the real API can emit, and document each with its HTTP status, retryability, and sample body.
- **Cover more than hard failures:**
  - auth expired and re-consent required
  - institution unavailable
  - rate limiting with `Retry-After`
  - timeouts and added latency
  - 5xx errors
  - partial or paginated responses that break mid-page
  - stale data with an old `last_updated`
  - duplicate or out-of-order webhooks
  - malformed upstream payloads
- **Make error bodies identical to production's.** Otherwise integrators write handlers against a shape that doesn't exist.

### Safety

- The simulation code must be compiled out of, or hard-disabled in, the production build and gateway. Add a test that asserts the header and endpoint return 404 or are ignored in prod.
- Every simulated response carries a marker such as `X-Ledgerlink-Simulated: true`, so nobody mistakes it for a real failure in logs.

## 4. Rollout order

1. **Decide:** drop the production export. Get a legal sign-off note for the aggregate-statistics pull.
2. **Build the per-request error header** and the error catalog. This is small and unblocks integrators immediately.
3. **Move to tenant-isolated sandboxes** with snapshot and reset.
4. **Ship the generator** with the four personas and the golden accounts.
5. **Add on-demand generation** (`POST /sandbox/accounts`) and the scoped error rules.
6. **Verify:**
   - Cross-tenant read tests must fail.
   - Same seed must give the same data.
   - The sandbox hooks must be inert in production.

Open questions for you:

- Do integrators need to test webhooks end to end?
- Do you need multi-currency in v1?
- Do you want integrators to submit custom persona specs in v1, or only choose from your catalog?