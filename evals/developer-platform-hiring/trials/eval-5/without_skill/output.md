# API Product Manager hiring loop (Hollis Retail Systems)

## Recommendation: keep the shape, change two stages

Keep the four-stage structure, so it still reads as your standard loop. Replace the **Python coding screen** and the **system design round**.

- **Coding screen:** a PM won't write production Python. Passing it says little about whether they'll run a partner API well, and it filters out strong API PMs who aren't engineers.
- **System design:** you'd be testing whether they can design the system, which your engineers own. Test whether they can design the *product*, with the system as a constraint.
- **What you actually need:** someone credible with 1,200 ISVs and with your engineers. That means API fluency, platform product judgment, and partner empathy. Your growth depends on it.

If Head of Product wants a coding signal, offer a compromise. Shrink stage 1 to a 15-minute "read this Python client snippet and say what breaks when we change the API". Reading code stays in. Writing it is out.

## The loop

Candidate time is about 3h45 total. Every candidate gets the same prompts, in the same order.

| # | Stage | Length | Interviewers | Replaces |
|---|---|---|---|---|
| 0 | Intro and motivation | 30 min | Hiring manager | n/a |
| 1 | API fluency screen | 45 min | Senior engineer or API architect | Python coding screen |
| 2 | Platform product design | 60 min | PM peer plus engineer | System design |
| 3 | Behavioral A: partners and engineering | 45 min | Eng lead plus partner-facing lead (DevRel, support, or partner manager) | Behavioral 1 |
| 4 | Behavioral B: judgment and ownership | 45 min | Head of Product | Behavioral 2 |

### Stage 0: Intro and motivation (30 min)

Run this as a gate, not a scored round. Check these four things:

- Do they understand the role? This is the first API PM, so they'd build the function as well as run it.
- Do they have partner or ecosystem experience, and are they interested in it?
- Are comp and level aligned?
- Would they enjoy working with ISVs?

### Stage 1: API fluency screen (45 min)

**Tests:** whether they can reason about an API as a contract with external developers.

**Exercise:** hand over a changelog between two versions of a fictional partner API (use a sanitized version of yours):

1. A field is renamed (`sku` → `item_id`).
2. `POST /orders` gains a new required parameter.
3. An enum gains a new value.
4. The rate limit drops from 600 to 300 requests per minute.
5. A `200` response becomes an async `202`.

The candidate does the following:

1. Classifies each change as breaking or not, with reasons (20 min).
2. Orders them by partner impact.
3. Sketches a versioning, deprecation, and communication plan for 1,200 ISVs (15 min).
4. Answers follow-ups (10 min).

**Answer key:**

- 1, 2, and 5 are breaking.
- 4 is breaking operationally.
- 3 is breaking for strict deserializers. Strong candidates say "depends on the client" and ask how partners parse.

**Probe:**

- "How do you find out who is calling the deprecated field?"
- "What would make you delay the change?"
- "What do you tell a partner who can't migrate for six months?"

**Strong signals:** asks who the clients are. Proposes usage telemetry before deciding. Separates "technically additive" from "safe in practice". Gives a dated deprecation timeline.

**Weak signals:** treats all changes alike. Reaches for a banner announcement. Has no plan for stragglers.

### Stage 2: Platform product design (60 min)

**Prompt:** "Partners tell us inventory sync is unreliable. Most poll our API. Design what we should offer."

The candidate will land on webhooks or events, but don't lead them there. Give them partner data around minute 35: calls per partner, error rates, and endpoints used.

**Tests:**

- **Segmentation:** the top partners and the long tail need different things. Do they notice?
- **Tradeoffs:** build vs. don't, delivery guarantees (at-least-once and idempotency), quotas, and who pays for fairness.
- **Engineering constraints:** can they absorb a "that's three quarters of work" answer and reshape scope?
- **Rollout:** who gets it first, how it's versioned, and how it's documented.
- **Success metrics (last 20 min):** can they define them? Good examples are time to first successful call, share of partners on events vs. polling, support tickets per integration, and partner-attributed revenue. Weak examples are "API calls" and "number of partners".

The engineer in the room asks one hard feasibility question. The PM peer asks "what would you cut?"

### Stage 3: Behavioral A, partners and engineering (45 min)

**Tests:** influence without authority, partner empathy, and conflict with engineering.

**Sample prompts:**

- A time you said no to a high-value customer or partner.
- A time engineering pushed back on your roadmap, and what changed.
- A time you shipped a breaking change. How did you handle the fallout?
- How do you learn what developers need when they never talk to you?

Interviewers split the topics so they don't overlap. The partner-facing lead takes the second and fourth. The eng lead takes the first and third.

### Stage 4: Behavioral B, judgment and ownership (45 min)

**Tests:** scope-setting in an unbuilt function, prioritization under ambiguity, and data-driven decisions.

**Sample prompts:**

- "You're the first API PM. What do you do in the first 90 days?" A strong answer starts with listening, an inventory of what exists, and a few early wins before any big roadmap.
- A decision made with incomplete data.
- A metric you used that turned out misleading.
- A time you were wrong, and how you found out.

Head of Product also covers the candidate's questions and the sell.

## Scorecard

Build it in two parts so it works for all three platform hires: a **core** that stays fixed and a **role module** you swap. I'm assuming the other two hires are platform-adjacent. If they're not, only the core's fit changes.

### Core outcomes (every platform hire)

Rate each 1–4 (1 = clear concern, 2 = below bar, 3 = meets bar, 4 = exceeds). Write evidence next to each score, not impressions.

| Outcome | Where tested |
|---|---|
| Partner and customer empathy: segments, listens, doesn't treat all partners alike | 2, 3 |
| Engineering partnership and influence without authority | 2, 3 |
| Judgment under ambiguity and prioritization | 2, 4 |
| Data and metrics reasoning | 2, 4 |
| Communication: clear, structured, concise | all |
| Ownership and bias to action in a function that doesn't exist yet | 0, 4 |

### Role module: API Product Manager

| Outcome | Where tested |
|---|---|
| API contract literacy: breaking changes, versioning, deprecation | 1 |
| Platform product design: tradeoffs, rollout, fairness across partners | 2 |
| Developer-experience instinct: time to first call, docs, errors, onboarding | 1, 2 |
| Ecosystem metrics: activation, retention of integrations, partner-attributed revenue | 2, 4 |

### Recommendation field

Each interviewer records **Strong hire / Hire / No hire / Strong no hire**, plus one line: "The single thing that would change my mind."

## Running it so it's reusable

1. **Fixed prompts:** keep each exercise in a shared doc with the answer key and probes. Retire a prompt only when it leaks.
2. **Written scorecards first:** interviewers submit scores and evidence before the debrief, and can't see others' scores. This prevents anchoring on whoever speaks first.
3. **Debrief:** go outcome by outcome, not candidate by candidate. A hire needs no 1s on any core outcome. Each stage's owner can veto on their dimension only if they cite evidence.
4. **Calibrate after candidate three:** compare score distributions across interviewers. If one interviewer gives all 3s, recalibrate.
5. **Next hires:** swap the role module and rewrite stages 1 and 2 around the new role's domain. Stages 0, 3, and 4 and the core scorecard carry over mostly intact.
6. **Pipeline:** with no deadline, expect two to three weeks per candidate and aim for four to six candidates through stage 2 before deciding.

## Assumptions to check

- Stage 1 and 2 exercises use a sanitized version of your real API. Don't expose internal details to candidates.
- Interviewers: you need a senior engineer, a PM peer, and a partner-facing person. Confirm who is available for all three hires, because this loop leans on them more than the engineering loop does.
- Head of Product must agree to the swap. I'd bring the compromise above and frame it as "same shape, tests what this role does."