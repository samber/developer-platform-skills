**Do not build this as asked.** Three of your four requirements conflict with Docker Hub's rules as of 2026-10-23. I took the facts from `docker-hub.md` and `release-workflow.md` in the skill. I ran nothing, and every publish or retag command below is for you to run.

| You asked | Problem | Plan |
|---|---|---|
| OIDC login from Actions | Docker Hub OIDC works only for Team, Business or Hardened Images orgs and DSOS namespaces. A free personal account cannot use it. | Use an expiring read-write PAT on a bot account, held in a protected environment. Move to an org to get OIDC (see "Why OIDC is not available"). |
| `DOCKER_CONTENT_TRUST=1` signing | `notary.docker.io` shuts down on **2026-12-08**, 46 days from now. Signatures made now stop verifying then. | Sign with cosign keyless instead. |
| Rollback by deleting the bad tag | Deleting breaks every consumer still pulling it, and it can hit the version tag. | Retag `latest` to the previous good digest, then publish a fix. |

Ranking by value per effort: the PAT and cosign steps are small, so do them first. The org move is the larger job.

## 1. Assumptions and inventory

I assumed these without asking. Correct me if any is wrong.

- CI is GitHub Actions on hosted runners.
- Only the image `greywick/sdk-playground` ships. It is a binary artifact, not a library. The tag format is `vX.Y.Z`.
- The image is for linux/amd64 and linux/arm64.
- The SDK is tied to a commercial product. This does not affect Docker Hub but would matter on Maven Central.
- Today the publish path is probably a laptop or a stored password. Please confirm.
- The account owner is you personally, with no second owner.
- I don't know whether any `latest` tag is already DCT-signed.

| Artifact | Registry | Publish path | Credential | Target |
|---|---|---|---|---|
| `greywick/sdk-playground` | Docker Hub, personal namespace, free plan | GitHub Actions on a protected tag | PAT, read-write, 30 or 90 days, bot account | Move to a Docker org on Team plan, then OIDC |

## 2. Decisions

**Credentials**
- **Now:** a PAT with an expiry, owned by a dedicated bot account. Store it only in the protected `release` GitHub environment. Never use an expiry-less token.
- **The bot account** must have write access to `greywick/sdk-playground`. A personal namespace has no teams or collaborators, so a free account can't grant it that way. Check on the Docker side whether the bot can push at all. If it can't, the PAT has to be yours, which breaks the "owned by a bot" rule.
- **After you move to an org:** switch to OIDC with `docker/login-action` v4.5.0 or later. Use an org access token only if OIDC isn't enabled for you.
- **Why OIDC is not available:** the reference says OIDC exists only for Team, Business or Hardened Images plans and DSOS namespaces. A free personal account has none of these. Docker Hub OIDC dates from 2026-07-31. Check Docker's current plan page before you pay, because plans change.

**Namespace**
- Create an org named `greywick` or similar, with two owners using phishing-resistant 2FA. Transferring the `greywick` name may not be possible. If it isn't, customers will need a new image path, so plan how you announce that.

**Tags**
- Publish an immutable version tag for each release (`1.4.2`), plus the floating tags `1.4`, `1` and `latest`.
- Turn on Docker Hub immutable tags for the version-tag regex, for example `^[0-9]+\.[0-9]+\.[0-9]+$`. Check that your plan supports it.
- Only move `latest` when the new version is the highest stable one. Pre-releases never move it.

**Signing**
- Sign by digest with cosign keyless, using the workflow's OIDC identity. No Docker Hub OIDC is needed for this, because cosign uses GitHub's own OIDC.
- Build with `--provenance=mode=max --sbom=true`.
- Provenance proves where the image was built, not that it is safe.
- Signing is on the starved rung of the credential ladder. But your customers pull into Kubernetes, which is exactly where admission-time verification applies, so it is worth doing.

**DCT migration**
- If `greywick/sdk-playground` already has DCT-signed tags, anyone running with `DOCKER_CONTENT_TRUST=1` breaks on 2026-12-08. Announce the cosign move to those customers before that date.
- After 2026-12-08, don't tell anyone to set `DOCKER_CONTENT_TRUST=1`.

**Preflight**
- `docker buildx build --check` before the build.
- Run the workflow end to end against a private repository first.

## 3. Pipeline (draft, pending your approval)

Placeholders: `<sha>` for each pinned action. Resolve each with `git ls-remote https://github.com/<owner>/<action> refs/tags/<version>`. Never invent one.

Repository setup first:
1. Add a tag ruleset on `v*` so only release managers can create, move or delete tags.
2. Create the `release` environment with reviewers: a team, or at least two people besides whoever cuts releases. Block self-review and restrict deployments to `v*` tags.
3. Put `DOCKERHUB_USER` and `DOCKERHUB_TOKEN` in that environment only. Add no repository-level secrets.

```yaml
name: release
on:
  push:
    tags: ["v*"]
permissions: {}

jobs:
  build:                               # unprivileged: no secrets, no id-token
    runs-on: ubuntu-latest
    permissions: { contents: read }
    outputs:
      version: ${{ steps.ver.outputs.version }}
      is_latest: ${{ steps.ver.outputs.is_latest }}
    steps:
      - uses: actions/checkout@<sha>   # v6
        with: { persist-credentials: false }
      - name: Tag must equal the VERSION file; decide whether latest moves
        id: ver
        run: |
          v="${GITHUB_REF_NAME#v}"
          [ "$v" = "$(cat VERSION)" ] || { echo "tag $v != VERSION"; exit 1; }
          case "$v" in
            *-*) latest=false ;;       # pre-release never moves latest
            *)   latest=true ;;        # backports to older lines: set false by hand
          esac
          echo "version=$v" >> "$GITHUB_OUTPUT"
          echo "is_latest=$latest" >> "$GITHUB_OUTPUT"
      - uses: docker/setup-buildx-action@<sha>   # v3
      - name: Build multi-arch OCI layout, no push
        env:
          VERSION: ${{ steps.ver.outputs.version }}
        run: |
          docker buildx build --platform linux/amd64,linux/arm64 \
            --provenance=mode=max --sbom=true \
            --label org.opencontainers.image.version="$VERSION" \
            --label org.opencontainers.image.source="https://github.com/${GITHUB_REPOSITORY}" \
            -o type=oci,dest=image.tar .
          mkdir layout && tar -xf image.tar -C layout
      - uses: actions/upload-artifact@<sha>      # v5
        with: { name: layout, path: layout }

  publish:
    needs: build
    runs-on: ubuntu-latest
    environment: release               # reviewers approve here
    permissions:
      contents: read
      id-token: write                  # cosign keyless only, not Docker Hub
    env:
      IMAGE: docker.io/greywick/sdk-playground    # becomes the org path after the move
      VERSION: ${{ needs.build.outputs.version }}
      IS_LATEST: ${{ needs.build.outputs.is_latest }}
    steps:
      - uses: actions/download-artifact@<sha>    # v5
        with: { name: layout, path: layout }
      - uses: imjasonh/setup-crane@<sha>         # pin; or install crane from a pinned release
      - uses: sigstore/cosign-installer@<sha>
      - name: Log in with a token on stdin
        env:
          DOCKERHUB_USER: ${{ secrets.DOCKERHUB_USER }}
          DOCKERHUB_TOKEN: ${{ secrets.DOCKERHUB_TOKEN }}
        run: printf '%s' "$DOCKERHUB_TOKEN" | crane auth login index.docker.io -u "$DOCKERHUB_USER" --password-stdin
      - name: Push the version tag, then sign by digest
        run: |
          crane push layout "$IMAGE:$VERSION"
          digest="$(crane digest "$IMAGE:$VERSION")"
          cosign sign --yes "$IMAGE@$digest"
          echo "DIGEST=$digest" >> "$GITHUB_ENV"
      - name: Move floating tags (only after signing succeeded)
        run: |
          [ "$IS_LATEST" = true ] || exit 0
          minor="${VERSION%.*}"; major="${VERSION%%.*}"
          for t in latest "$minor" "$major"; do crane tag "$IMAGE@$DIGEST" "$t"; done
```

Notes:
- The build job holds no secrets. The publish job holds the only publish identity, and uses it only after the environment gate approves.
- Signing happens on the digest, before floating tags move.
- The log-in command in the publish job is the one place a secret appears, and it comes from the protected environment.
- Floating tags point at the same signed digest as the version tag.
- Harden both jobs: no restored caches, no `pull_request_target`, no `workflow_run`, no `workflow_dispatch` without the same gate.
- Delete the Docker Hub password from every place that holds it. Revoke any old token after the first real release works.
- If you ever paste a secret into chat, revoke it.

## 4. Rollback runbook

Rollback does not delete a tag. Run these yourself, in this order.

1. **Publish the fix** as a new version tag, for example `1.4.3`. Do not wait on anything else.
2. **Point `latest` back** only if it points at the bad digest. First check:
   ```sh
   crane digest docker.io/greywick/sdk-playground:latest
   ```
   Then retag to the previous good digest, which you find in your release notes or the previous run log:
   ```sh
   crane tag docker.io/greywick/sdk-playground@sha256:<good-digest> latest
   ```
   Repeat for `1.4` and `1` if they also point at the bad digest. The bad version tag stays, because immutable tags forbid changing it. Say in the release note which version is bad and which is safe.
3. **If compromise is suspected**, isolate build hosts first. Then revoke and rotate the PAT and anything else the release job could reach. Some worms wipe hosts when they lose access.
4. **Hard deletion** is reserved for leaked secrets or malware. If you hit that case, contact Docker support. Do not just delete the tag.
5. **Announce** in the changelog and your security advisory channel. Include the bad digest.

**Kubernetes caveat that makes retagging incomplete.** Retagging `latest` doesn't change pods already running the bad image. It also doesn't change nodes that cached it, when `imagePullPolicy` is `IfNotPresent`. After step 2, tell customers to run:
```sh
kubectl rollout restart deployment/<name> -n <namespace>
```
Nodes with `imagePullPolicy: IfNotPresent` and a cached bad `latest` need the cache cleared or a pull-always policy.

**Rehearse** steps 1 and 2 on a private repository, never on the production image. Every public rehearsal burns a version tag forever.

## 5. Customer side (Kubernetes)

`latest` is the weakest part of your design for customers, because it moves under them. Recommend this instead, in your docs:

- **Pin by version or digest.** `greywick/sdk-playground:1.4.2` or `greywick/sdk-playground@sha256:...`. Keep `latest` for demos. A customer pinned by digest is unaffected by any rollback.
- **Verify the signature** before running:
  ```sh
  cosign verify docker.io/greywick/sdk-playground:1.4.2 \
    --certificate-identity "https://github.com/<owner>/<repo>/.github/workflows/release.yml@refs/tags/v1.4.2" \
    --certificate-oidc-issuer https://token.actions.githubusercontent.com
  ```
  This checks identity and issuer, not just that a signature exists. Enforce it in-cluster with an admission policy (Kyverno or Sigstore policy-controller).
- **Set the pull policy on purpose:** `Always` if they must follow `latest`, a pinned digest otherwise.
- **Docker Hub rate limits:** route pulls through a pull-through mirror. Reference images by full registry host. A short name silently resolves to Docker Hub.

I did not create a private-consumption probe, because this image is public. The dependency-confusion canary in `release-workflow.md` doesn't apply: there is no internal package name to protect.

## 6. Migration sequence

| # | Date (suggested) | Step | Evidence it leaves | Time |
|---|---|---|---|---|
| 1 | This week | Create bot Docker account with write access, issue a 90-day PAT, store it in the `release` environment | PAT expiry date in your secret store | ~20 min |
| 2 | This week | Add tag ruleset, `release` environment and workflow, test against a private repo | Green run log | ~2 h |
| 3 | Before 2026-11-15 | First real release through the pipeline. Verify with `cosign verify`. Revoke the old password or token | Signed digest, revocation log | ~1 h |
| 4 | Before 2026-11-15 | Announce the cosign move to customers, especially anyone using `DOCKER_CONTENT_TRUST=1` | Changelog entry | ~30 min |
| 5 | Before 2026-12-08 | Remove any DCT dependence from your docs and scripts | Docs diff | ~30 min |
| 6 | Q4 or Q1 | Create the Docker org on Team plan, add two owners, enable OIDC, drop the PAT | Org settings, workflow diff | ~half a day, plus plan cost |

## 7. Answers I need

I made assumptions where you didn't say. These change the plan:

1. Do any `sdk-playground` tags already carry DCT signatures?
2. Can the bot account get push access to your personal namespace, or must the PAT be yours?
3. Do you accept the cost of a Docker Team plan, or stay on a PAT for now?
4. Who else can approve a release? You need a second person for the gate.

**Next action:** create the bot account and issue the 90-day PAT (step 1, about 20 minutes), then send me the answers above.