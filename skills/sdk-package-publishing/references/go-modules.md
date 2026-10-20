# Go modules

## Contents

- Public publishing: release mechanics, major versions, retraction
- Private publishing
- Private consumption

## Public publishing

**Release mechanics**

- No upload step and no publish credential: the module path is the repository URL, and a pushed semver tag (`v1.4.2`) is the release. `proxy.golang.org` caches it on first request and `sum.golang.org` records its checksum forever.
- Release flow: `go mod tidy`, `go test ./...`, tag from a protected branch, push the tag, then warm the proxy with `GOPROXY=proxy.golang.org go list -m example.com/sdk@v1.4.2`.
- Never move or re-push a tag. The checksum database already holds the first content; every consumer then gets a security error.
- Protect release tags in the forge (tag protection rules, restricted pushers): tag control is the publish credential for Go.
- Submodules in a monorepo tag with the directory prefix: `sdk/go/v1.4.2`.

**Major versions**

- From v2, the module path needs the `/v2` suffix (`module example.com/sdk/v2`) and every internal import changes with it. A v2+ tag on a module whose `go.mod` lacks the suffix is unusable: `go get` rejects it. (`+incompatible` exists only for repositories with no `go.mod`.)
- Mark an old major deprecated with a `// Deprecated: use example.com/sdk/v2` comment above the `module` line, published in a new tag.

**Retraction (rollback)**

- Versions can never be deleted from the proxy or the checksum database.
- Retract by publishing a newer tag whose `go.mod` holds the directive, with a rationale comment users will see:

```
retract (
    v1.4.3 // Breaks token refresh; use v1.4.4.
)
```

- A version can retract itself; if the highest version retracts itself, `@latest` falls back to the previous one. Retracted versions are skipped by `@latest` and upgrades, hidden from `go list -m -versions`, labelled retracted on pkg.go.dev, and flagged to users who depend on them; pinned builds keep working.

## Private publishing

- A private module is a private repository plus tags; nothing is uploaded.
- Optional private proxy for caching and access control: Google Artifact Registry (Go format), Artifactory, Nexus, or a self-hosted GOPROXY server. GitHub Packages and AWS CodeArtifact have no Go registry; GitLab's Go proxy is experimental.

## Private consumption

```sh
# CI environment for a company module tree
export GOPRIVATE=corp.example.com        # prefix match; also sets GONOPROXY and GONOSUMDB
export GOPROXY=https://proxy.golang.org,direct
```

- `GOPRIVATE` keeps private paths away from the public proxy and checksum database; without it, every private path is sent to both.
- Never set `GOSUMDB=off` or a broad `GONOSUMDB` to make a private fetch pass: that drops checksum verification for public modules too. Scope `GONOSUMDB` to private prefixes, and keep `GOINSECURE` (plain HTTP) out of CI.
- Credentials: `GOAUTH` (Go 1.24+, default `netrc`). In CI write `.netrc` from a secret, or rewrite to SSH:

```
# ~/.netrc rendered at job start from the secret store (netrc expands nothing);
# mode 600, removed by an always-run cleanup step on self-hosted runners
machine github.com login ci-bot password <GO_READ_TOKEN value>
# or: git config --global url."ssh://git@github.com/".insteadOf "https://github.com/"
```

- With a private proxy serving everything, set `GOPROXY=https://goproxy.internal.example.com` and `GONOSUMDB=corp.example.com`. A comma between proxies falls back only on 404/410; a pipe falls back on any error, which can leak private paths during an outage.
- Import paths are URLs, so Go has no flat namespace to squat; dependency confusion here means a leaked path or a vanity domain you no longer control. Keep vanity domains renewed.
