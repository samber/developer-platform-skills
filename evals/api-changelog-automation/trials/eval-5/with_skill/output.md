**Not yet.** Don't add `suppressRemovalOfDeprecatedField` as the gate, and don't treat the Apollo result as clearance. You can still ship next week if the checks below come back clean.

## Why "zero operations" isn't enough

1. **Apollo's default window is one week.** Today is 2026-10-30, so it covers about Oct 23–30. A month-end reconciliation script last ran around Sep 30–Oct 2, so it is invisible to that check. The next run is tomorrow or Nov 1, which is before your release. Mobile apps on old builds have the same blind spot, because they only appear in the window if someone opens them that week.
2. **The rule you proposed removes the check.** `suppressRemovalOfDeprecatedField` downgrades the removal to "dangerous", and the CLI exits 0 on dangerous. CI would pass this removal, and every future deprecated-field removal, whether or not anyone still calls the field. The skill says to pair it with a usage rule, never to use it alone.
3. **"Deprecated in March" isn't the removal rule.** The notice window and sunset come from your written policy (`api-versioning-policy`). I don't know whether one exists. If it doesn't, the severity-map row below is provisional.

## CI change

Don't add the suppress rule. Use usage-aware classification with a long window, plus a lifecycle check that fails closed.

`.github/workflows/graphql-contract.yml`:

```yaml
name: graphql-contract
on:
  pull_request:
    paths: ["schema/**"]
jobs:
  breaking:
    runs-on: ubuntu-latest
    env:
      INSPECTOR_VERSION: "<pin>"     # pin; bump deliberately and review rule changes
      USAGE_WINDOW_DAYS: 90          # longest client cycle we know of: quarterly scripts, slow mobile updates
      MIN_DEPRECATION_DAYS: 90       # provisional until the written policy is signed
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0             # merge-base baseline needs history
      - uses: actions/setup-node@v4
      - run: npm i -g @graphql-inspector/cli@${INSPECTOR_VERSION}
      - name: Export per-field usage over the long window
        env:
          APOLLO_KEY: ${{ secrets.APOLLO_KEY }}
        run: node tools/export-field-usage.js --days "$USAGE_WINDOW_DAYS" --out /tmp/usage.json
      - name: Gate (PR vs merge base)
        run: |
          base="$(git merge-base origin/${{ github.base_ref }} HEAD)"
          git show "$base:schema/schema.graphql" > /tmp/base.graphql
          graphql-inspector diff /tmp/base.graphql schema/schema.graphql \
            --rule considerUsage --onUsage tools/on-usage.js
      - name: Lifecycle gate for removed fields
        run: |
          python3 tools/check-removal-lifecycle.py \
            --base /tmp/base.graphql --head schema/schema.graphql \
            --usage /tmp/usage.json --min-days "$MIN_DEPRECATION_DAYS" \
            --acks api/acks.json
```

- **`considerUsage`** fails a removal when the field was used inside the 90-day window. `tools/on-usage.js` reads `/tmp/usage.json` and answers per coordinate. Check its contract against the pinned version's docs.
- **`check-removal-lifecycle.py`** is small and you write it. For each removed field it fails unless all three hold:
  - the field was `@deprecated` at the merge base, with the deprecation date taken from the schema or `git log -S`,
  - at least `MIN_DEPRECATION_DAYS` have elapsed, and
  - usage is zero in `usage.json`, or an acknowledgement row covers the field.
- Put the schema, the severity map and `api/acks.json` under one CODEOWNERS rule with required review. Otherwise an author approves their own break.

**Can-fail control (run before merging the CI change).** Build a fixture where a deprecated field is removed and `usage.json` lists it as used. The gate must exit non-zero. Run a second fixture where usage is zero, and it must exit 0. Without the first, you have no proof the gate can fail. Also test whether `considerUsage` plus the suppress rule would let the used case through. I haven't verified how the two rules compose, and my reading is that they don't compose safely. That is another reason not to enable the suppress rule.

## Before the release (not CI)

1. **Widen the Apollo window to 90 days** in the graph's check settings, or the longest the plan retains. Re-read the field's usage broken down by client name and version.
2. **Wait for the month-end run.** Re-check usage on Nov 2–3. Zero hits through a full month-end plus the 90-day lookback is real evidence. Any hit means you don't remove it.
3. **Mobile:** look at usage by client version. If old app builds still select the field, removing it makes the whole operation fail validation for them. Either keep the field or decide that the policy allows breaking those builds. A support-and-force-upgrade plan is a policy decision, so route it to `api-versioning-policy`.
4. **Reach the quiet callers.** Zero traffic only shows who is still calling, not who got the notice. Identifying and contacting the logistics customers belongs to `integration-health-monitoring`, so hand it over.
5. **Confirm the notice window.** If the policy says 6 months and a sunset date, March to a November removal likely satisfies it. Put that date in `x-sunset` or the field's `@deprecated(reason:)` text.

## Records to create if it passes

Acknowledgement row in `api/acks.json`. It is needed only if the lifecycle gate asks for an override; fill the `<…>` values at approval:

```json
{
  "id": "ack-<year>-<n>",
  "covers": ["<12-hex fingerprint>"],
  "check": "FIELD_REMOVED",
  "operation": "",
  "path": "Shipment.legacyTrackingCode",
  "text": "<graphql-inspector message, verbatim>",
  "reason": "intended-break-new-version",
  "approver": "<named reviewer group>",
  "date": "<approval date>",
  "ticket": "<ticket>",
  "notice": "<link to the March deprecation notice>",
  "behaving_since": null,
  "rationale": null
}
```

The fingerprint is the first 12 hex characters of `sha256("FIELD_REMOVED::Shipment.legacyTrackingCode:<args>")`, where `<args>` are the structured values from the change's `meta`, never the message text.

Changelog entry: `kind: removed`, `classification: breaking`, `source: diff:FIELD_REMOVED`. For `action_required`, name the replacement field. I don't know it, so supply it. Run `check-entry-trace.py` before publishing.

## What I need from you

- Is there a written breaking-change policy, with a notice window? If not, I mark every severity-map row provisional.
- What replaces `legacyTrackingCode`?
- What does Apollo show for client versions over 90 days, and after the month-end run?