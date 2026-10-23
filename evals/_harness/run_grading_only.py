#!/usr/bin/env python3
"""Run only the objective-grading stage for one repo's pending skills.

Stage-selective wrapper around the sibling run_skill.py: imports it as a module
and drives run_objective_grading() alone - no classification, no trials, no
subjective grading, no trigger. The companion to run_trials_only.py: that pass
produces the transcripts, this one grades them, and the two can sit on different
providers because neither reads the other's model choice.

Never edits the harness it drives: run_skill.py, run_batch.sh and aggregate.py
stay untouched. This file is itself one of the byte-identical copies, so an edit
here owes the same treatment as an edit there - copy it into every other repo's
evals/_harness/ and diff each pair before committing (see skill-wip/CLAUDE.md
section Evals, "Running the harness"). Nothing in it may name one repo, which is
why --repo defaults to the directory this copy sits in.

Two preconditions, handled differently on purpose:

- classification.json must already exist for every selected skill. It decides
  which expectations are graded objectively at all, so grading without it would
  silently grade the wrong subset rather than fail. Missing for any skill aborts
  the whole pass, naming all of them at once.
- Trials must be complete. A skill with an absent or empty trial file is skipped
  with a reason, not aborted on: the fix is another run_trials_only.py pass, and
  the skills that are ready should not wait for it.

Manifest entries stay "pending": only run_skill.py's own main() flips a skill to
"done", and a grading-only pass is not a done skill.

Usage:
  python3 <repo>/evals/_harness/run_grading_only.py [--repo <repo-name>]
                                                    [--workers N] [--dry-run]

--dry-run prints what each skill would grade and exits without calling the CLI.
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

# Matches cfg["objective_model"] in run_skill.py. Objective expectations are the
# mechanically-checkable ones, graded on the cheaper model on purpose; EVAL_MODEL
# overrides that for a pass routed elsewhere. One model across every skill of a
# comparison, or the pass rates stop being comparable to each other.
GRADER_MODEL = os.environ.get("EVAL_MODEL", "sonnet")
# Matches the timeout run_skill.py passes its own objective-grading call. Longer
# than a trial's: one call carries every scenario of the skill and both the
# verdict and the evidence for each expectation.
GRADING_TIMEOUT_S = 1800


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


def missing_trials(evals, outdir):
    """Trial files still owed - resume semantics identical to run_trials."""
    jobs = []
    for ev in evals:
        for cond in ("with_skill", "without_skill"):
            dest = outdir / "trials" / f"eval-{ev['id']}" / cond / "output.md"
            if not (dest.exists() and dest.stat().st_size > 0):
                jobs.append(dest)
    return jobs


def load_classes(outdir):
    """Read classification.json, or None when it is absent.

    Keys come back as ints, matching run_skill.py's own read: the grading code
    indexes by the scenario id straight out of evals.json, and JSON object keys
    are always strings.
    """
    cpath = outdir / "classification.json"
    if not cpath.exists():
        return None
    return {int(k): v for k, v in json.loads(cpath.read_text()).items()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=DEFAULT_REPO)
    # Skills graded concurrently, not calls within one skill: objective grading
    # is one call per condition for the whole skill, so the only parallelism
    # available here is across skills.
    ap.add_argument("--workers", type=int, default=6,
                    help="skills graded concurrently (default 6)")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    manifest = REPO / "skill-wip" / "manifest.json"
    m = json.loads(manifest.read_text())
    pending = [k.split("/", 1)[1] for k, v in m.items()
               if v == "pending" and k.startswith(f"{args.repo}/")]
    if not pending:
        raise SystemExit(f"no pending skills for {args.repo}")

    jobs, unclassified, skipped = [], [], []
    for skill in pending:
        skill_dir, outdir = run_skill.resolve_skill(args.repo, skill)
        evals = json.loads((skill_dir / "evals" / "evals.json").read_text())["evals"]
        classes = load_classes(outdir)
        if classes is None:
            unclassified.append(skill)
            continue
        owed = missing_trials(evals, outdir)
        if owed:
            skipped.append((skill, len(owed), len(evals) * 2))
            continue
        jobs.append((skill, evals, classes, outdir))

    # Loud, and all at once: grading a skill whose expectations were never split
    # objective/subjective would grade the wrong subset without erroring, so the
    # pass refuses rather than guessing. Naming every offender saves a second
    # abort on the next skill in line.
    if unclassified:
        raise SystemExit(
            "classification.json missing for "
            f"{len(unclassified)} skill(s): {', '.join(unclassified)}\n"
            "Run run_skill.py on each (it classifies, then resumes from the "
            "cached trials) before grading them here.")

    for skill, owed, total in skipped:
        print(f"SKIP {skill}: {owed}/{total} trials absent or empty", flush=True)

    print(f"objective grader {GRADER_MODEL} on provider {provider_label()}",
          flush=True)
    for skill, evals, classes, _ in jobs:
        n_obj = sum(sum(1 for k in classes[ev["id"]] if k == "objective")
                    for ev in evals)
        print(f"{skill}: {len(evals)} scenarios, {n_obj} objective "
              f"expectation(s) per condition", flush=True)
    if args.dry_run:
        print(f"TOTAL this pass: {len(jobs)} skill(s) to grade, "
              f"{len(skipped)} skipped", flush=True)
        return

    def one(job):
        skill, evals, classes, outdir = job
        run_skill.run_objective_grading(evals, classes, outdir,
                                        GRADER_MODEL, GRADING_TIMEOUT_S)
        record_provenance(outdir, "objective_grading", GRADER_MODEL)
        print(f"{skill}: graded", flush=True)

    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        list(pool.map(one, jobs))

    print(f"TOTAL this pass: {len(jobs)} skill(s) graded, "
          f"{len(skipped)} skipped", flush=True)


if __name__ == "__main__":
    main()
