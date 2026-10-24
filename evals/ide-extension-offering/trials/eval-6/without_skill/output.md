**Next action:** list who holds publish credentials for all three channels (Marketplace PAT/Azure DevOps, Open VSX token, JetBrains token). The only maintainer left, so nobody may have access. Everything below depends on it.

# Deprecation plan: `fernhollow.fernhollow-login`

## Change to your plan: deprecate, don't unpublish

- Unpublishing hides the listing. It does not touch the 18k installed copies.
- Those users keep a dead extension and get no notice and no pointer to `fernhollow-tools`.
- Unpublishing also deletes the one place you can show a replacement link.
- Mark it deprecated with the new extension as replacement. Keep the listing up.
- Check the exact mechanism per channel before Friday:
  - VS Code Marketplace: deprecate option in the publisher portal.
  - Open VSX: the deprecated and replacement fields.
  - JetBrains: your plan skips it. It is the third channel, so it needs the same treatment.

## Other gaps in the plan

- **Date.** Today is Sat 2026-10-24. "Next Friday" is 2026-10-30, six days away. That is too tight for the steps below.
- **Newsletter order.** The newsletter lands after removal. Users would find out after the extension vanished. Announce first.
- **Replacement must be live first.** `fernhollow-tools` has to ship and pass a cold test before the old one is touched.
- **No maintainer.** Someone must own the final release and the security-fix window.
- **Auth.** The extension handles CLI sign-in. A dead extension holding a login flow is a security liability, so plan a revocation step.

## Phases

Define T0 as the day `fernhollow-tools` goes live.

**Phase 0: prep (before T0, about 3 to 5 days)**
1. Confirm credentials and build access for all three channels.
2. Name an owner for the sunset period. State who gets security reports for the old extension.
3. Write a parity table: each job of the old extension, its replacement, and any job with no replacement. Jobs are CLI sign-in and tenant config. Replacements are VS Code built-in auth and the MCP server.
4. Run a cold test. A dev who did not build it follows only the guide: sign into the CLI, then read and edit tenant config. Publish the measured time, not a guess.
5. Find out what telemetry exists on active users of the old extension. Installs are not active use.

**Phase 1: announce (T0)**
1. Publish `fernhollow.fernhollow-tools` on the Marketplace, Open VSX and JetBrains (if a plugin exists for it).
2. Ship a final `fernhollow-login` release:
   - One-time notification on activation: what changed, a link to the migration guide, and an install button for the new extension.
   - Add a "don't show again" action.
   - The install button can call the VS Code `workbench.extensions.installExtension` command with `fernhollow.fernhollow-tools`.
   - Update the README and listing description with the sunset date.
3. Mark the old extension deprecated on all channels, with the replacement set.
4. Publish the migration page at one stable URL.
5. Send the newsletter. If it is not due at T0, send a short dedicated email to registered tenants instead. Do not wait.
6. Add a deprecation message in the CLI wherever the editor sign-in flow is used.

**Phase 2: sunset window (T0 to T0+90 days)**
1. Security fixes only. Say so in the README.
2. Track weekly: active users of old vs new, tickets quoting the migration, and migration page visits.
3. Remind in the T0+30 and T0+60 newsletters.
4. Don't enforce hard cutoffs until the adoption curve flattens. Long tails are normal. Work the last ~15% by name where you can identify accounts.

**Phase 3: end (T0+90 days or later)**
1. Revoke the OAuth client or redirect that the old extension uses. Check what it uses first.
2. Leave the listing deprecated. Unpublish only if it becomes a security risk.
3. Archive the repo with a pointer to `fernhollow-tools`.

## Success measures

- Share of active users on `fernhollow-tools` at 30, 60 and 90 days.
- Migration tickets per 1,000 users, and which step causes most of them.
- Named stragglers at T0+90.

## Questions only you can answer

1. Does telemetry exist for the old extension, or only install counts?
2. Does a JetBrains plugin ship the same features, or is it a separate product?
3. Is the CLI sign-in flow tied to a dedicated OAuth client that you can revoke?
4. When is the next newsletter? If it is after T0, do you accept a separate email?
5. Would you rather keep the old extension ID and replace its content? That carries all 18k installs with no migration. You chose a new ID, so I assumed that stays.

**Next:** answer question 3 and run the credentials check. Both gate Phase 0.