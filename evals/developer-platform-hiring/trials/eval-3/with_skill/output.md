# Nimbus Ledger: Senior API Platform Engineer

## Verdict

⚠️ **Not hireable as written. Fixable before this afternoon.**

The posting fails the skill's scope-collapse test. It stacks three full-time jobs in one seat, with no team, no reporting line, and no headcount plan:

| Function | What your draft asks for |
|---|---|
| Build | v2 public payments API, integration architecture for 12 partners |
| Outreach | developer blog, quarterly community office hours |
| Growth | +40% monthly active API keys |

Each skill can sit in one strong candidate. The execution volume cannot. This is a structural inference from Postman's small-team data (84% of API teams have 1–9 people). It is not a named industry diagnosis.

Three more problems:
- ❌ **"Reports to: TBD"** can't be posted. Senior candidates read it as "nobody owns this".
- ❌ **"Solo for now, we'll see"** is the pattern the skill flags. Say what happens next, or the best candidates screen out.
- ⚠️ **The 40% key-growth target** belongs to the whole company, not to this seat. It depends on sales, docs, partner pull, and pricing, and it has no baseline.

## Assumptions

Veto any of these.

- **External consumer:** this role builds for developers outside Nimbus Ledger, such as customers and partners. It is an external-API platform role, not an internal developer platform role. Do not post on PlatformCon or Backstage channels.
- **Archetype:** a bolt-on public API on an existing fintech product, so (b) in the skill. If payments is the product and the API is the surface, it is closer to (a), and the bar is higher.
- **Track:** Platform Engineer/Architect, weighted on API and system design.
- **Not asked:** one-off vs repeat hire, deadline, and interviewer-hour ceiling. The loop below assumes a one-off hire and about 5 interviewer-hours per candidate.

## Decide before posting

1. **Reports to:** name a person or role, such as VP/Head of Engineering or CTO.
2. **Resourcing sentence:** pick one.
   - **A (recommended):** "First dedicated API platform hire. A developer-content/DevRel hire and a partner engineer are planned once [named trigger, e.g. v2 GA or N live partners]."
   - **B:** "Solo owner of the API platform, supported by [named backend team] for implementation."
3. **Level:** confirm "Senior" maps to a specific rung on your general engineering ladder.
4. **v2 deadline:** a GA date or target quarter.

## Tightened posting (draft)

**Senior API Platform Engineer, Nimbus Ledger**
*Reports to: [name/role]. Team: [resourcing sentence from above].*

Nimbus Ledger is a Series B fintech. We are building v2 of our public payments API, and developers outside our company (customers and integration partners) are its users. This role is **external-API platform engineering**. It is not internal developer-platform work (CI/CD, Kubernetes, golden paths).

**What you'll own (first 12 months)**
- Design and ship the v2 public payments API to GA by [date]. v2 reaches GA with no unplanned breaking changes to v1 consumers, and a documented migration path.
- Set the API design standards: idempotency, error model, pagination, webhooks, and versioning policy. Review every public contract change.
- Own the integration architecture for our 12 named partner integrations: a reference integration pattern, webhook and retry reliability, and sandbox/test tooling. You are the technical lead on each. [Partner relationships are handled by ___.]
- Measure and improve developer experience: time to first successful call, p99 latency and uptime on v2 endpoints, and the share of active keys migrated to v2 within [N] months of GA.

**Also part of the job**
- Review and correct technical accuracy in API reference docs and partner guides.
- Occasionally write or co-author a technical post on API design decisions. This is optional, not a quota.

**You'll have**
- Strong API design judgment, with shipped public or partner-facing APIs in production.
- Senior backend depth. Payments, ledger, or webhook-delivery experience is a plus.
- Evidence of your work, such as an API you designed or open-source contributions. We'll review it, not just quiz you.

**Compensation:** [band], set against our Senior Software Engineer ladder. [Equity/benefits.]

**What moved out of the role, and why**
- **Developer blog and community office hours.** This is DevRel work. Keep it out until a DevRel hire exists, or until you decide this person does a small, explicit slice, such as one engineering post per quarter.
- **+40% active API keys.** Keep it as the company's goal. The role gets the leading indicators above, which an engineer can influence.

## Role scorecard

**Mission:** As the first dedicated API platform engineer at a bolt-on-API fintech, ship a stable v2 public payments API and the architecture that lets 12 partners integrate reliably. Measured on contract stability and partner integration readiness.

| # | Outcome (12 months) | Target |
|---|---|---|
| 1 | v2 GA | [date] |
| 2 | Unplanned breaking changes to v1/v2 consumers | 0 |
| 3 | Partners integrated on the reference architecture | up to 12, ranked by priority, with no per-partner custom forks |
| 4 | v2 share of active keys at [N] months post-GA | [X%], set by product |
| 5 | Time to first successful API call | [baseline → target] |
| 6 | v2 availability / p99 | [SLO] |

**Competency weights (Platform Engineer/Architect):** API and system design 40%, delivery and reliability 30%, technical communication with partners and developers 15%, technical leadership 15%.

## Interview loop

This is an assembled design. No single published developer-platform loop exists for every track.

1. **Recruiter and hiring-manager call** (about 30–45 min each). Check scope understanding and the resourcing reality.
2. **API-design round** (60 min). For example: design a card-payment API for developers integrating it. Judge developer usability and misuse-resistance, not raw scale. Probe error messages that a developer can act on. Also probe idempotency, versioning, and backward compatibility. The skill's sources do not confirm a versioning scenario as a formal round, so this is my addition.
3. **Architecture review** (60 min). A partner-integration scenario: webhook delivery, retries, and failure modes.
4. **Hands-on or code review** (60 min), matched to Senior.
5. **Evidence review.** Read the candidate's shipped APIs or open-source work, as GitLab does for its Partner Integration Engineer family. Do this asynchronously to save interviewer hours.

Add a staff-level leadership conversation only if you hire above Senior.

## Sourcing

- **apidays:** the confirmed venue for API platform engineers and API product managers.
- **Senior-backend channels:** referral networks, senior-IC pipelines, and open-source contribution history. These outperform DevRel-adjacent channels for this track.
- **Payments and fintech backend alumni.** This is my suggestion and the skill does not source it.
- ❌ **Avoid** PlatformCon, Backstage community, and internal-IDP job boards. They draw the wrong applicant pool.

## Compensation stance

- Anchor to Nimbus Ledger's **general Senior Software Engineer band**, not a bespoke "platform engineer" title.
- Check that "comp band already agreed" was set against that ladder and not a platform-title search. Crowdsourced data for those titles is sparse.
- I didn't pull live market data. I have no figure to quote, and I won't put one in a deliverable undated. To check, search Levels.fyi by "Senior Software Engineer" plus team at comparable Series B fintechs, or ask a devtools-focused recruiter.
- Stripe's "Staff Software Engineer, API Platform" shows a platform role placed on the general engineering ladder. It is one sourced example, not an industry standard.

## Quality gate

| Check | Status |
|---|---|
| States external-API (not internal-IDP) | ✅ |
| Archetype and metric named, outcomes quantified | ✅ with your numbers filled in |
| Scope-collapse self-audit | ✅ after cuts, and only if you pick a resourcing sentence |
| Loop matches track | ✅ |
| Sourcing excludes PlatformCon | ✅ |
| Comp anchored to general ladder, with source and date | ⚠️ ladder anchor yes, live figure not pulled |

## To post this afternoon

Send me four things: reports-to, A or B resourcing, v2 GA date, and the level mapping. I'll finalize the text. If you want to keep the blog and office hours in the role, tell me the headcount plan that makes it credible. Otherwise I'd post the version above.