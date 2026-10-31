**Don't make "delete subgraph + recompose" the legal control. Cut the data flow first, then remove the schema.**

Deleting the subgraph is a schema change. Legal's requirement is about data leaving. Those are two different things, and the plan only covers the first.

## What the plan misses

**1. Recompose is not the cutoff. The running router is.**
- A new supergraph in the registry changes nothing until each router instance loads it.
- Polling delay, a rolling deploy, a stuck pod or a pinned schema file can leave old instances calling Tidemark after Saturday starts.
- Cut at the egress layer or the credential. Treat the schema removal as cleanup.

**2. What Tidemark receives is bigger than the field you can see.**
- Every `@requires` field on `Company` ships to Tidemark on each resolve, even when the client never selected it.
- A list query ships it once per row.
- Pull the SDL and list every field Tidemark receives: the `@key` fields, each `@requires` field and client arguments.
- That list is your evidence for legal of what was sent. It also shows whether anything beyond payroll-summary data left.

**3. Tidemark may reach you through other channels.**
- Check each of these before calling the cutoff complete:
  - Per-tenant OAuth grants, API keys or webhooks that Tidemark holds.
  - Webhook subscriptions that push events to Tidemark.
  - A sync job that exports data to them.
- If any exist, the subgraph deletion does nothing to them. Revoke them all.

**4. Client breakage across the ~30 tenants.**
- Once `tidemark_payrunSummary` leaves the schema, any query that selects it fails validation as a whole.
- The failure is not a null in that one field. The tenant's whole query errors, so their dashboards break.
- A deprecation window is normally required for this. Legal's deadline removes it, so decide on purpose how to cover the gap.
- Run the registry's removal-impact check now.
  - Cosmo: `wgc subgraph check --delete`.
  - Apollo: run operation checks against a composition without the subgraph.
- Pull per-field usage for `tidemark_payrunSummary` and the `Tidemark_` types over the last 30 days.
- Identify which tenants and which apps call them.
- Warn those tenants **before** Friday. Say what breaks, from when, and what to do.

**5. Other subgraphs may depend on Tidemark types.**
- Check whether another partner subgraph references `Tidemark_` types, or uses `@provides` or `@shareable` on them.
- If so, the recompose can fail or break that partner. Run the check on a copy of the composition first.

**6. Caches and stored queries.**
- Clear any cache entries that hold Tidemark responses.
- Check for persisted queries, APQ stores or CDN caches that could keep serving or replaying them.
- Partner responses should not sit in shared caches. Confirm that.

**7. Past data is a separate legal question.**
- Cutting now does not undo what Tidemark already holds.
- Ask legal whether you must send a deletion or return request, and whether you need written confirmation of deletion.
- Keep the router logs and the field list from point 2 as evidence.

**8. Tenants and UI.**
- Decide the state for the ~30 installed tenants: uninstalled or suspended.
- Decide what happens to Tidemark-related values stored in your platform and when they are deleted. The skill's rule is to define uninstall semantics up front: definitions deleted, values retained for a stated period.
- Remove any Tidemark UI, install prompt or marketplace listing.
- Tell tenants when they will be notified and what they should do.

## Revised plan

| When | Step | Time |
| --- | --- | --- |
| Now (Mon–Tue) | Ask legal the 3 questions below | 15 min |
| Now | Run the removal-impact check and pull field usage; list affected tenants | 1–2 h |
| Now | Build the data-clearance list from the SDL (point 2) | 1 h |
| Now | Check other channels: OAuth grants, webhooks, sync jobs | 1–2 h |
| Wed | Notify the ~30 tenants and any app owners that call the field | 1 h |
| Wed–Thu | Dry-run the cut on staging: recompose without the subgraph, confirm the router and tests pass | 1–2 h |
| Fri evening | **Cut data flow first.** Revoke the per-partner credential or block the egress host for Tidemark. Confirm calls fail. | 15 min |
| Fri evening | Revoke every other Tidemark grant or webhook (point 3) | 30 min |
| Fri evening | **Then** remove the subgraph from the partners variant and recompose. Roll out to every router instance. | 30 min |
| Fri evening | Clear caches (point 6) | 15 min |
| Fri night | **Verify the cutoff** (below) | 15 min |
| After Saturday | Follow up on deletion confirmation from Tidemark and the post-cutoff log review | — |

Order matters: the credential or egress block works even if a router lags on the new supergraph.

## Verify the cutoff

- Router and egress logs show zero requests to Tidemark's host after the cut time. Check every router instance.
- Query `tidemark_payrunSummary` before the schema removal. It should return null plus a masked error, with the rest of the `Company` data intact. This works only if the field is nullable. If the field is non-null, the whole object blanks. Check this first.
- After removal, the schema no longer lists the field and the `Tidemark_` types.
- Check Tidemark-installed tenants individually (the ~30).
- Run a test call to Tidemark's endpoint with a platform credential and expect a rejection.

## Questions for legal (answer before Friday)

1. Does "stop sending data from Saturday" cover only new transmissions, or also a deletion or return of data Tidemark already holds?
2. What cutoff time counts as Saturday, and in which timezone?
3. Must you notify the ~30 tenants, and by when?

## Decision for you

Before Friday, decide: do you break the tenants' queries on Friday, or keep the field in the schema returning null for a short window?

- **Keep the field, return null (my recommendation if a short window is allowed).**
  - The data flow stops Friday. Legal is satisfied.
  - Tenants' queries keep working, so you give them a real deprecation window.
  - You remove the schema field after the window.
  - Condition: `tidemark_payrunSummary` must be nullable, and a platform-owned stub resolver returns null. A stub means a platform-owned field. Do this only if legal agrees that the field name staying visible is not a problem.
- **Remove the field on Friday.** Simplest, but ~30 tenants may see failures Saturday morning. Only do this with notice sent first.

## Assumptions I made

- The graph is not consumed by the main router, per your note. If `Company` extensions or Tidemark types also appear in the main router's graph, the scope is larger. Tell me.
- Tidemark's subgraph is the only data path. Point 3 may disprove that.
- I could not see your SDL, router config or registry, so I do not know whether the field is nullable or whether a per-partner credential exists. Check both.

**Next (2 minutes):** send the 3 questions to legal, then run the removal-impact check from the registry.