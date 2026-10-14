# Six-month plan: backend engineer to external API platform engineer

Window: 2026-10-12 to 2027-04-11. I did not ask the skill's interview questions one at a time, so I list my assumptions at the end. Please correct them.

## 1. Course correction first ⚠️

**"Platform engineer" has two meanings, and your prep currently targets the wrong one.**

| | Internal developer platform (IDP) | External API platform |
|---|---|---|
| Consumer | The company's own engineers | Developers outside the company |
| Typical work | Kubernetes, CI/CD, Backstage, golden paths | Public API design, SDKs, webhooks, contract stability |
| Community | PlatformCon (280,000+ practitioners) | apidays |

- **Cadenza:** you would own the public REST API and the partner webhook surface. That is an **external API platform** role.
- **Vellum Labs:** you would design the SDKs customers integrate against. That is also **external**.
- ❌ **CKA is an internal-IDP credential.** The skill treats certifications in this field as largely not meaningful, and none is a stated hiring gate. Neither posting needs Kubernetes administration.
- ❌ **PlatformCon serves the IDP audience** and covers none of what these two jobs screen on. It also falls in June 2027, after this plan ends.

**Recommendations**
- Pause the CKA course. Resume only if a posting actually asks for it.
- Keep the PlatformCon booking if it is refundable or you like the event. It will not help with these two roles. Put apidays on your radar instead. I have not checked its dates.

## 2. Targets, named explicitly

| | Cadenza | Vellum Labs |
|---|---|---|
| Archetype | **Infra/API-first.** Payments, and the API is the product. | **Not yet confirmed.** Check whether SDKs are a dedicated team or one line item in a general backend role. |
| Track | **Platform Engineer** (external API). The webhook surface adds partner/integration flavor. | **Platform Engineer** (external API, client libraries and SDK design). |
| Measured on | API design quality, reliability, contract stability | Depends on archetype. Infra-first is measured on design quality, bolt-on on general delivery. |

**Ladder reference:** the only concrete high-bar example I have sourced is Stripe's "Staff Software Engineer, API Platform". It asks for 12+ years of experience and 5+ in strategic technical leadership. That is one company's posting, not an industry standard.
- With 6 years, a staff seat at an infra-first company is unlikely next year. Aim at a senior-level seat and ask in the first screen what level the role is.
- GitLab's Partner Integration Engineer ladder is the other sourced example, relevant only to the webhook/partner flavor. It asks for Go or Ruby, an open-source contribution history, and relationship skills, even at associate level.

**Compensation:** no survey-grade data exists for this niche, so I give no figures.
- Benchmark each offer against the company's general software-engineering band at the equivalent level, for example "Senior Software Engineer" at Cadenza.
- Do not search for "platform engineer" or "API platform" titles. They return sparse data.
- Pull a dated, sourced figure live before you negotiate.

## 3. What your background already gives you

- Six years of Go and Postgres is on the language list for Stripe and GitLab.
- Payments and webhooks need idempotency, transactional correctness, and retries. Postgres experience carries over directly.
- Missing: a **public track record** of API or SDK design, and any experience with external consumers.

## 4. The plan

I assume about 5 hours per week. Scale each month up or down if that is wrong.

### Month 1 (Oct–Nov): verify targets and learn the canon

1. Read both postings line by line. Mark responsibilities as external or internal, and find the team size and level.
2. Ask both recruiters (or find out otherwise) whether the team is dedicated or folded into general backend work. Most API teams are small: Postman's report puts 84% at 1–9 people. Expect breadth, not a narrow specialist seat.
3. Read the design canon:
   - Zalando's RESTful API Guidelines
   - Google's AIPs
   - Microsoft's REST API Guidelines
   - The Richardson Maturity Model
   - Brandur Leach's writing on the Stripe API, especially on change and versioning
4. Audit one API you use at work against those guidelines. Write the findings as a private one-pager.

**Exit check:** you can say which archetype each company is, and you have a ranked list of the guideline gaps in your own API.

### Month 2 (Nov–Dec): internal-API practice ground

⚠️ **Hypothesis, not an established route.** Building internal APIs carries less external-consumer accountability than shipping a public one, so it may be a lower-stakes place to practice. No practitioner account of this exact transition was found.

1. Propose an RFC or design doc at your logistics company for an internal API, webhook flow, or integration. Choose a topic with real consumers, such as a carrier or partner event feed.
2. Cover versioning, error contracts, pagination, idempotency, and the deprecation path.
3. Get it reviewed and ship it if you can.

Design docs from an employer are hard to publish. Keep a sanitized version with no confidential detail, so you can describe it in interviews.

### Month 3 (Dec–Jan): public portfolio, part 1

Build in the open:
1. A small payments-style REST API in Go and Postgres. It should have idempotency keys, a consistent error model, cursor pagination, and versioning.
2. A **webhook delivery system** next to it: signed payloads, retries with backoff, a replay endpoint, and an event schema doc. This maps to Cadenza's partner webhook surface.
3. A written design doc (RFC format) for each, explaining the decisions and the trade-offs you rejected.

Do not copy Stripe's design by default. The point is to show your own judgment.

### Month 4 (Jan–Feb): SDK and open-source signal

1. Write a Go client SDK for your sample API. Design for misuse resistance: typed errors, context support, retries, and pagination iterators. This is the Vellum Labs evidence.
2. Optionally add a thin second-language SDK, such as TypeScript, to show you can keep surfaces consistent. This is my suggestion and is not sourced from the skill.
3. Make 2–3 real contributions to a Go SDK or API-client project. GitLab names an open-source history as a requirement even at associate level.
4. Optional and informational only: look at apiMasters. Never treat it as a hiring gate.

### Month 5 (Feb–Mar): interview preparation

API design is a named interview format, separate from system design. It is judged on clarity and misuse resistance, not on scale.
1. Practice the commonly cited exercise: **design a payments API** scoped to card payments. The "users" are developers integrating it. Error messages must be specific enough to act on. This is close to Cadenza's work.
2. Practice with a peer or mock interviewer, timed. Cover versioning and breaking-change scenarios. Plausible, but I found no sourced account naming that as a formal round.
3. Prepare a story for each artifact: RFC, sample API, webhook system, SDK.
4. For Vellum, prepare for a possible take-home that designs an SDK or API surface. This is plausible by analogy only and is not confirmed.
5. Keep ordinary system design and behavioral prep going. The posted GitLab loop is a standard structured sequence: recruiter, hiring manager, 2–5 team interviews, and a possible executive round.

### Month 6 (Mar–Apr): apply and evaluate

1. Apply to Cadenza and Vellum Labs, plus 4–6 other external-API companies. Do not stake the move on two postings.
2. Before accepting any offer, re-ask the archetype question: dedicated platform org, or an API line item in a general role? Check the level and scope for under-titling.
3. Benchmark comp against the general engineering band, with source and date.

## 5. Checkpoints (tell me if you slip)

- End of month 2: one design doc shipped or reviewed.
- End of month 3: sample API and webhook system public, with RFCs.
- End of month 4: SDK public and at least one merged open-source PR.
- End of month 5: two mock API-design interviews done.

## 6. Assumptions to confirm

- The track is Platform Engineer (external API), and 5 hours per week is available.
- You are interviewing in about 6–12 months, and want a durable position rather than a one-off move.
- You have no public RFCs or open-source history yet.
- You work on internal APIs or integrations today. If not, month 2 needs a different vehicle.
- I did not check the Cadenza or Vellum postings myself. The archetype and level for both are unconfirmed.

Do you want me to adapt the plan to your real hours per week, or to turn month 3 into a concrete repo layout?