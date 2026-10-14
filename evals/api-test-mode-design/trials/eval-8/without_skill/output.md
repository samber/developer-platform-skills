**Verdict: reject 4 of 5 parts. Fix quickstart and sample data first, since both are exposures you can't take back.**

| # | Proposal | Verdict |
|---|---|---|
| 1 | Unusual key format | ❌ Backwards |
| 2 | Sandbox keys in public repos | ⚠️ Fine only with conditions |
| 3 | Prod key locally, flag in one codebase | 🔴 Worst item |
| 4 | Scrubbed real customer export as sample data | 🔴 Replace with synthetic data |
| 5 | `invalid_credentials` on wrong host | 🟠 Fix |

## 1. Key format: unusual is the wrong goal

Attackers who hold a leaked key don't need to recognize it. They already have it. Unrecognizable keys mainly blind defenders.

- GitHub secret scanning, TruffleHog and GitGuardian match known prefixes and shapes. An odd format means leaks go undetected.
- `VLTC-PRD-<uuid>` is a bare UUID with a label. Generic UUIDs are the shape scanners ignore, because they are everywhere.
- A UUID gives 122 random bits only if it is v4. v1 and v7 contain a timestamp, which weakens the key.

**Change:**
1. Use a distinctive, greppable prefix: `vltc_prd_…` and `vltc_sbx_…`. Lowercase and underscores let a double-click select the whole token.
2. Body: 32 or more bytes from a CSPRNG, base62 or base32. Do not use a UUID.
3. Add a checksum suffix, like GitHub's tokens. Scanners can then validate offline, with near-zero false positives.
4. Register the format with GitHub's secret scanning partner program, and any similar programs.
5. Store only a hash server-side. Show the key once. In the dashboard, show the prefix plus the last 4 characters.
6. Auto-revoke or alert the owner when a leak is reported.

Keeping the environment visible in the prefix is good. Keep that part.

## 2. Sandbox keys in public repos

"Can't touch real employee data" is only true if isolation is real. Verify these first:

- Sandbox uses a separate host, datastore and key store, not just a flag on shared infrastructure.
- A sandbox key has no path to production, including admin endpoints, webhooks and support tooling.

Even with real isolation, public sandbox keys still cause problems:

- **Abuse:** strangers use leaked keys as free compute, as a spam relay through webhooks, or to probe your API for bugs. You will see quota exhaustion and rate-limit blame on the key owner.
- **Attribution:** a per-developer key ties to an account, an org and an email. A committed key links a public repo to that account.
- **Shared state:** anyone with the key reads and writes that developer's sandbox data.
- **Habit:** teaching developers that committing `VLTC-*` keys is fine makes a committed production key one typo away. It also drowns real leak alerts in noise.

**Better:** don't ask developers to commit their own keys. Offer one of these:
- A dedicated public demo key, with a clearly distinct prefix such as `vltc_pub_`. It should be read-only, tightly rate-limited, shared and resettable. Treat it as non-secret by design.
- Examples that read the key from an env var, with a `.env.example` file.

## 3. Production key locally with a config flag

This is the biggest risk. A leaked key is bad, and it is also easy to hit production by accident.

- A developer's laptop, shell history, `.env` files, editor sync and CI logs now hold a payroll-capable key.
- One wrong flag value, or a stale env var, runs example or test code against real payroll data. That includes writes and deletes.
- Sandbox and production keys sit in the same codebase and config file. That is how a production key ends up in a commit.
- The quickstart is copied by thousands of people, so the habit spreads to them all.

**Change:**
1. The quickstart uses the sandbox key only. Production is a separate, later page.
2. Use distinct env var names: `VAULTIC_SANDBOX_KEY` and `VAULTIC_API_KEY`. Never use one variable plus a flag.
3. The SDK derives the host from the key prefix and refuses a mismatch client-side. Default to sandbox. Fail closed.
4. Production keys get scoped permissions, an optional IP allowlist, and no browser or example-repo use.
5. Writes and deletes against production require an explicit opt-in.

## 4. Scrubbed export of a customer's employee list

Do not ship this. Scrubbing HR data usually produces pseudonymized data, not anonymized data, and that is still personal data.

- Small teams are re-identifiable from combinations of job title, department, hire date, salary band and location. The org chart shape alone can identify the customer.
- Scrubbed names can collide with real people.
- Public sandbox plus public example repos means the data is effectively public, and copies cannot be recalled.
- "Friendly customer" is not consent. You need a DPA and a documented lawful basis, and under GDPR and similar laws the customer is the controller.
- If it leaks, the damage lands on a customer and its employees, not only on you.

**Change:** generate synthetic data from a seeded generator. Match the realism you need through statistical shape: salary distributions, tenure curves, department sizes. Don't copy individual records. If someone insists on real-derived data, require legal sign-off, written customer consent and a re-identification review first. Even then, keep it out of public repos.

## 5. `{"error": "invalid_credentials"}` on the wrong host

The same message covers a typo, a wrong environment and a revoked key. A developer will rotate keys and lose hours.

**Change:**
1. Return a distinct machine-readable code, `wrong_environment`, with HTTP 401. Example message: `"This host is production. The key has a sandbox prefix. Use https://sandbox.<host>."`
2. Base the check on the **prefix only**. It reveals nothing about whether the key is valid, so it creates no oracle for attackers.
3. Keep `invalid_credentials` for keys that fail on the right host.
4. Add `request_id` and a docs link to the error body.

⚠️ **Prod key sent to the sandbox host.** Treat it as a possible exposure. Sandbox infrastructure is lower-trust and its logs are usually less protected.
- Never log `Authorization` headers on sandbox.
- Reject the request, and flag the key.
- Notify the owner, and consider auto-rotation.

## Do first

1. Pull the quickstart and the real-data sample set before anything ships. Both are hard to undo once public.
2. Rewrite the key format with the prefix, checksum and scanner registration. It is cheap now and breaking later.
3. Ship the `wrong_environment` error with the key change.

**Next action:** decide whether sandbox keys stay per-developer or become a single public demo key. Every other choice in section 2 follows from that. Reply with which one.