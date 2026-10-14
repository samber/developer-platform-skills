# Nimbusgrid v2 API keys

**Start here:** the engineer is right about entropy and wrong about the problem. Nobody guessed your customer's key. They read it, in a public repo, for three weeks. No amount of randomness helps once a key is public, so email hygiene alone doesn't fix this.

## Why UUIDv4 failed

- **Undetectable.** A bare UUID looks like every resource ID, trace ID and request ID. Secret scanners can't flag it without drowning in false positives, so GitHub's scanning could never have caught it.
- **Easy to mishandle.** Customers log, paste and commit UUIDs freely because they're normally non-secret. Nothing about the string says "secret".
- **No integrity check.** Your gateway can't tell a typo from a bad key without a database hit.
- **Weaker guarantee than it sounds.** The "122 bits" holds only if the generating library used a CSPRNG. RFC 9562 says it should, but it doesn't guarantee it.

## v2 key format

```
nbg_sk_live_<32 base62 chars>_<6 char checksum>
```

| Part | Purpose |
|---|---|
| `nbg_` | Distinctive vendor prefix. This is what makes scanner registration possible. |
| `sk` / `pk` | Key kind. Secret keys never go in client code, publishable keys can. |
| `live` / `test` | Environment, visible at a glance. |
| 32 base62 chars | About 190 bits from a CSPRNG. Use base62 so a double-click selects the whole key. |
| CRC32 checksum | Lets scanners and your gateway reject non-keys offline, which cuts false positives. |

Server-side rules:

- **Store only a hash.** Use SHA-256 of the secret. A slow hash like bcrypt isn't needed for high-entropy tokens.
- **Use a separate public key ID for lookup.** Look the key up by ID, then compare hashes in constant time.
- **Show the key once** at creation.
- **Store metadata with each key:** owner, project, scopes, created, last-used, expiry, and the label the customer gave it.
- **Allow two active keys per project**, so rotation needs no downtime.
- **Check the v1 store.** If v1 keys are stored in plaintext, fix that in the same release.

## What to do about leaks

Layered, in priority order:

1. **Join leak-scanning programs.** Register the `nbg_` pattern with GitHub's secret scanning partner program, and with GitLab and package registries where they offer one. When a v2 key hits a public repo, GitHub sends you the token and you revoke it, usually within minutes. This is the single biggest fix. Also run your own scan of public sources for the pattern.
2. **Auto-revoke on confirmed public exposure.** Notify the customer immediately with the location of the leak. Make "revoke automatically" the default, with an opt-out only for customers who can show they have rotation automation.
3. **Shrink blast radius.**
   - Scope keys per project, environment and action. Default to least privilege.
   - Set an expiry (for example 90 days) and make rotation easy.
   - Offer an optional IP allowlist.
   - Add spend caps and anomaly alerts. For serverless hosting, the usual leak abuse is crypto-mining on the customer's bill.
   - Show last-used time and source in the dashboard.
4. **Remove static keys from CI.** Offer OIDC federation (GitHub Actions and others) so deploys use short-lived tokens. A key that doesn't exist can't be committed.
5. **Fix the developer workflow.** The CLI should store credentials in the OS keychain, not in project files. Document env-var use. Ship a pre-commit hook or `nimbus doctor` check. The hygiene email still belongs here, but as a supporting measure.

## Handling v1

- **Dual-accept for a fixed window.** Publish a deprecation date (about 6 months) and revoke remaining v1 keys at sunset.
- **Hunt for v1 leaks.** You can't register a pattern for them, but you can search public code for your env-var names (`NIMBUS_API_KEY=` and the like). Check every UUID you find against your key hashes, and revoke and notify on any match.
- **Make v1 less attractive.** Give v1 keys no new features, and alert on use from new IPs.

## The incident you already had

- **Pull the logs** for that key across the three weeks and look for use that wasn't the customer's.
- **Tell the customer** what you found, and check your contractual and regulatory notice obligations.
- **Run a retro.** The real gap was that nothing noticed three weeks of unusual use. Add anomaly detection regardless of key format.

## Reply to the engineer

"Entropy stops guessing. Our incident was exposure, and for exposure what matters is that we can detect, revoke and limit a key. A prefixed, checksummed format lets us do all three, and a UUID can't."