# Integration surface order for Tandemly

**Recommendation:** build turnkey payroll connectors first and a public REST API last. Do not skip the API. Build it as a by-product of the connectors, behind a dated, conditional commitment to the board.

## Why this order

- **Your buyers don't call APIs.** Office managers and HR directors never write code, so a public REST API gives them nothing to use. What closes deals is connecting their payroll tool in an afternoon.
- **A public API costs more than it looks.** It needs auth and scopes, rate limits, versioning, docs, a sandbox, and support. With one platform engineer, that work would stop connector work for months.
- **The board's goal and sales' goal can both be met.** "API-first" is a design principle, not a product you must ship publicly. Build every connector on a clean internal, versioned API. Publishing part of it later is then cheap.

## Order

| # | Surface | Effort (estimate) | Why now |
|---|---|---|---|
| 1 | **Guided CSV/spreadsheet import** with templates, column auto-mapping and a preview before commit | ~1–2 weeks | Works for every prospect, whatever payroll tool they use. It also becomes the fallback for the long tail. |
| 2 | **Native connector #1**: OAuth connect, employee roster sync, hire date, location and status, with a preview-then-import wizard | ~6–8 weeks | This is the "turnkey" demo. Pick the payroll tool that appears most in your pipeline and lost deals. |
| 3 | **Native connector #2**, built by the contractor on the pattern from #2 | ~4–6 weeks | Gives a second demo and proves the pattern is repeatable. |
| 4 | **Long-tail coverage via a unified HRIS/payroll API vendor** (Finch or Merge are the usual candidates) | ~2–4 weeks to evaluate and integrate | Buying coverage may beat building 10 connectors. Verify their coverage of your target tools, per-connection pricing, and data-handling terms first. |
| 5 | **Outbound webhooks and events** (for example "employee out of compliance") | ~3–4 weeks | This is the first piece of the surface that is externally visible, and it needs little support. |
| 6 | **Public REST API, v1, read-only** | ~8–12 weeks | Ship it when the triggers below fire. |

**Start now, because lead time is outside your control:**
- Apply to the payroll vendors' partner and marketplace programs. Approval can take weeks to months.
- Request sandbox accounts for demos. A demo against a real sandbox beats a mock.

## What to tell the board

Suggested wording:

> We are API-first in architecture. Every integration runs on our internal versioned API. We will publish a read-only public REST API once two payroll connectors are live. We also publish it earlier if a partner, a marketplace, or three or more customers need it. Until then, a public API serves no current buyer and would stall the integrations that close deals.

Put the triggers on the roadmap as explicit gates:
1. Two connectors are live.
2. Any partner or marketplace listing requires a public API.
3. Three or more customers or prospects ask for API access.

## Resourcing

- **Platform engineer** owns the architecture, the internal API, and credential and token storage. You handle employee PII, so security review sits here and is not contracted out.
- **Contractor** builds CSV import (#1) and connector #2 (#3) against the engineer's pattern. Do not let a contractor design the pattern.
- **Do not split the engineer** between connectors and a public API. That is the failure to avoid.

## Make "within an afternoon" a measurable target

- Track **time from signup to first successful sync**. A reasonable target is under 60 minutes at the median, with no engineer involved.
- Required product behaviors:
  - Self-serve OAuth.
  - Auto-mapping of fields.
  - A preview step before import.
  - Plain-language errors.
- Make the CSV fallback good enough that a failed connector never blocks setup.

## Data to check before committing (about one day)

1. Which payroll tools appear in the last 20–30 won and lost deals? This sets the connector #1 and #2 choices.
2. Do those vendors have open APIs, or are they partner-gated? Gated ones change the timeline.
3. How many prospects have asked for API access, as opposed to "integrates with X"? If it's zero, that settles the board question.
4. Which direction does data flow? A payroll-to-Tandemly roster sync is the likely core. Write-back is a later phase.

## Risks

- **Vendor lock-in or cost** from a unified API provider. Check pricing at your expected connection count.
- **Payroll-vendor API changes** break connectors. Budget ongoing maintenance, roughly a fraction of an engineer.
- **Board pushback.** The gated commitment above gives them a date and conditions. A bare "no" would not.
- **All timelines above are my estimates.** They depend on the vendors' API quality, so validate them with your engineer before presenting them.