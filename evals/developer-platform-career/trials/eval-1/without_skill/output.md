# Six-month plan: backend engineer to API and SDK platform roles

**Window:** Oct 2026 to Apr 2027. **Assumed budget:** about 10 h/week, roughly 250 h in total. Tell me if your real number differs and I'll rescale.

## Read this first (3 findings)

1. ⚠️ **Your two target jobs and your current study plan point in different directions.**
   - Cadenza (own the REST API and partner webhooks) and Vellum (design customer-facing SDKs) are **API and developer-experience platform** roles.
   - The CKA and PlatformCon lean toward **infrastructure platform** work (internal developer platforms, Kubernetes).
   - Your Go and Postgres background fits the API/SDK roles better than the Kubernetes track.
2. ⚠️ **PlatformCon is in June 2027, after this plan ends.** It can't help you get these jobs, because you'll be applying and interviewing from about Feb to Apr. Treat it as a networking bonus or a talk target.
3. ℹ️ **I haven't seen the Cadenza or Vellum postings.** I only know what you told me. Step 1 below is to extract their real requirements, and the plan adjusts after that.

## Recommendation

- **Keep the CKA, but cap it at about 45 h** and sit the exam by end of January. It's a credible signal and it covers deployment fundamentals.
- **Spend about 70% of your hours on one portfolio project.** It's a payments-style API with signed webhooks and two idiomatic SDKs. That is the actual job at both companies, shown in public.
- Whether you're a "platform engineer" matters less than showing you've shipped an API surface other people build on.

## Hours budget

| Track | Hours | Share |
|---|---|---|
| Portfolio project (API, webhooks, SDKs, docs) | ~175 | 70% |
| CKA (timeboxed) | ~45 | 18% |
| Interview prep and applications | ~30 | 12% |

## The portfolio project

Build **a mini payments API**, named however you like.

- **Stack:** Go, Postgres, OpenAPI-first.
- **Resources:** `customers`, `payment_intents`, `events`.
- **Must-haves (the hard parts of Cadenza's job):**
  - Idempotency keys, with a stored request fingerprint and replay of the original response.
  - Cursor pagination.
  - A consistent, typed error model.
  - API key auth with scoped keys and rate limiting.
  - Date-based or header-based API versioning.
- **Webhooks:**
  - Transactional outbox in Postgres.
  - HMAC signatures with a timestamp for replay protection.
  - Exponential backoff with jitter and a dead-letter state.
  - A delivery log and a manual replay endpoint.
  - Versioned event payloads, with at-least-once semantics documented honestly.
- **SDKs (the hard parts of Vellum's job):**
  - Generate a client from the OpenAPI spec.
  - Hand-write an idiomatic layer on top in TypeScript and Python, so you can show the generated and the designed versions side by side.
  - Auto-pagination iterators, retry and idempotency handling, typed errors, and a webhook signature verifier.
  - A changelog and a migration note for one deliberate breaking change.
- **Deploy it on Kubernetes** (kind or k3s) with manifests or Helm. This is where the CKA study becomes project evidence.
- **Docs:** a quickstart that gets a stranger to a first successful call in under 5 minutes.

## Month by month

### Month 1 (Oct to Nov): decide and set the baseline

- [ ] Read both postings line by line and build a gap matrix: requirement, evidence you have, evidence to create. **(2 h)**
- [ ] Look up each company's public API docs, SDK repos, and changelog. Note what you'd criticize and what you'd copy.
- [ ] Write the project's one-page design: resources, webhook events, SDK languages. **(3 h)**
- [ ] Set the CKA schedule: the exam date and weekly lab hours, with the exam in late January.
- [ ] Study for reference: Stripe's API docs, the Standard Webhooks spec, Google's API Improvement Proposals, and HTTP semantics (RFC 9110).
- [ ] **Work leverage:** at your logistics company, find an internal or partner-facing API or webhook. Offer to own its reliability or docs. A real production example is stronger than any side project.

**Exit check:** the gap matrix exists and the design page is written.

### Month 2 (Nov to Dec): API core

- [ ] Write the OpenAPI spec first, then the Go handlers.
- [ ] Add idempotency, pagination, errors, auth, and rate limiting, with tests around the edge cases: key reuse with a different body, concurrent same-key requests, expired keys.
- [ ] Add CI with spec linting and contract tests.
- [ ] CKA: finish the core objects (workloads, services, config) with hands-on labs.
- [ ] Plan around the holidays: expect a lighter late December.

**Exit check:** a documented API passes its contract tests and runs locally.

### Month 3 (Dec to Jan): webhooks and CKA exam

- [ ] Build the outbox, the signing, the retry and backoff, the dead-letter state, the delivery log, and the replay endpoint.
- [ ] Add failure tests: slow receiver, 500s, receiver down for hours, duplicate delivery, out-of-order events.
- [ ] Write a short design note: why at-least-once, how consumers dedupe.
- [ ] CKA: troubleshooting, networking, and storage labs, then timed mock exams in the last 2 weeks.
- [ ] **Sit the CKA by end of January.** If you're failing mocks two weeks before, move the date by 2 weeks and cut nothing from the project.

**Exit check:** webhooks survive a chaos test, and the CKA is passed or rescheduled.

### Month 4 (Jan to Feb): SDKs and deployment

- [ ] Generate the TypeScript and Python clients, then build the hand-designed layer.
- [ ] Add the webhook verifier to both SDKs.
- [ ] Write the quickstart and test it on one other person who hasn't seen the project.
- [ ] Deploy the stack to Kubernetes with manifests, a readiness probe, and a rolling upgrade you can demo.
- [ ] Ship one deliberate breaking change with a migration guide and a changelog entry.

**Exit check:** a stranger completes the quickstart unaided, and the deployment is reproducible from the README.

### Month 5 (Feb to Mar): publish and start applying

- [ ] Open-source the repo with a clean README, an architecture diagram, and a "design decisions" doc.
- [ ] Write two posts. One on idempotency and webhook delivery lessons, one on SDK design tradeoffs (generated vs hand-written).
- [ ] Learn payments basics for Cadenza: ledgers and double-entry, reconciliation, and PCI scope at a conceptual level.
- [ ] Update your resume to lead with the API and webhook work, and apply to both companies.
- [ ] Find 3 to 5 engineers at each company on LinkedIn or in their open-source repos. Send short, specific notes about their public API or SDK decisions, not "please refer me."

**Exit check:** the repo is public, both posts are live, and both applications are submitted.

### Month 6 (Mar to Apr): interviews and buffer

- [ ] Practice three interview types:
  - API design ("design a refunds endpoint").
  - System design ("design webhook delivery at scale").
  - SDK critique ("review this SDK's error handling").
- [ ] Do 2 mock interviews with peers.
- [ ] Prepare 3 stories from your logistics job about reliability, migrations, and partner integrations.
- [ ] Keep about 25% of this month as slack for slipped work.
- [ ] Check PlatformCon's CFP and speaker dates. If still open, submit a talk based on the webhook design note. If closed, just plan to attend.

**Exit check:** you're in interview loops, or you've re-targeted using what the first rejections told you.

## Decision points

| When | Question | If no |
|---|---|---|
| End of Month 1 | Do the postings really want API/SDK skills? | Re-weight toward Kubernetes and IDP work. |
| Mid-Month 3 | Are webhooks done? | Cut a second SDK language before cutting webhooks. |
| End of January | CKA passed? | Reschedule once, and don't let it block applications. |
| End of Month 5 | Applied to both? | Apply to 5 to 8 similar API-platform roles too. Don't wait on two companies. |

## What I'd cut if time runs short

1. The second SDK language (keep TypeScript, since Python is the cheaper add-on).
2. The Helm chart (plain manifests are enough).
3. The second blog post.

Don't cut the webhook failure tests or the quickstart test with a stranger. Those are what interviewers will probe.

## Questions that would change the plan

- Is your real budget closer to 5 h/week or 15 h/week?
- Which languages do Cadenza's and Vellum's SDKs target? That decides the SDK languages.
- Are both roles open now? If a posting closes before Month 5, I'd pull the application forward.
- Does your current employer have a partner-facing API you could work on? That could be your strongest single asset.