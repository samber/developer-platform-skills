# Packagist (PHP Composer)

## Contents

- Library vs binary
- CI auto-publishing
- Public publishing: namespace, removal, account security
- Private publishing and consumption
- Dated changes

## Library vs binary

- **Library:** a git repository registered on Packagist. Nothing is uploaded: Packagist reads `composer.json` from each tag, and Composer downloads the forge's zip archive.
- **CLI tool installed per project:** list scripts under `bin` in `composer.json`. Composer links them into `vendor/bin` of projects that require the package, never of the package itself.
- **Standalone tool:** build a PHAR (Box), attach it to the GitHub release with a detached GPG signature for PHIVE users and an artifact attestation, and never replace an uploaded asset. See the binary section of release-workflow.md.

## CI auto-publishing

There is no upload step and no publish credential: a pushed SemVer tag (`v1.4.2`) is the release. Protect release tags with a ruleset; on Packagist, tag control is the publish credential, as on Go.

- **Sync:** log in to Packagist with GitHub and grant the Packagist app access to the organization; pushes then update the package. GitLab, Bitbucket and Gitea use a repository webhook carrying the Packagist username and API token.
- **CI-triggered sync** (only when no hook exists): after the tag push, `POST https://packagist.org/api/update-package` with body `{"repository":"<repo url>"}` and header `Authorization: Bearer <user>:${PACKAGIST_SAFE_TOKEN}`. Use the SAFE token; the MAIN token can create and edit packages and never belongs in CI.
- **Provenance:** Packagist has no attestation support yet. Attest PHAR assets on the GitHub release.
- Omit `version` from `composer.json`: Packagist derives versions from tags, and a hard-coded version drifts from the tag.

## Public publishing

**Namespace**

- Names are `vendor/package`. Publish the company vendor's first package early, and use that one vendor for every SDK package so users can recognize the publisher.

**Removal**

- Never move or delete a release tag. Packagist no longer rewrites a published stable version when the upstream tag moves, so a re-tag leaves the registry and the repository disagreeing.
- Rollback: tag a fixed version and publish a security advisory on the repository; Composer's `audit` reads advisory databases.
- Retire a package with `"abandoned": "corp/new-sdk"` in `composer.json` (or `true`), or from the package page. Version and package deletion are web-UI actions only.

**Account security**

- Enable 2FA for every maintainer. Account takeovers and stolen tokens drove Packagist's 2026 changes: maintainer MFA status is public, and a transparency log records ownership, URL, maintainer and tag changes.
- Composer 2.10 blocks packages flagged as malware by default.

## Private publishing and consumption

- Hosts: Private Packagist, Satis (static repository), Artifactory, Nexus, GitLab's Composer registry.
- Composer 2 treats every repository as canonical: the first repository that contains a name serves every version of it. List the private repository first and scope it:

```json
{
  "repositories": [
    { "type": "composer", "url": "https://composer.internal.example.com", "only": ["corp/*"] }
  ]
}
```

- Never set `"canonical": false` on the private repository: Composer then compares versions across repositories, and a public `corp/sdk 9.9.9` wins.
- Credentials: `COMPOSER_AUTH` from the CI secret store, or a gitignored `auth.json`. Never put credentials in `composer.json`.
- Install with `composer install` against a committed `composer.lock`.

## Dated changes

- 2025-11-14: Packagist transparency log.
- 2026-05-27: published stable versions no longer rewritten on tag moves; malware flags shown; MFA push.
- 2026-05-28: Composer 2.10 blocks malware by default (`config.policy`).
