**Verdict:** ⚠️ Reuse about 60% of the loop and change the rest. The system design round tests the wrong thing for this role, and the loop is missing an API design round and a staff-level leadership signal.

**Next action:** replace the URL-shortener/Twitter prompt with an API design round, as described below.

Your answers covered the archetype, the track, and the interviewer-hour ceiling. I set the other interview questions aside and list them at the end, because they change the scorecard numbers and the scope check.

## Calibration (veto if wrong)

- **Role type:** the consumers are developers outside Trellis, so this is external-API platform engineering. It is not an internal developer platform role.
- **Archetype:** infra/API-first, because the messaging API is the product. This is the highest technical bar in the skill's three archetypes.
- **Track:** Platform Engineer/Architect at staff level.
- **Bar:** Stripe's posting for "Staff Software Engineer, API Platform" asks for 12+ years of experience and 5+ years of strategic technical leadership. That is one sourced example, not an industry standard.

## 1. Sanity check on your plan

- **The usual system design prompts test scale, not API judgment.** A URL shortener or Twitter design measures distributed-systems trade-offs. This hire will be judged on whether the API is clear, predictable, hard to misuse, and stable over time.
- **Candidates have drilled those prompts, so they tell you little at staff level.** That is my judgment, not a sourced claim.
- **A separate API design round exists for this reason.** Some companies, Meta being the named example, split it from system design. It is scoped smaller than system design and judged on developer-facing usability, misuse-resistance, and error messages a developer can act on.
- **Two coding rounds are low value at staff level.** They also eat your budget. A staff candidate's open-source or code history can stand in as existing evidence.
- **Staff level needs a technical-leadership conversation.** Your senior backend loop doesn't have one.
- **Your loop matches the skill's copy-a-general-loop failure mode.** The skill's fix is to use the API-design format for engineering tracks.
- **Caveat:** no published loop exists for this exact role. What follows is an assembled design, not an industry-standard loop.

## 2. Interview loop (5.0 interviewer-hours)

The recruiter call sits outside the 5 hours, since you said a recruiter does it. I assumed debriefs also sit outside the budget. If they count, cut the coding round to 45 minutes and the system design round to 45 minutes.

| # | Round | Min | Change vs your loop |
|---|---|---|---|
| 0 | Recruiter call | - | Unchanged, not counted |
| 1 | **API design** | 60 | New |
| 2 | System design, messaging-flavored | 60 | Prompt swapped, round kept |
| 3 | **API review** | 60 | Replaces coding round 2 |
| 4 | Coding | 60 | Coding round 1 kept |
| 5 | **Staff leadership + behavioral** | 60 | Merges and upgrades the behavioral round |
| | **Total** | **300** | |

**Round 1: API design.**
- Prompt: "Design the send-message endpoint and delivery-status model for a CPaaS API."
- The candidate designs the contract, not the architecture.
- Probe for:
  - idempotency
  - async delivery states and webhooks
  - pagination
  - error taxonomy
  - rate-limit semantics
  - how a developer recovers from each failure
- Pass signal: the candidate works from the integrating developer's point of view and names how the API could be misused.

**Round 2: system design.**
- Keep the format and swap the prompt for a domain one. Examples: per-tenant rate limiting and fair queuing across carriers, or webhook delivery with retries at high volume.
- Judge the architecture, not the contract.

**Round 3: API review.**
- Give the candidate a flawed OpenAPI spec or a PR that proposes a breaking change.
- They critique it, rank the issues, and propose a migration path.
- This covers the hands-on review and versioning judgment the role needs.
- The skill does not confirm versioning scenarios as a formal industry round. It is my addition, so label it as such.

**Round 4: coding.**
- One round, your existing bar.
- Check the candidate's public code or open-source history before the round, and shorten the round if the evidence is strong.

**Round 5: leadership and behavioral.**
- Run by the hiring manager or a senior engineer.
- Probe for:
  - a breaking change or deprecation they drove across teams
  - setting API standards without direct authority
  - saying no to a product request that harms contract stability

**Cuts:**
- the second coding round
- the standalone behavioral round, folded into round 5
- generic system design prompts

## 3. Role scorecard

**Mission:** own Trellis's public messaging API surface so that it stays stable, easy to integrate, and reliable.

**Weighting for the Platform Engineer/Architect track:** API and system design first, infra delivery second.

**Outcomes:** I haven't confirmed your measurement metric, so the targets below are brackets to fill from your baselines.
1. Ship [N] additive API versions or endpoints per year with zero unannounced breaking changes.
2. Publish and enforce a written API design standard, with [X]% of new endpoints reviewed before release.
3. Cut median time-to-first-successful-message for a new integrator from [baseline] to [target].
4. Reduce API-contract support tickets by [Y]% in 12 months.
5. Run [N] deprecations to completion with a migration path and a sunset date.

## 4. Scope-collapse check

The posting passes only if "own the public API surface" does not also include partner integrations, developer content, or community work. If it does, split that work into another hire or state the resourcing in the posting. Stacking build work and outreach work in one seat is the failure pattern.

The skill describes that pattern as a structural inference, not a sourced industry taxonomy. Run this check before you publish.

## 5. Sourcing

- **Use:** apidays, your senior-backend referral networks, and open-source contribution history as a screen.
- **My addition:** engineers who have built messaging or telecom APIs at similar companies.
- **Avoid:** PlatformCon and other internal developer platform channels. They serve the wrong population for this hire.

## 6. Compensation

- Anchor the offer to your Staff Software Engineer band, not to a bespoke "platform engineer" title.
- Stripe's "Staff Software Engineer, API Platform" is the sourced example of that leveling.
- I have no live figure. Pull your own band, or look up "Staff Software Engineer" on Levels.fyi with a date. Don't quote a number from memory.

## Open questions

These change the scorecard numbers and the scope check:
1. Is this the first dedicated owner of the API surface, or an addition to an existing team?
2. What is the role measured on: contract stability, integration speed, or something else?
3. What headcount and budget does the role get?
4. Do you have a compensation range?
5. Is there a hiring deadline?
6. Is this a one-off hire, or will you reuse the loop for later hires?