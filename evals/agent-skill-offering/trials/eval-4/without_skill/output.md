# Release wiring for the fgate skill and plugin manifests

I haven't run any of this, and I didn't read your repo. The manifest paths and the `cmd/fgate` build path are assumptions, so adjust them.

## Two problems with the plan

**1. A `before.hooks` rewrite never reaches users.** The hook runs in CI after the tag is pushed. The tagged commit still holds the old version, and the rewritten files are never committed. Plugin marketplaces and skill installers read `skills/` and the manifests from the git ref, not from your release artifacts. They would ship the stale version while the binary reports the new one.

The fix is to bump the files in a commit before tagging. Keep the goreleaser hook, but make it an assertion that fails the release if the tag and the committed files disagree.

**2. The content check as described can't fail.**
- `go build ./...` builds packages and produces no binary, so there is nothing to run. Use `go build -o <dir>/fgate ./cmd/fgate`.
- `fgate deploy --help` exits 0 whatever flags the skill mentions, because the flag you're testing isn't on the command line. An unknown flag next to `--help` probably errors in cobra and pflag, but I haven't verified that, and it's fragile anyway.
- The reliable check is to extract flags from the skill's `fgate ...` command lines and assert each one appears in that subcommand's `--help` output. Also assert that `--help` itself exits 0.

## `-yes` in help

It's fine if you use Go's stdlib `flag` package. Stdlib `flag` prints every flag with one dash but accepts both `-yes` and `--yes`. pflag and cobra print `--yes`, so seeing `-yes` points to stdlib `flag`.

Check `go.mod` and your imports to confirm which package you use. Then check these:

- **Positional arguments.** Stdlib `flag` stops parsing at the first non-flag argument. `fgate deploy my-app --yes` silently treats `--yes` as a positional argument. Test that exact order, since agents following the skill will write it that way. If it breaks, either write the skill with flags first or move to pflag.
- **Documentation.** Write `--yes` in the skill, since that's what users type. The checker below accepts one or two dashes.

## Files

### `scripts/set-version.sh`

This script **rewrites the manifest files**. It takes a bare version such as `1.4.0`, with no `v`, which matches goreleaser's `{{ .Version }}`.

```bash
#!/usr/bin/env bash
set -euo pipefail

version="${1:?usage: set-version.sh X.Y.Z}"
[[ "$version" =~ ^[0-9]+\.[0-9]+\.[0-9]+(-[0-9A-Za-z.-]+)?$ ]] || { echo "bad version: $version" >&2; exit 1; }

root="$(cd "$(dirname "$0")/.." && pwd)"
# Every file that carries the plugin version. Add the Codex manifest here if you ship one.
manifests=(
  ".claude-plugin/plugin.json"
  ".claude-plugin/marketplace.json"
)

for rel in "${manifests[@]}"; do
  f="$root/$rel"
  tmp="$(mktemp)"
  # Rewrite every "version" key, including plugins[].version in marketplace.json.
  jq --arg v "$version" 'walk(if type == "object" and has("version") then .version = $v else . end)' "$f" > "$tmp"
  mv "$tmp" "$f"
done
echo "manifests set to $version"
```

I'd leave `SKILL.md` without a version field. The skill shouldn't hardcode a version, because the binary reports its own via `fgate --version`. One fewer file to keep in sync.

### `scripts/check-version.sh`

The goreleaser hook runs this script. It only reads files.

```bash
#!/usr/bin/env bash
set -euo pipefail

version="${1:?usage: check-version.sh X.Y.Z}"
# Snapshot builds (goreleaser --snapshot) carry a suffix that never matches a manifest.
[[ "$version" == *SNAPSHOT* ]] && { echo "snapshot build, skipping version check"; exit 0; }

root="$(cd "$(dirname "$0")/.." && pwd)"
manifests=(".claude-plugin/plugin.json" ".claude-plugin/marketplace.json")
status=0

for rel in "${manifests[@]}"; do
  # Collect every version value in the file; fail on none, or on any mismatch.
  mapfile -t found < <(jq -r '.. | objects | select(has("version")) | .version' "$root/$rel")
  if [[ ${#found[@]} -eq 0 ]]; then
    echo "FAIL $rel: no version key" >&2; status=1; continue
  fi
  for v in "${found[@]}"; do
    [[ "$v" == "$version" ]] || { echo "FAIL $rel: has $v, tag says $version" >&2; status=1; }
  done
done
exit $status
```

### `scripts/check-skill-flags.sh`

This script **builds a binary into a temp dir**. Every flag the skill uses must appear in the matching subcommand's help.

```bash
#!/usr/bin/env bash
set -euo pipefail

root="$(cd "$(dirname "$0")/.." && pwd)"
skill="$root/skills/fgate/SKILL.md"
bin_dir="$(mktemp -d)"
trap 'mv "$bin_dir" "/tmp/fgate-check-$$"' EXIT   # no rm: stays out of the way of the safety net

(cd "$root" && go build -o "$bin_dir/fgate" ./cmd/fgate)
fgate="$bin_dir/fgate"

# Positive control: a flag that must exist and one that must not, so the grep can fail.
help_has() { # <flag-without-dashes> <subcommand-or-empty>
  # shellcheck disable=SC2086
  "$fgate" $2 --help 2>&1 | grep -Eq -- "(^|[^[:alnum:]-])-{1,2}$1([^[:alnum:]-]|\$)"
}
help_has "help" "" || { echo "control failed: help not detected" >&2; exit 2; }
! help_has "zz-no-such-flag" "" || { echo "control failed: bogus flag detected" >&2; exit 2; }

status=0
checked=0
# Lines inside code fences that start with "fgate ".
while IFS= read -r line; do
  read -ra tok <<< "$line"
  sub=""
  # Subcommand = first token after "fgate", when it is not a flag.
  [[ ${#tok[@]} -gt 1 && "${tok[1]}" != -* ]] && sub="${tok[1]}"

  "$fgate" $sub --help >/dev/null 2>&1 || { echo "FAIL '$line': '$sub --help' exits non-zero" >&2; status=1; continue; }

  for t in "${tok[@]:1}"; do
    [[ "$t" =~ ^-{1,2}([a-zA-Z][a-zA-Z0-9-]*)(=.*)?$ ]] || continue
    flag="${BASH_REMATCH[1]}"
    [[ "$flag" == "help" ]] && continue
    checked=$((checked + 1))
    # A flag may be global, so fall back to the root help.
    if help_has "$flag" "$sub" || help_has "$flag" ""; then :; else
      echo "FAIL '$line': flag --$flag not in '$sub --help'" >&2; status=1
    fi
  done
done < <(awk '/^```/{f=!f; next} f && /^[[:space:]]*fgate /{sub(/^[[:space:]]+/,""); print}' "$skill")

[[ $checked -gt 0 ]] || { echo "FAIL: no flags found in $skill, extractor is broken" >&2; exit 2; }
echo "checked $checked flag mentions"
exit $status
```

Known limits:
- It takes only the first token as the subcommand, so a two-level command like `fgate env set` needs a small map.
- It only sees flags inside fenced code blocks. Flags in prose go unchecked, so keep them in code spans, or extend the awk.

### `.goreleaser.yaml`

Merge this into your existing file. The ldflags line is only a reminder of what you already have.

```yaml
version: 2

before:
  hooks:
    - ./scripts/check-version.sh {{ .Version }}

builds:
  - main: ./cmd/fgate
    binary: fgate
    ldflags:
      - -s -w -X main.version={{ .Version }}
```

### `.github/workflows/release.yml`

```yaml
name: release
on:
  push:
    tags: ["v*"]

permissions:
  contents: write

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - uses: actions/setup-go@v5
        with:
          go-version-file: go.mod
      # Fail before publishing if the skill documents a flag the binary lacks.
      - run: ./scripts/check-skill-flags.sh
      - uses: goreleaser/goreleaser-action@v6
        with:
          version: "~> v2"
          args: release --clean
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### `.github/workflows/skill-check.yml`

This runs the flag check on pull requests. Otherwise you only learn about a drifted skill at release time.

```yaml
name: skill-check
on:
  pull_request:
    paths: ["skills/**", "cmd/**", "internal/**", ".claude-plugin/**"]

jobs:
  flags:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-go@v5
        with:
          go-version-file: go.mod
      - run: ./scripts/check-skill-flags.sh
```

### `scripts/release.sh`

This **creates a commit and a signed tag**. It does not push. The push is what triggers the release, so you run it yourself.

```bash
#!/usr/bin/env bash
set -euo pipefail

version="${1:?usage: release.sh X.Y.Z}"
root="$(cd "$(dirname "$0")/.." && pwd)"
cd "$root"

[[ -z "$(git status --porcelain)" ]] || { echo "working tree not clean" >&2; exit 1; }
[[ "$(git branch --show-current)" == "main" ]] || { echo "not on main" >&2; exit 1; }
git fetch origin main
[[ "$(git rev-parse HEAD)" == "$(git rev-parse origin/main)" ]] || { echo "main is not at origin/main" >&2; exit 1; }

./scripts/set-version.sh "$version"
./scripts/check-version.sh "$version"
./scripts/check-skill-flags.sh

git add .claude-plugin/plugin.json .claude-plugin/marketplace.json
git commit -m "chore(release): $version"
git tag -s "v$version" -m "v$version"

echo "Tagged v$version. To publish, run: git push origin main v$version"
```

## Release flow

1. Run `./scripts/release.sh 1.4.0`.
2. Run `git push origin main v1.4.0`.
3. The workflow checks the skill flags, goreleaser asserts that the tag matches the manifests, and then it builds and publishes.

Pushing the commit and the tag together stops the tag from landing on a commit that `main` doesn't have.

## Verify before relying on it

- Run `check-skill-flags.sh` once with a bogus flag added to the skill. It should fail.
- Run `check-version.sh 9.9.9` on the current tree. It should fail.
- Run `fgate deploy my-app --yes` and confirm the flag takes effect. If it doesn't, you're on stdlib `flag` and hit the positional-order trap.