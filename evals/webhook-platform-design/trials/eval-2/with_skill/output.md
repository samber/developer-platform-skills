# Portmint webhook signing: what to change and why

Security review is right on all three points. I read the `webhook-platform-design` skill and its signing reference and checked your setup against them. I didn't ask the skill's clarifying questions (greenfield vs retrofit, scale, consumer types), because you gave the retrofit facts. Items that go beyond the skill are marked **[mine]**.

## Verdict

| # | Today | Problem | Severity |
|---|---|---|---|
| 1 | HMAC over body only | No timestamp, so a captured request validates forever (replay) | 🔴 |
| 2 | One secret, old one dies on "regenerate" | Rotation forces revoke-then-deploy, so deliveries fail in the gap | 🔴 |
| 3 | Docs say "verify in your JSON body handler" | The parser re-serializes the body before the HMAC check, which breaks verification or pushes merchants to skip it | 🟠 |
| 4 | Bespoke `X-Portmint-Signature`, hex | A one-off scheme every merchant must hand-roll, and it is missing a stable event ID | 🟠 |

Your scheme is the same shape as GitHub's and Shopify's body-only signatures. The skill says those predate the convergence on Standard Webhooks and shouldn't be copied for a new platform. For payments infrastructure it is a poor place to be.

## Changes

### 1. Sign the timestamp (replay protection)

- Adopt the Standard Webhooks spec instead of patching the bespoke scheme.
- Send three headers on every delivery:
  - `webhook-id`
  - `webhook-timestamp`
  - `webhook-signature`
- Compute the signature as `base64(HMAC-SHA256(secret, "{webhook-id}.{webhook-timestamp}.{raw_body}"))`, sent as `v1,<sig>`.
- Document that receivers must reject any delivery whose timestamp is outside a tolerance window. The spec recommends 300 seconds.
- **Why:** the signature proves authenticity, not freshness. Today an attacker who captures one `payment.succeeded` request can replay it indefinitely, and every merchant that fulfills orders on that event is exposed.
- Signing the `webhook-id` too binds the event identity to the signature.

### 2. Zero-downtime rotation with multiple active secrets

- Let an endpoint hold more than one active secret.
- During rotation, sign every delivery with all active secrets. The `webhook-signature` header then carries space-delimited pairs, such as `v1,<new> v1,<old>`.
- Replace the dashboard's "regenerate" with a three-step flow:
  1. **Rotate:** issue a new secret. The old one stays valid and both sign.
  2. The merchant deploys the new secret and sees deliveries verify against it.
  3. **Retire the old secret** after confirmed delivery success, or automatically after an explicit expiry. Stripe's roll gives up to 24h of dual validity; Convoy uses an explicit expiry.
- **[mine]** Keep an explicit "revoke now" action for suspected compromise. That is the one case where an instant cutover is correct.
- **Why:** with 600 endpoints, some merchant will always deploy late. Instant revocation turns every rotation into failed payment notifications. It also discourages rotating at all, which is the opposite of what security review wants.
- Secret issuance, storage and rotation infrastructure belong to the sibling skill `api-auth-key-management`. This skill only owns the scheme and the verification contract.

### 3. Fix the docs: raw body, verify everything, exempt session auth

Rewrite the signing docs around the three pitfalls the skill lists:

1. **Verify every request, no exceptions.** A handler that "only posts to chat" still takes spoofed events.
2. **Verify against the raw body before any JSON parser touches it.** Your current advice is the reverse of this. In Express, for example, the webhook route needs `express.raw({ type: 'application/json' })`.
3. **Exempt the webhook route from session-auth middleware.** It authenticates by signature, so uniform auth middleware 401s it before the handler runs.

Docs should also include:
- Runnable verification snippets per major framework.
- The timestamp-tolerance check, with the replay explanation.
- The dual-signature rotation flow.

### 4. Secret format, asymmetric option, dedup ID

- Prefix symmetric secrets with `whsec_`, so scanners can identify leaked keys. Use 24–64 random bytes, base64-encoded.
- Offer asymmetric ed25519 signing as an option, with `whsk_`/`whpk_` prefixes and signature id `v1a`. Merchants verify with a public key and never hold a shared secret. The skill recommends it when you don't control both ends, and security-conscious payments merchants will ask for it. A provider can run both modes at once.
- `webhook-id` doubles as the dedup ID. It must be identical across retries of the same event. Confirm that is true of your delivery pipeline today, because you can't retrofit it for merchants who already built without it.

## Migration (retrofit, 600 live endpoints) [mine]

The skill doesn't prescribe a cutover, so this is my plan:

1. **Dual-send.** Ship the new headers alongside the legacy `X-Portmint-Signature`. Nothing breaks for merchants who haven't moved.
2. **Publish a deprecation date** for the legacy header. Notify merchants out-of-band by email and in the dashboard.
3. **Track adoption per endpoint**, meaning which endpoints verify the new headers. Chase the stragglers before removal.
4. **Remove the legacy header** only after that date.

Existing hex secrets can keep working during dual-send. New secrets issued after the change use the `whsec_` format.

Also **[mine]**: tell merchants to compare signatures in constant time. Standard Webhooks libraries already do this.

## Beyond signing (not asked, but you should audit)

Check these against the skill's five-fact "contract completeness" gate:

- Is the delivery guarantee documented as at-least-once, with no exactly-once claim anywhere?
- Is the ordering position stated as best-effort?
- Is the exact retry schedule published?
- Is the ack timeout stated (~10s is the convention)?
- Is the dedup ID location documented?

Payments-grade domains also lean toward the longer retry span, and the skill recommends telling merchants to reconcile periodically against your API for high-stakes events. I didn't review your retry or portal setup, so I can't say how those stand.

## Suggested order

1. Docs fix (item 3). It's cheap and removes the most common merchant-side failure.
2. Multi-secret rotation (item 2).
3. Standard Webhooks headers with dual-send (items 1 and 4).
4. Asymmetric signing, once the rest is stable.

I didn't edit any files or run any commands.