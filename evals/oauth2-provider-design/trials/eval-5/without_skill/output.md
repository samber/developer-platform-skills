# Consent screen redesign and the board number

## The number: don't use 50%

I have no verified industry figure for how much conversion an over-scoped consent screen costs, and I won't give you one for the deck.

- **The 50% has no source I can find.** It reads like a half-remembered stat from a blog post or vendor deck. If a board member asks "where's that from?", you have no answer.
- **The studies I know of measure other things.** Permission-prompt research covers mobile runtime permissions and social-login scopes, not B2B workspace-admin approvals. Admin approval is a different decision from a consumer tap, so those results wouldn't transfer even if I could cite them.
- **Your own data doesn't yet link the rejections to scope.** You know about a third of requests are rejected. You don't know why. Over-scoping is a plausible cause, but admins also reject because of the wrong requester, no security review, policy bans on all third-party apps, or an unclear vendor.

**Suggested slide wording (all true today):**

> **1 in 3 install requests is rejected by workspace admins. We haven't measured why, and the current consent screen gives us no way to find out.**
> Shipping a redesigned screen with built-in reason capture. First read: [date, e.g. 3–4 weeks after launch]. Target: [set after baseline, e.g. cut rejection rate from ~33% to ≤25%].

Only the target is a guess, and it should read as a target. If the VP insists on an external benchmark, I'd ask a colleague with access to published OAuth-app-store conversion data for a citable source rather than quote the 50%.

## The redesign

### What's wrong with the current screen

1. **Headers group by access type, not by purpose.** "Read / Write / Admin" tells an admin how much power you want, but not why. "Admin" alone is a red flag.
2. **Raw scope strings.** Admins can't judge `channels:history` without looking it up, and a confused admin rejects.
3. **All-or-nothing.** One scary scope fails the whole request, even when it powers an optional feature.
4. **No rejection reason is captured.** This is why you can't tell why a third of requests fail.

### New layout

```
┌──────────────────────────────────────────────────────┐
│ Marlowe Analytics wants to connect to [Workspace]    │
│ Requested by: Dana Lee (dana@acme.com) · Verified    │
│ publisher · Privacy policy · Security page           │
├──────────────────────────────────────────────────────┤
│ REQUIRED: Marlowe can't work without these           │
│                                                      │
│ ● See your workspace's usage data                    │
│   Powers dashboards and reports.                     │
│   Marlowe can't change any of your data.             │
│   ▸ Technical details (scopes: <read scopes>)        │
│                                                      │
│ ● Identify who is using it                           │
│   Matches reports to your team members' names.       │
│   ▸ Technical details (scopes: <identity scopes>)    │
├──────────────────────────────────────────────────────┤
│ OPTIONAL: turn on only what you need                 │
│                                                      │
│ [ ] Post scheduled reports to channels               │
│     Lets Marlowe send messages. Off = reports are    │
│     downloaded or emailed instead.                   │
│     ▸ Technical details (scopes: <write scopes>)     │
│                                                      │
│ [ ] Manage users and settings            ⚠️ Elevated │
│     Only needed for automatic user provisioning.     │
│     Most teams leave this off.                       │
│     ▸ Technical details (scopes: <admin scopes>)     │
├──────────────────────────────────────────────────────┤
│ You can change or remove access anytime in           │
│ Settings → Integrations. [Link to data-handling doc] │
│                                                      │
│ [ Approve selected access ]   [ Not now ▾ ]          │
│                                                      │
│ Not the right person to approve this?                │
│ [ Send to your security/IT team for review ]         │
└──────────────────────────────────────────────────────┘
```

### Design decisions

| Change | Why |
|---|---|
| Group by capability ("what it lets Marlowe do"), not by Read/Write/Admin | Admins decide on purpose and risk, not on scope taxonomy |
| One plain-language sentence per capability, plus a "can't do" line where true | Pre-answers the first question a security reviewer asks |
| Raw scope strings behind an expandable "Technical details" | Security reviewers can still audit them, and nobody else is confronted by them |
| Required vs optional split, with optional off by default | Turns "reject everything" into "approve the minimum". Admin scopes stop sinking the whole request. |
| Elevated-risk marker only on the genuinely high-risk item | Flagging everything makes the flag meaningless |
| Verified publisher, requester identity, privacy and security links at the top | Reduces "who is this?" rejections |
| "Send to IT/security for review" alternative | Many admins can't approve alone, and today the only options are approve or cancel |
| "Not now" opens a one-tap reason picker | Fixes the visibility problem (see below) |

### Reason capture on "Not now"

A single optional question: *"What held you back?"*

- Too much access requested
- Need security/IT approval first
- Don't recognise this app or publisher
- Company policy blocks third-party apps
- Just exploring, not ready
- Other (free text)

Log the choice with: which optional toggles were on, role of the decider, and whether the requester differs from the approver.

### Engineering prerequisite

Optional scopes require your product to **degrade gracefully** when they're absent, and to support **incremental authorization** so a feature can ask for its scope later, in context. Check this with engineering first. If every feature hard-depends on every scope, the toggles are cosmetic and the design won't help.

## How to get your real number

1. **Baseline now.** Instrument the current screen: views, approve, cancel, time on screen, and expand/scroll events. Pull the last 90 days of funnel data. Split the ~33% rejection by requester role, workspace size and plan.
2. **A/B test old vs new.** Randomize at the workspace level, not the user level, because admins decide per workspace. Primary metric: approval rate of install requests. Secondary: activation within 7 days. Guardrail: share of installs that grant only required scopes (if it jumps, check that feature usage doesn't fall).
3. **Read the reason picker.** After about 2–4 weeks it tells you what share of rejections is scope-related, versus policy, trust or "not ready". That share is the figure that belongs in the deck, and it comes from your own users.
4. **Size the test before launch.** Give your analyst the weekly install-request volume. At roughly a third rejection, detecting a 5-point improvement needs on the order of a few hundred requests per arm, so low volume means a longer test.

## Open questions for you

- Which scopes sit under each header today? I used placeholders. Send them and I'll write the real capability names and plain-language sentences.
- Which features break without which scopes? That decides what can be optional.
- Is the requester usually the same person as the approver? If not, the "send to IT" path matters more than anything else on the screen.