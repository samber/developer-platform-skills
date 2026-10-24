# Verdict: no, it won't pass a SOC 2 audit

The engineer's test doesn't test what you asked. Redo it with the probe below before the audit, which is feasible this week.

## Why the test fails

1. **It tested the wrong thing.** He removed the virtual from the client, so the Artifactory configuration was never in the path. The result only shows that public npm doesn't hold his packages. That is true on any day, and it is not the attack. The attack is a public `@hollowpine/*` package with a higher version number, served *through* the virtual. Metadata and "latest" lookups merge every included repository, so ordering alone doesn't stop it.
2. **"Watched it fail" is inconclusive.** I can't tell which failure he saw. A 404 from npmjs.org, a 401, a 403, a DNS error, a timeout and a missing token all look like a failed install. Nothing shows the install would have succeeded if a public squatter existed.
3. **There was no positive control and no public target.** No public package with an internal-looking name existed, so nothing could have been served. A test that can only fail proves nothing.
4. **He used an admin token.** Artifactory include and exclude patterns don't apply to admins. Even against the virtual, an admin sees internal and public names merged, so the result would be invalid for what your developers and CI experience.
5. **It left a separate finding.** An admin token on a developer's `.npmrc` or shell is a standing credential risk. Under SOC 2 it counts as an access-control exception, so rotate it and write down where it lived.

## Assumptions

- `npm-remote` and the virtual `npm` have no confirmed exclude pattern for `@hollowpine/**` yet. If they do, the probe below is what proves it.
- Internal packages all live under `@hollowpine`. Any unscoped internal name resolves from public npm and is outside the scope mapping.
- You own, or can claim, the `@hollowpine` org on npmjs.com.
- Your CI has a read-only, non-admin feed credential.

## Plan for this week

I did not run any of this. Steps 1 and 3 change public state, so a human with the right access runs them.

**Step 1. Claim the scope and publish one canary (human, once).**
- Confirm `@hollowpine` is an org you own on npmjs.com, with two owners using phishing-resistant 2FA.
- Publish one harmless package, `@hollowpine/confusion-canary`, to *public* npm only. Never publish it internally.
- It publishes permanently, so make it an empty package with a README. Run it from a laptop session (a first publish can't use OIDC) with `npm publish --access public`, or use `npm stage publish`, then revoke any token used.

**Step 2. Set the blocking rule.**
- Add the exclude pattern `@hollowpine/**` on `npm-remote`, and on the virtual `npm` if it has its own excludes.
- Optionally enable Priority Resolution on `npm-local`.
- Record screenshots or an export of both repository configs.

**Step 3. Run the probe (non-admin, read-only identity).**

Use the same credential CI uses, kept in a netrc file and never on the command line. Confirm in Artifactory that this identity isn't an admin.

```sh
FEED=https://<corp-host>/artifactory/api/npm/npm
code() { curl -s -o /dev/null -w '%{http_code}' --netrc-file "$FEED_NETRC" "$1"; }

# 0. Upstream control: the canary really exists on public npm
npm view "@hollowpine/confusion-canary" version --registry https://registry.npmjs.org

# 1. Feed control: the probe identity can see a real internal package
[ "$(code "$FEED/@hollowpine%2f<known-internal-pkg>")" = 200 ] || { echo "probe cannot see the feed"; exit 1; }

# 2. The test: the internal endpoint refuses the public canary, exact status
[ "$(code "$FEED/@hollowpine%2fconfusion-canary")" = 404 ] || { echo "PROBE FAILED or inconclusive"; exit 1; }
```

- Query metadata only. Never install or download the canary.
- Only an exact 404 after the two controls is a pass. A 401, 403, 5xx or DNS error is inconclusive.
- Run the same check against `npm-remote` directly, since it is the repository carrying the exclude.
- Also run `npm view "@hollowpine/confusion-canary" --registry "$FEED"` with the CI credential. It must fail with `E404`, not `E401` or `E403`.

**Step 4. Check client resolution.**
- Commit `.npmrc` with `@hollowpine:registry=https://<corp-host>/artifactory/api/npm/npm/` and `//<corp-host>/artifactory/api/npm/npm/:_authToken=${NPM_READ_TOKEN}`. Hold no secret in the file.
- In every `package-lock.json`, check that every `@hollowpine/*` entry's `resolved` URL points at the corporate host:
  ```sh
  git grep -h '"resolved"' -- '*package-lock.json' | grep -c 'registry.npmjs.org/@hollowpine' # must be 0
  ```
- Install with `npm ci` against the lockfile.
- List any unscoped internal package names. Rename them into the scope, or add them to the exclude list and map them explicitly.

**Step 5. Clean up credentials.**
- Revoke or rotate the admin token the engineer used.
- Make sure no developer or CI job holds an admin token.
- Give CI separate read-only and deploy identities. Deploy goes to `npm-local` only, ideally through GitHub OIDC with a mapping on `environment: release`.

**Step 6. Add a recurring check.**
- Run the probe in a scheduled CI job. Re-run it after every feed reconfiguration or internal package deletion, because deleting a private package while the remote can serve that name reopens the hole.
- Consider a release-age cooldown for new public versions, for example npm `min-release-age`.

## Evidence pack for the auditor

| Evidence | Shows |
|---|---|
| Exclude-pattern config on `npm-remote` and the virtual `npm` | The control exists |
| Public npm page or `npm view` output for the canary | A real target existed |
| Probe output with timestamp: control 200, canary 404 | The control works against a real target |
| Proof the probe identity is non-admin | The result matches what users and CI see |
| Committed `.npmrc` and the lockfile resolved-URL grep | Clients use the internal source |
| Admin-token revocation record | The access finding is closed |
| Scheduled probe job and its last run | The control is monitored |

Keep the engineer's note as a historical record only. Don't cite it as evidence.

## If the canary can't go out before the audit

The skill lets you substitute the blocking-rule check and the lockfile check, but only when no public name exists to probe with. Here a public name can exist, because the scope is yours to claim. So report it plainly instead: the exclude config and lockfile evidence are in place, the live probe is pending, and the date is set.