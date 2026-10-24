**Verdict: 1 of 5 parts is fine, 3 need changes, 1 needs a different plan.** Do first: ask the contractor to keep his account and never recreate `quillstone-lint-action`. Then create or pick the final home org before you accept the transfer.

I read the skill and its references. I did not look at the actual repo, so check my assumptions at the end.

## Plan review

| Part | Verdict | Why |
|---|---|---|
| Accept the transfer | ✅ Yes | He agrees, and a transfer keeps a redirect for `uses:`. |
| Into personal org `kaspar-tools` | ❌ No | It forces a second transfer later. |
| Delete v3 tags, re-cut v3 | ❌ No | It breaks pinned workflows and reuses a shipped version number. |
| Marketplace push + launch post | 🟠 Reorder | Marketplace is not the adoption lever. |
| GHES: zip + vendor | ❌ No | No pin, no provenance, no upgrade path. |
| GHES OIDC: reuse github.com exchange | ❌ Not as is | The issuer check and the claims differ on GHES. |

## 1. Home org: pick the final one now

- The skill says to choose org and repo names once. A transfer keeps a redirect but drops the Marketplace verified badge unless the new owner is verified.
- Moving from `kaspar-tools` to the company org later is a second transfer. 380 repos would migrate twice if you publish the interim `uses:` path.
- A personal org is also a single-person bus factor on a repo that runs in customers' CI with their secrets.
- "Org not set up for Marketplace" is probably the verified-creator badge. That step is slow. It does not block accepting a transfer or listing.
- Do this: create or use the company org now, even unverified. Accept the transfer there. Request the badge in parallel. Rename the repo only if you must, and do it once.
- Fallback: if you must use `kaspar-tools`, do not publish the new `uses:` path until the final home exists.

**Before you accept the transfer:**
1. Check his repo for secrets, deploy keys, webhooks and collaborators. Rotate or remove all of them after the transfer.
2. Verify his identity through a channel you already trust.
3. Ask him to keep the `jmbarros-dev` account and never recreate that repo name. If anyone recreates it, the redirect dies. If he deletes his account, someone else can register the name and hijack 380 workflows.

## 2. Tags: do not delete, do not reuse v3

- Rule: never reuse a version number the community action shipped with a different contract.
- Deleting tags breaks every pinned workflow at once. SHA pinners and lockfile users stay on the old commit silently. Tag users get a changed contract silently.
- Moving or replacing tags is the pattern in the tj-actions and reviewdog incidents. Security tooling will flag it.
- Do this instead:
  1. Audit every inherited tag against his commit history. Check each target is reachable from the default branch. Check the code for runtime downloads. Confirm each download host is still Quillstone's, not an expired domain.
  2. Declare all pre-transfer tags unsupported. Leave them in place.
  3. Ship your contract as the next unused major. Check what v3.x.y and v4 exist first. `v4` is likely.
  4. Publish a migration guide mapping v2 inputs and his v3 inputs to your names. This is the Failure-modes rule. It is not optional.
  5. Optional help for the 380 `@v2` repos: accept the old v2 names in v4 as deprecated aliases with `deprecationMessage`. Remove them in the next major.
- Whether his v3 contract is "wrong" does not matter. Customers pinned it.
- If the audit finds a critical hole in v2, ship a `v2.x.y` patch release. Never move the `v2` tag silently.

## 3. Marketplace push: wrong lever

- The skill rejects "Marketplace will bring users". Listing is unreviewed and is a trust surface. Docs and onboarding snippets drive adoption.
- Your real adoption pool is the 380 existing repos. Migrate them. Do not seek new users first.
- Spend effort, ranked:
  1. Quickstart in Quillstone docs and in-product onboarding, with the SHA-pinned `uses: org/action@<sha> # v4.0.0` line.
  2. Migration guide plus a release note naming the removal major.
  3. Verified badge request through GitHub partnerships. Enterprise allowlists key on it.
  4. Marketplace listing: one root `action.yml`, unique name, branding, one category.
  5. Launch post. Do it last, once the migration guide exists.
- Release process: every fix is an immutable `vX.Y.Z` release. The moving `v4` tag points only at a released commit. Enable immutable releases before the first public tag.
- Measure with a versioned `User-Agent`. Dependents and code search are public signals only, not usage.

## 4. GHES: no zip vendoring

- A zip is an unpinned snapshot. It has no version, no digest, no attestation and no upgrade path. You also cannot tell which customer runs which copy.
- The sanctioned routes are GitHub Connect, when their admin enables it, or `actions-sync` into their instance. Document both in the README and docs.
- Add inputs for a mirror base URL and a pre-installed CLI path. Air-gapped runners cannot reach your download host.
- Keep the action composite. A node runtime bump excludes old GHES releases. Check which GHES releases you will support before you promise a floor.

## 5. GHES OIDC: do not reuse the github.com exchange as is

- The github.com path pins the issuer to `https://token.actions.githubusercontent.com`. GHES tokens come from `https://<host>/_services/token`, usually on a private network. Your backend cannot reach it.
- If you loosen the issuer check to "accept any issuer", anyone can run an issuer and mint tokens. Never do that.
- Numeric `repository_id` and `repository_owner_id` are per instance. ID 123 on one GHES can collide with ID 123 on github.com. The binding must include the issuer.
- The immutable `sub` format does not exist on GHES. Match individual claims.
- Options:
  1. **Default for launch:** document GHES as key-only. The skill allows this. The `auth` input (`auto`, `oidc`, `key`) lets you add GHES OIDC later as a minor.
  2. **Later:** a customer-registered issuer, with a customer-allowlisted JWKS endpoint or uploaded JWKS with a rotation procedure. Bind on issuer, owner ID, repository ID, and ref or environment.
- On github.com, OIDC failure fails the step with a named error. No silent fallback to key or anonymous mode.

## Order of work

1. Today, 15 min: send the contractor the keep-account request. Pick the final org.
2. Before transfer, about 1 hour: do the repo audit and the tag audit.
3. Day 1 after transfer: rotate secrets. Enable immutable releases and a `v*` tag ruleset. Add the contract check and zizmor.
4. Week 1: write the migration guide and ship `v4.0.0`. Move `v4` to it.
5. After that: quickstart, GHES docs, Marketplace listing, launch post.

## Assumptions and questions

| Assumption | Drives |
|---|---|
| v2 is composite or JavaScript, with a CLI download at runtime | Action type, rule 5 |
| Backend already validates github.com OIDC | Step 4 |
| No v4 tag exists in his repo | Version number |
| Marketplace does not already list it under his name | Listing plan |

Answer these to confirm the plan:
1. What GHES releases and what share of paying customers use GHES, GitLab or other CI?
2. Is the Quillstone CLI a separate binary the action downloads? From where?
3. Who owns the action after launch? What is the on-call and effort ceiling?

**Next:** send the contractor the keep-account request, then answer the 3 questions.