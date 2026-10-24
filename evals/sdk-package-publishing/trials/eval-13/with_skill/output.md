# Marrowline: Go CI fetch fix and private module hosting review

**Verdict:** revert all three settings, and don't host the Go modules on GitHub Packages. The builds pass because the checks that were failing are now switched off. Neither of those changes fixes how the private path is configured.

I assumed Go modules at `git.marrowline.io/platform/...` served from a self-hosted git server, and a CI provider that hasn't been named. I haven't seen the original CI error. Send it, because the likely root cause below is a hypothesis.

## 1. The three settings

| Setting | What it does | Verdict |
|---|---|---|
| `GOSUMDB=off` | Turns off checksum verification for every module, including public ones. A tampered or substituted public dependency would build without error. | ❌ Remove. |
| `GOINSECURE=git.marrowline.io` | Allows plain HTTP or unverified TLS for that host. The probable reason is an internal CA the runners don't trust. | ❌ Remove. Install the CA on the runners. |
| `GOPROXY=https://proxy.golang.org\|direct` | A pipe falls back to `direct` on any error, not just 404 or 410. It also sends private paths to the public proxy first. | ❌ Replace with a comma form. |

The engineer's reasoning about the pipe is backwards. A comma falls back only on 404 or 410, which is the safe behaviour for public modules that are missing. A pipe also falls back on timeouts and 5xx, so during a proxy outage it masks failures and sends the private path to a second route. It doesn't add resilience for private modules, which never belong on the public proxy.

**Likely root cause.** The private prefix isn't declared private. Without `GOPRIVATE`, Go asks `proxy.golang.org` and `sum.golang.org` about `git.marrowline.io/...`. The public proxy can't see it, and the checksum database can't verify it. That produces the "cannot fetch" and "verifying module" errors. Disabling the sumdb, allowing insecure access and widening fallback hid those errors, but they didn't resolve them.

**A smaller leak.** Every private module path is currently sent to Google's proxy and checksum database.

## 2. Replacement CI configuration

```sh
export GOPRIVATE=git.marrowline.io        # also sets GONOPROXY and GONOSUMDB for this prefix only
export GOPROXY=https://proxy.golang.org,direct   # comma, not pipe
# GOSUMDB: leave unset (default sum.golang.org)
# GOINSECURE: leave unset
```

- **Authentication.** Render `~/.netrc` at job start from the secret store, with mode 600:
  - `machine git.marrowline.io login ci-bot password <GO_READ_TOKEN value>`
  - Go 1.24+ reads it through `GOAUTH`, whose default is `netrc`.
  - Use a read-only token that belongs to a bot account.
  - On self-hosted runners, add an always-run cleanup step that deletes the file.
  - The alternative is a git `insteadOf` rewrite to SSH.
- **TLS.** If `GOINSECURE` was there because of a private CA, install that CA in the runner image or job. If the server is on plain HTTP, put TLS in front of it.
- **Placeholders only.** I haven't seen any token. If one was pasted into a ticket or chat, revoke it.
- **Proof.** Run these on a clean runner with an empty module cache:
  1. `go env GOPRIVATE GONOSUMDB GOINSECURE` should show the prefix in the first two and nothing in the third.
  2. `go list -m git.marrowline.io/platform/authlib@<tag>` should succeed.
  3. `GOFLAGS=-mod=mod go mod verify` should pass.
  4. Temporarily clear `GOPRIVATE` on a scratch job. The fetch should fail again, which shows the fix is the cause.

## 3. Hosting Go modules on GitHub Packages

GitHub Packages has no Go registry, and neither does AWS CodeArtifact. npm working there doesn't carry over. For Go, the private module is the private repository plus a tag, and nothing is uploaded. You already have the repository, so you need no new host.

If you want a private Go proxy for caching and access control, these options exist:

- Google Artifact Registry (Go format)
- Artifactory
- Nexus
- A self-hosted GOPROXY server

I'd add a proxy only if you hit a concrete need, such as rate limits, git-server load or an audit requirement. If you add one:

- Point `GOPROXY` at it alone, for example `https://goproxy.internal.marrowline.io`.
- Set `GONOSUMDB=git.marrowline.io`.
- Don't use a pipe.
- Make sure it can't be bypassed to fetch your internal prefix from public upstreams.

**Dependency confusion.** Go has no flat namespace to squat, because import paths are URLs. The real risks are a leaked path or letting the `marrowline.io` domain lapse. Keep the domain renewed and the tag-push rights tight.

## 4. Release and rollback for the Go modules

- **Tags are the release.** A pushed semver tag publishes the module, so the tag ruleset is the publish credential. Restrict who can create `v*` tags, and tag only commits already on the protected branch. Use `sdk/go/v1.4.2`-style prefixes for submodules in a monorepo.
- **Never move or re-push a tag.** Consumers' checksums already pin the first content.
- **Rollback.** Publish a newer tag whose `go.mod` contains `retract v1.4.3 // reason; use v1.4.4`. I haven't run anything. You run the tag push yourself.
- **Rehearsal.** Use a scratch module.
- **Major versions.** From v2 onward, the module path needs the `/v2` suffix.

## 5. Next steps

1. Send me the original CI error. I'll confirm the `GOPRIVATE` diagnosis and check for a TLS or auth cause.
2. Remove the three variables and apply section 2 in one change.
3. Run the four-step proof above on a clean runner.
4. Decide on a private proxy only after the first rate-limit or audit trigger.
5. Keep GitHub Packages for npm. It is irrelevant to Go.

Questions that would change this plan: Which CI provider and runner type do you use? Is the git server on self-signed or internal-CA TLS? Do you also publish any Go binaries (that would bring in GoReleaser)?