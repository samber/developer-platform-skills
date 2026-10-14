# Marlowe Analytics: consent screen redesign and the board number

## The number for the deck

**Don't put 50% on the slide.** No rigorous, public A/B study of consent-screen conversion exists from a major identity provider. The "50% drop-off on over-scoped consent screens" figure traces to vendor blog posts, not measurements. If the VP cites it and someone on the board asks for the source, there isn't one.

Use these instead:

1. **Your own number, which is stronger.** About one third of install requests are rejected by workspace admins. You measured that yourselves, and it's the baseline the redesign has to beat.
2. **The qualitative claim, attributed to Slack.** Slack's developer guidance says: "Asking for more permissions than necessary can cause users or admins to reject the installation." That is a vendor's operating principle, not a statistic. Label it that way on the slide.
3. **A target, not an industry figure.** For example: "Cut admin rejections from ~33% to X% within one quarter of shipping." Pick X after the baseline work below. There are no industry thresholds to borrow.

If someone insists on 50%, put it on the slide as "illustrative vendor claim, unverified", never as a benchmark.

## Why the current screen loses admins

- **Grouped buckets hide what the app does.** "Read access / Write access / Admin" tells an admin nothing specific. Auth0 recommends per-scope descriptions over grouped permission names.
- **Raw scope strings are developer jargon.** An admin can't judge risk from `crm.leads.read`-style identifiers. The consent copy for that scope should read "View your sales leads".
- **All-or-nothing makes rejection the safe choice.** An admin who is fine with 80% of the request has only "cancel" available.
- **The "Admin" bucket is probably the main driver.** I haven't seen your scopes, so this is a hypothesis. It is the first thing to check.

## Redesigned consent screen

Scope names and copy below are placeholders. Replace them with Marlowe's real scopes.

```
[App logo]  Acme Reports wants to access Marlowe workspace "Northwind"
Publisher: acme.com ✅ domain verified

Required to work                              (cannot be turned off)
  ☑ View dashboards and reports               [analytics:read]
      Why: Acme Reports needs it to build your weekly summary.

Optional                                      (turn off any you don't want)
  ☑ View user and team names                  [users:read]
      Why: Lets Acme label reports by owner.
  ☐ Create and edit dashboards                [dashboards:write]
      Why: Only needed for the "Publish to Marlowe" feature.

Needs admin approval                          (shown only to admins)
  ☐ Manage workspace members and billing      [admin:write]
      Why: Only needed for automatic seat sync.
      ⚠️ This lets the app change who has access to your workspace.

Details: what data the app can see, what it cannot do

[ Approve selected ]   [ Cancel ]
```

### Design rules, each tied to the skill

1. **One plain sentence per scope.** Never grouped buckets, never the raw string as the headline. The string appears small, for auditors. A scope you can't explain in one sentence is a scope-design smell.
2. **Split required from optional.** Admins can approve the core and decline the rest. This is the direct fix for all-or-nothing.
3. **Add a "why this app needs it" line per scope**, written by the app developer at registration and reviewed by you.
4. **Show the admin tier separately.** B2B installs have two consent surfaces: the end user and the org admin. The admin surface should be a first-class design, with an approval queue, org-wide grant review, and an app-identity permission tier. Don't bolt it on afterwards.
5. **Show the publisher's verification status.** Use a separate badge for each signal: identity verified, self-attested, independently audited. Do not use one undifferentiated checkmark.
6. **Default to read-only.** Write and admin scopes are opt-in, and an app asking for them has to justify them.

## Server-side changes the new screen requires

- **Always diff granted scopes against requested scopes.** With partial grants, the granted set may not match the request. Return the granted set explicitly. Apps must disable features that depend on scopes they didn't get, and must be able to re-request later without penalty. Add an integration test for a partial grant.
- **Support incremental authorization.** Apps request a scope when the feature needs it, not at install. The re-consent screen shows only the net-new scope, not everything already granted. Google re-displays everything, and developers complain it makes them "look sloppy". Test the delta rendering explicitly.
- **Scopes are additive-only.** Never change what an existing scope means. Changing a scope set invalidates refresh tokens and forces re-consent, so batch scope additions.
- **Enforce declared scopes at runtime.** Reject any request for scopes the app didn't declare at registration. This also stops apps from asking for more than they were reviewed for.
- **Bind each scope to a token type** (bot/app vs. user-delegated) if both exist. Retrofitting this later forces reauthorization from every user, as Slack documented.

## Measure it, so the Thursday claim becomes a real number later

Baseline these now, before shipping:

- Install requests, split by approved, rejected, and abandoned.
- For rejections: which scopes were in the request, and which app. This tells you whether a few over-scoped apps drive the third, or whether it's broad.
- Share of apps requesting scopes their API traffic never uses.
- Median app-review turnaround.

Then ship the screen to a subset of apps or workspaces and compare against the baseline. Only that comparison gives Marlowe a defensible conversion figure. One caveat: if you ship the screen and a scope cleanup together, you can't separate their effects.

## Questions I'd normally ask first

I proceeded on assumptions, so these could change the design:

1. Which scopes sit in your "Admin" bucket today, and do any reach other users' data or PII? If so, those need a stricter app-verification tier.
2. Do apps act only on behalf of a signed-in user, or also with their own identity?
3. Does an admin approve before or after the end user, and is there an approval queue today?
4. Are the rejected installs concentrated in a few apps?

## Suggested slide wording

> "About one third of admin install requests are rejected today. Industry guidance (e.g. Slack) is that over-requesting permissions is a leading cause of rejection. We're moving to per-permission, optional, plain-language consent and will report the measured change next quarter."

No industry conversion statistic exists to cite, so the slide uses none.