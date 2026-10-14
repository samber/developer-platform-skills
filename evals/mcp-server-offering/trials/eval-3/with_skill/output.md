# Sanity check: Marlowe Commerce MCP write tools

## Verdict

Don't write the spec from this plan. All three parts rely on the client or the model to enforce safety, and neither can. The 900-retailer scale makes the gap worse.

| Your plan | Verdict | Why |
|---|---|---|
| Mark cancel, refund and notice as destructive so Claude Desktop shows a dialog | ❌ Not a control | Annotations are hints for clients, not security. A retailer who swaps clients, or runs a background agent, never sees the dialog. Enforcement has to live on your server. |
| Add "ask the user first" to each description | ❌ Not a control | It is a request to the model. A prompt injection in an order note or customer message can override it. The edit also changes which tools agents pick, so it needs the same review as a code change. |
| Confirmation prompt on every tool, reads included | ❌ Counterproductive | Approval fatigue teaches users to click through. Then the three prompts that matter get clicked through too. Reads should pass without a prompt. |

You are right about one thing: these three writes need real friction. Cancel and refund can't be undone, and the shipping notice emails a real person. The friction just has to be server-side, and only on the writes.

## Proposed spec skeleton

### Audience assumption

I assumed some of your 900 retailers will run unattended agents. The surface is therefore designed for the most demanding case. That also covers supervised chat users.

### Tool surface (curated, one risk tier per tool)

Names are verb-first and service-prefixed. This is a starting list of about 7 tools, well inside the 5-15 range. Design it from retailer jobs, not from your API endpoints.

| Tool | Tier | Gate |
|---|---|---|
| `marlowe_search_orders` | Read Only | pass through |
| `marlowe_get_order` | Read Only | pass through |
| `marlowe_get_shipment_status` | Read Only | pass through |
| `marlowe_cancel_order` | Contained Write | approval, dry-run, idempotency key, state precondition |
| `marlowe_issue_refund` | Contained Write (financial) | approval, dry-run, idempotency key, spend caps |
| `marlowe_send_shipping_notice` | Contained Write (messages humans) | approval, dry-run preview, idempotency key, rate cap |
| Refund over $500 | Critical | not exposed; the server rejects it |

Two rules apply to this list:
- **Split any tool that does two jobs.** A cancel that also auto-refunds and auto-emails is three tools. A community Shopify server shipped order-cancel tools that silently emailed real customers. Make `cancel_order` do only the cancel, with no implicit refund or email. If product wants "cancel + refund", expose it as a deliberate second call.
- **Mistake-proof the arguments.** The notice should take structured fields (a reason enum, new carrier, new ETA) rendered through a Marlowe template. It should not take free-text body copy. Free text lets an agent send unreviewed content to a customer under the retailer's brand. It is also an injection channel.

### Write-safety stack

All of this is enforced in your API layer, not in the MCP client:

1. **Scoped credentials per retailer and per tool.** A token issued to retailer A cannot touch retailer B. A "read-only" token cannot call the three write tools. This is the cheapest control with the best protection per unit of effort, so ship it first.
2. **Verified read-only mode.** Add a lockdown switch that strips the write tools. Test that they are actually absent, because GitHub shipped a bug where the flag failed to omit them.
3. **Server-side approval.**
   - Use MCP elicitation where the client supports it.
   - Fall back to a pending-approval state, approved in the Marlowe merchant dashboard. Unattended fleets and clients without elicitation both need this.
   - The human stays the principal. The agent acts under the retailer user's own permissions, with agent and session attribution added.
4. **Dry-run on all three writes.** Add a `dry_run: true` parameter that returns planned effects:
   - for cancel, the order state and what would change;
   - for refund, the amount and the payment destination;
   - for the notice, the rendered email and the recipient.

   Dry-run is rare in the ecosystem, which makes it a differentiator for you.
5. **Idempotency key on every write.** Make it a required parameter. A retried refund or a duplicate email is the likeliest real-world failure.
6. **Spend and rate caps.**
   - **Per-call cap:** $500. Reject above it server-side. Do not silently clamp.
   - **Aggregate cap:** per credential and per retailer, per day. A per-call limit alone lets an agent issue 100 refunds of $500. Pick the number with finance.
   - **Notice rate cap:** per order and per recipient.
7. **State preconditions on cancel.** Allow it only on orders in a cancellable state, such as unfulfilled. The server rejects it otherwise. This is my judgment call. The alternative is to mark `cancel_order` Critical and keep it disabled by default until the audit trail is clean. Decide which fits your risk appetite.
8. **Async audit log on every write.** Record who, which agent, which retailer, the arguments, and the outcome. Undo is largely absent across the industry, so attribution and audit are your substitute for reversibility. Don't promise rollback.

### Annotations (set honestly, as hints only)

| Tool | readOnly | destructive | idempotent | openWorld |
|---|---|---|---|---|
| Read tools | true | false | true | false |
| `cancel_order` | false | true | true (with key) | false |
| `issue_refund` | false | true (money out, irreversible) | true (with key) | false |
| `send_shipping_notice` | false | false per spec wording (additive) | false | **true** |

The spec defines destructive as destructive updates to data. A sent email is additive, so openWorld is the honest flag for it. Marking the notice destructive anyway is defensible, but only as a conservative hint. The approval gate comes from the server tier, not from the annotation.

Don't promise a Claude Desktop dialog in the spec. Client behavior is the client's choice and I couldn't verify it here.

### Hosting and auth

- **Posture:** remote, as a managed platform by default. Go self-hosted only if your server-side policy layer must run in your own infrastructure. The tiering above probably does need to live in your own API either way, so the hosting choice matters less than where the gates sit.
- **Resource server only.** The MCP server validates tokens and never mints them.
- **Protected-resource metadata:** publish RFC 9728 metadata.
- **Token audience:** require resource indicators (RFC 8707). Reject tokens not issued for this server.
- **Issuer validation:** RFC 9207, per the 2026-07-28 revision.
- **No bearer passthrough.** Get your own upstream token by token exchange.
- **Retailer identity:** map each token to exactly one retailer. This is critical for multi-tenancy.
- **Stateless instances.** Don't pin sessions.
- **Hardening:** schema-validate and bound every input, and never leak internal errors.

### Rollout

1. **Stage 1: read-only.**
   - Ship the 3 read tools with OAuth 2.1 and OpenTelemetry from the first call.
   - Publish to the MCP registry.
   - Gate to stage 2: sustained real-client volume (not demo spikes) with a tool-error rate under 2%. Treat both as defaults to calibrate against your own first month.
2. **Stage 2: graduated writes.** Ship refund and notice first, then cancel. Expand only on a clean audit trail, zero unattributed writes, and a reliable approval flow.
3. **Override:** if buyer RFPs actually demand writes, accelerate. Product asking for them is not the same as RFP demand. If volume stays flat for two full quarters, park the server at stage 1.

### Versioning

- Treat names, descriptions and schemas as a contract.
- Keep additive changes and alias old names.
- Hash the full surface in CI.
- Run golden-prompt tests, for example "cancel this order" must select the right tool and not the refund tool.
- Review description edits like code.

### Gate check against the skill's four binary gates

| Gate | Status for your plan |
|---|---|
| Safety coverage: one tier plus at least one named pattern per write tool, irreversible tools approval-gated | ❌ Fails as planned (annotation and description are not named patterns). ✅ Passes with the stack above. |
| Auth conformance | Not specified yet. The auth section above covers it. |
| Evidence hygiene | No adoption figures used here. Keep it that way in the business case. |
| Curation: 5-15 tools, correctly named | ✅ About 7 tools. |

## Questions to answer before the spec is final

1. **Demand:** have retailers or RFPs asked for MCP writes, or is this a product-roadmap idea? Is any community Marlowe server already out there?
2. **Agent types:** will retailers run unattended agents? That decides whether the dashboard approval fallback is stage 2 core or optional.
3. **Cancel:** should it be approval-gated on cancellable states, or Critical and disabled by default?
4. **Aggregate cap:** what daily refund ceiling per retailer will finance accept?
5. **Notice content:** is a templated, structured notice acceptable, or does product insist on free text?
6. **Auth:** do you already run an OAuth 2.1 authorization server, or is MCP the first consumer? If it's the first, the authorization-server design is a separate piece of work.
7. **Deadline and effort ceiling:** is there a date this must land by, and how many engineering hours can you commit? Both can change the hosting choice.

I skipped the skill's up-front question round to give you this answer now. Answers 1, 2 and 3 matter most, and they could re-rank the stack above.