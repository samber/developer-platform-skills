# Shipwell Labels auth bypass: response plan

**Don't close the plugin.** Ship a patched version now and ask the plugin team to push it.

## Why not close it

- Closing doesn't touch the 40,000 installed copies. They stay vulnerable.
- A closed plugin normally drops out of the update feed, so sites can't receive your fix. Confirm this with the plugin team, but assume it.
- Reopening is at the team's discretion, so "a couple of days" isn't yours to promise.
- The only gain is blocking new downloads. A patched 3.4.2 does that better, because new installs get the fix.
- If the CTO still wants a closure, ask the plugin team to close only if you can't ship a fix within hours.

## What "within the hour" can and can't mean

- **You can control:** the patch committed, tagged and live in the directory, usually within minutes of the stable-tag change.
- **You can't control:** sites pick up updates when WordPress checks, roughly every 12 hours. Auto-updates are off by default.
- **The lever:** the plugin team can force a security update to installed sites. Ask for it explicitly.

## Next 60 minutes

1. **Email plugins@wordpress.org now.** Use "Security: auth bypass in shipwell-labels, patch ready by HH:MM". Say you're fixing it, ask for a forced update when 3.4.2 is out, and ask them to confirm how the blocked-3.4.1 notice affects 3.4.2. Don't put exploit details in a public place.
2. **Patch the bypass minimally.** Fix only the auth check, with no refactor or unrelated changes. Write a failing test that reproduces the bypass, then make it pass. Check every sibling endpoint that uses the same permission pattern (REST routes, AJAX actions, admin-post handlers).
3. **Release as 3.4.2.** Update the version header, `readme.txt` stable tag and changelog. Commit to trunk, copy to `tags/3.4.2`, and run Plugin Check first so you don't trigger another block.
   - Keep the changelog vague: "Security: hardened authorization checks." Add no details until most sites have updated.
   - SVN diffs are public, so speed matters more than secrecy here.
4. **Add virtual patching in parallel.** Send the details to Patchstack and Wordfence, who can ship WAF rules to their users before sites update. If you have a managed-hosting or Cloudflare contact, ask for a rule there too.
5. **Tell the reporter.** Confirm the fix timeline and agree a disclosure date. Request a CVE through Patchstack or Wordfence, or MITRE.

## The "blocked from distribution" email

1. **Verify it before acting.** Check that the sender and headers are genuinely from wordpress.org. Don't click links. Look at your plugin's admin page and the live version. Phishing that imitates the plugin team is common right after an incident.
2. **If it's real, read each finding.** Reply in the same thread with a short, specific rebuttal per false positive.
3. **Don't wait for the dispute.** Fix cheaply anything that's easy to silence or clarify, even if it's a false positive, and include it in 3.4.2. Then ask the team to review 3.4.2 as a priority security release.
4. **Check whether 3.4.1 is the vulnerable version.** If it is, the block may be limiting who receives it. Say so in your reply.

## After the patch

- **Hunt for exploitation.** Check logs for unauthenticated hits on the vulnerable endpoint. Look for new admin users, changed options and unexpected files on your own sites.
- **Publish an advisory after a delay.** Wait 1–2 weeks, or until most installs have updated. It should list the affected versions (up to 3.4.1), the fixed version (3.4.2), the CVE, and a recommendation that site owners audit their admin users.
- **Add a regression test for the bug class**, and permission checks to code review.

## Open questions

- Which versions are affected? Is it only 3.4.1, or older ones too?
- Does the bypass need any plugin setting or special configuration to be exploitable?
- Who has SVN commit access right now?

Your answers change step 2 and the advisory wording. I can draft the plugin-team email or the advisory if you want.