# Verdict: not done

The page documents the happy path well. It leaves out nearly everything your support data says readers need. The prose may read beautifully, but the page doesn't yet help someone whose call fails.

I only saw your summary of the page. I couldn't check the JSON response or the curl example, so those rows are marked as unverified.

## Rubric

| # | Criterion | Status | Notes |
|---|---|---|---|
| 1 | Endpoint, method, one-line purpose | ✅ Pass | |
| 2 | Parameter list with type, required/optional, constraints | 🟠 Partial | Present, but several constraints are missing (see row 3). |
| 3 | Parameter edge cases | 🟠 Partial | Missing items:<br>- Maximum `amount_cents`.<br>- Which currency codes are accepted (ISO 4217?).<br>- What `currency` must match, and whether a mismatch with either account's currency is what triggers `currency_mismatch`.<br>- Whether source and destination can be the same account.<br>- Whether `memo` allows Unicode, and whether 140 counts characters or bytes. |
| 4 | Auth and required headers | ❌ Missing | Nothing on authentication or scopes. |
| 5 | `Idempotency-Key` header | ❌ Missing | The endpoint honors it, but the page doesn't mention it. For money movement this is the most important safety feature. Document:<br>- The key format.<br>- How long keys are retained.<br>- What a replay with the same key and same body returns.<br>- What a replay with the same key and a different body returns.<br>- Whether the first request is still in flight. |
| 6 | Success response | 🟠 Partial | The page shows a full example JSON. It has no field-by-field table. It also doesn't say whether `200` means the transfer is settled or only accepted, or which statuses the transfer object can hold. |
| 7 | Error responses | ❌ Missing | The page lists no errors at all. At minimum it needs `402 insufficient_funds` and `422 currency_mismatch`. It should also cover the statuses the endpoint can return for validation, auth, unknown account, and idempotency conflicts. Confirm those with engineering rather than guessing. |
| 8 | Prerequisites | ❌ Missing | Support says most failures come from the source account not having cleared KYC. The page never says a transfer needs a verified source account. Say how readers can check an account's KYC status and what error an uncleared account produces. |
| 9 | Troubleshooting guidance | ❌ Missing | There is no mapping from symptom to cause to fix. |
| 10 | Working request example | ❓ Unverified | A $25.00 curl is good. Check four things:<br>- It uses `amount_cents: 2500`.<br>- It includes the `Idempotency-Key` header.<br>- It uses a placeholder token, not a real one.<br>- Its output matches the response example. |
| 11 | Scope and focus | 🟠 Partial | Four paragraphs on double-entry accounting don't belong on a reference page. They push the information readers need further down. Keep one sentence about the two ledger entries and link to a concept page. |
| 12 | Side effects and observability | 🟠 Partial | The page says every transfer produces two ledger entries. It doesn't say how to retrieve those entries, or whether they appear immediately. |

## What to do

1. Add an **Errors** section as a table with columns for status, code, cause, and fix. Start with the two errors support sees most.
2. Add a **Before you call** note on KYC. Say that the source account must be verified. Link to wherever KYC status is shown.
3. Add an **Idempotency** section covering the points in row 5. Use `Idempotency-Key` in the curl example.
4. Add a response field table and the transfer status lifecycle.
5. Move the ledger essay to its own concept page and link to it. It is good writing, so keep it, but put it where it won't compete with the reference content.
6. Fill in the parameter constraints from row 3.

Once those are in, the page can ship. Quality of prose isn't the measure for a reference page. The measure is whether a developer who hits a 402 or 422 can fix it without opening a support ticket.

Two questions would let me tighten this: what do the transfer object's statuses look like, and what does an uncleared KYC account actually return? If it returns `402` or `422`, tell me which. I'd rather not guess.