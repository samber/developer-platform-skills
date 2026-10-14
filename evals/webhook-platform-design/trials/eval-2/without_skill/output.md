# Webhook signing changes for Portmint

I haven't seen the security review's wording, so I've assumed it covers the weak points below. Fixes are ordered by risk.

## 1. Sign a timestamp with the body (P0)

**Today:** the HMAC covers only the body. A captured valid request can be replayed forever. For payments, a replayed `payment.succeeded` can trigger a double fulfillment.

**Change:**
- Sign `"{timestamp}.{raw_body}"`, with the timestamp as Unix seconds.
- Send the timestamp in the header, for example `Portmint-Signature: t=1760000000,v1=<hex>`.
- Tell merchants to reject requests where `|now - t|` is over 5 minutes. Tell them to dedupe on the event ID.
- Add a stable `event_id` to the body if it isn't there already.
- Re-sign every retry with a fresh timestamp and the same `event_id`. Otherwise long retry backoffs fall outside the tolerance window.

**Why:** the timestamp becomes authenticated, so an attacker can't strip or alter it. Without it, replay protection is impossible.

## 2. Verify raw bytes, not the parsed JSON (P0)

**Today:** the docs say to verify inside the framework's JSON body handler. By then the body has been parsed, so the original bytes are gone. Merchants must re-serialize, and that changes key order, whitespace, number formatting and unicode escapes. Two things follow:
- Verification fails intermittently, and merchants "fix" it by loosening or skipping the check.
- Signing a re-serialized form invites parser-differential bugs, such as duplicate keys or float rounding.

**Change:**
- Rewrite the docs: capture the raw body, verify, then parse.
- Add per-framework snippets. Express needs `express.raw({type:'application/json'})` on the webhook route. Flask uses `request.get_data()`. Rails uses `request.raw_post`. Go uses `io.ReadAll(r.Body)`.
- Ship an official `verify(rawBody, header, secrets, tolerance)` helper in each SDK. Self-written crypto in 600 merchant codebases is where mistakes happen.
- Publish test vectors (secret, timestamp, body, expected signature).

## 3. Specify constant-time comparison (P1)

The docs must require a constant-time compare: `crypto.timingSafeEqual`, `hmac.compare_digest` or `subtle.ConstantTimeCompare`. Decode the hex first and check lengths. The SDK helper does this by default.

## 4. Rotation without an outage (P0)

**Today:** the old secret dies the instant the merchant clicks "regenerate". The merchant has to deploy the new secret at that same moment. Every webhook sent in between fails verification, and for payments that means missed or retried events. The cutover pressure also discourages rotating at all.

**Change:**
- **Roll with overlap.** On regenerate, mint a new secret and keep the old one valid for a merchant-chosen window. Default it to 24 hours and cap it at 7 days.
- **Dual signatures.** During overlap, sign with both secrets and put both in the header: `t=...,v1=<sig_new>,v1=<sig_old>`. The merchant's verifier accepts if any `v1` matches. Merchants can then deploy the new secret whenever it suits them, and there is no flag day.
- **Add an immediate-revoke option** for suspected compromise. Make it a separate, explicit action that kills the old secret at once.
- **Control the dashboard actions.** Require recent re-authentication or MFA to reveal or roll a secret. Write an audit-log entry and email the account owners on every roll or reveal.

## 5. Secret hygiene (P1)

- Generate at least 32 random bytes from a CSPRNG. Use a recognizable prefix such as `whsec_` so secret scanners can catch leaks in repos.
- Keep one secret per endpoint, as you do now. Don't change that.
- Store secrets encrypted with KMS envelope encryption, not plaintext in the table. You need the plaintext to sign, so protect it at rest.
- Use the new `whsec_` format only for secrets minted after the migration. Existing secrets keep working unchanged.

## 6. Versioned header and migration plan (P1)

Use the `t=…,v1=…` format. The `v1` label lets you move to another algorithm later without another breaking change.

**Don't break 600 live endpoints.**
1. Keep sending `X-Portmint-Signature` unchanged (body-only HMAC) during the migration window.
2. Send the new `Portmint-Signature` alongside it from day one.
3. Publish the SDK helpers and the new docs, and email merchants.
4. Make the new scheme the default for newly created endpoints.
5. Let merchants opt out of the legacy header per endpoint in the dashboard. Show a per-endpoint banner while the legacy header is still on.
6. After 6 to 12 months, deprecate the legacy header with notice. Chase the stragglers by endpoint, using your delivery logs.

Be honest with the reviewers: until the legacy header is off, replay protection is optional for a given merchant. Only the timestamped scheme gives it.

## 7. Later, optional: asymmetric signatures

With HMAC, anyone who holds the secret can also forge events, and Portmint must store a signing secret. Ed25519 signatures with a published public key (a JWKS-style endpoint) remove both problems. They cost more integration work, so treat them as a v2 option and don't block on them.

## Suggested order

1. Timestamped signature and dual header (items 1 and 6).
2. Docs rewrite and SDK verify helpers with test vectors (items 2 and 3).
3. Overlap rotation and dashboard controls (items 4 and 5).
4. Migration communication, then the deprecation timeline.

Open questions for you:
- Do your SDKs already exist, or do you only ship docs?
- Is there an `event_id` in every payload today?
- Do you have delivery logs that show which endpoints are failing verification? They would tell you which merchants have already worked around the body-parsing problem.