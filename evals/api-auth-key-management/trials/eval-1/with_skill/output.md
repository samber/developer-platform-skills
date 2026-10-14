# Parcelform API key storage and request-path lookup spec

**Recommendation:** use SHA-256, not bcrypt, for these keys. Look candidates up by an indexed plaintext prefix, then compare hashes in constant time. This differs from your tech lead's plan, and the reasons are in section 1.

I did not ask the skill's clarifying questions, because you asked for the spec directly. These are my assumptions, so correct any that are wrong:

- This is a retrofit of about N live keys. The current keys are 40-character CSPRNG output and are plaintext in `keys`.
- Merchants are organizations, and keys are used server-to-server only.
- There is no compliance regime yet, so the decision is hash-only storage, not encrypted retrievable storage.
- The ship date is soon, so I took the cheapest rung that fully closes the pentest finding.

## 1. Why not "bcrypt cost 12 and loop over the account's rows"

The two things differ in what they protect. Passwords are low-entropy and human-chosen, so a slow hash is what stops brute force. A 40-character random key has about 160 bits of entropy (hex alphabet) to about 238 bits (Base62). A GPU doing about 21 billion SHA-256 hashes per second is still infeasible against that, so the slow hash adds cost without adding security.

What the loop would cost you:

- **Per-request CPU.** Cost 12 is roughly 200-300 ms per compare. An account with 5 keys costs about 1-1.5 s of CPU on every failed attempt and half that on average for valid ones. Your label API sits on the hot path of every merchant checkout.
- **A CPU-exhaustion vector.** Each garbage key forces a full bcrypt pass over all of an account's rows. For this loop to be possible at all, the request must also carry an account identifier. An attacker who knows or guesses one can burn about 1 s of CPU per request.
- **No direct lookup.** Salted bcrypt hashes cannot be matched with `WHERE hash = ?`. That is why the loop exists, and it is why it scales with key count.
- **Rotation makes it worse.** Rotation needs two keys valid at once, so every request pays for at least 2 compares during the overlap.
- **A 72-byte input limit.** bcrypt silently truncates input at 72 bytes. 40 characters fits today, but adding a `pk_live_` prefix and a checksum leaves little headroom. Long keys would need a SHA-256 pre-hash anyway.

The slow-hash view (defense in depth, one policy for all secrets) is a real minority position. It is defensible only if you accept the CPU bill. You have a cheaper way to get the same property: enforce the entropy floor at generation (section 3) and fix the one thing that actually failed, which is that the keys were plaintext.

## 2. Schema (PostgreSQL)

```sql
CREATE TABLE api_keys (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  account_id    UUID NOT NULL REFERENCES accounts(id),   -- no ON DELETE CASCADE
  owner_type    TEXT NOT NULL DEFAULT 'organization'
                CHECK (owner_type IN ('user','organization','service_account')),
  owner_id      UUID NOT NULL,         -- user, org, or service account; decouples key from employment
  name          VARCHAR(255) NOT NULL, -- "prod label service", "CI staging"
  environment   TEXT NOT NULL CHECK (environment IN ('live','test')),
  key_prefix    VARCHAR(16) NOT NULL,  -- plaintext lookup handle; too short to reconstruct the key
  key_hash      CHAR(64) NOT NULL,     -- lowercase hex SHA-256 of the full key; never the plaintext
  key_last4     CHAR(4) NOT NULL,      -- masked display only
  scopes        TEXT[] NOT NULL CHECK (cardinality(scopes) > 0),  -- restrictive; empty never means all
  status        TEXT NOT NULL DEFAULT 'active'
                CHECK (status IN ('active','expiring','revoked')),
  expires_at    TIMESTAMPTZ,           -- also the end of a rotation grace window
  revoked_at    TIMESTAMPTZ,
  rotated_from  UUID REFERENCES api_keys(id),
  legacy_format BOOLEAN NOT NULL DEFAULT FALSE,  -- migrated 40-char keys
  created_by    UUID NOT NULL,
  created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  last_used_at  TIMESTAMPTZ            -- written async
);
CREATE INDEX idx_api_keys_prefix ON api_keys(key_prefix);
CREATE UNIQUE INDEX uq_api_keys_hash ON api_keys(key_hash);
CREATE INDEX idx_api_keys_account ON api_keys(account_id) WHERE status <> 'revoked';
```

- **Scopes.** Define a coarse set, for example `labels:create`, `labels:read`, `tracking:read`, `rates:read`. Give new keys one key per service per environment. Make the API reject a create call with no scopes. Never default to full access.
- **No unique-active-key constraint per account.** Rotation needs two valid keys at once.
- **Soft revoke.** Set `status='revoked'` and `revoked_at`. Do not hard-delete key rows that belong to a user-owned resource.
- **Audit log.** Add an append-only `api_key_events` table: `key_id, event (create/use-fail/rotate/revoke/reveal-attempt), actor, at, reason`. This is the evidence trail for any later audit.

## 3. Key format for newly issued keys

`pf_{live|test}_` + 32-character Base62 random body + 6-character CRC32 checksum.

- The body is about 190 bits from the OS CSPRNG. The floor is 120 bits and 32 or more characters. Enforce it in the generator and add a unit test for it, because fast hashing is only safe when this holds.
- The prefix encodes environment, and the checksum lets you reject malformed keys with no database call.
- Both features also make leaked keys detectable by secret scanners. Register the pattern with GitHub's partner program once real leaks justify it.
- `key_prefix` = `pf_live_` + the first 4 body characters, about 24 bits of the secret. That narrows lookup to one row or a handful.
- **Legacy keys.** For the existing 40-character keys, `key_prefix` is the first 8 characters, and `legacy_format = TRUE` skips the checksum step.
- **Show the full key exactly once**, in the creation response. The dashboard shows `key_prefix…key_last4` only.

## 4. Request-path lookup flow

1. **Parse and validate the shape.** Check the prefix is known, the length is right, and the checksum passes (skipped for `legacy_format`). On failure, return 401 with no database call.
2. **Fetch candidates.** Run `SELECT … FROM api_keys WHERE key_prefix = $1 AND status <> 'revoked'`, using the indexed prefix. It normally returns 1 row. Cache it for a short TTL if you need to.
3. **Hash and compare.** Compute `SHA-256(presented_key)` once. Compare it against each candidate's `key_hash` using a constant-time comparison (for example `crypto/subtle.ConstantTimeCompare`, or `hmac.compare_digest`). Do not use `==`, which leaks timing.
4. **Check lifecycle.** Check status and `expires_at`. Then check that `environment` matches the endpoint (a test key cannot hit live) and that the key's scopes cover the operation.
5. **Return the right error.** 401 for a key that does not exist, is revoked, or is expired. 403 for a valid key that lacks the scope. Use the same response body and timing for unknown versus revoked.
6. **Update telemetry off the hot path.** Enqueue the `last_used_at` update asynchronously, fire-and-forget, after success.

Failure handling:

- **Rate-limit key validation** like a login endpoint, per IP and per prefix, with a failure counter in the audit log.
- **Missing secrets fail closed.** If any required config is absent, the service must crash at startup. It must never fall back to a default.
- **Alternative lookup.** Because the hash is deterministic, `WHERE key_hash = $1` on the unique index is equally O(1) and removes the candidate loop. I kept the prefix because the dashboard needs it anyway.

## 5. Migration (retrofit)

This keeps every existing merchant integration working with no consumer-visible change.

1. **Add columns.** Add `key_prefix`, `key_hash`, `key_last4`, and `legacy_format` as nullable.
2. **Backfill in SQL.** Run `UPDATE keys SET key_hash = encode(sha256(convert_to(key,'UTF8')),'hex'), key_prefix = left(key,8), key_last4 = right(key,4), legacy_format = TRUE`. Then set the columns `NOT NULL`.
3. **Deploy the new lookup.** Ship the section 4 path, then verify in staging with real legacy keys. Keep the plaintext column until you have verified zero lookups that read it.
4. **Drop the plaintext column.** This step is hard to reverse, so take a backup first and confirm it is correct.
5. **Scrub other copies.** Dropping the column does not remove old plaintext from backups, PITR/WAL archives, read replicas, logs, APM traces, analytics exports, and support tooling. Inventory these and purge or expire them.
6. **Treat the keys as potentially exposed.** Hashing does not un-leak anything. Decide whether the pentest scope or your threat model means the legacy keys should be rotated. A one-time forced "roll" with a 14-30 day overlap on the new format is the safe default. Prioritize accounts with broad access.
7. **Ship the dashboard actions.** Add create, roll (atomic: new key plus old key's expiry in one call), and revoke before you announce the rotation.

## 6. Open items for your team

- **Entropy of the legacy generator.** Confirm it used a CSPRNG and which alphabet. If it did not, the 160+ bit assumption fails and those keys must be force-rotated.
- **Ownership.** Decide whether keys belong to users or to the organization, and issue service-account keys for unattended callers.
- **Rotation cadence.** Set the default grace window, 24 hours to 7 days for routine rotation, and zero for compromise or offboarding.
- **Sensitive operations.** Check whether any operation, such as account or billing changes, relies on a key alone. Keys identify the calling application, not a person.

## 7. Acceptance gates

- A schema audit shows zero plaintext keys at rest.
- Every live key has an owner, scopes, and an expiry or a documented exemption.
- One real key has been rolled with zero downtime, and its old key showed zero traffic before deletion.
- A load test shows p99 auth latency in single-digit milliseconds, with no CPU growth as keys per account increase.
- A timing test on unknown versus wrong-hash keys shows no distinguishable difference.