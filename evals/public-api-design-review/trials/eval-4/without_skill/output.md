**Decision: /billing-internal does not need the partner-API design review. It needs a lighter review, plus a written trigger that moves it onto the full review if its situation changes.**

**Why the full review doesn't fit**

A public-API review exists to protect things an internal API doesn't have:
- **Unknown consumers.** Partners can't be told to upgrade, so the contract has to be right before they depend on it.
- **Compatibility and versioning.** Breaking a public endpoint breaks outside businesses.
- **External abuse surface.** Rate limits, tenancy isolation, and docs all matter for outside callers.

Here, both consumers (the web app and the nightly batch job) live in your monorepo and ship under your control. A breaking change is one PR that updates the producer and both consumers, and CI catches any mismatch. Fixing a bad design later is cheap, and an alpha is the stage where you want to find that out. A blocking gate would add cost without reducing the risk it was built for.

**What it does need**

The API handles billing, so skipping review entirely would also be wrong. Before the first production deploy, require:
1. **A one-page design note.** It names the consumers, the auth model, and the money invariants: idempotency, retry safety for the batch job, rounding and currency, and what happens on a partial batch failure.
2. **One review from the billing owner and one security pass.** The security pass checks that the service is not reachable from public ingress, that service-to-service auth is enforced (not just assumed), and that sensitive data is not logged. This is hours of work, not a gate that blocks for weeks.
3. **Shared types or contract tests in the monorepo.** Producer and consumers then can't drift apart.

After that, normal PR review applies. The architecture lead can be a named reviewer on the design note, which gives them real input without a veto over the deploy.

**When it moves to the full review**

"Internal permanently" is a claim, so write the exceptions down. Any one of these triggers the full public-API review before it ships:
- A consumer outside the monorepo or outside your deploy control, including another team's service or a partner.
- Any exposure through public ingress, a partner gateway, or an externally reachable URL.
- A move from alpha to GA with an external SLA or compatibility promise.
- A change of scope that adds non-billing data or new tenants.

**How to close the deadlock**

Record this as a short ADR: the review tier is set by who can call the API and who can't be told to upgrade, not by how important the data is. The lead gets the tripwires in writing, and the team gets a proportionate process. If Northmark's written policy explicitly requires the full review for every service API, that policy overrides this. I haven't seen it, so check the policy text first. If it only says "public" or "partner" APIs, this answer stands.