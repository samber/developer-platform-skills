# v2 reporting API deprecation: communication plan (second opinion)

**Verdict:** keep the header idea, but it is one channel of five and it is not the plan. As proposed, it fails on every claim you made for it.

## What's wrong with "Sunset header on all v2 responses"

- **"Every client gets the signal on literally every call."** The signal is sent, but it is not received. Most API tooling and HTTP clients ignore these headers, and most integrators never log response headers. A header-only plan satisfies the RFC and reaches almost nobody. This is a named failure mode.
- **"RFC-compliant."** RFC 8594 (`Sunset`) is Informational, not Standards Track. The standard header for this is `Deprecation` (RFC 9745, Standards Track, March 2025). Ship `Deprecation` first. Add `Sunset` once the date is firm.
- **"After the date we're covered."** You aren't. If you own the thing being deprecated, you own migrating its consumers. Announce-and-walk-away is a named failure mode. About 3,000 keys is a list you can enumerate and contact, so "we put it in a header" will not hold up when a customer's reports break.
- **14 months** clears the 12-month public floor (Google Cloud, Shopify). It does not clear the 24-month floor (Microsoft Graph, GitHub, Meta) that applies if any consumers ship mobile apps or are enterprises. I don't know which applies to you (see questions below).

## Recommended plan

Stages: announce → deprecate → sunset → removal. Never go from announce straight to removed.

### 1. Before announcing (week 0)

1. Confirm the replacement exists. You can't announce a deprecation without a successor and a **migration guide** (concrete steps, endpoint-by-endpoint mapping, code samples, a named support channel). If there's no v3 yet, the clock shouldn't start.
2. Check what v2 means for new callers. A version that is both deprecated and still the default is a named failure (Discord). Stop issuing new keys on v2 by default.
3. Pick the sunset date as a **commitment**. Moving it later teaches integrators to ignore your dates (Twilio extended one EOL three times).
   - Define when the clock starts. Write "14 months from the announcement date, [date]", not "about 14 months".
   - Avoid the year-end freeze.
   - Example: announce Tue 2026-11-03, sunset Tue 2028-01-18 (about 14.5 months).
4. Pull a baseline from API logs: per-key v2 call volume for the last 90 days, plus which endpoints each key uses. Everything below targets from this list.

### 2. Announce (week 0)

- Post a changelog entry and a docs banner.
- Add a dashboard banner shown to logged-in users who hold a v2-active key.
- Send an email to the owner of every key with recent v2 traffic.
  - Include the date, the migration guide link, and an offer of help.
  - Check contact data first. Keys with stale or missing owner emails are the highest-risk group.

### 3. Deprecate: headers plus in-band signals (week 0 onward)

- `Deprecation` header (RFC 9745) on all v2 responses, now.
- `Sunset: <date>` (RFC 8594) on all v2 responses, now, since the date is firm. These are the headers you proposed. Keep them and add the rest.
- `Link: <v3-url>; rel="successor-version"` (RFC 8288), so tooling finds the replacement.
- `deprecated: true` in the v2 OpenAPI document, so docs and codegen surface it.
- **In-response warning** in the payload, if the reporting format allows it (Slack's approach). It reaches exactly the callers still affected and costs much less than a mass campaign.

### 4. Targeted outreach waves

Repeat the email to keys still calling v2 at **T-6 months, T-3 months, T-1 month** (T = sunset date). Add T-9 months and T-2 weeks if volume is still material. Each wave is smaller and more personal than the last.

- At T-3 months, switch from mass email to direct contact (account manager or support) for the top keys by volume.
- Offer migration help: office hours, a diff-style guide, or a compatibility check script.
- Measure after every wave. Deprecated-version traffic share should fall. A flat line after a mass email means that channel failed, and you want to learn that months before the sunset date, not on it.

### 5. Enforcement at the sunset date

Use a hard cutoff, not a silent fall-forward.

- After the date, v2 returns `410 Gone` with a descriptive error body and the successor link.
- Keep that `410` response for a grace period (for example 30 days) before removing anything.
- Don't reroute v2 calls to another version. Silent behavior drift is the Meta cautionary tale.
- Decide in advance who may grant a per-customer exception, and write it down. Without that, the first escalation will write the policy for you.

### 6. Governance

- Name one approver for the sunset date, and put the policy in writing: the breaking-change definition, the notice windows, and a narrow security exception.
- Don't let a business-motivated change skip this process (the Twitter/X ~7-day notice is the example).

### 7. Measurement

- **Migration completion by usage, never by calendar.** v2 is removable when traffic is zero, or a residue you have knowingly accepted. A date passing proves nothing about who migrated.
- Track deprecated-version traffic share by wave, and the number of keys still calling v2 against your week-0 baseline.
- **Date integrity:** the target for slipped sunset dates is zero.
- No industry threshold exists for the traffic metrics. Baseline them on this first cycle.

## Questions that could change the plan

I skipped the full interview to give you a usable draft. These answers would change it:

1. **Who calls v2?** If any consumers ship mobile apps or are enterprises, raise the window to at least 24 months.
2. **Does v3 (or an equivalent successor) exist today?** If not, the 14-month clock shouldn't start yet.
3. **Can you contact every key owner?** Check how many of the 3,000 keys have a valid owner email.
4. **Is there a hard external deadline?** If so, that argues for a tighter plan with more direct contact.
5. **How many people can handle migration support?** That sets how much of this is self-serve versus hands-on.

## Suggested answer to your tech lead

Ship the headers as the "machine" channel. Make email to affected keys, a migration guide, and per-key tracking the plan. Enforce with a `410`, and measure by traffic, not by date.