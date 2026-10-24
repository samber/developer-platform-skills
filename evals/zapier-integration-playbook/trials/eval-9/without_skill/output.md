**Do not rebuild from scratch. Do not ship 2.0.0.** Convert the existing app to a CLI project, keep every key identical, and ship it as a normal patch or minor version.

**First action (about 10 min):** run `zapier convert <app-id> ./oakspire-zapier` in a scratch directory. This generates a CLI project from your 1.2.0 UI app.

## Why not the proposal

1. **Rebuild plus 2.0.0 breaks your 90 users' Zaps.**
   - Zaps bind to trigger, action and field keys, to auth, and to dedupe IDs.
   - A hand-rebuilt app almost never reproduces them exactly. One renamed key means a broken Zap.
   - Users on 1.2.0 stay there until migrated, so you would be running a 90-user migration project for no new capability.
2. **A major version is a promise of breaking change.** Use it only when keys or behavior change on purpose. "New tooling" is not a reason.
3. **"Go back to the UI later" is probably not a real fallback.**
   - As far as I know, a UI app converted to CLI cannot return to the Visual Builder. Check Zapier's current convert docs before you commit.
   - Your real fallback is the old version. Keep 1.2.0 intact and never deprecate it early.
   - You can then migrate users back with `zapier migrate`. You cannot edit in the UI again.
4. **Maintenance load is the real risk.** "Too heavy for me" means a Platform UI person owns a Node codebase. Fix that with ownership, not with a rollback plan (see step 6).

## Plan

1. **Convert** (above). Commit the result as-is to a new repo. Do not refactor yet.
2. **Prove parity.**
   - Diff the generated definition against what the UI exports: triggers, actions, field keys, auth.
   - Add `zapier test` unit tests with recorded fixtures for each trigger and action.
   - Verify the auth flow end to end on a test Oakspire account.
3. **Set up CI.**
   - Run lint, tests and `zapier validate` on every PR.
   - Store a deploy key as a CI secret, not on a laptop.
   - Run `zapier push` from a tag only.
4. **Push as a new version, not 2.0.0.**
   - Use 1.2.1 if behavior is identical, or 1.3.0 if you add something non-breaking.
   - Push it private first. Test it with a few of your own Zaps.
5. **Roll out gradually.**
   - Promote, then run `zapier migrate 1.2.0 1.2.1 <percent>`. Start at 5–10%, wait a few days, then go to 100%.
   - Watch the Zapier error dashboard and support tickets between steps.
   - Public-app promotion can involve Zapier review. Allow days for that, not hours.
   - Keep 1.2.0 undeprecated for at least a month after 100%.
6. **Split ownership.**
   - Engineering owns the repo, CI and releases.
   - You own the product: which actions exist, field copy, and priorities.
   - Add 2 engineers as collaborators on the Zapier app. This kills the bus-factor risk and the "too heavy" worry.
7. **Use 2.0.0 later, only if you want it.** Once the repo is stable, a real breaking cleanup (rename keys, drop old actions) can ship as 2.0.0. Add a migration guide, and use a staged `zapier migrate`.

## Effort

- Steps 1–3: about 1–2 engineer days.
- Step 4: about 1 hour.
- Step 5: about 1–2 weeks of calendar time, mostly waiting and watching.
- A from-scratch rebuild plus a forced migration of 90 users: several weeks, with real support-ticket risk.

## What to tell engineering

"CLI plus git plus CI, yes. Same app, same keys, converted not rebuilt. Next version is 1.2.x. We save 2.0.0 for an intentional breaking change."

## Caveat

I did not check Zapier's current docs here. Confirm three things before step 1: the `zapier convert` behavior, that the conversion is one-way, and the promote and migrate rules for public apps.

**Next (2 min):** open Zapier's "convert an app" docs page and check the one-way and migration notes.