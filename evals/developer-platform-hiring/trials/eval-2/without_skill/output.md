**Next action:** Before Monday, fill the `[BRACKETS]` (comp range, hiring manager, reporting line, location). Everything else is ready to hand over.

**Assumptions I made.** Correct any that are wrong.
- The API exists because three enterprise accounts demanded it. I treat the funding driver as **enterprise retention and expansion first, partner-built integrations second**.
- The two backend engineers stay on the API. These hires add product, architecture and partner capacity, and they don't replace those engineers.
- All targets below are **proposed 12-month outcomes**, since I have no baseline data. Calibrate them against your actual API usage numbers before the recruiter publishes anything.

---

# Scorecard 1: API Product Manager

**Mission:** Turn the REST API from an accommodation for three accounts into a product that drives enterprise retention and expansion.

**Reports to:** [CPO / VP Product]. **Level:** [Senior PM]. **Comp:** [RANGE]

**Outcomes (ranked)**
1. Within 60 days, publish a written API strategy and a 12-month roadmap. Include a named target customer segment, three prioritized use cases, and an explicit "not doing" list. The CEO and the CTO sign off.
2. Within 90 days, define and instrument the API's core metrics: activation (time to first successful call), active integrations, and API-attributed revenue. Dashboards go live.
3. By month 6, hold structured discovery with at least 15 API consumers, including the 3 original enterprise accounts. Each interview produces a documented insight, and the roadmap changes in response.
4. By month 6, establish a pricing, packaging and rate-limit position for the API, agreed with Sales and Finance.
5. By month 12, [X]% of enterprise accounts have an active integration, and [Y] of the original 3 accounts have expanded or renewed with API usage cited as a factor.
6. By month 12, get a documented API lifecycle running (versioning, deprecation policy, changelog), with zero unannounced breaking changes.

**Competencies (weights)**
| Competency | Weight |
|---|---|
| Developer-product judgment: prioritizing for integrators, not end users | 25% |
| Customer discovery with technical buyers and builders | 20% |
| Technical fluency: reads an OpenAPI spec and discusses auth, pagination and idempotency credibly | 20% |
| Metrics and commercial thinking (adoption funnel, packaging) | 15% |
| Cross-functional influence without authority (Eng, Sales, CS) | 10% |
| Writing and strategy clarity | 10% |

**Strong signals:** has owned an API or platform product with external developers; can show a roadmap decision they killed and why.
**Red flags:** only ever managed end-user UI features; treats "developer experience" as documentation only; cannot name a developer they helped.

---

# Scorecard 2: Platform Architect

**Mission:** Make the API reliable, evolvable and safe to build on, so the 2-engineer maintenance burden shrinks while the surface area grows.

**Reports to:** [CTO / VP Eng]. **Level:** [Staff / Principal]. **Comp:** [RANGE]

**Outcomes (ranked)**
1. Within 60 days, deliver an architecture assessment of the current API. It covers the data-exposure model, auth and tenancy, rate limiting, error model, and the main sources of operational toil. It ends with a ranked remediation list.
2. Within 90 days, publish API design standards (resource modeling, naming, errors, pagination, idempotency) and a versioning and deprecation mechanism, adopted by all new endpoints.
3. By month 6, add automated contract testing and spec-driven governance (a single OpenAPI source of truth, breaking-change detection in CI).
4. By month 6, define SLOs for the API with monitoring and an on-call path. Reduce API-related interrupts to the 2 engineers by [X]%.
5. By month 9, ship the foundations the product roadmap needs, such as webhooks or event delivery, scoped credentials and per-tenant limits. The PM sets which; the architect decides how.
6. By month 12, the two original engineers spend at most [X]% of their time on API maintenance and unplanned work.

**Competencies (weights)**
| Competency | Weight |
|---|---|
| API and distributed-systems design depth, shown through trade-off reasoning | 25% |
| Security, multi-tenancy and data-access design for an analytics product | 20% |
| Operational maturity: SLOs, incident learning, backward compatibility | 20% |
| Hands-on delivery: writes and reviews code, no ivory tower | 15% |
| Influence and mentoring of a small team | 10% |
| Pragmatism at 60-person scale: right-sized, no premature platform | 10% |

**Strong signals:** has run an external API through a breaking-change migration; can explain a design they would now do differently.
**Red flags:** only large-company platform experience with a dedicated platform team behind them; design-only with no code in the last 2 years; proposes a rewrite as step one.

---

# Scorecard 3: Partner Engineer

**Mission:** Get customers and partners integrated successfully and quickly, and feed what they hit back into the product.

**Reports to:** [Head of Customer Success / Solutions / PM, decide before posting]. **Level:** [Mid-Senior]. **Comp:** [RANGE]

**Outcomes (ranked)**
1. Within 30 days, complete the API as a new developer would, with a written friction log. Fix or file every blocker. This is also the baseline for onboarding time.
2. By day 90, build and publish an end-to-end quickstart and 2 reference integrations (for example, a BI tool and a warehouse or CRM) that are tested and maintained.
3. By month 6, cut median time to first successful API call from [baseline] to [target], and move the 3 original accounts to healthy production usage.
4. By month 6, run a repeatable integration-support process: response-time target, a triaged issue log, and a monthly top-5 friction report to the PM and Architect.
5. By month 12, launch a partner program v1 with a documented onboarding path and [N] partners live in production.
6. By month 12, [N] customer or partner-built integrations are live that Calder did not build itself.

**Competencies (weights)**
| Competency | Weight |
|---|---|
| Hands-on integration skill: writes working code against APIs in several stacks | 25% |
| Customer and partner communication, technical and non-technical | 20% |
| Technical writing and teaching (samples, guides) | 20% |
| Diagnostic ability: reproduces and root-causes integration problems | 15% |
| Partner and relationship building | 10% |
| Feedback discipline: turns support patterns into product input | 10% |

**Strong signals:** public sample code or integration guides; has onboarded external developers; can walk through a hard integration they unblocked.
**Red flags:** pure support or sales-engineering background with no shipped code; unable to say what they would change in our API after one hour with it.

---

## Notes for the recruiter

**Interview loop (same questions for every candidate per role)**
1. Portfolio review first. Don't ask for new work if public work exists.
2. One structured conversation per competency, with questions mapped to the scorecard.
3. One work sample, paid, scored on a fixed rubric:
   - PM: critique our API docs and propose a one-page prioritization.
   - Architect: review a sample spec and a design for a breaking change.
   - Partner Engineer: integrate with a sandbox endpoint and write the quickstart.
4. Each interviewer submits written scores with evidence before any debrief. Combine the scores by the weights above.

**Sourcing.** Look for people from API-first companies (payments, communications, data infrastructure), not only from analytics vendors.

**Hiring order I recommend.** I'd hire the PM and the Architect first and start the Partner Engineer when the first quickstart scope exists. If all three must start in Q1, keep one interviewing panel and stagger offers.

**Three decisions needed from you before posting**
1. Compensation range and jurisdiction. Pay-transparency rules vary, so confirm current requirements for your hiring location with the recruiter.
2. Who the Partner Engineer reports to. Unclear reporting is the most common reason this role fails.
3. Who owns API decisions when the PM and Architect disagree. I'd suggest the PM owns the "what" and the Architect owns the "how", with the CTO as tiebreaker.

**Posting risk check.** The three roles don't overlap on outcomes, and each states a 12-month goal and a reporting line, so none is a "do everything" role. Keep it that way when the recruiter adapts the text. Don't let them merge duties across the roles to fit a headcount cap.

**Your next step (2 minutes):** reply with the reporting lines and the baseline numbers (current API consumers, time to first call, enterprise accounts using the API). I'll replace the `[X]` targets with real ones.