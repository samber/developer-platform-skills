# Release pipeline: Terraform Registry and OpenTofu Registry

Load at workflow step 7. One GitHub release feeds both registries; the work is a signing key, one GoReleaser config, one tag-triggered workflow, and two one-time registrations.

## Contents

- One-time setup
- Signing key
- GoReleaser config
- Release workflow
- Registering on the Terraform Registry
- Registering on the OpenTofu Registry
- Every release
- Docs generation
- Namespace moves
- Partner Premier SBOM

## One-time setup

1. Create a public GitHub repo `<org>/terraform-provider-<name>`, lowercase, under the organization that will own the provider for its whole life (see Namespace moves).
2. Add `terraform-registry-manifest.json` at the repo root:

   ```json
   { "version": 1, "metadata": { "protocol_versions": ["6.0"] } }
   ```

   Plugin Framework serves protocol 6 (`["6.0"]`); SDKv2 serves protocol 5 (`["5.0"]`). Protocol 6 needs Terraform 1.0 or later.
3. Create the signing key, store it as repo secrets, add the GoReleaser config and the workflow below.
4. Register the provider and the key on both registries.

## Signing key

- Generate an RSA key (4096 bits) dedicated to provider releases. The Terraform Registry accepts RSA or DSA only; current GnuPG defaults to an ECC (ed25519) key, which the Registry rejects.

  ```
  gpg --full-generate-key        # choose "RSA and RSA", 4096 bits
  gpg --armor --export <KEY_ID>  > public.asc    # registered on both registries
  gpg --armor --export-secret-keys <KEY_ID>      # stored as GPG_PRIVATE_KEY secret only
  ```

- Store `GPG_PRIVATE_KEY` and `PASSPHRASE` as repository or environment secrets. Restrict the release environment to tag pushes by maintainers.
- Set an expiry and a calendar reminder: OpenTofu checks key expiry when a key is submitted, and renewing a key means re-registering the public key on both registries.
- Keep an offline backup and a revocation certificate. A compromised key is one of the few reasons the OpenTofu Registry removes versions.

## GoReleaser config

Copy `.goreleaser.yml` from `hashicorp/terraform-provider-scaffolding-framework`. The fields that make a release valid:

| Field | Required value | Why |
| --- | --- | --- |
| `builds[].env` | `CGO_ENABLED=0` | static binaries run on any CI runner and hosted Terraform agents |
| `builds[].binary` | `{{ .ProjectName }}_v{{ .Version }}` | Registry expects `terraform-provider-<name>_v<version>` inside the zip |
| `archives[].formats` / `name_template` | `zip`, `{{ .ProjectName }}_{{ .Version }}_{{ .Os }}_{{ .Arch }}` | exact asset name the registries resolve |
| `checksum.name_template` | `{{ .ProjectName }}_{{ .Version }}_SHA256SUMS`, `algorithm: sha256` | the signed file |
| `checksum.extra_files` and `release.extra_files` | `terraform-registry-manifest.json` renamed `{{ .ProjectName }}_{{ .Version }}_manifest.json` | registries read the protocol version from it |
| `signs[].artifacts` | `checksum`, args `--batch --local-user {{ .Env.GPG_FINGERPRINT }} --output ${signature} --detach-sign ${artifact}` | produces the binary (not armored) `_SHA256SUMS.sig` |

Build every `goos`/`goarch` pair your users run: linux, darwin, windows, freebsd on amd64 and arm64 at minimum. A missing pair fails `init` on that platform with "does not have a package available for your current platform".

## Release workflow

`.github/workflows/release.yml`, triggered on tags matching `v*`:

1. Checkout with full history (`fetch-depth: 0`).
2. Set up Go from `go.mod`.
3. Import the key (`crazy-max/ghaction-import-gpg`) from the two secrets; export its fingerprint.
4. Run GoReleaser `release --clean` with `GITHUB_TOKEN` and `GPG_FINGERPRINT`.

- Pin every action to a full commit SHA; the workflow holds the signing key.
- Give the job `permissions: contents: write` and nothing more.
- Gate the tag on a green nightly acceptance run (see `references/acceptance-testing.md`).

## Registering on the Terraform Registry

1. Sign in to registry.terraform.io with GitHub; select the organization namespace.
2. Add the ASCII-armored public key under User Settings > Signing Keys for that namespace.
3. Publish > Provider, select the repo. The Registry installs a webhook and ingests every finalized (non-draft) GitHub release from then on.

Never modify or replace a released version: users' lock files then fail with checksum errors.

## Registering on the OpenTofu Registry

1. On `github.com/opentofu/registry`, open the "Submit new Provider" issue form with `<org>/terraform-provider-<name>`. Use the web issue form: submissions created by API, CLI or pull request are closed unprocessed.
2. Open the "Submit new Provider Signing Key" form with the namespace, optionally the provider name (omit it for a namespace-wide key), and the armored public key. The submitter must be a public member of the GitHub org.
3. The registry indexes GitHub releases; no separate upload exists.

Without a registered key, `tofu` installs the provider with GPG validation skipped, and users who set `OPENTOFU_ENFORCE_GPG_VALIDATION=true` cannot install it at all. Anyone can submit your provider repo; only your org can submit its key.

## Every release

1. Changelog section `## X.Y.Z (Unreleased)` complete (see `references/versioning-and-deprecation.md`).
2. Docs regenerated and committed; CI fails on a dirty `docs/` tree.
3. Nightly acceptance run green on the release commit.
4. Tag `vX.Y.Z` on the default branch. No branch may share the tag's name.
5. Verify both registries list the version and that `terraform init` and `tofu init` install it on a clean machine.

Never delete, retag or re-upload a version; ship the next patch instead. The OpenTofu Registry refuses removal for a double-published build, a regression or a change of mind, and removes a version only for malicious code, leaked secrets or credentials, a compromised signing key, a legal order, or extreme disruption. A release that leaked a secret: rotate the secret first, then request removal.

Enable GitHub immutable releases on the repo, and leave GoReleaser's `release.draft` unset: GoReleaser already creates a draft, uploads every asset, then publishes. Setting `draft: true` turns the publish step off, and the Terraform Registry never ingests a draft. Rehearse once on a throwaway repo.

## Docs generation

- Run `tfplugindocs generate` through `go generate` (`//go:generate go run github.com/hashicorp/terraform-plugin-docs/cmd/tfplugindocs generate --provider-name <name>`).
- Schema `MarkdownDescription` values are the field docs; write them in the same change as the schema.
- Templates where prose is needed: `templates/index.md.tmpl`, `templates/resources/<name>.md.tmpl`, `templates/data-sources/<name>.md.tmpl`, and the matching ephemeral-resources, functions, actions and list-resources folders.
- Examples in `examples/`: `provider/provider.tf`, `resources/<type>/resource.tf`, `resources/<type>/import.sh`, `resources/<type>/import-by-string-id.tf` (and `import-by-identity.tf` once identity ships), `data-sources/<type>/data-source.tf`. One minimal runnable example per file; no `terraform`, `provider` or `output` blocks outside the provider index example.
- The Registry needs `docs/index.md` and one page per resource, data source and function. Check rendering in the Registry doc preview tool before the first release.

## Namespace moves

Publish under the final organization from the first release. A provider address change (`<old-org>/<name>` to `<new-org>/<name>`) breaks every configuration that pins the old source, and modules without a `required_providers` block fail with "missing provider" errors and duplicate installs. Users must edit `source` and run `terraform state replace-provider` per state.

Registry namespaces follow the GitHub owner of the repo, so adopting a community provider always changes its address. Users keep their schema and state shape but must edit `source` and run `replace-provider` once.

Transfer-adopt (maintainer cooperates):

1. Transfer the repo into your org; GitHub keeps issues and stars and redirects the old URL.
2. Publish the next version under your namespace with your own key, on both registries (OpenTofu needs a new provider submission for the new address).
3. If pinned users need fixes at the old address during a migration window, that requires a repo left under the old owner and the old maintainer's key; agree it before the transfer or announce a hard cut.
4. Ask the previous maintainer to point the old README and docs index at the new address.

Fork-adopt (maintainer silent past the time box, license permits):

1. Fork into your org, keep the license and attribution, and continue the version line (next minor) so upgrade tests from the last community release apply.
2. Publish under your namespace; the old address freezes at its last release.
3. Open an issue on the old repo announcing the vendor-maintained provider and its new address.

Either way:

- Ship a guide in `docs/guides/` with the `source` edit and the `replace-provider` command, and an upgrade test that starts from the old address (see `references/acceptance-testing.md`).
- Keep the schema compatible across the address change: users should face one migration at a time.

## Partner Premier SBOM

Partner Premier requires an SBOM next to the release. Add a GoReleaser `sboms` section (Syft, emitting SPDX or CycloneDX per archive). The Registry's expected layout per OS and architecture is loosely specified: confirm it with the partner program before relying on it.
