# Developer Platform Engineer: scorecard and interview loop for Okabe Cloud

I skipped the usual intake questions and made the assumptions below. Veto any that are wrong. The ones that would change the design most are the first three.

## Assumptions

| # | Assumption | If wrong |
|---|---|---|
| 1 | Funding driver is **developer adoption**: integrators reaching a first successful API call and then production. | If it is sales enablement, move the weight from tutorials to demos and sales-engineer support. |
| 2 | This is the **first DevRel hire** and there is no incumbent to calibrate against. | Profile the loop from your best existing performer instead. |
| 3 | Your API is **PLG or hybrid**. Integrators can self-serve to a key. | If it is sales-led, add an enterprise-integrator outcome. |
| 4 | The role **ships code**: sample apps and SDK-adjacent work, and it reviews API ergonomics. | If code is light, you want a community manager or educator. Change the title. |
| 5 | You have **about 8 interviewer-hours per candidate** and no trained panel. | Fewer hours: drop stage 4. More hours: add a second conversational round. |
| 6 | Compensation range and jurisdiction are **not yet set**. | Confirm your location's current pay-transparency rules before publishing. |

## Role decision

**Title:** Developer Platform Engineer, a developer advocate who is product-focused and code-heavy.

**Main risk: this job is a pit trap as written.** One person runs a Discord, writes tutorials and sample apps, speaks at about three conferences a year, and collects integrator feedback. That is four pillars (community, enablement, advocacy, product input) on one headcount. Joe Nash (DevRelCon 2021) names this pattern "pit trap": a role that expects one person to cover everything with no stated goal and no resources. Do not post it as-is.

Rank the pillars and cap the costly ones:

| Rank | Pillar | Share of time | Constraint |
|---|---|---|---|
| 1 | Enablement: tutorials and sample apps | ~40% | Owns time-to-first-call. |
| 2 | Product input: integrator feedback to the product team | ~25% | A fixed monthly artefact, not ad hoc. |
| 3 | Community: Discord | ~20% | A hard cap, plus an engineering on-call rota for technical questions and volunteer or champion moderators. Discord has no natural ceiling and will eat the role otherwise. |
| 4 | Advocacy: conferences | ~15% | At most 3 talks a year, chosen where integrators are, not for reach. |

This split is my working assumption. It is not drawn from an industry standard.

## Artefact 1: Scorecard

**Mission:** Cut the time it takes an external developer to go from signup to a working production integration of the Okabe Cloud API, and feed what blocks them back into the product.

**Outcomes at 12 months, ranked.** The numbers are placeholders. Set them from your current baselines.

1. Reduce median time from signup to first successful API call by X% (set X from the current baseline; I suggest 30%).
2. Ship 6 tutorials and 3 maintained sample apps, each tested in CI against the live API and covering the top integration use cases.
3. Publish a monthly integrator-feedback digest. Get the product team to commit to or decline at least 5 items per quarter, and track how many shipped.
4. Hold the Discord to a first-response time of Y hours on weekdays, with at least 70% of technical questions answered by someone other than you. This is the sign of a self-sustaining community.
5. Deliver 3 accepted conference talks, each tied to a measurable follow-up such as signups or a tutorial's traffic.
6. Run a friction log of the whole developer journey, refreshed quarterly, with the top 10 issues owned by named product or docs people.

**Competencies and weights**

| Competency | Weight | What it covers |
|---|---|---|
| Technical depth and API judgment | 25% | Builds real integrations and spots poor API design. |
| Teaching and technical writing | 25% | Tutorials that work first time. |
| Developer empathy and product feedback | 20% | Turns raw complaints into prioritised, evidenced asks. |
| Self-direction and prioritisation | 15% | Essential for a first hire with no manager who has done the job. |
| Community and public communication | 10% | Discord and speaking. |
| Collaboration with engineering and product | 5% | Gets answers and fixes from busy people. |

**Posting self-audit**
- **Gatekeeper test.** Require only what the pillars need: production API or backend experience, public teaching evidence, and comfort speaking. Leave out "also an SDK author, an event organiser, and a designer".
- **Outcome test.** The posting lists the outcomes above, not a tactics list.
- **Level and pay test.** Level the role as senior IC, and pay to match. Publish a range, or state why you are withholding it.
- **Resources.** State the engineering support, the Discord moderator plan, and the conference budget. This is what keeps the post from being a pit trap.

## Artefact 2: Interview loop

Five stages, about 8 interviewer-hours. The portfolio review comes first because it needs nothing new from the candidate.

| # | Stage | Time | Interviewer | Tests |
|---|---|---|---|---|
| 1 | **Portfolio review** (async, before any call) | 1h | Hiring manager | Shipped public work (see Artefact 3). |
| 2 | **Conversational: role and product input** | 60 min | Hiring manager | Self-direction, feedback synthesis, prioritisation. |
| 3 | **Technical conversation: integration and API design** | 60 min | Senior backend engineer | Technical depth, API judgment. |
| 4 | **Paid live working session** | 2h, paid | Engineer plus product manager | Tutorial and sample-app craft, feedback synthesis. |
| 5 | **DevRel-opinion round and founder/exec** | 45 min | CTO or founder | Position on the discipline, and whether they would justify the function. |

**Scoring mechanics**
1. Each interviewer scores only their assigned competencies, 1 to 4, with a written evidence note.
2. Interviewers submit scores independently, before any debrief.
3. Combine mechanically using the weights above. Structured, independently scored interviews beat holistic debriefs. That is a general employment-selection finding, not a DevRel one.
4. The debrief covers only the cases where scores diverge by 2 or more points.
5. Freeze the questions and rubric before the first interview. Ask every candidate the same set.

**Question bank.** Ask 2 or 3 per competency, plus the opinion question.

*Technical depth and API judgment*
- "Here is one of our endpoints. What would you change about the design, and what would you not change?"
- "Walk me through the hardest third-party API integration you've built. What was missing from their docs?"
- "A developer's webhook handler is double-processing events. How do you diagnose it and what do you tell them?"

*Teaching and technical writing*
- "Show me a tutorial you wrote that you're proud of. Where did readers get stuck, and how do you know?"
- "How do you make sure a tutorial still works six months later?"

*Developer empathy and product feedback*
- "Tell me about feedback you brought to a product team that they initially rejected. What happened?"
- "Twelve integrators complain about the same thing. Three of them are your largest customers. How do you present it?"

*Self-direction and prioritisation*
- "You have one person and four jobs. Which do you do first in the first 90 days and which do you refuse?"
- "How would you decide whether a conference is worth a week of your time?"

*Community and communication*
- "A frustrated integrator posts publicly in Discord that our API is broken. Walk me through the next hour."
- "How do you keep a community healthy when you can't answer every question?"

*Collaboration*
- "Describe asking an engineer for help they didn't have time to give."

*DevRel-opinion (everyone gets this one)*
- "Developer relations is hard to measure. What would you want us to hold you accountable for in your first year, and what would you refuse to be measured on?"

## Artefact 3: Portfolio and work-sample evaluation

**Six signals, weighted for this role.** The weights are my assumption.

| Signal | Weight | Strong looks like |
|---|---|---|
| Teaching artefact (tutorial, workshop) | 25% | Runnable end to end, with evidence of reader success. |
| Code in public (samples, tools) | 25% | Maintained, tested, clearly documented. |
| Developer-voice artefact (feedback or friction write-up) | 20% | Specific, evidenced, actionable. |
| Public writing | 15% | Clear, accurate, not promotional. |
| Community evidence | 10% | Names developers they helped. |
| Public speaking | 5% | At least one recorded talk. |

**Negative signals to name explicitly:** follower count with no substance, only self-promotion, no shipped code, and being unable to name a developer they helped.

**Paid working session (stage 4)**
- Candidates with a strong public portfolio get a 2-hour, paid, live session. Do not set unpaid take-home work.
- Task: using our sandbox and a real, current onboarding pain point, the candidate builds or fixes a short quickstart with an engineer present, then turns a block of raw integrator feedback (provide 6 to 8 anonymised items) into a one-page prioritised brief.
- Score it on a fixed rubric: does the code run, is the explanation clear, did they ask good questions, and is the brief ranked with evidence.
- Anonymise any real customer data in the feedback sample.

## Artefact 4: 30-60-90 ramp

| Window | Goal | Deliverable |
|---|---|---|
| **Days 0-30** | Use the product as an outside developer would. | A friction log of the whole path from signup to production, with the top 10 issues ranked. |
| **Days 31-60** | Ship the first public artefact in the top-ranked pillar, paired with an engineer. | One tutorial plus a tested sample app, and the first monthly feedback digest. |
| **Days 61-90** | Own one recurring program. | Discord operating rhythm with moderator plan, and a written 12-month plan against the outcomes above, including which conferences to enter. |

## Sourcing

- Backend or integration engineers who already write public tutorials.
- Your own integrators and active Discord members. They already know the API.
- Developer-tools communities and DevRel-focused groups.
- Authors of well-maintained samples in adjacent APIs.

## Open decisions before you post

1. Compensation range and jurisdiction rules.
2. Who in engineering is on the Discord rota, and for how many hours a week.
3. Baselines for time-to-first-call, to fill in X and Y.
4. Conference budget (travel, tickets).
5. Who this person reports to. I'd suggest engineering or product, so the feedback loop has authority behind it.

If the product team can't commit to acting on feedback, the integrator-feedback outcome is hollow. Settle that before you hire.