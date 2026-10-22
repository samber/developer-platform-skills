# Parcelform API key storage and request-path lookup spec

## Recommendation: don't use bcrypt for API keys

The tech lead's goal is right: a database leak must not expose usable keys. Bcrypt-plus-loop is the wrong way to get there, for three reasons.

1. **Bcrypt exists to slow down guessing of low-entropy secrets.** Passwords have roughly 30–50 bits of entropy. A 40-character random key has about 238 bits if drawn from base62, or about 200 if hex-like. Brute-forcing it is infeasible even against plain SHA-256, so the work factor buys nothing here.
2. **The loop makes every request slow.** Bcrypt at cost 12 takes about 200–300 ms of CPU per compare. A merchant with 5 keys pays up to about 1.5 s on a miss, on every call to a latency-sensitive label API.
3. **The loop gives attackers a CPU denial of service.** Anyone can send an invalid key with a valid account identifier and force N bcrypt compares per request. At 10 req/s per attacker, a few attackers saturate your auth tier.

Bcrypt's per-row salt is the root cause of the loop: salted hashes can't be indexed, so you must scan. A fast unsalted hash of a high-entropy secret can be indexed. That gives a single lookup, and it is the same approach GitHub, Stripe and others use for tokens. I'd show the tech lead this reasoning and the pentest wording: "stored as a one-way hash, not recoverable from the database" is satisfied either way.

## Storage schema (PostgreSQL)

```sql
CREATE EXTENSION IF NOT EXISTS pgcrypto;  -- only needed for the backfill

CREATE TABLE api_keys (
    id            BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    account_id    BIGINT       NOT NULL REFERENCES accounts(id),   -- no ON DELETE CASCADE
    name          TEXT         NOT NULL DEFAULT '',                -- merchant-facing label
    key_hash      BYTEA        NOT NULL,                           -- 32 bytes, see "Hash function"
    hash_version  SMALLINT     NOT NULL DEFAULT 1,                 -- 1 = SHA-256, 2 = HMAC-SHA-256 (pepper v1), ...
    last4         CHAR(4)      NOT NULL,                           -- display only: "key ending in x7Qa"
    created_at    TIMESTAMPTZ  NOT NULL DEFAULT now(),
    expires_at    TIMESTAMPTZ,                                     -- NULL = no expiry
    revoked_at    TIMESTAMPTZ,                                     -- merchant or ops revocation
    deleted_at    TIMESTAMPTZ,                                     -- soft delete (user-owned resource)
    last_used_at  TIMESTAMPTZ,                                     -- coarse, see "Usage tracking"
    CONSTRAINT key_hash_len CHECK (octet_length(key_hash) = 32)
);

-- The request-path index. Unique, so a hash collision or double-insert fails loudly.
CREATE UNIQUE INDEX api_keys_key_hash_uq ON api_keys (key_hash);

-- Merchant dashboard: list an account's live keys.
CREATE INDEX api_keys_account_idx ON api_keys (account_id) WHERE deleted_at IS NULL;
```

Notes:

- **No plaintext column.** `last4` is the only fragment retained, for display and support triage.
- **`hash_version`** lets you move to HMAC-SHA-256 with a pepper later without a flag day. The lookup tries the current version first, then older ones during migration.
- **Key rotation:** a merchant creates a new key while the old one stays valid. Revoke the old one by setting `revoked_at`. Overlapping keys need no extra schema.
- **Audit trail:** if you need per-request audit, write `(key id, timestamp, endpoint)` to a separate append-only table or your log pipeline. Don't use `last_used_at` for that.

### Hash function

- **Baseline: `SHA-256(key)`** as raw bytes. It is fast, unsalted and indexable. With 200+ bits of entropy, a leaked hash can't be inverted.
- **Recommended hardening: `HMAC-SHA-256(pepper, key)`**, with the pepper held in a secrets manager or KMS and never in the database. A database-only leak then yields nothing even theoretically. The cost is pepper rotation (use `hash_version`) and one more secret to manage. Ship plain SHA-256 first if you want the smallest change, and add the pepper as version 2.
- Never use a salted hash here, because it can't be indexed. Never use MD5 or SHA-1.

## Request-path lookup flow

```
Authorization: Bearer <key>
        │
        ▼
1. Parse + shape check
   - header present, scheme "Bearer", token is exactly 40 chars of [A-Za-z0-9]
   - fail → 401 (no DB call, no hashing of oversized input)
        │
        ▼
2. h = SHA-256(token)            (or HMAC for hash_version 2)
        │
        ▼
3. Cache lookup by h (in-process LRU, TTL 30–60 s, max ~100k entries)
   - hit (valid) → go to 6
   - hit (negative) → 401
        │
        ▼
4. DB: SELECT id, account_id, expires_at, revoked_at, deleted_at
       FROM api_keys WHERE key_hash = $1       -- single unique-index probe
   - no row → cache negative (short TTL, 10 s) → 401
        │
        ▼
5. Validity checks, in application code
   - deleted_at IS NOT NULL, revoked_at IS NOT NULL, expires_at <= now() → 401
   - cache the positive result with min(TTL, time until expires_at)
        │
        ▼
6. Attach {key_id, account_id} to request context → proceed
   - enqueue last_used_at update (async, throttled)
```

### Rules for the flow

- **Same 401 body and similar timing for every failure** (malformed, unknown, revoked, expired). Don't tell the caller which one it was.
- **The database does the comparison.** The equality check happens against a hash of an unguessable secret, so lookup-timing leaks give an attacker nothing useful. If you want belt and braces, also compare the stored and computed hashes with `subtle.ConstantTimeCompare` (Go) or `crypto.timingSafeEqual` (Node) after the fetch.
- **Revocation latency equals the cache TTL.** State this in the docs (up to 60 s). For emergency revocation, publish the key's hash on a Redis or Postgres `NOTIFY` channel so instances evict it immediately. Cache only the 32-byte hash and the small result struct, never the raw key.
- **Fail closed.** If the database is unreachable and there is no cache entry, return 503, not 200.
- **Rate-limit failures** per source IP and per account (token bucket on 401s). The lookup is cheap, but you still want brute-force and noise protection.
- **Never log the key or the `Authorization` header.** Log `key_id` and `account_id`. Add the header to your redaction list in the logger, the reverse proxy and any APM tool.
- **Usage tracking:** don't write on every request, because it turns the read path into a write path and bloats the table through MVCC churn. Update `last_used_at` at most once per 5 minutes per key, asynchronously, with `UPDATE ... WHERE id = $1 AND (last_used_at IS NULL OR last_used_at < now() - interval '5 minutes')`.

### Performance expectation

One SHA-256 takes microseconds. One unique-index probe takes under 1 ms. With the cache, the typical request does no DB call. Compared with bcrypt at cost 12, that is roughly 200–1500 ms saved per request, and an invalid-key flood costs microseconds instead of CPU-seconds.

## Migrating the existing plaintext keys

Use expand and contract so the API never goes down.

1. **Expand.** Create the new columns, the `key_hash` unique index and the `last4` column on the existing `keys` table (or create `api_keys` alongside it). Leave `key` readable.
2. **Backfill in batches** (for example 5,000 rows per transaction, ordered by id):
   ```sql
   UPDATE keys SET key_hash = digest(key, 'sha256'), last4 = right(key, 4)
   WHERE id BETWEEN $1 AND $2 AND key_hash IS NULL;
   ```
   Make sure `log_statement` is not `all`. The values come from the table, so they won't be logged either way, but check anyway.
3. **Dual-write.** Newly issued keys write only the hash. The plaintext column becomes nullable. The key is shown to the merchant once at creation and never retrievable again.
4. **Switch reads** to the hash lookup. Keep the old plaintext path behind a flag for one release, as a rollback path only.
5. **Contract.** Set `key = NULL`, then `ALTER TABLE ... DROP COLUMN key`. Dropping the column doesn't physically remove the data from the pages, so also run `VACUUM FULL` (or `pg_repack`) to rewrite the table.
6. **Deal with the plaintext that already escaped.** It remains in WAL archives, base backups, replicas, snapshots, dev and staging copies, analytics exports and any log that captured the table. Inventory these and either expire them on the normal retention schedule or purge them. Because the pentest showed the plaintext was exposed, also tell merchants to rotate their keys. Build the rotation path first, with overlapping keys as above. Force-rotate on a deadline, starting with the highest-volume accounts.

## Test plan

- Valid key authenticates. A one-character change in any position fails.
- Wrong length (39, 41, 0, 10 KB), non-alphanumeric characters, a missing header and a wrong scheme all return 401 without a DB call.
- Revoked, expired (including `expires_at` exactly equal to now), soft-deleted and unknown keys return identical 401 responses.
- Key rotation: both keys work during the overlap, and the old key fails after `revoked_at` is set (within the cache TTL, and immediately after an eviction event).
- Cache: a negative-cache entry doesn't block a newly created valid key for longer than its TTL. The positive TTL is capped by `expires_at`.
- DB down: a cached key still works, and an uncached key returns 503.
- The unique index rejects a duplicate `key_hash`.
- Backfill: row count with `key_hash IS NULL` is zero after the run, and a sampled set of old plaintext keys authenticates via the hash path.
- After the contract step, `SELECT` on the table shows no plaintext column, and a grep of logs from a test run finds no key material.
- Load test: 1,000 req/s of invalid keys keeps auth CPU flat. This is the case where bcrypt-plus-loop would fall over.

## Decisions for the team

1. **Plain SHA-256 or HMAC with a pepper from day one.** My recommendation is HMAC if you already run a secrets manager, otherwise SHA-256 now and `hash_version` 2 later.
2. **Revocation latency target.** The cache TTL is the number to set. 60 s is a reasonable default, with push eviction for emergencies.
3. **Whether to force merchants to rotate.** This depends on what the pentest found about the exposure path, and I'd rotate.
4. **Key format for new keys.** Optionally add a visible prefix (for example `pf_live_`) so secret scanners such as GitHub's can detect leaked Parcelform keys. Existing 40-character keys keep working unchanged, because lookup is by hash of the whole token.