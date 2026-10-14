# Nimbus Telemetry developer portal: where we stand

I scored this with the Pronovix maturity framework from the `developer-portal-design` skill. I worked only from your description, with no walkthrough, analytics or ticket data. The skill asks for those first, so treat the ratings as provisional until someone checks the items under "What I could not verify".

## Bottom line for the VP

- **Stage:** portal as a project, the lowest of the three stages (project, product, critical business infrastructure). It's at risk of slipping further, because nobody owns it.
- **Next level:** portal as a product. That needs a named owner, a backlog, instrumented metrics and visible proof that the portal is maintained.
- **Headcount:** the missing piece is ownership, not volume of work. Approve one named owner first. Buy a managed platform rather than building a custom one. Pronovix's guidance, as the skill relays it, is that an unowned portal decays rapidly, and that is what is happening here.
- **No single score.** Pronovix rejects one number and uses a prioritized Priority 1/2/3 roadmap. I follow that shape. Their formal scoring rubric is proprietary, so for a formal audit you would need to engage them.

## Rating

Scale: **Strong**, **Partial**, **Weak**, **Absent**.

### The three dimensions

| Dimension | Rating | Why |
|---|---|---|
| Operational Excellence (can authors keep it current?) | **Weak** | No owner. Docs are fixed when an engineer happens to notice. No visible authoring workflow. I don't know whether the reference is generated from the OpenAPI spec in CI. If it is, that's a real strength. |
| Developer eXperience (friction across the journey) | **Partial** | The basics exist: reference, key dashboard, getting-started guide. There is no sandbox, request logs, search or assistant mentioned, and no trust signals. |
| Business Alignment (does the portal serve an intentional strategy?) | **Weak** | No evidence of an interface strategy, pre-login decision content or metrics. Nobody is accountable for outcomes. |

### The six focus areas

| Focus area | Rating | Evidence |
|---|---|---|
| Discovery | **Partial** | The OpenAPI reference exists. Nothing mentioned on search, an AI assistant or use-case pages. |
| Decision-making | **Unverified, likely Weak** | Pricing, use cases and comparisons aren't mentioned. If they sit behind login, that is what Pronovix calls "a sales enablement failure". |
| Onboarding | **Partial** | The guide and key dashboard cover the core path. TTFC (time to first call) is probably unmeasured, and there is no test-mode or ready-to-run collection. |
| Go-live | **Weak** | No status page. No mention of usage or quota visibility, or a test/live distinction. |
| Maintenance & troubleshooting | **Absent** | No changelog, no status page, no request logs, and support is an email address. This is the weakest area. |
| Community | **Absent** | Nothing mentioned. Lowest priority. |

Pronovix's juries repeatedly praise release notes, a changelog, a status page and last-updated timestamps as visible proof that a platform is maintained. Nimbus has none of them, and that is the clearest gap.

## What it takes to reach "portal as a product"

### Priority 1: close these before calling the work done

1. **Name an owner.** One person accountable for the portal, with a backlog and a metrics review. This is the headcount ask. Without it, everything else decays again.
2. **Publish a changelog and release notes.** Start with a dated entry for every API change. Use the `changelog-updates` or `developer-relations-skills:changelog-writing` skill for format.
3. **Stand up a status page and link it from the portal.** The practice itself is covered by `samber/developer-platform-skills@api-status-communication`.
4. **Add last-updated timestamps to docs pages.**
5. **Confirm the key dashboard is true self-service.** A developer must be able to create, rotate and revoke keys without a ticket. If any step needs a ticket, you have a documentation site, not a portal. Check this first.
6. **Generate the reference from the OpenAPI spec in CI.** A hand-maintained copy drifts from the spec, which is a listed failure mode. Because docs only get fixed when someone notices, this is likely where drift is hiding.
7. **Instrument TTFC in two stages** (landing to signup, signup to first call). Set an explicit target:
   - Simple REST with token auth: under 15 minutes (practitioner guidance).
   - Complex OAuth plus webhooks: under an hour.
   - Anchors: Ably's top mark is under 30 minutes, and Twilio's public target is 5 minutes.

   Pick the class once you've confirmed Nimbus's auth model. I'd provisionally assume the simple class.

### Priority 2: the next quarter, once an owner exists

1. **Ungate exploration.** Docs, pricing and the catalog should be readable without signup. This is mostly a policy change.
2. **Add a ready-to-run call collection** (importable, forkable). Postman reports a 1.7x average speed-up to first call. That is vendor-reported, so use the ratio and not their baseline minutes.
3. **Auto-provision a sandbox key at signup** and inject it into quickstart snippets. Do this as soon as the TTFC funnel shows developers stalling between signup and first call.
4. **Add a try-it console on endpoint pages**, defaulting to the sandbox with a visible test/live toggle.
5. **Create the solution layer**: use-case pages that connect business problems to APIs. Pronovix finds a "quality collapse" here on most portals.
6. **Add request or delivery logs and usage/quota visibility**, and give the error-code catalog a home.
7. **Replace the support email with a visible escalation path.**

### Priority 3: later

- Search plus an "Ask AI" assistant that cites sources, says "I don't know" when the docs don't cover a question, and routes unanswered questions into the docs backlog. Treat deflection claims (roughly 20-40% of tickets) as directional vendor figures and measure against your own ticket baseline.
- Organization and Project tenancy with roles, if customers need team access.
- Community channels.
- Agent readability for AI visitors, for example `llms.txt`.

## Build vs buy

- **Default: buy a managed platform.** That means a hosted docs/portal product or a portal bundled with your API gateway.
- **Don't build custom** unless you hit one of three conditions:
  - Compliance or data-residency needs no managed platform meets.
  - Business-side authors who need a real CMS.
  - A multi-gateway API portfolio.
- **Never build on an internal-portal framework** such as Backstage. Its security model excludes external users.
- If you do go custom, the owner and funded team must exist first.

## How the VP can judge success

- **Maturity gate:** re-run this benchmark after the work. Every Priority-1 gap must be closed.
- **TTFC gate:** the median TTFC for new signups meets the target.
- **Trends to watch, not gates:** support tickets (against today's baseline), and activation and retention. A fast first call alone is not a retained integrator.

Published rebuilds report large gains, for example PagBank's integration time of 20 days down to 7 and support tickets down 50%. These are agency-reported client retrospectives, not audited. They show that portal changes alone can move these numbers, since the APIs did not change. They are not a forecast for Nimbus.

## What I could not verify

Please confirm these. Each could change a rating:

1. Can a developer create, rotate and revoke keys without a ticket?
2. Is the OpenAPI reference generated from the spec, or hand-copied?
3. Is any pricing, use-case or docs content behind a login?
4. Is there a test-mode or sandbox key?
5. Do you have signup counts, docs traffic, support-ticket volume and any TTFC data?
6. Is the audience mostly integrating engineers, mostly business evaluators, or both? Are they public developers, partners, or both?
7. Is there an existing API gateway or docs tooling investment?
8. Are there compliance constraints?
9. When must this land, and what is the effort ceiling?

Answers 5 to 9 also decide the exact headcount shape. I have not sized the role, and I'd rather not guess a number without them.