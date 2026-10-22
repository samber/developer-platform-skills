# Where I'd push back on the Northvale partner program flow

The flow is clean because it's linear and puts control first. My main objection is that it spends your review effort at the start, where the risk is lowest, and leaves the end undefined, where the risk and the work are highest.

## 1. The 2-4 day company review blocks the wrong step

- A developer decides whether to build on you within hours. A multi-day wait before they can make one API call loses most of the casual and exploratory partners.
- A sandbox tenant with synthetic data exposes no customer data and no production system. The review protects nothing at that point.
- Vet at the point of risk instead: **production access**, **listing**, and **installation into a utility's tenant**.
- **Proposed change:**
  - Make sandbox self-serve and instant, with email verification and click-through sandbox terms.
  - Move the company review to the gate before production or listing.
- **Caveat:** if you must keep a gate up front (export control, sanctions screening), keep it narrow and automated. Don't do a manual 2-4 day review.

## 2. "Email them credentials" should go

- Secrets in email are a weak practice, and they're a bad look for a company selling to critical-infrastructure customers.
- Use a self-serve developer portal that issues sandbox client credentials with scoped permissions and rotation.
- Reserve human steps for production credentials.

## 3. Security review only at the end is a late surprise

- A partner who builds for weeks and then fails review on an architectural issue will churn, and may blame you.
- Publish the requirements on day one, as a checklist plus the scopes and data rules.
- Run automated checks during build: scope linting, dependency scanning, and secrets scanning on submission.
- Offer an early design review for apps that touch sensitive data.
- Tier the review depth by blast radius:
  - read-only versus write
  - customer PII
  - crew location data
  - anything adjacent to operational technology
- Commit to a review SLA and a defined resubmission loop. Otherwise review becomes your bottleneck, and the partner has no idea how long it will take.
- Utilities will ask what your review covers (for example NERC CIP exposure and their own vendor-risk questionnaires). Design it so your review output can answer those questions.

## 4. The plan stops where the hard part starts

Your flow ends at "submit for review." Not yet defined:

- **Customer authorization:** how a utility admin installs an app, which scopes they grant, and how they revoke it.
- **Distribution:** a marketplace listing, a private listing for a single utility, or both.
- **Production lifecycle:** API versioning, deprecation policy, and re-review when an app changes scope.
- **Commercials:** revenue share, who bills the utility, and who supports whom. Support ownership is the question utilities ask first.
- **Offboarding:** how you pull an app that has a security incident, and the partner's incident-notification duty.

## 5. One path assumes one partner type

These partners want different things, so they likely need different tracks:

- **Integrators** building custom work for one utility need fast access and a customer sponsor.
- **ISVs** with a product need a listing and a multi-tenant app model.
- **Utility in-house developers** may not be "partners" at all.

Decide who you're optimizing for first. Also decide what's in it for them, such as customer demand, co-selling, or access to your install base. Without that answer, the process design doesn't matter.

## 6. Sandbox realism and cost

- An empty tenant is useless for field service. Seed it with realistic work orders, assets, crews, and schedules.
- Provide event simulation and webhooks, plus a way to trigger status changes without a real mobile fleet.
- Decide on tenant expiry, cost per tenant, and rate limits now. Auto-provisioned tenants add up if nobody cleans them.

## 7. Legal timing

Click-through sandbox terms at signup, and a full partner agreement before production. Don't make partners negotiate a contract to try your API.

## Proposed flow

1. Sign up, verify email, accept sandbox terms.
2. Instantly get a sandbox tenant with seeded data and credentials from the portal.
3. Build against published security and data requirements, with automated checks along the way.
4. Optional early design review for sensitive scopes.
5. Apply for production or listing. This is where the company review, partner agreement, and tiered security review happen.
6. Customer-admin install flow, then ongoing monitoring, re-review on scope change, and revocation.

## How to start from zero

Don't build the whole machine first. Run it manually with 3-5 design partners and a shared channel. Record where they stall.

Track:

- time to first successful API call
- sandbox to submission rate
- review turnaround
- resubmission count

Automate only the steps that hurt.

## Questions that would change my advice

1. Who are the first partners: integrators, ISVs, or utilities' own developers?
2. Who staffs the security review, and what turnaround can they commit to?
3. Can partner apps write to work orders or touch crew location data, or are they read-only at launch?
4. Do utilities install apps themselves, or do you broker it?