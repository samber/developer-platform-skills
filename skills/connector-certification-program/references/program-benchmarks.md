# Connector certification program benchmarks

Read when choosing a tier shape, a revocation rule or a support statement and you want the precedent behind it. Rows marked "reported" rest on figures the operator does not publish itself.

## Contents

1. Comparison table
2. Tier labels: from quality to ownership
3. Support statements
4. Quantitative gates
5. Revocation precedents
6. Reversals and what they teach

## 1. Comparison table

| Program                                              | Labels                                                            | Quantitative gate                                                                                               | Who runs tests                                                                    | Renewal                                      | Revocation rule                       | Support for partner-built                     |
| ---------------------------------------------------- | ----------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------- | -------------------------------------------- | ------------------------------------- | --------------------------------------------- |
| Airbyte                                              | Airbyte, Enterprise, Marketplace, Custom, Archived                | test burden scales with usage; public sync-success and usage bands                                              | operator CI, required above a usage threshold; same tooling locally               | every release                                | archive for low use or no maintenance | community, no SLA                             |
| Fivetran Partner-Built                               | badge plus Private Preview, Beta, GA                              | none published                                                                                                  | not published                                                                     | none published                               | none published                        | partner SLA, joint triage                     |
| Confluent (Kafka Connect)                            | Verified Gold (all Must and Should), Verified Standard (all Must) | checklist                                                                                                       | partner self-test plus review                                                     | point-in-time                                | removal "in a matter of days"         | partner pledge                                |
| MuleSoft                                             | Select, Premium, Certified, Community                             | 65% test coverage                                                                                               | partner plus review                                                               | none published                               | none published                        | partner; operator triage on some listings     |
| Microsoft Power Platform                             | preview then GA; verified vs independent publisher                | GA: 99.95% availability, 99.5% SLO, >80% success rate                                                           | operator automated plus manual; publisher signs off in a 48-business-hour preview | every update re-validated                    | none published                        | partner, matching the backend's support model |
| Tableau                                              | Exchange listing                                                  | >90% of TDVT tests, all required tests pass or acknowledged                                                     | partner runs kit, operator reviews artifacts                                      | re-test on query-affecting change            | pulled on vulnerability until fixed   | partner, TSANet membership required           |
| dbt                                                  | Trusted vs Community                                              | pass the adapter test package                                                                                   | partner CI                                                                        | none published                               | none published                        | maintainer                                    |
| Okta Integration Network                             | published listing                                                 | all required tester cases pass, within 48 hours of submission                                                   | partner self-test, blocking; then operator QA                                     | re-test on update                            | none published                        | partner                                       |
| ServiceNow Store                                     | certified app                                                     | test plan plus architecture, performance, security review; 3-5 weeks                                            | operator team                                                                     | every platform release and every code change | implied                               | partner                                       |
| Zapier (partner-company tier, not a connector label) | Bronze to Platinum                                                | reported: 50 / 350 / 3,000 active users, or 350 with 20% quarterly growth for Platinum; plus daily health score | operator telemetry                                                                | quarterly                                    | automatic quarterly demotion          | partner                                       |
| OpenID Foundation                                    | per-profile certification                                         | pass the open conformance suite                                                                                 | implementer self-test, results published                                          | reported: per deployment                     | none published                        | not applicable                                |

## 2. Tier labels: from quality to ownership

- Airbyte retired alpha/beta/GA on 18 September 2023. Its stated reason: average sync success had passed 99%, so quality labels no longer discriminated. The new labels describe "who maintains and provides support for the connectors".
- MuleSoft, dbt and Confluent also encode ownership first, quality second.
- Power Platform separates verified publishers (who own the backend service) from independent publishers (community).

## 3. Support statements

- Fivetran: "Refer to the SLA of the partner who built the connector." Tickets go to either party, which triages by origin.
- MuleSoft "disclaims any support obligation for MuleSoft Certified Connectors". Some listings add that MuleSoft "will take initial calls from customers and isolate the issue for resolution".
- Tableau: "Partner-built connectors are not supported directly by Tableau."
- Segment catalog pages: "This integration is partner owned. Please reach out to the partner's support."
- Airbyte: Marketplace connectors "are not covered by Airbyte support SLAs".

## 4. Quantitative gates

- **Power Platform, preview to GA:**
  - Required: production backend, 99.95% availability, 99.5% SLO, >80% success rate, support matching the backend's model.
  - Recommended: 500 weekly active users over three weeks and 50 monthly active connections.
  - Exception path: six months in preview with a success rate of at least 50%.
  - Availability excludes backend-service issues and success rate excludes throttling: a published fault split.
  - Publishers must ask Microsoft for their own numbers, a known friction point.
  - A publisher publicly called the usage recommendation a catch-22, since preview status discourages production use.
- **Airbyte, partner-certified destinations:** ≥95% first-sync and overall sync success, a 3-business-day first response, and an update at least every 6 months.
- **Zapier (partner-company tier):** health is computed daily from open bugs (weighted by affected users), feature requests and responsiveness, not error rates. No tier requires more than "healthy".
- **Tableau:** required tests listed separately from the >90% overall bar. A failing required test must pass or be acknowledged as unsupported.

## 5. Revocation precedents

- **Confluent:** verified connectors it does not own "may be removed in a matter of days" for owner request, legal or security concerns, or lack of use. Example: vulnerable CDC connector versions announced on 1 September 2026 for removal on 15 September 2026, because their creator would not fix the vulnerabilities.
- **Tableau:** connectors with security vulnerabilities "will be pulled until a fix is provided".
- **Airbyte:** archived connectors receive no further updates or support.
- **Zapier:** demotion at quarter start to the tier still met.
- **Atlassian (certified app tier, adjacent):** its former Cloud Fortified tier committed to at least six months' notice before new requirements applied, with annual re-review.

## 6. Reversals and what they teach

| Reversal                                                                                                                                                                                  | Lesson                                                                                                    |
| ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------- |
| Fivetran Partner-Built closed to new partners after 13 connectors (5 sources, 8 destinations); builders redirected to a self-serve SDK                                                    | consistent with per-connector curation not scaling (no reason published)                                  |
| Atlassian Cloud Fortified closed to new submissions, phased out by end of 2026, replaced by a new enterprise certification                                                                | a certified tier can be retired; publish the transition and the end date                                  |
| Workato Partner Connectors program deprecated; partner label now at the operator's sole discretion                                                                                        | a label with no written criteria cannot be defended                                                       |
| Segment Developer Center stopped accepting new components                                                                                                                                 | partner paths get rebuilt when the integration framework changes; pin certifications to framework version |
| Microsoft's certification portal for Power Query connectors deprecated                                                                                                                    | a separate portal per connector type multiplies programs                                                  |
| Airbyte relabel, 2023                                                                                                                                                                     | quality labels stop working once everything passes them                                                   |
| Snowflake Ready validation: prerequisites are commercial (partner tier, 10 joint customers, references, a case study), and several 2025-2026 vendor press releases share template wording | commercial prerequisites turn a quality badge into co-marketing                                           |

No operator publishes certification pass rates or the causal effect of a badge on installs. Treat any adoption-lift figure as vendor marketing, not a target.
