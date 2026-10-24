# Review of the two Fennimore provider PRs

**Verdict: request changes on both.** I couldn't see either diff. The PRs aren't reachable from this workspace, which is a different repo, so this review rests on your description. Treat the line-level comments as things to check in the diffs.

Neither PR fixes the cause. Both hide it. The flakes come from two separate consistency bugs, and the provider needs two targeted fixes.

## Root causes

| Symptom | Cause | Right fix |
|---|---|---|
| Users get 404s right after `fennimore_zone` is created | Zone create returns 202 with an empty body and the zone shows up 30–90s later (docs say up to 2 min). The provider returns before the zone exists. | A waiter in `Create` that polls until the zone is visible and active. |
| `Provider produced inconsistent result after apply` on `fennimore_origin`, about 1 run in 5 | Origin create is synchronous, but the provider's immediate Read hits a replica that lags about 5s. Read returns 404 or stale attributes, so the state doesn't match the plan. | Don't depend on that Read. Build state from the create response, or wait for a consistent read. |

A 1-in-5 failure rate fits a race between a roughly 5s lag and an immediate read.

## PR 1: generic retry on any 4xx/5xx, 10 attempts

**Blockers**

1. **It doesn't touch the zone bug.** Create returns 202, which is a success, so the wrapper never triggers. The zone still isn't ready when apply finishes, and users still get 404s.
2. **Retrying 4xx is wrong.**
   - 400, 401, 403, 409 and 422 are deterministic. Retrying them delays every real error by up to 10 backoffs. A bad token in CI would now hang for minutes before failing.
   - Retrying 404 on Read breaks Terraform semantics. A deleted resource should drop out of state immediately, but now refresh, import, data sources and destroy all stall.
3. **Blind retries of non-idempotent calls can create duplicates.** If a `POST` times out or returns 5xx after the server already created the resource, the retry creates a second zone or origin, or hits a 409 that is then retried as well. Retries need an idempotency key, or a lookup by name before re-POSTing.
4. **Retry storms.** Terraform runs with parallelism 10 by default. Retrying 429s and 5xx up to 10 times each multiplies load on an already unhealthy API. Backoff needs jitter, a cap, and `Retry-After` support.
5. **It must respect `ctx` and the resource timeouts.** Check that the sleep is `select { case <-ctx.Done(): ...; case <-timer.C: }`, not `time.Sleep`. Otherwise Ctrl-C and `timeouts {}` blocks stop working.
6. **Retries stack.** Once the waiters below exist, an HTTP-level retry of 10 inside a waiter loop gives 10×N calls and unpredictable total duration.

**Narrow it to:**
- Retry only 429 (honouring `Retry-After`), 502, 503 and 504, plus network errors. Retry 500 only for idempotent methods.
- Make it bounded by total elapsed time, not just attempt count, with jitter.
- Log each retry at debug level and count them. The flake rate should stay visible, not be hidden.

## Fixes the provider needs

**Zone: waiter in Create**

```go
// Create: POST -> 202 (empty body) -> poll by name until visible and active.
// Set the ID only once known. Timeout comes from the resource's `timeouts` block.
stateConf := &retry.StateChangeConf{
    Pending:        []string{"pending", "not_found"},
    Target:         []string{"active"},
    Refresh:        func() (any, string, error) { /* GET /zones?name=<exact> ; 0 results => "not_found" */ },
    Timeout:        d.Timeout(schema.TimeoutCreate), // default 5m, not 2m: docs say "up to 2 minutes"
    Delay:          5 * time.Second,
    MinTimeout:     5 * time.Second,
    NotFoundChecks: 1 << 30, // absence is expected while 202 is in flight
}
```

- **Match the name exactly** and handle pagination or multiple matches.
- **Wait for an active status**, not just existence. Check that the API exposes one.
- **Add a delete waiter** that polls until the zone is gone.
- **Orphan zones:** if the poll times out, the zone may appear later with no state entry. Return an error that says so. Better, fix the API (below).

**Origin: remove the replica dependency**

- Populate state from the create response and skip the re-read.
- If you must re-read, retry the read for a bounded window (about 30s) until the resource exists and key fields match what was written. Do this only inside the create and update flow.
- On a normal refresh, a 404 still means "removed, drop from state".
- Check whether the API has a read-your-writes option, such as a primary-read flag, a version or ETag, or a consistency token. If not, ask for one.
- Also confirm the error text. "Root object was present, but now absent" points to replica lag. A specific attribute differing could instead be normalization (defaults, case, trailing slash), which is a different bug.

**API changes to request** (these would remove most of the polling):
- Return `{id, status: "pending"}` and a `Location` header on the 202.
- Expose `GET /zones/{id}` with a status field.

## PR 2: retry helper around flaky test steps

**Blocker.** This hides the bug in the tests that exist to catch it. Users don't get a retry helper, so green CI would no longer mean the provider works. A nightly failing 1 run in 5 is a correct signal of a real defect.

**Replace it with deterministic tests:**
1. **Fake server for zones.** It returns 202 and makes the zone visible only after N polls. Assert that `Create` returns only once the zone is active, and that it times out with a clear error if it never appears.
2. **Fake server for origins.** It returns 404 or stale data for the first K reads after create. Assert no inconsistent-result error.
3. **Retry policy tests.**
   - 400, 401, 403, 409 and 422 produce exactly 1 call.
   - 429 honours `Retry-After`.
   - 503 on a `POST` does not produce a duplicate create.
   - A cancelled `ctx` stops retrying immediately.
4. **Mutation check.** Remove the waiter and confirm the tests fail. Run with `-race -count=20` to show they're deterministic.
5. **Keep the acceptance tests unwrapped.** If you keep any retry in test setup, limit it to infrastructure steps with a narrow predicate, and comment why.

## Merge checklist

- [ ] Zone waiter, with `timeouts` defaulting to at least 5m
- [ ] Origin create no longer depends on a lagging read
- [ ] Retry layer limited to 429/502/503/504 and network errors, with jitter, a total-time cap, and `ctx` respected
- [ ] No blind retry of non-idempotent `POST`s
- [ ] Test retry helper removed from the flaky steps
- [ ] Fake-server tests for async create and replica lag, with a mutation check
- [ ] Acceptance tests pass unwrapped for about 2 weeks of nightlies
- [ ] API ticket filed for the 202 body and `Location` header, status field and read-your-writes

**If you send me the PR links or diffs**, I'll do a line-level pass. The first things I'd check are the retry predicate, the `ctx` handling and the POST idempotency.