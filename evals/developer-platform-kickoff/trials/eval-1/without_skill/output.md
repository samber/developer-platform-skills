**Do this first (30 min):** book a 30-minute slot with the CRO and the engineering lead, and ask one question: "Who is a partner?" Also ask who owns breaking changes. Both answers gate everything below.

## Recommendation

Do not start with a spec. Start with a CSV inventory, an owner, and a rule for breaking changes. Then publish a small documented API and webhooks. Do not build a marketplace or platform.

Why this rung: it is cheap and reversible with notice, and your customers' internal teams are the cheapest builders. It also frees the two engineers directly. Partner-built integrations come later, once the API has real users.

## Plan

1. **Define "partner" (this week, 30 min).** Pick one:
   - customers' own IT teams
   - carriers or TMS vendors that feed you data
   - resellers or integrators
   - independent software vendors (ISVs)

   Each one wants a different API, so the answer decides scope.
2. **Inventory the CSV drops (about 1 day).** Make one row per customer with these columns:
   - direction (in or out)
   - columns
   - frequency
   - engineer-hours per month
   - ARR of the customer
   - who asked for an API

   This is your counted demand and your baseline. Expect a few schemas to cover most drops. Those schemas become v1.
3. **Name the approver for breaking changes (this week).** Write one line in the repo: "API owner: X. Breaking changes need X plus the engineering lead." My suggestion is you as owner, since you are the platform PM. Without a named person, nobody can safely publish anything.
4. **Write the deprecation policy (about 2 hours).** Put it in the README before any endpoint ships:
   - a version in the URL (`/v1`)
   - notice period before removal
   - additive changes are never breaking
   - CHANGELOG entries are tagged breaking, additive, or fix

   I would propose 12 months of notice for partners. That number is my default, not a standard. Replace it with what your contracts allow.
5. **Write the spec first, as the source of truth.** Commit an OpenAPI file to the monorepo. Cover only the top two or three flows from the inventory, probably shipment and event ingest, status lookup, and webhooks for status changes. Add contract tests in CI that fail on breaking diffs.
6. **Dogfood the API.** Rebuild your CSV importer on top of the same endpoints. If internal code bypasses the public API, the public one stays second-class. This also lets you migrate customers off CSV without you doing the work.
7. **Publish a minimal docs site.** It needs auth, a quickstart that gets a first call working in 15 minutes, an error reference, rate limits, and a sandbox. Do this after the spec exists, not before.

## Readiness gates

| Gate | Status | How to resolve |
|---|---|---|
| Counted demand | Unknown | CSV inventory, step 2 |
| Stable internal interfaces | Unknown | Ask engineering whether the CSV importer shares the domain model with the product |
| Builder supply | Unknown | Step 1 answer, plus three customer calls |
| Staffing | Partial | The two CSV engineers are your funding source, if migration works |
| Competitor bundling | Check | Name which larger visibility platform could ship the same API. If a customer asks for yours because of theirs, that is your risk. |

Do not commit to a public date until the first two resolve.

## What you owe once it is public

- an API owner and a deprecation policy (steps 3 and 4)
- support for third-party bugs, which arrive as your outage
- an auth and scopes model that a customer security review will accept
- a written wind-down path, in case you ever retire the API

## Measure

- **Baseline today:** engineer-hours per month on CSV, and the number of active drops.
- **Target (set after the inventory):** drops migrated to API, hours freed, and time to first successful call.
- **Kill or de-escalate:** if fewer than the agreed share of the top CSV customers have moved to the API by the end of the cycle, stop expanding scope. Set that threshold and date with the CRO at kickoff, not later.

## Pushback for the CRO

"An API for partners" is a goal, not a requirement. If no named partner is waiting for it, this is a cost-reduction project first and a sales story second. Ask for three named partners who would integrate. If the CRO cannot name them, the cheaper answer is a standard CSV or JSON schema plus a self-serve upload, not a full API.

## Questions I need answered

1. Who are the "partners" the CRO means?
2. Does a date force this, such as a renewal or a partner deal?
3. Is there a security review function that can approve the auth model?

**Next:** open a spreadsheet and list your CSV customers with columns, frequency, and engineer-hours. About 1 day. Paste me the top 5 rows and I'll draft v1 endpoints from them.