# Ledgerhawk API key rotation design

I read the `api-auth-key-management` skill and its references. The skill says to ask clarifying questions first. This is a one-shot task, so I've stated my assumptions in section 1 and listed the answers that would change the design at the end.

## Verdict on the ops plan

Don't ship it. The 30-day rule isn't what auditors require, and the batch plan is likely to cause an outage across your tenants.

| Ops proposal | Problem | Replacement |
|---|---|---|
| Fresh keys for all 4,000 tenants in one batch | One cutover date for every tenant. Anything that goes wrong goes wrong 4,000 times at once, and the support queue spikes on the same day. | Tenant-initiated atomic **roll** plus staggered expiry (sections 3 and 4). |
| Email the new keys | A secret in a mailbox is a leak vector, and it sits in mail logs and forwards. The new key is shown once in the dashboard and never emailed. | Email carries notices only: expiry date, link, last-used telemetry. No secrets. |
| Disable all old keys the following Monday | The overlap is too short for slow consumers such as ERP connectors and nightly batch jobs. The date is also a problem on the calendar: the next 1st is Sunday 2026-11-01, so "the following Monday" is either 2026-11-02 (1 day of overlap) or 2026-11-09. It also ignores whether old keys still carry traffic. | Per-key expiry set by the tenant. Deletion only after last-used shows zero traffic. |
| "All keys rotate every 30 days" as a standing rule | No standard requires it (see below). At 4,000 tenants it creates 4,000 cutovers a month and trains customers to automate blindly or never rotate. | Mandatory expiry with a risk-based cadence (section 5). |

**What auditors actually check.**
- **SOC 2** (CC7.2, C1.2) prescribes no cadence. It wants a documented lifecycle policy for provisioning, rotation, revocation and destruction. It also wants evidence that the policy operates. Type II needs 3-12 months of that evidence.
- **PCI-DSS 4.0 Req. 8.6.3** names no fixed interval either. It requires a cadence justified by a documented targeted risk analysis (Req. 12.3.1), plus immediate rotation on suspected compromise. This applies only if you touch cardholder data, which an accounting API may not.
- **What enterprise security reviewers want** is a story they can verify. That means a documented policy, a real self-service rotation flow, mandatory expiry, and an audit log.

## 1. Assumptions and preconditions

This is a retrofit. I'm assuming:
- Today's keys are one long-lived key per tenant.
- They have no expiry.
- They may not be prefixed or hashed.

**Preconditions.** Rotation can't work without these three, so build them first:
1. Storage that allows two simultaneously valid keys per identity. That means an `expires_at` column and no unique-active-key constraint.
2. Last-used telemetry, written asynchronously and fire-and-forget, never blocking the request path.
3. Hash-only storage. If today's keys are plaintext or reversibly encrypted, hash them first (SHA-256, constant-time compare, indexed plaintext `key_prefix`). Audit the schema to prove no plaintext remains. Rotating plaintext keys only moves the exposure around.

## 2. Key format

New keys use `lh_live_` or `lh_test_`, then a random body of at least 120 bits (about 30 Base62 characters), then a CRC32 checksum. The prefix encodes type and environment. The checksum lets the gateway reject malformed keys without a database round trip and lets secret scanners filter noise.

Legacy keys keep working until they are rolled. Rolling replaces them with the new format, so rotation also migrates the format with no separate project.

## 3. The rotation mechanism

**Atomic roll.** One operation creates the new key and sets the old key's expiry. There are never two manual steps. Every key is in one of three states: `active`, `expiring` (old key inside its grace window) or `revoked`. Keep at most two active keys per key identity, as AWS IAM does, so overlap is forced and keys can't sprawl.

**Grace windows.**

| Scenario | Overlap |
|---|---|
| Routine roll, default | 14 days. Accounting integrations (ERP connectors, nightly batch jobs) sit on slow release trains. |
| Routine roll, tenant choice | 1 day to 14 days. If last-used still shows traffic near the end, the system warns and offers an extension rather than breaking a live consumer. |
| Suspected or confirmed compromise, or offboarding | Zero. Revoke immediately and accept the downtime. |
| Tenants with queued or agent workloads | Suggest the upper end of the range. |

**Per-roll runbook:**
1. The tenant admin rolls the key in the dashboard, picks the window, and re-authenticates with 2FA. The new key is shown once.
2. A notification email goes out with the old key's exact expiry timestamp and a link to its last-used telemetry. No secret is included.
3. The tenant cuts over, staging first, then production, then queued workloads.
4. Ledgerhawk watches the old key's traffic. If the tenant has not moved by 2 days before expiry, send an alert.
5. At expiry the old key is **deactivated, not deleted**. It must show zero traffic first. Wait 24-48 hours, then delete. Deactivation is reversible and deletion is not.
6. Every step is logged: who, when, window chosen, cutover confirmed.

**Two invariants.** Never delete an old key before last-used shows zero traffic, because that causes an outage. Never create a new key without scheduling the old one's revocation, because that doubles your attack surface.

## 4. Migrating the existing ~4,000 tenants

Replace the single batch with a staggered migration:

1. **Ship first** the roll operation, the dashboard (section 6), last-used telemetry and audit logging. Nothing else starts until these exist.
2. **Run one real rotation end-to-end** with an internal tenant and 2-3 design partners. Confirm zero downtime and zero traffic on the old key before deletion. This is also your first piece of SOC 2 evidence.
3. **Assign expiry to every legacy key** in cohorts, jittered across a roughly 90-180 day span, not on one date. Cohort by tenant tier, with enterprise prospects who are blocked on this first. Load then stays flat and support never sees a spike.
4. **Notify at 60, 30, 14 and 7 days** before each key's expiry. The email contains no secret. It links to the dashboard, where the tenant rolls the key themselves.
5. **Add a one-click "rotate now" nudge** for tenants who are ready early.
6. **Handle holdouts before enforcement.** A key that still carries traffic on its expiry date gets one extension and a direct outreach to the tenant. Only then does it expire.

## 5. Cadence policy: replace the blanket 30-day rule

Write this down. It is the policy artifact auditors will ask for.

| Key class | Policy |
|---|---|
| Production keys, default | **Mandatory expiry, 90 days maximum**, with warnings and forced-rotation reminders. No key is allowed to be non-expiring. |
| Tenant-selected shorter lifetime | Allowed. High-security tenants can set 30 days, which gives them the story without forcing it on everyone. |
| Service-to-service and automation keys | About 30 days, or better, short-lived tokens through OAuth client credentials. Any key that needs expiry, scopes and per-request revocation is the case where the skill says to adopt OAuth, not reinvent it. |
| Test keys (`lh_test_`) | Lower stakes. A longer lifetime is fine. |
| Any suspected compromise | Immediate, regardless of schedule. |

**Why 90 and not 30.** A 30-day rule means roughly 4,000 cutovers a month, each one a chance for an outage. Real customers respond by writing keys into config management with no review, or by ignoring the notices. Neither improves security.

The 90-day figure is a convention, not a standard. Back it with a short documented risk analysis: key blast radius, scoping, last-used monitoring, and the leak-detection pipeline. That is the 12.3.1-style document an auditor asks for, whichever regime applies.

**Why rotate at all with no breach.** GitGuardian found 64% of valid secrets leaked in 2022 were still valid years later. An undetected leak is the base case, and scheduled expiry is the only control that bounds it.

## 6. Self-service dashboard (what enterprise reviewers will click through)

All four actions must work without a support ticket: sign up, create a key, rotate a key, revoke a key.

- **List view:** label, creation date, last-used, status badge (active, expiring, revoked), and direct roll/revoke buttons.
- **Masking:** after creation, show only the first and last few characters. The full key appears once, in the creation modal.
- **Usage:** a separate per-key usage view from the last-used timestamp. One shows whether the key is alive, the other what it is doing.
- **Rate limits:** treat key-validation and key-creation endpoints like login endpoints, with rate limiting and brute-force protection.
- **Errors:** 401 for a key that fails authentication (expired or revoked), 403 for a valid key without the scope.

## 7. Ownership, scoping and offboarding

- **Owner tiers:** support individual keys for experiments and org-owned or service-account keys for production. Default production to service-account or org-owned keys, so credentials don't depend on one person's employment.
- **Scoping:** one key per service per environment, with restrictive-by-default scopes (read versus write, per product area). Omitting scopes must never mean full access.
- **Admin view:** org admins get a filterable list of every key a specific user created, so offboarding is executable.
- **Offboarding runbook:** enumerate the leaver's keys, revoke each with zero grace, rotate any shared credential they could see, and log it.
- **Production on a personal key** is a standing incident. Migrate it to a service account.

## 8. Evidence and governance

Build these into the product, because building them produces the audit evidence:
- An **audit log** of every create, use, roll and revoke, with who, when, and why. Retain it at least 12 months, with the latest 3 months immediately accessible, so the same log works if PCI ever applies.
- **Expiry warnings and forced-rotation reminders**, which are the evidence that rotation happened without relying on anyone's memory.
- A **documented lifecycle policy**: provisioning, rotation, revocation, destruction.
- **Periodic access reviews** of who can create and revoke keys.

Type II needs 3-12 months of continuous operation. A policy adopted the week before the audit fails by construction, so start generating evidence on day one.

## 9. Gates (iterate until all pass)

- **Storage:** 100% of keys hashed, with no plaintext at rest, verified by schema audit.
- **Inventory:** every live key has an owner, a scope, and an expiry.
- **Rotation:** one real key has been rolled with zero downtime, and the old key was confirmed at zero traffic before deletion.
- **Self-service:** all four actions work without a ticket.

Trends to baseline in month one: time from leak detection to revocation, the share of keys with last-used older than 90 days, and the share of traffic on service-account keys versus personal keys.

## Open questions

These would change the design:
1. How are keys stored today (plaintext, hashed, encrypted)? This sets the preconditions in section 1.
2. Do you handle cardholder data? If yes, PCI 8.6.3 and the 12.3.1 risk analysis become mandatory.
3. Do third-party apps act on behalf of your tenants' users? If yes, hand that surface to OAuth.
4. Is there an RBAC system that key scopes can reuse? That would make fine-grained scoping cheap.
5. What is your ship date? A hard date promotes the cheap rungs: hash-only storage and a per-environment key split.

I did not check the evals file, and I did not run or test any of this.