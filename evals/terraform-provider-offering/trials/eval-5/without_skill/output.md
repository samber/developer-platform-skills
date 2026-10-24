# Pre-release checklist for terraform-provider-oakhollow v1.0.0

I haven't opened your repo or config. This comes from how the Terraform Registry and OpenTofu work, plus what you described. Three items in your checklist are wrong or risky: the GPG key, the re-tag plan, and the OpenTofu assumption. Do those first.

## Do first (about 30 min)

1. **Regenerate the GPG key as RSA.**
   - Your retries won't help. Recent GnuPG defaults to ed25519 (ECC), and as far as I know the Registry accepts only RSA/DSA keys. Check this against the Registry's "Preparing your provider" page.
   - Confirm with `gpg --list-keys --keyid-format long`. An `ed25519` line means that's the cause.
   - Generate a new key: `gpg --quick-generate-key "Oakhollow Eng <you@…>" rsa4096 sign 2y`.
   - Upload the **public** key only: `gpg --armor --export <KEYID>`. Include the BEGIN/END lines.
   - Back up the private key and a revocation certificate somewhere safe.

2. **Settle the namespace, because it's your engineering org.**
   - The Registry namespace is the GitHub org that owns the repo. The repo is at `oakhollow-eng/…`, so the provider will be `oakhollow-eng/oakhollow`, not `oakhollow/oakhollow`.
   - Users' `required_providers` blocks and the lock files they generate will bake this in. Renaming later means republishing.
   - If you want `oakhollow/oakhollow`, transfer the repo to the main org before you publish.
   - Sign in at registry.terraform.io with GitHub, then Publish → Provider.
   - You need org owner rights. The org may also need to approve the Terraform Registry OAuth app.
   - Add the GPG key under that same namespace's signing-keys settings.

## Fix in the release setup

3. **Widen the build matrix.**
   - Linux/darwin amd64 only will break Apple Silicon Macs, which are probably most of your team, and arm64 CI runners.
   - Add `darwin/arm64`, `linux/arm64` and `windows/amd64`. It's cheap, and users on a missing platform get "no available releases match".
   - Archives must be named `terraform-provider-oakhollow_<version>_<os>_<arch>.zip`.

4. **Check the release artifacts.** GoReleaser must produce all of these:
   - the zips
   - `..._SHA256SUMS`
   - `..._SHA256SUMS.sig` (a detached signature made with your RSA key)
   - `terraform-provider-oakhollow_<version>_manifest.json`, copied from a `terraform-registry-manifest.json` at the repo root. Without it, the Registry assumes protocol 5. If you use plugin-framework, you need `{"version":1,"metadata":{"protocol_versions":["6.0"]}}`.

5. **Plan around `draft: true`.**
   - The Registry ingests releases through a GitHub webhook that fires when a release is published. A draft won't trigger it.
   - After you review the assets, click Publish. If the version doesn't show up within a few minutes, use "Resync" on the provider page.

6. **Replace the `@v4` pins.**
   - Tags are mutable, which is a supply-chain risk. Pin each action to a full commit SHA, with a version comment.
   - `goreleaser-action@v4` is also old. If it pulls GoReleaser v2, your `.goreleaser.yaml` needs `version: 2`.
   - Set `permissions: contents: write` on the job.
   - Use `fetch-depth: 0` on checkout.
   - Add repo secrets `GPG_PRIVATE_KEY`, `PASSPHRASE` and `GPG_FINGERPRINT`. The engineering org doesn't inherit secrets from the main org.

7. **Get the Registry docs in place.**
   - The Registry renders `docs/` at the release tag. Generate it with `tfplugindocs` and commit it.
   - Without it, the provider page is empty.
   - The repo must be public and have a LICENSE.

## Drop two assumptions

8. **OpenTofu doesn't mirror the Terraform Registry.**
   - It has its own registry at registry.opentofu.org, which indexes GitHub releases.
   - Submit the provider through the provider-submission issue form in the `opentofu/registry` repo. It's a separate step, and the form asks for your signing key.
   - Until then, `tofu init` can't find the provider. Do this the same day, and note that it reads published releases only, not drafts.

9. **Don't re-tag v1.0.0. Roll forward to v1.0.1.**
   - Registry versions are immutable. Once ingested, a moved tag isn't re-ingested.
   - Users' `.terraform.lock.hcl` checksums will mismatch the new zips. They'll see "checksum mismatch" errors, which is worse than the original bug.
   - The one safe case is a draft you never published. Delete the draft and the tag, fix, and re-tag.
   - If a bad version is already live, ship v1.0.1 and yank or deprecate v1.0.0 from the provider settings page.

## Dry run today

10. **Tag `v1.0.0-rc1` first.**
    - Run `goreleaser release --snapshot --clean` locally.
    - Then push the rc tag, publish the draft, and watch the Registry ingest it. Pre-releases are accepted but not offered as the default version.
    - This tests the key, the webhook, the signatures and the namespace before the real release.
    - Verify the assets yourself: `sha256sum -c *_SHA256SUMS`, then `gpg --verify *_SHA256SUMS.sig *_SHA256SUMS`.
    - From a clean directory, run `terraform init` against the published rc.

## Release day

1. Push `v1.0.0` and let CI build the draft.
2. Check the asset list against item 4, and check the platform count.
3. Publish the release, then confirm the version appears on the Registry.
4. Confirm the OpenTofu submission has merged.
5. Run `terraform init` and `tofu init` from a scratch directory on both a Mac and a Linux machine.

If the key is still rejected after the RSA regeneration, send me the output of `gpg --list-keys --keyid-format long` (public data only) and the first line of the exported block.