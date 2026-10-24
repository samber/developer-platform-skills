Revoke the shared publish token now, then deal with the community extension. Do **not** file the takedown yet.

Status: provisional. Assumptions are at the bottom.

## Fire 2: leaked publish token (first, about 4 hours of work)

**Hour 0 to 1: stop the bleeding**
1. **Revoke** the Marketplace token. In Azure DevOps, go to User settings, then Personal access tokens, on the Owner account that created it.
2. **Revoke** every other PAT on that Owner account too.
3. **Delete** the Open VSX token (profile, Access Tokens).
4. **Delete** the org secret.
5. Prove revocation with a probe that can fail:
   - Run `vsce verify-pat` and `ovsx verify-pat` with the old token. Pass it by env var, never as an argument.
   - Require an exact auth failure (401).
   - Run a positive control with a known-good credential first. A network error or crash proves nothing.
6. Save a private copy of the leaking run's log, then **delete the run's logs**. Deleting does not un-leak. Treat the token as copied.

**Hour 1 to 3: audit.** "Nothing looks odd in the publish history" does not clear you.
- The token came from an Owner account, so it may have done more than publish. Check these:
  - Marketplace publisher members: remove any member you don't know. CI must be Contributor only.
  - Open VSX namespace members and tokens.
  - The Owner account's sign-ins and the org audit log, if auditing is on.
- Map every version on both registries to a CI run or tag.
- On Open VSX, a deleted version keeps its number reserved. A gap in version numbers means a deletion.
- Download every `.vsix` published since the leak, from both registries. Compare sha256 against your CI artifacts. The hashes must match across registries.
- Find the cause. GitHub masks only exact secret values, so encoded, split or debug-echoed copies print. Check `set -x`, step debug, verbose `vsce` output and base64 steps. Grep other workflows and logs for the same pattern, and rotate any other secret in that log.

**If you find any unknown version**
- Marketplace: publish a clean higher patch at once and report the bad version to Marketplace support. Unpublish the whole extension only if you have no clean build.
- Open VSX: delete the bad version and publish the clean patch.
- Email customer security contacts directly. They allowlist your publisher ID. Include the version range and hashes.

**If you find nothing**
- Still post a short note: exposure window, token revoked, hashes verified. The log was public and a customer may find it first. This is your call.

**This week: rebuild publishing without stored secrets (½ to 1 day per registry)**
1. Marketplace: register a trusted-publishing policy for the repo and workflow, then run `vsce publish --packagePath <file>.vsix --oidc`.
   - The job needs `permissions: id-token: write, contents: read` and Node 22+.
   - If OIDC is blocked, use `--azure-credential` with Entra workload identity.
2. Open VSX: register a trusted-publisher policy, then run `ovsx publish <file>.vsix --trusted-publishing`.
3. **Delete** `OVSX_PAT` and every PAT path from the job. A PAT takes precedence and hides a broken OIDC setup.
4. Add a CI step that fails when the packed `.vsix` contains a secret.
5. Never mint a replacement PAT from an Owner account.
   - If you need a stopgap, use a dedicated Contributor-role account, short expiry, scoped to the namespace on Open VSX.
   - Global Azure DevOps PATs stop working on 2026-12-01, 38 days from now, so PAT publishing ends anyway.

One token for both registries made one leak into two. Federation gives each registry its own short-lived identity.

## Fire 1: community extension

**Why not the takedown**
- You report through the registry only if the listing impersonates you. Check for your logo, an "official" claim, or a lookalike publisher name.
- Removal normally stops new installs only. The 9,800 existing installs keep their keys in plaintext `settings.json`. The takedown doesn't fix the exposure.
- Your v2 change broke it. Removing the only tool users have, with no replacement, costs goodwill and fixes nothing.
- "Uninstall" is the wrong message. The risk is the keys. Tell users to rotate and remove the key.

**Steps**
1. Verify (1 hour). Read the extension's source and listing.
   - Confirm key-in-settings and direct REST calls.
   - Check for impersonation and for an Open VSX copy.
   - Audit your own official extensions against the same rule first: keys in `SecretStorage`, never settings.
2. Find affected customers (1 hour to 1 day). Match the extension's User-Agent or request pattern in API logs.
   - You know these customers. Email them directly: rotate the key, delete it from `settings.json`, and use the interim path.
3. Publish a docs notice. Use facts only: unofficial, stores the key in settings, broken on v2, rotate your key.
   - Add the notice link to the v2 error body returned to legacy calls.
4. Post one public issue on the extension's repo offering a v2 fix or adoption. Two emails over six weeks is enough to count the maintainer as unreachable. Don't block on a reply.
5. Run a takedown only if step 1 shows impersonation. Use the registry's report channel.

**Official replacement (2 to 4 weeks, if a CLI with `--json` exists)**
- Job: view and browse cost data in the editor. The community extension's installs are demand evidence, but installs are acquisition only. Count active keys from your API logs.
- Verdict: Go, as a thin shell (tree view, status bar, quick pick) over the CLI or a generated SDK. It holds no hand-written API calls.
- Keep the rich webview starved. Promote charts only if a tree view can't show the job and an owner is staffed.
- Auth: reuse CLI login (`quarrystone auth token --json`), else `SecretStorage`.
- Telemetry: follow the host's level, and send a versioned User-Agent server-side.
- Name: distinct from "Quarrystone Costs". Publish under your verified publisher to both registries from the same `.vsix`.
- Link it from docs, CLI help and the dashboard as the official extension.
- If your existing official extension already covers this job, skip the new build. Point users to it.
- Publish only through the new federated pipeline.
- If the community maintainer appears, adopt their listing instead.

## Order

| # | Action | When |
|---|---|---|
| 1 | Revoke tokens, verify revocation | today, 1 h |
| 2 | Audit members, versions, hashes | today, 2 h |
| 3 | Verify community extension, find affected keys | today to tomorrow |
| 4 | Customer emails, docs notice | this week |
| 5 | OIDC publishing on both registries | this week, before any release |
| 6 | Official thin shell | 2 to 4 weeks |

## Assumptions

| ID | Assumption | Who confirms |
|---|---|---|
| A1 | You already ship an official extension (the CI token suggests it) | Extension owner |
| A2 | A CLI with `--json` and a token command exists | CLI owner |
| A3 | The listing doesn't impersonate you | You, in step 1 |
| A4 | Key-in-settings is true (reported, not read) | You, in step 1 |
| A5 | The token had Owner-level reach | Azure DevOps token page |
| A6 | Active user count is unknown | API logs |

Next: open Azure DevOps, User settings, Personal access tokens, and revoke.