#!/usr/bin/env python3
"""Run only the trial stage of the skill eval harness for one repo's pending skills.

Stage-selective wrapper around the sibling run_skill.py: imports it as a module
and drives run_trials() alone - no classification, no grading, no trigger.
The with/without trials are the expensive network-bound part and the only stage
routed to the trial model, so this splits a batch into "produce the transcripts
now, grade them later": run_skill.py resumes from the cached trial outputs and
only pays for the stages it still owes.

Never edits the harness it drives: run_skill.py, run_batch.sh and aggregate.py
stay untouched. This file is itself one of the byte-identical copies now, so an
edit here owes the same treatment as an edit there - copy it into every other
repo's evals/_harness/ and diff each pair before committing (see
skill-wip/CLAUDE.md section Evals, "Running the harness"). Nothing in it may
name one repo, which is why --repo defaults to the directory this copy sits in.

Manifest entries stay "pending": only run_skill.py's own main() flips a skill to
"done", and a trials-only pass is not a done skill.

Usage:
  python3 <repo>/evals/_harness/run_trials_only.py [--repo <repo-name>]
                                                   [--workers N] [--dry-run]

--dry-run prints per-skill missing-trial counts and exits without calling the CLI.
"""

import argparse
import json
import os
import sys
import urllib.parse
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

# Matches cfg["trial_model"] in run_skill.py: every trial runs on the trial
# model, with and without the skill, so runs stay comparable across skills.
# EVAL_MODEL overrides it for a pass routed elsewhere, and overrides it for both
# conditions at once - a with_skill trial and a without_skill trial measured on
# different models compare nothing.
TRIAL_MODEL = os.environ.get("EVAL_MODEL", "sonnet")
# Matches the timeout run_skill.py passes its own trial calls.
TRIAL_TIMEOUT_S = 900


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
    """Count of trials still owed - resume semantics identical to run_trials."""
    jobs = []
    for ev in evals:
        for cond in ("with_skill", "without_skill"):
            dest = outdir / "trials" / f"eval-{ev['id']}" / cond / "output.md"
            if not (dest.exists() and dest.stat().st_size > 0):
                jobs.append(dest)
    return jobs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=DEFAULT_REPO)
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    manifest = REPO / "skill-wip" / "manifest.json"
    m = json.loads(manifest.read_text())
    pending = [k.split("/", 1)[1] for k, v in m.items()
               if v == "pending" and k.startswith(f"{args.repo}/")]
    if not pending:
        raise SystemExit(f"no pending skills for {args.repo}")

    print(f"trial model {TRIAL_MODEL} on provider {provider_label()}", flush=True)
    total = 0
    for skill in pending:
        skill_dir, outdir = run_skill.resolve_skill(args.repo, skill)
        evals = json.loads((skill_dir / "evals" / "evals.json").read_text())["evals"]
        owed = missing_trials(evals, outdir)
        print(f"{skill}: {len(owed)}/{len(evals) * 2} trials to run "
              f"({len(evals)} scenarios)", flush=True)
        total += len(owed)
        if args.dry_run or not owed:
            continue
        run_skill.run_trials(evals, skill_dir, outdir,
                             TRIAL_MODEL, TRIAL_TIMEOUT_S, args.workers)
        record_provenance(outdir, "trials", TRIAL_MODEL)
        # Re-count from disk: an all-attempts-failed trial writes an empty file,
        # and only the disk state tells that apart from a completed one.
        still = len(missing_trials(evals, outdir))
        print(f"{skill}: done, {still} trial(s) still empty on disk", flush=True)

    print(f"TOTAL owed this pass: {total} trials across {len(pending)} skills",
          flush=True)


if __name__ == "__main__":
    main()
