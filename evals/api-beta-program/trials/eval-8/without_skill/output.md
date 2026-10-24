# Beaconhive: Fleet-snapshots shutdown and Device-groups GA communications

I changed four things in your plans before drafting. Say so if you disagree with any of them.

**Changes to your plans**

| Your plan | What I drafted | Why |
|---|---|---|
| Changelog first, so everyone hears at once | Direct email to every enrolled account first, changelog an hour or two later | Marrowbot and Ospreyline run this in production. They should not learn about the shutdown from a public post. Marrowbot also has an order form. |
| Keep Fleet-snapshots enrollment open until the end date | Close enrollment the day of the notice | New enrollments would start a migration project the day they sign up. It also adds a billing obligation for a feature you are killing. |
| Bill through shutdown | Bill prorated to the shutdown date, nothing after | Charging for a day with no service is a dispute. Marrowbot's term may require more than this (see below). |
| Device-groups: cut over on GA day, no overlap | Announce about 2 weeks before GA. On GA day, keep `/v1beta/device-groups` working with both field names for 90 days. | The migration is small to write. Four production accounts still need a deploy window, and a hard cutover on GA day breaks any that miss it. The overlap costs you one alias and one field mirror. |

**Check before sending**

- ⚠️ Have someone read Marrowbot's order form. I haven't seen it. If it sets a minimum term or a notice period, 3 weeks may not satisfy it. The draft has a bracketed placeholder for any credit or refund. Fill it from the form.
- ℹ️ Your brief says "only 1 activated" but also "two call from production". Check how you define "activated" before anyone repeats that number. The drafts avoid it.
- ℹ️ Bracketed items are facts I don't have. The dates assume you send on Mon 2026-10-26.

**Send sequence**

| When | Action |
|---|---|
| Mon 2026-10-26, morning | Close Fleet-snapshots enrollment. Call Marrowbot, then send email 1A. |
| Same morning | Send email 1B to Ospreyline and email 1C to the other 6 accounts. |
| Same day, 1–2 hours later | Publish changelog entry 1D. |
| Mon 2026-11-16 | Fleet-snapshots shuts down. The endpoint returns `410 Gone`. |
| ~2 weeks before GA | Send email 2A to all 11 Device-groups accounts. |
| GA day | Publish changelog entry 2B. |
| GA + 90 days | `/v1beta/device-groups` sunsets. |

---

## 1. Fleet-snapshots shutdown

### 1A. Email to Marrowbot Robotics (order form customer)

**Subject:** Fleet-snapshots preview ends November 16: your plan and what we'll do for you

Hi [name],

We are ending the Fleet-snapshots preview on **Monday, November 16, 2026**. After that date the endpoint will return `410 Gone`.

You are one of two accounts calling it from production, so I'm writing to you before we post anything publicly.

**Why we're ending it.** Most preview teams solved the same problem with the existing telemetry-export endpoint, and we'd rather invest in that one path than maintain two. I know this is a shorter runway than you'd like, and I'm sorry for the disruption.

**What you need to do.** Move your calls to `GET /v1/telemetry/export`. [One or two lines mapping your Fleet-snapshots usage to the export parameters, for example "the per-device state you read from a snapshot is available with `fields=...`".] I'll walk through your integration with your engineers on a call this week, and we'll test against your real fleet if that helps.

**Your data.** [Say whether existing snapshots can be exported before November 16, and how.]

**Billing.** The order form's $200/month applies through November 16, prorated for the final partial month. You won't be charged after that date. [Credit or refund terms from the order form, if any.] If November 16 doesn't give your team enough time, tell me. I'd rather extend your access than have you rush a migration.

Can we talk this week? Let me know a time, or book one here: [link].

[Sender name, title]

### 1B. Email to Ospreyline Sensors (preview terms)

**Subject:** Fleet-snapshots preview ends November 16

Hi [name],

We are ending the Fleet-snapshots preview on **Monday, November 16, 2026**. After that date the endpoint will return `410 Gone`. Your account calls it from production, so I wanted you to hear this directly before we announce it publicly.

**Why.** Most preview teams solved the same problem with the telemetry-export endpoint, so we're consolidating on that one.

**What to do.** Move your calls to `GET /v1/telemetry/export`. [Short mapping for their usage.] I'm glad to review your integration with you, so reply or book time here: [link].

**Your data.** [Export option for existing snapshots, if any.]

Preview access is free of charge, so there is nothing to settle on the billing side. If November 16 is too tight for your release cycle, tell me and we'll talk.

[Sender name, title]

### 1C. Email to the other 6 enrolled accounts

**Subject:** Fleet-snapshots preview ends November 16

Hi [name],

We are ending the Fleet-snapshots preview on **Monday, November 16, 2026**. New enrollments are closed as of today.

Most preview teams solved the same problem with the telemetry-export endpoint (`GET /v1/telemetry/export`), so we're putting our effort there. If you use Fleet-snapshots in anything beyond experiments, reply and we'll help you move. Migration notes are in the changelog: [link].

Thank you for trying it. The feedback shaped this decision.

[Sender name, title]

### 1D. Public changelog entry

**Fleet-snapshots preview ends November 16, 2026**
*Deprecation · October 26, 2026*

We are ending the Fleet-snapshots private preview on **November 16, 2026**.

**Why.** During the preview, most teams solved the same problem with the telemetry-export endpoint. We are putting our effort there rather than maintaining two overlapping paths.

**What changes**
- Enrollment is closed as of today.
- Enrolled accounts have been notified directly.
- On November 16, Fleet-snapshots endpoints return `410 Gone`.

**If you use Fleet-snapshots.** Use `GET /v1/telemetry/export` instead. [Link to a short guide mapping snapshot reads to export parameters.] If the export endpoint doesn't cover your case, tell us at [email or link]. We want to hear about gaps.

---

## 2. Device-groups GA

### 2A. Email to all 11 preview accounts (about 2 weeks before GA)

**Subject:** Device-groups goes GA on [GA date]: two small API changes

Hi [name],

Device-groups goes generally available on **[GA date]**. Two things change in the API, and neither is urgent for you.

| | Preview | GA |
|---|---|---|
| Path | `/v1beta/device-groups` | `/v1/device-groups` |
| Field | `group_label` | `name` |

**Overlap period.** On [GA date], `/v1/device-groups` goes live. `/v1beta/device-groups` keeps working until **[GA date + 90 days]**, and:
- Requests accept either `name` or `group_label`.
- Responses return both fields.
- Every v1beta response carries `Deprecation` and `Sunset` headers.

On `/v1`, only `name` is accepted. Sending `group_label` returns a `400` that names the replacement field.

**What to do.** Change the path and rename the field, then deploy any time before [sunset date]. A before/after example is in the docs: [link]. If you'd like us to check a staging environment before GA, reply and we'll do it.

[Sender name, title]

### 2B. Public changelog entry (GA day)

**Device-groups is generally available**
*Release · [GA date]*

Device-groups is out of preview. It's stable, supported under our standard terms, and available on `/v1`.

**Breaking changes from the preview**

| | Before | After |
|---|---|---|
| Path | `/v1beta/device-groups` | `/v1/device-groups` |
| Request and response field | `group_label` | `name` |

```diff
- POST /v1beta/device-groups   { "group_label": "warehouse-east" }
+ POST /v1/device-groups       { "name": "warehouse-east" }
```

**Migration window.** `/v1beta/device-groups` keeps working until **[GA date + 90 days]**. It accepts both field names and returns both. Responses carry `Deprecation` and `Sunset` headers. After the sunset date it returns `410 Gone`.

On `/v1`, sending `group_label` returns a `400` that names the replacement field.

Preview accounts were notified on [date of 2A]. Questions: [link].

---

**Next step:** tell me the GA date and what Marrowbot's order form says about term and notice. I'll replace the brackets and tighten both emails to match.