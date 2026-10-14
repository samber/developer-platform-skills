**Next action:** read the "Decide before Monday" list at the bottom. Four answers change the scorecards. Everything below is the handoff document. About 10 minutes to read and veto.

# Calder Analytics: developer-platform hires, Q1 2027

## Calibration (veto this first)

- **Which "platform" this is:** external API platform. The consumers are developers at customer and partner companies, not Calder's own engineers. These are not internal-developer-platform (Backstage/PlatformCon-style) roles.
- **Archetype:** bolt-on public API on a seven-year-old product. The API is four months old, driven by three enterprise accounts, and run by two backend engineers part-time.
- **Scorecard bar:** senior-to-staff on Calder's own engineering and PM ladders. The infra-first bar (12+ years, staff-level API platform leadership, as at Stripe) does not apply.
- **Metrics:** I could not ask what each role is measured on, so I assumed it. API PM: adoption and revenue outcomes. Architect: API design quality and contract stability. Partner Engineer: partner and integration counts. Change any that are wrong.
- **Sizing risk:** most API teams have 1-9 people (Postman's State of the API Report). Three specialized hires on top of two part-time engineers is above that norm. The CEO has approved the budget, so the three scorecards stand. Recommendation: **open the API PM and Platform Architect searches now, and gate the Partner Engineer search** on the conditions in that scorecard.
- **Scope-collapse check:** passes. Build, product, and partner work sit in three seats. Gap: **nobody owns developer docs, developer marketing, or community**. Each scorecard owns only the docs tied to its own work. If Calder wants a broader developer-content job, that is a fourth role, not extra scope for these three.

Targets marked *(proposed)* are my placeholders. Confirm them with the CEO or replace them with real baselines.

---

## Scorecard 1: API Product Manager

**Mission:** Turn Calder's public REST API from an enterprise-driven side project into a product with a roadmap, packaging, and a revenue line. The measure is active integrating accounts and API-attributed revenue.

**Outcomes**

1. **Day 60:** an instrumented baseline is live and reviewed monthly. It covers active API accounts, calls per account, time to first successful call, and API-related support tickets.
2. **Day 90:** a written API strategy and 12-month roadmap is approved by the CEO. It rests on the three enterprise accounts plus at least 10 interviews with other customers and prospects.
3. **Day 120:** a packaging and pricing decision is documented and agreed with Sales. It says whether the API is included, tiered, or metered.
4. **Day 180:** a versioning and deprecation policy and a changelog cadence are published. Zero unannounced breaking changes after that date.
5. **Every quarter from Q2:** at least 80% of committed roadmap items are delivered *(proposed)*.
6. **Month 12:** active API accounts reach at least 2x the day-60 baseline, and API-attributed or API-influenced revenue is reported monthly *(proposed, set the target at day 90)*.

**Competency weights**

| Competency | Weight |
|---|---|
| Roadmap and monetization judgment | 30% |
| Customer and market discovery | 20% |
| API and technical fluency (explains REST, auth, versioning without hand-waving) | 20% |
| Stakeholder management (CEO, Sales, Engineering) | 20% |
| Metrics and execution | 10% |

**Interview loop**
- Recruiter call.
- Hiring-manager interview.
- Scoping and design-thinking round, not a coding round. Example: "scope an API product for a specific customer segment."
- Roadmap-prioritization scenario with competing enterprise asks.
- Technical conversation with one of the two backend engineers. The candidate explains how APIs and systems fit together, with no code.
- Written product exercise, if Calder's PM process already uses one.

**Sourcing:** technical PM pipelines filtered for API or developer-facing product experience, plus apidays. No dedicated API-PM job board has been verified.

---

## Scorecard 2: Platform Architect (external API)

**Mission:** Make Calder's API consistent, stable, and hard to misuse. The measure is contract stability and design quality, so the two backend engineers go back to their roadmap.

**Outcomes**

1. **Day 45:** an audit of the live API is delivered. It covers resource naming, error formats, pagination, auth, and breaking-change risks, with a ranked fix list.
2. **Day 90:** API design guidelines are published. An OpenAPI spec is the source of truth, and a CI check blocks merges that introduce breaking changes.
3. **Day 180:** a versioning scheme is in production. Consistency across endpoints is 100% for new endpoints and on a dated plan for legacy ones.
4. **Day 180:** an availability and latency SLO is defined, published, and measured *(proposed: 99.9%, confirm with the CEO)*.
5. **Day 180:** unplanned API support work on the two existing engineers is cut by at least 50% from the day-30 baseline *(proposed)*.
6. **Month 12:** zero unannounced breaking changes. Time to first successful call for a new developer is at least 50% below baseline *(proposed)*.

**Competency weights**

| Competency | Weight |
|---|---|
| API design (clear, predictable, hard to misuse, actionable errors) | 30% |
| System design and reliability | 25% |
| Technical leadership without authority (works with two existing engineers) | 20% |
| Versioning and backward-compatibility judgment | 15% |
| Written decision-making and spec/reference-doc quality | 10% |

**Interview loop**
- Recruiter call.
- Hiring-manager interview.
- **API-design round**, separate from general system design. Example: design a data-export API scoped to one use case, where the users are integrating developers. Judge it on developer usability and misuse resistance, not scale.
- Architecture-review round on a sanitized slice of Calder's current API.
- Versioning and backward-compatibility scenario. This is an assembled round, not a documented industry-standard one.
- Technical-leadership conversation. Include both existing backend engineers in the loop.

**Sourcing:** general senior-backend channels (referrals, senior-IC pipelines, open-source history as a screen), plus apidays. Do **not** use PlatformCon or internal-IDP boards. They draw the wrong applicant pool.

---

## Scorecard 3: Partner Engineer (relationship-facing)

**Mission:** Get partner and enterprise integrations to production and keep them healthy. The measure is partners supported, integrations live, and integration usage growth.

**Gate before opening this search:** at least 3 named partner or integration candidates beyond the existing three accounts, and a decision on who owns the partner relationship commercially. Without a pipeline, the role has nothing to measure.

**Outcomes**

1. **Day 30:** a health review of each of the three enterprise accounts, and an integration onboarding runbook.
2. **Day 90:** each of the three accounts has a named owner and a live production integration. Integrations are counted in a shared tracker.
3. **Day 90:** time from signed integration to first production call is measured. It is cut by 30% from baseline by day 180 *(proposed)*.
4. **Day 180:** at least 5 qualified partners in the pipeline and at least 2 live integrations beyond the original three *(proposed)*.
5. **Monthly from day 60:** a structured partner-feedback digest goes to the API PM. At least half of roadmap items cite partner input.
6. **Day 180:** integration-related escalations to the backend engineers are cut by at least 50% from baseline *(proposed)*.

**Competency weights**

| Competency | Weight |
|---|---|
| Partner relationship management | 30% |
| Integration technical skill (reads and writes against REST APIs, debugs auth and pagination issues) | 25% |
| Enterprise customer communication | 15% |
| Feedback synthesis | 15% |
| Reviewable code or open-source evidence | 15% |

**Interview loop (GitLab's posted sequence)**
- Recruiter call.
- Hiring-manager interview.
- 2-5 team interviews, weighted toward relationship scenarios. Example: a partner is blocked in production and blames the API.
- Executive round only if the level is senior.

**Sourcing:** senior backend and solutions/integration engineering pipelines, plus apidays. Do not use DevRel boards or conference-speaker circuits.

---

## Compensation stance (all three)

- Anchor each offer to Calder's own general software-engineering or product-management bands at the equivalent level. Do not use a bespoke "platform engineer" or "API product manager" title search.
- Reason: Stripe's comparable role is titled "Staff Software Engineer, API Platform", which sits on its general engineering ladder. Bespoke platform titles return sparse crowdsourced data.
- I have not pulled live figures, so this document contains no salary number. If the recruiter wants outside data, search Levels.fyi by the general title plus team name, and record the source, date, and level.

## Decide before Monday

1. Level for each seat (senior or staff) on Calder's existing ladders.
2. Reporting line and budget for each hire, and who the two backend engineers report to. Missing reporting lines are a scope-collapse symptom.
3. Confirm the assumed measures (adoption and revenue for the PM, contract stability for the Architect, partner counts for the Partner Engineer), and replace the proposed numbers.
4. Whether the Partner Engineer search opens now or waits for the gate above.

**Not covered:** I did not verify any figure against the live market, and I did not interview you first, so the four decisions above stand in for the questions I could not ask.