# Nimbusgrid v2 API keys: format and leak response

## Verdict on the UUID argument

The 122-bit figure is right, but it answers the wrong question. A brute-force attack on the key was never the threat. What happened last month was a leak, and the UUID format fails there in three ways:

- **Nothing identifies it as a secret.** A bare UUIDv4 looks like a request ID, a database primary key or a trace ID. Secret scanners can't flag it without drowning in false positives. GitHub moved off hex-only tokens for this reason: they were "indistinguishable from other encoded data like SHA hashes."
- **Nobody can be told about it.** There is no prefix to register with GitHub's Secret Scanning Partner Program. Nimbusgrid never gets the webhook when a key lands in a public repo. That's how this one sat exploitable for three weeks until the customer's auditor caught it.
- **Nothing is known about how it's stored or scoped.** A UUID says nothing about type or environment. I also haven't seen how v1 keys are stored. If they're plaintext, that's a separate finding to fix now.

Emailing customers about hygiene does nothing about the format. It should happen alongside the fix, not instead of it.

One related point: the 122 bits are fine as raw entropy. The v2 body should still be generated from a CSPRNG at 120 bits or more. The 120-bit floor is a minimum, not the target.

**Assumptions.** You asked for a deliverable, so I didn't run the skill's interview. I'm assuming:

- Retrofit, with an unknown number of live v1 keys.
- Mostly server-to-server consumers, plus some CI.
- No PCI scope.
- Enterprise buyers may ask for SOC 2.
- A hard ship date.

Correct me if any of these are wrong. The scoping and storage choices below shift if they are.

## 1. The v2 key format

```
nbg_<type>_<env>_<30-char Base62 body><6-char CRC32 checksum>
```

Example: `nbg_sk_live_7Hq2...` (`live` or `test`).

- **Prefix `nbg_`.** It's unique and greppable. Register this pattern with GitHub's partner program.
- **Type segment.** `sk` is a secret key. `sa` is a service-account key. `rk` is a restricted key. Reserve a separate family for webhook signing secrets (`whsec_`-style), since those aren't API keys.
- **Environment segment.** `live` or `test` goes in the prefix from day one. It also serves a test-mode design.
- **Body.** 30 Base62 characters is about 178.6 bits, GitHub's benchmark. The floor is 120 bits and 32+ random characters.
- **Checksum.** 6 characters of CRC32. A validator can reject malformed keys with no database round-trip. Scanners can also filter noise before alerting. The cost is about 10 characters of key length, which is worth paying.
- **Transport.** Send it as `Authorization: Bearer`, HTTPS only.

### Storage

- Store only a SHA-256 hash. Show the full key once at creation. Never store plaintext.
- SHA-256 is right for high-entropy machine-generated keys. bcrypt and Argon2 defend low-entropy human passwords, and they cost CPU on every request for no gain here.
- Keep a short plaintext `key_prefix` column, indexed, for O(1) candidate lookup. Compare hashes in constant time.
- Table columns:
  - `owner_id`
  - `key_prefix`
  - `key_hash`
  - `name`
  - `scopes` (never empty-means-all)
  - `created_at`
  - `last_used_at`, written asynchronously
  - `expires_at`
- Fail secure: a missing signing secret crashes the service at startup. It never falls back to a default value.

### Scoping

- Issue one key per service per environment.
- Use coarse scopes, restrictive by default (read vs write, per product area). Never let omitted scopes mean full access.
- These two together take days of work. A leaked key then compromises one service, in one environment, with one permission set.
- Fine-grained per-resource scoping is a later promotion. Do it if enterprise or compliance demand it, or if you already have an RBAC system the scopes can reuse.

### Expiry and ownership

- Give keys an expiry, or a documented exemption.
- Support three ownership tiers: individual, organization, and service account. Production and CI default to service-account keys, so credentials don't depend on one person's employment.
- For CI, plan workload identity federation as the longer-term direction. It means no stored secret at all.
- Never ship a long-lived key to a browser. Mint a short-lived scoped token server-side instead.

### Rotation

- Make "roll" one atomic operation. It creates the new key and schedules the old one's expiry in a single call.
- Routine grace period: 24 hours to 7 days. Compromise or offboarding: zero grace.
- Never delete an old key until last-used telemetry shows zero traffic on it. Deactivate first and wait 24 to 48 hours.

### Dashboard

All four actions must work without a support ticket: sign up, create a key, rotate it, and revoke it. Each key shows a label, creation date, last-used time and status. After creation, keys are masked to their first and last few characters. 401 means authentication failed, and 403 means the key lacks scope.

## 2. What to do about leaks like that one

### Detect and revoke automatically

1. **Ship the prefix and checksum format** (above). Without it, nothing below works.
2. **Enroll in GitHub's Secret Scanning Partner Program.** Last month's incident is the justification. The steps are:
   - Email secret-scanning@github.com and agree to the terms.
   - Supply a detection regex and a test account.
   - Stand up a public HTTPS webhook endpoint.
   - Verify GitHub's ECDSA signatures (P-256, SHA-256).
   - Revoke the reported key and notify its owner.
   - Optionally return true/false-positive feedback.
3. **Treat every reported match as public and compromised.** Revoke with zero grace, notify the owner, and log the event. PCI-DSS 4.0 also requires immediate rotation on suspected compromise, if that regime ever applies to you.
4. **Add a customer-facing alert and a one-click "replace key"** so the owner can re-issue immediately.
5. Consider GitGuardian-style commercial scanning later for surfaces beyond GitHub.

With this in place, the time from leak to revocation drops from weeks to minutes.

### Handle the existing v1 keys

Auto-revocation can't help v1 keys, because a bare UUID gives the partner program nothing to match. Do these in order:

1. **Audit v1 storage now.** If keys are plaintext, hash them. A database leak is the same class of incident as a repo leak.
2. **Revoke the leaked key if you haven't.** The customer should issue a replacement and check usage logs for the three-week exposure window.
3. **Set a v1 sunset date.**
   - v2 and v1 run side by side. Issue v2 keys through the roll flow, so customers cut over without downtime.
   - The overlap window should be long, since v1 customers have no tooling to migrate.
   - Track last-used on v1 keys, then warn and finally disable the stragglers.
4. **Don't re-encode v1 UUIDs into the new format.** The old secrets stay unscannable and unrotated.

### Customer communication

Email still has a place, with three jobs:

- Announce v2 and the migration path.
- Tell customers how leak detection now works.
- Give practical hygiene guidance: use env vars and a secrets manager, use test keys in development, keep keys out of repos.

Hygiene advice alone would not have prevented last month's incident, but it complements the detection above.

## 3. Audit and compliance

Enterprise buyers will ask for a documented key lifecycle and evidence that it operates.

- Log every create, use, rotate and revoke with who, when and why.
- Enforce mandatory expiry and send expiry warnings.
- Keep an offboarding runbook: enumerate the leaver's keys, revoke them with zero grace, and rotate any shared credentials.
- For SOC 2 Type II, start generating evidence from day one. A policy adopted just before the audit fails by construction.
- If PCI-DSS 4.0 applies, Requirement 8.6.3 doesn't mandate a fixed interval. It requires a documented risk analysis to justify your cadence.

## 4. Success measures

Before calling v2 done, check these:

- No plaintext keys at rest, confirmed by a schema audit.
- Every live key has an owner, a scope, and an expiry or documented exemption.
- You've run a real zero-downtime roll end to end.
- All four self-service actions work without a ticket.

Track these from month one:

- Time from leak detection to revocation.
- Share of keys with last-used older than 90 days.
- Share of traffic on service-account keys vs personal keys.

## Open questions

- How are v1 keys stored today (plaintext, hashed or encrypted), and roughly how many are live?
- Are there PCI or SOC 2 commitments with a date attached?
- Do you have an existing RBAC system that scopes could reuse?
- What's the ship date? That decides whether fine-grained scoping lands in v2 or later.