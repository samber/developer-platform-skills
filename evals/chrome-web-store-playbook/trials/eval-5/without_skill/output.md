# Chrome extension publishing review: what to change

## Verdict

🔴 The current setup is one phishing click, or one departed employee, away from the Cyberhaven outcome. The extension has 80k mostly enterprise users, so a malicious update would reach corporate browsers, and enterprise customers will ask about this setup in security reviews.

For context, the Cyberhaven attacker phished a developer into approving a malicious OAuth app. That gave them publish rights, and they pushed a trojanized version in late December 2024. Password 2FA was on and didn't help, because the attacker never needed the password. Treat that as the threat model: stolen sessions and OAuth grants, not just stolen passwords.

## Do first (1–2 days, no new tooling)

1. **Treat the former engineer as an access holder.**
   - Whatever the intent, he knows the password. He may also hold the recovery email, the recovery phone, and the 2FA device.
   - If the TOTP secret is on his phone, he is still your second factor. If it's in the same 1Password vault, 2FA adds nothing.
2. **Take control of the Google account.**
   - Change the password and the recovery email and phone to company-controlled ones.
   - Re-enroll 2FA on company hardware, and sign out all sessions.
   - Review the account's Security page: third-party app access, app passwords, mail forwarding, and recent sign-ins.
   - Remove anything you don't recognize.
3. **Check what the live listing actually is.**
   - Compare the published version's contents and hash against what you intend to ship.
   - Check the version history for uploads nobody on the team made.
   - Confirm every collaborator or group on the publisher account.
4. **Inventory what else hangs off that Gmail.**
   - Likely items: the Google Cloud project for the Web Store API, Search Console domain verification, analytics, and support email.
   - Also check the public trader contact details. The EU trader disclosure may show his personal info.
5. **Route store notifications to a monitored company alias.**
   - Policy warnings and takedown notices must not land in a personal inbox.

## Fix ownership (within 2 weeks)

- **Move to a company-owned identity.**
  - Create the publisher on a Google Workspace account that you control. Use a role account such as `chrome-publisher@company`, not a person.
  - Prefer a Chrome Web Store group publisher backed by a Google Group. Membership then becomes an offboarding-aware list rather than a shared password.
  - Transfer the existing item to it. The item ID and install base must be preserved, so users keep getting updates.
  - ⚠️ Verify the exact transfer path and its limits in current Chrome Web Store docs or with developer support before you start. Do not delete or recreate the listing.
- **Stop sharing the password.**
  - A shared login has no attribution. After an incident, you can't tell who published.
  - Individuals should act under their own Workspace identities as group members. The shared credential then only exists for break-glass use.
- **Own the domain proof.** Make sure the verified website domain and its Search Console ownership belong to the company.
- **Name an owner and a backup.** Write them down. The point is that this never depends on one person again.

## Harden authentication (within 2 weeks)

- **Use phishing-resistant factors.**
  - Require FIDO2 security keys or passkeys for everyone who can publish. Don't use SMS or TOTP, which can be phished or relayed.
  - Enroll the publisher accounts in Google's Advanced Protection Program.
  - Keep two keys per person, plus one sealed spare.
- **Close the OAuth path.**
  - In Workspace admin, restrict third-party app access to an allowlist and block unreviewed consent grants.
  - This is the control that would have stopped Cyberhaven's vector.
- **Use a dedicated browser profile** for store admin. Don't read mail or browse there.
- **Run phishing training for the publishers.** Use the Cyberhaven lure as the example: a fake "Chrome Web Store policy violation" email asking for consent to an app.

## Replace laptop uploads with a pipeline (within 30 days)

1. **Build in CI from a tagged commit.**
   - Protect the release branch with required reviews, signed commits, and no force-push.
   - Use lockfiles with pinned dependency versions, and add dependency scanning.
   - Record the hash of the built zip.
2. **Publish through the Chrome Web Store API from CI.**
   - Use the narrowest credential available (service account where supported, else a scoped OAuth refresh token). Keep it in the CI secret store, never on a laptop.
   - Gate the publish step behind a protected CI environment that needs approval from a second person.
3. **Use staged rollout.**
   - Publish to a small percentage first and watch error and crash signals.
   - Expand only after that, so a bad build, malicious or not, doesn't hit all 80k users at once.
4. **Alert on drift.**
   - A scheduled job compares the live store version and hash to the last CI release.
   - Any version the pipeline didn't produce pages the on-call engineer.
5. **Revoke the old path** once CI works. The old publishing credentials get rotated, and the laptop flow is retired.

## Reduce blast radius in the extension

- **Keep permissions minimal.** Adding a permission in an update disables the extension until the user or admin re-approves. That friction is a useful tripwire, so don't pre-request broad host permissions.
- **Avoid remote code.** Manifest V3 already bans it. Keep a strict CSP, and don't load config that can change behavior without a review.
- **Review third-party dependencies** that run in the content script or service worker. The same account-takeover risk applies to your npm supply chain.

## Enterprise customer controls

- **Publish a security contact and a changelog.** Admins need to know what changed in each release.
- **Offer pinned or self-hosted deployment.** Admins can force-install from their own update URL and approve versions on their own schedule. Document the policy settings.
- **Give a signed release hash or SBOM** so customers can verify what they deploy.
- **Prepare an incident notice** that tells customer admins how to block a bad version quickly.

## Incident readiness

- **Write a runbook** for a hijacked publish: how to push a clean version fast, whom to contact at Chrome Web Store support, who tells customers, and who can approve all of this on a weekend. Cyberhaven's malicious build was live for roughly a day, and that is the window to beat.
- **Run a short tabletop exercise** once the pipeline is live.

## Suggested order

| When | Action |
|---|---|
| Day 1 | Rotate the credentials, recovery, and sessions on the current account. Audit the live listing and the OAuth grants. |
| Week 1 | Fix the notification alias, trader details, and domain ownership. Block unreviewed OAuth apps. Buy and enroll hardware keys. |
| Week 2 | Create the company-owned publisher group and transfer the item. Retire the shared password. |
| Weeks 3–4 | CI publishing with an approval gate, staged rollout, and drift alert. Retire laptop uploads. |
| Month 2 | Customer-facing security page, runbook, and tabletop. |

## Questions for your CISO

1. Is the departed engineer's exit documented, and does that include revoking his access to other shared vaults?
2. Do any customers require attestation of publisher-account controls? If so, the evidence should come from the new setup, not the old one.
3. Is the Chrome Web Store the only distribution channel, or are there also self-hosted or Edge and Firefox listings with the same weakness?

## Caveats

Chrome Web Store account transfer, service-account publishing, and staged-rollout specifics change over time. I haven't checked them against current docs in this session. Confirm each against the official Chrome Web Store documentation or developer support before you commit to the plan. The Cyberhaven details above are from memory of the public write-ups.