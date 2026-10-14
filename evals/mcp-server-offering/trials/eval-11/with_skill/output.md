# Okerlund Expense MCP App: design review

**Verdict: ❌ don't build as designed.** The queue app is the right call, because stepping through a queue item by item is a listed MCP Apps use case. But `approved_in_ui=true` lets anyone skip the confirmation on a tool that moves real money. Two more items (calendar completion, the result-shape change) will also break in production.

## Blockers

### 1. 🔴 `approved_in_ui=true` is a client-set flag that skips the gate

- Any model, script, other MCP client or prompt-injected receipt can send `approved_in_ui=true`, and then `pay_batch` runs with no confirmation.
- The skill's test for every safety pattern is that an end user can't bypass it by switching clients. This fails that test.
- "A click inside the app is not approval." A UI-initiated write must pass its tier's gate exactly as if the model had called it.
- The server can't prove a human clicked. Receipt text (merchant, notes, OCR) is untrusted input, and the third-party scripts in the CSP (finding 2) run in the same iframe as the buttons.

**Fix**
1. Tier each tool, one tier per tool:
   - `approve_expense` and `reject_expense` are **Contained Write**.
   - `pay_batch` is **Critical**: money out, irreversible.
2. Drop the flag. Keep per-item approve/reject clicks in the app, as they are Contained Writes. Back them with server-side attribution (manager as the principal), async audit, and idempotency keys. Add a per-manager approval limit, and don't let a manager approve their own expenses.
3. Keep one gate on `pay_batch`, but make it one per batch, not one per item. It should show the count and the total, and ask once.
   - Use elicitation or a host-level confirmation, or a server-minted single-use token.
   - Bind the token to user, batch id, total amount and expiry.
   - This also fixes the 40 round-trips complaint. The 40 prompts come from per-item gating, and approving 40 items then paying once is 41 clicks and 1 confirm.
4. Add a `dry_run` on `pay_batch` that returns the payees, amounts and total. Add spend caps per manager, company and day.
5. Check whether the MCP Apps spec lets you mark `approve_expense`/`reject_expense`/`pay_batch` as app-only (hidden from the model). That would shrink the attack surface. I couldn't verify this from the skill, so check the ext-apps spec.
6. Keep the non-UI path unchanged. Every app-backed tool must stay complete without its UI, for headless clients and agent fleets.

### 2. 🔴 CSP is wider than the job needs

- `*.okerlund.io` covers every subdomain, including any dangling one. List exact origins.
- Bundle React into the single HTML file (`vite-plugin-singlefile`, the default in the build guide). That removes the CDN entirely.
- Drop Segment and Intercom. They would sit in a financial approval screen that shows receipts and bank-adjacent data, and a compromised script there can read the DOM or click Approve.
- Measure usage with server-side OpenTelemetry (queue items cleared, app-rendered vs text calls) instead.
- Drop `camera` now. Request permissions only for features the job needs today. Add it in the release that ships receipt capture. Adding it later is additive, and the host may prompt or deny it anyway.
- Ask 2-3 design partners whether their security teams allow iframe-rendered third-party UI in their assistant. The skill calls this an open question, not a settled yes.

### 3. 🟠 "Batch complete when the calendar reminder lands"

- The calendar handoff goes through the host and needs the user's consent. It also needs a connected calendar connector. The user may decline, have no connector, or run headless.
- The server never sees whether the reminder landed. Completion would hang forever, or you'd mark it complete on a guess.
- Define completion from server state: payout `initiated`, `settled` or `failed`, with failures surfaced in the result.
- Make the reminder a best-effort extra and make it idempotent. Never gate state on it.

### 4. 🟠 Switching `pay_batch` to grouped-by-employee two weeks after launch

- The tool's result shape is part of the contract. Changing it breaks the app silently, and breaks agents too.
- Hosts can preload and cache the `ui://` resource, so old UI and new server can meet.

**Fix**
- Keep the flat list and add a `by_employee` field, or an opt-in `group_by` parameter.
- Version the `ui://` resource with the tool and ship them in the same release.
- Keep the old shape readable for at least 90 days. Add a version marker in the response envelope and log it on every call.
- Hash the tool surface and run golden-prompt tests in CI.

## Smaller items

- 🟠 **Tool names:** `approve_expense` and the others lack a service prefix (`okerlund_…`). Add prefixed names as aliases and don't rename, since renames break agents silently.
- 🟠 **Annotations:** set `destructiveHint` honestly on `pay_batch`. They are hints, not controls.
- 🟠 **Escaping:** escape all receipt and employee data in the UI.
- 🟠 **Auth:** the server is an OAuth 2.1 resource server. Check the token audience and never forward the bearer token upstream. Keep instances stateless.
- 🟠 **Testing:** test in two hosts plus one client without the extension.
- 🟠 **Success metric:** round-trips per 40 expenses, and queue items cleared per session.

## Revised design

1. Queue app: per-item Approve/Reject, with attribution, audit, idempotency and limits.
2. One `pay_batch` confirmation showing the total, with a server-side dry run, caps and a batch idempotency key.
3. Result shape additive: flat list plus `by_employee`.
4. CSP: exact `okerlund.io` origins only, or none if everything is bundled. No Segment, Intercom or camera.
5. Batch status comes from payout state. The calendar reminder is optional.

## Gates

| Gate | Status |
|---|---|
| Safety coverage (one tier plus a named pattern per write tool, irreversible tools gated) | ❌ fails today, passes with the revised design |
| Auth conformance | ⏳ unverified, no details given |
| Curation (5-15 tools) | ✅ 3 write tools plus the reads |
| Evidence hygiene | ✅ no figures cited |

## Questions that could change this

I assumed the answers below. Tell me if any is wrong.

1. Do unattended agents or enterprise fleets call these tools? I assumed yes, which makes server-side gates mandatory.
2. Is "Pay" one button for the whole batch, or per item? I assumed per batch.
3. Is a payout reversible, and how long does it take to settle? I assumed neither: irreversible, settles asynchronously.
4. Is the same person allowed to approve and pay? I assumed separation of duties is wanted.
5. Have any of the 20,000 customers' security teams said anything about iframe UI? I assumed no.

I didn't save anything to the `developer-platform-context.md` memory file the skill suggests. Say so if you want it.