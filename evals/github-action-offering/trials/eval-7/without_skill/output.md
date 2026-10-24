# Verdict: keep the transfer and v2 stewardship. Change the other four steps.

## 1. Transfer to `kaspar-tools`: transfer to the company org instead

- **Marketplace setup is a small hurdle.** For a free action it needs a company org with 2FA on, the Developer Agreement accepted, and one checkbox on the release. You don't need to publish a listing to accept a transfer, and the org can be created today.
- **A personal org adds a second transfer.** A second transfer means a second redirect hop and a possible re-listing. It also leaves a company asset, and the supply chain of about 380 repos, under your personal account.
- **Ownership is unclear.** A personal org raises bus-factor, IP-ownership and employment-agreement questions. Get a short written statement from the contractor that he transfers the repo and that the code is MIT or Apache, or assigned to you.
- **Pending transfers are an exposure.** Until the transfer completes, his account is a supply-chain risk to every `@v2` user. Do it soon.
- **Don't let him create a new repo at the old name.** The old name redirects after transfer, and `uses:` lines rely on that redirect. A new repo at that name would break it.
- **Audit after transfer.** Check Actions secrets, deploy keys, webhooks, collaborators and tokens. Rotate everything.
- **Verify what happens to an existing Marketplace listing.** I'm not certain it survives a transfer, so test this first.

## 2. Delete v3 tags and re-cut v3 with your input names: don't

- **Deleting and re-pointing `v3` is a silent breaking change.** GitHub Actions only warns about unknown inputs. Anyone on `@v3` would run with their config ignored and defaults applied, so a lint step could pass while checking nothing. That is worse than a loud failure.
- **Deleting tags also breaks resolution.** Workflows get "unable to resolve action" until you re-cut.
- **Retire v3 and ship a new major.** Release `v4` with your contract.
- **Make `v3` fail loudly or translate.** Leave the tags, or move `v3` once to a shim that does one of two things:
  - It accepts the old v3 input names as deprecated aliases.
  - It fails with `::error::v3 is retired, use v4 or v2`.
- **Size the problem first.** Code-search the repos on `@v3`. If it's a handful, contact them directly.
- **Enable immutable releases** after this fix, so tags can't be moved again.

## 3. Marketplace listing push and launch post: wrong target, wrong order

- **Adoption isn't the problem.** You already have about 380 repos, and the risk is breaking them.
- **The listing helps discovery.** It does nothing for migration.
- **Sequence it like this:**
  1. Take over the repo and fix security.
  2. Ship a maintained `v2` patch with a stability promise.
  3. Ship `v4` with a migration guide. The `version-migration-guide` skill covers this.
  4. Announce.
- **Write the post for the existing users.** It should say who maintains the action now, that `v2` is safe, and how to pin by SHA.
- **Keep the repo listable.** The action needs a root `action.yml` and branding, and the repo must not contain workflow files.

## 4. GHES: download the zip and vendor it: don't

- **A zip has no tags or history.** `uses: org/quillstone-lint-action@v2` then fails, and customers can't take updates.
- **Use the supported routes instead:**
  - `actions-sync` mirrors the repo with tags into an org on the instance.
  - GitHub Connect resolves public actions from github.com.
- **Check the action type.** A Docker action needs its image pullable from air-gapped instances. A JS action needs a Node runtime the customer's GHES runners support.
- **Test against the oldest GHES version you support.**

## 5. GHES OIDC: reuse the same token exchange: not as is

- **The issuer differs per instance.** On GHES it is `https://<host>/_services/token`, not `token.actions.githubusercontent.com`, and enterprises can customize it. A github.com-only exchange rejects every GHES token.
- **Trust must be registered per customer.** Don't accept arbitrary issuers. Each customer registers an issuer, an audience and a claim mapping.
- **Namespace identities by issuer.** An org or repo called `acme` on github.com and on a GHES instance are different entities. If you key on `repository_owner` alone, one can impersonate the other.
- **Your service probably can't fetch their JWKS.** Most GHES instances sit behind firewalls. Choose one of these:
  - The customer publishes the JWKS.
  - The customer pastes the keys.
  - The exchange runs inside their network.
- **If you fetch customer-supplied URLs, guard against SSRF.**
- **Ask whether you need OIDC at all.** A per-instance API key secret may be enough for GHES.

## Revised order

1. Get a written IP statement from the contractor. Create the company org.
2. Transfer the repo to the company org. Audit and rotate secrets.
3. Count the `@v3` users, then retire `v3` with a shim or a loud failure.
4. Ship the `v2` patch, then `v4`, with a migration guide.
5. Document the `actions-sync` and GitHub Connect GHES paths. Design the per-issuer OIDC trust.
6. Announce, with the Marketplace listing.

## Questions that change this

1. Is the action JS, Docker or composite?
2. Does the repo have a license, and does it cover his code?
3. How many repos use `@v3`?
4. What does the token exchange protect: an API key, or tenant data?