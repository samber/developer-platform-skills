# Cross-border compliance and residency mechanics for bulk export

## What counts as a transfer (broader than engineers assume)

A GDPR cross-border transfer is any movement of personal data from the EEA to a third country - including cloud storage, **remote access**, and intra-group transfers. A support engineer in a non-EEA office querying an EEA customer's exported bucket is the same regulated event as copying the file across the border. Design "who can read this" and "where is this stored" as one question.

## The legal mechanisms, in GDPR's own preference order

1. **Adequacy decision (Art. 45)** - the EU has pre-certified the destination country; no extra paperwork.
2. **Appropriate safeguards (Art. 46)** - Standard Contractual Clauses or Binding Corporate Rules, the standard fallback. Since Schrems II (CJEU, 2020), SCCs alone are not enough: a **Transfer Impact Assessment** must document that the destination country's surveillance laws don't undermine the protection the clauses promise.
3. **Binding Corporate Rules (Art. 47)** - the intra-group variant.
4. **Derogations (Art. 49)** - narrow, case-by-case, last resort.

The stakes are concrete: Meta was fined €1.2 billion in 2023 specifically for cross-border transfer failures - the largest GDPR fine on record at the time.

## Architectural patterns, in the order a design should introduce them

1. **Region pinning / regional buckets** - keep EU customer data in EU regions so the transfer question is eliminated at the source. Every major platform (AWS, Snowflake, BigQuery) offers region selection as a first-class export setting; treat it the same way, from day one. The cost of not doing so is documented: Segment fully deprecated its Data Lakes product in the EU rather than retrofit SCCs onto a US-region design - retrofitting residency can cost the whole product.
2. **Regionalized key management (CMEK)** with policy blocks on cross-region key use - a key that never leaves the EU closes the "ciphertext moved, but it's encrypted so it doesn't count" loophole, which regulators do not accept as a substitute for a legal transfer mechanism.
3. **Pseudonymized replicas** - strip or tokenize identifying fields before a replica leaves its home region, so what crosses the border is no longer personal data under GDPR's own definition.
4. **Metadata replication with payload restriction** - replicate schema/metadata globally (not personal data) while payload access stays geographically restricted. Zero-copy sharing is structurally friendly to this by construction: Snowflake replicates data only into regions where a consumer exists, and BigQuery linked datasets stay inside the subscriber's own VPC perimeter rather than being copied out.
5. **Localization mandates are a separate, stricter category** - China's PIPL and Russian localization law can forbid the transfer outright for certain data classes, beyond anything SCCs or pseudonymization can satisfy. The precedented design outcomes are an in-country deployment or explicit non-availability: Stripe does not offer Data Pipeline to customers in India, citing data-localization requirements. "Not offered in region X" is a legitimate product decision with a named precedent.

## How this composes with the rest of the design

Compliance cost is a genuine ranking axis for this skill's menus, not a cosmetic one. A single global bucket chosen for engineering simplicity silently selects the SCC + TIA paperwork path for every EU customer, forever; region selection built in at stages 1-2 of the rollout mostly dissolves the question. State that trade-off in the design document explicitly - it is a choice being made either way, and only one version of it is visible.

Per-transfer documentation to include in the deliverable, for each delivery route that crosses a border, so the compliance review reads a table instead of reverse-engineering the architecture:

- Legal basis (adequacy / SCC+TIA / BCR).
- Data classes involved.
- Whether pseudonymization applies.
