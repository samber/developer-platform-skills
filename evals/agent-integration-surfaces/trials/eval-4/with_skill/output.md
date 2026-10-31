# Ferrocore `/v1/instant`: agent integration plan and design review

**Verdict:** keep the idea (provision-then-claim). Change three things before building. The link is a login session in a URL, stores never expire, and the endpoint has no abuse controls.

## Defaults I assumed

I couldn't ask the interview questions, so these defaults stand until you overturn them:

- Agent classes: coding agents with a shell, plus chat assistants that call HTTP.
- No hard date.
- This is a standing agent channel.
- Effort ceiling is one engineer for a quarter.
- Ferrocore has a self-serve free tier, so the claim flow is not deleted.
- Ferrocore stores data, so the store contents are the user's data.

I haven't run the reachability gate. I have no access to your edge, so every gate result below is **unverified**, not a pass.

## 1. Review of the proposed design

| # | Problem | Why it matters | Fix |
| --- | --- | --- | --- |
| 1 | The magic link carries `session=<session_token>` and logs the human in | The URL is a session secret, and URLs leak into logs, history, referrers, analytics and the agent transcript. Anyone holding the link becomes the user. | Replace it with a **claim link**: single-use, expiring, and never a session. The human must log in or sign up before it does anything. |
| 2 | Stores live forever | Unauthenticated creation with unlimited lifetime is free permanent storage for abusers, and you can't tell a real project from an abandoned one. | Unclaimed stores expire (start at 72 hours) and run under small quotas. |
| 3 | No abuse controls on an unauthenticated POST | It is a free resource factory. | Per-IP and per-signature creation caps, no outbound network or email from unclaimed stores, and a kill switch. |
| 4 | The design doesn't say what the agent gets | The agent needs connection details to use the store before any human arrives. | Return a store-scoped credential, never a human or account key. |
| 5 | No claim state machine | Pre-claim credentials stay live after a human takes over. | Use states `unclaimed → claiming → claimed`. Claiming revokes pre-claim tokens and rotates credentials. |
| 6 | Human-only actions return a generic 403 | The agent can't tell "blocked until a human claims" from "broken". | Return a named error, `capability_requires_claim`, with the claim URL in the body. |
| 7 | Terms of Service and data handling are unspecified | A store created with no account has no accepted Terms. | Accept Terms at claim. Unclaimed stores hold no personal data. |
| 8 | The POST isn't safe for blind retries | Agents retry without thinking, so a retry makes a second store. | Accept an `Idempotency-Key` and return the same store for the same key. |

## 2. Agent class x surface matrix (relevant cells)

| Surface | Training crawler | AI search | User-triggered fetcher | Browser agent | Coding agent / fleet |
| --- | --- | --- | --- | --- | --- |
| Signup page | deny | deny | allow (read) | allow verified agents; no CAPTCHA-only step | **not the path.** Use `/v1/instant`. |
| `/v1/instant` | deny (edge rule) | deny (edge rule) | deny | allow | **allow**, rate-capped |
| Claim page | deny | deny | deny | allow, after human login | n/a (human step) |
| Store API | n/a | n/a | credential required | credential required | store-scoped credential |

Enforce the `deny` cells at the CDN or WAF. robots.txt alone is not enforcement, because user-triggered fetchers may ignore it.

## 3. Reachability gate (do this first, then rung A)

This gate is not a rung, and every later step scores zero if it fails.

| Class | Surface | Status | Check |
| --- | --- | --- | --- |
| Coding agent (curl, SDK, CLI) | `POST /v1/instant` | **unverified** | Does a "block AI bots" preset or bot-fight rule challenge or 403 it? Does a CAPTCHA or JS challenge sit in front of `/v1/*`? |
| Chat assistant with HTTP | `POST /v1/instant` | **unverified** | Same checks. |
| Browser agent | claim page and login | **unverified** | Open the claim URL in a headless browser and record any challenge. |

A spoofed user-agent from a laptop tests only your user-agent rules. It tells you nothing about IP-verified or signature-verified rules. Mark those cells unverified until you've counted 200s from verified traffic in the edge logs over a week.

## 4. Revised API

### Create

```
POST /v1/instant
Idempotency-Key: <client-generated uuid>
Content-Type: application/json

{ "name": "optional-label" }
```

Response `201`:

```json
{
  "store_id": "st_...",
  "state": "unclaimed",
  "connection": { "url": "...", "credential": "<store-scoped, secret shown once>" },
  "limits": { "max_bytes": 26214400, "max_ops_per_sec": 50 },
  "expires_at": "2026-11-02T14:00:00Z",
  "claim_url": "https://app.ferrocore.dev/claim?code=<one_time_code>"
}
```

- Keep the credential out of logs and never put it in a URL.
- The limit numbers are placeholders. Set them so that abuse isn't profitable.
- Name the field `code`, not `session`. The claim code is not a session token and must never be accepted as one.
- A repeated `Idempotency-Key` returns the same store and the same `claim_url`. Don't mint a second code.

### Claim

1. The human opens `claim_url`. The page shows no data and no session. It shows the store label, creation time and expiry, and a "Log in or sign up to claim" button.
2. The page sets `Referrer-Policy: no-referrer` and strips analytics. The server exchanges the code on the POST after login, then redirects to a clean URL.
3. After login, the claim moves the store `unclaimed → claiming → claimed` in one transaction:
   - **revoke** the pre-claim store credential,
   - **issue** a new credential to the account,
   - **attach** the store to the account's normal billing and free-tier quota,
   - **invalidate** the claim code.
4. Terms are accepted on this screen. Without acceptance, the state stays `unclaimed`.
5. A claim code works once. It also expires with the store and can't be replayed after expiry.

### Errors

Errors carry a stable `code`, the failing field and a next step:

| Code | When |
| --- | --- |
| `capability_requires_claim` | The agent tried an action reserved for claimed stores (raising quota, outbound webhooks, adding members). The body includes `claim_url`. |
| `store_expired` | The unclaimed store passed `expires_at`. |
| `rate_limited` | 429 with `Retry-After`. |
| `quota_exceeded` | A limit was hit while unclaimed. |
| `claim_code_invalid` | The code was used, expired or revoked. |

### Expiry and cleanup

- Start at 72 hours. A claimed store never expires.
- Warn the agent in API responses as expiry approaches: `X-Store-Expires-At` on every response, which the agent can surface to the human.
- Delete expired stores' data, not just access. Say so in the docs.
- Optional: let a claimed account request a one-time extension of an unclaimed store, but not by the agent alone.

## 5. Identity and delegation model

| Field | Coding agent / chat HTTP agent |
| --- | --- |
| Identified by | the store-scoped credential. User-agent and env-var tag are telemetry only. |
| Authority | its own, autonomous, over this one store |
| Credential | store-scoped secret, issued at creation |
| Scope | read and write keys in that store. No account-level scope. |
| Lifetime | until `expires_at` while unclaimed. Revoked at claim. |
| Sponsor | none before claim, so the unclaimed window is bounded by expiry and quota. The claiming human becomes the sponsor. |
| Revocation | automatic at claim or expiry. A kill switch revokes any store or the whole endpoint. |
| Approval gate | anything irreversible, billing-bearing or account-level requires claim |

- The agent never holds a human's long-lived key or session. The old design handed the human a session. The new one gives the agent only a disposable store credential.
- Web Bot Auth identifies the operator but grants no user authority. If you accept signed agents, use it as a creation-cap key and a trust signal, never as an authorization.

## 6. Abuse controls (ship in the same pass)

- Per-IP and per-signature creation caps, plus a global rate on `/v1/instant`.
- No outbound network, webhooks or email from unclaimed stores.
- Small storage and operations quota, and a short TTL.
- No personal data allowed in unclaimed stores. Enforce it in the docs and Terms, and scan for obvious violations.
- A kill switch: disable creation, or revoke all unclaimed stores in a cohort.
- Tripwires: alert when creation volume from one ASN or signature spikes, or when many unclaimed stores expire unclaimed (a sign of scripted abuse).
- No CAPTCHA on `/v1/instant`. It blocks legitimate agents and doesn't stop determined bots.

## 7. Agent-safe API checklist

| Item | Status |
| --- | --- |
| Machine-readable errors | needs the table above (`api-error-design`) |
| Idempotency key on mutating calls | needed on `POST /v1/instant` (`api-idempotency-retry`) |
| Published limits, per-credential, `Retry-After` on 429 | needed, and unclaimed limits must be separate from account limits (`api-rate-limit-policy`) |
| User-generated fields marked untrusted | any stored value returned to an agent is untrusted content, so say so in the docs |
| Spend cap and out-of-band confirmation | n/a: unclaimed stores can't spend money |
| Sandbox or test mode | an unclaimed store is effectively a sandbox |
| Destructive operations need dry-run or confirm | store deletion needs a confirm token (`cli-interface-design`) |

## 8. Execution path

- Coding agents with a shell: an Agent Skill that drives a `ferrocore` CLI with `--json`, for example `ferrocore instant --json`. The skill says when to use it, what to check, and how to hand the human the claim link. The CLI executes.
- JSON only on stdout, with banners and warnings on stderr, and no prompts off a TTY.
- "Next step" hints go in as data fields (identifiers), never as shell strings. The agent must not run them verbatim.
- Chat assistants without a shell call the HTTP endpoint directly. Build an MCP server only on evidence of shell-less clients that need per-user remote auth. A stakeholder request is not that evidence.

## 9. Measurement (build this before shipping)

- Tag every request with an agent class (crawler, search, fetcher, browser, coding, fleet, human, `unknown`). `unknown` is a value, not a null.
- Append the detected agent to the CLI and SDK user-agent, and log it server-side as its own field.
- Funnel: `/v1/instant` calls by class → stores created → claim page views → claimed → activated → paid. The claim rate (created to claimed) is the central number.
- Report agent share with its method and floor caveat, for example "at least N%, from env-var detection". Env-var detection undercounts.
- Never mix crawler hits and agent API calls into one number.
- Neon's 80% and Supabase's 60–70% are company claims about database creations, not targets for Ferrocore.

## 10. Discovery

- Claim the Context7 entry and publish docs markdown (owner: `coding-agent-docs-optimization`).
- Add `/.well-known/api-catalog` (RFC 9727) only as a background task if you have an OpenAPI spec. An agent card isn't needed, because Ferrocore doesn't expose an agent.
- Document `/v1/instant` prominently: a short docs page, in the CLI help, and in the Skill.

## 11. Ranked rungs

| Order | Rung | Why | Owner / delegated skill |
| --- | --- | --- | --- |
| 0 | Reachability gate | Every later step scores zero if the edge blocks `/v1/instant`. | Platform/security, with the CDN owner |
| 1 | A. Measurement tags | Baseline before anything ships. | Platform eng |
| 2 | B. Docs markdown and Context7 claim | Cheap, and coding agents read current docs. | `coding-agent-docs-optimization` |
| 3 | F. Provision-then-claim (this design) | Self-serve free tier is the funnel, and a standing agent channel promotes F. Highest effort, so build it after 0–2 prove agents arrive. | You, with `api-auth-key-management` for the store credential |
| 4 | C. Agent credentials and delegation | The store credential is a minimal C. Full delegated tokens for claimed accounts follow (`oauth2-provider-design`). | `api-auth-key-management` |
| 5 | D. Skill plus `--json` CLI | The shell-agent execution path. | `cli-interface-design`, `agent-skill-offering` |

**Deleted:** E (MCP) until evidence of shell-less clients appears, and G (discovery files) as a milestone.

**Note on the order:** the skill's default puts F behind A, B and C, because it rebuilds signup, billing and abuse controls. You asked for F directly. Keep it, but run A and the gate first so you can tell whether it worked. If logs show agents already creating a share of new accounts, move F to rung 1.

## 12. Exit criteria

- Zero "allow" cells fail the gate. Each passes for a verified agent of that class, or is listed unverifiable with the reason.
- The "deny" cells are enforced at the edge.
- Every agent credential names scope, lifetime, sponsor and per-agent revocation.
- No agent holds a human's long-lived key.
- Every agent-facing surface emits an agent-class field, with a baseline before the first rung ships.
- An unclaimed store cannot outlive `expires_at`, and a claim code cannot be replayed.

## Open questions

1. What do the quotas and the 72-hour window cost you in abuse risk versus agent usefulness? Both numbers are placeholders.
2. Does the claim page need to show a data preview, or is label and expiry enough? A preview raises the damage if a claim link leaks.
3. Do you accept the risk that whoever opens the claim link first takes the store? The mitigations are a short expiry, a visible creation time and IP region, and small quotas. A stronger option is to bind the claim to the creating IP or a code the agent shows the human, at the cost of friction.