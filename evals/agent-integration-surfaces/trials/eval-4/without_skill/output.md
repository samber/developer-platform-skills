# Review of `POST /v1/instant`: verdict and tightened design

The core idea is sound: no account required, agent creates the store, human claims it later. Three parts of the current design need to change before launch: the magic link, the "lives forever" rule, and abuse controls. The rest is hardening.

## Blocking issues

**1. A session token in a query string is a leak.** `?session=<token>` ends up in:
- Server, CDN and proxy access logs.
- Browser history.
- `Referer` headers sent to third-party scripts on the welcome page.
- Link unfurlers (Slack, Discord, email scanners). These make a GET request, and that request can consume or burn the token.
- The agent's transcript, which is often logged, shared or pasted into bug reports.

Anyone who reads the link is logged in as the owner. The agent also has to relay the link to the human, so it is guaranteed to pass through a log.

**Fix:**
- Rename it to a *claim token*. It is not a session.
- Put it in the URL fragment: `https://app.ferrocore.dev/welcome#claim=<token>`. Fragments are not sent to servers and not sent in `Referer`.
- The page JS reads it and POSTs it to `/v1/claim`. GET requests never consume it, so unfurlers are harmless.
- Make it single-use, at least 128 bits of entropy, and stored hashed (SHA-256) server-side.
- Give it a short TTL for the link itself (e.g. 24h), separate from the store's TTL.
- Serve the welcome page with `Referrer-Policy: no-referrer` and `Cache-Control: no-store`.

**2. The link logs the human into an account that no one authenticated, with no consent step.** There are two attacks:
- **Login CSRF / session fixation:** an attacker creates a store and sends the link to a victim. The victim clicks it and is silently logged in as the attacker's anonymous account. Anything they then upload (data, secrets, a later-added payment card) lands in the attacker's account.
- **Clobbering:** a human who is already logged in as themselves gets their session replaced.

**Fix:**
- The welcome page must show a confirmation: "An agent created store `abc123` at 14:02 from <coarse location>. Claim it?" The user must click.
- If a session exists, the page offers "Attach to my account" and never replaces the session.
- If no session exists, redeeming the token gives a store-scoped session with limited rights: view, delete, upgrade. It cannot touch billing, other stores or API-key export until the user adds a verified email (or OAuth).
- Claiming means attaching the store to a verified identity. Until then the store stays ephemeral (see issue 3).

**3. "Stores live forever" for unauthenticated creation means unbounded cost and a permanent abuse surface.** Anyone can create stores in a loop and they never go away. Each one costs storage and an index, and each one can hold abusive content: phishing payloads, malware staging, a free dead-drop for exfiltrated data.

**Fix: ephemeral by default, permanent only when claimed.**

| State | Lifetime | Limits |
|---|---|---|
| Unclaimed | TTL 24h (consider 7d as a ceiling), non-renewable by the agent | Tiny quota (e.g. 10 MB, low ops/s), no public/shared access |
| Claimed (free) | Persistent, but reaped when idle (e.g. no reads/writes for 90 days → suspend → delete after +30 days with email warnings) | Free-tier quota |
| Claimed (paid) | Until deleted | Plan quota |

Other lifetime rules:
- Return `expires_at` in the create response so the agent can tell the human.
- Send expiry warnings once a claimed store has a verified email.
- Unclaimed expiry is a hard delete. Run a purge job and measure it.

**4. No abuse controls are specified.** Unauthenticated write endpoints get found fast.
- Rate-limit per IP and per /24 or /48, plus a global circuit breaker. For example, 5 creations per IP per day and 1 per 10s, with a lower cap for known hosting ASNs. Return `429` with `Retry-After`.
- Add a cheap proof-of-work or a signed attestation challenge for bulk traffic. Don't use CAPTCHAs: agents can't solve them and it defeats the purpose.
- Cap unclaimed stores per IP, so a single IP can't hold hundreds of live stores.
- Add content scanning or at least value-size and key-count caps. Give unclaimed stores no public read path.
- Add a kill switch: an operator can bulk-suspend by IP, ASN or fingerprint.
- Alert on creation rate and on the unclaimed-to-claimed ratio. A collapse in that ratio is the signal that the endpoint is being farmed.

## Tightening (not blocking)

**Request and response shape.** Return the data-plane credential directly in the JSON body, separate from the claim link. The agent needs the credential to use the store, and never needs the claim token to work.

```http
POST /v1/instant
Idempotency-Key: 6f1c...        # prevents retry loops creating duplicate stores
Content-Type: application/json

{ "client": "claude-code/1.x", "region": "eu-west-1" }   # both optional
```

```json
201 Created
{
  "store_id": "st_8Qx...",
  "endpoint": "https://st-8qx.eu-west-1.ferrocore.dev",
  "api_key": "fc_live_...",             
  "claim_url": "https://app.ferrocore.dev/welcome#claim=<token>",
  "state": "unclaimed",
  "expires_at": "2026-10-31T14:02:00Z",
  "limits": { "storage_mb": 10, "ops_per_sec": 20 },
  "notice": "Store deletes at expires_at unless claimed. Do not commit api_key."
}
```

Notes on the response:
- `api_key` is scoped to this store only and is shown once. Support rotation and revocation, including from the claimed session.
- Do not return `claim_url` over a channel you can't control. Tell agents in the API docs and the `notice` field to hand it to the human and not to log or persist it.
- Make the claim token revocable. Claiming consumes it. Re-issuing needs the `api_key` (`POST /v1/stores/{id}/claim-link`).
- Add `DELETE /v1/stores/{id}` authenticated with the `api_key`, so an agent can clean up after itself.

**Operational details:**
- Accept `Idempotency-Key`, and return the same store for a repeated key within a window.
- Never log request bodies, `Authorization` headers or claim tokens. Add a log-redaction test.
- Show the claim page's domain as fixed (`app.ferrocore.dev`) so a prompt-injected agent can't be talked into emitting a different phishing link: serve the link only from the API response, never accept a caller-supplied base URL.
- Quotas: enforce them server-side at the store level, including key count and value size, not only totals.
- Region: default by IP geolocation rather than asking, since agents rarely know.
- Tests: expiry purge, single-use token (second redeem fails with exactly 410, after a positive control that the first redeem succeeds), unfurler GET doesn't consume the token, logged-in session isn't replaced.

## Open questions for the engineer

1. Is 24h the right unclaimed TTL, or should it be longer so a human who opens the link next morning can still claim?
2. Does claiming require email verification, or is OAuth (GitHub/Google) enough?
3. What's the abuse tolerance per IP, and who owns the on-call for the kill switch?
4. Should unclaimed stores be readable only from the creating IP range? This is a strong control, but it breaks agents running in ephemeral cloud sandboxes.
5. Is there a legal or retention constraint on deleting unclaimed data (GDPR erasure is easy here, but check logs and backups)?

## Summary of changes to the original design

| Original | Change |
|---|---|
| `?session=<session_token>` in query | Fragment-carried, single-use, hashed *claim* token, redeemed by POST |
| Link logs the human in directly | Confirmation step, store-scoped limited session, never replaces an existing session |
| Stores live forever | Unclaimed TTL, claimed stores reaped when idle with notice |
| No abuse controls | Per-IP/ASN limits, global breaker, quotas, kill switch, monitoring |
| Not specified | Idempotency key, scoped one-time `api_key`, agent-side delete, log redaction |