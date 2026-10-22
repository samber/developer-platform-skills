# Perron onsite prep: nine-day plan (Thu 2026-10-08 to Fri 2026-10-16)

**Assumptions (correct me if wrong):**
- **Track:** Platform Engineer, senior level.
- **Population:** the external, public-API-platform kind. "API platform team" at a card-payments company most likely means developers outside Perron integrate against it. It does not mean an internal developer platform (Kubernetes, Backstage, golden paths). Confirm this with the recruiter, because it changes which interviews you'll get.
- **Archetype:** probably API-first (Stripe-style), where the API is the product. That is the highest bar for API design quality and contract stability.

## Your plan is half right

⚠️ **Treating the two interviews as the same skill twice is the main flaw.** They test different things.

| | System design | API design |
|---|---|---|
| Tests | Distributed-systems architecture at scale | Decisions about an interface that developers consume, and what those decisions cost later |
| Judged on | Scale, availability, and consistency trade-offs | Clarity, predictability, and resistance to misuse |
| Scope | Full architecture | Smaller; no architecture to sketch |
| Example | Design a payment processing system | Design a payments API for card payments, where the "users" are developers integrating it |

- **Your list covers system design well.** Sharding, consistency models, cache invalidation and load balancer topologies all belong there. It covers almost none of the API design round, so grinding it for both leaves that round underprepared.
- **Source caveat:** the split is documented at Meta and other major companies, mostly through candidate-prep literature. Perron's exact format is unconfirmed, so ask the recruiter (see Day 1).
- **Payments flavor:** weight your system design prep toward payments, not generic distributed systems. A card-payments company will likely ask about idempotency, ledgers, retries and webhook delivery. Generic "design Twitter" prep serves you less.

## Take-home?

**Unknown, and I can't confirm either way.**
- No named, sourced account exists of an "API or SDK design" take-home for this track. Anything I said beyond that would be invention.
- It is plausible by analogy to the API-design interview type, but that is inference, not confirmed practice.
- You're at the onsite stage, and your recruiter email lists only the two interviews. A take-home would normally have come earlier. **Ask the recruiter directly.**
- Cheap hedge: your Day 4–6 API design practice produces a written design doc anyway, so it doubles as take-home prep.

## Day 1 (Oct 8): ask the recruiter, then baseline

Send these questions today:
1. What format is the API design round (whiteboard, shared doc, or code)? How long is it? Who interviews you (engineer, PM, staff)?
2. Is there any written or take-home component?
3. Does the API platform serve external developers or internal teams?
4. What does the rest of the onsite look like (coding, behavioral, hiring manager)? Your plan covers only two of the rounds.

Then spend the rest of the day on a timed, cold baseline. Take 45 minutes for "design a payments API", write it down, and keep it. You'll compare it against Day 9.

## Days 2–3 (Oct 9–10): system design, payments flavor

Use your own list for the generic material and add the payments-specific topics:
- **Your list:** sharding strategies, consistency models, cache invalidation, load balancer topologies.
- **Idempotency and exactly-once effects:** idempotency keys, retries, and duplicate detection under failure.
- **Money movement:** ledger and double-entry modelling, and sagas versus two-phase commit.
- **Reliable events:** the outbox pattern, and webhook delivery with retries, ordering and signing.
- **Protection:** rate limiting and backpressure for a public API.
- **Reliability:** multi-region, failure modes, and what must never be lost.

Do one full timed design each day, and talk through trade-offs out loud.

## Days 4–6 (Oct 11–13): API design, the part your plan was missing

- **Day 4: read the anchors.** Skim the frameworks that define the bar:
  - Google AIPs
  - Microsoft REST API Guidelines
  - Zalando RESTful API Guidelines ("great RESTful APIs look like they were designed by a single team")
  - Richardson Maturity Model

  Skim for the *reasoning*, not the rules. Then read how Stripe's public API handles idempotency keys, errors and pagination.
- **Day 5: practice the core exercise.** Design a card-payments API end to end:
  - **Resources and lifecycle:** authorize, capture, refund, and failure and async states.
  - **Request and response shape:** naming and consistency, a pagination strategy, and error design (specific, actionable messages).
  - **Safety:** idempotency, authentication, and rate limits.
  - **Webhooks:** event design for async state changes.
  - **Misuse-resistance:** make the wrong call hard to write.
- **Day 6: versioning and backward compatibility.** Brandur Leach's point: API developers lose the freedom to iterate as soon as one user consumes the interface. Practice "we need to change this field or behavior with live integrators". Work out additive-only changes, deprecation, and version pinning. Interview-format status: a distinct "versioning scenario" round is plausible for a senior role but **not confirmed** as one, so prepare it as a likely follow-up inside the API design round.

## Day 7 (Oct 14): mock and critique

Run one full API design mock and one system design mock, ideally with another engineer, otherwise recorded aloud. Review them against the Zalando consistency bar. Rework Day 5's design after the critique.

## Day 8 (Oct 15): your own material

- **Senior-level evidence:** prepare two or three stories where you shaped an API or abstraction, handled a breaking change, or wrote a design doc. Perron is hiring a senior; for comparison, Stripe's equivalent posting wants leadership "working on API design, abstractions, frameworks, or client libraries" and high autonomy.
- **Questions for them:** how many teams consume the platform, how they handle breaking changes, and how API review is governed.
- **Confidentiality:** be ready to describe past designs without disclosing confidential detail.

## Day 9 (Oct 16): light day

Redo the Day 1 baseline timed and compare. Reread your notes only. Confirm logistics for tomorrow and sleep.

## Open questions

These would sharpen the plan, and I haven't assumed answers:
1. Hours per day you can give this?
2. Did the recruiter say which seniority or level the role is?
3. Is the API platform external-facing, as I assumed?

**Not covered:** compensation. If an offer comes, benchmark it against Perron's general backend-engineering bands at the equivalent level, with a dated source. Don't search for "platform engineer" or "API platform" as a title.