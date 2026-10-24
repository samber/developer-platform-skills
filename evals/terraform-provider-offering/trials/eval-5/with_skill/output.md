# terraform-provider-oakhollow: what's left before tomorrow's v1.0.0

I read the skill and its `release-pipeline.md` and `plan-templates.md`. I did not read the other references, such as acceptance testing and resource design. I also haven't seen your repo, so everything below comes from your checklist.

Four items on your checklist would break or block the release. Two more are risky, and one is a decision you need to make today.

## Decide first: which GitHub org owns the provider?

- The repo is `oakhollow-eng/terraform-provider-oakhollow`, but your main org is `oakhollow`.
- The Registry namespace follows the GitHub owner of the repo. Today's repo gives users `oakhollow-eng/oakhollow` as the provider source.
- Moving later changes that address. Every user has to edit `source` and run `terraform state replace-provider` on each state.
- The skill's rule is to publish under the final org from the first release.
- Ask yourself which org customers will see and which one will last. If it's `oakhollow`, move the repo before you tag.
- Whichever org you pick, your OpenTofu key submission must come from a public member of that org.

## Fix before tagging

1. **Your GPG key is the reason the Registry says it's invalid. Stop retrying.**
   - `gpg --quick-generate-key` with defaults makes an ECC (ed25519) key. The Registry accepts only RSA or DSA.
   - Generate a new key: `gpg --full-generate-key`, choose "RSA and RSA", 4096 bits.
   - Set an expiry and a calendar reminder. Renewing a key means re-registering it on both registries.
   - Export the public key with `gpg --armor --export <KEY_ID> > public.asc`. Export the private key only into the CI secret `GPG_PRIVATE_KEY`, and put the passphrase in `PASSPHRASE`.
   - Keep an offline backup and a revocation certificate.
   - Delete the ECC key from your Registry settings.

2. **Your GoReleaser build matrix is too narrow.**
   - linux and darwin on amd64 only means Apple Silicon Macs fail on `init` with "does not have a package available for your current platform". That happens even if your team never uses them.
   - Build linux, darwin, windows and freebsd, each on amd64 and arm64, at minimum.
   - Also check these fields against HashiCorp's scaffolding `.goreleaser.yml`:
     - `CGO_ENABLED=0`
     - the binary name `{{ .ProjectName }}_v{{ .Version }}`
     - zip archives named `{{ .ProjectName }}_{{ .Version }}_{{ .Os }}_{{ .Arch }}`
     - the `_SHA256SUMS` file with a binary (not armored) detached `.sig`
     - the manifest file renamed to `_manifest.json`
   - Make sure `terraform-registry-manifest.json` is at the repo root. For the Plugin Framework it contains `{"version":1,"metadata":{"protocol_versions":["6.0"]}}`.

3. **Remove `release.draft: true`.**
   - The Registry never ingests a draft release, so v1.0.0 would never appear.
   - GoReleaser already creates a draft, uploads every asset, then publishes. The setting turns off that last step.
   - To review the assets, run `goreleaser release --snapshot --clean` locally. Then do a real rehearsal with a prerelease tag (see "Rehearse" below).
   - Enable GitHub immutable releases on the repo.

4. **Pin actions to full commit SHAs, not `@v4`.**
   - This workflow holds your signing key, so a moved tag could exfiltrate it.
   - Give the job `permissions: contents: write` and nothing more.
   - Restrict the release environment to tag pushes by maintainers.
   - Check the workflow does the following:
     - checks out with `fetch-depth: 0`
     - sets up Go from `go.mod`
     - imports the key with `crazy-max/ghaction-import-gpg`
     - runs `goreleaser release --clean` with `GPG_FINGERPRINT`

5. **OpenTofu does not mirror the Terraform Registry for keys.**
   - OpenTofu indexes your GitHub releases, but your signing key isn't there until you submit it.
   - Without a registered key, `tofu` installs your provider with GPG validation skipped. Anyone who sets `OPENTOFU_ENFORCE_GPG_VALIDATION=true` cannot install it at all.
   - Use the web issue forms on `github.com/opentofu/registry`. Submissions made by API, CLI or pull request are closed unprocessed.
     1. "Submit new Provider", with `<org>/terraform-provider-oakhollow`.
     2. "Submit new Provider Signing Key", with the namespace and your armored public key.
   - Do both on the same day, before or right after you tag. The OpenTofu key is processed by humans, so it may not be done by tomorrow.

6. **Never retag v1.0.0. If it's broken, ship v1.0.1.**
   - Re-tagging or re-uploading a version breaks every user's lock file with checksum errors.
   - Neither registry removes a version because of a bug. OpenTofu removes one only for malicious code, a leaked secret, a compromised key, a legal order or extreme disruption.
   - If a release leaks a secret, rotate the secret first, then request removal.
   - Consider whether v1.0.0 should be `0.x` or `1.0.0`. From 1.0.0 you promise compatibility: no removals or renames outside a major. If the resource map is still moving, take `0.x` first.

## Rehearse before the real tag

You listed no prerelease. The skill rehearses with a local snapshot build, then a prerelease tag.

1. Run a local `goreleaser release --snapshot --clean`. Check the asset names and the signature.
2. Tag `v0.1.0-beta1` once the new RSA key is accepted on the Terraform Registry. Range constraints never select prereleases, so this is safe.
3. Confirm the Registry ingests it and that `terraform init` works on a clean machine.

If the key is still rejected or the Registry doesn't ingest the beta, you now know before launch day. Slip v1.0.0 rather than skip this.

## Register on the Terraform Registry

1. Sign in at registry.terraform.io with GitHub, and select the final org namespace.
2. Add the ASCII-armored public key under User Settings > Signing Keys for that namespace.
3. Publish > Provider, and pick the repo. The Registry installs a webhook and ingests every finalized release from then on.

## Release-day checklist

1. The changelog section `## 1.0.0 (Unreleased)` is complete.
2. Docs are regenerated with `tfplugindocs generate` and committed, and `docs/index.md` exists. CI fails on a dirty `docs/` tree.
3. The acceptance suite is green on the release commit.
   - Check every resource's suite has `_basic` with import, `_disappears` and update tests.
   - Check no test sets `ExpectNonEmptyPlan`.
4. Fill the API readiness gate matrix (`plan-templates.md`). Any resource with a FAIL or UNKNOWN row moves to the next minor. Never ship a known perpetual diff.
5. Tag `v1.0.0` on the default branch. No branch may share the tag's name.
6. Verify both registries list the version.
7. On a clean machine, run `terraform init` and `tofu init` with `OPENTOFU_ENFORCE_GPG_VALIDATION=true`. Both must install the latest version.

## Order of work

1. Pick the org and move the repo if needed.
2. Generate the RSA key, register it on the Terraform Registry, and submit it to OpenTofu.
3. Fix `.goreleaser.yml`: add the platforms and remove `draft: true`.
4. Pin the actions to SHAs and set the permissions.
5. Run the snapshot build, then tag `v0.1.0-beta1`.
6. Verify the install on both tools.
7. Tag `v1.0.0` if everything is green. Otherwise slip.

I haven't checked your acceptance tests, resource map or docs, so I can't say whether the gate matrix passes. If you share the repo or the failing Registry message, I can review the GoReleaser config and the workflow line by line.