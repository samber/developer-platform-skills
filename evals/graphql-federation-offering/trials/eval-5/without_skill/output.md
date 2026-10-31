Don't just delete the subgraph on Friday evening. Delete it earlier, in a set order, and cut the other data paths too. I'm assuming managed federation (Apollo GraphOS-style registry), so the commands and polling behaviour below are from general knowledge, not from your setup.

## Biggest gaps

1. **Deleting from the registry doesn't stop traffic.** Routers keep the old supergraph until they pick up the new one.
   - Managed routers poll for the new schema. Self-hosted routers need a redeploy.
   - Until each replica runs the new schema, it keeps calling Tidemark's URL and sending entity data.
   - Confirm every replica runs the new supergraph. Don't treat "deleted in registry" as "stopped".

2. **Removing the field breaks clients that query it.** An unknown field is a validation error, so the whole operation fails, not just that field.
   - This is a partners graph, so external partners may query `tidemark_payrunSummary` or `Tidemark_` types.
   - Run schema checks against real traffic or usage reports for the last 30 days.
   - Find persisted queries, safelisted operations and your own UI using the field.
   - Warn those clients before the cutover.

3. **Composition can fail.** Other subgraphs may reference `Tidemark_` types or extend `Company` in ways that depend on Tidemark.
   - Look for `@key`, `@external`, `@requires`, `@provides` and shared types.
   - Run the composition dry-run first. Use `rover supergraph compose` with the Tidemark subgraph removed. Check the `rover subgraph delete` flags for a dry-run option.
   - Don't discover composition errors Friday at 18:00.

4. **The graph is not the only data channel.** Legal said "stop sending customer data". Check everything else Tidemark touches.
   - Webhooks, event streams, ETL, scheduled syncs and exports for the 30 tenants.
   - OAuth tokens, API keys and installation records. Revoke or disable them.
   - Header propagation from router to subgraph. Tenant IDs and auth tokens ride along.
   - Caches holding Tidemark responses: entity cache, response cache, CDN.
   - Logs and traces that forward to Tidemark.

5. **Timing.** "From Saturday" probably means 00:00 in some timezone.
   - Friday evening leaves no buffer if the deploy fails.
   - Ask legal for the exact cutoff and timezone.
   - Do the cutover Thursday or Friday midday.

## Also do

- Save the Tidemark subgraph SDL and the variant config before deleting. If legal or the contract changes, you can restore it.
- Delete from every variant (prod, staging, others) and check the main graph doesn't also include it.
- Check router config for stale entries naming the removed subgraph, such as `override_subgraph_url` or per-subgraph headers. Stale entries can warn or error on startup.
- Tell the 30 tenants.
  - Update the sub-processor list and DPA documents.
  - Hide the Tidemark UI and remove the install for those tenants.
  - Ask legal whether you must notify them.
- Ask legal about data already sent. Cutting off doesn't retract it.
  - Get a written deletion or return confirmation from Tidemark.
- Add a fast hard stop that doesn't depend on the schema, such as an egress block or a `override_subgraph_url` to a dead stub. Use it only if the rollout slips.

## Order

1. Today, about 30 min: grep your code and run schema checks or usage reports for the field and types.
2. Today, about 30 min: run the composition dry-run without Tidemark.
3. Thursday: message partners and clients using the field. Revoke webhooks, tokens and sync jobs.
4. Thursday or Friday midday, about 1 h: delete the subgraph, recompose, roll out routers, confirm every replica's supergraph hash.
5. Same day, about 15 min: check results.
   - Query `tidemark_payrunSummary` and expect a validation error.
   - Check egress logs show zero requests to Tidemark's host.
6. Saturday morning, about 5 min: re-check egress logs.
7. Next week: collect Tidemark's deletion confirmation.

Next: run the composition dry-run without Tidemark, and paste any errors.