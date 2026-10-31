# Notewise release check: `tabs` + `https://*/*` + storage v2

**Don't push this to everyone on Friday.** The manifest change and the storage migration are each risky on their own. Together they could disable the extension for 42,000 users and leave no safe way to roll back.

Figures marked † are practitioner-reported or may have changed. Check them against current Chrome Web Store docs before you rely on them.

## Assumptions

I couldn't ask, so I assumed:

- "Capture from any tab" runs after a user action, such as a click on the toolbar icon, a shortcut, or a context menu.
- Notewise has no broad host access today.
- Users are mostly self-serve, with some managed fleets possible.
- The new version hasn't been submitted yet.

If any of these is wrong, tell me. The first one matters most.

## 1. Permissions: the biggest risk

### Problems with the manifest as drafted

**Required `https://*/*` triggers a disabling warning.**
- A new permission with a new install warning disables the extension for every existing user until they accept it.
- The warning would read "read and change all your data on all websites". Expect churn, and expect support tickets from people who never notice the extension went off.
- Broad hosts also get the slowest and most in-depth review.

**`tabs` beside broad host access is the textbook Purple Potassium rejection.**
- Host access already exposes `url` and `title` for matching tabs, so `tabs` is redundant.
- `tabs` adds its own "read your browsing history" warning.
- Reviewers assume you use every permission, so an unused one gets rejected.

**Broad hosts are justified only when the single purpose spans every page.** Notewise captures from pages the user chooses. That is a click-triggered feature, not a page annotator.

### What to ship instead

Use the narrowest layer that works. These are ranked by review speed and install conversion per unit of engineering.

| Rank | Layer | Use when |
|---|---|---|
| 1 | `activeTab` alone, with no `tabs` and no host permission | Capture is triggered by a click or shortcut on the current tab. This probably covers most of the feature. |
| 2 | `optional_host_permissions: ["https://*/*"]`, requested with `permissions.request` from a user gesture (an "Enable capture from any tab" button), then `scripting.registerContentScripts` | You need to capture a non-active tab, or run without a click on pages the user picks. |
| 3 | Required `https://*/*` | Only if the single purpose truly spans every page. Justify it in writing. You will get the slowest review and the scariest warning. |

Optional permissions don't disable anyone on update. Only users who press Enable see a prompt. Promote a permission to required only in a later major version, after testing the upgrade by packing two CRX versions locally.

Managed fleets need separate handling:
- Force-install grants required permissions silently.
- Optional hosts still prompt each user.
- Users on a force-installed fleet can't disable or remove the extension.
- Test on a managed profile.

### Permission-to-feature map for the submission

| Permission | Required or optional | Feature | API calls | Dashboard justification |
|---|---|---|---|---|
| `activeTab` | required | "Capture from this tab" | `scripting.executeScript` or `tabs.captureVisibleTab` on click | Reads the current page only when the user clicks Capture. |
| `https://*/*` (only if rank 2) | optional | Capture from any tab | `permissions.request` from settings | Requested only when the user enables capture from other tabs. |
| `tabs` | **drop it** | None | None | None |

Write how the extension uses each permission, never what the permission does. Delete any row with no shipped feature.

## 2. Privacy tab and policy must match the new code

Capturing page content or URLs counts as browsing activity. Before you submit:

1. Update the **single purpose** sentence so it still names one narrow focus. It must cover capture.
2. Write one justification per permission, naming the user-facing feature.
3. Tick every data type the code now collects, stores locally, or transmits. That includes captured page content and URLs, and `chrome.storage.sync` if you use it.
4. Update the privacy policy at its live URL. If it's silent on captured data, you risk **Purple Lithium**.
5. Disclose and get consent before first capture (**Purple Nickel**). Send data only over HTTPS (**Purple Copper**).
6. Collect page URLs only for the user-facing feature the listing describes (**Purple Magnesium**).
7. Re-certify the Limited Use statement. It must be published on your own site.

Update the listing description too. A mismatch between code, Privacy tab, and listing is itself a rejection reason.

Add a **test instructions** block that tells the reviewer how to trigger "capture from any tab". Give it a permanent seeded demo account with no SSO or MFA, and a recording link. A reviewer who can't reach the feature returns **Yellow Magnesium**.

## 3. Storage v1 → v2 with old keys deleted: not rollback-safe

Rollback republishes the previous version, which is v1 code, under a new version number. It takes minutes and needs no review. During a partial rollout, rollback returns to the last version published to 100%, which may be two versions back.

If v2 has deleted the v1 keys, a rollback leaves v1 code looking at empty storage. Users look like they've lost their notes. `chrome.storage.local` is per-profile, so there's no server-side copy to restore from unless you sync.

### Make the migration two-phase

1. **Release N (this one):**
   - Write v2 data under new keys.
   - Keep the v1 keys untouched.
   - Store a `schemaVersion` marker.
   - Make the migration idempotent: re-running it must produce the same result.
   - Run it from `runtime.onInstalled` and again on startup if the marker is missing.
   - Wrap it in try/catch so partial failure leaves v1 intact.
   - Verify the v2 write by reading it back before setting the marker.
2. **Release N+1 or later:** delete the v1 keys only after N is at 100% and has been stable for at least one more release cycle.

### Migration cases to test

Test these on real profiles, not only unit tests:

- Fresh install.
- v1 with a large dataset, to check the `chrome.storage.local` quota. Watch for quota errors, since old and new copies coexist.
- Empty v1.
- Corrupt or half-migrated v1.
- A user who skips versions and goes from older than v1 straight to v2.
- Two browser windows or a service-worker restart mid-migration.
- Rollback to v1 after migration. It must still see its own keys.
- Roll-forward again after rollback. The migration must not duplicate data.

## 4. Rollout: don't hit "everyone on Friday"

You have about 42,000 weekly users†. Partial rollout needs over 10,000 seven-day active users†, so you qualify.

1. **Submit now.**
   - Google says review takes a few days to a few weeks†.
   - Queues reached 3-4 weeks† in April 2026.
   - Broad hosts and a Privacy tab change make a slower review likely.
   - Friday is a hope, not a date.
2. **Untick auto-publish.** An approved build waits up to 30 days†, then reverts to draft. Publish it yourself on a day you choose, early in the week and early in the day, not on Friday with nobody watching.
3. **Set a partial rollout before submitting.**
   - Start at a small percentage and raise it in steps.
   - Raising the percentage needs no review.
   - Do one rollout at a time.
   - Watch error rates, support tickets, and uninstall rate between steps.
4. **Don't cancel and resubmit** if review runs long. Cancelling reset the queue position, per 2026 reports†. Escalate to support after about three weeks†.
5. **If rejected,** fix every cited point in one resubmission. Appeal each violation once, with the map row, code references, and a screen recording.
6. **Rollback runbook:**
   - Write down who decides and who clicks.
   - Rollback discards any pending submission.
   - Check that rollback works with storage v2 data present (section 3).
   - Don't plan a rollback you haven't tested.
7. **Dates:** if approval might miss a fixed announcement date, say "coming soon". Don't announce a date you don't control.

## 5. Account security (quick check)

- Turn on Verified CRX Uploads. CI then uploads signed CRX files instead of zips, and the key lives in CI secrets or an HSM, not the Google account.
- Publish from CI with a dedicated service account, not a person's OAuth token.
- Alert on any published version CI didn't produce.
- Restrict third-party app access in your Workspace. A phished employee granting OAuth publish access caused the December 2024 incident.

## What to do, in order

1. Answer the assumptions above, especially whether capture is click-triggered.
2. Drop `tabs`. Move to `activeTab` or optional host permissions.
3. Rework the migration so v1 keys survive this release. Test rollback on a v2-migrated profile.
4. Update the single purpose, justifications, data types, privacy policy, and test instructions.
5. Build, submit with auto-publish off and a partial rollout set, and track the review queue.
6. Publish once approved, early in the week. Ramp the percentage while watching metrics.
7. Delete the v1 keys in a later release.

Send me the current manifest and the capture code path, and I can write the exact permission map and Privacy tab answers.