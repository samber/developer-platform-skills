**Do not register 2.0.0. Do not rebuild from scratch.** Run `zapier-platform convert` on the existing integration and push the result as `1.3.0` in the same major line. Git, CI and releases come from the CLI, not from a new major version.

## 1. Assumptions
- Steps unknown. I assume every current step has live Zaps. Flag: Oakspire to list them.
- Auth scheme unknown. I assume no change is wanted.
- API webhook support, sort order and id stability unknown. They matter only when you later improve triggers.
- No deadline. I assume engineering days are limited, so the first CLI release changes no behavior.
- ~90 active users is your figure. I assume it counts this quarter's active users.
- You cannot see your users' emails. Zapier gives no list.

## 2. Stage and route
- Stage: public, 1.2.0 promoted, Platform UI, ~90 users.
- Route: Maintain, step 4. Classify the change first, then convert, test, canary, promote, migrate.
- Engineering's proposal fails this classification.
  - Zapier blocks user migration across majors: `1.9.0 → 2.0.0` never works†.
  - Every one of ~90 users would rebuild their Zaps by hand.
  - You cannot email them, so you could not warn them.
  - Your own channels (in-app, support, email) would carry the whole message.
- "Go back to the UI later" is also a trap.
  - UI → CLI is a `convert`, and users carry over through normal migration†.
  - CLI → UI has no conversion. Developer Support creates an empty version, you rebuild it by hand, and users cannot migrate to it†.
  - The undo button disappears once users run on a CLI version.
- Engineering's goals are git, CI tests and releases. All of them work on 1.x.

## 3. Step table

| Key | Label | Type | Change class | Reason |
| --- | --- | --- | --- | --- |
| each existing trigger, action, search | unchanged | unchanged | `keep` | `convert` must reproduce keys, input keys, output keys and shape exactly. |
| new integration registered as 2.0.0 | n/a | n/a | `rejected` | Users cannot migrate across a major†. |
| any later fix: renamed key, changed output, polling ↔ hook, new sort or id format | n/a | n/a | `additive` | Copy the step under a new key (`new_job_v2`), then `hide` the old one. |
| any step engineering wants to "clean up" now | n/a | n/a | `rejected` for 1.3.0 | Cleanup breaks live Zaps. Ship it later as an additive twin. |

Fill in real keys once you list the steps. 1.3.0 contains zero `additive`, `hide` or `breaking` rows.

## 4. Auth and trigger-type decisions
- **Auth:** keep the current scheme and field keys.
  - Changing the scheme, renaming an auth field or adding a required auth field is breaking†. It needs a new major.
  - Only that case could justify a 2.0.0, and ask Zapier about assisted connection migration first.
- **Trigger type:** keep each trigger's current type.
  - Flipping polling to instant is breaking†.
  - If you later want an instant trigger, add it as a twin under a new key. That needs a webhook subscribe/unsubscribe API that supports several live subscriptions. Answer 3 is unknown.
- **Sort order, page contents, id format:** do not touch them.
  - Each live Zap's dedupe memory holds the old ids.
  - A change would make the first poll fire every unseen item as new.

## 5. Publish checklist
Already public, so the eligibility rules are met. Items for this release:

| Item | Owner role | Week |
| --- | --- | --- |
| List all steps, auth scheme and live Zap counts per step | Ops lead | 1 |
| Run `convert --version 1.3.0-beta`; commit the project to git | Engineering | 1 |
| Pin `zapier-platform-core` exactly; set per-version env vars; CI on Node 22† | Engineering | 1 |
| Unit tests with `nock` mocks for every step; `validate` clean | Engineering | 1–2 |
| Hand diff against 1.2.0 (see §7) | Engineering + Ops lead | 2 |
| Name the Technical Contact; confirm the Integration Maintenance Program opt-in or out | Ops lead | 2 |
| Canary, promote, migrate | Engineering, Ops lead approves | 3 |

Total: about 3 weeks of calendar time. Engineering effort for `convert`, tests and diff is roughly 3–5 days, depending on step count. That is my estimate, not a platform number.

## 6. Growth actions ranked
1. Check whether public Zap templates exist for the top jobs. Moved by answer 4, which is unknown.
2. Embed the templates in help articles.
3. Add the Workflow Element in-product, once a public template exists. Moved by answer 5: no deadline means the compounding channel.
4. Silver tier needs 50 active users†. You are at ~90, so check your tier and health score before October's re-evaluation.

Do none of this inside the release. Growth follows the migration.

## 7. Versioning plan
**Target: `1.3.0`, the next minor of 1.2.0.** 1.2.0 is promoted and frozen, so you must clone, not edit.

1. **Convert.** Run `zapier-platform convert <path> --integrationId <id> --version 1.3.0-beta`, then `zapier-platform push`.
   - A labelled version lets you iterate. Users cannot migrate to it.
   - The project links to the same integration, so users carry over by normal migration.
2. **Test.** Add unit tests with `createAppTester` and `nock`, so CI needs no credentials. Run `zapier-platform invoke` on every step. Run `validate`.
3. **Hand diff against 1.2.0.** Promotion does not catch renamed or removed output keys, changed response structure or changed perform behavior. Check these:
   - step keys, input keys, output keys;
   - output structure per step;
   - polling sort order, page size, id format;
   - auth fields and the `test` call;
   - 401 handling and error messages.
4. **Push `1.3.0`.** Unlabelled versions push in sequence.
5. **Share** `1.3.0` with internal or friendly accounts using `users:add`.
6. **Decision gate: stop here and decide.**
   - If the CLI is too heavy, delete the CLI version and keep using the UI. Nothing is lost.
   - After promotion and migration, this exit is closed.
7. **Canary.** `zapier-platform canary:create 1.2.0 1.3.0 -p 10 -d 3600`: 5–10% for 30–60 minutes†. Stop if errors rise more than 5%†.
8. **Promote** 1.3.0.
   - Automatic migrations are on by default, so promotion itself moves a first group of users.
   - Do not promote until the canary is clean.
9. **Migrate** 5% first, then watch Monitoring. Then migrate the rest.
10. **Mark 1.2.0 legacy.** Do not deprecate it. Deprecation is only for a version that will stop working.
11. **From now on:**
    - Run `zapier-platform pull` before every push if the Maintenance Program is on.
    - Treat step keys and output shape as a public contract.
    - Ship changes as new minors in 1.x. Each breaking fix is an additive twin: new key, hide the old step, resubmit any template on the new key.
    - Cut a 2.0.0 only if something truly cannot ship additively, such as an auth scheme change. Plan for manual user migration then.

**To keep the CLI light for you:**
- Engineering owns the repo and CI.
- You own the Bugs & Feature Requests queue, Monitoring and the go/no-go on each release.
- Keep the project on the `convert` output. Add no custom middleware until a need appears.

## 8. Metric baseline

| Metric | Current value or where to read it |
| --- | --- |
| Active users this quarter | ~90 (your figure). Tier thresholds: Silver 50†. |
| Share of users on the promoted version | Unknown. Read it in the Developer Platform version page. |
| Activation within 24 hours, per step | Unknown. Read it in the Developer Platform. |
| Open bugs and feature requests, days to first response | Unknown. Read it in the Bugs & Feature Requests queue. |
| Zap run error rate | Unknown. Read it in Monitoring logs. |
| Templates live | Unknown. Check the Developer Platform. |

Run the first read before the canary. It becomes the baseline for the migration.

**†** Zapier platform number or rule from the skill's references. Verify against Zapier's live docs before quoting it to engineering or leadership.

**Next:** send me the list of step keys and the auth scheme. About 5 minutes. I will turn §3 into your real table.