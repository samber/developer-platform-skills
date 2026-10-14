Next action: confirm or veto the 5 assumptions below. The deliverable follows them. I made the assumptions instead of interviewing you one question at a time, so nothing here is final until you check them.

The career skill is candidate-side, so I used its mirror, `developer-platform-hiring`, plus the references of both skills.

## Assumptions (veto any)

1. **External API platform, not an internal developer platform.** The consumers are customers and partners outside Kestrel. If it is Backstage, Kubernetes or golden-path work for your own engineers, stop. That is a different search and none of this applies.
2. **Archetype: bolt-on public API on an existing product.** At 40 people you are not infra-first and have no partner-ISV org. The skill's data says that here the API is usually folded into general backend work. So this hire is a real resourcing shift.
3. **Track: Platform Engineer, senior IC.** It is not an API PM, and not a partner engineer. Reason: at 40 people nobody else owns API design judgment.
4. **First dedicated hire, solo.** You will need to name the team and budget in the posting.
5. **Compensation: your own general engineering ladder.** Pay the equivalent level, for example Senior Software Engineer. No bespoke "platform engineer" salary search. I give no salary figure. I have no dated, sourced one, and none would be reliable for this niche.

⚠️ **Scope-collapse check, before you post.** Write down who does each of these three jobs: (a) API design and contract stability, (b) partner or customer integrations, (c) developer docs and content. Postman data says 84% of API teams have 1-9 people, so this is normal. The failure is one seat owning all three with no headcount plan. The JD below makes (a) the job. It makes (b) shared, and (c) support only. If you actually want (b) and (c) owned too, you need a second hire or a stated plan for one.

---

## 1. Job description

**Senior Software Engineer, API Platform**
Kestrel Compliance · Engineering · Reports to: Head of Engineering

**Platform meaning.** This role builds the public API and integration surface that customers and partners use to build on Kestrel. It is not internal developer-platform (Kubernetes, CI/CD, Backstage) work.

**Mission.** Make Kestrel's public API a surface that developers can integrate without our help. It must stay stable for customers in a regulated space. You own its design quality and contract stability.

**What you will do**
- Own the design of the public API: resources, naming, errors, pagination, auth scopes and idempotency. Keep it consistent across endpoints.
- Write and review design docs or RFCs for every new or changed public endpoint before it ships. Act as the design reviewer for other teams' API changes.
- Define and run the versioning and deprecation policy. Decide what counts as a breaking change, and own the migration path when one is unavoidable.
- Set up the machinery: a spec as the source of truth, contract tests, breaking-change detection in CI, and rate limits.
- Make the audit-relevant parts of the API trustworthy. These are access logs, webhook delivery guarantees and data export. Compliance customers depend on them.
- Work with support and solutions engineers on integration failures. Turn recurring ones into design fixes.

**Measured on (set targets with us in your first 30 days; the numbers below are placeholders to calibrate)**
- Zero unannounced breaking changes to the public API per quarter.
- Every public endpoint change has a reviewed design doc before merge.
- API-related support tickets per active integration trend down quarter over quarter.
- Time for a customer's developer to reach a first successful call.
- Deprecations completed on schedule, with migration completion tracked.

**What you will not do:** own partner relationships or developer marketing. Technical input to docs and partner calls is welcome.

**Team and resources:** you are the first dedicated API platform engineer. You work with backend engineers who own services, with a named support or solutions contact, and with a technical writer or docs owner. *[Fill in: who these are, and whether a second hire is planned. A posting that leaves this blank fails the scope test.]*

**You might be a fit if**
- You have designed and shipped a public or partner-facing API that other companies integrated against, and lived through changing it.
- You have strong opinions on error design, idempotency, versioning and misuse-resistance, and you can defend them.
- You have written design docs that changed what shipped.

**Compensation:** *[Range from Kestrel's Senior Software Engineer band. Publish it.]*

---

## 2. Must-have vs nice-to-have

Screen on evidence you can review, not on years.

**Must-have**
1. Shipped and maintained an external-facing API through at least one breaking-change or deprecation event. Ask for specifics.
2. API design judgment: error contracts, idempotency, pagination, auth scoping, versioning. Tested live, not just claimed.
3. Strong backend engineering in your stack. You need a senior engineer who can implement the guardrails, not only review.
4. Written design docs or RFCs they can describe, even if the docs are confidential.
5. Can explain trade-offs to a developer who consumes the API and to a non-technical colleague.

**Nice-to-have**
- Compliance, audit or security-sensitive product experience (access logs, data retention, SOC 2-type constraints).
- Webhook or event delivery design, OAuth2 provider experience.
- SDK or client-library design.
- Public open-source contributions or public API design writing. Useful as existing evidence, but not a gate. GitLab treats it as required, but its role is partner-facing.

**Do not require**
- A job title containing "platform engineer", since the term mostly means internal platforms.
- Any certification. apiMasters is informational at best.
- A fixed number of years. Stripe's 12+ years is a staff-level, infra-first bar, not yours.
- Prior experience at an API-first company. Stripe itself welcomes people new to infra.

---

## 3. Interview loop

The skill says plainly that no fully documented developer-platform loop exists. This is an assembled design based on the confirmed API-design-versus-system-design split and GitLab's posted sequence. Total candidate time is about 5 hours. Interviewer-hours are about 8 per finalist. Cut stage 5 first if you must shrink it.

| # | Stage | Length | Who | What it tests |
|---|---|---|---|---|
| 1 | Recruiter or hiring-manager screen | 30 min | You | Confirms external-API experience, level and expectations. Explains the solo-first-hire reality and tests whether they want it. Look for how they describe shipped APIs and what broke. |
| 2 | Past-work deep dive | 60 min | You and a senior backend engineer | One API or design doc they shipped. Probe: what was the breaking change, how was it handled, what would they redo. Tests ownership and real versus claimed experience. |
| 3 | API design round | 60 min | Senior engineer | Design a bounded public API, for example an export-evidence or access-log endpoint for a compliance product. The users are integrating developers. Judge on clarity, predictability, misuse-resistance and actionable errors. Not on scale. Do not reuse your generic system-design question. |
| 4 | Versioning and change scenario | 45 min | You or an engineering lead | Hand them a flawed endpoint that customers already use. Ask them to plan the fix without breaking those customers: policy, communication, sunset timeline. This is not a confirmed industry format. It is my inference from how central the judgment is to the role. |
| 5 | Hands-on or design-review exercise | 60 min | Backend engineer | Review a real or sanitized PR or spec for API issues, or implement a small guardrail such as contract-test or breaking-change detection. Tests that they can build, not only advise. |
| 6 | Cross-functional conversation | 45 min | Support or solutions lead, plus the docs owner | How they work with the people who see integration pain. Do they turn tickets into design changes? Can they say no to a request without friction? |

**Scorecard rules**
- Score each stage against the five must-haves. Any miss on #1 or #2 from the must-have list is a no.
- Use the same API-design prompt for every candidate.
- An executive round is optional. GitLab adds one only for senior hires.

**Sourcing**
- Use senior-backend channels: engineering referrals, senior-IC pipelines, and open-source history as a screen.
- Use apidays for visibility.
- Do not use PlatformCon or Backstage channels. They draw the internal-platform pool, which is the wrong one.

---

## Quality gate: where this stands

- ✅ External-API meaning stated.
- ✅ Archetype and metrics named. The metric numbers are placeholders, not benchmarks.
- ⚠️ Scope test passes only if you fill the team line honestly.
- ✅ Loop matches an engineering track.
- ✅ Compensation anchored to your general ladder. No figure was quoted, because none was sourced.
- ℹ️ GitLab's and Stripe's structures are single sourced examples here, not industry standards.

## Next

Reply with corrections to assumptions 1-5, and the team line for the JD (who the solo hire works with, and whether a second hire is planned). Doing that takes about 5 minutes. I then lock the JD and write per-stage question banks and scoring rubrics.