# Platform cases: how real graphs let partners in

Load this when the team cites "X lets partners extend its graph" as precedent, or wants a worked model for one ladder rung.

No major public API platform verifiably composes raw, partner-owned federated subgraphs into its production public graph. Every case below keeps schema ownership with the platform. Absence claims rest on public documentation and talks, not on stated refusals.

| Platform | What partners get | Ladder rung | Who owns the schema | Lesson |
| --- | --- | --- | --- | --- |
| Shopify | App-owned metafields and metaobjects under the reserved `$app` namespace | 1 | Platform defines shapes; the app owns its definitions | Ownership namespace plus uninstall semantics |
| Atlassian (GraphQL Gateway, Forge) | Forge modules, runtime-registered dynamic modules, Teamwork Graph connectors that ingest into Atlassian-defined object types | 1, 2 | Atlassian | Partners contribute data into a platform schema, not schema into the graph |
| Hasura | Remote schemas (v2) and a GraphQL connector (v3) added by the instance operator | 3 | Operator | Namespacing and header defaults built into the remote-schema config |
| Hygraph | Remote sources and remote fields per project | 3 | Project owner | Per-field placement and a default response cache on remote fields |
| Apollo GraphOS | Subgraphs within one organization; contracts filter what partner consumers see; Connectors map a REST API into the graph declaratively | 3 | Graph organization | Contracts serve partners as consumers, not contributors |
| WunderGraph Cosmo | Subgraphs, contracts, feature flags; REST connectors | 3, 5 | Graph organization | Technically possible to accept partner subgraphs; no public program |
| Block (Square) | A public graph third-party developers query | n/a | Block | Third parties consume; public subgraphs were merged into the internal graph |

## Shopify: the ownership namespace

- Definitions declared in the app-reserved namespace ensure "only the owning app can make changes to definitions."
- Shopify later removed public access for app-owned data (`PUBLIC_READ_WRITE` became `MERCHANT_READ_WRITE`); apps needing cross-app access must move to a custom namespace. Isolation tightened over time, never loosened.
- On uninstall, Shopify deletes the app-owned definitions and temporarily retains the values without a definition - an offboarding contract a raw subgraph never has.
- Functions can read app-owned metaobject entries, but only `$app`-prefixed types.

## Atlassian: data into platform types

- Forge apps call the gateway as the user or as the app; they do not extend it.
- Teamwork Graph connectors ingest third-party objects into canonical types such as documents. An app either calls the graph API or provides a connector, not both.
- Nadel, the gateway's open-source engine, exposes nothing undeclared: "if a schema member is not declared in the .nadel file it is not exposed." Explicit allowlisting plus type and field renaming is the strongest built-in collision defense among the engines reviewed.
- Gateway rate limiting is cost-based per user; schema producers set field cost with a directive; the default budget is in the order of ten thousand points per user per minute, with 429 and Retry-After over budget.
- Administrators approve the external domains a Forge app may send data to: an admin-side consent gate worth copying for any partner resolver.

## Hasura and Hygraph: operator-added remotes

- Hasura v2 remote schemas: `forward_client_headers` defaults to false; `customization` sets a root-field namespace and type-name prefixes; header precedence runs configuration headers, then session variables, then client headers.
- Hasura v3 replaces remote schemas with a GraphQL connector that can forward entire headers - a reminder that the safe default changed with the version.
- Hygraph sets headers per remote source and per remote field, can forward all client headers, and caches queries with remote fields for minutes by default.

## Scale references (internal federation only)

- Netflix: 200+ services in its federated graph.
- Booking: about a hundred subgraphs serving billions of requests a day. Its engineers state that a 20% latency increase "causes a lot of booking loss."
- Brex: dozens of subgraphs, with about a third of the federated graph found to be dead code.

All of these are internal domain teams. None publishes a partner-subgraph count or failure rate.
