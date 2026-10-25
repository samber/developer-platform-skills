# Conformance kit and telemetry criteria

Read when writing the criteria table (workflow step 3) or specifying the kit (step 4).

## Contents

1. Kit layers
2. Kit rules
3. Telemetry criteria
4. Criteria catalog
5. Escape hatches

## 1. Kit layers

Build the kit as layers, cheapest first. Each layer is connector-agnostic and speaks the platform's own contract, so one kit covers the whole catalog.

| Layer           | Checks                                                                                                                                         | Runs on                                          | Precedent                                                             |
| --------------- | ---------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------ | --------------------------------------------------------------------- |
| Static          | manifest validates against schema, metadata, icon, changelog, no secrets in fixtures, declared scopes                                          | every submission                                 | Airbyte QA checks; schema validation before submission                |
| Contract        | each operation exercised end to end: auth, list/discover, read, write, pagination, error mapping, rate-limit handling, state and checkpointing | every connector release, against a sandbox       | Airbyte validation tests (spec, check, discover, read); Okta's tester |
| Regression      | output of the release candidate diffed against the current version on recorded or live data                                                    | releases of connectors above the usage threshold | Airbyte regression suite                                              |
| Platform matrix | the contract layer re-run against every supported platform version                                                                             | every platform release that changes the contract | Tableau's SDK branched per product release                            |

Generate contract tests from the connector's own declared contract (its manifest or spec), not from tests the partner wrote. Partner-written tests prove internal consistency, not conformance to the platform.

## 2. Kit rules

- **Version the kit.** Semver it, publish a changelog, and record which kit version each badge was earned on. A new kit major is a renewal trigger.
- **Open the kit to partners.** Partners run the same kit locally before submitting. A pre-submission run cuts the first-pass failure rate, and Okta blocks submission until required tests pass.
- **Split required from optional tests.** Tableau's shape: an overall pass bar (>90%) plus a required list that must pass or be acknowledged as unsupported. A single percentage lets partners skip the tests that matter.
- **Regression-test the kit itself.** The OpenID Foundation reports regression-testing its open suite daily; a kit bug fails every partner at once.
- **Keep results fresh.** Okta accepts only tester passes from the 48 hours before submission, so results match the code submitted.
- **Publish results per connector.** Published logs let buyers and competitors check a claim.
- **No secrets in fixtures.** Sample values and recorded data must never contain credentials or personal data.

## 3. Telemetry criteria

Telemetry is the only evidence that tracks production behavior between releases. Each telemetry criterion needs four parts, or one bad week decides a badge:

- **Attribution:** every production call or sync is tagged with the connector and version that made it (a partner User-Agent, a connector ID on each job).
- **Window:** a trailing period long enough to smooth one incident - weeks, not days.
- **Minimum volume:** below it the criterion reads "insufficient data", never pass or fail.
- **Fault split:** errors caused by the platform's own outages are excluded from the connector's rate.

Re-evaluate on a fixed cadence and publish the date, so partners can predict their own result. Show each partner its own criteria values on the same cadence; a partner who cannot see the metric cannot fix it inside a remediation period.

## 4. Criteria catalog

Pick from this list and fill every column. A row with an empty column is not a criterion.

| Criterion                 | Example threshold                                       | Window               | Minimum volume      | Measured by        |
| ------------------------- | ------------------------------------------------------- | -------------------- | ------------------- | ------------------ |
| Contract layer pass       | all required, >90% overall                              | per release          | not applicable      | operator CI        |
| Production success rate   | ≥95% syncs or calls                                     | trailing 28 days     | ≥200 runs           | operator telemetry |
| First-run success         | ≥95% of new connections succeed on first run            | trailing 90 days     | ≥30 new connections | operator telemetry |
| Platform-version currency | passes the matrix on every supported version            | per platform release | not applicable      | operator CI        |
| Release cadence           | at least one release, or a signed no-change attestation | 6 months             | not applicable      | operator registry  |
| Support response          | first response ≤3 business days                         | trailing quarter     | ≥5 tickets          | operator ticketing |
| Security contact          | named and reachable                                     | annual check         | not applicable      | operator           |

The example thresholds echo published bars (≥95% sync success, a 3-business-day first response, an update every 6 months for one data catalog's partner-certified tier). Set your own from your baseline: certify against what your best existing connectors already achieve, not against a number borrowed from another catalog.

## 5. Escape hatches

Some operations cannot be generic-tested: destructive writes, paid actions, hardware. Let the partner flag them as exempt from generic tests, with three conditions:

- every exemption names a reason and a replacement test or manual check
- a reviewer signs off each exemption
- the exemption count shows in the published results

An unreviewed opt-out becomes the default path within a few releases.
