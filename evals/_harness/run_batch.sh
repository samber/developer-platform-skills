#!/usr/bin/env bash
# Run every skill still pending in the manifest, LANES at a time.
#
# Two lanes rather than one: the trial and grading phases are network-bound, so
# a second skill overlaps the first without contending for CPU. Commits are
# serialized under flock because both lanes share one git index.
#
# This file lives at skill-wip/<repo>/evals/_harness/run_batch.sh, identically
# duplicated into every repo's own evals/_harness/ (see skill-wip/CLAUDE.md
# section Evals, "Running the harness"). Invoking any copy processes every
# pending entry in the shared skill-wip/manifest.json, whichever repo it
# belongs to - the copy run from is not the scope, it is just which repo's
# directory happened to hold the script that got invoked.
set -uo pipefail
cd "$(dirname "$0")/../../../.." || exit 1

LANES="${LANES:-2}"
BRANCH=feat/quirky-wozniak-5q3s2c
export BRANCH

run_one() {
  local entry="$1" repo skill H
  repo="${entry%%/*}"
  skill="${entry##*/}"
  H="skill-wip/$repo/evals/_harness"
  echo "=== START $entry $(date -u +%H:%M:%S) ==="
  python3 "$H/run_skill.py" --repo "$repo" --skill "$skill" \
    --workers "${WORKERS:-5}" --trigger-workers "${TRIGGER_WORKERS:-8}" \
    > "$H/$skill.log" 2>&1
  local rc=$?
  [ $rc -ne 0 ] && echo "!!! FAILED $entry rc=$rc (see $H/$skill.log)"

  # Both lanes write the same index and push the same branch, so the whole
  # commit-and-push sequence has to be one critical section. The lock lives at
  # one fixed path shared by every repo's harness copy, since they all commit
  # into the same git index regardless of which repo's evals/ they touch.
  flock skill-wip/.gitlock bash -c '
    git add -A skill-wip/manifest.json "skill-wip/'"$repo"'/evals" >/dev/null 2>&1
    git diff --cached --quiet && exit 0
    git commit -q -m "test('"$repo"'): eval run results for '"$skill"'

Graded with and without the skill across its scenarios, blind objective
grading, and trigger-query accuracy under isolated per-query project roots.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01U6ZNPXAkdyyDGzomAB3Vbw"
    for a in 1 2 3 4; do
      git push -q origin '"$BRANCH"' && exit 0
      sleep $((2 ** a))
    done
    echo "!!! PUSH FAILED for '"$skill"'"
  '
  echo "=== DONE $entry $(date -u +%H:%M:%S) ==="
}
export -f run_one

python3 -c '
import json
m = json.load(open("skill-wip/manifest.json"))
for k, v in m.items():
    if v != "done":
        print(k)
' | xargs -P "$LANES" -I{} bash -c 'run_one "$@"' _ {}

echo "=== BATCH COMPLETE $(date -u +%H:%M:%S) ==="
