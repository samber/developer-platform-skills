# Review of the two Fennimore PRs: both blocked

I haven't seen the diffs, only your descriptions of them, so this review judges the approach. The checklist at the end covers what to confirm in the code.

**Next action:** close both PRs, or mark them request-changes. Neither fixes the cause, and each hides the symptom from a different place. Ask the API team for the zone ID change (§2) this week, because it is the longest-lead item.

## Verdict

| PR | Verdict | Provider-contract rules it breaks |
| --- | --- | --- |
| 1. Generic retry wrapper on every call, any 4xx/5xx, 10 tries | ❌ Block | Rule 2 (Read must remove the resource on 404), step 4 ("never retry broad error classes"), gate row "idempotent create" |
| 2. Retry helper around flaky test steps | ❌ Block | Acceptance-testing flakiness rule: "never with test-level retries: users run the same code path" |
| Underlying `fennimore_zone` | ❌ Gate FAIL, should not ship as-is | Rule 1: 202 with an empty body means no object ID |
| Underlying `fennimore_origin` | ⚠️ Fixable in the provider | Not-yet-visible class, 5 s replica lag |

## 1. Diagnosis: two separate bugs

Your API has two different consistency problems, and PR 1 treats them as one.

**`fennimore_origin` is "not yet visible" (class 1).**
- Create is synchronous, but the follow-up Read hits a replica about 5 s behind.
- Read returns a 404 or stale values, so the provider reports "inconsistent result after apply".
- A flake rate of about 1 run in 5 fits a race of a few seconds that a nightly hits across several origins.
- I can't confirm which of the two symptoms you see (404 or stale 200). Log the raw Read-after-create response for a few nightlies to find out.
- Stale 200s matter because a retry wrapper never fires on them.

**`fennimore_zone` is async (class 3), and the API gate is FAIL.**
- Create returns 202 with an empty body, then you poll `GET /zones?name=...` for 30-90 s (docs say "up to 2 minutes").
- A 202 isn't an error, so PR 1's wrapper never sees it. The 404s users report come from the provider returning before the zone is usable, so a dependent resource such as an origin gets a 404 or a refusal.
- Without an ID in the 202 body, the provider can't write anything to state before polling. If the poll times out, nothing is tracked. The next apply creates again, giving a duplicate or a 409.
- The skill says plainly that there is no safe recovery without the ID. Polling by name is a workaround, not a compensation. It is safe only if the API enforces name uniqueness per account, and I don't know whether it does.

## 2. Why PR 1 (generic retry wrapper) fails

1. **It retries deterministic errors.**
   - 400, 401, 403, 404, 409 and 422 will never succeed on retry.
   - A typo in a config becomes ten backoffs ending in a vague timeout instead of an immediate plan or apply error.
2. **It breaks Read.**
   - Read must treat 404 as "gone", remove the resource from state, and return no error, so the next plan proposes recreating it.
   - With the wrapper, every drifted or deleted object stalls for the full backoff first.
   - If the wrapper then surfaces an error, users are trapped in a state they can't plan past.
   - `_disappears` tests will slow down or fail.
3. **It retries non-idempotent creates.**
   - A POST that times out or returns 5xx after the server acted is retried and creates a duplicate untracked object.
   - The gate says: synchronous create gets no client retry, or a lookup by a unique name before retrying. Async create has no compensation.
4. **It multiplies load.**
   - Terraform defaults to 10 parallel operations. Ten calls times ten retries is a 429 storm against a rate limit I haven't seen documented.
   - 429 needs `Retry-After` handling and client-side throttling, not blind backoff.
5. **It doesn't cover the real failures.** Stale 200s and the unready zone produce no 4xx/5xx on the call that matters.
6. **It hides the problem.** Retries inside the client make the flake invisible to your nightly metrics, until users see it in production.

**Replace it with:**

- **Typed waiters only in the reads that follow your own writes** (the skill's retry rule is one waiter per write path, never in the plain refresh Read):
  - Create: wait until the object is usable, then Read and set every attribute from the response.
  - Update: wait for the written value to appear.
  - Delete: wait for the 404.
  - Require two consecutive good reads, because the API sits behind replicas.
- **A narrow client retry policy:**
  - 429 with `Retry-After`, plus throttling to the documented quota.
  - Optionally a specific 503, but only on idempotent GET and DELETE, if your API documents it as transient.
  - Match by status code or error type, never by message text.
  - Never retry POST create.
- **Named constants with a justifying comment.** The skill's starting point is about 3× the published propagation time for the retry window, and operation timeouts of about 2× the worst case observed in the sandbox. Tune both from nightly timings.

| Resource | Start with | Basis |
| --- | --- | --- |
| `fennimore_origin` | Waiter window about 15 s, poll every 1 s | 3 × the 5 s replica lag |
| `fennimore_zone` | Create timeout at least 5 min, user-configurable via `timeouts` | Docs say up to 2 min, 3× published, with headroom |

**`fennimore_zone` shipping gate.**
- Ask the API team for the missing fix: return `{id, status}` in the 202 body (or at least a `Location` header). Add a `GET /zones/{id}` status that moves from creating to active, with a terminal error state.
- Ideally, accept an idempotency key (see `samber/developer-platform-skills@api-idempotency-retry`).
- With the ID, the provider writes it to state before polling. A poll timeout then returns the error with the ID in state, Terraform taints the resource, and the next apply replaces it instead of duplicating it.
- If the fix can't land before your cut, move `fennimore_zone` to the next minor, per the cut rule: "never ship it with a known perpetual diff".
- If the zone is already shipped, treat the problem as a known defect with a documented limitation until the API ships the ID. Don't hide it behind retries.

## 3. Why PR 2 (test-level retry helper) fails

- Users run the same code path. A test retry turns "fails one night in five" into green CI, while production users still hit the race.
- It destroys your best signal. The skill says a resource that flakes in CI produces "inconsistent result after apply" in production, and a test that needs a retry usually exposes the race a customer will hit.
- Re-running a whole step that already created objects can leak duplicates and defeat the sweepers.
- It is the same family as `ExpectNonEmptyPlan: true`, which the skill bans as a way to turn CI green. A PR that adds it must link the API bug it works around.

**Revert it.** Fix the cause in the provider (waiters, §2), then track flake rate per resource. That flake rate becomes your pass/fail metric (step 9).

## 4. Gate matrix (current best reading)

| Check | `fennimore_zone` | `fennimore_origin` | Ask / owner |
| --- | --- | --- | --- |
| Stable server-assigned ID | UNKNOWN (name only in the 202) | UNKNOWN (not stated) | API team |
| GET returns every writable non-secret field | UNKNOWN | UNKNOWN | API team |
| In-place update | UNKNOWN | UNKNOWN | API team |
| Idempotent create | UNKNOWN | UNKNOWN (sync: no client retry, or look up by unique name first) | API team |
| Bounded propagation | PASS-ish (30-90 s observed, docs 2 min) | COMP (about 5 s, bounded waiter) | Provider |
| Pollable async op, ID in 202 body | **FAIL** | n/a (synchronous) | API team |
| Deterministic normalization and ordering | UNKNOWN | UNKNOWN | API team |
| Secrets identified | UNKNOWN | UNKNOWN | Provider team |
| Documented rate limits | UNKNOWN | UNKNOWN | API team |

UNKNOWN counts as FAIL until answered. Those answers are what I need next.

## 5. Replacement PRs

1. **Client:** replace the generic wrapper with 429/`Retry-After` handling plus client-side throttling. Remove retries from POST create and from every 4xx.
2. **Origin:** add create, update and delete waiters, with two consecutive good reads and a typed not-found check. Leave plain Read untouched.
3. **Zone, provider side:** a create waiter polling by name, a configurable create timeout, and a status check before returning. Land the state-ID path only once the API returns an ID.
4. **Zone, API side:** the 202 body with ID, plus a status endpoint (§2).
5. **Tests:**
   - Revert the retry helper.
   - Add a fault-injection test using an `httptest` server that returns 404 or stale data for the first N reads after create. It proves the waiter works.
   - Do the mutation check: remove the waiter and the test must fail, which proves the test can fail.
   - Add `_basic` with import verification, `_disappears`, and an update test per mutable attribute.
   - Add the data source `_basic`.
   - Add an `_upgrade` test from the last release.
   - Add a `tofu` lane.
   - Run sweepers before and after each nightly.
6. **Nightly flake tracking per resource,** plus a docs note stating the propagation window you designed for.

## 6. Checks to run against the actual diffs

- Does the wrapper wrap Read as well? (It breaks the not-found rule if so.)
- Does it wrap POST create anywhere? (It can create duplicates.)
- Is `Retry-After` honoured on 429?
- Does the test helper re-run a whole `TestStep`, or only the HTTP call?
- Does either PR add `ExpectNonEmptyPlan: true`, or change `Optional+Computed` handling?
- Are the retry counts and delays unnamed numeric literals? They need named constants with a comment.

## 7. Open questions

1. Is zone name unique and immutable per account, enforced server-side?
2. Can the 202 return the zone ID or a `Location` header? Is there a `GET /zones/{id}` with a status field?
3. Does `GET /zones?name=...` also read from the lagging replica?
4. Does origin create support an idempotency key, or does a unique name exist to look up before retrying?
5. Is the 5 s origin lag a maximum or typical? What is the p99?
6. What are the documented rate limits?
7. What do the failing nightly logs show at the "inconsistent result" step: a 404, or a stale 200?
8. Which minimum Terraform and OpenTofu versions do you support?