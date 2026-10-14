# What you're signing up for

## Bottom line

You are not signing up for a sprint or two of JDBC driver work. You are committing to **a customer-facing data product** with three parts:

- a tenant-isolation and workload-governance layer
- connectors for two BI tools
- a long-term certification and support obligation

The driver is the smallest of the three. Six weeks is realistic for a **design-partner beta**. It is not realistic for "certified with Tableau and Power BI".

The timelines below are my estimates, not vendor commitments. Verify the certification mechanics with each vendor's partner program before you quote dates to Sales.

## Four problems in the proposal

### 1. Power BI does not use JDBC

- Power BI has no JDBC connector, and neither does the on-premises gateway.
- It reaches custom sources through ODBC or a Power Query (M) custom connector.
- A Type-4 JDBC driver therefore gets you Tableau only.
- Power BI needs a second deliverable: an ODBC driver (usually C/C++) or an M connector over an HTTP API.

### 2. Pointing the driver straight at the shared cluster is a security hole

- Client-side code is not a security boundary. Customers can modify or bypass the driver.
- If tenant scoping happens in your app tier today, a direct connection skips it. That means cross-tenant reads on a cluster holding all 60 customers' events.
- Direct access also means exposing ClickHouse to the internet or via private links. Each customer then needs its own credentials, TLS, IP allowlists, and audit logging.
- Without server-side limits, BI workloads hurt every other customer. Tableau dashboards fire dozens of queries on load, extract refreshes scan everything, and refreshes cluster at the top of the hour.
- **Fix:** put a gateway between the driver and ClickHouse. The gateway handles authentication, mandatory tenant scoping, query governance, quotas, concurrency limits, result caching, and audit logs. The driver becomes a thin client over it.

### 3. VQL is the hard part

- Tableau and Power BI generate ANSI-flavored SQL: subqueries, joins, window functions, date math, custom SQL.
- VQL must either support that natively, or the gateway needs a SQL-to-VQL translation layer. That is a parser and planner, not a driver.
- Certification tests this heavily. Tableau requires passing its TDVT suite, which covers thousands of expression and logical-query tests. Any VQL gap becomes a failed test or a degraded feature in the dialect file.
- Once VQL is a published, certified dialect, you owe customers backward compatibility. VQL changes become breaking changes for external users.

### 4. Certification is a calendar you don't control

- Tableau: you build a connector package (manifest, dialect, connection dialog), pass TDVT, then go through partner review. Uncertified connectors can be sideloaded on Desktop and Server, but not on Tableau Cloud.
- Power BI: a custom connector works uncertified only if each customer enables it and installs it on their gateway. Certified status requires Microsoft's review.
- Both reviews can run weeks to months and come after the engineering is finished.
- Both vendors ship new versions on their own schedule, so you retest and often recertify indefinitely.

## Realistic estimate

| Workstream | Estimate | Notes |
|---|---|---|
| Gateway with tenant isolation and governance | 1–2 months | Needed under every option |
| SQL surface or translation for BI-generated queries | 1–3 months | Depends on how complete VQL is today |
| Tableau connector, TDVT pass, review | 2–3 months of engineering, plus 1–3 months of review | |
| Power BI ODBC or M connector, certification | 2–3 months of engineering, plus 2–4 months of review | |
| Ongoing ownership | About 0.5–1 FTE | Releases, JDK and BI-tool compatibility, support, docs, recertification |

Rough total: **6–9 months to certified on both, with 2–4 engineers.** That is not 1–2 sprints.

## What you can ship in 6 weeks

- A tenant-safe gateway, with per-customer credentials, mandatory scoping, quotas, and query timeouts.
- An uncertified Tableau connector, sideloaded, for 5–10 design partners.
- For Power BI, either a documented ODBC or M path, or nothing yet.
- Clear "beta, uncertified" labeling, with Sales told exactly that.

## Alternatives to evaluate before committing

1. **Postgres-wire-compatible endpoint on the gateway.** Tableau and Power BI both ship native PostgreSQL connectors. There is no custom driver and no certification, and one endpoint serves both tools. You still need the SQL layer and a curated schema or semantic layer, but this removes the biggest calendar risk. I would evaluate this first.
2. **Warehouse or object-store export** (Snowflake, BigQuery, S3/Parquet). Customers use their own BI on their own copy. Isolation is trivial and your cluster stays safe. The cost is data freshness and customer-side setup.
3. **ClickHouse's existing Tableau and Power BI connectors** against tenant-scoped read endpoints with curated views. This is fast, but it exposes ClickHouse SQL instead of VQL.

## Decisions to make before you say yes

1. Who owns tenant isolation: the gateway or the cluster? "Neither" is not an option.
2. Can VQL express what BI tools emit, or is a SQL frontend in scope?
3. Is certification a launch requirement or a later milestone? Sales may only need "works with Tableau and Power BI", which a beta or the Postgres-wire option can deliver sooner.
4. Who funds ongoing ownership? Name the owner and the headcount.
5. Is this a paid-tier feature? Check the compute cost of 60 customers running BI refreshes against the revenue behind the asks.

## Questions for the 60 customers

- Which BI tool does each one use?
- Do they need live queries or extracts?
- Which tables and volumes do they query?
- Would they accept a Postgres-compatible endpoint or a warehouse export instead?

If most would accept either, the custom driver and its certification burden may not be necessary.

## What to tell Sales

"Six weeks gets a limited beta for design partners, with tenant isolation built properly. Certified connectors for both tools are a 6–9 month program, and I'll confirm that once we choose the architecture."