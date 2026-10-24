I didn't run `npm unpublish`, and I'd advise you not to run it either. The plan also can't work: 4.2.0 can never be republished.

## Why the plan fails

- **The version is gone for good.** npm never lets a `name@version` be reused, even after an unpublish, so you can't republish a fixed 4.2.0. Your customers' pins would then point at a version that no longer exists.
- **Installs would break.** Anyone with 4.2.0 in a lockfile or an exact pin gets an install error (ETARGET) instead of a working install. Tickets would go from "token refresh broken" to "can't install".
- **The unpublish rules may not allow it.** At five hours you're inside the 72-hour window. But it's only allowed if no public package depends on `@brightmoor/billing-sdk`, and an SDK may well have dependents.
- **I won't run it.** Unpublish is public and irreversible, and it has no dry run. The skill I'm following (`sdk-package-publishing`, Operating rule 2) bars me from running unpublish, deprecate and dist-tag moves. I prepare the commands and you run them.

## What to do instead

Roll forward in this order. Steps 1–3 are all you need from the train.

1. **Fix the bug and release 4.2.1 from CI.** Use a protected tag `v4.2.1` and your normal release pipeline. Keep the fix to the token-refresh bug only. The tag must equal the `package.json` version. Don't hard-code `--tag latest`. A higher stable version takes `latest` by default, so 4.2.1 will move it.

2. **Optional, if the fix will take hours:** point `latest` back at your last good version so new installs stop getting 4.2.0. Replace `4.1.X` with that version, and run this only if `latest` currently points at 4.2.0:

   ```sh
   npm view @brightmoor/billing-sdk dist-tags      # confirm latest = 4.2.0 first
   npm dist-tag add @brightmoor/billing-sdk@4.1.X latest
   ```

   Ranges like `^4.2.0` still resolve to 4.2.0 until 4.2.1 exists. This only protects bare `npm install @brightmoor/billing-sdk`.

3. **After 4.2.1 is live, deprecate 4.2.0.** Installs keep working but print a warning that names the fix. The warning is what reaches the pinned customers.

   ```sh
   npm deprecate @brightmoor/billing-sdk@4.2.0 "Breaks token refresh. Upgrade to 4.2.1."
   ```

   An empty message clears it if you need to undo this.

4. **Tell the three ticket owners to bump their pin to 4.2.1.** Exact pins can't be fixed from your side.

5. **Announce in the changelog and your advisory channel.** Say what broke, which versions are affected and which version fixes it.

If you have a staged-publish setup, 4.2.1 will wait for `npm stage approve <stage-id>`, which needs your 2FA. Approve it as soon as it appears.

## Hard deletion

Reserve unpublish for leaked secrets or malware. A token-refresh bug is neither.

## Run the commands from your terminal

I didn't run anything, so the repo and registry are untouched. Run the commands above yourself, either on the train once the connection holds or from the CI environment. If the connection drops during step 3, rerun it, because deprecate is safe to repeat. If you want, I can start on the 4.2.1 fix. Tell me where token refresh lives and I'll write a failing test first.