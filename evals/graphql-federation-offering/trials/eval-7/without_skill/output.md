# Spec: `Prescription.pharmacyPricing` (Verdane Rx)

**Status:** draft for sprint planning. **Do not enable in production until the 5 gates in §6 clear.** Build against a mock Verdane in the meantime.

## 1. Two problems with the plan as written

**Problem 1: it sends health-linked PII to the US.**
- `@requires(fields: "patient { dateOfBirth address }")` makes the router send every patient's DOB and home address to Verdane's subgraph on every request that selects the field.
- Together with a prescription, that is special-category health data (GDPR Art. 9). The destination is us-east-1, outside the EU. Clinics in DE, FR and ES are the controllers, and they will ask about this.
- ⚠️ Check with your DPO and counsel. Likely issues: a transfer basis (EU-US Data Privacy Framework certification for Verdane, or SCCs plus a transfer impact assessment), an Art. 28 DPA chain, German medical-secrecy rules, and French HDS hosting rules. I am not certain how each applies here.

**Problem 2: the pricing engine probably doesn't need raw DOB and address.**
- Copay and coverage rules usually turn on age thresholds, country, region and coverage scheme. Examples are an 18+ cutoff in DE, regional copay in ES, and ratio or ALD status in FR.
- Ask Verdane for their exact rule inputs. Until they answer, assume derived values will do.

## 2. Recommended architecture

Make Saltreed own the field in our subgraph and call Verdane's pricing API server-side. Don't compose a Verdane-hosted subgraph into the public supergraph.

| Concern | Federated `@requires` | Saltreed-owned resolver (recommended) |
|---|---|---|
| What Verdane receives | Whatever the selection says, on every call | Only fields we choose, in one place |
| Their outage or schema change | Hits our public graph | Contained behind a circuit breaker |
| Third party in our supergraph | Yes | No |
| Auth, consent, caching | Split across two services | One resolver |

If you still want federation, keep the same contract below. `@requires` becomes `patient { ageBand region }` (new derived fields we publish), never `dateOfBirth` or `address`.

## 3. GraphQL contract

```graphql
extend type Prescription {
  """Live price quote from Verdane Rx. Never an error for partner trouble: check status."""
  pharmacyPricing: PharmacyPricing
    @requiresScopes(scopes: [["pharmacy:pricing:read"]])
}

type PharmacyPricing {
  status: PharmacyPricingStatus!
  listPrice: Money
  patientPays: Money
  insurerPays: Money
  quotedAt: DateTime!
  validUntil: DateTime
  """Version of Verdane's coverage rules, for support and audit."""
  ruleVersion: String
}

enum PharmacyPricingStatus {
  OK
  NOT_COVERED
  UNAVAILABLE        # timeout, breaker open, Verdane 5xx
  CONSENT_MISSING    # patient has not consented to pharmacy price lookup
  NOT_ENABLED        # clinic has not enabled the Verdane integration
  UNSUPPORTED_MEDICATION
}

type Money {
  amountMinor: Int!      # cents, avoids float rounding
  currency: CurrencyCode!
}
```

- Nullable field, with `status` for expected failures. One flaky partner must not null out a 50-row page.
- Scope gating hides the cost for clinics that haven't enabled it.

## 4. Data sent to Verdane

| Field | Source | Notes |
|---|---|---|
| `medicationCode` | Prescription | National code: CIP13 (FR), PZN (DE), CN (ES) |
| `quantity`, `dosageForm` | Prescription | |
| `countryCode` | Clinic | DE / FR / ES |
| `ageBand` | Derived from DOB on our side | Band edges at legal thresholds. Confirm with Verdane |
| `region` | Derived from address | Postal prefix or region code, no street |
| `coverageScheme` | Patient | Statutory insurer or scheme ID, if needed |
| `patientRef` | HMAC of patient ID, per partner | Pseudonymous, only for their idempotency or audit |

Never send name, street address, DOB, or free-text notes. Add a contract test asserting the outbound payload contains no key outside this list.

## 5. Pagination and performance (50 per page)

- **Batch:** one Verdane call per page, up to 50 lines. Never one call per prescription. us-east-1 from the EU is roughly 80-110 ms round trip, so 50 sequential calls would take about 5 s or more.
- **Verdane's batch limit:** confirm their max batch size and chunk if it is under 50.
- **Dedupe and cache:** key on `(medicationCode, quantity, ageBand, region, coverageScheme, ruleVersion)`. The key holds no PII and lets different patients share hits. Start with a 15 min TTL, tuned to how often Verdane prices change.
- **Don't block the dashboard:** load the list first, then fetch pricing via `@defer` or a second query by prescription IDs. Starting budget: 1.5 s per batch, then return `UNAVAILABLE`.
- **Resilience:** circuit breaker (for example 50% failures over 20 calls opens it for 30 s), limited retry on idempotent 5xx only, and a concurrency cap per clinic.
- **Cost guard:** this is a public API and each call costs money. Give the field a high query-complexity weight, rate limit per clinic, and cap `first` at 50 when `pharmacyPricing` is selected.

## 6. Gates before production (compliance, not code)

1. Verdane offers an EU endpoint, or has DPF certification, or SCCs plus a transfer impact assessment are done. **Ask for an EU region first**, since it removes most of the problem.
2. DPA with Verdane signed, with zero retention, no secondary use, and a sub-processor list.
3. Per-patient consent or another lawful basis confirmed per country. A consent flag gates the resolver (`CONSENT_MISSING`).
4. Clinic-side opt-in so the integration is off by default. Update clinic DPAs and the sub-processor notice.
5. Disclosure audit log: clinic, user, `patientRef`, fields sent, timestamp. It holds no raw PII.

## 7. Sprint breakdown

1. Schema, scope directive and mock Verdane server. ✅ unblocked.
2. Resolver with batching, dedupe cache, timeout and breaker.
3. Payload minimizer (`ageBand`, `region`) and the outbound contract test.
4. Consent and opt-in checks, and the audit log.
5. Load test: 50-row page, Verdane at p99 2 s, and Verdane down.
6. Observability: structured logs with no PII, latency and error metrics per status.

**Acceptance:** a page of 50 makes one outbound call. A Verdane outage still returns the page with `UNAVAILABLE`. No raw DOB or address appears in any outbound payload or log.

## 8. Questions that change the spec

1. Does Verdane run a federated subgraph, or only a REST/gRPC pricing API?
2. Which exact inputs do their rules need? Can they accept `ageBand` and `region`?
3. Can they serve from the EU?
4. What is their max batch size and p95 latency?
5. Is pricing per patient, or can quotes be shared across patients, given the cache key above?
6. Who pays per call, and is there a cap?

I assumed answers of "API only", "bands are fine" and "batch of 50 works". Items 1-3 are the ones most likely to change the design.