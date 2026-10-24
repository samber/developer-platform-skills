# Design: `check_skill.py`, a two-way check between SKILL.md and the CLI

I haven't run any of this, and I didn't touch your repo. I assumed a click/typer CLI and paths like `skills/nb/SKILL.md`, so adjust both. The script below is a design draft, not a tested tool.

## Why the requested check wouldn't have caught the bug

"Every command appears in the skill" is a **coverage** check. The 3.2 skill probably already mentioned every command, and `nb sync --legacy` would still have been in it. The bug was a **validity** failure: the skill mentioned something the CLI no longer accepts. Exempting `--legacy` by pattern would also bring back the original bug the next time someone writes a runnable `nb sync --legacy` line.

So the check needs both directions, and "removed" has to be a structured state rather than an allowlisted string.

## Rules

The CLI's own command tree is the single source of truth. Walk the click group; don't scrape `--help`.

| # | Rule | Direction |
|---|------|-----------|
| 1 | Every non-hidden leaf command has at least one `nb <path>` invocation in SKILL.md, in a code fence or inline code. | Coverage |
| 2 | Every `nb …` invocation outside the removed region must resolve: command path exists, and every flag exists on that command or an ancestor. | Validity |
| 3 | Removed items may appear only between `<!-- nb-removed:start -->` and `<!-- nb-removed:end -->`. Each one must match an entry in `removed.toml`. | Removal |
| 4 | Each `removed.toml` entry must really be absent from the CLI, and its `since` must be ≤ the current version. | Registry honesty |
| 5 | Inside the removed region, an invocation that does resolve is an error. The region can't be used to hide live commands. | Registry honesty |
| 6 | A hidden or internal command is skipped only if listed under `exempt` with a reason. | Explicit opt-out |
| 7 | If the extractor finds fewer than `MIN_INVOCATIONS` invocations, the check fails. | Fail-open guard |

With these rules, the `--legacy` mention passes only in the "removed" section and only if the registry records it. The same text in a normal bash fence fails rule 2.

## `removed.toml`

Someone has to fill in the real 3.0 removals from the changelog. I don't know them.

```toml
[[removed]]
command = "sync"
flag = "--legacy"
since = "3.0.0"

[[exempt]]
command = "debug dump"
reason = "internal, hidden from --help"
```

## SKILL.md convention

````markdown
## Removed in 3.0

<!-- nb-removed:start -->
`nb sync --legacy` no longer exists. Use `nb sync`.
<!-- nb-removed:end -->
````

## `scripts/check_skill.py`

```python
#!/usr/bin/env python3
"""Check SKILL.md against the real nb command tree, in both directions."""
import re
import shlex
import sys
import tomllib
from importlib.metadata import version
from pathlib import Path

import click
from packaging.version import Version

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "skills/nb/SKILL.md"
REGISTRY = ROOT / "skills/nb/removed.toml"
# Below this the extractor is assumed broken, not the skill empty.
MIN_INVOCATIONS = 5

START, END = "<!-- nb-removed:start -->", "<!-- nb-removed:end -->"
FENCE = re.compile(r"^\s*(```|~~~)")
INLINE = re.compile(r"`([^`\n]+)`")
SEPARATORS = re.compile(r"\s*(?:&&|\|\||[|;])\s*")
HELP_FLAGS = {"--help": False, "-h": False}


def build_tree():
    """Map command path -> (own flags {name: takes_value}, is_group, hidden)."""
    from nb.cli import main as root  # adapt: argparse CLIs walk _SubParsersAction

    tree = {}

    def walk(cmd, path):
        ctx = click.Context(cmd)
        flags = dict(HELP_FLAGS)
        for p in cmd.get_params(ctx):
            for opt in (*p.opts, *p.secondary_opts):
                flags[opt] = not getattr(p, "is_flag", False)
        is_group = isinstance(cmd, click.Group)
        tree[path] = (flags, is_group, cmd.hidden)
        if is_group:
            for name in cmd.list_commands(ctx):
                walk(cmd.get_command(ctx, name), path + (name,))

    walk(root, ())
    return tree


def snippets(text):
    """Yield (lineno, code, in_removed_region)."""
    removed = in_fence = False
    buf = ""
    for n, line in enumerate(text.splitlines(), 1):
        if START in line:
            removed = True
        elif END in line:
            removed = False
        elif FENCE.match(line):
            in_fence = not in_fence
        elif in_fence:
            if line.rstrip().endswith("\\"):
                buf += line.rstrip()[:-1] + " "
            else:
                yield n, buf + line, removed
                buf = ""
        else:
            for m in INLINE.finditer(line):
                yield n, m.group(1), removed


def invocations(code):
    for seg in SEPARATORS.split(code):
        seg = seg.strip().removeprefix("$ ").strip()
        if seg == "nb" or seg.startswith("nb "):
            yield seg


def resolve(argv, tree):
    """Return (final path, problems); a problem is (path, flag-or-None)."""
    path, problems, i = (), [], 1
    while i < len(argv):
        tok = argv[i]
        known = {}
        for k in range(len(path) + 1):
            known.update(tree[path[:k]][0])
        if tok.startswith("-"):
            name = tok.split("=", 1)[0]
            if name not in known:
                problems.append((path, name))
            elif known[name] and "=" not in tok:
                i += 1  # flag consumes the next token as its value
        elif tok[0] in "<[":
            pass  # placeholder such as <command>
        elif tree[path][1]:  # group: next bare token must be a subcommand
            nxt = path + (tok,)
            if nxt not in tree:
                problems.append((nxt, None))
                break
            path = nxt
        i += 1
    return path, problems


def main():
    tree = build_tree()
    reg = tomllib.loads(REGISTRY.read_text())
    removed = [(tuple(e["command"].split()), e.get("flag"), e["since"]) for e in reg.get("removed", [])]
    exempt = {tuple(e["command"].split()) for e in reg.get("exempt", [])}
    current = Version(version("nb"))
    errors, covered, seen = [], set(), 0

    for path, flag, since in removed:  # rules 4
        exists = path in tree and (flag is None or flag in tree[path][0])
        if exists:
            errors.append(f"removed.toml: `{' '.join(path)} {flag or ''}` still exists in the CLI")
        if Version(since) > current:
            errors.append(f"removed.toml: since={since} is newer than installed {current}")

    for n, code, in_removed in snippets(SKILL.read_text()):
        for inv in invocations(code):
            seen += 1
            try:
                argv = shlex.split(inv)
            except ValueError:
                errors.append(f"SKILL.md:{n}: cannot parse `{inv}`")
                continue
            path, problems = resolve(argv, tree)
            if in_removed:  # rules 3 and 5
                if not problems:
                    errors.append(f"SKILL.md:{n}: `{inv}` is valid but sits in the removed region")
                for p, f in problems:
                    if not any(p == rp and f == rf for rp, rf, _ in removed):
                        errors.append(f"SKILL.md:{n}: `{inv}` is not in removed.toml")
            else:  # rule 2
                covered.add(path)
                for p, f in problems:
                    errors.append(f"SKILL.md:{n}: `{inv}` is invalid: unknown {f or ' '.join(p)}")

    if seen < MIN_INVOCATIONS:  # rule 7
        errors.append(f"extractor found only {seen} invocations; refusing to pass")

    for path, (_, is_group, hidden) in tree.items():  # rule 1
        if path and not is_group and not hidden and path not in covered and path not in exempt:
            errors.append(f"coverage: `nb {' '.join(path)}` is missing from SKILL.md")

    print("\n".join(errors) or f"ok: {seen} invocations, {len(covered)} commands covered")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
```

## Tests for the checker (`tests/test_check_skill.py`)

A safety check can pass because it can't see anything, so test that it fails when it should:

1. **Positive control:** the real SKILL.md passes.
2. **The reported bug:** put `nb sync --legacy` in a plain ```` ```bash ```` fence in a copy of the skill. The check must fail with an "invalid" error.
3. **Legitimate removal:** the same text inside the removed markers with a registry entry passes. Without the registry entry it fails.
4. **Stale registry:** add an entry for a flag that still exists. The check must fail.
5. **Coverage:** delete one command's section from a copy. The check must fail and name that command.
6. **Dead extractor:** run it on a skill with no code blocks. It must fail on rule 7, not pass.
7. **Pivot cases:** a flag with `=value`, a backslash-continued line, `nb a && nb b`, a `<placeholder>`, and a typo'd subcommand (`nb synk`).

## CI wiring

- Run on **every PR** that touches `src/nb/**` or `skills/**`, not only at release. The `--legacy` drift happened between releases, and the version check never looked at content.
- Keep the existing version-match check as is.
- Make the check a required status. Don't allow `|| true` on it.

## What this does not guarantee

- It guarantees every visible command is present and that nothing the skill tells agents to run is syntactically invalid. It does **not** guarantee the prose is correct. A command can exist while its behavior, defaults, or flag meaning changed.
- To go further, tag some examples as runnable and execute them in a sandbox in CI. Even `nb <path> --help` exit-0 on every referenced command catches more. I'd add that as a second step once this lands.
- "Complete coverage" here means commands, not flags. A flag-level coverage rule would force the skill to document every flag, and I'd push back on that for agent-facing text.

## Decisions for product and you

1. Which hidden or internal commands go under `exempt`? That's a product call, so it needs to be an explicit list.
2. Do you want removed entries pruned after N majors? I'd keep them forever. They're cheap and they guard against someone re-adding the text.
3. Someone needs to populate `removed.toml` from the 3.0 changelog. The first run will probably surface other stale references besides `--legacy`.