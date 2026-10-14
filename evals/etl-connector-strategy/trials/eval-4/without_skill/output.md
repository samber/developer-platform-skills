# Build decision: ELT connector for the Veridian Labs renewal

**Do first, this week (about 1 hour):** ask the customer's data team in writing which ELT tool they run, and whether "available in" means (a) works on their instance or (b) listed in the vendor's public catalog. That answer can add months, and everything below depends on it.

## Recommendation

Build one Python connector with a **static schema**, on the framework of the customer's tool. Put most of the effort into a clean incremental export API underneath it.

| Customer tool | Build this | Why |
|---|---|---|
| Airbyte | Connector Builder (declarative YAML), with the Python CDK only for the parts YAML can't express | Little code to maintain. Two Python engineers can drop to the CDK when needed. |
| Fivetran | Connector SDK (Python) | Runs on Fivetran's infrastructure, so you host nothing. |
| Meltano, Stitch or Singer | A Singer tap in Python | It is open, and several tools can run it. |
| Unknown or several | The Singer tap | It is the widest-reach option. Airbyte and Meltano can both run it. |

I haven't checked current vendor programs or terms. Confirm them before committing. My reasoning for the choices:

- **Python SDK or CDK, not a vendor-managed or no-code route.** Half your backend team already writes Python daily. The 4 hours a month after launch only works if any engineer can fix the connector without ramp-up.
- **Static schema, no dynamic discovery.** Your object schema barely changes, so hand-written stream definitions are cheap to keep. Skip the generic discovery layer.
- **Declarative first.** Every line of custom code is something you maintain at 4 hours a month.

## Where the 3 engineer-weeks go

1. **Week 1, export API.** Add an incremental read path with an `updated_at` cursor, stable pagination, and a way to report deletes (soft-delete flags or a tombstone stream). Add per-tenant auth and rate limits. This is the real work. Without it, any connector will be fragile.
2. **Week 2, connector.** Implement the streams, state handling, and a full-refresh fallback. Test against a staging tenant with realistic volumes.
3. **Week 3, hardening.** Contract tests in CI, and a pinned framework version. Write the customer setup doc and run a joint test with their data team.

## Clinical-trial constraints that can blow the estimate

Check these in week 1. If any of them forces new work, the 3 weeks won't hold:

- **Sensitive data.** Which fields must be excluded or masked in the export? Do you need an audit log of exports? Does the customer need validated or GxP-style evidence?
- **Deletes and corrections.** Trial data gets amended. If the export misses edits or deletes, their warehouse silently diverges from your system.
- **Data residency and credential scope.** Use read-only, per-tenant tokens.

## After launch: the 4 hours a month

- A CI job runs the connector against staging nightly and alerts on failure.
- Upgrade the framework quarterly, in a fixed 2-hour slot.
- A schema change means a change-log entry first, then a connector update.
- One named owner, plus one backup who writes Python.

## Timeline against a 5-month review

- **Weeks 1–2:** tool confirmed, written definition of "available" agreed.
- **Weeks 3–6:** build.
- **By month 2:** customer runs it on their side.
- **Months 3–5:** buffer for catalog listing or vendor review. If "available" means a public listing, start that process right after the build, because I expect it to be the slowest step.

## Fallback

If the tool is obscure, or the listing process won't finish in time, propose scheduled Parquet or CSV exports to their object storage, with a documented schema. Most ELT tools ingest that without a custom connector. This only works if the customer accepts it in writing as meeting the condition, so ask before you build anything.

## Open questions that would change this answer

1. Which ELT tool, and is a public listing required?
2. Will other customers want the same connector? If so, the Singer or Airbyte route has more reuse value.
3. Does the export API already support incremental reads, or does it need building from scratch?