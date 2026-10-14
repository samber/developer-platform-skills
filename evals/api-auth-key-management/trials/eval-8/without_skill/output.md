# Quillhook API key storage and dashboard redesign

**Verdict: reject both engineering proposals. Keep the goal, which is fewer "I lost my key" tickets, and get it by making a lost key cheap to replace.**

## Why the proposals fail

1. **Reversible encryption with the key in the app config.**
   - The config file sits on the same host as the DB. One server breach or one backup leak exposes the DB and the decryption key together.
   - Every key is then recoverable in bulk. Hashing prevents that.
   - Quillhook sends newsletters. A leaked key means spam or phishing sent from your domain, which damages sender reputation for every customer.
2. **Built-in default key when the env var is missing.**
   - The default lives in the repo or binary, so it is public.
   - One misconfigured prod deploy leaves the encryption open to anyone who reads the source.
   - The failure is silent, so nobody notices.
   - Rule: **a missing secret must crash startup, never degrade.**
3. **Print the full key on every page load.**
   - "We can re-show keys anyway" does not justify this. Each load leaks the key into browser history and cache, screenshots, screen shares, extensions, proxies, and APM or session-replay tools.
   - It also gives an XSS bug a free key theft.
   - Hobbyists screen-share and stream often, so this is a real risk for your users.

## Design

### 1. Key format

`qh_live_<key_id>_<secret>`

- `qh_live_` or `qh_test_` is a fixed prefix. It lets GitHub secret scanning and your own scanners detect leaks. Register the pattern with GitHub's secret scanning partner program.
- `key_id` is 8 to 12 random characters. It is public and used for lookup and display.
- `secret` is 32 bytes from a CSPRNG, base62 or base32 encoded. That is at least 190 bits of entropy.

### 2. Storage

```sql
CREATE TABLE api_keys (
  id            BIGSERIAL PRIMARY KEY,
  account_id    BIGINT NOT NULL REFERENCES accounts(id),   -- no ON DELETE CASCADE
  key_id        TEXT NOT NULL UNIQUE,                       -- public part, for lookup
  secret_hash   BYTEA NOT NULL,                             -- HMAC-SHA-256(pepper, secret)
  label         TEXT NOT NULL,                              -- "blog prod", "local dev"
  scope         TEXT NOT NULL DEFAULT 'full',               -- 'full' | 'send_only'
  display_hint  TEXT NOT NULL,                              -- last 4 chars of secret
  last_used_at  TIMESTAMPTZ,
  expires_at    TIMESTAMPTZ,                                -- set during rotation grace
  revoked_at    TIMESTAMPTZ,
  created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
  deleted_at    TIMESTAMPTZ                                 -- soft delete only
);
CREATE INDEX ON api_keys (account_id) WHERE deleted_at IS NULL;
```

- **Hash with HMAC-SHA-256 and a server-side pepper.** The pepper comes from a secrets manager or env var. The app refuses to boot without it.
  - Slow hashes (bcrypt, argon2) are not needed. The secret is random, with no dictionary to attack, and a slow hash adds latency to every API call.
  - A DB-only leak is then useless, because the attacker lacks the pepper.
  - Keep a `pepper_version` column if you want to rotate the pepper later.
- **Authentication path:**
  1. Parse `key_id` from the key.
  2. Fetch the row.
  3. Compute the HMAC of the presented secret.
  4. Compare with `subtle.ConstantTimeCompare` (or your language's equivalent).
  5. Reject if `revoked_at` is set, if `expires_at` has passed, or if `deleted_at` is set.
  6. Update `last_used_at` at most once per minute, to avoid a write on every request.
- Do not log keys. Redact the `Authorization` header in access logs and error reporters.

### 3. Lifecycle: the real fix for the tickets

A lost key must cost the user 10 seconds, with no support involved.

| Action | Behavior |
|---|---|
| **Create** | Label, scope. The full key shows **once** in a modal with a copy button and a "copy as `.env` line" button. The user must tick "I saved it" to close. Send a "new key created" email with the label and the hint, never the key. |
| **Rotate** | One click creates a new key. The old key stays valid for a chosen grace period (1 hour, 24 hours, or 7 days), then expires automatically. Services keep working during the swap. |
| **Revoke** | Immediate. Needs a confirmation dialog with the key's label and last-used time. |
| **Multiple keys per account** | Allow 5 or more active keys. A lost laptop key then does not force a prod key change. |
| **Scopes** | `send_only` for sending code. Admin operations require `full`. This limits the damage of a leak. |

### 4. Dashboard

**Keys list page (default view):**
- Columns: label, `qh_live_ab12cd34…wxyz` (prefix, `key_id`, and the last 4 chars), scope, created date, last used ("3 min ago", "never"), status.
- Per-row actions: Rotate, Revoke, Rename.
- A key never used for 90 days gets a "stale" badge and a nudge to revoke it.
- Empty state: a single "Create key" button with a 3-line quickstart.

**Never on this page:** the full key, in HTML, JSON, or a hidden field.

**Reveal modal (create and rotate only):**
- The key comes in the response to the create or rotate POST. It is never fetchable by a later GET.
- The response carries `Cache-Control: no-store`.
- Keep the key out of URLs, query strings, and client-side state that persists. Clear it from memory when the modal closes.
- Copy text: "This is the only time we show this key. Lost it? Create a new one in 10 seconds."

**Account security:**
- Require a recent login (re-auth within 10 minutes) for create, rotate, and revoke.
- Show an activity log: key created, rotated, revoked, with IP and time.
- Send an email on every create and revoke.

### 5. Local development without a default key

The engineering concern is valid: local dev must not break. Solve it without a baked-in secret.

1. **Startup check.** If the pepper, DB URL, or any required secret is missing, the process exits with a clear message: `QUILLHOOK_PEPPER not set. Run 'make dev-env' to generate .env.local.`
2. **`make dev-env`** (or `quillhook dev init`) generates random secrets into a git-ignored `.env.local` and ships a `.env.dist`, per the repo's usual convention. First run takes a few seconds. After that it just works.
3. **Seed script** creates a dev account and a `qh_test_` key, and prints the key once to the terminal.
4. **Sandbox mode** (`qh_test_` keys): validates the request and sends nothing. Hobbyists can try the API with no risk of real sends.
5. **CI** injects secrets from its secret store. A missing one fails the job loudly.

A guard test asserts that the app refuses to boot with an empty pepper. This is a gate: never weaken it.

### 6. Migration of existing keys

Do these in order. Do not skip step 1.

1. **Audit what exists.** Find out how keys are stored today. If they are plaintext, treat all of them as exposed to anyone who ever had DB or backup access.
2. **Remove the full-key display from the dashboard first.** This is a small change that ships fast and stops the leak.
3. **Hash in place.** Migration reads each plaintext key, writes `key_id`, `secret_hash` and `display_hint`, then nulls the plaintext column. Existing keys keep working. The old format needs a compat parser until users rotate.
4. **Purge plaintext from backups** on your retention schedule, and note the date.
5. **Email all users.** Say: "Your key is no longer shown on the dashboard. It still works. Rotate any time." Offer a one-click rotate link.
6. **If the default key or AES scheme ever reached prod**, assume compromise. Force rotation for affected accounts with a deadline.
7. **Retire the compat parser** after 90 days.

### 7. Support runbook

- Support **cannot** see or recover keys. Say this on the support page.
- Standard reply: "Open Dashboard, Keys, Create key. Paste it into your app. Revoke the old one when done." Add a screenshot or a 30-second GIF.
- Link the same steps from the API 401 error body: `{"error":"invalid_api_key","hint":"Keys are shown once. Create a new one at https://…/keys"}`.
- For account takeover claims, support triggers revoke-all and sends a re-auth email. It never reads a key.
- Track tickets tagged "lost key" weekly. The target is a drop of 80% or more within a month of launch. If it does not drop, fix the UX, not the storage.

## Rollout order

1. Remove the full-key print from page loads (about 1 hour of work). Ship now.
2. Add the startup check and remove the default-key fallback. Add `make dev-env`.
3. Ship the new schema, the HMAC auth path, and the create/reveal-once flow.
4. Ship rotate with grace period, multiple keys, and scopes.
5. Run the migration and send the user email.
6. Update the support macro and the 401 error body.

## What to tell engineering

- The goal is right: fewer lost-key tickets and no broken local dev.
- Recoverable keys are the wrong tool. Cheap rotation removes the ticket cause, and hashing removes the breach cost.
- Local dev is solved by generating secrets, not by shipping one.

**Next action:** do step 1 of the rollout today. Remove the key from the dashboard page render, then reply with the file that renders it if you want the diff reviewed.