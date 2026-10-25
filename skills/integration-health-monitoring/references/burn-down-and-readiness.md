# Burn-down and Readiness

The two-curve burn-down, the readiness worksheet, the exception register, brownout scheduling and the precedents behind them.

## Contents

- Two-curve burn-down
- Readiness worksheet
- Go/no-go memo
- Exception register
- Brownout scheduling
- Extensions and slips
- Precedents

## Two-curve burn-down

Plot weekly, from notice day to the break date:

- **Calls** on the deprecated surface. Large integrations migrate first, so this curve drops early and looks finished long before it is.
- **Integrations** still calling, split into top tier and long tail. This is the curve the gate reads.

Add a third line for unattributed calls. When it stays flat while the others fall, the residue is traffic you cannot notify, and only in-response warnings and brownouts will reach it.

No major provider publishes the readiness threshold it uses. Set your own from these curves and defend it in writing.

## Readiness worksheet

Fill one per surface, one week before each brownout and before cutoff:

| Line | Check | Status |
|---|---|---|
| 1 | Top-tier integrations neither migrated under the SKILL.md step 3 rule nor under exception | must be 0 |
| 2 | Long-tail integrations not notified at a verified contact or customer admin | must be 0 |
| 3 | Unattributed calls: authenticated surfaces / public surfaces | 0 / below floor |
| 4 | Replacement met its service objective for migrated traffic over the last several weeks, no open incident, headroom for residual load | yes |
| 5 | Exceptions without owner, reason or expiry | must be 0 |

A failed line names the next action, not a delay: line 1 returns to named outreach, line 2 to contact resolution, line 3 to attribution work or another brownout, line 4 to the replacement's owners.

## Go/no-go memo

Send the decision-maker this, not a date and a percentage:

```
Surface: POST /v1/charges    Proposed cutoff: 2026-12-01    Announced cutoff: 2027-01-15
Verdict: NO-GO for 2026-12-01; GO path for 2027-01-15 if lines 1 and 2 close by 2027-01-05

Line 1  top-tier not migrated: 7 of 22 (3 run quarter-end exports, next run 2026-12-31)
Line 2  long tail without verified contact: 41 of 180
Line 3  unattributed calls: 1,900 / week on an authenticated surface = gateway logging gap, fix first
Line 4  replacement met objective for migrated traffic, last 6 weeks: yes
Line 5  exceptions incomplete: 0

Next actions: named outreach to the 7 this week; contact resolution for the 41;
logging fix for line 3; first brownout 2026-11-18, 4 h.
Cost of waiting to the announced date: <on-call weeks>. Cost of cutting early: <customers x failed runs>.
```

The verdict names the line that blocks, so the next action is obvious and the date argument becomes an argument about one line.

## Exception register

One row per integration granted extra time:

| Integration | Surface | Reason | Owner | Granted | Expires | Allowed past cutoff by |
|---|---|---|---|---|---|---|

- Implement exceptions as an allowlist on the old surface, keyed on credential, so everyone else meets the original date.
- Give each a single expiry. A second extension needs the same review as the first.
- A row under a valid exception satisfies worksheet line 1 for that integration until its expiry.
- Contrast Microsoft's Azure AD Graph extended access: a self-serve per-app opt-in to one global end date, with no owner, reason or per-row expiry. It is a global slip gated by friction, not a register. Its useful half is the other lever: new applications were blocked from the old API by default.

## Brownout scheduling

- Announce every window in advance, in the changelog, the targeted email and the error body.
- Return the final-state status (for example `410 Gone`) during each window, mark it temporary in the body with the schedule, and send `Cache-Control: no-store`: 410 is heuristically cacheable, and a cached brownout outlives its window.
- Escalate duration: GitHub ran 12-, 24- and then 48-hour brownouts before removing query-parameter authentication; its Actions runner-image retirements used repeated 8-hour windows.
- Start each window inside working hours for the affected regions, so the engineer who sees the first alert can act on it.
- Pause on any incident in the replacement. GitHub paused one brownout series after an incident on the new API and resumed two days later.
- Offer a self-serve brownout where possible: Salesforce shipped an opt-in enforcement switch so admins could "temporarily force this breakage" and find their own dependent applications.

## Extensions and slips

A global slip is sometimes right and always costly:

- Slip for everyone only when the replacement is not ready (worksheet line 4).
- Give a high-harm row an exception in the register, never a global slip, and keep the date.

Precedents of global slips: Salesforce moved its API 21.0-30.0 retirement from Summer '23 to Summer '25 after partner consultation; Slack moved a method sunset by eight months and put a second retirement on hold; Atlassian moved Connect's end of support from December 2026 to the end of January 2027. Each slip teaches integrators that the next date moves too.

## Precedents

Notice periods published by large platforms run about a year to 24 months: Shopify supports each version at least 12 months with at least 9 months of overlap and flags deprecated calls in its dashboard, HubSpot and Zendesk ran roughly a year, Microsoft Graph and Meta commit to 24 months. These come from `api-versioning-policy`'s domain; this skill only runs the ladder inside whatever window the policy set.

Documented breakages share one cause: the notice reached the credential holder, and the person who had to act was elsewhere.

- Plugin developers were notified, but site owners had to migrate manually.
- Emails went to bot accounts.
- Admins were told to contact developers they could no longer identify.

Census the end owner, not only the credential holder.
