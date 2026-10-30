# Oakhurst Signals: SDKs, sandbox, quickstart, examples, hackathon

**Next action:** run the examples census script in section 4. It takes 5 minutes and sets the hackathon scope.

**Limits of this answer:**
- I can't see your API, SDK package names, or repos.
- Every endpoint, key format, and package name below is a **placeholder I invented**. Check each one against the real API.
- Nothing here has been cold-run. Treat the quickstart as an unverified draft until you run it.

## 0. Short answers

| Question | Answer |
|---|---|
| Which SDK languages next? | **Go**, then **Ruby**, then **Java/Kotlin**. Mobile only when users ask. Build none before the hackathon unless the hackathon stack demands one. |
| Sandbox? | Build "test-mode projects" first (about 2 days), then anonymous temporary sandboxes (about 4 days). |
| Quickstart? | Written in section 3. It uses curl, needs no signup, and has one success moment. |
| Examples? | Run a census, then archive or merge down to one `examples` monorepo plus one starter-template repo. Don't fully migrate before the hackathon. |
| One demo app instead of all this? | **Build the demo app, but not instead of the sandbox and quickstart.** The app depends on both, and hackers hit both in their first 20 minutes. Skip the SDK work and the examples migration until after the hackathon. |

## 1. SDK languages

**Recommended order: Go, Ruby, Java/Kotlin.**

This is a default from market shape, not from your data. A product analytics API gets most of its non-browser traffic from server-side event ingestion. After Node and Python, that traffic comes from Go, Ruby/Rails, PHP, and the JVM.

Check the default against your data first. This takes 1 hour:
1. Count signup-survey answers and support or Discord requests that name a language.
2. Count GitHub issues asking for an SDK.
3. If one language beats Go by about 2x, switch to it.

**Rules for a solo owner:**
- **Cap supported SDKs at 3 hand-written ones.** Each is a standing maintenance job: releases, dependency bumps, and every API change.
- **Hand-write thin ingestion clients.** Analytics SDKs need batching, flush on exit, retry with backoff, and idempotent event IDs. OpenAPI generators don't give you those.
- **Write one language-neutral conformance suite first.** It should cover batching, retry on 429/5xx, flush on shutdown, and the shape of the error. Run it against every SDK. The second and third SDKs then cost about 2 to 3 days each.
- **Generate clients for the long tail** (PHP, C#, and the rest) from your OpenAPI spec, and label them "generated, community-supported". Document the raw HTTP API as the official path for everything else.
- **Mobile (Swift, Kotlin, React Native) is a different job.** It needs offline queues, app lifecycle handling, and privacy prompts. Don't take it on solo before there is real demand.

**Tiers to publish:**

| Tier | Languages | Promise |
|---|---|---|
| 1 | JS, Python | Tested in CI against the sandbox; fixes within a week |
| 2 | Go (then Ruby) | Same CI gate; best-effort fixes |
| 3 | Generated clients | Compile-only, no support SLA |

**Time:** the Go SDK plus the conformance suite is about 4 days. Schedule it after the hackathon (section 6).

## 2. Sandbox design

**Goal:** a stranger gets a working key and visible data in under 60 seconds, with no signup and no way to touch production data.

### Options, ranked by minutes saved per week of engineering

| Option | What | Effort | Verdict |
|---|---|---|---|
| A. Test-mode project | Existing signup creates a project flagged `sandbox`. It uses separate keys, a short retention, and hard quotas. | About 2 days if you have multi-tenancy | **Build first** |
| B. Anonymous temporary sandbox | `POST /v1/sandboxes` with no auth returns keys that expire. | About 4 more days | **Build second**, before the hackathon if possible |
| C. Separate full environment | A parallel stack. | Weeks, plus ongoing cost | Reject |

The baseline numbers below (quotas, TTLs) are my defaults, not benchmarks. Tune them to your cost per event.

### Design

1. **Separate base URL.** Use `https://sandbox.<your-api-host>`, same paths and same validation as production. A sandbox key sent to the production host returns `401` with a message that says so. A separate host stops quickstart traffic from polluting production metrics.
2. **Key prefixes.** Use distinct prefixes for sandbox keys, e.g. `sbx_w_…` for write and `sbx_r_…` for read. Scanners and humans can then tell them apart at a glance.
3. **Creation (option B).** `POST /v1/sandboxes` returns `sandbox_id`, `write_key`, `read_key`, `expires_at`.
   - Rate limit: 5 sandboxes per hour per IP.
   - TTL: 7 days. The hackathon variant can use a 14-day TTL via a code.
4. **Seed data.** Each sandbox starts with a fictional app: 30 days, about 200 users, about 5,000 events (`signup_completed`, `checkout_started`, `checkout_completed`). Queries return something on the first call, so the reader never sees an empty chart.
5. **Quotas.**
   - 10,000 events total.
   - 50 events per second.
   - Reject over-quota writes with `429` and an error that names the limit and the reset path.
6. **Read-after-write consistency.** Make sandbox ingestion synchronous so a query right after a write sees the event. If production is eventually consistent, document the difference in one line on the quickstart page. A quickstart that shows `count: 0` kills trust.
7. **Reset.** `POST /v1/sandboxes/{id}/reset` restores the seed state. Also add `DELETE` for cleanup.
8. **Failure injection.** Header `X-Sandbox-Simulate: rate_limit | server_error | slow`. SDK authors and hackers can then test retry code without waiting for a real outage.
9. **Abuse controls.**
   - No outbound webhooks, or an allowlist only.
   - Reject payloads over 32 KB.
   - Show a banner in the response headers, `X-Sandbox: true`.
   - Add a "no personal data" line to the terms.
10. **Conversion path.** Every sandbox response includes a `claim_url`. Claiming turns the sandbox into a real account with the same project, so the quickstart connects to the funnel.
11. **CI use.** All SDK tests and example repos run against fresh sandboxes. The sandbox is also your docs test environment.

**Open question for engineering:** can your ingestion path run synchronously for flagged projects? If not, option A slips to about 4 days.

## 3. Quickstart page

**Commitments:**
- Success moment: you send an event and read it back from the query API.
- Time budget: 5 minutes.
- Pass gate: a cold run on a clean machine passes all five checks before it ships (see the verification plan below).

Everything between the lines is the page. Replace the hosts and field names with the real ones.

---

# Send your first event

Send one event to the Oakhurst Signals sandbox, then read it back. About 5 minutes. No account needed.

**Prerequisites**

- `curl` 7.68 or later. Check with:

```bash
curl --version
```

## 1. Create a sandbox

Request a temporary sandbox with its own keys.

```bash
curl -s -X POST https://sandbox.example.com/v1/sandboxes
```

You should see:

```json
{
  "sandbox_id": "sbx_01…",
  "write_key": "sbx_w_…",
  "read_key": "sbx_r_…",
  "expires_at": "2026-12-07T10:00:00Z"
}
```

Save the two keys in your shell:

```bash
export SIGNALS_WRITE_KEY=<WRITE_KEY_FROM_OUTPUT>
export SIGNALS_READ_KEY=<READ_KEY_FROM_OUTPUT>
```

If you get `429`, you hit the limit of 5 sandboxes per hour. Wait, or reuse an earlier sandbox.

## 2. Send an event

Record one event named `quickstart_hello` for a user called `user_1`.

```bash
curl -s -X POST https://sandbox.example.com/v1/events \
  -H "Authorization: Bearer $SIGNALS_WRITE_KEY" \
  -H "Content-Type: application/json" \
  -d '{"event": "quickstart_hello", "user_id": "user_1", "properties": {"plan": "free"}}'
```

You should see:

```json
{"accepted": 1}
```

If you get `401`, the key is wrong or unset. Run `echo $SIGNALS_WRITE_KEY` and check that it starts with `sbx_w_`.

## 3. Read the event back

Count `quickstart_hello` events in the last hour.

```bash
curl -s "https://sandbox.example.com/v1/query?event=quickstart_hello&metric=count&since=1h" \
  -H "Authorization: Bearer $SIGNALS_READ_KEY"
```

You should see:

```json
{"event": "quickstart_hello", "metric": "count", "value": 1}
```

If `value` is `0`, you used the write key here. Use `$SIGNALS_READ_KEY`.

## You're done

You sent an event and read it back. The sandbox also holds 30 days of sample data. Try it:

```bash
curl -s "https://sandbox.example.com/v1/query?event=checkout_completed&metric=count&since=30d" \
  -H "Authorization: Bearer $SIGNALS_READ_KEY"
```

**Next**

- Install an SDK: [JavaScript](#) · [Python](#)
- Browse the [API reference](#)
- Ask for help in [Discord](#)

---

### Verification plan (not yet run)

1. Fresh machine or container, no stored keys, no existing sandbox.
2. Paste each block verbatim, with no edits.
3. Compare each output to the documented one.
4. Time page-load to success. It must be 5 minutes or less. If it is longer, shrink the success moment instead of raising the budget.
5. Have someone who has never seen the product do it.

### Instrumentation

- Fire an event per step (`qs_step_1`, `qs_step_2`, `qs_step_3`) and a `qs_success` event. You are an analytics company, so use your own product.
- Primary metrics: step drop-off and median time to success.
- Set the target after 4 weeks of baseline.
- Run these commands in CI against the live sandbox on every release.

## 4. Examples cleanup

**Step 1: census (5 minutes, read-only).** Fill in your two org names.

```bash
mkdir -p /tmp/examples-census
for org in <NEW_ORG> <OLD_ORG>; do
  gh repo list "$org" --limit 200 \
    --json name,pushedAt,isArchived,stargazerCount,primaryLanguage,description \
    > "/tmp/examples-census/$org.json"
done
```

Then list the repos by last push date:

```bash
jq -r '.[] | [.name, .pushedAt, .stargazerCount, (.primaryLanguage.name // "-"), .isArchived] | @tsv' \
  /tmp/examples-census/*.json | sort -k2
```

**Step 2: triage each repo with these rules.**

| Test | Action |
|---|---|
| Last push over 12 months ago and it uses a removed API | **Archive** |
| Duplicates another example | **Merge** the better one, archive the other |
| Works, is under about 150 lines, and is not a template | **Fold** into the monorepo |
| Is a starter people fork | Keep as a **standalone template repo** |
| Doesn't run against the sandbox | **Fix** if cheap, otherwise archive |

**Step 3: target end state.**

- One public `examples` monorepo, 6 examples at most:
  1. `quickstart-js`
  2. `quickstart-python`
  3. web tracking (Next.js)
  4. server events (Express or FastAPI)
  5. a funnel dashboard
  6. the sandbox seed script
- One `signals-starter` template repo for the hackathon (section 5).
- A `README` table in the monorepo listing each example, its language, its tier, and its owner.
- Every old repo gets a final commit pointing to the new home before archiving.

**Step 4: enforce.**
- Add a CI job that compiles every example against the latest published SDK.
- Run the quickstart path (Run tier) on every release.
- Mark every sample as Run, Compile-only, or Illustrative.
- Once a week, re-run the job and open an issue if it fails.

**Side-effect commands.** Run these only after the user-facing pointer commit exists.

```bash
# **archives** the repo (reversible in settings, but it blocks pushes and issues)
gh repo archive <OLD_ORG>/<repo> --yes
# **transfers** the repo (GitHub keeps redirects from the old URL)
gh api repos/<OLD_ORG>/<repo>/transfer -f new_owner=<NEW_ORG>
```

Prefer **archive** to delete. Deleting breaks links and loses stars.

**Time:** census and triage about 2 hours, CI harness about 1 day, migration about 2 days.

**Before the hackathon:** do the census and triage, and archive the clear duplicates. Leave the full migration for after.

## 5. Hackathon: one demo app?

**Yes, build the one demo app, with three jobs.** Don't treat it as an alternative to the sandbox and quickstart.

1. **Starter template.** Hackers fork it in the first 10 minutes. This is the `signals-starter` repo.
2. **Live-demo showcase.** Use it in the kickoff talk.
3. **Quickstart "next step".** It's what you point readers at after the curl success.

**Why not only the demo app:**
- Hackers can't use it without a key, and a signup wall costs the first 20 minutes. That makes the sandbox critical path.
- Hackers' first contact is the quickstart. If it fails, they never reach your app.
- The app depends on the sandbox for seed data and keys.

**The app (suggested).** A small storefront with the checkout funnel already instrumented, plus a dashboard page that reads the query API. Hackers swap the storefront for their own idea and keep the dashboard. Keep the repo short: under 300 lines of app code, one `README`, one `.env.example`.

**Live demo plan.**
- Primary: a recorded screencast embedded in the slides, narrated live.
- Fallback: the same app running locally against the sandbox.
- Prepare a reset command and a front-row colleague with a copy.

**Assumptions to confirm** (you didn't say):
- Are you hosting, sponsoring, or just attending?
- What stack do participants use?
- Can you get the registration form language counts?

If participants are mostly Go or Ruby, move that SDK up. Otherwise it waits.

### 5-week plan (today is 2026-10-30)

I assumed about 25 DX hours per week. Scale it down if you have less.

| Week | Do | Done when |
|---|---|---|
| 1 (Oct 30 to Nov 5) | Examples census and triage. Sandbox option A. Quickstart draft. | Test-mode keys work, and a census table exists |
| 2 (Nov 6 to 12) | Seed data, reset, quotas. Cold-run the quickstart and fix it. Publish with step events. | A stranger completes the quickstart in 5 minutes or less |
| 3 (Nov 13 to 19) | Sandbox option B (anonymous creation). Build the starter app. | `POST /v1/sandboxes` works, and the starter runs from a fresh clone |
| 4 (Nov 20 to 26) | Polish the app. Hackathon kit: quota code, README, office-hours schedule. Record the demo. | A teammate completes the starter cold |
| 5 (Nov 27 to Dec 3) | Freeze. Load-test the sandbox. Rehearse the demo three times. Plan support coverage. | No changes except fixes. A load test passes at the expected hacker count |

**After the hackathon:** Go SDK plus the conformance suite (4 days), then the examples migration (3 days), then Ruby.

### Risks

- **Solo.** Support during the hackathon is the real single point of failure. Arrange a backup engineer on call and a Discord channel.
- **Sandbox cost spike.** Cap quotas and set a daily budget alert.
- **Scope creep.** Anything outside this table waits until after the hackathon.

## 6. What I need from you

1. Do you own the backend, or does another team own it? It decides whether the sandbox is 2 days or 2 weeks.
2. Your role in the hackathon, and the participants' stack.
3. The real API shape, so I can replace the placeholders. Paste the OpenAPI spec path or three example requests.

**Next action:** run the census script from section 4.