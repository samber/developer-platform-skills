Your plan has two problems, so I changed it. I couldn't run any of this: writes to `/tmp` were denied. I haven't seen your repo, `.goreleaser.yaml` or `fgate` source either.

**Next action:** run `make release VERSION=x.y.z` (below) instead of a goreleaser hook. Do not start with the hook.

## Verdicts

1. **`before.hooks` cannot bump.**
   - Goreleaser runs after the tag exists. A bump made then never reaches the tag.
   - Lockstep rules 3 and 4 need the skill inside the tagged commit. A failure must happen before the tag exists.
   - Use `make release`: bump, gate, commit, tag, push. Keep goreleaser only to re-check (gate 2) and to publish.
2. **`go build ./...` plus `deploy --help` exit 0 is a weak check.**
   - `go build ./...` with several packages writes no binary. You would run whatever `fgate` is on PATH.
   - It also skips the `-ldflags` version stamping.
   - `fgate deploy --help` is one fixed command. It proves only that `deploy` exists, never that a flag does.
   - Exit code is the wrong signal. Some parsers exit 2 after printing help.
   - Instead: build an explicit binary with stamping, then grep each flag from the skill in the help output.
   - Also check that unknown subcommands fail and that the archive contains `SKILL.md`.
3. **`-yes` in help is OK, if `fgate` uses Go's stdlib `flag`.**
   - Stdlib `flag` prints `-yes` and accepts `-yes` and `--yes`. Users typing `--yes` works.
   - Write `--yes` in the skill. The gate matches either dash count.
   - Two stdlib quirks remain. A bool takes `--yes=false`, never `--yes false`. Parsing stops at the first positional argument.
   - If `fgate` uses cobra or pflag, help would already show `--yes`. Then something else renders it, so check which.

## Files

**1. `Makefile`**

Assumes the module path `./cmd/fgate` and the version variable `main.version`. Match your existing `ldflags`.

```make
MANIFESTS := --manifest .claude-plugin/plugin.json \
	--manifest .claude-plugin/marketplace.json \
	--manifest .codex-plugin/plugin.json \
	--manifest .cursor-plugin/plugin.json \
	--manifest gemini-extension.json
LDFLAGS := -s -w -X main.version=$(VERSION)

.PHONY: skill-gates release
# Pull request check: skill matches the last tag, content matches the HEAD build.
skill-gates:
	python3 scripts/check-skill-version.py "$$(git describe --tags --abbrev=0)" --skills-dir skills $(MANIFESTS)
	go build -ldflags "-X main.version=dev" -o ./bin/fgate ./cmd/fgate
	python3 scripts/check-skill-content.py ./bin/fgate --skills-dir skills --allowlist scripts/skill-content-allowlist.txt

release:
	@test -n "$(VERSION)" || (echo "usage: make release VERSION=x.y.z" && exit 1)
	@test -z "$$(git status --porcelain)" || (echo "dirty tree" && exit 1)
	python3 scripts/check-skill-version.py $(VERSION) --write --skills-dir skills $(MANIFESTS)
	go build -ldflags "$(LDFLAGS)" -o ./bin/fgate ./cmd/fgate
	python3 scripts/check-skill-content.py ./bin/fgate --skills-dir skills --allowlist scripts/skill-content-allowlist.txt
	git add skills .claude-plugin .codex-plugin .cursor-plugin gemini-extension.json
	git commit -m "chore: release v$(VERSION)"
	git tag v$(VERSION)
	git push origin HEAD v$(VERSION)
```

`release` **writes files, creates a commit and a tag, and pushes**.

**2. `scripts/check-skill-content.py`** (gate 3, Python 3.8+ stdlib)

```python
#!/usr/bin/env python3
"""Gate 3: assert the skills and the built fgate binary agree. Python 3.8+, stdlib only.

Usage: check-skill-content.py <binary> [--skills-dir skills] [--allowlist FILE] [--archive GLOB]

Allowlist lines (blank lines and '#' comments skipped):
  ignore <token>               e.g. `ignore --version`: never check this token
  removed <path...> <--flag>   e.g. `removed deploy --legacy`: the skill names it only to say it is gone;
                               fails if the flag exists again
"""
import argparse
import glob
import re
import subprocess
import sys
import tarfile
from pathlib import Path

HELP_TIMEOUT_S = 10  # a help call that hangs means the binary waits on stdin or the network
FENCE = re.compile(r"^\s*(```|~~~)")
INLINE = re.compile(r"`([^`\n]+)`")
FLAG = re.compile(r"^--?([A-Za-z][\w-]*)(?:=.*)?$")
WORD = re.compile(r"^[a-z][a-z0-9-]*$")
SHELL_BREAK = {"|", "||", "&&", ";", ">", ">>", "<", "2>&1"}
# Tune to the exact message fgate prints for an unknown subcommand.
UNKNOWN = re.compile(r"unknown (sub)?command|invalid command|no such command", re.I)
BAD_MARK = "✗"  # lines under a ✗ label are intentionally wrong examples
SKIP_FLAGS = {"h", "help"}  # stdlib flag handles these without listing them

_cache = {}


def help_text(binary, path):
    key = tuple(path)
    if key not in _cache:
        # stdlib flag prints help to stderr: capture both. Exit code is not asserted:
        # some parsers exit 2 after printing help.
        p = subprocess.run([binary, *path, "--help"], capture_output=True, text=True,
                           timeout=HELP_TIMEOUT_S, stdin=subprocess.DEVNULL)
        _cache[key] = p.stdout + p.stderr
    return _cache[key]


def has_flag(text, name):
    # Match with 1 or 2 leading dashes: stdlib flag prints `-yes`, users type `--yes`.
    return re.search(r"(?<![\w-])--?" + re.escape(name) + r"(?![\w-])", text) is not None


def invocations(path, binary):
    in_fence = False
    fence_bad = False
    bad_next = False
    for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if FENCE.match(line):
            in_fence = not in_fence
            fence_bad = bad_next if in_fence else False
            bad_next = False
            continue
        if in_fence:
            if BAD_MARK in line:
                fence_bad = True
            candidates = [] if fence_bad else [line.strip().lstrip("$ ").strip()]
        else:
            if BAD_MARK in line:
                bad_next = True
                continue
            candidates = INLINE.findall(line)
        for c in candidates:
            tokens = c.split()
            if tokens and tokens[0] == binary:
                yield n, tokens


def load_allowlist(file):
    ignore, removed = set(), []
    if file and Path(file).exists():
        for raw in Path(file).read_text(encoding="utf-8").splitlines():
            parts = raw.split("#", 1)[0].split()
            if len(parts) >= 2 and parts[0] == "ignore":
                ignore.add(parts[1])
            elif len(parts) >= 3 and parts[0] == "removed":
                removed.append((parts[1:-1], parts[-1]))
    return ignore, removed


def check_invocation(binary, tokens, ignore):
    """Return a list of problems for one skill invocation."""
    problems = []
    path, i = [], 1
    text = help_text(binary, [])
    while i < len(tokens) and WORD.match(tokens[i]):
        tok = tokens[i]
        if re.search(r"^\s+" + re.escape(tok) + r"(\s|$)", text, re.M):
            path.append(tok)
            text = help_text(binary, path)
            i += 1
            continue
        if UNKNOWN.search(help_text(binary, path + [tok])):
            problems.append("unknown subcommand '%s' after '%s'" % (tok, " ".join(["fgate"] + path)))
        break  # otherwise tok is a positional argument
    for tok in tokens[i:]:
        if tok in SHELL_BREAK:
            break
        m = FLAG.match(tok)
        if not m or m.group(1) in SKIP_FLAGS or tok.split("=")[0] in ignore:
            continue
        name = m.group(1)
        if not (has_flag(text, name) or has_flag(help_text(binary, []), name)):
            problems.append("flag '%s' not in '%s --help'" % (tok, " ".join(["fgate"] + path)))
    return problems


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("binary")
    ap.add_argument("--skills-dir", default="skills")
    ap.add_argument("--allowlist")
    ap.add_argument("--archive", help="glob of release archives that must contain a SKILL.md")
    a = ap.parse_args()

    ignore, removed = load_allowlist(a.allowlist)
    name = "fgate"  # skill text names the tool, not the build path
    errors, seen = [], 0
    for md in sorted(Path(a.skills_dir).rglob("*.md")):
        for n, tokens in invocations(md, name):
            seen += 1
            for p in check_invocation(a.binary, tokens, ignore):
                errors.append("%s:%d: %s" % (md, n, p))
    if seen == 0:
        errors.append("no '%s' invocation found under %s: the check is blind" % (name, a.skills_dir))
    for path, flag in removed:
        if has_flag(help_text(a.binary, path), flag.lstrip("-")):
            errors.append("allowlist rot: '%s %s' exists again" % (" ".join(path), flag))
    if a.archive:
        archives = sorted(glob.glob(a.archive))
        if not archives:
            errors.append("no archive matches %s" % a.archive)
        for arc in archives:
            with tarfile.open(arc) as t:
                if not any(m.endswith("/SKILL.md") or m == "SKILL.md" for m in t.getnames()):
                    errors.append("%s: no SKILL.md inside" % arc)
    for e in errors:
        print("FAIL " + e, file=sys.stderr)
    print("checked %d invocation(s), %d problem(s)" % (seen, len(errors)))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
```

Known limits:
- It does not do the new-surface direction: failing when a command added since the last release is never mentioned. That needs a command list. Add a hidden `fgate commands --json`, or tell me the layout of the root `--help`.
- Subcommands nested under a subcommand are only found if each level's help lists them as indented lines.
- The `UNKNOWN` regex must match what `fgate` prints for a bad subcommand.
- Run it once against a deliberately wrong skill (a bogus flag, a removed subcommand). It must fail. If it doesn't, the check is blind.

**3. `scripts/skill-content-allowlist.txt`**

```text
# Skill names --version on purpose; stdlib flag does not list it in help.
ignore --version
```

**4. `.goreleaser.yaml`** (merge into your existing file)

```yaml
version: 2
before:
  hooks:
    # Backstop for gate 2. Snapshot versions (x.y.z-SNAPSHOT-sha) never match the skill.
    - '{{ if .IsSnapshot }}true{{ else }}python3 scripts/check-skill-version.py {{ .Version }} --skills-dir skills --manifest .claude-plugin/plugin.json --manifest .claude-plugin/marketplace.json --manifest .codex-plugin/plugin.json --manifest .cursor-plugin/plugin.json --manifest gemini-extension.json{{ end }}'
builds:
  - id: fgate
    main: ./cmd/fgate
    binary: fgate
    env: [CGO_ENABLED=0]
    ldflags:
      - -s -w -X main.version={{ .Version }}
archives:
  - files:
      - LICENSE
      - README.md
      - skills/**/*
release:
  footer: |
    ## Agent skill for this release
    ```
    gh skill install {{ .Env.GITHUB_REPOSITORY }} fgate@{{ .Tag }}
    /plugin marketplace add {{ .Env.GITHUB_REPOSITORY }}#{{ .Tag }}
    npx skills add {{ .Env.GITHUB_REPOSITORY }}#{{ .Tag }}
    gemini extensions install https://github.com/{{ .Env.GITHUB_REPOSITORY }} --ref={{ .Tag }}
    ```
    Already installed? Re-run with the new tag.
```

**5. `.github/workflows/release.yml`**

The gates job must pass before anything is published.

```yaml
name: release
on:
  push:
    tags: ["v*"]
permissions:
  contents: read
jobs:
  skill-gates:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with: { fetch-depth: 0 }
      - uses: actions/setup-go@v5
        with: { go-version-file: go.mod }
      - name: Skill version matches tag
        run: |
          python3 scripts/check-skill-version.py "$GITHUB_REF_NAME" --skills-dir skills \
            --manifest .claude-plugin/plugin.json --manifest .claude-plugin/marketplace.json \
            --manifest .codex-plugin/plugin.json --manifest .cursor-plugin/plugin.json \
            --manifest gemini-extension.json
      - uses: goreleaser/goreleaser-action@v6
        with:
          version: "~> v2"
          args: release --snapshot --clean --skip=publish
      - name: Skill matches the built binary and archive
        run: |
          BIN="$(find dist -type f -name fgate -path '*linux_amd64*' | head -1)"
          python3 scripts/check-skill-content.py "$BIN" --skills-dir skills \
            --allowlist scripts/skill-content-allowlist.txt \
            --archive 'dist/*linux_amd64*.tar.gz'
      - uses: astral-sh/setup-uv@1c37ad07a6a961277cf70c0d37d6f313000f5884 # v10.3.0
      - name: Snyk Agent Scan
        run: uvx snyk-agent-scan@latest --ci --dangerously-run-mcp-servers --skills ./skills
        env:
          SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
  release:
    needs: skill-gates
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
      - uses: actions/checkout@v4
        with: { fetch-depth: 0 }
      - uses: actions/setup-go@v5
        with: { go-version-file: go.mod }
      - uses: goreleaser/goreleaser-action@v6
        with:
          version: "~> v2"
          args: release --clean
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

- `--skip=publish` is goreleaser v2 syntax. On v1 use `--skip-publish`.
- Pin the actions to commit SHAs. I pinned only `setup-uv`.
- Pin `snyk-agent-scan` instead of `@latest`.
- Gate 2 on the tag is only a backstop. A failure there means deleting the tag.

**6. Manifests**

I can't fill in author, repository or license. Copy them from your Go module metadata and `LICENSE`. Version `0.0.0` is overwritten by the first `make release`.

`.claude-plugin/plugin.json`:
```json
{
  "name": "fgate",
  "version": "0.0.0",
  "description": "Drive the fgate CLI: deploy safely, read errors, avoid invented flags.",
  "author": { "name": "<from existing metadata>" },
  "homepage": "<docs URL>",
  "repository": "<repo URL>",
  "license": "<SPDX id of LICENSE>",
  "keywords": ["fgate", "ferrisgate", "agent-skills"]
}
```

`.claude-plugin/marketplace.json` has no `version` in the entry, because `plugin.json` would win and the validator warns:
```json
{
  "name": "fgate",
  "owner": { "name": "<owner>" },
  "plugins": [
    { "name": "fgate", "source": "./", "description": "Agent skill for the fgate CLI." }
  ]
}
```

`.codex-plugin/plugin.json`:
```json
{
  "name": "fgate",
  "version": "0.0.0",
  "description": "Drive the fgate CLI: deploy safely, read errors, avoid invented flags.",
  "author": { "name": "<from existing metadata>" },
  "homepage": "<docs URL>",
  "repository": "<repo URL>",
  "license": "<SPDX id of LICENSE>",
  "skills": "./skills/",
  "interface": {
    "displayName": "fgate",
    "shortDescription": "Deploy with the fgate CLI",
    "developerName": "<owner>",
    "category": "Developer Tools",
    "capabilities": [],
    "websiteURL": "<docs URL>"
  }
}
```

`.cursor-plugin/plugin.json`:
```json
{
  "name": "fgate",
  "displayName": "fgate",
  "version": "0.0.0",
  "description": "Drive the fgate CLI: deploy safely, read errors, avoid invented flags.",
  "author": { "name": "<from existing metadata>" },
  "homepage": "<docs URL>",
  "repository": "<repo URL>",
  "license": "<SPDX id of LICENSE>",
  "skills": "./skills/"
}
```

`gemini-extension.json`:
```json
{ "name": "fgate", "version": "0.0.0", "description": "Drive the fgate CLI: deploy safely, read errors, avoid invented flags." }
```

## `skills/fgate/SKILL.md` requirements

The scripts depend on these:
- Frontmatter has `metadata.version: "0.0.0"`, quoted. `name: fgate` matches the directory.
- `compatibility: Requires the fgate CLI on PATH.` has no version number.
- The body opens with a `Skill version: 0.0.0` line outside any code fence, followed by the two-sided guard. Use the `acme` text in `references/skill-content-examples.md` with `fgate` swapped in. A dev build reports `dev`.
- Write `--yes`, never `-yes`.
- Mark intentionally wrong invocations under a `✗` label. Otherwise the gate fails on them.

## Not covered

- Golden agent tasks (gate 5). That is deferred by default.
- A gate 4 pull-request workflow. `make skill-gates` is the local version.
- Binary-only installs. If most users install via Homebrew, they get no skill. Then promote the bundled rung: `fgate skills install` with `//go:embed`, plus a drift notice. Say if you want it.

## Questions

1. Does `fgate` use stdlib `flag`, or cobra or pflag? This decides whether `-yes` is normal.
2. What is the real main package path and version variable? Paste your `.goreleaser.yaml` `builds:` block.
3. Is `fgate` run from a Go module that publishes a `skills/` directory in its zip, or only as a binary?