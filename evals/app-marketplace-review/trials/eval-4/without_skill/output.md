# How deep should the app directory security review go?

**Short answer:** Don't run a Salesforce-style multi-week manual review. Do a lightweight, tiered review of about 8 engineer-hours up front, then about 1 hour per partner. Your engineer's 4 hours a week covers that comfortably.

## Why the CTO's analogy doesn't fit

- **Salesforce's review exists because AppExchange apps touch customer tenants.** They get OAuth access to customer orders, contacts and records, often with write access. The review protects customers' data from the partner.
- **Your directory has none of that.** Apps read public catalog and carrier-rate metadata. There are no orders, shipments or personal data, and no writes.
- **A malicious or sloppy partner app can't damage a customer.** There's nothing sensitive to leak and nothing to modify.
- **The risk sits on your side.** It's about abuse, scraping, load, and what your API accidentally exposes. A review of partner code doesn't address any of that.

A multi-week review would burn the engineer's time on the wrong threat. At 4 hours a week, it would also delay launch by months.

## What procurement actually wants

Procurement teams want evidence that the directory is run with care. They don't need Salesforce's process. Three cheap artifacts give them that:

1. A one-page "Directory security and data scope" statement. It says what the API exposes, that it's read-only, and that there's no customer or personal data.
2. Published listing criteria, so they can see the bar apps must meet.
3. A named security contact and a process for pulling a listing.

This does more for credibility than a long review, and it's honest about the real scope.

## Recommended review depth

### Phase 1: API-side hardening (about 4 hours, week 1)

This is where the real risk is.

- **Data audit (about 1.5 hours).** Confirm that nothing outside the intended public catalog and carrier-rate metadata is reachable. Check every field in every response, plus pagination, filters, and any ID-based lookups.
- **Authorization (about 1 hour).**
  - Use per-app API keys, not a shared key.
  - Enforce read-only at the credential level, not just by convention. Confirm that POST, PUT, PATCH and DELETE return 405 or 403.
- **Abuse controls (about 1 hour).** Set per-key rate limits and quotas, and confirm you can revoke a key instantly.
- **Basics (about 30 minutes).** Check TLS-only, no secrets in URLs, no verbose error leakage, and that logs record key ID and endpoint.

### Phase 2: Partner listing process (about 4 hours, week 2)

- **Self-attestation form (about 10 questions).** Cover:
  - company identity and contact
  - privacy policy URL
  - how the app stores its API key (server-side, never shipped in client code)
  - what it does with the data
  - a commitment to your terms
- **Light manual check per app (about 30–60 minutes).**
  - Verify the company is real.
  - Verify the key isn't exposed in a client bundle or public repo.
  - Verify the app stays within your rate limits.
  - Check the branding for trademark misuse.
- **Written terms.** Include a right to revoke keys and delist.

### Ongoing

- About 1 hour per new partner.
- About 1 hour a month to review usage anomalies and revoke bad actors.

## What to skip

- Penetration-testing partner apps.
- Source-code review of partner apps.
- A formal security-questionnaire gauntlet (SOC 2 evidence, pen-test reports) from partners. That would filter out small, legitimate partners and add no real protection for read-only public data.

## Two checks that could change the answer

1. **Is the carrier-rate metadata really public?** If any of it reflects negotiated or customer-specific rates, it's commercially sensitive. Move the data audit to the front and make it much more thorough.
2. **Is the catalog identical for every caller?** If responses vary by customer, the "no customer data" claim needs verifying. Do this in the data audit.

## Triggers to move up a tier

Revisit the depth, with a heavier review, if any of these happen:

- Apps get OAuth access to customer tenants.
- Any write scope is added.
- Customer orders, shipments or personal data become reachable.
- Partners start embedding in your own UI (for example iframes or SSO).

At that point a Salesforce-like review starts to make sense. Tell the CTO this upfront: the review depth is tied to the data and permissions exposed, and it will scale up when they do.

## Suggested line for the CTO

> "Salesforce reviews deeply because its apps can read and write customer data. Ours can't. We'll harden the API, publish clear scope and listing criteria, and review each partner proportionally. If scope grows to customer data or write access, we'll move to a deeper review before enabling it."

## Caveat

I haven't seen your API, so this assumes it matches your description. The Phase 1 data audit is what verifies that assumption. Treat it as the gate for launch.