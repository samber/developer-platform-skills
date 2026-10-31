# Shipwell Labels: auth bypass and blocked 3.4.1

**Do not close the plugin. Ship 3.4.2 with the fix and the blocked release's findings resolved.** The directory cannot put a fix on customer sites within the hour, so use your own service for that hour.

## Assumptions (tell me if wrong)

- The bypass exists in 3.4.0 and 3.4.1, so every site is exposed today.
- Sites currently run 3.4.0 or earlier, because 3.4.1 was blocked and never reached them.
- You haven't sent me the block email, so I don't know the findings. They may be the same bug the reporter found.

## Why not close it

- ❌ Closing is meant to be permanent, not a pause. Reopening needs a full review against current standards, and that review has no guaranteed speed.
- ❌ Above 10,000† users, closing needs a written request to the Plugins Team.
- ⚠️ Closing doesn't remove the vulnerable code from 40,000 sites. My inference is that it also stops the fix from reaching them through core updates. Confirm this with the Plugins Team.
- You also lose search rank, installs and forum history for nothing.
- ✅ Tell the CTO that a block is not a closure. The listing stays up, and the fix goes out as a new version.

## Why the directory can't do it in an hour

- Every release waits a 6-hour† cooldown while the automated security review runs.
- A high score blocks that version, and sites keep the previous one. That is what happened to 3.4.1.
- Release Confirmation's 24-hour† delay holds back automatic updates only. Don't pick the delay for this release, and be at your keyboard to click the emailed confirm link.
- Realistic outcome: the fix is on sites with auto-update on about 7 to 24 hours after you commit. Sites without auto-update stay exposed until an admin updates.

## Next 60 minutes

1. **Mitigate in your service.** The plugin is a connector, so your API sees every request.
   - Reject or neutralise the vulnerable request path server-side.
   - Rotate or revoke any tokens or API keys the bypass could expose.
   - Check logs for exploitation.
   - Ask your WAF or a virtual-patch vendor for a rule if you have one. Treat that as an extra layer, not the fix.
2. **Warn customers through the service.** The plugin already displays messages your API returns, so push an urgent "update to 3.4.2 / contact us" notice that way.
   - Email affected customers.
   - Publish a plain zip of the fixed version on your own site for manual install. This is fine, but never add a custom updater or remote installer to the directory plugin.
3. **Read the 3.4.1 block email and sort the findings.**
   - Compare each finding to the reported bug. Fix any that match.
   - Fix every other finding too, or restructure the code so the scanner stops flagging it. A rewrite is faster than an appeal.
   - Reply to the email only for a clear false positive, and expect the reply to be slower than a new release.
4. **Build 3.4.2 and test the bypass fix.** It must contain:
   - the auth fix;
   - the fixes for the 3.4.1 findings;
   - the 3.4.1 changes, since 3.4.1 never shipped.
5. **Run Plugin Check, Security category included.** It runs again on the shipped update, so a failure here predicts a second block.

## Release (one clean push)

1. Bump `Version` in the main file and `Stable tag` in `trunk/readme.txt`. `Stable tag` must be a real tag, never `trunk`.
2. Write a generic changelog line such as "Security fix". Publish no exploit details until most sites have updated.
3. Deploy from CI with the account's SVN password. Commit `trunk/`, then copy it to `tags/3.4.2`.
4. Make one commit, not rapid-fire ones. Commits made to look recent break Guideline 14.
5. Confirm the Release Confirmation email immediately.
6. Watch the committer inbox for a block notice during the 6-hour† window.
7. If 3.4.2 is blocked, fix the findings and ship 3.4.3. Don't wait on a reply.
8. Make sure a human reads that inbox. Auto-replies after warnings can close every plugin the account owns.

## If the CTO still wants a Plugins Team contact

- Email plugins@wordpress.org (verify the address) with the vulnerability summary and a request to expedite the 3.4.2 review.
- Queue jumping is allowed only for security or legal issues, and this qualifies.
- Ask for the force-update question there too. I can't confirm from the playbook that the team will push a fix to sites, so don't promise customers it.
- Don't ask for closure. Ask for help getting the fix out.

## Obligations at risk

- Any clear in-plugin lock or telemetry added in the rush reopens review. Keep the patch minimal.
- Forum support stays for the free plugin only. Point questions about the incident to your own channel, and pin one forum notice.
- Never ask for reviews, or seed them, to offset bad press.

## Measure to watch

- Share of active installs on 3.4.2, tracked daily.
- Connected sites as a share of active installs.
- No block notice for 3.4.2, and the resolved-thread share for incident threads.

† Verify against the current developer.wordpress.org handbook and make.wordpress.org/plugins; the release process changes often.

**Send me:** the 3.4.1 block email and the reporter's description. I'll map each finding to the bypass and say which are likely real.