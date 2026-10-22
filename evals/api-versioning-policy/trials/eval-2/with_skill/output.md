# Review of your 90-day deletion plan, and the draft policy

**Verdict: don't send the plan to Legal as written.** Marking the 14 fields `@deprecated` is correct. Scheduling deletion by calendar date is the flaw. The policy below keeps your cleanup goal and changes the removal trigger from a date to a date plus observed usage.

I couldn't run the skill's one-question-at-a-time interview, so the policy rests on the assumptions listed after the review. If any of them is wrong, the numbers change.

## Review findings

1. **`@deprecated` does not warn everyone.**
   - Apollo calls it "a documentation and tooling signal, not a removal mechanism."
   - It reaches only people whose tooling surfaces it, such as codegen, linters or IDE schema views. It never reaches a shipped mobile build or a server nobody has touched in two years.
   - "Everyone gets a full quarter of warning" is an unverified claim. This is the skill's "headers-only communication" failure mode.

2. **Removal must be gated on usage, not on the calendar.**
   - Migration completion is measured by traffic, "never by calendar."
   - In GraphQL, removing a field makes any operation that selects it fail validation. The client gets no partial result.
   - After day 90, some of your 900 apps may still send those queries. Each one breaks entirely.

3. **90 days is far below published floors.**

   | Audience | Floor |
   |---|---|
   | Fully public API | at least 12 months (Google Cloud, Shopify) |
   | Mobile or enterprise consumers | at least 24 months (Microsoft Graph, Meta) |

   - The closest precedent for roughly 90 days is Meta's Marketing API. It is a different, more sophisticated audience.
   - A document-workflow platform almost certainly has enterprise integrators. That puts you in the 24-month class.
   - Treat those figures as floors, not as averages to match.

4. **The clock is undefined.** "90 days after that release ships" is a start date. It doesn't say what happens at day 91 if traffic remains. An undefined clock becomes a support dispute.

5. **A published date you then slip does damage.**
   - Twilio extended one EOL three times, and Salesforce slipped a retirement by two years. Each slip teaches integrators to ignore your dates.
   - A hard date written before you have telemetry invites that outcome.
   - The fix is to publish "earliest removal date, subject to the usage gate," and to say so up front.

6. **Registered apps help you.** All ~900 apps have a registered owner, so you can reach them directly in a way anonymous API users can't. Contact data goes stale, so verify it.

7. **Batch the 14 fields.** One release that deprecates all 14 counts as one breaking-change event. The policy's health metric is no more than about 2 breaking changes per year.

**What your plan gets right.**
- The `@deprecated` marker comes first.
- The deadline is written down.
- Legal is involved before the removal, not after.

**A fast lane you may be able to keep.** If telemetry shows a field had zero requests for a full trailing 12 months, a short notice is defensible, and your 90 days could stand for that field. This is my judgment, not a published benchmark. Check each of the 14 fields' traffic before deciding.

## Assumptions to confirm

- **Surface:** GraphQL, fully public, with registered apps. Webhooks, REST and SDKs, if you have them, need separate policies.
- **Consumers:** some apps are mobile or enterprise. If you can confirm none are, the floor drops from 24 to 12 months.
- **Telemetry:** you can log per-field usage by app ID. If you can't, build that before announcing, because the policy depends on it.
- **Change frequency:** no more than about 2 breaking changes per year.
- **Effort:** field-level telemetry is affordable. Version machinery is not needed.

## Candidate policies

| | A. Continuous evolution + usage gate (recommended) | B. Date-versioned GraphQL (Shopify-style) | C. Your current plan |
|---|---|---|---|
| Scheme | One live schema | `YYYY-MM` quarterly versions | One live schema |
| Removal trigger | Floor and zero usage | Version retirement date | Day 90 |
| Effort | Telemetry plus outreach | High: multi-version schema upkeep | Low |
| Risk | Slow cleanup if telemetry is poor | Maintenance cost | Breaks live apps, undefined at day 91 |

Choose A. It is the paradigm's own default, and it fits a 14-field cleanup with no version machinery. Choose B only if you later want one versioning story across several surfaces.

---

# Quillhaven GraphQL API deprecation policy

*Effective [DATE]. Version 1.0. Owner: API Product. Reviewed by: Legal [name, date].*

## 1. Scope

- **Covered:** the public Quillhaven GraphQL schema: types, fields, arguments, enum values and directives.
- **Not covered:**
  - Webhook event schemas, REST endpoints and client SDKs, which follow their own policies. [Link each.]
  - Unreleased or preview surfaces marked as such, which may change at any time.
  - Anything not published in the schema or documentation.

## 2. Evolution rules

- Quillhaven runs one continuously live schema. It has no version numbers.
- Changes are additive by default.
- To retire a schema element, Quillhaven marks it `@deprecated(reason: "...")`. The reason names the replacement and links the migration guide.
- A deprecation is never removed on a calendar date alone. See section 5.

## 3. What counts as breaking

**Breaking** (follows this policy):
- Removing or renaming a type, field, argument, or enum value.
- Changing a field's or argument's type, including nullability.
- Adding a required argument or input field.
- Changing the meaning of an existing field's data.

**Non-breaking** (ships at any time):
- Adding types, fields, optional arguments, or enum values in enums listed as open: [list of open enums].
- Adding directives.
- Reordering fields.
- Changing the format or length of opaque identifiers.

**Not contractual** (may change without notice):
- Error message text.
- Field ordering.
- Response timing.
- Any observable behavior not described in the published schema or documentation.

## 4. Support windows

- **Standard notice: at least 24 months** from the announcement date to the earliest removal date. [Use 12 months if no mobile or enterprise consumers are confirmed.]
- **The clock starts** on the announcement date, which is the date the release containing the `@deprecated` marker ships. Quillhaven records that date in the changelog.
- **Zero-traffic fast lane:** if a field received no requests from any app for the 12 months before the announcement, its notice period may be shortened to **at least 90 days**. API Product must record the telemetry evidence and name the approver. [Confirm with Legal.]
- **Published dates are earliest-removal dates.** Quillhaven does not remove a field before its date. Removal after that date is subject to section 5.
- Partner or enterprise contracts may set longer periods. The contract governs where it conflicts.

## 5. Field rollover (removal)

A deprecated element is removed only when all of these are true:

1. The notice period in section 4 has elapsed.
2. Telemetry shows zero requests for that element over the last [90] days, or API Product has recorded and approved a named residue of known consumers with a plan for each.
3. Every app that used the element in the last [12] months was contacted at least 3 times, at [T-6 months, T-3 months, T-1 month] before removal.
4. The governance approval in section 8 is on file.

**If traffic remains at the earliest-removal date**, Quillhaven does one of these:
- Contacts the remaining apps and sets a new removal date, announced publicly with a reason.
- Removes the field anyway, only with approval and a recorded reason.

Each announced date that moves is counted and published under section 9.

## 6. Communication

Quillhaven never relies on the directive alone. For every deprecation it:

1. Adds `@deprecated(reason: "...")` and the replacement.
2. Publishes a changelog entry and a migration guide with concrete before-and-after queries.
3. Shows a banner in the developer dashboard.
4. Emails the registered contact of every app that called the element in the last 12 months, at each milestone in section 5.
5. Adds a deprecation warning to the `extensions` of responses to affected operations, where technically feasible. [Confirm feasibility.]
6. Offers a support channel for migration questions: [channel].

Quillhaven owns the migration, not just the announcement.

## 7. Enforcement at removal

- After removal, operations selecting the element fail GraphQL validation. Because no partial result is returned, the removal date is announced in advance in each email and the changelog.
- Quillhaven does not silently redirect, null out, or substitute a different field.
- Removal is logged in the changelog the same day.

## 8. Governance

- A schema diff check runs in CI on every schema change and flags breaking changes. [Tool.]
- **No breaking change ships without written approval from [named approver or board].** This applies equally to business-motivated changes, such as pricing or product moves.
- The approver checks: notice dates, telemetry evidence, outreach log, migration guide.
- When the schema outgrows one reviewer, Quillhaven moves to a review board with a written charter.

## 9. Security and exceptions

- Quillhaven may change or remove any element sooner when needed for a critical security or privacy issue. This is the only exception. Quillhaven will notify affected apps through [channel] as soon as it can, and publish the reason afterward.

## 10. Measurement

Reviewed [monthly] during any active deprecation and published [annually]:

- Breaking changes per year. Target: no more than 2.
- Per-element traffic share of deprecated fields, and the trend after each communication wave. A flat line after an email shows that channel failed.
- Elements removed at zero or accepted-residue traffic. Target: 100%.
- Announced removal dates that moved. Target: 0.

---

## Questions to resolve before Legal sees it

1. Do any apps ship mobile builds or serve enterprise customers? This sets 24 versus 12 months.
2. What did each of the 14 fields' traffic look like over the last 12 months, by app? This decides who qualifies for the fast lane.
3. Can you log per-field usage by app ID today? If not, that is the first task.
4. Is the `extensions` warning feasible in your gateway?
5. Do the developer terms need a clause pointing at this policy? That is for Legal.

I haven't saved this to `developer-platform-context.md` or any file. Tell me if you want it stored.