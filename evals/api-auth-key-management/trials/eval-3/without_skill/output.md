# Ledgerhawk API key rotation design

## Verdict

Don't ship the ops plan. Build overlapping keys first, then roll out in waves. Replace "30 days for everyone" with a policy each tenant can configure.

**First action:** ship multi-key support with `last_used_at`. Every later step depends on it, and it is also what enterprise reviewers ask about.

I did not read your code or any repo files. I'm assuming keys are bearer secrets and each tenant currently has one. If you store keys in plaintext, hash them in step 1.

## Why the ops plan fails

| Ops plan | Problem |
|---|---|
| Fresh keys for all ~4,000 tenants in one batch | Failures arrive together. One bug or one bad email template hits everyone at once, and support has no way to spread the load. |
| Email the keys | A secret in email sits in mailboxes, forwards and search indexes for years. Reviewers will flag it, and it undermines the story you're trying to tell. |
| Send on the 1st, disable old keys the following Monday | The window is only days. It also lands on month-end close, the busiest time for an accounting API. A tenant with a quarterly deploy freeze goes down. |
| Hard disable, no overlap | Rotation needs old and new keys valid at the same time. Without that, every rotation is an outage that tenants schedule around. |
| 30-day rotation for all keys | See below. |

**The cost of a universal 30-day rule:**
- About 133 rotations a day, forever (4,000 ÷ 30).
- Even 1% of those going wrong is about 40 broken integrations a month.
- Frequent forced rotation pushes tenants to automate badly, or to paste keys into wikis and chat so they can find them again. That makes security worse.

**What auditors actually need:**
- A documented maximum key lifetime.
- Evidence you enforce it.
- A tested path for revoking a compromised key immediately.
- Logs that show all three.

SOC 2 and ISO 27001 ask for a defined, justified policy, not 30 days specifically. PCI DSS expects you to define a cryptoperiod based on risk. NIST has also moved away from calendar-based rotation toward event-driven rotation, meaning rotate on compromise or staff departure. A configurable maximum age plus fast emergency revocation satisfies the control and can be defended to a reviewer.

## Design

### 1. Key model

- Each tenant can hold **up to 5 active keys**.
- Key format: `lh_live_<key_id>_<secret>`.
  - The prefix identifies Ledgerhawk keys, so you can join GitHub secret scanning and run your own leak detection.
  - The `key_id` lets you look up a key without comparing secrets.
- Store only a hash of the secret (SHA-256 is fine for high-entropy random secrets). Show the secret once at creation.
- Fields per key:
  - `id`, `tenant_id`, `label`, `scopes`
  - `created_at`, `expires_at`
  - `last_used_at`, `last_used_ip`, `last_used_user_agent`
  - `status`: `active`, `expiring`, or `revoked`
  - `revoked_at`, `revoked_reason`
- Keep revoked keys as tombstones for 90 days. This lets the API answer `key_revoked` with a clear message instead of a generic `invalid_key`. That alone prevents most "the API is down" tickets.

### 2. Rotation flow (the part tenants actually do)

1. Tenant creates key B in the dashboard or via `POST /v1/keys`. Both keys are now active.
2. Tenant deploys key B.
3. Tenant watches `last_used_at` on key A. When it goes quiet, they revoke A.
4. If they do nothing, A expires at its `expires_at`, never earlier than promised.

For tenants who want one call, `POST /v1/keys/{id}/rotate` creates a new key and sets `expires_at = now + overlap` on the old one. The default overlap is 7 days, configurable from 1 to 30.

**Who may create or revoke keys:**
- Require dashboard login with MFA, or a separate management credential.
- A leaked data-plane key must not be able to mint its own replacement. Without this, a thief can self-perpetuate.

### 3. Delivery

- **Never email a secret.**
- Email and webhooks carry notices only: "Key `lh_live_ab12…` expires on 2026-12-01. Rotate here: <dashboard link>".
- The secret is displayed once, in the dashboard or the API response.
- Later option, only if enterprise customers ask: push new keys straight into the tenant's AWS Secrets Manager or Vault.

### 4. Policy: configurable, not fixed

| Setting | Default | Range |
|---|---|---|
| Maximum key age | 365 days | 30 to 365, set by a tenant admin |
| Overlap on rotate | 7 days | 1 to 30 days |
| Enforcement | Enforced for new keys | Enterprise plans can lock a minimum policy, for example 90 days |

- **Message for auditors:** "Keys have a documented maximum lifetime, enforced by the platform. Customers can tighten it to 30 days. We revoke immediately on suspected compromise."
- Anyone who truly wants 30 days can have it. You won't force 30 days on 4,000 tenants.

### 5. Warnings before anything breaks

- Send notices at 30, 14, 7 and 1 day before expiry, by email and webhook (`key.expiring`). Send them to every tenant admin, not just the key creator.
- On any call made with an expiring key, add response headers: `LH-Key-Expires: <timestamp>` and `LH-Key-Replacement: <docs url>`.
- Dashboard banner for any key within 30 days of expiry.
- **Brownout for hard cutoffs:** before an enforced expiry on migrated legacy keys, reject requests for 5 minutes, 2 days ahead. This catches forgotten integrations while the fix is still easy.

### 6. Emergency revoke (separate from rotation)

- Immediate, no grace period. Available in the dashboard, via API, and through your support team (with identity verification).
- Automatic revoke when secret scanning reports a leaked key. Notify the tenant right away.
- Tenants can revoke all keys with one action.
- Record who did it, why, and when.

### 7. Audit evidence

- Log events: key created, rotated, used from a new IP, expired, revoked.
- Tenants can export the log, and you retain it for at least 12 months.
- Keep a one-page rotation policy that maps to your SOC 2 control. Reviewers ask for this document first.
- Run a quarterly test that revokes a test key and checks the effect in under a minute. The test result is the artifact you show.

## Migrating the existing ~4,000 keys

Don't re-issue keys. Existing keys stay valid. Give each one an expiry date and let tenants rotate themselves.

| Phase | When | What |
|---|---|---|
| 0. Build | Weeks 1–6 | Multi-key support, hashed storage, `last_used_at`, dashboard UI, rotate API, audit log, notices. Dogfood on internal tenants. |
| 1. Enterprise pilot | Weeks 7–8 | Opt-in for 10–20 friendly tenants and the prospects blocked in security review. Fix what breaks. Ask them to try the flow without help. |
| 2. Announce | Week 9 | Docs, changelog, email to all tenants: new capability, new expiry dates, nothing breaks yet. |
| 3. Staggered expiry | Weeks 10–30 | Assign each legacy key an `expires_at` 6–12 months out, hashed by tenant ID so waves are random. Aim for roughly 5% of tenants per week. Notices go out at 90, 60, 30, 14, 7 and 1 day. |
| 4. Steady state | After week 30 | Every key has an expiry. New keys follow the tenant's policy. |

**Scheduling rules:**
- No expiry or rotation wave in the last 3 business days or first 5 business days of a month, at quarter-end, or in the week of a major tax deadline. Accounting tenants are busiest then.
- Spread waves out so support sees about 200 tenants a week. That is 5% of 4,000, so about 40 a business day at most.
- Pause the rollout if the number of 401s from just-expired keys exceeds an agreed threshold, for example more than 2% of notified tenants in a wave. Define the threshold before wave 1.
- Tenants who haven't acted by their date get a final extension of 14 days if they reply to the notice. Log every extension.

**What to say to the ops team:** their instinct to rotate everything is right. The method is wrong because it creates one large outage with no recovery path.

## What to measure

- Share of tenants with more than one key ever used (proof the overlap model works).
- Share of keys older than their tenant's policy (should trend to 0).
- 401 rate on keys expired in the last 7 days, by wave.
- Support tickets per wave, and time to resolve.
- Median time between a new key's first use and the old key's last use (the real overlap tenants need).
- Emergency revoke time: request to enforced, with a target under 60 seconds.

## Decisions I need from you

1. **Maximum age default:** 365 days is my recommendation. 180 days is a stronger story for enterprise but doubles support volume. Pick one.
2. **Management credential:** MFA dashboard session only, or also a separate management API key? The first is simpler. The second is what automation-heavy tenants will ask for.
3. **Hashing:** are keys currently stored in plaintext? If so, I would hash them in phase 0 as a quiet migration.
4. **Enterprise minimum policy:** do you want to let customers lock a minimum policy (for example 90 days) account-wide? I would, because it is a common request from enterprise security teams.