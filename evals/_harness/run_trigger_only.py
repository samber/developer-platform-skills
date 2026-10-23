#!/usr/bin/env python3
"""Re-measure only the trigger stage, for one repo's skills whose run was suspect.

Stage-selective wrapper around the sibling run_skill.py: imports it as a module
and drives run_trigger() alone, always with redo=True - no classification, no
trials, no grading. Sibling of run_trials_only.py and run_grading_only.py, and
the only one of the three that re-runs work already recorded, because that is the
whole point: a suspect trigger run has a trigger-evals.json on disk and it has to
be replaced.

Scope is the flag, not the manifest. A skill is selected when its own
summary.json carries trigger_run_suspect true - fewer than half its
should-trigger queries fired at all, which run_skill.py records as a suspect run
rather than as a routing score. run_skill.py marks a skill "done" even when its
trigger run was suspect, so the manifest is the wrong filter here whichever way
it currently reads.

The flag it selects on is also the flag it cannot clear: this driver rewrites
trigger-evals.json and leaves summary.json untouched, so a selected skill stays
selected until run_skill.py runs again and re-summarizes from the new file. Run
this, then run_skill.py, and expect the second pass to resume from every cached
artifact and pay only for the summary.

Never edits the harness it drives: run_skill.py, run_batch.sh and aggregate.py
stay untouched. This file is itself one of the byte-identical copies, so an edit
here owes the same treatment as an edit there - copy it into every other repo's
evals/_harness/ and diff each pair before committing (see skill-wip/CLAUDE.md
section Evals, "Running the harness"). Nothing in it may name one repo, which is
why --repo defaults to the directory this copy sits in.

Usage:
  python3 <repo>/evals/_harness/run_trigger_only.py [--repo <repo-name>]
                                                    [--workers N]
                                                    [--trigger-workers N]
                                                    [--dry-run]

--dry-run prints the selected skills and their query counts, and exits without
calling the CLI.
"""

import argparse
import json
import os
import sys
import urllib.parse
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path


def _checkout_root() -> Path:
    # Same walk-up as the harness itself: repos have sat at two depths under
    # skill-wip/, so trust the manifest's presence, not a fixed parents[N].
    for parent in Path(__file__).resolve().parents:
        if (parent / "skill-wip" / "manifest.json").is_file():
            return parent
    raise SystemExit("checkout root not found: no ancestor holds skill-wip/manifest.json")


REPO = _checkout_root()

# The harness copy this driver ships beside, imported rather than located by
# name: every copy is byte-identical, so each driver drives the harness of the
# repo it was invoked from instead of one repo's copy for all seven.
sys.path.insert(0, str(Path(__file__).resolve().parent))

import run_skill  # noqa: E402  (path set up above)

# This copy's own repo directory, from <repo>/evals/_harness/<this file>. Both
# skill-wip layouts - flat and owner-nested - put the repo name at the same
# offset, so parents[2] resolves in either. A literal default would name one
# repo and be wrong in the other six that ship this same file.
DEFAULT_REPO = Path(__file__).resolve().parents[2].name

# Matches cfg["trigger_model"] in run_skill.py, and EVAL_MODEL overrides it.
# Overriding this one is not free: Haiku 4.5 measured against Sonnet on one
# skill's queries under otherwise identical code scored 6/10 to Sonnet's 10/10,
# four of five should-trigger queries failing outright. Re-measure before
# reading any number produced under a different model as comparable to the rest.
TRIGGER_MODEL = os.environ.get("EVAL_MODEL", "sonnet")


# --- provenance sidecar ----------------------------------------------------
#
# summary.json records the model names run_skill.py's own cfg declares, never
# the endpoint that served them. A split-provider pass makes those two different
# facts: the same model string answered by another provider is not the same
# measurement, so each driver records what its own stage actually used.
#
# Only a short label is stored, never ANTHROPIC_BASE_URL itself and never any
# token. These repos publish publicly, and a base URL can carry a port, a path
# or userinfo that identifies private infrastructure.

# Second-level labels that are a public suffix rather than an organization name,
# so a host like api.example.co.uk reads as "example" and not "co". Deliberately
# short: it covers the country-code shapes an API endpoint realistically uses,
# and a miss only makes the label less readable, never the run wrong.
PUBLIC_SLDS = ("co", "com", "net", "org", "gov", "edu", "ac")


def provider_label() -> str:
    """Short label for whichever endpoint served this stage."""
    raw = os.environ.get("ANTHROPIC_BASE_URL", "").strip()
    if not raw:
        return "anthropic"  # unset means the SDK's own default endpoint
    host = (urllib.parse.urlsplit(raw).hostname or "").lower()
    if not host:
        return "unknown"
    labels = host.split(".")
    # An IP literal, an IPv6 address or a bare local name is someone's own
    # proxy, and its address is exactly the internal detail a public repo must
    # not carry. Collapse it to one neutral word rather than writing it out.
    if len(labels) < 2 or ":" in host or all(p.isdigit() for p in labels):
        return "self-hosted"
    # The organization label, not the leading subdomain: endpoints are named
    # api.*, open.*, dashscope.* and so on, so only the registrable part of the
    # host actually names the provider.
    org = labels[-2]
    if org in PUBLIC_SLDS and len(labels) > 2:
        org = labels[-3]
    return org


def record_provenance(outdir: Path, stage: str, model: str) -> None:
    """Merge one stage's model and provider into evals/<skill>/provenance.json.

    Merged, never overwritten: the stages run as separate passes, possibly on
    separate providers, and each pass must leave the other stages' records
    intact. An unreadable file is replaced rather than aborting the run - the
    sidecar is a record of the pass, not a precondition for it.
    """
    path = outdir / "provenance.json"
    data = {}
    if path.exists():
        try:
            data = json.loads(path.read_text())
        except Exception:
            data = {}
    if not isinstance(data, dict):
        data = {}
    data[stage] = {"model": model, "provider": provider_label()}
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2))


def is_suspect(outdir):
    """True when this skill's own summary reports its trigger run as suspect.

    A skill with no summary.json has nothing to re-measure against, and an
    unreadable one is not evidence of a suspect run: both read as not selected,
    so a malformed file never silently enrols a skill in a re-run.
    """
    path = outdir / "summary.json"
    if not path.exists():
        return False
    try:
        return bool(json.loads(path.read_text()).get("trigger_run_suspect"))
    except Exception:
        return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=DEFAULT_REPO)
    # Skills in flight at once, the same idea as run_batch.sh's LANES and the
    # same default: each selected skill already fans out to --trigger-workers
    # subprocesses, so this multiplies against that rather than adding to it.
    ap.add_argument("--workers", type=int, default=2,
                    help="skills re-measured concurrently (default 2)")
    ap.add_argument("--trigger-workers", type=int, default=8,
                    help="trigger-query parallelism inside one skill (default 8)")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    manifest = REPO / "skill-wip" / "manifest.json"
    m = json.loads(manifest.read_text())
    # Every entry for the repo, whatever its status: the suspect flag and the
    # manifest status are independent, and a suspect run is often marked done.
    entries = [k.split("/", 1)[1] for k in m if k.startswith(f"{args.repo}/")]
    if not entries:
        raise SystemExit(f"no manifest entries for {args.repo}")

    jobs = []
    for skill in entries:
        skill_dir, outdir = run_skill.resolve_skill(args.repo, skill)
        if not is_suspect(outdir):
            continue
        queries = json.loads(
            (skill_dir / "evals" / "evals.json").read_text()).get("trigger_queries", [])
        jobs.append((skill, skill_dir, queries, outdir))

    if not jobs:
        raise SystemExit(
            f"no skill in {args.repo} reports trigger_run_suspect true "
            f"(scanned {len(entries)} manifest entries)")

    print(f"trigger model {TRIGGER_MODEL} on provider {provider_label()}",
          flush=True)
    for skill, _, queries, _ in jobs:
        positives = sum(1 for q in queries if q.get("should_trigger"))
        print(f"{skill}: {len(queries)} queries ({positives} should-trigger)",
              flush=True)
    if args.dry_run:
        print(f"TOTAL this pass: {len(jobs)} suspect skill(s) of {len(entries)}",
              flush=True)
        return

    def one(job):
        skill, skill_dir, queries, outdir = job
        outdir.mkdir(parents=True, exist_ok=True)
        run_skill.run_trigger(skill_dir, queries, outdir, TRIGGER_MODEL,
                              args.trigger_workers, redo=True)
        record_provenance(outdir, "trigger", TRIGGER_MODEL)
        rate = run_skill.trigger_fire_rate(outdir / "trigger-evals.json")
        print(f"{skill}: re-measured, positive fire rate "
              f"{'n/a' if rate is None else round(rate, 3)}", flush=True)

    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        list(pool.map(one, jobs))

    print(f"TOTAL this pass: {len(jobs)} skill(s) re-measured. summary.json is "
          "now stale for each - run run_skill.py to re-summarize.", flush=True)


if __name__ == "__main__":
    main()
