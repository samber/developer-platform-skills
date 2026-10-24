Next action: revoke the leaked token at both registries now. Do fire 1 before fire 2.

## Fire 1: leaked publish token (about 2 hours to contain, 1 day to audit)

Treat the token as compromised. It sat in a public log for three weeks. Log deletion does not help, because scrapers and forks keep copies.

1. **Freeze releases and revoke (10 min).**
   - Marketplace: revoke the Azure DevOps PAT behind it, under User settings, Personal access tokens.
   - Open VSX: delete the access token in your open-vsx.org profile.
   - Revoke before investigating. CI publishing breaks for a while, and that is acceptable.
2. **Snapshot evidence (10 min).**
   - Save the leaking run's log and its URL.
   - Export the version list and timestamps for both registries.
   - Then delete the run log (repo admin) to stop further exposure.
3. **Find why masking failed (30 min).** GitHub masks secrets in logs. A printed token usually means one of these:
   - `set -x` or a debug flag
   - the value was transformed (base64, split, URL-encoded) before printing
   - the token was written to a file and then printed
   - a tool echoed its own config

   Check which workflow change introduced it. Also check whether any `pull_request_target` or fork-PR path can reach the secret.
4. **Audit the last 3 weeks, and ideally all history (2 to 4 hours).**
   - Match every published version against a CI run and tag.
   - Download each VSIX from both registries and diff it against a rebuild from the tag.
   - Check the Azure DevOps org audit log for PAT creation and use.
   - Check the publisher and namespace members and tokens for anything you did not add.
   - Check listing metadata, dependencies, and extension-pack entries.
   - "Nothing odd in the publish history" is weak evidence. An attacker can wait, or publish under a different ID.
5. **Check what else leaked.** Scan the same log, and the org's Actions logs, with gitleaks or trufflehog. Rotate any other secret that job could reach.
6. **Issue new tokens (1 hour).**
   - Use one token per registry, never a shared one.
   - Limit each to the publish scope only. Set a short expiry, 90 days or less. For Marketplace, use a specific org rather than "all accessible organizations".
   - Create them from a dedicated bot account holding the lowest role that can publish, not from an Owner account. Verify which role that is.
   - Store them as secrets in a protected environment with required reviewers, restricted to the tag or main branch, on the one repo that publishes. Do not use org-wide secrets.
   - Pin third-party actions by SHA.
7. **Review the Owner account.** The old token inherited that account's reach. Check its other PATs, its 2FA, and its sessions.
8. **Decide on disclosure.**
   - If the audit shows a malicious or unexplained publish, unpublish it, report to Microsoft and Open VSX security, and notify users.
   - If the audit is clean, write an internal incident record.

## Fire 2: community extension (this week, after step 4 above)

Do not file the takedown or send an uninstall notice yet.

- **Sequencing.** If the audit finds your own listing was tampered with, pointing users to your official extension is unsafe.
- **Weak grounds.** A broken, unmaintained community extension is not a Marketplace policy violation. Takedown needs impersonation, trademark misuse, or malware. Using your product name to describe compatibility is likely allowed. Check Microsoft's current abuse and IP claim process before promising Support an outcome.
- **The break is yours.** The v2 API change broke it. Check whether you gave a deprecation window.

Sequence:

1. **Open a public issue or PR on the extension's repo** with a v2 fix. Two emails over six weeks is a thin record. A PR fixes the problem, or gives you a documented non-response.
2. **If the license allows, fork or adopt it** and ship an official extension. Use VS Code `SecretStorage` for the key, not `settings.json`. Offer scoped, read-only keys if you do not have them yet.
3. **Publish an official note for the 9,800 users.**
   - The extension is not affiliated with Quarrystone, and it breaks on v2.
   - Link the official alternative.
   - Advise moving keys out of `settings.json`. Rotate the key if Settings Sync or dotfiles exposed it.
   - Do not say "uninstall" before an alternative exists.
4. **File a takedown only if all three hold:** your official extension is live, the name causes real confusion with your brand, and the maintainer ignores a third contact. Claim trademark or impersonation, not "broken".

Next: do step 1 now, then paste the leaking workflow step and I'll find the masking failure.