# Ledgerline API reference audit

I couldn't run the audit itself. I don't have your OpenAPI spec, the Contentful page export, or sandbox access in this session, and I haven't seen docs.ledgerline.com. So there are no page-level findings below. I'd rather not invent any.

Your own numbers already change what to expect, though.

## 1. Expect more than polish

- **52 operations vs 49 pages.** At least 3 operations probably have no page. The real gap is likely larger. Pages for removed or renamed endpoints and pages that cover several operations both hide missing coverage in a net count.
- **The spec is generated from code and the pages are hand-written.** The spec is the source of truth, and nothing forces the pages to follow it. They change only when a PM remembers to tell the writers.
- **Good prose and good traffic don't show the pages are accurate.** A well-written page that is stale is the worst case for a payouts API. Readers trust it, and traffic means more people hit the wrong parameter, status or error code.
- **Where drift usually sits:** newly added optional fields, enum values, error codes, changed defaults, required-ness changes, new headers, and deprecations. Writers rarely notice any of these.

My prior is that the audit finds real accuracy defects, with the missing pages first. If it finds only polish, that is worth knowing, but I wouldn't plan around it.

## 2. Audit method, in order of value

1. **Coverage diff.** Match `operationId`, method and path against the page list, in both directions.
   - Operations with no page.
   - Pages with no operation (stale).
   - Pages whose path or method differs from the spec.
2. **Contract diff per page.** Compare each page with its spec operation on these points.
   - Parameters: names, required/optional, types, defaults, enums, formats and limits.
   - Request and response fields, including nullable ones.
   - Status codes and error codes.
   - Auth scopes and required headers.
   - Idempotency, pagination and rate-limit behavior.
3. **Example truth test.** Run every documented request against the sandbox.
   - Does it succeed?
   - Does the real response validate against the spec schema?
   - Does it match the documented response, including field names and money units?
4. **SDK parity.** For the Python and Node snippets on each page, check that the method exists in the current SDK version. Then run the snippets in the sandbox.
5. **Cross-cutting pages.** These are where integrators lose the most time.
   - Authentication and key types.
   - Error model.
   - Idempotency.
   - Pagination.
   - Rate limits.
   - Webhooks and signature verification.
   - Payout status lifecycle and terminal states.
   - Currency and amount representation.
   - Sandbox vs production differences.
6. **Lifecycle.** Check deprecation markers, the changelog against spec history, and versioning statements.
7. **Polish.** Do this last: wording, consistency, link rot, and screenshot or snippet style.

## 3. Severity rubric

| Level | Meaning | Example |
|---|---|---|
| 🔴 Blocker | An integrator following the page gets money, data or auth wrong | Wrong required field, wrong amount unit, missing idempotency requirement |
| 🟠 Major | The page is wrong or missing and the integrator can recover | Undocumented endpoint, example fails, stale enum |
| 🟡 Minor | Incomplete but not misleading | Missing optional field, missing error code |
| 🟢 Polish | Style only | Wording, formatting |

## 4. Coverage diff script (**reads** two files, **writes** nothing)

```python
import json, sys
spec = json.load(open("openapi.json"))
ops = {(m.upper(), p): o.get("operationId")
       for p, item in spec["paths"].items()
       for m, o in item.items()
       if m in {"get","post","put","patch","delete"}}
# pages.csv columns: method,path,url  (one row per Contentful endpoint page)
import csv
pages = {(r["method"].upper(), r["path"]) for r in csv.DictReader(open("pages.csv"))}
print("Spec ops with no page:", sorted(set(ops) - pages))
print("Pages with no spec op:", sorted(pages - set(ops)))
```

Normalize path parameters first (`{id}` vs `:id`). Check for paths documented under more than one operation, and for pages that cover two operations.

## 5. What I need to run it

1. The OpenAPI 3.1 file (current main).
2. The Contentful export of the 49 endpoint pages. JSON or the Content Management API is fine.
3. A sandbox API key. Put it in an env var and don't paste it in chat.
4. The current Python and Node SDK versions.
5. The page list with method and path, if it isn't in the export.

With those, I'd split the work as a rolling pipeline of Sonnet agents, one per page. Each agent does contract diff, example run and SDK check. A single Opus pass would then merge the findings and rank them.

## 6. Fix the cause too

The audit is a one-time cleanup. The drift will return unless the process changes.

- **Add a CI drift check.** On every spec change, diff operations and schemas against a manifest of documented ones. Fail or ping the writers when they diverge.
- **Generate the contract parts from the spec.** Parameters, schemas and error tables can be rendered into Contentful or alongside it. Writers keep the prose, examples and guides.
- **Run the examples in CI against the sandbox,** so a broken snippet shows up as a failing build.
- **Notify the writers automatically.** The notice should name which operations changed, so it no longer depends on a PM remembering.

If you send the five inputs above, I'll produce the actual findings report in this format.