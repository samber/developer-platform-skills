# Discovery and content serving

Contents: listing order, Context7, markdown negotiation, api-catalog, agent card, registries owned elsewhere.

## Listing order

- reach, most first: `Context7 and docs markdown > MCP registry and skill directories > api-catalog > agent card`
- effort, least first: `api-catalog == agent card > Context7 claim > docs markdown > registries`

Registries for MCP servers and skills belong to `samber/developer-platform-skills@mcp-server-offering` and `samber/developer-platform-skills@agent-skill-offering`. Docs entry points (llms.txt, markdown endpoints) belong to `samber/developer-relations-skills@coding-agent-docs-optimization`. This file covers what neither owns.

## Context7

A docs index coding agents query for version-specific library docs.

1. Search Context7 for your library first. Anyone may add a public repo, so a third-party entry may already serve your docs with someone else's parsing choices.
2. Claim it with one `context7.json` that also carries the generated public key: repo-sourced libraries commit it at repo root on the default branch, website-sourced libraries host it under the library's base URL. Claiming unlocks version management and higher refresh limits.
3. Configure the same file: `projectTitle` (100 chars), `description` (500 chars), `folders`, `excludeFolders` (wins over `folders`), `excludeFiles`, `rules`, `previousVersions` (git tags), `branchVersions`. Title and description reject agent instructions and promotion.
4. Name old docs folders so default exclusions catch them (`*deprecated*`, `*legacy*`, `*archive*`, `old`), or list them in `excludeFolders`. A folder named `v1-docs` gets indexed as current.
5. Refresh runs on request once docs are older than a popularity threshold: one day for the top 100 libraries, up to 45 days for the long tail. Add a refresh call on push to the default branch, or a long-tail library serves pre-release docs for weeks.

Only English docs are indexed; source code is a fallback when docs are thin.

## Markdown beyond docs

Docs markdown endpoints belong to `samber/developer-relations-skills@coding-agent-docs-optimization`. This skill extends the same `Accept: text/markdown` negotiation to pricing, plan, limits and status pages, which agents read when they compare or choose products.

- Return `Content-Type: text/markdown; charset=utf-8` and `Vary: Accept`. Without `Vary`, a shared cache serves markdown to browsers or HTML to agents.
- Never send `noindex` on the negotiated response of a canonical URL: crawlers that receive it may drop the page. Give separate `.md` URLs a canonical link to the HTML page; add `noindex` only if they still appear in search results.
- Check conversion output on a real page before announcing it.

## api-catalog (RFC 9727)

`GET /.well-known/api-catalog` returns a Linkset (`application/linkset+json`) pointing at each API's spec, docs and status. Final standard, minutes of work, few readers and few publishers so far.

```json
{ "linkset": [ { "anchor": "https://api.example.com/v2",
    "service-desc": [ { "href": "https://api.example.com/v2/openapi.json", "type": "application/json" } ],
    "service-doc": [ { "href": "https://docs.example.com/api" } ] } ] }
```

## Agent card

`/.well-known/agent-card.json` advertises an agent endpoint for agent-to-agent protocols. Publish it only if the product exposes an agent other agents talk to. It never replaces an OpenAPI spec or an MCP server for a product agents operate.
