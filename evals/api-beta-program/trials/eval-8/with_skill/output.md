# Beaconhive: Fleet-snapshots shutdown and Device-groups GA communications

Two parts of your plan break the `api-beta-program` skill's rules, so I changed them before drafting. The drafts below use the changed plan. Items in `<angle brackets>` are values I don't have.

## Changes to your plan

**Fleet-snapshots (kill)**

| Your plan | Change | Why |
|---|---|---|
| 3 weeks notice | About 6 months: private notices on 2026-10-26, shutdown 2027-04-30. | Two accounts run production on it. The skill says kill notice is months, not weeks, once anyone runs production. Honeycode, a beta kill, gave about 6 months. |
| Public changelog first | Private notice to all 8 enrolled accounts first. Then the waitlist. Then the public changelog. | Production callers must not learn of a shutdown from a public post. |
| Enrollment open until the end date | Close new enrollment today. | You are killing the feature, so you should not take on new callers. |
| Bill through shutdown | Marrowbot: credit the $200/month from the announcement date. Ospreyline: nothing to bill. | The skill says to stop billing from the announcement, then credit it where a signed order form says otherwise. Marrowbot's order form is a signed commitment, so credit it. Total credit at the default date is about $1,200, which is small next to the dispute risk. |

- **Legal check:** counsel should read Marrowbot's order form for a termination clause and any minimum term. Their notice goes out only after that read.
- **Shorter runway:** a shorter runway, 90 days at minimum, is defensible because telemetry-export already replaces the feature. That is your decision, not the skill's default.
- **Activation discrepancy:** two accounts call from production, but only one counts as activated. Check your activation-event definition before the exit-review write-up, because the numbers won't reconcile otherwise.
- **After the shutdown date:** return `410 Gone` with a pointer to telemetry-export. Don't return a silent 404.

**Device-groups (GA)**

| Your plan | Change | Why |
|---|---|---|
| Cut over on GA day, no overlap | Keep `/v1beta/device-groups` working for a full overlap window. | Four accounts run production on it. The skill says to use the GA deprecation window from `api-versioning-policy` when production traffic sits on the beta surface, and never to cut over silently. |
| Public announcement | Private notice to the 11 enrolled accounts first, 4 production owners included. Public changelog after. | Enrolled accounts hear first. |

- **Overlap length:** I couldn't read your versioning policy, so `<OVERLAP_END>` is left blank. Fill it from that policy. I'd use 90 days at minimum.
- **Compatibility change:** ship this on `/v1beta` now, ahead of GA. `/v1beta` accepts `name` as well as `group_label`, and responses return both fields. Callers can then migrate the field first and the path second.
- **Rename freeze:** the rename is a breaking change. Per the freeze rule, partners should migrate onto the final shape before the exit review. Landing the rename only on GA day defeats that.

## Dates assumed

- Today: Fri 2026-10-23.
- Private notices: Mon 2026-10-26.
- Public changelog: Wed 2026-10-28, after private delivery is confirmed.
- Fleet-snapshots shutdown: Fri 2027-04-30.
- Check-in calls: 2027-01-29 and 2027-03-31.
- Device-groups GA: `<GA_DATE>`.
- Device-groups overlap end: `<OVERLAP_END>`.

---

## Part 1: Fleet-snapshots shutdown

### 1a. Private email to Marrowbot Robotics (production caller, signed order form)

Send this only after counsel has reviewed the order form.

```
Subject: Fleet-snapshots preview ends on 2027-04-30 - what changes for Marrowbot

Hi <technical owner>,

We are discontinuing the Fleet-snapshots preview. You are hearing this before
anyone else, because your production systems call it.

Why: only one of eight preview accounts reached production-shaped use, and in
interviews most customers said they already solve this with the telemetry-export
endpoint. We decided not to take Fleet-snapshots to GA.

What stops: <list of Fleet-snapshots operations Marrowbot called in the last
90 days>. They stop working on 2027-04-30. After that date they return
410 Gone with a pointer to telemetry-export.

Before then:
- Export your snapshot data with <export tool or link>, available until 2027-04-30.
- Telemetry-export is the replacement. <Short mapping: which snapshot fields
  and use cases map to which telemetry-export parameters.> Migration notes:
  <link>.

Billing: we stop charging for Fleet-snapshots as of today (2026-10-26). Under
your order form, the $200/month will be credited from today until the end
date. Credit details: <how and when the credit appears>.

Timeline:
- 2026-10-26: this notice. New enrollment is closed.
- 2026-10-28: public changelog entry (it does not name any customer).
- 2027-01-29 and 2027-03-31: we will contact you to check your migration.
- 2027-04-30: Fleet-snapshots shuts down.

I am your contact for this: <name, channel>. If 2027-04-30 is a problem for
your release schedule, tell me now. I would rather hear it today than in April.

<Sender>
```

### 1b. Private email to Ospreyline Sensors (production caller, preview terms)

```
Subject: Fleet-snapshots preview ends on 2027-04-30 - what changes for Ospreyline

Hi <technical owner>,

We are discontinuing the Fleet-snapshots preview. You are hearing this before
anyone else, because your production systems call it.

Why: only one of eight preview accounts reached production-shaped use, and in
interviews most customers said they already solve this with the telemetry-export
endpoint. We decided not to take Fleet-snapshots to GA.

What stops: <list of Fleet-snapshots operations Ospreyline called in the last
90 days>. They stop working on 2027-04-30. After that date they return
410 Gone with a pointer to telemetry-export.

Before then:
- Export your snapshot data with <export tool or link>, available until 2027-04-30.
- Telemetry-export is the replacement. <Short mapping.> Migration notes: <link>.

Nothing changes in your access or terms until the end date. The preview was not
billed, and it stays unbilled.

Timeline:
- 2026-10-26: this notice. New enrollment is closed.
- 2026-10-28: public changelog entry (it does not name any customer).
- 2027-01-29 and 2027-03-31: we will contact you to check your migration.
- 2027-04-30: Fleet-snapshots shuts down.

I am your contact for this: <name, channel>. If 2027-04-30 is a problem for
your release schedule, tell me now.

<Sender>
```

### 1c. Private email to the other 6 enrolled accounts

Check your 90-day call logs first. If any of these accounts called the API at all, give them the same operation list as 1a and 1b.

```
Subject: Fleet-snapshots preview ends on 2027-04-30

Hi <technical owner>,

We are discontinuing the Fleet-snapshots preview. Reason: only one of eight
preview accounts reached production-shaped use, and most customers told us
they already solve this with the telemetry-export endpoint.

Your account's usage: <no calls in the last 90 days / these operations: ...>.
Fleet-snapshots stops working on 2027-04-30 and returns 410 Gone with a pointer
to telemetry-export after that. New enrollment is closed as of today.

Before then: export any snapshot data with <export tool or link>, and consider
telemetry-export as the replacement: <link>.

The preview was not billed, and it stays unbilled. Questions: <channel>.

<Sender>
```

### 1d. Waitlist reply

```
Thanks for your interest in Fleet-snapshots. We are discontinuing the preview
and are not enrolling new accounts. The telemetry-export endpoint covers the
same need for most customers: <link>. If it does not cover your case, tell us
what is missing at <channel>.
```

### 1e. Public changelog entry (publish 2026-10-28)

```
## Fleet-snapshots preview will be discontinued on 2027-04-30

We are ending the Fleet-snapshots private preview. In the preview, most
customers solved the same problem with the telemetry-export endpoint, and too
few accounts reached production use to justify taking Fleet-snapshots to GA.

- New enrollment is closed as of 2026-10-26.
- Fleet-snapshots stops working on 2027-04-30. After that, its operations
  return 410 Gone with a pointer to telemetry-export.
- Accounts that use it have already been contacted directly.
- Export your snapshot data with <export tool or link> before 2027-04-30.
- Alternative: telemetry-export. Migration notes: <link>.

Questions: <channel>.
```

Also put a banner on every Fleet-snapshots entry point: the docs overview, each operation's reference page, and the console.

---

## Part 2: Device-groups GA

### 2a. Private email to the 4 production accounts

```
Subject: Device-groups reaches GA on <GA_DATE> - what changes for <account>

Hi <technical owner>,

Device-groups leaves private preview on <GA_DATE>. Your integration calls
<operations called in the last 90 days>.

What changes:
- Path: /v1beta/device-groups becomes /v1/device-groups.
- Field: group_label becomes name.
- Everything else in the request and response shape is unchanged.

Overlap: /v1beta/device-groups keeps working until <OVERLAP_END>. During the
overlap, /v1beta accepts both group_label and name on requests, and returns
both fields in responses. You can switch the field name first and the path
second, in separate releases. (Available from <date>.)

After <OVERLAP_END>, /v1beta/device-groups returns 410 Gone with a pointer to
the migration guide.

Pricing: <GA price, any preview discount and its term, or "unchanged: free">.
Migration guide: <link>, with before and after request and response examples.
Questions: <channel>, answered by <team>. We will check in with you on <date>
to confirm your migration.

<Sender>
```

### 2b. Private email to the 7 non-production accounts

```
Subject: Device-groups reaches GA on <GA_DATE>

Hi <technical owner>,

Device-groups leaves private preview on <GA_DATE>.

What changes: the path /v1beta/device-groups becomes /v1/device-groups, and
the field group_label becomes name. Nothing else changes in the shape.

/v1beta/device-groups keeps working until <OVERLAP_END>. Migration guide:
<link>. Pricing: <...>. Questions: <channel>.

<Sender>
```

### 2c. Public changelog entry (publish at GA, after the private notices)

```
## Device-groups is generally available

Device-groups is now GA at /v1/device-groups.

Changes from the preview:
- The path moves from /v1beta/device-groups to /v1/device-groups.
- The field group_label is now name.

Preview accounts have been notified directly. /v1beta/device-groups keeps
working until <OVERLAP_END>, then returns 410 Gone.

Migration guide: <link>. Pricing: <...>.
```

---

## Before you send

1. Counsel reads Marrowbot's order form (termination clause and minimum term). Fleet-snapshots is blocked until then.
2. Fill in `<OVERLAP_END>` from `api-versioning-policy`. Device-groups is blocked until then.
3. Pull the per-account operation lists from 90 days of call logs for both features. The notices above don't work without them.
4. Confirm the activation definition (see the discrepancy above).
5. Decide whether to ship the `/v1beta` compatibility change (both fields) before GA.
6. Run the usual leak check on the public entries: no customer names, no internal paths beyond the public API.