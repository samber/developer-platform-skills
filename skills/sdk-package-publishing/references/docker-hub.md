# Docker Hub and container registries

## Contents

- Library vs binary
- CI auto-publishing: credentials
- Public publishing: tags and immutability, signing and attestations, namespace, removal
- Private publishing
- Private consumption
- Dated changes

## Library vs binary

- Every image is a binary artifact: a CLI, agent, server or SDK playground packaged with its runtime. Libraries never ship as images; their image is at most a dev container or example.
- Multi-architecture images (`linux/amd64`, `linux/arm64`) go out as one manifest list per tag, built once in the build job.
- Go binaries built by GoReleaser can publish their images from the same release (go-modules.md).

## CI auto-publishing

- **Trigger:** a protected tag push. Pipeline shape: release-workflow.md, which pushes the prebuilt OCI layout and signs by digest.
- **Provenance:** sign and attest every pushed digest (Signing and attestations, below).

**Credentials**

- Docker Hub OIDC from GitHub Actions exists only for organizations on Team, Business or Docker Hardened Images plans and Docker-Sponsored Open Source namespaces, never personal accounts: an org owner creates the connection, the job uses `id-token: write` and `docker/login-action` v4.5.0+.
- Paid orgs without OIDC: an Organization Access Token (OAT) scoped to the target repositories with push only, and an explicit 30- or 90-day expiry (OATs can be created with none; never pick it).
- Free or Pro personal namespaces: a personal access token with read-write scope and an expiry, owned by a dedicated bot account, not a person. Move SDK images to an organization once OIDC or OATs matter.
- Log in with `--password-stdin`, never a password argument that lands in shell history and logs.
- On GitHub, publishing to `ghcr.io` needs only the workflow's built-in token with `packages: write`; add the `org.opencontainers.image.source` label to link the repository.

## Public publishing

**Tags and immutability**

- Publish an immutable version tag per release (`1.4.2`) plus floating tags (`1.4`, `1`, `latest`) that you move deliberately.
- Turn on Docker Hub immutable tags for version-tag patterns (regex) so a release tag can never be overwritten or deleted; keep floating tags mutable.
- Tell consumers to pin by digest (`image@sha256:...`) in production manifests.

**Signing and attestations**

- Docker Content Trust (Notary v1) is being retired (see Dated changes): do not build signing on `DOCKER_CONTENT_TRUST=1`, and migrate existing signed repositories. Docker publishes no replacement signatures for you.
- Sign with Sigstore cosign keyless from CI (`cosign sign <image>@<digest>` using the CI OIDC identity) or with Notation; signatures live as OCI referrers next to the image.
- Consumers verify identity and issuer, not just presence: `cosign verify <image> --certificate-identity=<workflow-ref> --certificate-oidc-issuer=<ci-issuer>`. Enforce in-cluster with an admission policy.
- BuildKit attaches minimal provenance by default; publish `--provenance=mode=max --sbom=true` for SDK images, which needs the attestation permissions on the build job.

**Namespace**

- The namespace is the user or org name. Publish from an org, never a personal account. Docker Verified Publisher (paid, commercial) and Docker-Sponsored Open Source (free, non-commercial OSS) add badges and lift pull limits for consumers.

**Removal and rollback**

- Rollback = point `latest` and the affected floating tags back at the previous good digest, then publish a fixed version tag. Consumers pinned by digest are unaffected.
- Deleting a tag breaks every consumer still pulling it; prefer retagging plus a release note.

## Private publishing

- Private repositories on Docker Hub, `ghcr.io` (new images are private by default), cloud registries (Amazon ECR, Google Artifact Registry, Azure Container Registry), GitLab Container Registry, Harbor, Artifactory, Nexus.
- Push with cloud workload identity or CI OIDC federation into the cloud account wherever the registry supports it; fall back to a scoped, expiring robot or access token.

## Private consumption

- Developer machines: a credential helper (`credsStore`, or `credHelpers` per registry such as `docker-credential-ecr-login`) instead of base64 credentials in `~/.docker/config.json`.
- Kubernetes: node or workload identity for cloud registries; otherwise an `imagePullSecrets` secret of type `kubernetes.io/dockerconfigjson`, created per namespace from the secret store, never committed:

```sh
# Dedicated config holding only the read-only pull credential; never the publish job's config
export DOCKER_CONFIG="$(mktemp -d)"
printf '%s' "$REGISTRY_READ_TOKEN" | docker login registry.internal.example.com -u ci-puller --password-stdin
kubectl create secret generic regcred -n sdk-demo \
  --type=kubernetes.io/dockerconfigjson \
  --from-file=.dockerconfigjson="$DOCKER_CONFIG/config.json"
rm -rf "$DOCKER_CONFIG"   # the credential must not outlive the job
```

- A config file that uses `credsStore` holds no credentials, so the resulting secret would be empty.

- Route public base images through a pull-through mirror to survive Docker Hub rate limits and to scan once.
- Reference images by full registry host (`registry.internal.example.com/corp/sdk:1.4.2`); a short name silently resolves to Docker Hub.

## Dated changes

- 2025-07-29: immutable tags API.
- 2026-07-31: Docker Hub OIDC connections for GitHub Actions (paid and DSOS orgs).
- 2026-12-08: `notary.docker.io` shuts down; Docker Content Trust stops working.
