**Verdict:** Keep the annotations. Drop the confirm-everything idea. Don't rely on either for safety, because the real limits belong in server code.

## What to change

1. **Annotations are hints, not enforcement.** MCP clients may ignore `destructiveHint`, and the spec says to treat server annotations as untrusted. Claude Desktop may show a dialog, but users can usually pick "always allow". Other clients, API agents, and headless runs may show nothing. Test in your real client before you put "shows a dialog" in the spec.
2. **Set the full annotation set, not just destructive.**
   - `cancel_order`: `destructiveHint: true`, `idempotentHint: true`.
   - `issue_refund`: `destructiveHint: true`, `idempotentHint: false`. Retries can double-pay, so require an idempotency key.
   - `send_shipping_notice`: it destroys no data, but it can't be recalled. Set `openWorldHint: true`, and treat it as a gated write.
   - Every read tool: `readOnlyHint: true`.
3. **"Ask the user first" in the description is a soft nudge.** Keep it for UX. It is not a control. The model can skip it, and text inside order data (customer notes, product titles) can talk the model out of it. Never let this line be the reason a refund is safe.
4. **Enforce the limits server-side.**
   - **Refund cap:** apply $500 to the cumulative total per order and per time window, not per call. Otherwise an agent can split one refund into many. Reject anything over the order's remaining refundable amount. Define the currency for non-USD retailers.
   - **Over the cap:** return "approval required" and route it to a human queue. Don't just fail.
   - **Tenant isolation:** with about 900 retailers, scope every tool to the caller's retailer through the auth token. Never trust a `retailer_id` or `order_id` that the model passes in.
   - **Order state:** block cancelling shipped orders. Define what cancel does to payment and inventory, and whether it auto-refunds, so cancel plus refund can't pay twice.
   - **Audit log:** record who, which agent session, and which tool call for each action.
5. **Treat the email tool as a phishing risk.**
   - Take the recipient from the order record, never from a parameter.
   - Use a fixed template with structured fields (new carrier, new ETA). Don't accept a free-text body.
   - Rate-limit it per order and per retailer.
6. **Drop confirmations on read tools.** Dialogs on every call teach users to click "allow" without reading, so the three dialogs that matter get approved by reflex. They also slow every agent flow. Protect reads with authorization and tenant scoping, not prompts.
7. **For a real human gate, use a server-driven step.** Either add a two-step flow (`prepare_refund` returns a quote and a token, and `execute_refund` requires that token), or use MCP elicitation if your target clients support it. Both hold up even when the client skips its dialog.

## Open questions to answer in the spec

- Who is "the user" being asked: retailer staff, or the end customer?
- Who may approve a refund? Do you need a role check?
- Can a cancel be undone once payment is captured or stock is released?
- What triggers the revised shipping notice, and can the agent resend it?

## Spec-ready summary

- Three write tools, each with full annotations.
- Limits are enforced in server code: aggregate refund cap, tenant scoping, state checks, idempotency keys, audit log.
- Emails use a fixed template and an order-derived recipient.
- Reads are annotated read-only and carry no prompts.
- Human approval above the cap goes through a server-side step.

**Next:** decide who the approver is, whether the retailer's staff or the end customer. The approval design depends on that answer. It takes about 5 minutes.