# Terraform provider for Cobblewick: no-go for v1.0.0 in three weeks

**No-go on a provider now, and no-go on a 1.0.0 in three weeks.** Spend the three weeks on the API gaps and on measuring demand. Revisit the decision at week 3.

## Why: two blockers

### 1. Demand fails the "ship when two signals hold" test (step 1)

| Signal | Status |
| --- | --- |
| Community provider with real downloads or issues | No. None exists. |
| Deals or security reviews asking for a Partner-badged provider | No evidence. |
| Long-lived configuration objects | Unknown. Needs interview Q3. |
| Customers already scripting the API in pipelines | Unknown. |

- The only demand is one customer asking in passing last month.
- That is at most one signal, and probably zero.
- No community provider means no proof anyone wants this.

### 2. The API fails the gate (step 2)

The skill's contract rule 1 says a resource MUST NOT ship while its gate row reads FAIL or UNKNOWN. I scored one assumed object, "employee", keyed on email plus company. I assumed your other objects behave the same, since you said most lack IDs.

| Check | Employee | Verdict |
| --- | --- | --- |
| Stable server-assigned ID | **FAIL** | The skill says "none - fix the API". Without an ID, import, `moved` and identity are impossible. A key built from email plus company changes whenever the email changes, and each update recreates the object. |
| GET returns every writable non-secret field | UNKNOWN | Counts as FAIL. |
| In-place update | **FAIL** | The skill's compensation is `RequiresReplace`, but here every edit would destroy and recreate payroll data. That compensation is not safe for payroll data. |
| Idempotent create | **FAIL** | A retried create makes a duplicate. If the API is synchronous, compensation is possible: no client retry on create, or look up by the unique key first. That is fragile, and it is useless if creates are async. |
| Bounded propagation | UNKNOWN | Counts as FAIL. |
| Pollable async op with ID in the 202 body | UNKNOWN | Without an ID this is "fix the API". |
| Deterministic normalization and ordering | UNKNOWN | Counts as FAIL. |
| Secrets identified | UNKNOWN | Counts as FAIL. |
| Documented rate limits | UNKNOWN | Counts as FAIL. |

No Go code fixes this. A provider on this API would show a perpetual diff or a destroy-recreate on edits. Retries would leave duplicate records in customers' payroll systems.

### Why the schedule is also wrong

- The skill's first-release template runs about 10 weeks to a 1.0.0 or 0.x tag. That plan assumes a passing gate and one developer for the whole time.
- The 1.0.0 label promises schema compatibility. Rule 3 makes every removal or rename a major after that.
- A schema built on today's key scheme would have to break the moment you add real IDs.
- One developer cannot also carry the Partner commitments: nightly acceptance tests, critical fixes in 48 hours, others in 5 business days. They do not need Partner for a first release, but this shows the maintenance load.

## What to do in the three weeks

1. **Week 1: close the demand question.**
   - Reply to the customer and ask what they would manage in Terraform. Ask whether they script the API today, and whether a deal depends on it.
   - Search support tickets and sales notes for "Terraform", "IaC" and "OpenTofu".
   - Ask whether they run Terraform or OpenTofu, and which version.
   - Record the answers. If you reach two signals, the demand gate opens.
2. **Weeks 1-2: fill the full gate matrix.**
   - Use the template in `plan-templates.md`, one column per object.
   - Resolve every UNKNOWN: propagation times, async behaviour, whether the 202 carries an ID, rate limits, secrets, and whether GET returns every writable field.
3. **Weeks 1-3: file the API asks as product work.** These are the "fix the API" rows, so they are product work, not provider work. Your Go developer can own the design.
   - A stable server-assigned ID on each object, plus in-place update (PUT or PATCH).
   - An idempotency key on create. See `samber/developer-platform-skills@api-idempotency-retry`.
   - Rate limits documented. See `samber/developer-platform-skills@api-rate-limit-policy`.
   - Any async operation returns the object ID.
4. **Week 3: decision point.** Check demand and gate status again.
   - If demand holds at two or more signals and the ID, update and idempotency rows are scheduled, start the build on the vendor-owned hand-written path. Cover the 5 to 15 objects customers configure most, on the Plugin Framework.
   - If demand is still one passing question, stop. Say so to the customer and keep the API fixes, which help your SDK and REST users anyway.

## If you build later

- Publish under your final GitHub organization from the first release (rule 6).
- Sign releases with an RSA key registered on both registries (rule 5).
- Tag `0.x` while the resource map still moves. Promise compatibility only from `1.0.0`. That is the `1.0.0` date to commit to, and only once the gate is clean and the schema is stable.
- Cut order if time runs out: actions and functions, then list resources, then the least-used data sources. Never cut import support or upgrade tests.
- Skip OpenAPI generation for full coverage. It ships spec gaps as bugs.

## Assumptions to confirm

I recorded these as UNKNOWN or assumed, because you did not answer the skill's interview questions:

- Q3: which objects customers configure once versus create constantly.
- Q4: the rest of the API shape listed above.
- Q5: whether you have a sandbox account for acceptance tests and an on-call owner for provider issues.
- Q6: target tier and the oldest Terraform and OpenTofu versions customers run.

Answers could change the gate rows. They do not change the three blockers: no demand evidence, no stable IDs, and non-idempotent create with recreate-on-update. Of the three, only the stable-ID row can be fixed in your three weeks, by an API change.

I did not run any code or check your actual API. Everything above comes from your description and the skill's rules.