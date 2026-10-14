# API Platform Engineer: hiring package for Kestrel Compliance

I don't know your stack, comp bands, or what your API looks like today, so I assumed the following. Change any that are wrong, because the loop depends on them.

- ⚠️ **Level:** Senior (about 6+ years), first dedicated hire, no team to lead yet. They own the API as a product and set standards for the engineers who ship endpoints.
- ⚠️ **State of the API:** It already exists and has customers or integration partners. It grew feature by feature, with inconsistent conventions, and nobody owns it as a whole.
- ⚠️ **Domain:** Customers use the API to push and pull compliance data such as evidence, controls, audit artifacts and user and asset inventories. The platform must be correct, auditable and tenant-safe, and your own SOC 2 or ISO scope covers it.
- ⚠️ **Stack:** I wrote it language-agnostic. Fill in your stack in the JD.

---

## 1. Job description

**Senior API Platform Engineer**
Kestrel Compliance · [Location / remote policy] · [Comp range]

### About Kestrel
Kestrel Compliance helps [customer type] prove they are compliant without the spreadsheet scramble. We are 40 people, and engineering is the team that makes the product trustworthy. Our customers' auditors rely on what our system records, so we treat correctness as a feature.

### The role
Our API has grown with the product. Customers and partners now build integrations on it, and it needs an owner. You will be our first dedicated API platform engineer. You will decide what a good API looks like at Kestrel, build the shared foundations that make it easy for other engineers to follow, and be accountable for how external developers experience it.

### What you'll do
- Own the public API's design standards: resource modeling, naming, pagination, filtering, error format, idempotency, and versioning.
- Build and maintain shared platform pieces such as authentication and authorization, rate limiting, request validation, webhook delivery, audit logging, and API key and OAuth management.
- Define and run the deprecation and breaking-change process so customers are never surprised.
- Make the API observable. That means per-tenant latency, error and usage dashboards, SLOs, and alerts that fire before customers write in.
- Partner with product, support and solutions engineers on integration pain points and turn the recurring ones into platform fixes.
- Drive developer experience: an accurate OpenAPI spec, a docs-from-spec pipeline, SDK or client strategy, a sandbox, and changelogs.
- Review API-affecting changes from other teams, and coach engineers on good API design without becoming a bottleneck.
- Help make the case for the next platform hires by showing, with data, where the team's time goes.

### What success looks like
- **90 days:** You have audited the current API, published a short "API standards v1" doc, shipped one visible fix (for example consistent errors or idempotency keys on write endpoints), and have usage and error dashboards that the team trusts.
- **6 months:** New endpoints follow the standards by default through templates, linting and review. Webhook delivery is reliable and inspectable. A deprecation policy is published and has been used at least once.
- **12 months:** Integration-related support tickets are down, partner onboarding is measurably faster, and you can tell us confidently whether we need a second hire and what they should do.

### About you
**You have:**
- 5+ years building backend services, including 2+ years owning an API that external developers or customers used in production.
- Real design judgment: you can explain why you chose cursor over offset pagination, how you'd version a breaking change, and what makes a retry safe.
- Hands-on experience with authN/authZ for multi-tenant systems (OAuth 2.x, scoped tokens, per-tenant isolation).
- Operational ownership: you've been on call for what you built, and you've used metrics and traces to find real problems.
- Strong written communication. Much of this role is standards, RFCs and docs that other people act on.
- Comfort being the only person in the seat, setting your own priorities, and saying no with reasons.

**Bonus points:**
- Experience in compliance, security, fintech, or other audit-heavy domains.
- Designed or ran webhook or event delivery at scale.
- Used API contract tooling (OpenAPI, linters such as Spectral, contract tests, SDK generators).
- Experience with GraphQL or gRPC and a clear view on when not to use them.
- Worked at a company of 20–100 people through the move from "endpoints" to "platform."

### How we hire
Six conversations over about two weeks, with no take-home. One is a live API design session and one is a code review of a realistic PR. We tell you the format in advance and give you feedback either way.

### Benefits
[Fill in]

*Kestrel is an equal opportunity employer. If you meet most of this but not all, apply anyway.*

---

## 2. Must-have vs nice-to-have

Screen against the must-haves only. The nice-to-haves break ties and should never reject someone.

### Must-have
| # | Requirement | Why it's a must |
|---|---|---|
| 1 | Owned a production API used by external consumers | Without this, they've never felt a breaking change |
| 2 | API design fundamentals: idempotency, pagination, errors, versioning | This is the job |
| 3 | Multi-tenant authN/authZ experience | A tenancy bug in compliance software is a trust-ending incident |
| 4 | Production operations: on call, SLOs, debugging with telemetry | Platform means reliability is part of the product |
| 5 | Clear writing | Standards only work if people read and adopt them |
| 6 | Self-direction as the first and only person in the role | No team means no one to hand them a roadmap |
| 7 | Strong in at least one backend language we can ramp them on | Language fit is secondary, but they must write real code |

### Nice-to-have
| Requirement | Note |
|---|---|
| Compliance or audit-heavy domain | Learnable in a month, so don't over-weight it |
| Webhook or event delivery at scale | Valuable, but a strong generalist picks it up |
| OpenAPI and contract tooling | Same: a skill, not a trait |
| Our exact language or framework | Only a tie-breaker |
| GraphQL or gRPC | Useful context, not required |
| Startup or scale-up experience | Useful, but big-company people who've owned APIs can also do this |
| Open source or public writing | A good signal if present, a bad filter if required |

### Decide before you post
1. **Level:** Senior or Staff? Staff means more scope and more cost, and the loop below is then weighted toward stage 6.
2. **Compliance domain:** Is it a must or a nice-to-have? I'd keep it nice-to-have, because requiring it shrinks the pool a lot.
3. **Language:** Name your stack in the JD, but don't gate on it.
4. **Comp transparency:** Include the range, because candidates at this level will ask anyway.

---

## 3. Interview loop

**Total:** a 30-minute screen plus about 5.5 hours, which can fit in one long day or two half-days. Every stage has one owner, a written rubric, and an independent scorecard submitted before the debrief.

| # | Stage | Length | Interviewer | Tests |
|---|---|---|---|---|
| 1 | Hiring manager screen | 30 min | You | Motivation, scope fit, comp, basic bar |
| 2 | Past-work deep dive | 60 min | Senior engineer | Real ownership, judgment, lessons |
| 3 | Live API design | 75 min | Senior engineer or CTO | Design thinking, tradeoffs |
| 4 | PR review exercise | 60 min | Engineer who owns relevant code | Security and correctness instincts, review style |
| 5 | Reliability and platform systems | 60 min | Engineer or SRE | Operating a platform, multi-tenancy |
| 6 | Cross-functional and consumer empathy | 45 min | PM plus support or solutions | Collaboration, customer focus, communication |
| 7 | Leadership and fit | 45 min | CTO or CEO | First-hire judgment, prioritization, values |

I'd merge stages 3 and 5 if you want a shorter loop, but you lose depth on operations.

### Stage 1: Hiring manager screen (30 min)
- **Goal:** Confirm the role is what they want and that they clear the must-have bar on paper.
- **Ask:**
  - "Tell me about an API you owned. Who used it and what broke?"
  - "What would you want to learn about our API in your first month?"
  - Comp expectations and timeline.
- **Strong signal:** They name specific consumers and specific incidents, and ask about our current pain before pitching themselves.
- **Red flags:** They describe only internal services with no external consumers. They talk about "building a platform" without any customer story.

### Stage 2: Past-work deep dive (60 min)
- **Goal:** Test depth of real ownership, which is hard to fake past 15 minutes.
- **Format:** Pick one system from their resume. Go three levels deep on "why" and "what happened next."
- **Probe:**
  - A breaking change they had to ship, and how they handled the customers.
  - An incident they caused or handled, and what changed afterwards.
  - A standard or convention they introduced, how they got adoption, and what failed.
  - Something they'd design differently now.
- **Strong signal:** They own mistakes without defensiveness, distinguish what they did from what the team did, and have numbers (traffic, latency, number of consumers).
- **Red flags:** "We" for everything, no failures, vague on scale, blames consumers.

### Stage 3: Live API design (75 min)
- **Prompt:** "Design the external API for customers to submit evidence, such as screenshots, logs and config exports, for compliance controls, and to find out when an auditor requests more." Include large file uploads, bulk submission, and notifying customers asynchronously.
- **Goal:** See how they think when the problem is ambiguous. Whiteboard or shared doc, no code.
- **What to watch:**
  1. Do they clarify who the consumers are and what they're trying to do before drawing resources?
  2. Resource modeling and naming.
  3. Idempotency on writes, and safe retries.
  4. Pagination and filtering for large lists.
  5. Error model and validation feedback.
  6. Async and webhooks: signing, retries, ordering, replay.
  7. Authorization: scopes, tenant isolation, auditor vs. customer access.
  8. Versioning and evolution: "Six months later we need to rename a field."
- **Escalation prompts:** "A customer retries a timed-out upload three times. What happens?" "An integrator's webhook endpoint is down for six hours."
- **Strong signal:** They name tradeoffs unprompted and change the design when you push on it.
- **Red flags:** Jump to endpoints without asking about consumers. Treat REST rules as dogma. No answer for retries or authorization.

### Stage 4: PR review exercise (60 min)
- **Setup:** Give them about 15 minutes to read a realistic 200–300 line PR adding a "bulk export" endpoint in our stack. Plant 6–8 issues:
  - An authorization check that verifies the user but not the tenant.
  - A non-idempotent write that is unsafe to retry.
  - An N+1 query behind a list endpoint.
  - Offset pagination on a large table.
  - An inconsistent error shape.
  - A new field that quietly breaks existing clients.
  - A log line that leaks a token or sensitive data.
  - Missing tests for the failure paths.
- **Goal:** Check instincts, prioritization and tone, not whether they find everything.
- **Strong signal:** They find the tenancy and data-leak issues first, separate blocking from non-blocking, and give feedback a junior would be able to act on.
- **Red flags:** Only style nits. Rewrites the PR instead of reviewing it. Misses the tenancy issue.

### Stage 5: Reliability and platform systems (60 min)
- **Prompt:** "One large tenant's integration is hammering the API and other customers see latency. Walk me through diagnosing it, then fixing it for good."
- **Goal:** Test whether they treat the API as a running system.
- **Probe:**
  1. Triage and observability: what do you look at first? What should already exist?
  2. Rate limiting design: algorithm, per-tenant vs. per-key vs. per-endpoint, response headers, and how to tell the customer.
  3. Fair queuing and noisy-neighbor isolation.
  4. Webhook delivery architecture: queues, retries with backoff, dead-letter handling, delivery logs.
  5. SLOs: what would you commit to publicly?
  6. Rollout safety: how do you ship a change to auth middleware?
- **Strong signal:** They reach for data before fixes, think about the customer communication as part of the fix, and know what they'd cut for a small team.
- **Red flags:** Jumps straight to "add a gateway." Cannot name what they'd measure.

### Stage 6: Cross-functional and consumer empathy (45 min)
- **Interviewers:** Product plus someone from support or solutions engineering.
- **Exercises:**
  1. Role-play: "A key customer's integration broke after yesterday's release. I'm their engineer, on a call, and annoyed. Talk to me."
  2. Write, live or beforehand, a short deprecation notice for a field we're removing.
  3. "Product wants a new endpoint by Friday that would break your standards. What do you do?"
- **Strong signal:** They stay calm and curious with the angry customer, write plainly, and negotiate the tradeoff instead of just refusing.
- **Red flags:** Condescension about non-engineers. Standards-as-gatekeeping. Jargon in the customer-facing writing.

### Stage 7: Leadership and fit (45 min)
- **Interviewer:** CTO or CEO.
- **Goal:** Check they will thrive as the first person in the seat.
- **Ask:**
  - "You have 90 days and nobody telling you what to do. What do you do in week one?"
  - "How do you decide what *not* to build?"
  - "Tell me about a time you had to influence engineers who didn't report to you."
  - "What would make you leave in a year?"
- **Strong signal:** A concrete, sequenced plan that begins with listening and measuring. They are comfortable with ambiguity and set expectations.
- **Red flags:** Wants a defined roadmap handed over. Wants to rewrite everything first.

---

## 4. Scorecard and decision process

### Scorecard
Each interviewer scores independently, **before** reading anyone else's, on a 1–4 scale. There is no middle score, so no one can hide.

| Score | Meaning |
|---|---|
| 4 | Strong hire. Clearly above the bar for this level |
| 3 | Hire. Meets the bar |
| 2 | Lean no. Gaps that matter |
| 1 | No hire |

### Dimensions
1. API design judgment (stages 3, 4)
2. Production and reliability maturity (stages 2, 5)
3. Security and tenancy instincts (stages 3, 4, 5)
4. Communication and writing (stages 2, 6, 7)
5. Collaboration and customer empathy (stage 6)
6. Self-direction and prioritization (stages 1, 7)

### Decision rules
- **Hire:** No score of 1, at most one 2, and none of those 2s in dimensions 1, 2, or 3.
- **Hard stop:** Failing to notice the tenancy issue in stage 4 *and* having no tenant-isolation answer in stage 3. In a compliance product, that gap isn't coachable on our timeline.
- **Debrief:** 30 minutes, held within 24 hours of the final stage. Written scorecards first, discussion second. The hiring manager speaks last.
- **Level check:** If the candidate is strong but below the bar for senior, don't hire them anyway. Re-scope the role or pass. This role has no one above it to catch mistakes.

### Process notes
- **Calibrate the exercises first.** Have two current engineers do stages 3 and 4 before you use them, and fix any ambiguity they hit.
- **Same questions for everyone.** Vary only the follow-ups.
- **Share the format in advance.** Send candidates the stage list and tell them stage 3 is whiteboard and stage 4 is review.
- **Keep to about two weeks.** Senior API people have other offers, and a slow loop loses them.
- **Reference checks:** Ask for someone who consumed their API, not only their manager.

---

## 5. Questions to settle before launch
1. Seniority: Senior, or Staff?
2. Real comp range, and equity?
3. Remote policy and time zones?
4. Which stack goes in the JD?
5. Who are the interviewers for stages 2, 4 and 5? You need at least two trained on each.
6. Does anyone inside the company currently own API decisions informally? If so, bring them into the loop early so the hire doesn't threaten them.

I can tighten any section next. I can also draft the stage 4 PR with the planted bugs, or the stage 3 rubric as a one-page handout for interviewers, once you give me your stack.