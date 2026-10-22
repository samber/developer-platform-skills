**Don't put 50% in the deck.** No rigorous public study of consent-screen conversion exists. The circulating "50% drop-off" figures trace to vendor blog posts, not measurements. A board member who asks for the source will not get one.

## The number for the deck

Use your own data. Your install funnel gives a measured figure:

> "Workspace admins reject about 1 in 3 install requests today (Marlowe install funnel, [date range])."

Before Thursday, do three things:

1. Pull the exact rate and date range from the funnel, and replace "about a third".
2. Put the target on the slide as a hypothesis, not a forecast: "Redesign shipped to a 50% A/B split; result read at 4 weeks."
3. If the VP wants an outside reference, cite Slack's developer guidance, which is a documented principle, not a statistic: "Asking for more permissions than necessary can cause users or admins to reject the installation."

You can't yet say the rejections come from the consent screen. Nothing tells you why admins reject, so the screen is a hypothesis. The redesign below includes the instrumentation that gets you the cause.

## Why the current screen fails

- **Grouped headers** ("Read / Write / Admin") hide what each scope does. An admin sees the word "Admin" and rejects.
- **Raw scope strings** force the admin to translate them. Admins who can't explain a scope to security reject it.
- **All-or-nothing** leaves the admin one safe choice: cancel.
- **One screen for two audiences.** In a B2B workspace the end user and the admin are separate gates. The admin gate is where your third is lost.

## Redesigned screen

**Admin screen:**

```
[App logo] Acme Reports wants access to Marlowe workspace "Northwind"
Published by Acme Inc. · Identity verified

What this app can do                              Allow
─────────────────────────────────────────────────────────
View your dashboards and reports                  [x]   (required)
View who is in your workspace                     [x]
Create and edit dashboards on your behalf         [ ]   (optional)
Export data to files                              [ ]   (optional)

Needs admin approval
Access data for all workspace members             [x]  ⚠ org-wide
  Used for: "team usage report"

[Approve selected]   [Request changes]   [Decline]
```

Rules behind it:

1. **One plain sentence per scope.** Never group them and never show the raw string. Write the copy when the scope is created, and review it like UI copy. A scope that can't be explained in one sentence is a design smell.
2. **Required and optional scopes are separate.** Optional scopes are unchecked by default, and the admin can grant a subset.
3. **Read-only first.** Write scopes are off by default and listed after the read scopes.
4. **Org-wide and app-identity scopes sit in their own "Needs admin approval" block**, each with the reason the app gave at registration. The end-user screen never shows them.
5. **"Request changes" is a third exit** besides approve and decline. It lets an admin send the app a note such as "drop export access", which turns an outright rejection into a negotiation.
6. **Publisher identity is shown**, with its own badge. Keep it visually separate from any attestation or audit badge.
7. **Incremental consent.** Request a scope when the feature needs it, not at install. Re-consent shows only the net-new scope, never the full granted list again.

**End-user screen:** same per-scope sentences, with the org-wide block removed (an admin owns it).

## Server-side requirements (the screen depends on these)

- **Diff granted scopes against requested scopes on every authorization response**, and return the granted set explicitly. With partial grants, the two sets differ even when the admin thinks they approved everything.
- **Apps must disable features whose scopes were denied.** Document this in your developer docs.
- **Enforce at runtime that requested scopes are a subset of what the app declared at registration.**
- **Add scopes, never repurpose them.** A scope change forces re-consent.
- **Bind each scope to a token type** (app identity vs. user delegated) now. Retrofitting that later forces reauthorization from every user.

## Find out why admins reject

This is what answers "we can't tell why". Add these events and a one-question reason capture:

1. Events: `consent_viewed`, `scope_toggled`, `approved_partial`, `approved_all`, `request_changes`, `declined`. Each carries `app_id`, `actor_role` (admin or user), and the scope count and list requested.
2. On decline or request-changes, show one optional question: "What stopped you?" Options: too many permissions, unclear permission, don't know this publisher, need security review, other.
3. Slice rejection rate by scope count, by presence of org-wide scopes, and by verified vs. unverified publisher.

After 2–4 weeks you will know which of the three levers carries the loss. Without that, the redesign is a guess.

## Rollout and test plan

1. **Instrument the current screen first.** About a week of baseline data.
2. **A/B test** the new screen against the old one at the admin gate. The metric is admin approval rate, split by app.
3. **Read the result at 4 weeks.** Put the measured delta in the next board update, not a pre-announced target.
4. **Gates before ship:** every scope has per-scope plain-language copy; a partial-grant integration test exercises the server-side diff; the re-consent screen shows only the new scope.

## Open questions

I assumed these. Each one changes the design:

1. **Which scopes exist today?** If you ship one broad scope per group, per-scope copy needs a taxonomy change first.
2. **Do apps get app-identity (org-wide) access or only user-delegated?** That decides whether the "Needs admin approval" block exists.
3. **Are the 1-in-3 rejections concentrated in a few apps?** If yes, the cause is those apps' over-scoping, not your screen.

**Next:** pull the exact rejection rate and date range from the funnel, and put that figure on the slide in place of 50%. About 10 minutes.