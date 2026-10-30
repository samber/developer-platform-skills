# Does "modal + UA whitelist" make Tallowfield agent-safe?

**No, on both counts.** The modal does not control agent actions, and the WAF rule opens a hole in front of payroll. Below is what to do instead, as an agent integration plan. I used the `agent-integration-surfaces` skill and did not ask the interview questions. Defaults are printed at the end so you can overturn them.

## Why neither change works

### 1. Confirmation modal before "Submit payroll"

- **The agent can click it.** A browser agent driving the session sees the modal and clicks "Confirm". The approval has to travel outside the agent's channel: push, email or a second device. A confirm button in the session the agent drives does not count.
- **It is invisible to the real risk.** Local agents run in the user's own Chrome with the same IP and user-agent as the human. Nothing separates them at your edge or in your UI, so the modal cannot even tell which sessions to apply friction to.
- **It is still worth keeping as a human speed bump.** But it is not the control.

### 2. Allowlisting `User-Agent` containing "ChatGPT" or "Claude"

- **A user-agent is a claim, not an identity.** Anyone can send `User-Agent: Claude`. You would be adding "skip the bot challenge" for every credential-stuffing script against a payroll login.
- **It matches the wrong things.** `ClaudeBot` is the training crawler. `Claude-User` and `Claude-SearchBot` are different classes with different robots.txt behavior. A substring match lumps them all together.
- **It does not reach your customers' agents.** Agents running in a customer's own Chrome send the browser's normal user-agent, so the rule never fires for them. Agents running in the vendor's cloud may carry the string, but then the spoofing problem applies.
- **It confuses identity with delegation.** Even a verified ChatGPT agent proves only which operator sent the request. It says nothing about which user authorized what.

## The plan

### 1. Agent class × surface matrix

| Surface | Training | AI search | User-triggered fetch | Hosted browser agent | Local browser agent | Customer agent fleet / coding agent |
| --- | --- | --- | --- | --- | --- | --- |
| Marketing site, docs | business call | allow | allow | allow | same as human | allow |
| Signup, login | deny | deny | read only | allow if verified (signature or vendor IP list), no CAPTCHA-only step | same as human; no edge lever | API or claim path |
| Authenticated app (dashboard) | deny | deny | n/a | verified agent inside a user session; submit gated out of band | same as human; no edge lever | use the API |
| API | n/a | n/a | credential | credential | credential | agent credential |

Local browser agents cannot be targeted at the edge. Your levers for them are a UI they can drive (labelled fields, no CAPTCHA-only step), an API for the same jobs, and the server-side approval gate below.

### 2. Reachability gate (run before anything else)

- Request login and dashboard as each class you mean to admit. Record status codes, WAF rule hits and challenges.
- Check any "AI bots" preset in the WAF or CDN. If one is on, it may already be blocking hosted agents you want.
- Classes you can't impersonate (signed agents, vendor IP ranges): count 200s from verified traffic in edge logs over a week.
- A spoofed-UA request from a laptop tests only your UA rules. It proves nothing about signature or IP rules.
- Replace the UA rule with an allow rule on a **verified** identity: your CDN's verified-bot or signed-agent category (Web Bot Auth, RFC 9421 based), or vendor IP lists. Web Bot Auth is still an IETF draft, so expect changes.
- Everything else keeps the challenge. Any deny must be enforced at the edge, not in robots.txt alone.

### 3. Identity and delegation (payroll makes this the top rung)

Payroll moves money, so credentials and approvals come first.

| Field | Value |
| --- | --- |
| Identified by | Agent-labelled credential issued by you, not a UA |
| Authority | Delegated: the user grants it, with an `act` chain in logs ("agent X for user Y") |
| Credential | Per-agent key or delegated token. Device grant (RFC 8628) for CLIs and headless agents. Never the human's key or session |
| Scope | Workflow only, for example `payroll:read`, `payroll:draft`. **No `payroll:submit` scope by default** |
| Lifetime | Hours or days, never "until revoked", and never longer than the user token it derives from |
| Sponsor | A named human per credential |
| Revocation | Per agent, from the customer's settings, without logging the human out |
| Approval gate | "Submit payroll" returns `pending_approval`. A named human approves it out of band (push, email or second device) |

- **The approval gate is the real replacement for the modal.** The agent prepares a run, and the API refuses to execute it until an authorized human approves in another channel. This works for local agents too, because it is enforced server-side.
- Make approval cover the amount and recipients, not just "submit". Add a per-credential spend cap.
- **Local browser agents** are the exception: they reuse the human's session. Bound it with a short absolute session lifetime and refresh rotation. The `pending_approval` gate protects submit even there. Per-agent revocation is impossible on that path, so list it as a known exception.
- Hand token formats and rotation to `api-auth-key-management`, and grants and consent to `oauth2-provider-design`.

### 4. Execution path per class

- **Customers' agent fleets and "run payroll via API" workflows:** the API plus SDKs with agent credentials. This is the preferred path and it gives agents far fewer ways to go wrong than driving the UI.
- **Browser agents:** keep the UI drivable (labelled fields, no CAPTCHA-only steps), but route the money step through the approval gate.
- **Coding agents with a shell:** a skill plus `--json` CLI only if you already have a CLI. Otherwise delete this rung.
- **MCP server:** only if you have evidence of shell-less chat clients or per-user remote access. A stakeholder asking for it is not that evidence.

### 5. Signup path

Payroll is likely sales-led or has heavy onboarding, so provision-then-claim is deleted by default. If self-serve signup exists and agents are creating accounts, revisit: money-moving products must run unclaimed resources in sandbox mode only, with ToS accepted at claim.

### 6. Agent-safe API checklist

Each item below needs an owner:

- Stable machine error codes with the failing field and a next step (`api-error-design`).
- Idempotency keys on every mutating call, so a retrying agent cannot double-submit payroll (`api-idempotency-retry`). This one is critical here.
- Per-agent-credential rate limits with `Retry-After` (`api-rate-limit-policy`).
- Employee-supplied fields such as names and notes are marked as untrusted content in responses. They are a prompt-injection path into any agent reading them.
- A sandbox or test mode so agents can run end to end with no real payments (`api-test-mode-design`).
- Dry-run or confirm token on destructive operations, never a prompt.
- Per-credential spend cap with out-of-band confirmation, as in section 3.

### 7. Measurement (baseline first)

- Add an agent-class field to every request record: crawler, search, fetcher, browser, coding, fleet, human, `unknown`. `unknown` is a value, not a null.
- Log credential type and the `act` chain on API calls.
- Report agent share with its method and floor caveat ("at least N%, from verified signatures and agent credentials"). Local browser agents are undetectable and will undercount.
- Never sum crawler hits and agent API calls into one number.
- Track failure points: blocked at the edge, stalled at approval, failed auth, error codes by class.

### 8. Ranked rungs

Gate fixes come first and are not a rung. Until the "allow" cells pass, everything below scores zero.

| Order | Rung | Why |
| --- | --- | --- |
| 0 | **Gate fixes:** remove the UA allowlist, add a verified-identity allow rule, check presets | Safety and reachability |
| 1 | **A. Measurement tags** | Cheap, and every later rung needs the baseline |
| 2 | **C. Agent credentials, delegation and the out-of-band approval gate** | Money-moving operations promote this above everything |
| 3 | **B. Docs markdown and Context7 claim** | Cheap and delegated to the docs skill |
| 4 | **D. Skill plus `--json` CLI** | Only if a CLI exists |
| Deleted | E. MCP, F. Claim flow, G. Discovery files | No evidence of shell-less clients, no self-serve path, almost no readers yet |

E returns as a later rung if you find evidence of chat clients or customer agent fleets that need it. G (`api-catalog`) can be a background task once you have an OpenAPI spec.

## What to tell product

- Keep the modal as UX. Stop calling it a safety control.
- Don't ship the UA allowlist. Replace it with the verified-identity rule.
- Build the server-side approval gate and agent credentials. That is the actual "agent-safe" feature.

## Defaults I assumed (overturn any of these)

- Agent classes in play: hosted browser agents and local browser extensions today, API-calling customer fleets next.
- Sales-led accounts, so no claim flow.
- No hard date, a standing agent channel and one engineer for a quarter.
- No existing CLI or MCP server.
- Gate results are unverified. I could not run the edge checks from here, and an unverified cell is not a pass.

## Questions that would change the ranking

1. Do you have a public API and OpenAPI spec today? That decides how much of the approval gate can live in the API instead of the UI.
2. Is there already a "block AI bots" preset at your WAF or CDN?
3. Do customers' agent fleets call anything beyond the dashboard today?