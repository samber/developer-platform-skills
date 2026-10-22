# Meridian Parts: v1 sunset enforcement policy (draft for approval)

## 1. What I changed from your brief

I did not write the "route every /v1 call to the /v2 handler" plan. It fails Meridian's own policy rules, and it doesn't deliver "no customer sees an error."

- **It is not error-free.** v1 clients send v1 requests and parse v1 responses. If v2 changed any field, type, required parameter, or status code, those clients will break inside their own code. That is the reason v2 exists.
- **The breakage moves out of your sight.** A 410 shows up in your logs and in support tickets on day one. A parse failure, or a wrong value that parses fine, shows up in a customer's system weeks later. That could be a changed fitment rule, price, or unit in an auto-parts catalog.
- **It is a breaking change by the policy's own definition.** Changing the response or status for the same request is breaking. It would need governance approval, and no one has approved it.
- **It is the pattern the skill names as a failure mode.** The skill calls this "undocumented fall-forward." Meta's version of it is the cautionary example: "your app keeps running while its behaviour changes underneath you." Meta falls forward to an older, compatible version. This plan jumps to a new contract, which is riskier.
- **v1 never dies.** Traffic keeps flowing, so you can't tell who migrated. v1 also becomes the unversioned path the skill says never to allow.

Head of support's goal is right: no customer should be surprised. The policy below enforces it as: **no live v1 consumer reaches the sunset date without having been contacted, acknowledged, and offered an extension.** That is the only kind of "no errors" the policy can promise.

## 2. Assumptions to confirm

I could not run the interview. Each answer below changes numbers in the draft.

- **Audience:** B2B partners, identifiable by API key, with notice windows in contracts (not a public policy page).
- **Scheme:** URI major version (`/v1`, `/v2`), with no unversioned access.
- **Date:** the sunset falls in October 2026, which is under four weeks away. I used `[D]` for the exact timestamp.
- **Notice given:** I don't know what notice v1 consumers have received. The benchmarks are at least 12 months for public APIs and at least 24 for mobile or enterprise consumers. If you are well short of that, the date should depend on usage (section 4), not the calendar.

## 3. Candidate policies

| | A. Hard cutoff + contracted extensions (recommended) | B. Cutoff + time-boxed v1 compatibility adapter | C. Fall-forward v1 to v2 (the original plan) |
|---|---|---|---|
| After `[D]` | All `/v1/*` return `410 Gone`. Allowlisted keys keep real, frozen v1. | Same, but extension keys are served by an adapter that translates to v2 and back to the v1 shape. | All `/v1/*` get v2 logic and v2 shapes. |
| Effort | Low: keep the v1 stack running for allowlisted keys only. | Medium: one transformer per v1/v2 difference, Stripe-style. | Lowest. |
| Risk | Loud failure for anyone who ignores notice. | Adapter bugs, and it needs its own end date. | Silent drift, no migration signal, v1 never ends. |
| Fits "no surprise" | Yes, through extensions. | Yes, and it hides v1 infrastructure from you. | Only on paper. |

I recommend A. Choose B only if the extension list is long and keeping the v1 stack running costs too much.

## 4. Policy text

### Enforcement at sunset

**Scope.** This section covers REST `/v1/*` on the Meridian Parts catalog API. It does not cover `/v2`, SDKs, or webhooks.

**4.1 Sunset behavior**

- At `[D]` (exact UTC timestamp, announced), every `/v1/*` request returns `410 Gone`.
- The body is `application/problem+json` (RFC 9457) with these fields:
  - `code`: `api_version_retired`
  - `retired_at`
  - `migration_guide_url`
  - `support_contact`
- Each response carries `Link: <…/v2/…>; rel="successor-version"`.
- The policy defines no redirect, rewrite, proxy, or handler substitution from `/v1` to `/v2`. A `301` or `308` counts as fall-forward and is also forbidden.
- Meridian does not serve unversioned paths at any time.

**4.2 Grace period**

- The `410` response continues for 30 days after `[D]`. v1 routes and code are then removed, subject to 4.6.

**4.3 Allowlisted extensions (the only exception)**

- A contracted partner may request an extension before `[D]`.
- An extension covers named API keys only, never a whole account or all traffic.
- Allowlisted keys keep the real v1 contract, frozen. No new v1 features or behavior changes.
- An extension lasts at most `[90]` days and cannot be renewed.
- `[Named approver]` signs each extension. The record lists the key IDs, the end date, and the reason.
- Extensions never move `[D]`. Keys not on the allowlist get `410` at `[D]`.
- Support's script for an extension request: acknowledge within one business day, then forward to the approver.

**4.4 Pre-sunset enforcement (my addition, not in the skill)**

- Run scheduled brownouts of `410` on `/v1/*` at `[D-4w]` for 1 hour, `[D-2w]` for 4 hours, and `[D-1w]` for 24 hours. Announce each one by email and on the dashboard before it runs.
- Brownouts surface customers who ignored email, while a rollback is still cheap.
- Skip any brownout if fewer than 7 days remain before it would run.
- Exclude allowlisted keys from brownouts.

**4.5 Communication required before `[D]`**

Verify or send each item. If `[D]` is under 30 days away, do all of them now.

- `Deprecation` header (RFC 9745) on every v1 response, `Sunset: [D]` (RFC 8594) once the date is firm, and `Link: rel="successor-version"`. Mark `deprecated: true` in the v1 OpenAPI document.
- Targeted email to every key with v1 traffic in the last 30 days. Include the date, the migration guide, and how to request an extension.
- Direct contact from an account manager to the top `[N]` keys by v1 volume. Log each acknowledgment.
- Dashboard banner and a changelog entry.
- A migration guide covering each v1→v2 change with concrete steps, plus a support channel.
- Do not rely on headers alone.

**4.6 Removal criteria**

- Remove v1 code only when observed v1 traffic is zero, or at an accepted residue of `[<0.1% of calls and no contracted account]`.
- A date passing proves nothing about migration. Telemetry decides.

**4.7 Security exception**

- Meridian may patch any version for critical security or privacy issues, with notice through `[channel]`.

**4.8 Governance**

- No change to `[D]` and no extension beyond 90 days ships without `[named approver]`.
- Any fall-forward, redirect, or handler substitution counts as a breaking change. It needs the same approval and is documented as a policy change first.
- The CI breaking-change diff (`[oasdiff or equivalent]`) runs on v1 and v2 specs.

**4.9 Measurement**

- **Unacknowledged live v1 consumers at `[D]`:** target 0. This replaces "no customer sees an error" as the support metric.
- **v1 traffic share:** reviewed weekly until removal. A flat line after an email wave means that channel failed.
- **Slipped sunset dates:** target 0. Extensions are per key and don't count as slips.
- **Extensions granted:** count and age, reviewed at `[D+30d]`.

## 5. Decisions I need from you

1. How much notice have v1 consumers actually received, and what is the exact `[D]`?
2. Who is the named approver for extensions and for date changes?
3. Do you want A, or B (an adapter for extension keys)?
4. What does v2 change that v1 clients send or parse? The answer sizes the migration guide and decides whether B is feasible.

I would validate each section with you before finalizing, as the skill requires. Nothing here has been written to a file.