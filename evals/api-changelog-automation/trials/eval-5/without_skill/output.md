# Not yet: hold the deletion until the Apollo data covers a month-end

"Zero operations in the last week" doesn't cover your two riskiest client groups.

## Why the evidence is too thin

1. **Your customers' month-end scripts probably haven't run in that window.** Apollo's default check window is 7 days, as far as I know, so it can't see jobs that run once a month. Today is Oct 30, so the next month-end run is tomorrow or the day after. Those are the clients most likely to still request `legacyTrackingCode`.
2. **Old mobile builds stay in the wild for months.** Users don't update and app-store review adds lag. A one-week zero can't tell you the oldest supported app version has stopped calling the field.
3. **Apollo only sees traffic that reports usage.** Scripts that hit the API outside the instrumented router won't appear. A zero from Apollo is evidence, not proof.
4. **The deprecation is 7 months old, but I don't know whether customers got a removal date.** For a public API, an email or changelog entry with a date is the real contract.

## Before the release

1. Set the Apollo operation check window to the longest your plan allows, ideally 30 days or more. Rerun the check after the month-end jobs have run.
2. Filter the usage by client name and version. Confirm the oldest app version you still support shows zero.
3. Log hits on the field in the resolver (field name plus API key or client ID) from now through month-end. This catches traffic Apollo misses. It's a few lines and fully reversible.
4. If you can't cover the full window by next week, slip the release one cycle. Alternatively, for a short time return `null` for the field and log the access, then delete it later. A brownout is easier to roll back than a deletion.

## The CI change

`suppressRemovalOfDeprecatedField` is global. It downgrades every future removal of a deprecated field, not only this one. I'd gate it on a PR label so the default stays strict. The label then records that someone approved the removal.

I couldn't see your CI config, so this assumes GitHub Actions, `schema.graphql` at the repo root, and `main` as the base branch. Adapt the paths to yours.

```yaml
# .github/workflows/schema-check.yml
name: schema-check
on:
  pull_request:
    paths: ["schema.graphql"]

jobs:
  inspector:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0 # needed so the git: ref below can read origin/main

      - uses: actions/setup-node@v4
        with:
          node-version: 22

      - name: Diff schema against main
        env:
          # Set on the PR by a reviewer who has confirmed the field is unused
          # across a full month-end cycle and every supported mobile version.
          ALLOW_DEPRECATED_REMOVAL: ${{ contains(github.event.pull_request.labels.*.name, 'approved-deprecated-removal') }}
        run: |
          RULES=""
          if [ "$ALLOW_DEPRECATED_REMOVAL" = "true" ]; then
            RULES="--rule suppressRemovalOfDeprecatedField"
          fi
          npx --yes @graphql-inspector/cli@latest diff \
            "git:origin/main:schema.graphql" \
            "schema.graphql" \
            $RULES
```

Release steps:

1. Run this workflow unchanged on the removal PR. It should still fail. That's the positive control showing the gate works.
2. Rerun the Apollo check with the longer window after month-end.
3. Add the `approved-deprecated-removal` label only once the Apollo check and the resolver logs both show zero.
4. Read the diff output. It should list only `Shipment.legacyTrackingCode` as suppressed. The rule applies to every deprecated field, so any other removal in the same PR would also pass silently.
5. Pin the CLI version instead of `@latest` if you want reproducible CI.

I haven't run this workflow. Check the `--rule` flag against your installed `@graphql-inspector/cli` version.