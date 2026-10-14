# Recommendation: build the shell, buy the engine

Build the site and the design layer yourselves. Don't build the API reference renderer. Use an open-source or licensed OpenAPI component and theme it with your design tokens. Keep your CMS as the source for guides and customer stories.

I haven't seen your CMS, your specs or your gateway config, so the conditional parts below rest on assumptions. I list them at the end.

## Why not a fully bought platform

Mintlify, ReadMe and Redocly are fast to stand up. They fail two of your four constraints:

- **Design:** they allow themes, CSS overrides and some custom components. They don't allow pixel control, and the layout and navigation patterns stay recognizably the vendor's. That is the templated look your head of design is rejecting.
- **Content workflow:** their editors or git-based content would take over guides and stories. Marketing would have to move off the CMS they already use, or you'd pay to sync two systems.

Fast time to launch is the only strong argument for buying. That matters less with two contractors and 10 weeks.

## Why not a fully custom build

Building the OpenAPI reference (schema rendering, `oneOf`/`allOf`, code samples in several languages, a try-it console, search) is the part that eats 10 weeks. It adds nothing a customer can see that an existing component doesn't. Two contractors will run out of time on it, and you'd inherit the maintenance afterward.

## Architecture

1. **Site framework:** Astro or Next.js, your own design system and tokens. Design controls all layout and typography.
2. **API reference:** Scalar or Redoc components, themed with your tokens. Both are embeddable and open source. Check each one's license and theming depth first, and pick the one whose DOM your designer can actually restyle.
3. **Guides and customer stories:** pulled from your existing CMS through its API at build time. A publish webhook triggers a rebuild, or incremental regeneration if you use Next. Marketing publishes in the CMS and the site updates with no ticket.
4. **Specs:** the gateway is your single source of truth. Export one OpenAPI spec per product from it in CI and publish all four under one site with a product switcher. One gateway means one auth model, one error format and one set of rate-limit docs, so write those once as shared pages.
5. **Search:** Pagefind (static) or Algolia DocSearch. Don't build your own.
6. **Try-it console:** point it at a sandbox only. This is a payroll API, so it must never touch real employee data.

## 10-week plan for two contractors

| Weeks | Contractor A (platform) | Contractor B (front end) |
|---|---|---|
| 1 | Spec export from the gateway in CI, CMS API audit | Design-token handoff with design, component inventory |
| 2–4 | Site scaffold, CMS ingestion, preview and webhook rebuild | Page templates, navigation, product switcher |
| 3–6 | Reference integration for all four specs | Themed reference, code-sample tabs |
| 6–8 | Search, sandbox try-it, auth docs | Guide and story templates, accessibility pass |
| 9 | Content migration, redirects, SEO basics | Visual QA with design |
| 10 | Launch buffer, runbook, handover | Launch buffer, handover |

Weeks 9 and 10 are deliberately buffer. Most of the schedule risk sits in the spec export and the CMS integration.

## Decision gates

Check these in week 1 before committing:

1. **Does your CMS expose a content API?** If it is a headless CMS or has a REST or GraphQL API, the plan holds. If it is a page-builder CMS that can only render HTML, either embed its output or adopt a different approach for guides. Tell me which CMS it is before you commit.
2. **Is the gateway's OpenAPI export clean?** If the specs are missing descriptions, examples or error schemas, budget 1–2 weeks of cleanup. A themed renderer can't fix a poor spec.
3. **Does the reference component take your design?** Have Contractor B theme one real endpoint page by end of week 2 and have the head of design sign off. If it fails, fall back to a bought renderer or a more heavily customized one. Don't hand-build the renderer.

## Fallback

If gate 1 or 3 fails, the second-best option is a bought platform (Redocly or Mintlify) with maximum theming, used for the reference only. Guides and stories would stay on your CMS under a matching shell. That sacrifices some design control but keeps the marketing workflow.

## Risks

- **Ownership after week 10:** contractors leave. Name an internal owner now, or the site rots. This is the biggest long-term risk.
- **Four products on one site:** versioning and per-product changelogs add scope. Cut per-product versioned docs from v1 if time slips.
- **Design scope creep:** freeze the design system by the end of week 2.

## What I assumed and need from you

- Which CMS is it, and does it have an API?
- Is there a named internal owner for the site after launch?
- Do you have sandbox environments, and are the gateway specs reasonably complete?
- Do the four products have different audiences or a shared developer account?

If the CMS and the spec both pass their gates, go with the build-the-shell plan above.