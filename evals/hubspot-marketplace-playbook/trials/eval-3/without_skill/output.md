**Next action (30 min):** open HubSpot developer docs and write down 4 facts below. Plan hinges on them. I am working from memory, not live docs, so verify each.

1. Sunset date for classic CRM cards and legacy (non-projects) apps.
2. Whether your app can migrate in place and keep app ID, client ID, and 140 installs. I recall a CLI migrate command for public apps.
3. Current agent-tool format, and which Breeze agents can call them.
4. Current marketplace listing requirements. I recall a minimum active-install count (60?), reference customers, and a security review. 140 installs likely clears the count, but confirm it.

## Order: migrate, then agent tools, then list

Why this order:
- Listing review checks the app as it ships. Scope or feature changes after listing risk re-review.
- Agent tools need the new platform. So migrate first.
- Adding scopes forces re-consent in portals. Do all scope changes in one release, not two.

Exception: start listing paperwork in parallel from week 2. It has lead time and no code dependency.

## Plan (13 weeks)

**Week 0-1: Discovery and gates**
1. Verify the 4 facts above. Record the sunset date. If the date falls inside the quarter, migration becomes urgent and everything else waits.
2. Inventory the 140 portals: tier (Free/Pro/Enterprise), which use cards, active vs dormant. Dormant installs may not need the cards migrated.
3. Inventory API usage: endpoints, versions, webhooks, the OAuth refresh flow, and the settings page. List every legacy endpoint to replace.
4. Pick the migration path: in-place (keeps installs) vs new app (needs 140 reinstalls). Recommend in-place. Choose new app only if HubSpot blocks it.
5. Decide the final scope list now, including scopes agent tools will need. Make them optional where the platform allows.

**Week 2-6: Migration**
1. Move the app into a project. Repo, CI, and `hs project` deploys in source control.
2. Rebuild the cards as new UI extensions. Keep the data fetching on your backend.
3. Keep classic and new cards working side by side if the platform allows, with feature parity as the gate.
4. Pilot with 5-10 friendly portals across tiers. Soak 1 week.
5. Roll out in cohorts (10%, 40%, 100%). Keep a rollback path per cohort.
6. Email customers before any re-consent step. Support gets a runbook.

**Gate A (end of week 6):** all active portals on the new cards, no classic dependency, error rate flat. Do not start tools until this passes.

**Week 6-9: Agent tools (book jobs)**
1. Split tools by risk:
   - Read-only first: check availability, look up job or customer.
   - Write second: book, reschedule, cancel.
2. Booking writes real work orders and technician time, so:
   - Idempotency key on every booking.
   - Explicit confirmation step before commit (agent proposes, user confirms).
   - Server-side permission check per portal and per user.
   - Audit log per call.
   - Rate limits.
3. Map each HubSpot portal to its Trackpoint account. Reject ambiguous mappings.
4. Test with adversarial prompts: double-book, wrong time zone, missing contact, duplicate contact, and a prompt that tries to book for another portal.
5. Pilot with the same 5-10 portals. Read-only tools first, then writes.

**Gate B (end of week 9):** zero cross-portal leakage in tests, zero duplicate bookings under retry, and a documented rollback (kill switch per tool).

**Week 2-13: Listing, in parallel then final**
- Weeks 2-8 (no code needed): privacy policy, terms, support contact and SLA, security questionnaire answers, listing copy, screenshots, demo video, 2-3 reference customers from the pilots.
- Weeks 9-10: update screenshots and copy to include the agent tools. Run a final scope check against what the code requests. Do not request scopes you do not use.
- Week 10: submit.
- Weeks 11-13: review buffer. Expect at least one round of feedback. Budget for it.

## Risks, ranked

1. **Sunset date is earlier than the plan.** Mitigation: check in week 0, reorder if needed.
2. **Re-consent drops installs.** Mitigation: one scope change, optional scopes, customer email, pilots.
3. **Agent writes the wrong booking.** Mitigation: confirm step, idempotency, read-only first.
4. **Listing review slips past the quarter.** Mitigation: prepare paperwork early. Treat "submitted" as the quarter goal and "live" as a bonus.
5. **Install base was never reviewed.** Your 140 installs came through your own page, outside the marketplace. Check each install flow meets the current OAuth requirements before submitting.

## Quarter goals

- Must: Gate A passed. Gate B passed. Listing submitted.
- Not promised: listing live inside the quarter, since HubSpot controls review time.

## Open questions for you

1. Do all 140 portals use the cards, or only some?
2. Does Trackpoint already expose a clean booking API with idempotency?
3. Who owns the backend work: how many engineers, and any other commitments this quarter?
4. Is a fallback acceptable, i.e. listing without agent tools if tools slip?

**Next:** answer question 3. Team size sets whether weeks 6-9 can overlap with migration.