#!/usr/bin/env python3
"""Fail when a repository's agent skills or plugin manifests disagree with the release version.

Usage:
    python3 check-skill-version.py <expected-version> [--skills-dir skills]
        [--manifest PATH ...] [--tag-prefix PREFIX] [--allow-nested KEY ...] [--write]

<expected-version> is the code version being released: the git tag ("v1.4.0"), or the
value the release tool already bumped (package.json, pyproject.toml, a version constant).
A leading "v" is ignored on both sides of every comparison. --tag-prefix strips a
component prefix first, for monorepo tags such as "acme-cli-v1.4.0" or "cli/v1.4.0".

Checks, all offline and read-only:
  1. Every SKILL.md under <skills-dir> (any depth) has a quoted `metadata.version`
     equal to the expected version. `metadata` must be a flat block map of strings,
     as the Agent Skills spec defines it, except for keys named with --allow-nested
     (for example `openclaw`, which OpenClaw reads only as an indented block map).
  2. No SKILL.md carries a top-level `version:` key (the spec has none), and no
     `metadata` key appears twice.
  3. A body line "Skill version: X.Y.Z" outside code fences (the agent-visible copy of
     metadata.version, since some harnesses never show the frontmatter to the model)
     equals the expected version when present. A missing body line is a warning.
  4. Every --manifest JSON file has a top-level "version" equal to the expected version.
     For a marketplace file (a "plugins" array), every plugin entry that declares a
     "version" must match too. A warning is printed when an entry declares one, because
     some installers silently prefer the plugin manifest's own value.

With --write, the script first rewrites every SKILL.md `metadata.version`, every
"Skill version:" body line and every manifest "version" to the expected version (the bump step of a release), then runs the
checks. Use it in the commit the release tag will point at, never in a tag-triggered
job: a bump made after tagging never reaches the tag. Line endings and a trailing
comment on the version line (such as "# x-release-please-version") are preserved.

Supported frontmatter: block maps and block scalars. Multi-line plain scalars and flow
maps (`{...}`, `[...]`) under `metadata` are rejected rather than guessed at: strict
YAML loaders, including the spec's reference validator, refuse flow style.

Exit codes: 0 all checks pass; 1 at least one mismatch or unreadable SKILL.md in check
mode; 2 usage error, or any read/parse error under --write (nothing is written then).
Dependencies: Python 3.8+ standard library only.
"""

import argparse
import json
import re
import sys
from pathlib import Path

# Exit codes kept distinct so CI logs separate "stale skill" from "broken invocation".
EXIT_OK = 0
EXIT_MISMATCH = 1
EXIT_USAGE = 2

# The frontmatter block is the text between the first two lines that are exactly "---".
FRONTMATTER_DELIMITER = "---"
# YAML block-scalar indicators: content of `key: |` / `key: >` is text, never keys.
BLOCK_SCALAR = re.compile(r"^[|>][+-]?\d*$")
# A `key: value` line, capturing indentation, key, and the raw value after the colon.
KEY_LINE = re.compile(r"^(?P<indent>[ \t]*)(?P<key>[A-Za-z0-9_.-]+)\s*:(?P<rest>.*)$")
# The agent-visible version line in the SKILL.md body, e.g. "Skill version: 1.4.0".
BODY_VERSION = re.compile(r"^(?P<lead>[\s>*_`-]*Skill version:[*_`]*\s*`?)(?P<value>[^\s`*_]+)(?P<tail>.*)$")
# A flow collection value (`{...}` or `[...]`) after `key:` or a `- ` list marker.
FLOW_VALUE = re.compile(r"^[ \t]*(?:-[ \t]+)?(?:[A-Za-z0-9_.-]+[ \t]*:[ \t]*)?[{\[]")
# Split "value  # comment" so a trailing comment survives a rewrite.
VALUE_AND_COMMENT = re.compile(r"^(?P<value>.*?)(?P<comment>\s+#.*)?$")


class SkillParseError(ValueError):
    """The SKILL.md frontmatter has a shape this script refuses to guess about."""


def normalize(version, prefix=""):
    """Strip whitespace, quotes, an optional component prefix and one leading 'v'."""
    value = version.strip().strip("\"'")
    if prefix and value.startswith(prefix):
        value = value[len(prefix):]
    return value[1:] if value[:1] in ("v", "V") else value


def split_lines(text):
    """Return (lines, newline) keeping the file's own line ending; drop a UTF-8 BOM."""
    text = text.lstrip("﻿")
    newline = "\r\n" if "\r\n" in text else "\n"
    return text.replace("\r\n", "\n").split("\n"), newline


def frontmatter_bounds(lines):
    """Return the index of the closing '---' line, or raise when absent or unclosed."""
    if not lines or lines[0].strip() != FRONTMATTER_DELIMITER:
        raise SkillParseError("does not start with a '---' frontmatter line")
    for index in range(1, len(lines)):
        if lines[index].strip() == FRONTMATTER_DELIMITER:
            return index
    raise SkillParseError("frontmatter is never closed by a second '---' line")


def read_raw(path):
    """Read text without newline translation, so CRLF files can be written back as CRLF."""
    return path.read_bytes().decode("utf-8")


def write_raw(path, text):
    path.write_bytes(text.encode("utf-8"))


def indent_of(line):
    return len(line) - len(line.lstrip(" \t"))


def locate_versions(lines, end, allow_nested=()):
    """Find the top-level `version` line and the `metadata.version` line.

    Returns (top_level_index, metadata_index, metadata_version_index, child_indent),
    each None when absent. Only direct children of `metadata` count, the first
    `version` child wins, block-scalar text is skipped, a nested block map is skipped
    only under a key listed in allow_nested, and any other nested or flow map under
    `metadata` raises SkillParseError instead of being guessed at.
    """
    top_level = None
    metadata_at = None
    version_at = None
    child_indent = None
    in_metadata = False
    skip_deeper_than = None
    in_allowed_nested = False
    seen_keys = set()
    for index in range(1, end):
        line = lines[index]
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        depth = indent_of(line)
        if skip_deeper_than is not None and depth > skip_deeper_than:
            if in_allowed_nested and FLOW_VALUE.match(line):
                raise SkillParseError(f"line {index + 1}: flow value inside an allowed nested metadata block; use block style")
            continue
        skip_deeper_than = None
        in_allowed_nested = False
        match = KEY_LINE.match(line)
        rest = match.group("rest").split(" #", 1)[0].strip() if match else ""
        if depth == 0:
            key = match.group("key") if match else None
            in_metadata = key == "metadata"
            if in_metadata:
                metadata_at = index
                if rest:
                    raise SkillParseError("inline 'metadata:' value; write metadata as an indented block map")
            elif key == "version":
                top_level = index
            elif BLOCK_SCALAR.match(rest):
                skip_deeper_than = 0
            continue
        if not in_metadata:
            continue
        if child_indent is None:
            child_indent = depth
        if depth != child_indent or not match:
            raise SkillParseError(f"line {index + 1}: metadata must be a flat map of string values")
        key = match.group("key")
        if not rest:
            if key not in allow_nested:
                raise SkillParseError(f"line {index + 1}: nested map under metadata.{key}; the spec allows string values only (pass --allow-nested {key} to accept it)")
            skip_deeper_than = depth
            in_allowed_nested = True
        elif rest[:1] in ("{", "["):
            raise SkillParseError(f"line {index + 1}: flow value under metadata.{key}; write it as an indented block map")
        elif BLOCK_SCALAR.match(rest):
            skip_deeper_than = depth
            continue
        if key in seen_keys:
            raise SkillParseError(f"line {index + 1}: metadata.{key} appears twice; YAML readers keep the last one")
        seen_keys.add(key)
        if key == "version":
            version_at = index
    return top_level, metadata_at, version_at, child_indent


def read_skill(skill_file):
    lines, newline = split_lines(read_raw(skill_file))
    end = frontmatter_bounds(lines)
    return lines, newline, end


def version_value(line):
    """Return (raw_value, is_quoted) for a `version: ...` line."""
    rest = KEY_LINE.match(line).group("rest")
    value = VALUE_AND_COMMENT.match(rest.strip()).group("value").strip()
    quoted = len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"')
    if value[:1] in ("'", '"') and not quoted:
        raise SkillParseError(f"malformed metadata.version value {value}; a comment needs a space before '#'")
    return value, quoted


def body_versions(lines, end):
    """Return [(index, value)] for every "Skill version:" line in the body, outside code fences."""
    found = []
    in_fence = False
    for index in range(end + 1, len(lines)):
        if lines[index].lstrip().startswith(("```", "~~~")):
            # Fenced examples (for instance a "bad guard" sample) are documentation, not the live line.
            in_fence = not in_fence
            continue
        match = None if in_fence else BODY_VERSION.match(lines[index])
        if match:
            found.append((index, match.group("value")))
    return found


def write_skill_version(skill_file, expected, allow_nested=()):
    """Set metadata.version (quoted), adding the key or the metadata map when absent."""
    lines, newline, end = read_skill(skill_file)
    _, metadata_at, version_at, child_indent = locate_versions(lines, end, allow_nested)
    if version_at is not None:
        line = lines[version_at]
        match = KEY_LINE.match(line)
        comment = VALUE_AND_COMMENT.match(match.group("rest").strip()).group("comment") or ""
        lines[version_at] = f'{match.group("indent")}version: "{expected}"{comment}'
    elif metadata_at is not None:
        indent = " " * (child_indent or 2)
        lines.insert(metadata_at + 1, f'{indent}version: "{expected}"')
    else:
        lines[end:end] = ["metadata:", f'  version: "{expected}"']
        end += 2
    for index, _ in body_versions(lines, end):
        match = BODY_VERSION.match(lines[index])
        lines[index] = f'{match.group("lead")}{expected}{match.group("tail")}'
    write_raw(skill_file, newline.join(lines))


def write_manifest_version(manifest, expected):
    """Set "version" in a JSON manifest, keeping its indentation and line endings."""
    raw = read_raw(manifest)
    data = json.loads(raw)
    if not isinstance(data, dict):
        raise ValueError("top level is not a JSON object")
    plugins = data.get("plugins")
    if "version" in data or not isinstance(plugins, list):
        data["version"] = expected
    if isinstance(plugins, list):
        for entry in plugins:
            if isinstance(entry, dict) and "version" in entry:
                entry["version"] = expected
    match = re.search(r"\n([ \t]+)\S", raw)
    indent = match.group(1) if match else None
    newline = "\r\n" if "\r\n" in raw else "\n"
    text = json.dumps(data, indent=indent, ensure_ascii=False)
    write_raw(manifest, text.replace("\n", newline) + newline)


def check_skills(skills_dir, expected, prefix, errors, warnings, allow_nested=()):
    skill_files = sorted(skills_dir.rglob("SKILL.md"))
    if not skill_files:
        errors.append(f"no SKILL.md found under {skills_dir}/ - is --skills-dir right?")
        return 0
    for skill_file in skill_files:
        try:
            lines, _, end = read_skill(skill_file)
            top_level, _, version_at, _ = locate_versions(lines, end, allow_nested)
            value, quoted = version_value(lines[version_at]) if version_at is not None else (None, False)
        except (OSError, UnicodeDecodeError, SkillParseError) as err:
            errors.append(f"{skill_file}: {err}")
            continue
        body = body_versions(lines, end)
        if not body:
            warnings.append(f"{skill_file}: no 'Skill version: X.Y.Z' body line; agents that never see frontmatter cannot run the version guard")
        for index, found in body:
            if normalize(found, prefix) != expected:
                errors.append(f"{skill_file}:{index + 1}: body 'Skill version: {found}', release is {expected}")
        if top_level is not None:
            errors.append(f"{skill_file}: top-level 'version:' is not an Agent Skills field; move it under metadata")
        if version_at is None:
            errors.append(f"{skill_file}: metadata.version missing (expected \"{expected}\")")
            continue
        if not quoted:
            errors.append(f"{skill_file}: metadata.version {value} is unquoted; YAML may read it as a number - write \"{value}\"")
        if normalize(value, prefix) != expected:
            errors.append(f"{skill_file}: metadata.version is {value}, release is {expected}")
    return len(skill_files)


def check_manifest(manifest, expected, prefix, errors, warnings):
    try:
        data = json.loads(read_raw(manifest))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as err:
        errors.append(f"{manifest}: cannot read JSON: {err}")
        return
    if not isinstance(data, dict):
        errors.append(f"{manifest}: top level is not a JSON object")
        return
    plugins = data.get("plugins")
    if "version" not in data and not isinstance(plugins, list):
        errors.append(f"{manifest}: no top-level \"version\" field")
    elif "version" in data and normalize(str(data["version"]), prefix) != expected:
        errors.append(f"{manifest}: version is {data['version']}, release is {expected}")
    if isinstance(plugins, list):
        for entry in plugins:
            if isinstance(entry, dict) and "version" in entry:
                name = entry.get("name", "?")
                warnings.append(f"{manifest}: plugin '{name}' sets version; keep it in the plugin's own manifest only")
                if normalize(str(entry["version"]), prefix) != expected:
                    errors.append(f"{manifest}: plugin '{name}' version is {entry['version']}, release is {expected}")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("expected_version", help="release version, e.g. v1.4.0, 1.4.0 or acme-cli-v1.4.0")
    parser.add_argument("--skills-dir", default="skills", help="directory holding the skills (default: skills)")
    parser.add_argument("--manifest", action="append", default=[], help="JSON manifest to check; repeatable")
    parser.add_argument("--tag-prefix", default="", help="component prefix to strip, e.g. 'acme-cli-' or 'cli/'")
    parser.add_argument("--allow-nested", action="append", default=[], metavar="KEY", help="metadata key allowed to hold a nested block map, e.g. 'openclaw'; repeatable")
    parser.add_argument("--write", action="store_true", help="rewrite versions to the expected version before checking")
    args = parser.parse_args()

    if "version" in args.allow_nested:
        print("error: --allow-nested version is not allowed; metadata.version must stay a quoted string", file=sys.stderr)
        return EXIT_USAGE
    expected = normalize(args.expected_version, args.tag_prefix)
    if not expected:
        print("error: expected version is empty", file=sys.stderr)
        return EXIT_USAGE
    skills_dir = Path(args.skills_dir)
    if not skills_dir.is_dir():
        print(f"error: skills directory not found: {skills_dir}", file=sys.stderr)
        return EXIT_USAGE

    if args.write:
        current = None
        try:
            # Parse every manifest and skill before touching any file, so one bad
            # file never leaves the tree half-bumped.
            for manifest in args.manifest:
                current = manifest
                if Path(manifest).is_file() and not isinstance(json.loads(read_raw(Path(manifest))), dict):
                    raise ValueError("top level is not a JSON object")
            for skill_file in sorted(skills_dir.rglob("SKILL.md")):
                current = skill_file
                lines, _, end = read_skill(skill_file)
                _, _, version_at, _ = locate_versions(lines, end, args.allow_nested)
                if version_at is not None:
                    version_value(lines[version_at])
            for skill_file in sorted(skills_dir.rglob("SKILL.md")):
                current = skill_file
                write_skill_version(skill_file, expected, args.allow_nested)
            for manifest in args.manifest:
                current = manifest
                if Path(manifest).is_file():
                    write_manifest_version(Path(manifest), expected)
        except (OSError, UnicodeDecodeError, ValueError) as err:
            # json.JSONDecodeError and SkillParseError are ValueError subclasses.
            print(f"error: cannot rewrite versions in {current}: {err}", file=sys.stderr)
            return EXIT_USAGE

    errors = []
    warnings = []
    count = check_skills(skills_dir, expected, args.tag_prefix, errors, warnings, args.allow_nested)
    for manifest in args.manifest:
        path = Path(manifest)
        if not path.is_file():
            errors.append(f"{path}: manifest file not found")
            continue
        check_manifest(path, expected, args.tag_prefix, errors, warnings)

    for warning in warnings:
        print(f"warning: {warning}", file=sys.stderr)
    if errors:
        print(f"FAIL: {len(errors)} problem(s) against release {expected}:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return EXIT_MISMATCH
    print(f"OK: {count} skill(s) and {len(args.manifest)} manifest(s) match release {expected}")
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
