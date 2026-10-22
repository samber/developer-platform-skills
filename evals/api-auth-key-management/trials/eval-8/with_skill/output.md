# Quillhook API keys: storage and dashboard redesign

I followed the `api-auth-key-management` skill. It asks clarifying questions first, so I've listed my assumptions at the end, with what changes if each is wrong.

## Verdict on the three proposals

| Proposal | Verdict | Why |
|---|---|---|
| AES-encrypt keys, with the encryption key in the app config file | ❌ Reject | The skill says "never app-managed encryption keys". Anyone who can read the database can usually read the config, so the encryption protects nothing. |
| Fall back to a built-in default key when the env var is missing | ❌ Reject | A missing secret must crash at startup. A hardcoded default runs in production exactly like the real key, and it is public the moment the repo or binary is. |
| Print the full key on every page load, justified by "we can re-show keys anyway" | ❌ Reject | The full key is shown once, at creation, and never again. Every page load that shows it is another place it can leak: browser history, cache, screenshots, session replay, support screen-shares. |

The real problem is that lost keys cost support hours. That is solved by self-service reissue, not by making keys re-readable.

## 1. Key format

- Format: `qh_live_<30 base62 chars><6-char CRC32>` and `qh_test_<…>` for sandbox.
- The body gives about 178 bits of entropy, above the 120-bit floor.
- The checksum lets the API reject typos with no database call, and lets secret scanners ignore noise.
- The prefix carries the key type and environment, so a leaked key is identifiable on sight.
- Later, once there is a real leak incident, register the pattern with GitHub's Secret Scanning Partner Program.

## 2. Storage: hash-only, with self-service reissue

Show the full key once, at creation, and store only a hash. Stripe, AWS, GitHub, OpenAI and Resend all do this.

```sql
CREATE TABLE api_keys (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  owner_id      UUID NOT NULL,
  key_prefix    VARCHAR(16) NOT NULL,  -- plaintext, indexed: lookup handle only
  key_hash      CHAR(64) NOT NULL,     -- SHA-256 of the full key
  name          VARCHAR(255) NOT NULL, -- "Blog signup form"
  scopes        TEXT[] NOT NULL,       -- never empty-means-all
  created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  last_used_at  TIMESTAMPTZ,           -- written async
  expires_at    TIMESTAMPTZ,           -- also the rotation grace end
  revoked_at    TIMESTAMPTZ
);
CREATE INDEX idx_api_keys_prefix ON api_keys(key_prefix);
```

Lookup on every request:

1. Check the format and checksum. Reject malformed keys with no database call.
2. Query by `key_prefix`.
3. Compare SHA-256 of the presented key with `key_hash` in constant time. Do not use `==`.
4. Check expiry and revocation, then enforce scopes.
5. Update `last_used_at` asynchronously, never on the request path.

SHA-256 is correct here and bcrypt is not. The keys are high-entropy and machine-generated, so a slow hash only adds CPU per request without adding security. This depends on the entropy floor being enforced at generation.

**Startup behavior.**
- The API refuses to boot if the hashing pepper, database credentials or any other required secret is missing.
- There are no defaults in code and no `dev-secret-key-123`.
- `.env.dist` ships empty placeholders.

**Local dev never breaks, without a fallback key.**
- Signup auto-creates a `qh_test_` key, and the sandbox accepts it with no real sends.
- The quickstart is `export QUILLHOOK_API_KEY=qh_test_…`.
- A missing variable fails with a clear message: "set QUILLHOOK_API_KEY, get a test key at <dashboard>".
- Engineering gets its goal of dev never breaking, and no production path has a default.

**Support load.** The tickets go away because reissue takes 10 seconds and needs no human, not because keys are revealable. The skill ranks retrievable storage higher for ticket reduction, so I'm stating the trade-off plainly:
- Ship hash-only plus the self-service roll below.
- Measure lost-key tickets for 60 days.
- Step up to retrievable only if the tickets stay high. That means AES-256-GCM, with the key-encryption-key in a **KMS** (not the config file), a SHA-256 hash stored alongside for validation, and an audit-logged "reveal" action.
- Newsletter keys can send mail to a customer's subscriber list, which makes abuse (spam, phishing) a real harm. That is a reason to delay the step-up.

## 3. Scoping

- Restrictive by default. Omitting scopes never grants full access.
- Starting scopes: `send`, `subscribers:read`, `subscribers:write`, `stats:read`. The form-embed use case gets `subscribers:write` only.
- One key per project per environment (test and live). Hobbyists get their blast-radius containment from this split.
- Defer fine-grained per-resource scoping. Revisit it when an enterprise or compliance request arrives.
- Never put a live key in browser code. The signup-form use case gets a scoped, write-only key, or a short-lived token minted server-side.
- Rate-limit key validation and key creation like login endpoints.

## 4. Rotation: a one-click roll

- A single **Roll key** action creates the new key and sets the old key's expiry in one call.
- The expiry picker offers Now, 24 hours, 7 days (default) and Custom.
- Both keys validate during the overlap. Allow at most two active keys per name, as AWS does.
- The new key is shown once, with the old key's exact expiry timestamp and a link to its last-used time.
- Never delete the old key before `last_used_at` shows no traffic. Deactivate first, wait 24 to 48 hours, then delete.
- On suspected compromise, use **Revoke now** with zero grace.
- Email the owner when a key goes unused for 90 days, or is about to expire.

## 5. Dashboard

Self-service means four actions with no support ticket: sign up, create, roll, revoke.

**Key list.** Each row shows:
- the label,
- a masked key (`qh_live_AbC…x9Zk`, first and last characters only),
- the scopes,
- created date and last-used time,
- a status badge: active, expiring or revoked,
- **Roll** and **Revoke** buttons.

**Creation modal.** This is the only place the full key ever appears:
- a copy button,
- a warning: "You won't see this again. Lost it? Roll the key in one click."
- a checkbox to confirm it was saved before closing.
- Send it with `Cache-Control: no-store`, and exclude that response from logs, analytics and session replay.

**Lost-key flow.** The empty-state copy and the lost-key help article both point to **Roll key**. This is what removes the support tickets.

**Usage.** Show per-key request volume as a separate surface from last-used. Last-used answers "is this key alive", and usage answers "what is it doing".

**Errors.** Return 401 for an invalid, expired or revoked key, and 403 for a valid key without the needed scope. Messages say which one it was.

## 6. Ownership

- Hobbyists mostly run individual keys, so that is the default tier.
- Team and service-account keys are explicitly deferred. When the first team customer arrives, add org-owned keys with an admin view of every key per member, so offboarding is possible.
- Write one line in the docs: "Production integrations should not depend on a personal key".

## 7. Compliance

No regime is in scope as far as I know, so the minimum is:
- an audit log of every create, roll and revoke, with who and when,
- a documented key-lifecycle policy.

This costs little, and it is what a SOC 2 procurement questionnaire asks for later.

## Migration for the current system

Today's dashboard prints full keys, so keys are stored recoverably (plaintext or reversibly). Treat that as a standing incident.

1. **Now:** stop printing the full key on page load. This ships first and is a small change.
2. Check whether keys have leaked through logs, analytics, session replay or HTTP caches. Purge them if so.
3. Add `key_hash` and `key_prefix`. Backfill them from existing keys in one migration, then **drop** the plaintext or encrypted column. Verify with a schema audit that no recoverable key remains.
4. Existing keys keep working because the hash is computed from the key already stored. No customer migration is required.
5. Remove any default-key fallback in the same release, and add the startup crash for missing secrets.
6. Optionally email customers that keys will be masked from now on, and that they can roll at any time.
7. Cap the old keys' lifetime and nudge customers to roll them once. This removes the exposed history.

## Pass/fail gates

- **Storage:** zero recoverable keys at rest, proven by schema audit.
- **Startup:** the API exits non-zero with every required secret unset.
- **Inventory:** every live key has an owner and a scope, and has an expiry or a documented exemption.
- **Rotation:** one real key rolled end to end with zero downtime, and the old key confirmed idle before deletion.
- **Self-service:** all four actions work with no ticket.
- **Trend metrics** (no industry thresholds exist, so baseline them in month one):
  - lost-key tickets per week,
  - share of keys unused for more than 90 days,
  - time from leak detection to revocation.

## Assumptions

These are the skill's questions. I answered them myself, and I'll revise if you correct them.

1. **Retrofit, not greenfield.** Current storage is recoverable or plaintext. If keys are already hashed, step 3 of the migration disappears.
2. **Individual hobbyist keys dominate,** with a few teams. If teams are many, org and service-account keys move into scope now.
3. **Consumers only call as themselves.** If third-party apps act for Quillhook users, that part goes to OAuth (`oauth2-provider-design`).
4. **No PCI or SOC 2 regime in scope.** If one is, add mandatory expiry and fine-grained scoping.
5. **No RBAC to reuse.** If one exists, fine-grained scopes become cheap and should come sooner.
6. **Ship date and effort.** I assumed days, not quarters. Everything above fits that, and the KMS step-up is optional and later.