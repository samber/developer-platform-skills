#!/usr/bin/env python3
"""Build changelog entry skeletons for one API version, or the tool ignore file, from records.

Usage:
  python3 scripts/build-entries.py --changelog changelog.json --api-version 2026-07-01 \
      --date 2026-07-01 --acks acks.json [--fragments changes/] --out entries.json
  python3 scripts/build-entries.py --acks acks.json --ignore-out oasdiff-err-ignore.txt

--changelog takes oasdiff `changelog -f json` for the release baseline, audience-filtered,
one spec per run (or another tool's output mapped to "id", "level", "fingerprint",
"operation", "path", "text"). Entries leave "summary" and "action_required" for a human.
Only findings oasdiff marks with one sharedSchema are grouped; never on text alone.
--ignore-out writes oasdiff ignore lines from acknowledgements that name a location.
Exit 0 written, 1 written with notices to act on, 2 unusable input. Python 3.8+, stdlib only.
"""

import argparse
import datetime
import json
import re
import sys
from pathlib import Path

# Same level table as check-entry-trace.py: oasdiff JSON uses 3/2/1, mapped output of other
# tools may use words. Anything else is unusable input.
CLASSIFICATION_BY_LEVEL = {
    3: "breaking", "err": "breaking", "error": "breaking", "breaking": "breaking",
    2: "potentially-breaking", "warn": "potentially-breaking", "warning": "potentially-breaking",
    "dangerous": "potentially-breaking", "unclassified": "potentially-breaking",
    1: "non-breaking", "info": "non-breaking", "non-breaking": "non-breaking",
}
CLASSIFICATIONS = {"breaking", "potentially-breaking", "non-breaking"}
KINDS = {"added", "changed", "deprecated", "removed"}

# Sort order inside a version: what costs callers work comes first.
CLASSIFICATION_ORDER = {"breaking": 0, "potentially-breaking": 1, "non-breaking": 2}

# Rules about the release itself (version bumps), not contract changes: never entries.
META_CHECKS = {"api-version-not-bumped", "api-version-decreased", "api-major-version-not-bumped"}
META_SECTION = "info"

# Check-id fragments that contain -added/-removed but change something callers already use:
# an added scope, removed anonymous access, a new enum value, a new pattern constraint.
CHANGED_NOT_ADDED_OR_REMOVED = ("security", "anonymous", "enum-value", "pattern", "became-")

ISO_DATE = re.compile(r"\d{4}-\d{2}-\d{2}")

# oasdiff names a shared-schema change at one property path (`tax/legacy_amount`) and appends
# "(shared schema: ...)". Strip both so two removals in one schema stay two changes while
# the same removal reached from several operations groups into one.
PROPERTY_PATH = re.compile(r"`(?:[^`/]+/)+([^`/]+)`")
SHARED_SUFFIX = re.compile(r"\s*\(shared schema:.*\)\s*$")


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


def as_list(data, path):
    if isinstance(data, list):
        return data
    fail_input(f"{path}: expected a JSON list")


def classify(level, where):
    if isinstance(level, str):
        level = level.strip().lower()
    if level not in CLASSIFICATION_BY_LEVEL:
        fail_input(f"{where}: missing or unknown level {level!r}")
    return CLASSIFICATION_BY_LEVEL[level]


def kind_of(check_id):
    if "deprecated" in check_id:
        return "deprecated"
    if any(marker in check_id for marker in CHANGED_NOT_ADDED_OR_REMOVED):
        return "changed"
    if "-removed" in check_id:
        return "removed"
    if "-added" in check_id:
        return "added"
    return "changed"


def write_text(path, text):
    try:
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(text)
    except OSError as exc:
        fail_input(f"cannot write {path}: {exc}")


def write_ignore_file(acks, path):
    lines = []
    for ack in acks:
        text = ack.get("text")
        if not text:
            continue
        if ack.get("operation") and ack.get("path"):
            lines.append(f"{ack['operation']} {ack['path']} {text}  # {ack.get('id')}")
        else:
            lines.append(f"components {text}  # {ack.get('id')}")
    write_text(path, "\n".join(lines) + ("\n" if lines else ""))
    print(f"wrote {len(lines)} ignore line(s) to {path}")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--changelog")
    parser.add_argument("--api-version")
    parser.add_argument("--date", help="release date, YYYY-MM-DD")
    parser.add_argument("--fragments")
    parser.add_argument("--acks")
    parser.add_argument("--api", default="", help="API name written into the feed")
    parser.add_argument("--out")
    parser.add_argument("--ignore-out")
    args = parser.parse_args()

    acks = as_list(load_json(args.acks), args.acks) if args.acks else []

    if args.ignore_out:
        write_ignore_file(acks, args.ignore_out)
        if not args.changelog and not args.fragments:
            sys.exit(0)

    if not args.changelog and not args.fragments:
        fail_input("pass --changelog, --fragments, or both (or only --acks with --ignore-out)")
    for name in ("api_version", "date", "out"):
        if not getattr(args, name):
            fail_input(f"--{name.replace('_', '-')} is required when building entries")
    if not ISO_DATE.fullmatch(args.date):
        fail_input(f"--date must be YYYY-MM-DD, got {args.date}")
    try:
        datetime.date.fromisoformat(args.date)
    except ValueError:
        fail_input(f"--date is not a real date: {args.date}")

    notices = []
    findings = []
    seen = set()
    if args.changelog:
        for finding in as_list(load_json(args.changelog), args.changelog):
            fingerprint, check = finding.get("fingerprint"), finding.get("id")
            if not fingerprint or not check:
                fail_input(f"{args.changelog}: every finding needs 'id' and 'fingerprint'")
            if fingerprint in seen:
                fail_input(f"{args.changelog}: duplicate fingerprint {fingerprint}")
            seen.add(fingerprint)
            if check in META_CHECKS or finding.get("section") == META_SECTION:
                continue
            finding["_classification"] = classify(finding.get("level"), f"{args.changelog}: finding {fingerprint}")
            findings.append(finding)

    location_count = {}
    for finding in findings:
        key = (finding.get("id"), finding.get("operation"), finding.get("path"), finding.get("text"))
        location_count[key] = location_count.get(key, 0) + 1

    def approval_for(source_id, finding=None):
        for ack in acks:
            if source_id in ack.get("covers", []):
                return ack.get("id")
        if finding is None:
            return None
        # Fingerprints move when the baseline moves (PR merge base vs release tag). Re-match
        # only on check + operation + path + exact tool text, and only when one finding in
        # this run has that exact location: a shared location never inherits an approval.
        key = (finding.get("id"), finding.get("operation"), finding.get("path"), finding.get("text"))
        for ack in acks:
            if (ack.get("check"), ack.get("operation"), ack.get("path"), ack.get("text")) == key:
                if location_count[key] != 1:
                    notices.append(f"ack {ack.get('id')}: ambiguous match ({location_count[key]} findings at one location); approve each explicitly")
                    return None
                notices.append(f"ack {ack.get('id')} matched {source_id} by location and text; add {source_id} to its covers")
                return ack.get("id")
        return None

    # Group only what oasdiff itself marks as one shared-schema change. Identical text on
    # unrelated operations is two changes and stays two entries.
    groups = {}
    for finding in findings:
        shared = (finding.get("sharedSchema") or {}).get("name")
        change = SHARED_SUFFIX.sub("", PROPERTY_PATH.sub(r"`\1`", finding.get("text", "")))
        key = ("shared", finding["id"], finding["_classification"], shared, change) if shared else ("one", finding["fingerprint"])
        groups.setdefault(key, []).append(finding)

    entries = []
    for members in groups.values():
        first = members[0]
        classification = first["_classification"]
        targets = []
        for member in members:
            operation, path = member.get("operation"), member.get("path")
            target = f"{operation} {path}" if operation and path else (path or member.get("section") or "components")
            if target not in targets:
                targets.append(target)
        covers = [member["fingerprint"] for member in members]
        member_approvals = {m["fingerprint"]: approval_for(m["fingerprint"], m) for m in members}
        approvals = sorted({a for a in member_approvals.values() if a})
        unapproved = [fp for fp, a in member_approvals.items() if not a]
        if classification == "breaking" and unapproved:
            notices.append(f"breaking finding(s) {', '.join(unapproved)} ({first['id']}) have no acknowledgement record")
        entries.append({
            "id": f"{args.api_version}/{covers[0]}",
            "api_version": args.api_version,
            "date": args.date,
            "area": "",
            "operations": targets,
            "shared_schema": (first.get("sharedSchema") or {}).get("name"),
            "kind": kind_of(first["id"]),
            "classification": classification,
            "source": f"diff:{first['id']}",
            "covers": covers,
            "summary": "",
            "tool_text": first.get("text", ""),
            "action_required": "",
            "sunset": None,
            "links": {"migration": None, "approval": approvals[0] if len(approvals) == 1 else (approvals or None)},
        })

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
            fragment_id = str(fragment["id"])
            approval = approval_for(fragment_id)
            if fragment["classification"] == "breaking" and not approval:
                notices.append(f"declared breaking change {fragment_id} has no acknowledgement record")
            entries.append({
                "id": f"{args.api_version}/{fragment_id}",
                "api_version": args.api_version,
                "date": args.date,
                "area": fragment.get("area", ""),
                "operations": fragment.get("operations", []),
                "shared_schema": None,
                "kind": fragment["kind"],
                "classification": fragment["classification"],
                "source": f"declared:{fragment_id}",
                "covers": [fragment_id],
                "summary": fragment.get("summary", ""),
                "tool_text": "",
                "action_required": fragment.get("action_required", ""),
                "sunset": fragment.get("sunset"),
                "links": {"migration": (fragment.get("links") or {}).get("migration"), "approval": approval},
            })

    entries.sort(key=lambda e: (CLASSIFICATION_ORDER.get(e.get("classification"), len(CLASSIFICATION_ORDER)),
                                e.get("area") or "", e.get("operations") or []))
    feed = {
        "feed_version": 1,
        "api": args.api,
        "generated_at": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "entries": entries,
    }
    write_text(args.out, json.dumps(feed, indent=2) + "\n")

    print(f"wrote {len(entries)} entries for {args.api_version} to {args.out}")
    for notice in notices:
        print(f"NOTICE {notice}")
    sys.exit(1 if notices else 0)


if __name__ == "__main__":
    main()
