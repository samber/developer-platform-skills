Don't ship Friday to 100%. Cut the permission scope first, then stage the rollout on Tuesday or Wednesday.

Two things can hurt you here: the permission increase, and the irreversible storage delete.

## Must fix before release

1. **Check whether you need `tabs` and `https://*/*` at all.**
   - Existing users get a new permission warning. Chrome **disables the extension** until each user re-accepts it.
   - `https://*/*` shows as "Read and change all your data on all websites". `tabs` shows as "Read your browsing history".
   - Expect real churn at 42k users. Some will never re-enable it, and ratings will drop.
   - If capture starts from a user click, shortcut or context menu, `activeTab` covers it with no warning. It grants temporary access to the current tab and works with `chrome.scripting` and `tabs.captureVisibleTab`.
   - `tabs` is only needed to read `url`, `title` or `favIconUrl` of other tabs. `chrome.tabs.create` and `query` work without it.
   - If you need broad access, put it in `optional_host_permissions` and call `chrome.permissions.request` at first use. Existing users then see no warning and are not disabled.
   - `https://*/*` does not cover `http://` sites. Confirm that matches your intent.
2. **Make the migration non-destructive.**
   - The Web Store has no rollback. A fix means a new, higher version number, and users already on v2 have lost their v1 keys.
   - In release N, write v2 keys, verify them, then set a `schemaVersion` flag. Keep the v1 keys.
   - Delete the v1 keys in release N+1, once you see no migration errors.
   - Do the v2 write in one `storage.local.set` call. Several calls can be interrupted partway.
3. **Don't rely on `onInstalled` alone.**
   - The service worker can be killed mid-migration, and `onInstalled` will not fire again.
   - If the user was disabled by the permission prompt, `onInstalled` may also be missed on re-enable.
   - Run an idempotent "if `schemaVersion` < 2, migrate" check at every worker startup.
   - Make the popup and content scripts wait for that check before they read storage.
   - Users who skip versions must still migrate. Handle v1, missing or corrupt data, and an already-v2 state.
4. **Check the storage quota.**
   - `chrome.storage.local` is capped at 10 MB unless you declare `unlimitedStorage`.
   - v1 and v2 coexist during migration, so heavy users can hit `QUOTA_BYTES` and the write fails.
   - Check `getBytesInUse` first. Surface the failure and keep v1 intact when it fails.
5. **Plan for a slower Web Store review.**
   - Broad host permissions trigger in-depth review. That can take days, or get a rejection.
   - Submit early. Fill in the permission justifications and the privacy disclosures in the dashboard.
   - Update your privacy policy to say what capture reads and where it goes. Page content counts as user data under the Limited Use policy.
   - Use deferred publishing so approval does not auto-publish on a Friday night.

## Should do

- **Staged rollout:** Use the Web Store percentage rollout. It needs more than about 10k weekly users, and you have 42k.
  - Go 1%, then 5%, then 25%, then 100%, with at least 24 hours between steps. Pause if numbers look wrong.
  - 1% is about 420 users, enough to expose migration bugs.
- **Test the upgrade path:** Install the current store version with realistic v1 data. That means a large dataset, odd values, and an empty profile. Then update to the new build and diff the storage. Kill the worker mid-migration and confirm it recovers.
- **Add migration telemetry:** Log success, failure and error code only, with no content. Without it you learn about failures from one-star reviews.
- **Prepare a hotfix:** Have the next version number, a build, and a support reply ready before you push.
- **Explain the permission:** Put a changelog line and a store-description note on why the extension needs it. Show a short in-product message once the user re-enables it.
- **Check enterprise installs:** Admin allowlists or blocklists of permissions (`ExtensionSettings`) can block the update for managed users.

## Timing

- The code changes (`activeTab` or optional permissions, a two-phase migration, the startup check) take about half a day to a day.
- Review and staged rollout add about 3 to 7 days.

## Next action

Open `manifest.json` and list every place capture reads another tab's `url` or `title`. If there are none, drop `tabs`. Then answer one question: is capture always user-initiated? If it is, use `activeTab` and drop `https://*/*` too.