# Greywick `sdk-playground` publishing: what works, and what to change

Three of your four requirements don't work as written. Each has a replacement below, plus the workflows. I couldn't check Docker's current docs from here, so confirm the OIDC and DCT status below before you build on it.

## Where your requirements break

| Ask | Problem | Replacement |
|---|---|---|
| OIDC login to Docker Hub | Docker Hub has no OIDC trust for GitHub Actions. Hub login takes a username plus a PAT, or an org access token on paid plans. | Use a scoped PAT for the Hub login. Use OIDC where it exists: Sigstore keyless signing. |
| `DOCKER_CONTENT_TRUST=1` | DCT (Notary v1) is being retired across the ecosystem. It needs long-lived root and repo keys, which defeats the point of OIDC. Kubernetes never checks it: kubelet pulls ignore DCT, so customers get zero verification. | Sign with cosign keyless (OIDC). Customers verify with an admission policy. |
| Rollback = delete the bad tag | Deleting `latest` doesn't revert anything. New pulls fail with `ImagePullBackOff`. Nodes that already cached the bad image keep running it. With DCT, the signing metadata would also stay behind. | Repoint `latest` to the last good digest. Delete a tag only for a security takedown, after repointing. |
| Customers pull `:latest` | `latest` is mutable. K8s defaults to `imagePullPolicy: Always` for it, so every pod start is a pull, and a bad push hits customers instantly. | Publish immutable version tags. Tell customers to pin a version or digest. Keep `latest` as a convenience that you move deliberately. |

## Account risks to fix

- **Personal account:** `greywick/` is tied to one person. If they leave or lose the account, you lose the image. Move it to a Docker org, which needs a paid plan.
- **Pull limits:** customer clusters pulling `:latest` behind shared NAT will hit anonymous rate limits. Free plans are the weak spot here.
- **Retention:** check the current free-plan policy on deleting inactive images before relying on old version tags for rollback.
- **Open source:** if the SDK is open source, look at the Docker-Sponsored Open Source program. It gives free org features and removes pull limits.

## 1. One-time setup

1. Create a Docker PAT on the owning account with **Read & Write** scope. Don't use Read-Write-Delete.
2. In GitHub, create an environment `release` with required reviewers.
3. Add `DOCKERHUB_TOKEN` as a secret in that environment, and `DOCKERHUB_USERNAME` as a variable.
4. Pin every action below to a full commit SHA before shipping. I wrote tags for readability.

## 2. Publish workflow: `.github/workflows/publish.yml`

It runs on a version tag, builds, pushes immutable tags, and signs by digest.

```yaml
name: publish
on:
  push:
    tags: ["v*.*.*"]

permissions:
  contents: read

jobs:
  publish:
    runs-on: ubuntu-latest
    environment: release
    permissions:
      contents: read
      id-token: write # Sigstore keyless signing (OIDC)
    env:
      IMAGE: greywick/sdk-playground
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-buildx-action@v3
      - uses: sigstore/cosign-installer@v3

      - uses: docker/login-action@v3
        with:
          username: ${{ vars.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}

      - id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.IMAGE }}
          # No "latest" here: promotion is a separate, deliberate step.
          flavor: latest=false
          tags: |
            type=semver,pattern={{version}}

      - id: build
        uses: docker/build-push-action@v6
        with:
          context: .
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          provenance: mode=max
          sbom: true

      - name: Sign by digest
        env:
          DIGEST: ${{ steps.build.outputs.digest }}
        run: cosign sign --yes "${IMAGE}@${DIGEST}"

      - name: Verify what we just signed
        env:
          DIGEST: ${{ steps.build.outputs.digest }}
          REPO: ${{ github.repository }}
        run: |
          cosign verify "${IMAGE}@${DIGEST}" \
            --certificate-oidc-issuer https://token.actions.githubusercontent.com \
            --certificate-identity-regexp "^https://github.com/${REPO}/\.github/workflows/publish\.yml@refs/tags/v"
```

The verify step must fail the job when the signature is missing. Check that once by running it against an unsigned digest.

## 3. Promote and rollback workflow: `.github/workflows/promote-latest.yml`

One workflow does both jobs. Promote a new version, or roll back to an older one, by pointing `latest` at an existing version tag.

```yaml
name: promote-latest
on:
  workflow_dispatch:
    inputs:
      version:
        description: "Existing version tag to make :latest (e.g. 1.4.2)"
        required: true

permissions:
  contents: read

jobs:
  promote:
    runs-on: ubuntu-latest
    environment: release # required reviewers gate every move of latest
    env:
      IMAGE: greywick/sdk-playground
      VERSION: ${{ inputs.version }}
    steps:
      - uses: docker/setup-buildx-action@v3
      - uses: sigstore/cosign-installer@v3
      - uses: docker/login-action@v3
        with:
          username: ${{ vars.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}

      - name: Refuse unsigned or unknown versions
        env:
          REPO: ${{ github.repository }}
        run: |
          cosign verify "${IMAGE}:${VERSION}" \
            --certificate-oidc-issuer https://token.actions.githubusercontent.com \
            --certificate-identity-regexp "^https://github.com/${REPO}/\.github/workflows/publish\.yml@refs/tags/v"

      - name: Repoint latest (server-side copy, same digest)
        run: |
          docker buildx imagetools create -t "${IMAGE}:latest" "${IMAGE}:${VERSION}"
          docker buildx imagetools inspect "${IMAGE}:latest"
```

The `latest` tag now shares the digest of `VERSION`. The signature is bound to the digest, so it carries over with no re-sign.

## 4. Rollback runbook

1. **Stop the bleeding.** Run **promote-latest** with the last good version. Get the approval from a second reviewer.
2. **Confirm.** Check that `docker buildx imagetools inspect greywick/sdk-playground:latest` shows the good digest. Then run `docker pull greywick/sdk-playground:latest` on a clean machine.
3. **Tell customers.** Nodes that cached the bad image keep it until the pod restarts and re-pulls. Under the default `Always` policy a restart is enough. Pinned-digest users are unaffected.
4. **Leave the bad version tag in place** for forensics. Never reuse or overwrite it. Ship the fix as a new patch version, then promote that.
5. **Delete a tag only for a security takedown** (leaked secret, malicious content), and only after step 1. Do it in the Hub UI or with a Read-Write-Delete token created for that incident and revoked afterward. The CI token can't delete, by design.
6. **Write the post-incident note.** Record the bad digest, the window it was `latest`, and who pulled it.

## 5. What customers should do

Pin a version or digest in their manifests:

```yaml
image: greywick/sdk-playground:1.4.2@sha256:<digest>
```

To enforce signatures, they can use Kyverno `verifyImages` or Sigstore policy-controller. Both need the same issuer and identity values as the `cosign verify` step above. Publish those values in your docs. That check is the real replacement for DCT, and it works in Kubernetes.

## If you still want DCT

You can add `DOCKER_CONTENT_TRUST=1` and `docker trust` signing, but it has costs:

- You must store the delegation key and its passphrase as Actions secrets.
- You have to back up the offline root key.
- You'd have no customer-side benefit unless they run `docker pull` with DCT on. Kubernetes won't check it.

I'd skip it. Tell me if you need it for a compliance reason, and I'll write that variant.

## Decisions for you

1. Move to a Docker org (paid) or keep the personal account and accept the bus-factor risk?
2. Can you tell customers to pin versions, or does `:latest` stay the contract? If it stays, step 3 of the runbook will happen on every incident.
3. Does a compliance requirement force DCT?