# Thornfield Media: `thornfield/sdk` Packagist fix and hardening plan

Do the work in this order. It restores a consistent state first, then closes the credential and resolution holes.

## Assumptions

- CI is GitHub Actions. I didn't verify this. Other CI providers use the same Packagist flow.
- `thornfield` is a Packagist vendor you own, with 2FA on every maintainer.
- I don't know the content of the hotfix. If it fixes a vulnerability, add the advisory step in the rollback runbook below.
- I don't know why installs failed before the contractor set `canonical: false`. Diagnose that first (section 3).

## Findings

| # | Finding | Severity |
|---|---|---|
| 1 | Moving the `v3.2.0` tag can't be fixed by re-syncing. Since 2026-05-27 Packagist no longer rewrites a published stable version when its tag moves. | 🔴 |
| 2 | The **MAIN** Packagist token sits in CI. It can create and edit packages, so treat it as exposed. | 🔴 |
| 3 | `canonical: false` on the Satis repository lets a public `thornfield/internal-auth` with a higher version outrank your private one (dependency confusion). | 🔴 |
| 4 | A hard-coded `version: 3.2.0` in `composer.json` drifts from the tag. Packagist derives versions from tags. | 🟠 |
| 5 | Nothing stopped the tag from moving. On Packagist the tag ruleset is the publish credential. | 🟠 |

## 1. Fix the moved tag

Packagist keeps serving the old `v3.2.0` commit for good. Roll forward.

1. Ship the hotfix as **`v3.2.1`**. Don't re-sync or re-push `v3.2.0`.
2. Put `v3.2.0` back on the commit Packagist recorded. Read that commit from the `v3.2.0` version page on Packagist (the source reference). This makes the repository and the registry agree again. You must run the tag push yourself (**moves a public tag**, so do it only after the ruleset in section 5 is in place, with a release manager account):
   ```sh
   git fetch origin
   git tag -f v3.2.0 <sha-packagist-recorded>    # **rewrites local tag**
   git push --force-with-lease origin refs/tags/v3.2.0    # **rewrites remote tag**
   ```
   Packagist won't change either way, so this is cosmetic consistency. Skip it if you'd rather not touch the tag again.
3. Tell consumers to upgrade to `^3.2.1` in the changelog. Lockfiles that pinned `3.2.0` keep the old code until they run `composer update thornfield/sdk`.
4. Deleting a version on Packagist is a web-UI action only, and unnecessary here.

## 2. Replace the MAIN token

1. Set up the replacement first, so a release never has a gap. Pick one:
   - **Preferred:** log in to Packagist with GitHub and grant the Packagist app access to the `thornfield` organization. Pushes then sync with no credential, and you delete the CI sync step.
   - **Fallback:** keep the CI step, but use the **SAFE** token.
2. Regenerate the MAIN token on your Packagist profile page. This is a **registry credential change** that you must do yourself.
3. Delete the old secret from the CI secret store. Check the CI audit log for where else it was used.
4. Never paste the token here. If you did paste it anywhere, treat it as revoked.

Fallback sync step, with placeholders only:

```yaml
sync-packagist:
  needs: tests
  runs-on: ubuntu-latest
  permissions: {}
  steps:
    - name: Notify Packagist
      env:
        PACKAGIST_SAFE_TOKEN: ${{ secrets.PACKAGIST_SAFE_TOKEN }}   # SAFE token only
      run: |
        curl -fsS -X POST https://packagist.org/api/update-package \
          -H "Authorization: Bearer <packagist-user>:${PACKAGIST_SAFE_TOKEN}" \
          -H "Content-Type: application/json" \
          -d '{"repository":"https://github.com/thornfield/sdk"}'
```

Trigger this job only from a protected `v*` tag push.

## 3. Fix the Satis repository config

1. **Find out why installs failed.** The cause is probably one of:
   - Satis lacks a version the constraint needs.
   - Authentication failed.
   - A package with the same name exists elsewhere.

   Run these in a clean checkout:
   ```sh
   composer install -vvv
   composer why-not thornfield/internal-auth <constraint>
   ```
   Fix that cause (rebuild Satis with the missing tags, fix the `auth.json` or `COMPOSER_AUTH` entry), not the symptom.
2. **Remove `canonical: false`** and scope the repository to your internal names:
   ```json
   {
     "repositories": [
       { "type": "composer", "url": "https://composer.internal.thornfield.example", "only": ["thornfield/internal-auth"] }
     ]
   }
   ```
   List each private package by name. `thornfield/*` would also route the public `thornfield/sdk` to Satis. The public SDK falls back to Packagist if Satis lacks it, but exact names are clearer.
3. **Credentials:** use `COMPOSER_AUTH` from the CI secret store, or a gitignored `auth.json`. Use a read-only Satis credential, separate from anything that publishes. Keep credentials out of `composer.json`.
4. **Install** with `composer install` against a committed `composer.lock`.

### Proof that internal names resolve only from Satis

Packagist has no blocking endpoint, so the control is client mapping plus vendor ownership. Run these checks:

```sh
code() { curl -s -o /dev/null -w '%{http_code}' --netrc-file "$FEED_NETRC" "$1"; }
# positive control: the probe can see the feed
[ "$(code "$SATIS_URL/p2/thornfield/internal-auth.json")" = 200 ] || { echo "probe cannot see the feed"; exit 1; }
# the name must NOT exist publicly (anonymous request, exact status)
[ "$(curl -s -o /dev/null -w '%{http_code}' https://repo.packagist.org/p2/thornfield/internal-auth.json)" = 404 ] \
  || { echo "public package with internal name exists, or probe inconclusive"; exit 1; }
```

- A 401, 403, 5xx or DNS error is inconclusive, never a pass.
- Query metadata only. Never install the probe target.
- Check the lockfile: the `dist.url` and `source` for `thornfield/internal-auth` must point at the Satis host.
- Confirm `thornfield` is a Packagist vendor you own. Only vendor owners can create packages under it, so nobody else can publish `thornfield/internal-auth` publicly.
- Repeat the probe after any Satis or `composer.json` change.

## 4. Remove the hard-coded version

1. Delete `"version": "3.2.0"` from `composer.json`.
2. Add a CI guard so it can't come back:
   ```sh
   composer validate --strict
   jq -e 'has("version") | not' composer.json >/dev/null || { echo "remove version from composer.json"; exit 1; }
   ```
3. Don't add a tag-equals-manifest check. On Packagist the tag is the version.

## 5. Make the tag the protected credential

On Packagist the tag is the release, so lock it like a token.

1. **Tag ruleset** (GitHub repository settings) for `v*`:
   - Only release managers may create tags.
   - Nobody may update or delete them (this blocks moved tags).
   - Require signed tags if your team can.
2. Make the sync job's trigger, the ruleset and the environment rule list the same `v*` pattern.
3. The sync job holds only the SAFE token. Put it in a protected `release` environment with at least two reviewers besides whoever cuts releases, and block self-review.
4. Pin every action to a full commit SHA. Set default permissions to none. Don't trigger on `pull_request_target` or `workflow_run`.
5. Provenance: Packagist has no attestation support. Attest only PHAR assets on the GitHub release, if you ship any.

## 6. Rollback runbook for `thornfield/sdk`

You run these steps. I run none of them.

1. Tag the fixed version (`v3.2.1`) and let the hook or the SAFE-token sync pick it up.
2. If the bad version has a security impact, publish a **security advisory** on the repository. `composer audit` reads advisory databases. Name `3.2.1` as the safe version.
3. If compromise is suspected, isolate the build hosts, then revoke and rotate every credential the release job could reach.
4. Never move or delete the bad tag. Hard deletion is a Packagist web-UI action, reserved for leaked secrets or malware.
5. Announce in the changelog and the advisory channel.
6. Rehearse steps 1-2 on a private Composer repository, never on `thornfield/sdk`.

## 7. Migration sequence

| When | Step | Evidence it leaves |
|---|---|---|
| Day 0 | Set up the Packagist GitHub app or SAFE token; regenerate MAIN; delete the old secret | Packagist token page, CI secret list |
| Day 0 | Tag ruleset on `v*` | Ruleset export |
| Day 0 | Tag `v3.2.1`; optionally restore the `v3.2.0` tag | Packagist version list |
| Day 1 | Diagnose the Satis failure; remove `canonical: false`; add `only` | PR diff, `composer install` log |
| Day 1 | Run the confusion probe; check lockfile sources | Probe output, `composer.lock` diff |
| Day 2 | Remove `version`; add the CI guard | PR diff, CI run |
| Day 2 | Protected `release` environment and SHA-pinned actions | Environment settings |

## Definition of done

- ✅ No MAIN token anywhere in CI.
- ✅ `v*` tags can't be moved or deleted.
- ✅ `v3.2.1` is on Packagist.
- ✅ `canonical: false` is gone, and the probe returns exact 200 on Satis and exact 404 publicly.
- ✅ `composer.json` has no `version` key, and CI enforces it.