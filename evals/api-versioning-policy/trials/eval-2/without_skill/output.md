# Verdict

**The 90-day window is reasonable. The claim that "everyone gets a full quarter of warning" is not.** I haven't seen your written plan, so this review rests on what you've described.

## Review of the plan

**1. `@deprecated` reaches developers, not running apps.**
- The directive only shows up when someone opens an IDE, introspects the schema, or runs a linter against it.
- A deployed app sending stored queries never sees it. Neither does a mobile app on an old binary, a no-code connector, or an integration whose author left.
- With about 900 apps, expect a long tail of apps that nobody is actively watching.

**2. Deleting a field breaks the whole operation.**
- In GraphQL, a query that references a removed field fails validation entirely. The client doesn't just lose that field.
- One of the 14 fields in a query can take down a client's whole screen or workflow.

**3. Dates can't be the only deletion gate.** Gate deletion on measured usage as well as the calendar.
- Log field-level usage per app now, before the release.
- At day 0, you know which apps use which of the 14 fields.
- Contact those app owners directly: email, dashboard banner, and in-response notices.
- Delete only if usage is zero or the remaining callers have been individually handled.

**4. Check the mechanics of `@deprecated` itself.**
- A `reason` must be set, and it should name the replacement and the removal date.
- Under the GraphQL spec, required arguments and required input fields can't be deprecated.
- If any of the 14 are arguments or input fields, they need to become optional first.
- Every deprecated field needs a working replacement before you announce, not after.

**5. The clock start is ambiguous.**
- "90 days after the release ships" is unclear if the rollout is staged, or if a changelog entry appears later than the schema.
- Fix one anchor, such as the production schema deploy date. Publish the resulting removal date explicitly.

**6. Mobile and enterprise lag.**
- App-store update cycles and customer change freezes can exceed 90 days.
- Check contracts and SLAs for notice terms that are longer than 90 days.
- If the deleted fields are used by your largest customers, give them a longer path.

**7. Add a soft landing before deletion.**
- Run brownouts: short, announced windows where the fields return errors, one or two weeks before removal.
- Keep a kill switch to restore a field fast.
- Send reminders at 60, 30, and 7 days, aimed at the apps still calling the fields.

**Suggested timeline**

| Day | Action |
|---|---|
| Before release | Add per-app field-usage logging. Confirm replacements exist. Finalize `reason` text. |
| 0 | Ship `@deprecated`. Publish changelog and migration guide. Email owners of apps using the fields. |
| 30, 60 | Reminders to apps still calling the fields. |
| 76–83 | Brownout windows. |
| 90 or later | Delete, only if the usage gate passes or exceptions are recorded. |

## Deprecation Policy

*Draft for Legal review. Items in [brackets] need your input.*

---

# Quillhaven GraphQL API Deprecation Policy

**Effective date:** [date]
**Owner:** API Product Management
**Applies to:** the public Quillhaven GraphQL API

## 1. Purpose

This policy describes how Quillhaven retires parts of its public GraphQL API, and what notice and support developers can expect. It governs fields, arguments, input fields, types, enum values, and operations.

## 2. Definitions

- **Deprecation:** marking an API element as scheduled for removal. A deprecated element continues to work.
- **Removal:** the date the element stops working.
- **Deprecation notice:** the set of communications in section 4.
- **Registered app:** an application registered in the Quillhaven developer platform.

## 3. Minimum notice period

- Quillhaven will give at least **90 days** between the deprecation notice and removal.
- The period starts on the date the deprecation is live in the production schema. That date is stated in the notice.
- Quillhaven may extend a removal date at its discretion. It will not shorten one, except under section 7.

## 4. How we give notice

For each deprecation, Quillhaven will:

1. Mark the element with the GraphQL `@deprecated` directive. The `reason` states the replacement and the removal date.
2. Publish an entry in the [changelog] and a migration guide.
3. Email the [technical/owner contact] of each registered app that has used the element in the [90] days before the notice.
4. Show a notice in the [developer dashboard] for those apps.

Reminders go to apps still using the element at approximately 60, 30, and 7 days before removal.

**Limits of notice.** The `@deprecated` directive is visible in schema tooling and introspection. It does not appear in the responses of running applications. Quillhaven therefore relies on the direct contact in items 3 and 4 and does not treat the directive alone as notice to any specific developer. Developers are responsible for keeping their registered contact details current.

## 5. Replacements

Quillhaven will make a replacement available before or at the time of deprecation, except where the capability is being discontinued. In that case, the notice says so.

## 6. Removal process

Before removal, Quillhaven will:

1. Review usage of the element by registered apps.
2. Contact apps that still use it and, where practical, help them migrate.
3. [Optional] Run announced brownouts, short periods where the element returns errors, to surface remaining usage.

Removal takes place on or after the stated date. Quillhaven may postpone removal where usage remains significant, and will announce any postponement by the same channels.

**Effect of removal.** A request that references a removed element fails validation as a whole. Developers should plan migration with this in mind.

## 7. Exceptions

Quillhaven may remove or disable an API element on shorter notice, or without notice, where required to:

- address a security vulnerability or abuse,
- comply with law, regulation, or a court order,
- respond to a third-party dependency that is itself being discontinued, or
- protect the stability of the service.

In these cases, Quillhaven will give as much notice as is reasonable and will explain the reason afterwards where it can.

## 8. Contractual terms

If a written agreement with a customer specifies a longer notice period or other terms, that agreement controls for that customer. [Legal to confirm interaction with the Developer Terms and enterprise agreements.]

## 9. What this policy does not cover

- **Beta, preview, or experimental elements** (labeled as such in the schema or documentation) may change or be removed without the notice period.
- **Non-breaking changes**, such as adding fields, types, or optional arguments, need no notice.
- **Bug fixes** that correct behavior to match the documentation.

## 10. Changes to this policy

Quillhaven may update this policy. Changes are announced in the [changelog] at least [30] days before taking effect and do not shorten the notice for deprecations already announced.

## 11. Contact

Questions: [developer-support address]. Deprecation schedule: [URL].

---

## What I need from you

- **Contact data:** do all 900 apps have a working owner contact? If not, that's your biggest gap.
- **Enterprise contracts:** do any have notice terms longer than 90 days?
- **Field types:** are any of the 14 fields arguments or input fields?
- **Telemetry:** do you log field usage per app today?
- **Policy scope:** section 9's beta carve-out and the section 7 exceptions are standard, but Legal should confirm both.