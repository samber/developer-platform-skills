# Where to fish for a Senior Platform Engineer at Meridian Freight Cloud, and what to change

Your applicant pool is the predictable result of where you fished. It is not evidence that no one exists. I followed the `developer-platform-hiring` skill and its four reference files.

The skill says to interview one question at a time. You asked for the full answer in one go, so I made assumptions where I had to. Each one is marked **[assumed]** and can be vetoed.

## 1. Diagnosis

The title and the channels both point at the wrong population.

- **"Platform engineer" means internal developer platform to most of the industry.** That covers Kubernetes abstractions, CI/CD, golden paths and Backstage. PlatformCon is the flagship community for that meaning. Its 280,000+ practitioners build for their own company's engineers.
- **Your role has an external consumer.** Your 400 customer dev teams integrate against your tracking API. The skill's first gate says an external consumer puts you in a different search from internal-platform hiring.
- **Your three channels all draw the internal-IDP pool.** The PlatformCon booth, the weekly Backstage Slack posts and the "Platform Engineer" title are all aimed at that pool. Every applicant wanting to talk about operators, Argo CD and golden paths is the system working as designed.
- **The 31 applicants mean the funnel works, not that the market is empty.** Six weeks of spend went into a pool that cannot contain your hire.

## 2. Calibration (veto this paragraph if wrong)

- **Archetype [assumed]:** a bolt-on public API on an existing product, with an ambition to become a business line. The skill has a caveat here: it found no directly sourced example of this archetype. That shape is implied by Postman's finding that 84% of API teams have 1–9 people, and by postings that list "API design" as one line item in a general backend role. Treat the calibration as inference.
- **Track [assumed]:** Platform Engineer/Architect, not API PM. See §8 for why the PM gap may matter more.
- **Bar:** your own general senior backend ladder, with API-design judgment layered on. Do not use a Stripe-style staff bar of 12+ years of API-team leadership.

## 3. Artefact 1: Scorecard

**Mission:** Own the external contract of the shipment-tracking API so that third-party dev teams integrate quickly, safely and without breaking on upgrades. This is the first dedicated hire for a bolt-on API turning into a revenue line.

**Outcomes (12 months).** The numbers are placeholders. Replace them with your baselines. I don't have them.

1. Ship a versioning and deprecation policy, with a published sunset window, in the first 90 days. Then run one real deprecation under it with zero unplanned breaking changes.
2. Cut median time-to-first-successful-call for a new integrator to a target you set after measuring today's number.
3. Move [X]% of the 400 teams onto the supported API version.
4. Define SLOs for the public API (availability, latency, webhook delivery). Report against them monthly.
5. Reduce integration-related support tickets by [Y]% through better error contracts, idempotency and rate-limit behavior.
6. Ship one customer-facing capability that a paying integrator asked for. That could be webhooks, bulk endpoints or an SDK. It proves the person can ship what a customer integrates against.

**Competency weights for this track:**

| Competency | Weight |
|---|---|
| API design judgment (misuse-resistance, error messages, contract stability) | High |
| Production delivery and reliability of a customer-facing service | High |
| Infrastructure | Medium |
| Customer-facing communication | Medium |

**Must-have signal:** has shipped something outside customers integrate against and has lived with the consequences of a breaking change.

**Deliberately not weighted:** Kubernetes operators, Argo CD, Backstage and golden-path experience. They are acceptable as extras and are no longer the filter.

## 4. Artefact 2: Interview loop

The skill states plainly that no fully documented developer-platform-specific loop exists. This is an assembled design built from sourced parts: the API-design vs system-design split, and GitLab's posted structure.

1. **Recruiter or hiring-manager call.** Open with: "Tell me about an API you shipped that external developers depended on, and a change you couldn't make because of it." This screens out internal-platform-only profiles in 20 minutes.
2. **API-design round, separate from system design.** Use a prompt close to your domain, such as designing a shipment-event subscription API. The "users" are integrating developers. Judge on predictability, misuse-resistance, versioning, pagination and idempotency. Also judge whether error messages let a developer act. Do not judge scale trade-offs here.
3. **Architecture or reliability review matched to seniority.** The candidate reviews a real or sanitized slice of your current API.
4. **Hiring-manager and cross-functional conversation.** Include someone who talks to integrating customers, covering how they weigh a customer's request against contract stability.
5. **Open-source or prior public API work as evidence.** GitLab screens on reviewable contribution history. Use this only if the candidate has it. It is not a gate.

**Not confirmed by the skill:** a named versioning/backward-compatibility scenario round, and an SDK-design take-home. Both are plausible by analogy. Don't present them as industry-standard. Your interviewer-hour ceiling (skill question 9) is unknown. If it is tight, cut stage 5 and merge 3 into 2. Don't reorder.

## 5. Artefact 3: Sourcing plan

**Stop:**
- PlatformCon booth and sponsorship spend. Check whether the contract can be reduced or reassigned.
- Backstage Slack posts.

**Start:**
- **apidays.** This is the one venue the skill confirms by name for this audience. It explicitly lists "API platform engineers" and "API product managers," with 100,000+ past attendees and an OpenAPI Initiative track. Sponsor, post or recruit there instead of PlatformCon.
- **General senior-backend sourcing.** The skill says this pool overlaps more with senior backend engineering than with any specialist community. It names these channels:
  - Engineering referral networks.
  - Senior-IC pipelines.
  - Open-source contribution history as a screen.
- **Where I extend the skill (inference, not sourced):** target engineers at companies that run public APIs for developers. The skill's own logic points there, since the screening signal is "has lived with external consumers." Examples are payments, messaging, logistics and carrier APIs, or competitors' API teams. Ask your own 400 integrating teams for referrals too. Their senior engineers already know your API's shortcomings.
- **Do not use DevRel channels.** Developer-advocate boards, DevRel Slack communities and conference speaker circuits attract a different profile.

## 6. Artefact 4: Compensation stance

Anchor to Meridian's existing senior software engineer band at the equivalent level. Don't search for a "platform engineer" salary figure. The skill's sourced example is Stripe's "Staff Software Engineer, API Platform" posting: general engineering ladder, with "API Platform" as the team name. I'm not quoting a market number. The skill requires a dated source for any figure, and I haven't pulled one. If you want a benchmark, search Levels.fyi under the general title plus team name, and record the date.

## 7. What to change, in order

1. **This week:** pause the Backstage posts and review the PlatformCon booth spend.
2. **This week:** retitle the req, for example "Senior Software Engineer, Public API", and rewrite the first paragraph. State that the consumers are external developers, with 400 customer teams integrating today. State that Kubernetes and internal-platform work is not the job. The skill's gate 1 requires the posting to say which meaning of "platform engineer" it uses.
3. **This week:** run the scope-collapse self-audit (see §8).
4. **Next 2 weeks:** post through apidays and referral channels. Ask your internal customer-facing teams for the integrators who complain most, and approach their engineers.
5. **Next 2 weeks:** rebuild the loop per §4. Re-screen the 31 applicants with the stage 1 question. A few may have external-API history behind the Kubernetes talk, and the call costs 20 minutes each.
6. **Before the next req round:** confirm the interviewer-hour ceiling and whether the recruiter knows the new brief.

## 8. Scope-collapse check and open questions

The skill's red-flag pattern is a posting that stacks build work (API design and integration architecture) with outreach work (developer content and marketing) in one seat with no headcount plan. You told me "a real business line." I haven't seen your req text, so I can't tell whether it has that stack. Check three things:

- Does the req mention partner integrations, developer content or docs ownership alongside engineering? If yes, split it or state the resourcing.
- Who owns roadmap and monetization today? A business line needs pricing, packaging and roadmap decisions that an engineer should not own alone. That is an **API Product Manager** gap, and it may be a bigger hole than the engineering seat. Per the skill, the PM loop weights scoping and design thinking over coding.
- Who else works on this API surface today, and is this a first dedicated hire or an addition? Postman's data says 84% of API teams are 1–9 people, so a first dedicated hire is a real resourcing shift. Say so in the posting.

## 9. Limits of this answer

- The skill states plainly that no named, sourced hiring-red-flag taxonomy exists for developer-platform roles. The scope-collapse pattern is a structural inference from Postman's data and DevRel analogy.
- Two things in the skill are unverified: a bolt-on company example, and a dedicated API PM job board. I used general technical-PM channels filtered for API experience, as the skill advises.
- My additions are labelled inference: the "retitle" suggestion, and targeting engineers at public-API companies. The skill doesn't source them. They follow from its reasoning, and I did not verify them against outside data.
- I did not fetch live compensation data.

## 10. Decisions I need from you

1. Is Platform Engineer/Architect the right track, or is the product and monetization seat the harder hole?
2. Does the current req include any partner, content or marketing duties?
3. What is the interviewer-hour budget per candidate, and how much of the booth and sponsorship contract can you reclaim?
4. What baselines do you have for time-to-first-call and API-related support volume? The scorecard numbers depend on them.