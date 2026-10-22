#!/usr/bin/env python3
"""Graded with/without-skill evaluation run for one skill.

Drives fresh Sonnet/Opus runs as `claude -p` subprocesses: two trials per
scenario (with and without the skill), then blind grading of each trial
against that scenario's own expectations as an explicit rubric.

Subprocesses rather than in-session subagents: the full set is ~750 trials
plus ~2,200 grading calls, which no single orchestrating context holds.
Each subprocess is an independent fresh context on the named model, so the
measurement semantics are unchanged.
"""

import argparse
import json
import os
import random
import re
import shutil
import subprocess
import tempfile
import threading
import sys
import time
import types
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

# This file lives at skill-wip/<repo>/evals/_harness/run_skill.py, identically
# duplicated into every repo's own evals/_harness/ (see skill-wip/CLAUDE.md
# section Evals, "Running the harness"), so parents[4] reaches the checkout
# root regardless of which repo's copy is running.
REPO = Path(__file__).resolve().parents[4]
SUBJECTIVE_PASS_THRESHOLD = 4  # 0-5 scale; below this the expectation fails


# Carried by every subprocess, trials and trigger alike.
#
# No subprocess sees an MCP server: one otherwise puts unrelated tools in reach,
# and an MCP tool call aborts trigger detection, which only counts a run opening
# with Skill or Read.
#
# The per-machine sections (cwd, env info, memory paths, git status) move out of
# the system prompt into the first user message. Those are exactly the parts
# that differ between calls, so leaving them in the prompt prefix defeats the
# cache for every run; moving them lets the constant prefix be reused.
SHARED_CLI = ["--strict-mcp-config", "--mcp-config", '{"mcpServers":{}}',
              "--exclude-dynamic-system-prompt-sections"]

# Trials and grading additionally load user setting sources only, which drops
# this repo's CLAUDE.md. That file is about the eval framework and the
# affiliation research rather than any skill's subject, and a check confirmed it
# was reaching every trial. Dropping it needs this flag rather than a neutral
# working directory, because the sandbox blocks reading the skill by absolute
# path from outside the repository, and rather than --bare, which also skips
# keychain reads so every call under it fails to authenticate here.
#
# The trigger path deliberately keeps the default sources: run_single_query
# advertises the skill as a project command under <root>/.claude/commands/, and
# a user-only run would not see it. Its root is a fresh temporary directory, so
# no project CLAUDE.md exists there to leak in the first place.
#
# The user-level CLAUDE.md still loads everywhere. It applies equally to both
# conditions, so it does not bias the with-versus-without comparison.
TRIAL_CLI = [*SHARED_CLI, "--setting-sources", "user"]


def claude(prompt: str, model: str, timeout: int, attempts: int = 6) -> str:
    """One fresh `claude -p` run. Returns final response text, or "" on failure."""
    env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}
    cmd = ["claude", "-p", prompt, "--model", model,
           "--output-format", "json", *TRIAL_CLI]
    for attempt in range(attempts):
        try:
            proc = subprocess.run(
                cmd, cwd=str(REPO), env=env, timeout=timeout,
                stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
            )
            data = json.loads(proc.stdout.decode("utf-8", errors="replace"))
            text = data.get("result") or ""
            if text.strip() and not data.get("is_error"):
                return text
        except Exception:
            pass
        # Exponential with jitter, to roughly ten minutes across all attempts.
        # A linear 5/10/15s budget lasted half a minute, which a sustained
        # rate-limit window outlives easily: a whole batch of skills aborted at
        # classification while the CLI itself was healthy minutes later.
        if attempt < attempts - 1:
            time.sleep(min(240, 15 * (2 ** attempt)) * (0.7 + random.random() * 0.6))
    return ""


def extract_json(text: str):
    """Pull the first JSON object out of a model response."""
    fence = re.search(r"```(?:json)?\s*(.*?)```", text, re.S)
    candidates = [fence.group(1)] if fence else []
    start = text.find("{")
    if start != -1:
        candidates.append(text[start:text.rfind("}") + 1])
    for c in candidates:
        try:
            return json.loads(c)
        except Exception:
            continue
    return None


# --- step 2: objective / subjective classification -------------------------

CLASSIFY = """You are triaging evaluation expectations for a graded skill run.

Classify each expectation as one of:
- "objective": mechanically verifiable by a careful reader with low ambiguity \
(a named section is present, a figure carries through, a named framework is \
applied, a banned move is absent, a specific count is met).
- "subjective": settling it genuinely requires a judgment call about quality, \
tone, or degree that two careful readers could reasonably split on.

Most prose-behaviour checks a careful reader settles without taste. Default to \
"objective" unless the expectation is genuinely unclear.

{body}

Return ONLY a JSON object mapping each scenario id (as a string) to an array of \
classification strings, one per expectation, in the order given:
{{"1": ["objective", "subjective", ...], "2": [...]}}"""


def classify(evals, model, timeout):
    body = []
    for ev in evals:
        body.append(f"\nScenario {ev['id']} expectations:")
        for i, e in enumerate(ev.get("expectations", []), 1):
            body.append(f"  {i}. {e}")
    out = claude(CLASSIFY.format(body="\n".join(body)), model, timeout)
    parsed = extract_json(out)
    # A parse failure would silently mark every expectation objective, which is
    # indistinguishable from a genuine all-objective verdict. Fail loudly instead.
    if not parsed:
        raise SystemExit("classification failed: model returned no parsable JSON")
    missing = [ev["id"] for ev in evals
               if str(ev["id"]) not in parsed and ev["id"] not in parsed]
    if missing:
        raise SystemExit(f"classification incomplete: scenarios {missing} absent")
    result = {}
    for ev in evals:
        n = len(ev.get("expectations", []))
        got = parsed.get(str(ev["id"])) or parsed.get(ev["id"]) or []
        # Unclassified expectations default to objective, per the triage rule.
        def kind(i):
            if i >= len(got):
                return "objective"
            return "subjective" if str(got[i]).lower().startswith("subj") else "objective"
        result[ev["id"]] = [kind(i) for i in range(n)]
    return result


# --- step 3: trials --------------------------------------------------------

WITH = ("Read {skill}/SKILL.md in full, and any references/scripts it points you "
        "to. Follow it to complete this task: {prompt}. Give your complete answer "
        "as your final response - the actual deliverable, not a summary of what "
        "you did.")

WITHOUT = ("Complete this task using your own judgment. Do not read, search, or "
           "reference anything under skill-wip/ in this repo: {prompt}. Give your "
           "complete answer as your final response - the actual deliverable, not "
           "a summary of what you did.")


def run_trials(evals, skill_dir, outdir, model, timeout, workers):
    jobs = []
    for ev in evals:
        for cond, tpl in (("with_skill", WITH), ("without_skill", WITHOUT)):
            dest = outdir / "trials" / f"eval-{ev['id']}" / cond / "output.md"
            if dest.exists() and dest.stat().st_size > 0:
                continue
            jobs.append((dest, tpl.format(skill=skill_dir, prompt=ev["prompt"])))
    def one(job):
        dest, prompt = job
        text = claude(prompt, model, timeout)
        # Written as each trial lands, so an interrupted run resumes from the
        # trials already completed rather than redoing the whole skill.
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(text)

    with ThreadPoolExecutor(max_workers=workers) as pool:
        list(pool.map(one, jobs))


# --- steps 4-5: blind grading ----------------------------------------------

OBJECTIVE = """You are grading transcripts against fixed rubrics. You do not \
know how any transcript was produced, and must not speculate about it.

Each section below is a separate, independent task: its rubric applies only to \
its own transcript. Judge every section on its own evidence. Do not let one \
section's quality colour another's, and never carry a verdict across sections.

{body}

Be strict: an item passes only when its own transcript clearly satisfies it. \
Length alone is never evidence.

Return ONLY JSON, mapping each section id to its verdicts in rubric order:
{{"1": [{{"text": "...", "passed": true, "evidence": "..."}}], "2": [...]}}
Evidence must quote or cite that section's transcript."""

SUBJECTIVE = """You are grading a transcript against a fixed rubric. You do not \
know how the transcript was produced, and must not speculate about it.

<transcript>
{transcript}
</transcript>

Rubric - score each numbered item 0-5:
{rubric}

0 = clearly absent or violated, 5 = fully and clearly satisfied. Bias toward the \
lower score whenever ambiguous. These items exist to catch what a plain answer \
usually misses, and judged verdicts are documented to favour longer answers, so \
length or thoroughness alone never earns a score.

Return ONLY JSON, one entry per rubric item in order:
{{"expectations": [{{"text": "...", "score": 3, "evidence": "..."}}]}}"""


def _split(ev, kinds):
    exps = ev.get("expectations", [])
    return ([e for e, k in zip(exps, kinds) if k == "objective"],
            [e for e, k in zip(exps, kinds) if k == "subjective"])


def _read_trial(outdir, eval_id, cond):
    t = outdir / "trials" / f"eval-{eval_id}" / cond / "output.md"
    return (t.read_text() if t.exists() else "") or "(no output produced)"


def _fully_graded(path, cond):
    """True when this condition is recorded AND every row actually got a verdict.

    Presence alone is not enough to skip on a resume: a failed grading call
    still writes rows, marked ungraded, which count as failures. Treating those
    as done would freeze an artifact into the result.
    """
    if not path.exists():
        return False
    try:
        rows = json.loads(path.read_text()).get(cond, {}).get("expectations")
    except Exception:
        return False
    return bool(rows) and all(r.get("graded") for r in rows)


def _merge(path, cond, rows):
    """Both conditions share one file, each under its own key."""
    path.parent.mkdir(parents=True, exist_ok=True)
    existing = {}
    if path.exists():
        try:
            existing = json.loads(path.read_text())
        except Exception:
            existing = {}
    existing[cond] = {"expectations": rows}
    path.write_text(json.dumps(existing, indent=2))


def _rows(items, got):
    rows = []
    for i, t in enumerate(items):
        g = got[i] if i < len(got) and isinstance(got[i], dict) else {}
        row = {"text": t, "evidence": str(g.get("evidence", ""))[:600]}
        if "score" in g:
            try:
                row["score"] = max(0, min(5, int(g["score"])))
            except Exception:
                row["score"] = 0
            row["passed"] = row["score"] >= SUBJECTIVE_PASS_THRESHOLD
        else:
            row["passed"] = bool(g.get("passed", False))
        # A grading call that returned nothing usable counts as a failure,
        # never as a silent pass.
        row["graded"] = bool(g)
        rows.append(row)
    return rows


def run_objective_grading(evals, classes, outdir, model, timeout):
    """One grading call per condition, covering every scenario of the skill.

    Batched the way classify() already batches: a call per scenario paid the
    same fixed per-call overhead ~10 times over for no extra signal. The grader
    now sees several of a skill's scenarios at once, so a strong or weak
    impression could in principle bleed between neighbouring sections; the
    prompt isolates them explicitly, and the trade-off is recorded in
    skill-wip/CLAUDE.md section Evals.
    """
    for cond in ("with_skill", "without_skill"):
        sections, wanted = [], []
        for ev in evals:
            obj, _ = _split(ev, classes[ev["id"]])
            if not obj:
                continue
            path = outdir / "grading" / f"eval-{ev['id']}-objective.json"
            if _fully_graded(path, cond):
                continue
            rubric = "\n".join(f"{i}. {t}" for i, t in enumerate(obj, 1))
            sections.append(
                f"=== SECTION {ev['id']} ===\n<transcript>\n"
                f"{_read_trial(outdir, ev['id'], cond)}\n</transcript>\n"
                f"Rubric for section {ev['id']}:\n{rubric}")
            wanted.append((ev["id"], obj, path))
        if not wanted:
            continue
        out = claude(OBJECTIVE.format(body="\n\n".join(sections)), model, timeout)
        parsed = extract_json(out) or {}
        missing = []
        for eval_id, obj, path in wanted:
            got = parsed.get(str(eval_id)) or parsed.get(eval_id) or []
            if isinstance(got, list) and got:
                _merge(path, cond, _rows(obj, got))
            else:
                missing.append((eval_id, obj, path))
        # One call per condition asks for every expectation's verdict and
        # evidence in a single JSON response, which the largest skills can
        # overrun: the whole condition then comes back ungraded, and ungraded
        # expectations count as failures. Those scenarios are re-graded one call
        # each, so batching keeps its saving wherever it does fit.
        for eval_id, obj, path in missing:
            rubric = "\n".join(f"{i}. {t}" for i, t in enumerate(obj, 1))
            section = (f"=== SECTION {eval_id} ===\n<transcript>\n"
                       f"{_read_trial(outdir, eval_id, cond)}\n</transcript>\n"
                       f"Rubric for section {eval_id}:\n{rubric}")
            out = claude(OBJECTIVE.format(body=section), model, timeout)
            got = (extract_json(out) or {}).get(str(eval_id)) or []
            _merge(path, cond, _rows(obj, got if isinstance(got, list) else []))


def run_subjective_grading(evals, classes, outdir, model, timeout, workers):
    """Two independent Opus passes per (scenario, condition), left unbatched.

    Independence between the passes is the whole point of the agreement
    measure, and these are a small share of total calls.
    """
    todo = []
    for ev in evals:
        _, sub = _split(ev, classes[ev["id"]])
        if not sub:
            continue
        rubric = "\n".join(f"{i}. {t}" for i, t in enumerate(sub, 1))
        for cond in ("with_skill", "without_skill"):
            for p in (1, 2):
                path = outdir / "grading" / f"eval-{ev['id']}-subjective-pass{p}.json"
                if _fully_graded(path, cond):
                    continue
                todo.append((path, cond, sub, SUBJECTIVE.format(
                    transcript=_read_trial(outdir, ev["id"], cond), rubric=rubric)))
    with ThreadPoolExecutor(max_workers=workers) as pool:
        outs = list(pool.map(lambda j: claude(j[3], model, timeout), todo))
    for (path, cond, sub, _), text in zip(todo, outs):
        got = (extract_json(text) or {}).get("expectations", [])
        _merge(path, cond, _rows(sub, got if isinstance(got, list) else []))


# --- step 6: inter-pass agreement ------------------------------------------

def gwet_ac1(ratings_a, ratings_b):
    n = len(ratings_a)
    if n == 0:
        return None
    po = sum(a == b for a, b in zip(ratings_a, ratings_b)) / n
    all_ratings = ratings_a + ratings_b
    p_pass = sum(r == "pass" for r in all_ratings) / len(all_ratings)
    pe = 2 * p_pass * (1 - p_pass)
    return 1.0 if pe == 1 else (po - pe) / (1 - pe)


# --- step 7: trigger eval --------------------------------------------------

def run_trigger(skill_dir, trigger_queries, outdir, model, workers):
    """Trigger accuracy, using skill-creator's run_single_query per query.

    run_single_query advertises the skill by writing a uniquely-named command
    file under <root>/.claude/commands/ and counts a trigger only when the model
    invokes that exact name. One root shared across concurrent workers therefore
    breaks the measurement: every in-flight query's file is visible at once, the
    model picks one of the identical entries, and the other workers record a
    miss.

    A fresh root per query fixes that but defeats the prompt cache, because the
    working directory appears in the system prompt, so every call presents a
    different prefix. Each worker instead keeps one root for its whole run: only
    one query is ever live in it, and the constant prefix (system prompt plus
    skill description) is reused across the hundred-odd queries that worker
    handles. The repetitions of a query run back-to-back on that same root, so
    the second reads the cache the first wrote.
    """
    dest = outdir / "trigger-evals.json"
    if dest.exists():
        return
    sys.path.insert(0, "/mnt/skills/examples/skill-creator")
    import scripts.run_eval as run_eval_mod
    from scripts.run_eval import run_single_query
    from scripts.utils import parse_skill_md

    # run_single_query builds its own argv, so the neutral flags are injected by
    # swapping the subprocess reference it resolves against. Scoped to that
    # module, leaving the real subprocess module and upstream's logic untouched.
    if not getattr(run_eval_mod, "_neutral_cli_patched", False):
        real = run_eval_mod.subprocess

        def popen(cmd, *args, **kwargs):
            if isinstance(cmd, list) and cmd and cmd[0] == "claude":
                cmd = [*cmd, *SHARED_CLI]
            return real.Popen(cmd, *args, **kwargs)

        run_eval_mod.subprocess = types.SimpleNamespace(
            Popen=popen, PIPE=real.PIPE, DEVNULL=real.DEVNULL)
        run_eval_mod._neutral_cli_patched = True

    name, description, _ = parse_skill_md(skill_dir)
    # Two runs, and both must agree: a query passes only when it triggers every
    # time it should and never when it should not. A majority rule over two runs
    # would let one ambiguous run carry the verdict.
    RUNS_PER_QUERY = 2
    local, roots, roots_lock = threading.local(), [], threading.Lock()

    def worker_root():
        root = getattr(local, "root", None)
        if root is None:
            root = tempfile.mkdtemp(prefix="trig-")
            (Path(root) / ".claude" / "commands").mkdir(parents=True)
            local.root = root
            with roots_lock:
                roots.append(root)
        return root

    def one(item):
        root = worker_root()
        runs = []
        for _ in range(RUNS_PER_QUERY):
            try:
                runs.append(bool(run_single_query(
                    item["query"], name, description, 120, root, model)))
            except Exception:
                runs.append(False)
        return runs

    try:
        with ThreadPoolExecutor(max_workers=workers) as pool:
            all_runs = list(pool.map(one, trigger_queries))
    finally:
        for root in roots:
            shutil.rmtree(root, ignore_errors=True)

    results = []
    for item, runs in zip(trigger_queries, all_runs):
        rate = sum(runs) / len(runs)
        should = bool(item["should_trigger"])
        results.append({
            "query": item["query"], "should_trigger": should,
            "trigger_rate": rate, "triggers": sum(runs), "runs": len(runs),
            "pass": (rate == 1.0) if should else (rate == 0.0),
        })
    passed = sum(1 for r in results if r["pass"])
    dest.write_text(json.dumps({
        "skill_name": name, "description": description,
        "runs_per_query": RUNS_PER_QUERY, "threshold": "full agreement",
        "model": model, "results": results,
        "summary": {"total": len(results), "passed": passed,
                    "failed": len(results) - passed},
    }, indent=2))


# --- step 8: metrics -------------------------------------------------------

def summarize(repo, name, evals, classes, outdir, cfg):
    counts = {c: {"passed": 0, "total": 0} for c in ("with_skill", "without_skill")}
    failed = {c: [] for c in counts}
    a, b, disagreements = [], [], []

    for ev in evals:
        exps, kinds = ev.get("expectations", []), classes[ev["id"]]
        sub_texts = [e for e, k in zip(exps, kinds) if k == "subjective"]
        for cond in counts:
            verdicts = {}
            op = outdir / "grading" / f"eval-{ev['id']}-objective.json"
            if op.exists():
                for r in json.loads(op.read_text()).get(cond, {}).get("expectations", []):
                    verdicts[r["text"]] = r["passed"]
            p1 = outdir / "grading" / f"eval-{ev['id']}-subjective-pass1.json"
            p2 = outdir / "grading" / f"eval-{ev['id']}-subjective-pass2.json"
            r1 = json.loads(p1.read_text()).get(cond, {}).get("expectations", []) if p1.exists() else []
            r2 = json.loads(p2.read_text()).get(cond, {}).get("expectations", []) if p2.exists() else []
            for i, text in enumerate(sub_texts):
                v1 = r1[i]["passed"] if i < len(r1) else False
                v2 = r2[i]["passed"] if i < len(r2) else False
                a.append("pass" if v1 else "fail")
                b.append("pass" if v2 else "fail")
                if v1 != v2:
                    disagreements.append(
                        {"eval_id": ev["id"], "condition": cond, "expectation": text,
                         "pass1": v1, "pass2": v2})
                verdicts[text] = v1  # pass 1 is authoritative for the count
            for text in exps:
                counts[cond]["total"] += 1
                if verdicts.get(text, False):
                    counts[cond]["passed"] += 1
                else:
                    failed[cond].append({"eval_id": ev["id"], "expectation": text})

    def rate(c):
        t = counts[c]["total"]
        return round(100.0 * counts[c]["passed"] / t, 1) if t else 0.0

    with_r, without_r = rate("with_skill"), rate("without_skill")
    delta = round(with_r - without_r, 1)
    uplift = round(with_r / without_r, 2) if without_r else None

    trig = {}
    tp = outdir / "trigger-evals.json"
    if tp.exists():
        try:
            trig = json.loads(tp.read_text()).get("summary", {})
        except Exception:
            trig = {}
    trig_acc = (round(100.0 * trig["passed"] / trig["total"], 1)
                if trig.get("total") else None)

    # A trial whose subprocess failed every attempt writes an empty file and
    # would grade as all-fail, which is indistinguishable from a genuine low
    # score. Surface the count so a degraded run is never read as a result.
    empty = {c: [] for c in counts}
    for ev in evals:
        for cond in counts:
            t = outdir / "trials" / f"eval-{ev['id']}" / cond / "output.md"
            if not t.exists() or not t.read_text().strip():
                empty[cond].append(ev["id"])
    ungraded = 0
    for gp in sorted((outdir / "grading").glob("*.json")):
        for cond_rows in json.loads(gp.read_text()).values():
            ungraded += sum(1 for r in cond_rows.get("expectations", [])
                            if not r.get("graded", True))

    n_sub = sum(sum(1 for k in v if k == "subjective") for v in classes.values())
    summary = {
        "repo": repo,
        "skill": name,
        "scenarios": len(evals),
        "expectations_total": counts["with_skill"]["total"],
        "expectations_subjective": n_sub,
        "expectations_objective": counts["with_skill"]["total"] - n_sub,
        "pass_rate_with_skill_pct": with_r,
        "pass_rate_without_skill_pct": without_r,
        "delta_pp": delta,
        "uplift_multiplier": uplift,
        "trigger_accuracy_pct": trig_acc,
        "trigger_queries": trig.get("total"),
        "subjective_ac2": (round(gwet_ac1(a, b), 3) if a else None),
        "subjective_pass_disagreements": disagreements,
        "concern_flag": bool(without_r >= 70.0 and delta < 10.0),
        "concern_reason": ("without-skill pass rate >=70% with delta <10pp: the eval "
                           "set needs harder traps, not the skill more rules"
                           if without_r >= 70.0 and delta < 10.0 else None),
        "models": {"trial": cfg["trial_model"],
                   "objective_grader": cfg["objective_model"],
                   "subjective_grader": cfg["subjective_model"],
                   "trigger": cfg["trigger_model"]},
        "harness_version": cfg["harness_version"],
        "conditions": cfg["conditions"],
        "empty_trials": empty,
        "ungraded_expectations": ungraded,
        "run_degraded": bool(empty["with_skill"] or empty["without_skill"] or ungraded),
        "failed_expectations": failed,
    }
    (outdir / "summary.json").write_text(json.dumps(summary, indent=2))
    return summary


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--skill", required=True)
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--trigger-workers", type=int, default=8)
    args = ap.parse_args()

    skill_dir = REPO / "skill-wip" / args.repo / args.skill
    data = json.loads((skill_dir / "evals" / "evals.json").read_text())
    evals = data["evals"]
    outdir = REPO / "skill-wip" / args.repo / "evals" / args.skill
    outdir.mkdir(parents=True, exist_ok=True)

    cfg = {
        "trial_model": "sonnet",
        "objective_model": "sonnet",
        "subjective_model": "opus",
        # Sonnet, not a smaller model. Haiku 4.5 was measured against it on one
        # skill's queries under otherwise identical code and scored 6/10 to
        # Sonnet's 10/10, four of five should-trigger queries failing outright,
        # so routing does not measure the same on the small model here. Whether
        # that gap is a finding about the descriptions or a confound is a
        # separate question; this run keeps one trigger model across all skills
        # so the numbers stay comparable.
        "trigger_model": "sonnet",
        "harness_version": subprocess.run(
            ["claude", "--version"], stdout=subprocess.PIPE
        ).stdout.decode().strip(),
        # What the subprocesses were exposed to. Recorded per skill because a
        # run under different conditions is not comparable to this one.
        "conditions": {
            "mcp_servers": "disabled",
            "project_claude_md": "not loaded (trials and grading)",
            "user_claude_md": "loaded",
            "dynamic_prompt_sections": "excluded",
        },
    }

    cpath = outdir / "classification.json"
    if cpath.exists():
        classes = {int(k): v for k, v in json.loads(cpath.read_text()).items()}
    else:
        classes = classify(evals, cfg["subjective_model"], 900)
        cpath.write_text(json.dumps(classes, indent=2))

    run_trials(evals, skill_dir, outdir, cfg["trial_model"], 900, args.workers)
    run_objective_grading(evals, classes, outdir, cfg["objective_model"], 1800)
    run_subjective_grading(evals, classes, outdir, cfg["subjective_model"],
                           900, args.workers)
    run_trigger(skill_dir, data.get("trigger_queries", []), outdir,
                cfg["trigger_model"], args.trigger_workers)
    s = summarize(args.repo, args.skill, evals, classes, outdir, cfg)

    mpath = REPO / "skill-wip" / "manifest.json"
    m = json.loads(mpath.read_text())
    m[f"{args.repo}/{args.skill}"] = "done"
    mpath.write_text(json.dumps(m, indent=2))
    print(json.dumps({k: v for k, v in s.items()
                      if k not in ("failed_expectations",
                                   "subjective_pass_disagreements")}, indent=2))


if __name__ == "__main__":
    main()
