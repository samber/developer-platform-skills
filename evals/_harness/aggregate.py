#!/usr/bin/env python3
"""Cross-skill results table from every summary.json written so far.

Skills are grouped by the conditions they were measured under, because the
harness changed twice mid-run and the tiers are not comparable to each other.

This file lives at skill-wip/<repo>/evals/_harness/aggregate.py, identically
duplicated into every repo's own evals/_harness/ (see skill-wip/CLAUDE.md
section Evals, "Running the harness"). It globs across every repo, so any
copy reports the same table; run it from the checkout root.
"""
import glob
import json

def tier(row):
    """Label the conditions a skill was measured under.

    The harness changed three times mid-run, so these are ordered stages rather
    than variants: each one carries the previous one's changes. Skills in
    different stages are not comparable on the metrics the change touched.
    """
    c = row.get("conditions") or {}
    if c.get("mcp_servers") == "enabled" or c.get("project_claude_md") == "loaded":
        return "early"
    if row.get("_threshold") != "full agreement":
        return "interim"
    if c.get("dynamic_prompt_sections") != "excluded":
        return "current"
    return "cached"


rows = []
for f in sorted(glob.glob("skill-wip/*/evals/*/summary.json")):
    r = json.load(open(f))
    t = f.rsplit("/", 1)[0] + "/trigger-evals.json"
    try:
        r["_threshold"] = json.load(open(t)).get("threshold")
    except Exception:
        r["_threshold"] = None
    r["_tier"] = tier(r)
    rows.append(r)

rows.sort(key=lambda r: (r["_tier"], r["repo"], -(r["delta_pp"] or 0)))

hdr = (f"{'skill':<38}{'repo':<14}{'tier':<9}{'with':>7}{'w/o':>7}"
       f"{'delta':>8}{'uplift':>8}{'trig':>7}{'ac2':>7}  flags")
print(hdr)
print("-" * len(hdr))
for r in rows:
    up = f"{r['uplift_multiplier']:.2f}x" if r.get("uplift_multiplier") else "n/a"
    tr = f"{r['trigger_accuracy_pct']:.1f}" if r.get("trigger_accuracy_pct") is not None else "n/a"
    ac = f"{r['subjective_ac2']:.2f}" if r.get("subjective_ac2") is not None else "n/a"
    flags = []
    if r.get("concern_flag"):
        flags.append("CONCERN")
    if r.get("run_degraded"):
        flags.append("DEGRADED")
    print(f"{r['skill']:<38}{r['repo'].replace('-skills',''):<14}{r['_tier']:<9}"
          f"{r['pass_rate_with_skill_pct']:>6.1f}%{r['pass_rate_without_skill_pct']:>6.1f}%"
          f"{r['delta_pp']:>+7.1f}p{up:>8}{tr:>7}{ac:>7}  {' '.join(flags)}")

print(f"\n{len(rows)} skills summarized")

# The two failure modes need different work and must not be reported together.
rewrite = [r for r in rows if r.get("concern_flag")]
weak = [r for r in rows if not r.get("concern_flag")
        and r["pass_rate_without_skill_pct"] < 50
        and r["pass_rate_with_skill_pct"] < 75]
print(f"\nEval set needs harder traps ({len(rewrite)}): "
      + ", ".join(r["skill"] for r in rewrite))
print(f"\nSkill instructions need work ({len(weak)}): "
      + ", ".join(f"{r['skill']} ({r['pass_rate_with_skill_pct']:.0f}% with)"
                  for r in weak))
