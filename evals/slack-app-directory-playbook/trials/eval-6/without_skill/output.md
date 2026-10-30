Do not do both changes together. Disable distribution first, if you disable it at all. Token rotation comes last, and only after a staging dry run. It is hard to undo, and you have nobody to catch the fallout.

I could not check Slack's current docs here. The ⚠️ items below are my best recollection, so verify each one.

**Next action (10 min):** open the app's settings page at api.slack.com/apps, then **Manage Distribution**. Screenshot it and check the support email and URL on the listing. That address now goes to nobody.

## Sequence

1. **Stabilize first (day 0–1)**
   - Roll back or hotfix the bad release. Distribution and rotation change nothing about the current uninstall rate.
   - Check for a pattern in uninstalls. Subscribe to `app_uninstalled` and `tokens_revoked` if you have not already.
   - Note the uninstall workspaces and their admin contacts, if you store them. A short apology email may win some back.

2. **Clear the ticket backlog (day 0–3)**
   - Name one temporary owner, such as an engineer on rotation or a founder. Do not leave the queue ownerless.
   - Set an auto-reply stating the rewrite and an expected response time.
   - Triage by severity. Answer anything involving data loss or broken installs first.

3. **Decide whether to turn off public distribution at all (day 1–3)**
   - ⚠️ If the app is in the Slack Marketplace, you probably cannot flip a toggle. Removal likely goes through Slack, and relisting may need a new review. A month away may cost your listing and ranking.
   - ⚠️ Check whether workspaces that already installed keep working. Test on a throwaway workspace or ask Slack support. Never assume.
   - Your actual goal is likely "no new installs while the product is unstable". A banner on your site and a notice in the listing description reach that goal without risking the listing.
   - If you do disable it: announce it to existing customers first, pause install links on your site, and write down how to re-enable it.

4. **Do the rewrite against a separate dev app**
   - Use a separate Slack app ID for rewrite testing. Do not mutate the production app's config.
   - Existing installs are tied to the production app ID. A new production app means every customer reinstalls, so keep the production ID.

5. **Token rotation: enable only on a staging copy first**
   - ⚠️ Opting in is, as far as I know, irreversible for that app, and it affects the whole app, not one workspace.
   - ⚠️ Tokens then expire after about 12 hours and must be refreshed through `oauth.v2.access` with the refresh token. Each refresh token is single use, so concurrent workers can race and lose the pair.
   - ⚠️ Existing long-lived tokens need to be exchanged (`oauth.v2.exchange`) to become rotating ones. Confirm whether old tokens keep working until you exchange them.
   - Build and test in the rewrite: a token store with locking, refresh before expiry, handling of `invalid_refresh_token`, and an alert on refresh failures.

6. **Production rotation rollout (after the rewrite is stable)**
   - Ship the refresh code first, while the app is still on long-lived tokens.
   - Opt in at a low-traffic time with someone on call.
   - Exchange tokens in batches, starting with a few internal or friendly workspaces. Watch the failure rate for a day before the full batch.
   - Never run this while the support queue is unstaffed. A broken refresh looks like a silent outage and causes the exact uninstall wave you are trying to recover from.

7. **Reopen distribution** only after one week of clean metrics: refresh failures near 0, uninstall rate back at baseline, and the backlog empty.

## Why this order

- Rotation is the only irreversible step, so it goes last, after a dry run.
- Disabling distribution is the riskiest for revenue. Verify the Marketplace consequences before you do it.
- Staffing comes before both: with no support engineer, a silent token failure goes unseen for days.

**Open questions for you:** Is the app in the Slack Marketplace, or only distributed by install link? How many workspaces are installed, and is the token store single-process or multi-worker?