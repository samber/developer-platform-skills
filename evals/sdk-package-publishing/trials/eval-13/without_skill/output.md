# Review: Marrowline Go module CI settings

**Verdict:** revert all three settings. The GitHub Packages idea won't work for Go. I haven't seen your CI or repo, so the root cause of the original fetch failure is still unknown.

## Next action

Find out why the fetch failed, then replace the three env vars with one: `GOPRIVATE`. Builds only pass today because the checks that caught the problem are off.

## The three settings

| Setting | What it does | Problem | Fix |
|---|---|---|---|
| `GOSUMDB=off` | Turns off checksum-database verification for every module, public ones included. | A tampered or swapped dependency is accepted silently. `go.sum` only protects modules it already lists. | Remove it. `GOPRIVATE` exempts only the private path. |
| `GOINSECURE=git.marrowline.io` | Allows plain HTTP and skips TLS certificate verification for that host. | Anyone on the network path can inject code into `authlib`, and `authlib` is the auth library. It also hides the likely root cause, which is a cert or auth problem. | Remove it. Fix the CA or credentials instead. |
| `GOPROXY=https://proxy.golang.org\|direct` | The pipe falls through to `direct` on any error. The comma falls through only on 404/410. | Every fetch of an internal module path is first sent to a public proxy, which leaks internal names. Transient errors and a misbehaving proxy get masked. | Use the default `https://proxy.golang.org,direct`. |

The "pipe is more resilient" claim is true, but it buys resilience by hiding failures. Combined with the other two settings, nothing verifies anything.

## Probable root cause

Go could not reach or authenticate to `git.marrowline.io`. The usual causes are:

- **Missing credentials in CI.** There is no token, so `git` can't read the private repo.
- **Untrusted internal CA.** The runner doesn't trust the certificate. This is the likely reason someone reached for `GOINSECURE`.
- **Vanity import unreachable.** The `?go-get=1` meta tag isn't served to the runner.
- **Public proxy tried first.** Without `GOPRIVATE`, Go asks `proxy.golang.org` and the checksum DB, which cannot see a private host.

To confirm, run these on a CI runner:

```sh
go env GOPROXY GOSUMDB GOPRIVATE GOINSECURE
git ls-remote https://git.marrowline.io/platform/authlib
go mod download -x git.marrowline.io/platform/authlib
```

## Correct configuration

```sh
# Private path skips proxy and checksum DB. It sets GONOPROXY and GONOSUMDB too.
GOPRIVATE=git.marrowline.io/*
# GOPROXY, GOSUMDB, GOINSECURE: unset, so Go uses its defaults.
```

Then fix the real cause:

- **Auth:** give CI a read-only token and wire it in with `git config --global url."https://<user>:<token>@git.marrowline.io/".insteadOf "https://git.marrowline.io/"` or a `.netrc`. Store the token as a CI secret. **This writes to the runner's git config.**
- **Certificates:** install the internal CA on the runner image.
- **Integrity:** commit `go.sum` and build with `-mod=readonly`.
- **Real resilience:** run a caching proxy such as Athens or Artifactory, or cache the module cache (`GOMODCACHE`) in CI. This beats the pipe.

## GitHub Packages for Go

I don't think GitHub Packages has a Go module registry. As far as I know it covers npm, Maven/Gradle, RubyGems, NuGet and containers. Please check the current GitHub docs before deciding, because my knowledge could be out of date. Your npm setup doesn't carry over.

Go modules are fetched from version control, so the options are:

1. **Move `authlib` to a private GitHub repo.**
   - The module path becomes `github.com/marrowline/authlib`, so every import needs rewriting.
   - Set `GOPRIVATE=github.com/marrowline/*`.
   - Use a GitHub App token or fine-grained PAT with read access to contents. In Actions, `GITHUB_TOKEN` only reaches the current repo.
2. **Keep the current host** and fix auth and certificates as above. This is the smallest change.
3. **Adopt a Go-aware registry or proxy**, such as Artifactory, Athens or Google Artifact Registry, if you want a central store.

I'd start with option 2 and move to option 1 only if you are leaving `git.marrowline.io` anyway.

## Cleanup

- Check whether those variables were set at org or shared-pipeline level. If so, every Marrowline build is affected, not just this one.
- Run `go mod verify` and compare `go.sum` against a build from before the change, in case a dependency changed while checks were off.
- Add a CI check that fails if `GOSUMDB=off` or `GOINSECURE` appear in the environment.

**Open question:** what was the actual error in the original CI failure (TLS, 401/403, 404, or timeout)? That decides which fix applies.