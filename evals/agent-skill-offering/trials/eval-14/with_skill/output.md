**Step 1: create `skills/rushmere/SKILL.md` in the rushmere repo.** Draft below. Total time is about 3.5 hours, so it fits the afternoon.

I read the three agent failures and your constraints against the skill. I did not run any of this against your repo. You did not give me rushmere's real signature or its `strict` default, so I marked the spots to fill in.

## Confirm 4 things first (2 minutes)

1. **Correct argument order.** You wrote `validate(schema, data)` as the swapped call, so I assumed the correct order is `validate(data, schema)`. Reverse the draft if I am wrong.
2. **`pyproject.toml` has a static `version`.** A dynamic version such as hatch-vcs changes the gate commands.
3. **Tags look like `v2.1.0`.**
4. **Repo license.** Use its SPDX id in the `license:` line.

## What to ship

- **Where:** inside the rushmere repo, at `skills/rushmere/SKILL.md`. The community skill lives in someone else's repo, so it cannot match your tags.
- **Gates:** spec validation, version equality, content check and security scan, all before the tag. Gate 4 (changed-surface) and gate 5 (golden agent tasks) are deferred. That deviates from the default, which runs gate 4 on pull requests. I cut it because of your afternoon ceiling.
- **Install:** tag-pinned git commands, printed in the README and every release note.
- **Not this week:** an MCP server, a bundled `rushmere skills install` subcommand, and the Anthropic directory submission.

## 1. The skill (45 min)

Everything under this heading is the file content. I assumed MIT in the `license:` line. Put your repo's real license there.

````markdown
---
name: rushmere
description: Guides correct use of the rushmere Python data-validation library - calling rushmere.validate with the right argument order, surfacing validation errors instead of hiding them, and migrating off the removed rushmere.legacy module. Use whenever the user writes or reviews Python that imports rushmere, calls rushmere.validate, sets strict=, or hits an ImportError on rushmere.legacy, even if they never say "validation library".
license: MIT
compatibility: Requires the rushmere package installed in the project's Python environment.
metadata:
  version: "2.1.0"
---

# rushmere

Skill version: 2.1.0
Read the installed version before writing code: `python -c "import importlib.metadata as m; print(m.version('rushmere'))"`.
- Same major.minor: continue. If only the patch differs, mention the matching tag once.
- Major or minor differs, in either direction: trust `help(rushmere.validate)` and the package's own docstrings over this skill, and tell the user to install the skill from their version's tag.
- Major 1: this skill does not apply. `rushmere.legacy` still exists there.

For exact signatures run `python -c "import inspect, rushmere; print(inspect.signature(rushmere.validate))"`. This skill covers which call to make and when.

## Validate data against a schema

Data comes first, schema second. Agents often swap them.

```python
import rushmere

rushmere.validate(data, schema)
```

Let validation errors propagate, or catch the exception class documented in `help(rushmere.validate)`. Show the error to the user.

## Leave `strict` alone

Never pass `strict=False` to make an error go away. It hides real validation errors. Leave `strict` unset. When validation fails, fix the data or the schema, or ask the user.

## Removed in 2.0: rushmere.legacy

```text
rushmere.legacy was removed in 2.0. Never import it.
Replace each legacy call with its 2.x equivalent: <FILL FROM YOUR 2.0 MIGRATION GUIDE>.
```
````

Fill the `<FILL ...>` line from your 2.0 migration notes before shipping. The version string `2.1.0` is a placeholder. The bump script rewrites it in step 2.

Three notes on the draft:

- **Description:** it is built to trigger on `import rushmere`, `rushmere.validate`, `strict=` and `rushmere.legacy`, which are the strings agents actually hit.
- **Argument order:** once you have the real signature, switch the example to keyword arguments if the signature allows them. The content gate in step 3 then checks the keyword names, which makes the call order-proof.
- **Failure 2, `rushmere.legacy`:** the removal sits in a `text` fence so the gate skips it. The removal is stated in prose, not hidden in code.

## 2. Version wiring (20 min)

1. Copy `check-skill-version.py` from the skill into your repo as `scripts/check-skill-version.py`. It is standard library only and needs Python 3.8 or newer.
2. Add this Makefile target. It bumps, gates, commits, tags and pushes in one step. Replace the `uv version` line with however you bump `pyproject.toml` today.

```make
MANIFESTS = --manifest .claude-plugin/plugin.json --manifest .claude-plugin/marketplace.json

release: # usage: make release VERSION=2.1.0
	uv version $(VERSION)
	python3 scripts/check-skill-version.py $(VERSION) --write --skills-dir skills $(MANIFESTS)
	python3 -m build
	python3 -m venv /tmp/rushmere-gate && /tmp/rushmere-gate/bin/pip install dist/*.whl
	/tmp/rushmere-gate/bin/python scripts/check-skill-content.py skills
	git commit -am "chore: release v$(VERSION)"
	git tag v$(VERSION) && git push origin HEAD v$(VERSION)
```

`--write` updates `metadata.version`, the `Skill version:` body line and every manifest in the commit that the tag points at. A bump made after tagging never reaches the tag.

## 3. Content gate (60 min)

Save as `scripts/check-skill-content.py`. It extracts the `python` fences from `skills/` and checks them against the installed build:

- imports resolve
- every `rushmere.x` attribute exists
- call arguments fit the real signature

```python
#!/usr/bin/env python3
"""Fail when a python block in skills/ uses a rushmere symbol the installed build lacks.

Usage: check-skill-content.py <skills-dir>
Run it against the built wheel installed in a clean venv, never the source tree.
"""
import ast
import importlib
import inspect
import re
import sys
from pathlib import Path

PACKAGE = "rushmere"
# Only ```python fences are checked; use ```text for pseudo-code and removed APIs.
FENCE = re.compile(r"^```python\n(.*?)^```", re.S | re.M)


def resolve(node, aliases):
    """Return the object a dotted name rooted at the package refers to, else None."""
    if isinstance(node, ast.Name):
        return aliases.get(node.id)
    if isinstance(node, ast.Attribute):
        base = resolve(node.value, aliases)
        if base is None:
            return None
        if not hasattr(base, node.attr):
            raise AttributeError(f"no attribute {node.attr!r}")
        return getattr(base, node.attr)
    return None


def bind_imports(tree, errors):
    aliases = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.split(".")[0] != PACKAGE:
                    continue
                try:
                    module = importlib.import_module(alias.name)
                except ImportError as exc:
                    errors.add((node.lineno, f"import failed: {exc}"))
                    continue
                if alias.asname:
                    aliases[alias.asname] = module
                else:
                    aliases[PACKAGE] = importlib.import_module(PACKAGE)
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            if node.module.split(".")[0] != PACKAGE:
                continue
            try:
                module = importlib.import_module(node.module)
            except ImportError as exc:
                errors.add((node.lineno, f"import failed: {exc}"))
                continue
            for alias in node.names:
                try:
                    obj = getattr(module, alias.name, None) or importlib.import_module(
                        f"{node.module}.{alias.name}")
                except ImportError:
                    errors.add((node.lineno, f"{node.module} has no {alias.name!r}"))
                    continue
                aliases[alias.asname or alias.name] = obj
    return aliases


def check_call(call, target):
    try:
        params = list(inspect.signature(target).parameters.values())
    except (TypeError, ValueError):
        return []
    errors = []
    kinds = inspect.Parameter
    accepts_kwargs = any(p.kind is kinds.VAR_KEYWORD for p in params)
    accepts_varargs = any(p.kind is kinds.VAR_POSITIONAL for p in params)
    keyword_names = {p.name for p in params
                     if p.kind in (kinds.POSITIONAL_OR_KEYWORD, kinds.KEYWORD_ONLY)}
    max_positional = sum(1 for p in params
                         if p.kind in (kinds.POSITIONAL_ONLY, kinds.POSITIONAL_OR_KEYWORD))
    has_star = any(isinstance(a, ast.Starred) for a in call.args)
    if not accepts_varargs and not has_star and len(call.args) > max_positional:
        errors.append(f"{len(call.args)} positional args, signature takes {max_positional}")
    for kw in call.keywords:
        if kw.arg and kw.arg not in keyword_names and not accepts_kwargs:
            errors.append(f"unknown keyword {kw.arg!r}")
    return errors


def check_block(code):
    errors = set()
    try:
        tree = ast.parse(code)
    except SyntaxError as exc:
        return {(exc.lineno or 1, f"syntax error: {exc.msg}")}
    aliases = bind_imports(tree, errors)
    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute):
            try:
                resolve(node, aliases)
            except AttributeError as exc:
                errors.add((node.lineno, str(exc)))
        elif isinstance(node, ast.Call):
            try:
                target = resolve(node.func, aliases)
            except AttributeError:
                continue  # already reported through the Attribute node
            if target is not None and callable(target):
                for message in check_call(node, target):
                    errors.add((node.lineno, message))
    return errors


def main(argv):
    if len(argv) != 2:
        print(__doc__)
        return 2
    package = importlib.import_module(PACKAGE)
    print(f"checking against {package.__file__}")
    failed = False
    for path in sorted(Path(argv[1]).rglob("*.md")):
        text = path.read_text(encoding="utf-8")
        for match in FENCE.finditer(text):
            first_code_line = text.count("\n", 0, match.start()) + 2
            for lineno, message in sorted(check_block(match.group(1))):
                print(f"{path}:{first_code_line + lineno - 1}: {message}")
                failed = True
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
```

This gate **cannot catch swapped positional arguments**, because it checks names and counts, not types. Only keyword-argument examples (see the note after the skill) or a golden agent task can guard failure 1. Say so in your PR description.

## 4. CI: one reusable workflow (20 min)

Create `.github/workflows/skill-gates.yml`. It runs on pull requests and is called from the release workflow, so the same gates run before the PyPI upload:

```yaml
name: skill-gates
on:
  pull_request:
    paths: ["skills/**", "src/**", "pyproject.toml", ".claude-plugin/**"]
  workflow_call:
jobs:
  skill-gates:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - name: Read version source of truth
        run: echo "PYVER=$(python3 -c "import tomllib;print(tomllib.load(open('pyproject.toml','rb'))['project']['version'])")" >> "$GITHUB_ENV"
      - name: Tag equals pyproject version
        if: startsWith(github.ref, 'refs/tags/')
        run: test "${GITHUB_REF_NAME#v}" = "$PYVER"
      - name: Skill version matches code version
        run: |
          python3 scripts/check-skill-version.py "$PYVER" --skills-dir skills \
            --manifest .claude-plugin/plugin.json --manifest .claude-plugin/marketplace.json
      - name: Build artifacts
        run: python3 -m pip install build && python3 -m build
      - name: sdist carries the skill
        run: tar tzf dist/*.tar.gz | grep -q 'skills/rushmere/SKILL.md'
      - name: Content check against the built wheel
        run: |
          python3 -m venv /tmp/gate && /tmp/gate/bin/pip install dist/*.whl
          /tmp/gate/bin/python scripts/check-skill-content.py skills
      - uses: astral-sh/setup-uv@1c37ad07a6a961277cf70c0d37d6f313000f5884 # v10.3.0
      - name: Run Snyk Agent Scan
        if: github.event.pull_request.head.repo.full_name == github.repository || github.event_name != 'pull_request'
        run: uvx snyk-agent-scan@latest --ci --dangerously-run-mcp-servers --skills ./skills
        env:
          SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
```

In your tag-push workflow, add the gate job and make the trusted-publishing job wait for it:

```yaml
jobs:
  skill-gates:
    uses: ./.github/workflows/skill-gates.yml
  publish:
    needs: skill-gates
    # existing trusted-publishing job, unchanged (permissions: id-token: write)
```

Five cautions:

- **Backstop only.** In the tag workflow the tag already exists, so a failure there means deleting the tag. The real gate is `make release` plus the pull-request run. The workflow stops a stale skill from reaching PyPI, nothing more.
- **Packaging.** hatchling includes `skills/` in the sdist by default. With setuptools, add `graft skills` to `MANIFEST.in`. Add the same directory to the wheel only if you want it there (hatchling: `force-include`).
- **Snyk.** It needs a `SNYK_TOKEN` repo secret, and it uploads skill content to Snyk. If you have no Snyk account, drop the scan step this week and log the gap. Pin the version instead of `@latest`.
- **Spec validation (gate 1).** Add `skills-ref` with a pinned version. I did not wire it above, because its entry-point name must be checked at install time. `check-skill-version.py` already rejects a top-level `version:`, a duplicate key, and an unquoted or flow-style `metadata`.
- **Fork pull requests.** The Snyk step is skipped for them, since forks get no secrets.

## 5. Manifests (20 min)

Create `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json`.

- **`plugin.json` fields:** `name: "rushmere"`, `version`, `description`, `author`, `homepage`, `repository`, `license`, `keywords`. Copy the author, homepage and repository from `pyproject.toml`.
- **`marketplace.json` entry:** `name: "rushmere"`, `source: "./"`, and **no `version` in the entry**. When both are set, `plugin.json` wins silently.
- **If time remains:** `.codex-plugin/plugin.json` (add `skills: "./skills/"`), `.cursor-plugin/plugin.json` and `gemini-extension.json`. Append each to `MANIFESTS` and to the workflow's `--manifest` flags.
- **No stray `version` fields.** Gate 2 fails the release if any manifest disagrees with `pyproject.toml`.

## 6. README and release notes (20 min)

Print installs with a placeholder, so the README never goes stale. The README install section also drives the skills.sh listing.

```text
Agent skill: install the tag that matches `pip show rushmere`.
  gh skill install <owner>/rushmere rushmere@v<installed-version>
  npx skills add <owner>/rushmere#v<installed-version>
```

Generate the same block, with the real tag, in every GitHub release note. Never type the tag by hand. Add the repo topics `agent-skills` and `gemini-cli-extension`.

## 7. The wrong community skill

You cannot delete it, and I could not verify any takedown or dispute process on skills.sh. Do not plan around one.

1. **Ship yours under the same `rushmere` name from the official repo**, and link the install from your docs. Agents resolve by name, so being the obvious source matters.
2. **Open a polite issue or PR on their repo.** Name the wrong lines, link the official skill, and ask them to redirect or archive. Keep the text public-safe.
3. **Do not copy their text.** Its license is unknown.
4. **Do not tell agents to fetch or follow it.** Audits flag that pattern.

## 8. Dry-run before you call it done (20 min)

The setup passes only if both checks below fail the way they should:

1. **Stale version.** Hand-edit `metadata.version` to the wrong value and run `make release VERSION=x.y.z` on a scratch branch with the push line removed. It must fail before any tag exists.
2. **Removed symbol.** Add `rushmere.legacy` to a `python` fence. The content gate must fail with a file and line.

If either run passes, the gate is broken. Fix it before Friday.

## Timeline for the afternoon

| Step | Time |
| --- | --- |
| 1. Skill file | 45 min |
| 2. Version wiring | 20 min |
| 3. Content gate | 60 min |
| 4. CI | 20 min |
| 5. Manifests | 20 min |
| 6. README and notes | 20 min |
| 8. Dry-run | 20 min |

That sums to about 3 hours 25 minutes, so budget 3.5 hours.

## Deferred, with triggers

- **Gate 4** (changed-surface check): add it after Friday.
- **Gate 5** (golden agent tasks): promote it after the first issue traced to a wrong skill.
- **Bundled docs plus an `AGENTS.md` pointer:** add it if agents still import `rushmere.legacy` after the skill is installed. On-demand skills sometimes never load.
- **Plugin directory submission:** later.

Separately, you could make `rushmere.legacy` an import stub that raises a clear "removed in 2.0, use X" error, and make `validate` raise a clear `TypeError` on swapped arguments. Agents read error messages, so that fixes failures 1 and 2 even when no skill loads. That changes the tool's code, so I did not include it.

**Next:** run `pip show rushmere` and `python -c "import inspect, rushmere; print(inspect.signature(rushmere.validate))"`. Paste the signature and your answers to the four confirmations. I will fix the draft's argument order and swap in keyword-argument examples.