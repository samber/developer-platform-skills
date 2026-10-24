# Marrowline Zapier plan review: OAuth2 and `/v1/employees` sunset

## Bottom line

**Do not run the plan as written.** Three steps break, and one risk the plan misses comes first.

1. **`migrate 1.6.0 2.0.0 100` cannot work.** Zapier migrates only within one major version†. Every user must move their Zaps to 2.0.0 by hand. Zapier gives you no user email list, so you reach them only through your own channels.
2. **A 10-day deprecation notice is below Zapier's minimum.** The deprecation date must be 3 weeks to 1 year ahead†. Zapier's own email goes out 14 days before†. 10 days is also too short for 2,400 users who must rebuild Zaps by hand.
3. **Deleting 1.x is not possible while it has users.** Delete a version only at zero users, counting paused Zaps and connections. Deprecation pauses every unmigrated Zap, so the people left behind lose their automations.
4. **Missed risk: the `/v1/employees` sunset lands before the OAuth2 work.**
   - The sunset is in about 6 weeks (roughly 2026-12-04). 2.0.0 cannot ship before then.
   - 1.6.0 breaks for all 2,400 users on that date. `new_employee` and `find_employee` both call `/v1/employees`.
   - Nobody else can pick up this fix, so ship it on the 1.x line first.

Next action: ask platform engineering today whether `/v1/employees` can slip 2 weeks, and whether `/v2` ids and sort order match `/v1`. Details are in section 7.

## 1. Assumptions

Each assumption below stands in for an answer I lacked. Correct any that are wrong.

- A1. "Q1" means calendar Q1 2027, so the deadline is 2027-03-31. Today is 2026-10-23.
- A2. Marrowline's API has no OAuth2 server yet. This is the unknown most likely to break the Q1 date. If one exists, section 5 gets shorter.
- A3. `/v1` returns `hired_on` as an ISO 8601 string and `name` as one combined string. Check this against the 1.6.0 sample data before writing the mapping.
- A4. `new_employee` is a polling trigger. It is not a REST hook.
- A5. `/v2/employees` keeps the same `id` format and supports newest-first sorting.
- A6. No other step calls `/v1/employees`. Check hidden dropdown triggers and the `authentication.test` call, because both often use it.
- A7. Marrowline can identify Zapier-originated API traffic from its own access logs. Basic-auth usernames plus user agent or IP would do. This is how you build a user list.
- A8. Automatic migrations and the Integration Maintenance Program are on. They are the default.
- A9. The 6 live templates sit on 1.6.0 and use only `new_employee` and `find_employee` plus other apps' steps.

## 2. Stage and route

The integration is public with live users. 1.6.0 is promoted, built on the CLI, and has about 2,400 active users.

Route: **Maintain**, then **Publish** steps 4-5 for the template resubmission. Under the rule "any version with live users, or any planned change to one", each change is classified first.

| Change | Class | Consequence |
| --- | --- | --- |
| Basic auth to OAuth2 | breaking | Needs a new major. Cannot migrate across it. |
| `/v1` to `/v2` call with the old output shape kept | non-breaking, if diffed by hand | Ship as 1.7.0 inside the 1.x major. |
| `name` split into `given_name` and `family_name` | breaking if exposed as-is | Rebuild `name` in code. |
| `hired_on` as epoch seconds | breaking if exposed as-is | Convert back to the v1 format in code. |
| Dedupe-relevant order or ids | breaking in effect | Verify that `/v2` matches `/v1`. |
| Deprecating and deleting 1.x | see section 7 | Delete is not available. |

## 3. Step table

| Key | Label | Type | Class | Reason |
| --- | --- | --- | --- | --- |
| `new_employee` | New Employee | polling trigger | `keep` in 1.7.0 and 2.0.0 | Same key, same output keys, same shape. Only the upstream endpoint changes. Map `/v2` back to the old shape in the `perform` code. |
| `new_employee` output `name` | n/a | output field | `keep` | Rebuild it as `given_name + " " + family_name` in code. Check the result against the old string for edge cases such as middle names, ordering, and empty family names. |
| `new_employee` output `hired_on` | n/a | output field | `keep` | Convert epoch seconds to the v1 format, with the same timezone offset. Do not pass the epoch through. |
| `new_employee` outputs `given_name`, `family_name` | n/a | new output fields | `additive` | New optional output keys are non-breaking. Add them in 1.7.0 and keep them in 2.0.0. |
| `find_employee` | Find Employee | search | `keep` | Same treatment. A miss still returns `[]`. Check that the `/v2` filter params match the old search inputs. |
| `authentication` | n/a | auth | `breaking` | See section 4. Lands only in 2.0.0. |
| Hidden dropdown triggers, `authentication.test` | n/a | n/a | unknown | Run `grep -rn "v1/employees"` across the repo before the sunset. Fix anything found in 1.7.0. |
| Any new step key or twin step (`new_employee_v2`) | n/a | n/a | `rejected` | Not needed if the shape can be mapped back. A twin step would invalidate the 6 templates on any hidden step. Use a twin only if the mapping cannot be made faithful. |

## 4. Auth and trigger-type decisions

**Auth: OAuth2 in a new major (2.0.0).** The skill lists an auth scheme change as breaking. OAuth2 is Zapier's preferred scheme†.
- Rests on: Marrowline exposing an OAuth2 authorization server.
- You cannot replace the scheme on a promoted version with more than 4 users†.
- Before building, email Zapier partner support. Ask whether assisted connection migration exists for this integration†. Zapier can sometimes migrate connected accounts between schemes for public integrations. If yes, this removes most of the manual rebuild. If no, plan as written.
- Auth requirements for the OAuth server:
  - It must return HTTP 401 on expired tokens, because Zapier refreshes on 401 only.
  - Set `refreshAccessToken` and `autoRefresh: true`.
  - Store the client id and secret as per-version environment variables (`env:set`).
  - Read `redirect_uri` from `zapier-platform describe`.
  - Use the narrowest scope that serves read-only triggers plus searches. HR data is sensitive.
  - `connectionLabel` must never be a secret.

**Trigger type: keep `new_employee` as polling.** Do not flip it to a REST hook. A type change is breaking. A 2.0.0 hook trigger would also widen scope when the deadline is tight. Revisit after Q1.

**Polling contract on `/v2`:**
- Request newest-first with an explicit sort and a limit of 100† per page, because Zapier never reads page two.
- Make the id match `/v1` in value and format. A different id format fires every unseen item as new on the first poll after the change.
- Do not filter "already sent" items server-side.

## 5. Publish checklist

Week 1 is the week of 2026-10-26.

| Item | Owner role | Week |
| --- | --- | --- |
| Confirm with platform engineering: sunset date, 2-week buffer, `/v2` ids, sort order, `hired_on` format | Platform eng + CTO | W1 |
| Email Zapier partner support: assisted connection migration for the basic-to-OAuth2 change | Integration owner | W1 |
| Build the list of affected accounts from API access logs | Backend engineer | W1-2 |
| Decide whether an OAuth2 server exists. If not, start it and set a date | CTO + security | W1 |
| Run `zapier-platform pull` before any push, because of the Integration Maintenance Program | Integration owner | W1 and before each push |
| Clone 1.6.0 to 1.7.0. Swap to `/v2`, map back, add new output keys, update unit tests with `nock` | Integration engineer | W1-3 |
| Hand diff of `new_employee` and `find_employee` output against a recorded 1.6.0 response | Integration engineer + reviewer | W3 |
| `validate`, canary 1.7.0 at 5-10% for 30-60 min†, then promote | Integration owner | W4 |
| Migrate to 1.7.0 at 5%, watch Monitoring, then the rest | Integration owner | W4-5 |
| Buffer week before the sunset | all | W6 |
| Build 2.0.0 on the 1.7.0 code. Keep step and field keys identical | Integration engineer | W5-9 |
| Push `2.0.0-beta` to a labelled version and test with internal accounts | Integration engineer | W8-9 |
| Promote 2.0.0 and mark older versions legacy, oldest first | Integration owner | W10 |
| Rebuild the 6 templates on 2.0.0 and resubmit them | Integration owner + marketer | W10, approval about 2 weeks† |
| Send user comms (see section 7) | Support lead + marketer | W10 onward |
| Set the deprecation date | CTO | W10 |
| Deprecation date and security sign-off | CTO + security | by 2027-03-15 |

## 6. Growth actions ranked

1. **Rebuild the 6 templates on 2.0.0 and resubmit them on promotion day.** Templates must use the promoted version†. Deprecating 1.x marks the old templates Invalid within 24 hours†. Moved by interview answers 1 and 5: public stage, 6 templates live, hard deadline.
2. **Replace every embedded old template in launch posts and help articles.** The embed links die when the templates go Invalid. This takes minutes per article.
3. **Put a migration banner in Marrowline's own Zapier settings page.** Use the access-log list from W1-2. Zapier cannot reach these users, so Marrowline's channels carry the whole message.
4. **Add a support macro for "my Zap paused after the Zapier update".** The cost is low and it deflects tickets in the weeks around the cutoff.
5. **Defer the Workflow Element and the Workflow API marketplace.** They are not what moves the date.

## 7. Versioning plan

**Target versions:**
- 1.7.0: `/v2` swap behind the old output shape. Basic auth stays.
- 2.0.0: OAuth2. Same step keys, same output shape, same `/v2` call.

**Order matters: ship 1.7.0 first.** Doing the endpoint fix inside 2.0.0 means 1.x breaks on the sunset date with no fix available.

**1.7.0 release procedure:**
1. Clone 1.6.0, because it is promoted and frozen. Fix the clone, run `validate`.
2. Canary at 5-10%† for 30-60 minutes†. Stop if errors rise by more than 5%†.
3. Promote.
4. `zapier-platform migrate 1.6.0 1.7.0 5`, watch Monitoring, then raise it. This is the same major, so migration is allowed†.
5. Do not use 100 on the first run. Promotion already moves a first group under automatic migrations.

**Diff by hand before promoting** (promotion checks do not catch these):
- Output key set, including the new `given_name` and `family_name`.
- Response shape, including `name` and `hired_on` values on records with unusual data.
- Order and id of the first 100 items from `/v2` against `/v1`, because dedupe memory holds `/v1` ids.
- Search filters.
- Empty and null names, and epoch-to-date conversion edge cases such as timezone and zero.

**Fallback if `/v2` ids or order cannot match `/v1`:** do not edit the trigger in place. Add `new_employee_v2` under a new key, hide the old step, and rebuild the 6 templates on the new key. Promote a version whose old step throws a clear error naming the replacement.

**2.0.0 release procedure:**
1. Build from the 1.7.0 code. Replace `authentication` only.
2. Test on a labelled version (`2.0.0-beta`). Labelled versions cannot be migrated to, which is safe for testing.
3. Promote. 1.7.0 becomes Available.
4. Mark older versions legacy one at a time, oldest first. This hides them from new Zaps and keeps existing ones working.
5. Do not use `zapier-platform migrate` across the major. It will not work†.

**Deprecation and communication:**
- Set the date at least 8 weeks after 2.0.0 promotion. Suggested: no later than 2027-03-15, leaving 2 weeks before the security deadline.
- Use your own notices at 60, 30, 14, 7 and 1 days before, alongside Zapier's email at 14 days†. Zapier's email does not reach anyone Zapier already migrated.
- Deprecate only because 1.x will stop working: either Marrowline's API stops accepting basic auth from Zapier at Q1 end, or the security review says so. Confirm that fact with security. Otherwise mark 1.x legacy and stop there.
- **Do not delete 1.x.** Deleting is possible only at zero users†. A deprecated version stays on record. Drafts also migrate only when published, so a user can republish an old draft onto an old version until deprecation.
- Expect attrition. Set a target share of users on 2.0.0 and track it weekly.

**Risks to name to security:**
- If OAuth2 slips past Q1, 1.x with basic auth stays alive past the deadline. Agree a fallback now, such as restricting basic-auth access from Zapier IPs.
- HR automations built on `new_employee` often drive onboarding. Paused Zaps mean new hires get no provisioning. Warn customers explicitly.

## 8. Metric baseline

| Metric | Current value | Where to read it |
| --- | --- | --- |
| Active users | about 2,400 (stated) | Developer Platform, Partner Program tier page |
| Partner tier | Gold-range (350†+), below Platinum (3,000†) | Partner Program tier page |
| Share of users on 1.6.0 | unknown, probably near 100% | Developer Platform, Versions and Users tab |
| Zap activation within 24 h per step | unknown | Developer Platform, Monitoring |
| Run errors per step | unknown | Monitoring logs, `zapier-platform logs` |
| Open bugs and feature requests, median days to first response | unknown | Bugs & Feature Requests queue |
| Templates live | 6 | Developer Platform, Zap Templates |
| Users migrated to 1.7.0, then 2.0.0 | not started | Versions page, plus your access-log list |
| Support tickets mentioning Zapier | unknown | Marrowline support tool |

† Zapier platform numbers: verify against Zapier's live docs before quoting any of them. Covers the 3-weeks-to-1-year deprecation window, the 14-day user email, same-major migration only, the fewer-than-5-users edit rule, canary 5-10% for 30-60 minutes with a 5% error stop, the 100 items per poll and one-page read, the ~2-week template review, the 24-hour template invalidation, and the Partner Program tier thresholds (350 and 3,000).