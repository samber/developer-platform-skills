**Drop the Python coding screen.** Hollis is an enterprise platform with about 1,200 ISV partners, which the skill treats as the "enterprise partner ecosystem" archetype. For an API Product Manager, the skill says to weight a scoping and design-thinking round over a coding round, as Google and Uber do for their PM loops. Your Head of Product's loop keeps its shape: four rounds, same order. Only the content changes.

I couldn't ask the skill's interview questions one at a time, so I assumed answers where you didn't give any. Veto any of them:

- **Consumer:** external. ISVs are the consumers, so this is in scope. It is not internal-platform engineering.
- **Role track:** API PM, first dedicated hire.
- **Measured on:** partner-facing growth metrics, such as active ISVs, time to first call and usage growth. Your growth story points here.
- **Reuse:** the next two platform hires are probably an engineer-track role and a partner or integration role. The loop is built as a shared core plus a swappable module for that reason.

## Scope check before you post the role

The skill flags a pattern where one seat gets API design, partner integrations and developer content. Each skill can be held by one person, but it is three full-time jobs. With 1,200 partners, that risk is real.

- Keep this role to product outcomes: roadmap, contract stability, partner feedback loop.
- Assign partner integration work to a partner or integration engineer, and docs and content to someone else, or state the resourcing in the posting.
- Postman data puts 84% of API teams at 1–9 people, so a lean setup is normal. The posting just has to say what the PM does not own.

## The loop

No published developer-platform-specific loop exists for every track. This is an assembled design, not an industry standard. The API-design and PM-vs-engineer split is sourced. The exact rounds below are my assembly.

| Stage | Format | What it tests | Replaces |
|---|---|---|---|
| 0. Recruiter screen | 30 min | Has owned an externally consumed API or developer-facing product. Comp fits the band. Understands the role has no team yet. | — |
| 1. Technical conversation | 45 min, with an engineer, no code | Explains how an API system fits together without hand-waving: auth, rate limits, pagination, webhooks, idempotency, versioning. Asks good questions of engineers. | Python coding screen |
| 2. API scoping and design | 60 min | Scopes a partner API capability for ISVs. For example: "design inventory-sync for ISVs." Judged on who the developer is, whether it's clear and hard to misuse, whether errors are actionable, and what a change does to 1,200 consumers. Not judged on scale or implementation. | System design round |
| 3. Roadmap and stakeholder scenario | 60 min | Prioritizes competing asks from large ISVs and internal teams. Handles a breaking change or deprecation across a large partner base. Says no with reasons. | Behavioral 1 |
| 4. Cross-functional and ownership | 45 min, with the Head of Product | Works without a team or budget. Handles conflict with engineering. Past evidence of ecosystem or partner relationships. | Behavioral 2 |

**Optional written exercise:** a roughly 90-minute written exercise, such as a one-page API proposal. Use it only if Hollis's PM process already includes one. It is plausible by analogy to Google and Meta PM loops, not a confirmed developer-platform practice.

**Cost:** about 4 interviewer-hours per candidate, plus the debrief. If you need to cut, delete stage 1 or stage 4 rather than reorder. Stage 2 is the signature round and stays.

## Scorecard

**Mission:** As the first API PM for Hollis's ~1,200-ISV partner ecosystem, grow partner-driven platform usage by owning the API roadmap, contract stability and the partner feedback loop.

**Outcomes** (fill the blanks from your own data before posting, since I have no baselines):

1. **90 days:** baseline established for active ISVs, partner API call volume and time to first production call. Roadmap and prioritization criteria published and reviewed with engineering and the top [N] ISVs.
2. **12 months:** active ISVs (at least one production call in 30 days) grow from [baseline] to [target].
3. **12 months:** time to first successful production call for a new ISV drops from [baseline] to [target] days.
4. **Ongoing:** zero unannounced breaking changes. A deprecation policy is published and applied, with at least [N] months' notice per breaking change.
5. **12 months:** [N] net-new ISV integrations go live from roadmap items you can name.
6. **12 months:** partner-originated API volume or revenue grows [x]% year over year.

**Competency weights** (my proposal, adjust to taste):

| Competency | Weight | Seen in stage |
|---|---|---|
| Roadmap and ecosystem-growth judgment | 30% | 3, 4 |
| API design judgment (usability, misuse-resistance, versioning) | 25% | 2 |
| Partner and stakeholder management | 20% | 3, 4 |
| Technical fluency | 15% | 1, 2 |
| Written and verbal scoping | 10% | 2, written exercise |

Rate each competency 1–4 with written evidence. Each interviewer scores independently before the debrief.

## Reuse for the next two hires

- **Shared core:** recruiter screen, hiring-manager interview, the scorecard format, and the debrief.
- **Track module:** swap stages 1–3 per role.
  - Platform engineer or architect: an API-design round distinct from system design, plus an architecture review.
  - Partner or integration engineer: GitLab's posted sequence is the one sourced example. It runs recruiter call, hiring-manager interview, 2–5 team interviews, and an executive round for senior hires. Treat it as an example, not a standard.

## Sourcing

- **Use:** apidays, the one confirmed venue for API platform engineers and API PMs. Also general technical-PM pipelines filtered for API or developer-facing product experience. No dedicated API-PM job board was found.
- **Don't use:** PlatformCon or Backstage channels. They serve internal-developer-platform people, not external-API ones.

## Compensation

Anchor to Hollis's own general PM bands at the equivalent level. Don't search for a bespoke "API Product Manager" title, because it returns sparse crowdsourced data. API PM levels generally mirror general PM ladders. I did not pull a live market figure, so I'm giving no number. Get a current one from your PM bands, Levels.fyi searched by general PM title, or a devtools-focused recruiter.

## Still open

- Who owns the API surface today, and does any team exist beyond this hire?
- Is the 12-month metric set right, and what are the baselines?
- What interviewer-hour ceiling do you have, and is there a recruiter?

I haven't saved this to memory. The skill suggests storing it in `developer-platform-context.md` for the repeat hires. Tell me whether that file or your CLAUDE.md is the right place.

**Next, in under two minutes:** answer the first open question (who owns the API surface today). That decides whether the scope-collapse warning applies.