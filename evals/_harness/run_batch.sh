#!/usr/bin/env bash
# Run every skill still pending in the manifest, LANES at a time.
#
# Two lanes by default rather than one: the trial and grading phases are
# network-bound, so a second skill overlaps the first without contending for
# CPU. Raise LANES when the account's rate limit has headroom.
#
# This file lives at <repo>/evals/_harness/run_batch.sh, identically duplicated
# into every repo's own evals/_harness/ (see skill-wip/CLAUDE.md section Evals,
# "Running the harness"). Invoking any copy processes every pending entry in the
# shared skill-wip/manifest.json, whichever repo it belongs to - the copy run
# from is not the scope, it is just which repo's directory happened to hold the
# script that got invoked. Set REPO_FILTER to narrow that to one repo.
#
# Environment:
#   LANES            skills in flight at once (default 2)
#   WORKERS          trial/grading parallelism inside one skill (default 5)
#   TRIGGER_WORKERS  trigger-query parallelism inside one skill (default 8)
#   REPO_FILTER      only run manifest entries whose repo equals this
#   COMMIT           1 to commit and push each skill's artifacts (default 0)
#   BRANCH           branch to push when COMMIT=1
#   SKILL_CREATOR_PATH  Anthropic skill-creator plugin, for the trigger step
set -uo pipefail

# Repos have sat at two depths under skill-wip/, so walk up to whichever
# ancestor holds the manifest instead of counting fixed ".." levels.
root="$(cd "$(dirname "$0")" && pwd)"
while [ "$root" != "/" ] && [ ! -f "$root/skill-wip/manifest.json" ]; do
  root="$(dirname "$root")"
done
[ -f "$root/skill-wip/manifest.json" ] || { echo "checkout root not found"; exit 1; }
cd "$root" || exit 1

LANES="${LANES:-2}"
COMMIT="${COMMIT:-0}"
BRANCH="${BRANCH:-}"
export BRANCH COMMIT

run_one() {
  local entry="$1" repo skill H
  repo="${entry%%/*}"
  skill="${entry##*/}"
  # The harness copy belonging to this entry's repo, wherever that repo sits.
  H="$(ls -d skill-wip/*/"$repo"/evals/_harness skill-wip/"$repo"/evals/_harness \
       2>/dev/null | head -1)"
  [ -n "$H" ] || { echo "!!! no harness dir for $repo"; return 1; }
  echo "=== START $entry $(date -u +%H:%M:%S) ==="
  python3 "$H/run_skill.py" --repo "$repo" --skill "$skill" \
    --workers "${WORKERS:-5}" --trigger-workers "${TRIGGER_WORKERS:-8}" \
    > "$H/$skill.log" 2>&1
  local rc=$?
  [ $rc -ne 0 ] && echo "!!! FAILED $entry rc=$rc (see $H/$skill.log)"

  if [ "$COMMIT" = "1" ]; then
    # Both lanes write the same index and push the same branch, so the whole
    # commit-and-push sequence has to be one critical section. The lock lives at
    # one fixed path shared by every repo's harness copy, since they all commit
    # into the same git index regardless of which repo's evals/ they touch.
    flock skill-wip/.gitlock bash -c '
      git add -A skill-wip/manifest.json "'"${H%/_harness}"'" >/dev/null 2>&1
      git diff --cached --quiet && exit 0
      git commit -q -m "test('"$repo"'): eval run results for '"$skill"'

Graded with and without the skill across its scenarios, blind objective
grading, and trigger-query accuracy under isolated per-query project roots."
      [ -n "'"$BRANCH"'" ] || exit 0
      for a in 1 2 3 4; do
        git push -q origin '"$BRANCH"' && exit 0
        sleep $((2 ** a))
      done
      echo "!!! PUSH FAILED for '"$skill"'"
    '
  fi
  echo "=== DONE $entry $(date -u +%H:%M:%S) ==="
}
export -f run_one

pending() {
  REPO_FILTER="${REPO_FILTER:-}" python3 -c '
import json, os
wanted = os.environ.get("REPO_FILTER") or ""
m = json.load(open("skill-wip/manifest.json"))
for k, v in m.items():
    if v == "done":
        continue
    if wanted and k.split("/", 1)[0] != wanted:
        continue
    print(k)
'
}

# A full repo costs more calls than one usage window allows, and every skill the
# window swallows fails the same way: classification returns nothing parsable
# and run_skill.py aborts loud, leaving no artifacts. Relaunching afterwards is
# the documented recovery, so RETRY_UNTIL_DONE just does it without a human
# awake for the reset. A pass that completes nothing means the window is still
# closed, so that case waits RETRY_SLEEP before trying again rather than
# spinning through the whole manifest failing one skill at a time.
RETRY_UNTIL_DONE="${RETRY_UNTIL_DONE:-0}"
RETRY_SLEEP="${RETRY_SLEEP:-1800}"
MAX_PASSES="${MAX_PASSES:-12}"

for pass in $(seq 1 "$MAX_PASSES"); do
  before="$(pending | wc -l | tr -d ' ')"
  [ "$before" = "0" ] && break
  echo "=== PASS $pass: $before pending $(date -u +%H:%M:%S) ==="
  pending | xargs -P "$LANES" -I{} bash -c 'run_one "$@"' _ {}
  after="$(pending | wc -l | tr -d ' ')"
  [ "$RETRY_UNTIL_DONE" = "1" ] || break
  [ "$after" = "0" ] && break
  if [ "$after" = "$before" ]; then
    echo "=== PASS $pass completed nothing, waiting ${RETRY_SLEEP}s $(date -u +%H:%M:%S) ==="
    sleep "$RETRY_SLEEP"
  fi
done

echo "=== BATCH COMPLETE $(pending | wc -l | tr -d ' ') still pending $(date -u +%H:%M:%S) ==="
