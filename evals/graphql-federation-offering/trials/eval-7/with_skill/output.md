# Spec: `Prescription.verdanePricing` (Verdane Rx live pricing)

## Verdict

**Do not build `@requires(fields: "patient { dateOfBirth address }")` as written.** The patient's date of birth and home address would go to a US-hosted partner. That would happen once per prescription row, about 50 times per dashboard page, and the clinician would not have to ask for it. Under the skill's data-clearance rule, that pair fails the regulated-data gate today.

This spec keeps the field but changes the mechanism. Saltreed Care runs the call to Verdane and sends only a coarse, derived input.

## 1. Need classification

Verdane computes a price live, so this is **live data computed by the partner**. That leaves rungs 3–5 standing and removes rungs 0–2. The skill's "stored data plus events" check does not apply, because the price depends on the day, the patient's coverage and stock.

## 2. Rung choice: rung 3, platform-operated connector

Rankings, re-emitted for rungs 3–5 only:

- **Efficiency:** `platform-operated connector > mediated extension field > isolated partner subgraph`
- **Effort, highest first:** `isolated partner subgraph > mediated extension field > platform-operated connector`
- **Value (live partner data in one query):** `isolated partner subgraph == mediated extension field > platform-operated connector`
- **Compliance cost, highest first:** `isolated partner subgraph > mediated extension field > platform-operated connector`
- **Durability:** `platform-operated connector > mediated extension field > isolated partner subgraph`

What moved the ranking:

- **One partner under contract:** rung 3 is the default for live data from a few partners with existing APIs. A single partner does not push you toward rung 4's self-serve proxy.
- **Build starts next sprint (interview Q7):** this promotes rung 3, because the platform builds it without Verdane engineering.
- **Personal and regulated data (Q4):** this favours the rung where the platform writes the schema and decides what leaves.
- **Rung 5 is not warranted:** it only pays off when partner fields need joint planning across several platform entities. This is one field on one entity.

**Promotion condition:** move to rung 4 if more pharmacy partners want the same field. Move to rung 5 only if a strategic partner must shape fields across several entities. In both cases Verdane never joins the first-party production supergraph. A partner subgraph there is refused outright.

Where the plan used `@requires` in "their partner field", a federation `@requires` in the partner's SDL would mean Verdane ships a subgraph. At rung 3 the `@requires` sits in a **Saltreed-owned** subgraph, and Verdane only ever sees an HTTP call.

## 3. Contract: namespace and shape

Rung 3 applies only the namespace rule from step 3, because the platform writes the mapping.

```graphql
# Saltreed-owned connector subgraph. Field names are illustrative; match your real schema.

type Patient @key(fields: "id") {
  id: ID!
  # Derived, coarser fields. Hidden from the public API schema.
  pricingAgeBand: AgeBand @inaccessible       # UNDER_18, 18_29, ... 65_PLUS
  pricingRegion: String   @inaccessible       # region code only, e.g. DE-BY, FR-PDL, ES-AN
}

type Prescription @key(fields: "id") {
  id: ID!
  medicationCode: String @external   # PZN (DE), CIP (FR), CN (ES)
  quantity: Int          @external
  patient: Patient       @external

  """Provided by Verdane Rx. Not covered by the Saltreed Care SLA."""
  verdanePricing: Verdane_Pricing
    @requiresScopes(scopes: [["partner:verdane"]])
    @requires(fields: "medicationCode quantity patient { pricingAgeBand pricingRegion }")
}

type Verdane_Pricing {
  status: Verdane_PricingStatus!
  currency: String!              # ISO 4217, validated
  grossPriceMinor: Int           # minor units, validated
  patientCopayMinor: Int
  coveredMinor: Int
  quotedAt: DateTime!
  detailsUrl: URL                # https only, host-checked
}

enum Verdane_PricingStatus { QUOTED NOT_COVERED NOT_AVAILABLE }
```

Rules this encodes:

- **Prefixed and nullable:** the type is `Verdane_`-prefixed, and `verdanePricing` is **nullable** on `Prescription`. A Verdane outage gives `null` plus a masked error, never a blank prescription.
- **Platform-typed, partner-valued:** Saltreed owns the envelope. Every Verdane value is validated as untrusted input before it reaches the schema (currency code, integer minor units, https-only link).
- **`@inaccessible` is platform-side only:** the directive is yours, on your own derived fields. The skill's policy bans it only in partner SDL.
- **Verify in staging:** confirm that your composition version lets the connector `@requires` an `@inaccessible` field.
- **Errors:** mask Verdane errors to `PARTNER_UNAVAILABLE` plus the partner ID `verdane`. Never pass Verdane `extensions` to clients.

## 4. Data-clearance list (what Verdane receives)

| Field sent | Why Verdane needs it | Status |
| --- | --- | --- |
| `medicationCode`, `quantity` | The price depends on the product | **Cleared only with consent.** A medication tied to a patient is health data. |
| `pricingAgeBand` | Coverage rules usually depend on age band, not birthday | Cleared with consent |
| `pricingRegion` (region code) | Scheme and reimbursement differ by region, not by street | Cleared with consent |
| Opaque per-tenant request reference (HMAC of the prescription ID) | Support correlation | Cleared |
| `dateOfBirth`, `address`, patient name, patient ID, clinic name | — | **Not sent** |

**Ask Verdane to justify the exact inputs.** If their engine truly needs the exact date of birth or the street address, escalate it as a separate decision. It would need all three of these first:

- tenant consent recorded at install
- signed data-processing terms
- a passed residency check

### Residency blocker (us-east-1)

Residency is the largest open risk, and it needs a decision before the sprint starts.

- **Cross-border transfer:** patient-linked medication data would leave the EU for the US. You need a valid transfer mechanism, either EU–US Data Privacy Framework certification by Verdane or standard contractual clauses.
- **Sub-processor status:** clinics are the data controllers. Verdane probably becomes a sub-processor of Saltreed Care, so clinics must be informed and able to object.
- **National health-data rules:** France has health-data hosting certification. Germany has professional-secrecy rules for clinic staff. Spain has its own data-protection law.
- **Pharmacy steering:** showing one pharmacy's prices in the clinic dashboard may raise pharmacy-steering questions in Germany.
- **Action:** have counsel confirm these points before launch. I am not giving legal conclusions.

**Cheapest fix:** ask Verdane for an EU endpoint, for example `eu-central-1` or `eu-west-3`. That solves most of the residency problem and removes about 90–100 ms of transatlantic round trip from every call. Without it, ship to no clinic until the transfer paperwork is done.

## 5. Credentials toward Verdane

- **No client credential reaches Verdane:** forward no end-user `Authorization`, no `Cookie` and no Saltreed API key.
- **Per-partner token:** mint a short-lived token (RFC 8693 token exchange). Bind it to audience `verdane`, to the installing tenant and to scope `pricing:quote`. Minting runs per request, in a router extension, a coprocessor or the egress proxy. A static header insert cannot carry a tenant-bound token.
- **Header allowlist, by name:** `content-type`, `accept`, `x-request-id` and the minted `authorization`. No catch-all propagation rule.
- **mTLS or signed requests:** Verdane's endpoint must authenticate every call. It reads tenant and scopes from the token, never from the payload.
- **Introspection:** it must answer `_service` and introspection only to Saltreed.
- **Egress:** Verdane's URL is registered by Saltreed, HTTPS only, public hosts only, re-validated on every DNS resolution. All calls leave through a dedicated egress proxy with a host allowlist.

## 6. Blast radius

**Pagination and `@requires` cost (50 rows per page)**

- A batched call carries up to 50 small rows, each with medication, quantity, age band and region. No row carries a date of birth or an address.
- **Ask Verdane for a batch endpoint.** Without one, you make 50 parallel calls per page, capped at 10 concurrent.
- **Recommended UX decision:** do not select `verdanePricing` in the 50-row list query by default. Load it on row expand or in the detail query. Every list view would otherwise send medication data for 50 patients, whether or not anyone reads the price.
- If product insists on pricing in the list, the batched call is the only acceptable shape. Also enforce `first ≤ 50` whenever the field is selected.

**Timeouts.** The formula is: client SLA, minus internal p95 up to the Verdane hop, minus a margin. The hop runs after the platform has fetched the `@requires` fields. Your SLA and internal p95 were not given, so these numbers are **assumptions to replace**:

| Setting | Value |
| --- | --- |
| Client SLA, prescription list query (assumed) | 1000 ms |
| Internal p95 to the Verdane hop (assumed) | 250 ms |
| Margin | 100 ms |
| **Per-partner timeout** | **650 ms** |
| **Request-level deadline** (a backstop above partner timeouts, never below) | **1200 ms** |

- **Defaults:** router defaults of 30–60 s must not apply to Verdane.
- **Circuit breaker, counting timeouts as failures:** starting values are open after 5 consecutive failures or a 50% error rate over a 20-request window. Stay open 30 s, then probe half-open. Where the router has none, put Verdane behind the egress proxy with outlier detection.
- **Suspension threshold:** the field leaves the schema variant if the circuit is open more than 1 hour in 24. Name the person who decides.
- **Cost model:** price `verdanePricing` in the query cost model. Rate-limit per tenant and globally for Verdane. Tune both from dashboard traffic.
- **Caching:** exclude Verdane responses from shared caches and from cross-request deduplication. If you cache quotes, key them per tenant and keep them private-scoped.

## 7. Who sees the field

- **Tenant gate:** only clinics that installed Verdane and gave recorded consent. The router checks `partner:verdane` at request time. Do not create a contract variant per install combination.
- **Role gate:** also restrict to the roles that may see prescription costs.
- **Schema filtering:** if you publish a partner-facing contract, filter with **include-only** rules. An exclude filter publishes every field nobody tagged.
- **Docstring:** the field docstring states "Provided by Verdane Rx. Not covered by the Saltreed Care SLA."

## 8. Lifecycle

1. **Publish:** Saltreed owns the schema and the mapping, so Verdane never holds publish rights. CI runs contract tests against a Verdane sandbox. Verdane gives advance notice of API changes, and a failing sandbox contract test blocks the release.
2. **Platform changes:** renaming a field on the clearance list, such as `medicationCode`, is a breaking change for the mapping. The notice window comes from the versioning policy.
3. **Partner changes:** a Verdane change that fails validation yields `null` plus an error. It never rolls the graph forward around it.
4. **Observe:** per-partner latency, error rate, timeout rate and circuit state, visible in response extensions. Name an owner and keep a status component for Verdane.
5. **Offboard:** run the removal-impact check and pull per-field usage over the notice window. Deprecate `verdanePricing`, keep it returning `null` through the window, then remove it.
6. **Uninstall:** a clinic that uninstalls Verdane immediately stops all calls. Define what happens to any cached quotes. The default is delete them.

## 9. Acceptance gates for the sprint

Each gate must pass in staging against a canary endpoint standing in for Verdane:

1. **Exposure:** the canary receives no date of birth, no address, no name and no patient ID. The field is nullable and invisible to tenants without the install.
2. **Credentials:** an echo canary shows no client `Authorization`, `Cookie` or platform key.
3. **Authentication:** a call with no credential, or another tenant's token, is rejected.
4. **Blast radius:** with the canary stalled, the list query returns prescription data plus a masked `verdanePricing` error within 1000 ms.
5. **Pagination:** a 50-row query selecting the field makes one batched call (or a capped number of calls) and sends only the cleared fields.
6. **Offboarding drill:** the removal-impact check runs before the field is removed.

## Decisions I need from you before the sprint

1. **Residency:** will Verdane provide an EU endpoint, or is the transfer paperwork in place? Without one of them, no launch.
2. **Inputs:** does Verdane's engine really need exact date of birth and address, or do age band and region suffice?
3. **Dashboard:** is pricing on row expand acceptable, or must it appear in the 50-row list?
4. **Latency:** what are your real client SLA and internal p95? I used 1000 ms and 250 ms.
5. **Stack:** which router and registry do you run? Does it have a circuit breaker?
6. **Markets:** does Verdane serve Germany, France and Spain at launch, or one country first?
7. **Notice period:** what window do you promise clinics before removing a field?

I did not write to `developer-platform-context.md`, because you did not ask me to. Once you settle the decisions above, I can record them in it.