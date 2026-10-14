# Applying for a Partner Engineer role when your design docs are under NDA

**Target (assumed from your message):** Partner/Integration Engineer track, at an enterprise platform with a large partner/ISV ecosystem. The "platform engineer" ambiguity doesn't apply here. The consumers of what you'd build are outside developers and partners, so this is the external track.

## Next action

Don't send the CV as-is. Do these three things first, in about a week:

1. Rewrite the CV around outcomes.
2. Build one public, NDA-safe artifact.
3. Ask the recruiter five questions (listed below).

## Is it really the same job?

Partly. The overlap is real, but the gap is the part they'll interview you on.

- **What carries over.** An Integration Engineer designs and supports how applications and external partners exchange data reliably: queues, iPaaS and error handling. That is your day job, and the skill's role definition describes it almost word for word.
- **What differs.** A Partner Engineer is relationship-facing. In the skill's sourced examples (GitLab, Uber), they are the technical liaison to external partners and marketplace developers.
- **What they do.** They give consultative guidance on OAuth, APIs and webhooks, gather requirements, build partner tooling and enablement, and influence the product roadmap.
- **Your side of the table.** At Marrowfield you most likely consume your carriers' APIs. As a Partner Engineer you'd be the provider, helping outsiders integrate with your employer's platform. That is my inference from your description, so correct me if you also expose APIs to external parties.
- **How you're measured.** The one sourced scorecard (GitLab's) tracks partners supported, integrations launched, integration usage and year-over-year usage growth. These are partner outcomes, not internal delivery.

Apply anyway, but frame yourself as someone who has lived on the consumer side of partner integrations and wants to move to the provider side.

## Handling the NDA

You have nothing public, but the skill treats a real employer's design doc as the hardest portfolio artifact to publish. Use these substitutes, in this order:

1. **Describe patterns, not systems.**
   - Prepare 3–4 stories with the client, schema, volumes and internal names stripped out. For example: "idempotent retry and dead-letter design for carrier webhooks", "reconciling ERP and warehouse state after partial failure", or "versioning a flow when a carrier changes its contract".
   - Check your NDA for what counts as confidential. Ask your manager or legal if it is unclear. Don't guess.
   - Don't paste or lightly paraphrase the real docs into a public place.

2. **Write one public design doc on a generic problem.**
   - Pick a problem you did not solve for Marrowfield. A good one is a partner-facing webhook and retry API for a fictional shipping platform, covering error semantics, versioning and a deprecation policy.
   - Write it the way a provider would, which is the perspective the new role needs.
   - The skill says RFC-style design docs are a checkable signal for this field.
   - Make it clear, predictable and hard to misuse, with actionable error messages. Those are the criteria the API-design interview format uses.

3. **Add open-source history.**
   - GitLab, the one sourced example, lists an open-source contribution history as a requirement, even at the associate level.
   - Your target employer may not require it, so confirm with the recruiter.
   - Cheap options are a fix, docs or an example in an SDK or connector you already use from your iPaaS or carrier work.

4. **Ask your employer for a sanitized version.**
   - Ask whether a redacted write-up of one design could be published or shared with interviewers. It's a cheap ask, and the answer may be yes.

**Hypothesis, not an established route:** your internal-integration work is a plausible practice ground for the external track. The skill found no named practitioner account of this transition, so don't present it to interviewers as a proven path.

## CV changes

- **Retitle the bullets.** Keep your real title, but write bullets in partner-facing terms: integrations shipped, third parties onboarded, incidents reduced, time to onboard a new carrier.
- **Use numbers you are allowed to share.** If you can't, use ranges or relative changes.
- **Surface external-facing work.** Examples are carrier onboarding, API contract negotiations, and debugging with a third party's engineers. This is the relationship-facing skill they screen for.
- **Match their stack.** GitLab's example asks for Ruby/Rails or Go. Check your target's actual language requirement and list any overlap.

## Interview prep

- **API design is a separate round from system design** at major companies. It is judged on clarity, misuse-resistance and consequences for the developer consuming the interface, not on scale.
- **Practice the worked example.** Design a card-payments API where the users are integrating developers, with specific, actionable error messages.
- **Practice the NDA-safe stories** out loud. Your edge is real failure handling: retries, idempotency, partial failure and versioning.
- **Expect a standard loop.** GitLab's is a recruiter call, a hiring-manager interview, 2–5 team interviews, and a possible executive round for senior hires. Treat an SDK or API take-home as plausible but unconfirmed.

## Questions for the recruiter

1. Is there a dedicated partner-engineering team with its own manager?
2. What KPIs does the role carry? Partner metrics depend on partners' own adoption pace, which you don't control.
3. What level is the role, and which engineering ladder does it map to?
4. Which languages and SDKs are expected?
5. Is an open-source or public portfolio expected, and what happens if I can't share designs for NDA reasons?

Archetypes differ. The skill warns that roles can be under-titled or under-leveled against their real scope, and most API teams are small (84% have 1–9 people), so expect breadth.

## Compensation

- Benchmark against the company's general software-engineering band at the equivalent level, not against a "partner engineer" title search, which returns sparse data.
- I have not pulled a live figure. Look for it on Levels.fyi under the general engineering title for that company before you negotiate.
- Don't rely on any undated number.

## Open questions

I assumed you are mid-level, with no deadline and a few hours a week available. These three answers would change the plan:

1. Is there a deadline? If the recruiter is pushing, the open-source and public-doc steps shrink to the recruiter questions plus the NDA-safe stories.
2. How many hours a week can you spend on a portfolio?
3. Which ecosystem do you want to be credible in: REST, webhooks, or a specific vendor's SDK?