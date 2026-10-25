#!/usr/bin/env python3
"""Fail an API changelog publish when an entry and its sources disagree.

Usage:
  python3 scripts/check-entry-trace.py --diff changelog.json --entries entries.json \
      --api-version 2026-07-01 --acks acks.json [--fragments changes/]

--diff takes oasdiff `changelog -f json` findings (or another tool's output mapped to them:
unique "fingerprint", "level"), one spec per run. --entries takes the entries or the feed.
Fails when an entry covers no finding or fragment, changes its classification, carries
another version or no action; when a breaking or potentially breaking source has no entry;
when a breaking entry's approval ids do not cover all its sources.
Exit 0 pass, 1 trace failures, 2 unusable input. Python 3.8+, standard library only.
"""

import argparse
import json
import re
import sys
from pathlib import Path

# oasdiff JSON encodes ERR as 3, WARN as 2, INFO as 1. Word levels come from mapped
# output of other tools. Anything else is unusable input, never silently treated as INFO.
CLASSIFICATION_BY_LEVEL = {
    3: "breaking", "err": "breaking", "error": "breaking", "breaking": "breaking",
    2: "potentially-breaking", "warn": "potentially-breaking", "warning": "potentially-breaking",
    "dangerous": "potentially-breaking", "unclassified": "potentially-breaking",
    1: "non-breaking", "info": "non-breaking", "non-breaking": "non-breaking",
}

CLASSIFICATIONS = {"breaking", "potentially-breaking", "non-breaking"}
KINDS = {"added", "changed", "deprecated", "removed"}

# Classifications whose findings must reach the changelog and whose entries need an action.
MUST_ENTER = {"breaking", "potentially-breaking"}

# Rules about the release itself (version bumps), not contract changes: never entries.
META_CHECKS = {"api-version-not-bumped", "api-version-decreased", "api-major-version-not-bumped"}
META_SECTION = "info"

# Same normalization as build-entries.py: one entry may cover one change reached from several
# operations or property paths, never two different changes.
PROPERTY_PATH = re.compile(r"`(?:[^`/]+/)+([^`/]+)`")
SHARED_SUFFIX = re.compile(r"\s*\(shared schema:.*\)\s*$")


def change_of(finding):
    text = SHARED_SUFFIX.sub("", PROPERTY_PATH.sub(r"`\1`", str(finding.get("text") or "")))
    return (finding.get("id"), text)


def fail_input(message):
    print(f"error: {message}", file=sys.stderr)
    sys.exit(2)


def load_json(path):
    try:
        with open(path, encoding="utf-8") as handle:
            return json.load(handle)
    except OSError as exc:
        fail_input(f"cannot read {path}: {exc}")
    except json.JSONDecodeError as exc:
        fail_input(f"{path} is not valid JSON: {exc}")


def as_list(data, keys, path):
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        for key in keys:
            if isinstance(data.get(key), list):
                return data[key]
    fail_input(f"{path}: expected a JSON list or an object with one of {keys}")


def classify(finding, path):
    level = finding.get("level")
    if isinstance(level, str):
        level = level.strip().lower()
    if level not in CLASSIFICATION_BY_LEVEL:
        fail_input(f"{path}: finding {finding.get('fingerprint')} has missing or unknown level {level!r}")
    return CLASSIFICATION_BY_LEVEL[level]


def is_meta(finding):
    return finding.get("id") in META_CHECKS or finding.get("section") == META_SECTION


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--diff", action="append", default=[], help="structured diff JSON (repeatable)")
    parser.add_argument("--entries", required=True)
    parser.add_argument("--api-version", required=True)
    parser.add_argument("--acks")
    parser.add_argument("--fragments")
    args = parser.parse_args()

    if not args.diff and not args.fragments:
        fail_input("pass at least one --diff or --fragments source")

    findings = {}
    for diff_path in args.diff:
        for finding in as_list(load_json(diff_path), ("changes", "findings"), diff_path):
            if not isinstance(finding, dict):
                fail_input(f"{diff_path}: every finding must be a JSON object")
            key = str(finding.get("fingerprint") or "")
            if not key:
                fail_input(f"{diff_path}: a finding has no 'fingerprint' (map non-oasdiff output first)")
            if key in findings:
                fail_input(f"{diff_path}: duplicate fingerprint {key}")
            if is_meta(finding):
                continue
            finding["_classification"] = classify(finding, diff_path)
            findings[key] = finding

    fragments = {}
    if args.fragments:
        directory = Path(args.fragments)
        if not directory.is_dir():
            fail_input(f"{directory} is not a directory")
        for path in sorted(directory.glob("*.json")):
            fragment = load_json(path)
            if not isinstance(fragment, dict) or not fragment.get("id"):
                fail_input(f"{path}: fragment must be a JSON object with an id")
            if fragment.get("classification") not in CLASSIFICATIONS:
                fail_input(f"{path}: classification must be one of {sorted(CLASSIFICATIONS)}, got {fragment.get('classification')!r}")
            if fragment.get("kind") not in KINDS:
                fail_input(f"{path}: kind must be one of {sorted(KINDS)}, got {fragment.get('kind')!r}")
            versions = fragment.get("api_versions")
            if versions and args.api_version not in versions:
                continue
            fragments[str(fragment["id"])] = fragment

    entries = as_list(load_json(args.entries), ("entries",), args.entries)

    acks = None
    if args.acks:
        acks = {}
        for ack in as_list(load_json(args.acks), ("acks", "records"), args.acks):
            if isinstance(ack, dict) and ack.get("id"):
                acks[str(ack["id"])] = {str(c) for c in ack.get("covers", [])}

    problems = []
    entered = set()

    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            problems.append(f"entry #{index}: not a JSON object")
            continue
        label = str(entry.get("id") or f"#{index}")
        if entry.get("api_version") != args.api_version:
            problems.append(f"entry {label}: api_version {entry.get('api_version')!r}, expected {args.api_version!r}")
        classification = str(entry.get("classification") or "")
        if classification not in CLASSIFICATIONS:
            problems.append(f"entry {label}: classification must be one of {sorted(CLASSIFICATIONS)}, got {classification!r}")
        source = str(entry.get("source") or "")
        kind, _, detail = source.partition(":")
        covers = [str(c) for c in entry.get("covers") or []]

        if kind == "diff":
            if not covers:
                problems.append(f"entry {label}: diff entry has no covers list")
            changes = {change_of(findings[c]) for c in covers if c in findings}
            if len(changes) > 1:
                problems.append(f"entry {label}: covers {len(changes)} different changes; give each its own entry")
            for fingerprint in covers:
                finding = findings.get(fingerprint)
                if finding is None:
                    problems.append(f"entry {label}: covers {fingerprint}, but no finding has this fingerprint")
                    continue
                if detail and finding.get("id") and str(finding["id"]) != detail:
                    problems.append(f"entry {label}: source names check '{detail}', finding {fingerprint} is '{finding['id']}'")
                if finding["_classification"] != classification:
                    problems.append(f"entry {label}: classified {classification!r}, finding {fingerprint} is {finding['_classification']!r}")
                entered.add(fingerprint)
        elif kind == "declared":
            fragment = fragments.get(detail)
            if fragment is None:
                problems.append(f"entry {label}: source names fragment '{detail}', not found for this version")
            else:
                if fragment.get("classification") != classification:
                    problems.append(f"entry {label}: classified {classification!r}, fragment says {fragment.get('classification')!r}")
                entered.add(detail)
            # A declared entry stands for its fragment, whatever its covers field says.
            if covers and covers != [detail]:
                problems.append(f"entry {label}: declared entry covers {covers}, expected ['{detail}']")
            covers = [detail]
        else:
            problems.append(f"entry {label}: source must start with 'diff:' or 'declared:', got '{source}'")

        if classification in MUST_ENTER and not str(entry.get("action_required") or "").strip():
            problems.append(f"entry {label}: {classification} entry has no action_required")

        if classification == "breaking":
            approval = (entry.get("links") or {}).get("approval")
            approval_ids = [str(a) for a in approval] if isinstance(approval, list) else ([str(approval)] if approval else [])
            if acks is None:
                problems.append(f"entry {label}: breaking entry, but no --acks file was given to verify approval")
            elif not approval_ids:
                problems.append(f"entry {label}: breaking entry has no approval link")
            else:
                unknown = [a for a in approval_ids if a not in acks]
                if unknown:
                    problems.append(f"entry {label}: approval {', '.join(unknown)} not found in acknowledgement records")
                covered = set().union(*(acks.get(a, set()) for a in approval_ids))
                missing = [c for c in covers if c not in covered]
                if missing:
                    problems.append(f"entry {label}: approval {', '.join(approval_ids)} does not cover {', '.join(missing)}")

    for key, finding in findings.items():
        if finding["_classification"] in MUST_ENTER and key not in entered:
            problems.append(f"finding {key}: {finding['_classification']}, but no entry ({finding.get('text', '')})")

    for fragment_id in fragments:
        if fragment_id not in entered:
            problems.append(f"fragment {fragment_id}: declared change with no entry")

    print(f"findings: {len(findings)}  fragments: {len(fragments)}  entries: {len(entries)}")
    if problems:
        for problem in problems:
            print(f"FAIL {problem}")
        print(f"{len(problems)} trace failure(s)")
        sys.exit(1)
    print("OK every entry traces to a source; every breaking source has an entry")


if __name__ == "__main__":
    main()
