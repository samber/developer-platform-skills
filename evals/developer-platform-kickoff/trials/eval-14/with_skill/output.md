# Hollowbrook Freight: where to start

I've read the kickoff skill and its routing reference. Two things first:

- **Cold start, no interview.** I couldn't ask the questions interactively. Question 1 (audience) is answered by your message: technology partners, 18 of them. The rest are listed below as open, with what each would change.
- **Context file not written.** `developer-platform-context.md` has no Hollowbrook project to live in. The only repo here is `example-repo`, which is the wrong place for it. A draft is at the end. Tell me which repo it belongs in and I'll write it there.

## What "better error handling" means

Your boss has named one thing, but you have three problems at three different scales. Pitching it as one project will stall it.

| Symptom | Scale | Problem |
|---|---|---|
| Two partners at 40% failures for 9 days, found out via the partner's customer calling the AE | One integration's history | Neither side could see the failure. |
| 50-minute outage, customers heard it on Twitter first | The whole platform | You had no channel to tell everyone at once. |
| "Got a 400, no idea why" tickets | One response body | The error text doesn't say what to fix. |

## Route: `samber/developer-platform-skills@integration-error-observability`

Run this one first.

- **Scope match.** Its declared scope covers "alerting partners when their integration breaks", per-integration logs with replay, and correlation IDs that survive into a support ticket. It also covers a provider-side fleet view.
- **Why first.** Nine days at 40% on two partners is the failure with the biggest cost: partner trust, and an AE blindsided in front of a customer. Your own team didn't see it either, so the provider-side fleet view is the missing piece. Eighteen partners is small enough that one person can realistically own the follow-up.
- **Cost.** Real engineering: a log store with retention and per-key error-rate aggregation. It also needs a named person who contacts partners when the view flags one.

## Short-list, ordered by value per unit of effort

1. **`integration-error-observability`**
   - **Bottleneck it attacks:** partners and you not knowing an integration is failing.
   - **Cost:** the largest build here, plus a named follow-up owner.
   - **Re-rank:** the technology-partner audience (Q1b) promoted it above its default place.
2. **`api-error-design`**
   - **Bottleneck it attacks:** the "got a 400" tickets. The integrator reads the error and fixes it alone.
   - **Cost:** one design session, then a backend change per endpoint class. It ships additively behind the responses you already publish.
   - **Shares an ID with #1:** the correlation ID in the response body is what #1 indexes.
3. **`api-status-communication`**
   - **Bottleneck it attacks:** customers learning about the outage from Twitter. It covers monitoring-driven status, push channels, update cadence and public postmortems.
   - **Cost:** a status pipeline plus a comms owner who can post during an incident. The postmortem for the 50-minute outage is a cheap first deliverable.
4. **`public-api-design-review`**
   - **Scoped to** error-envelope consistency across endpoints. A 400 that says nothing is often inconsistent across endpoints, not one bad message.
   - **Cost:** one session over an existing spec, with no deploy and no sign-off. Skip it if error-design already covers the envelope.
   - **Re-rank:** it normally leads the list. It sits here because your three incidents already name the classes below it.
5. **`api-versioning-policy`**
   - **Bottleneck it attacks:** nobody agreeing on what counts as a breaking change or who signs one off.
   - **Why it is here:** the cause of the 40% is unknown. If a contract change on your side broke those two partners, this jumps to #1. The same happens if Q4 comes back with no named signer.
   - **Cost:** coordination across product, legal and sales. It ships no code.

## Chain

None. The three incident skills are independent. They share only the correlation ID, which is a coupling and not a dependency order, so I'm not inventing a sequence.

## Not now

- **`api-idempotency-retry`**: after you learn what the 40% was. If partner retries piled on or duplicated writes, it becomes urgent.
- **`api-rate-limit-policy`**: if the 40% turns out to be 429s.
- **`integration-partnership-strategy`**: promoted by the partner audience, but it doesn't touch this month's incidents. Revisit once the fleet view exists, since it tells you which partners warrant deeper tiers.
- **Specialist protocol surfaces, second surfaces and ecosystem execution:** the audit isn't asking for them. If an answer below rules them in, they come back with that condition.

## Gap

The collection has no skill for these:

- **Your own detection and paging.** Why your monitoring didn't page on 40% failures for two partners, and the internal on-call and alerting tooling around it.
- **Fleet-wide drift across deployed integrations.** Version drift and deprecated-API usage. The observability skill surfaces errors as they happen, not drift.
- **Internal root-cause analysis.** The status skill covers the public postmortem, not the internal one. Do the RCA on the 40% yourself first.

## Proposed routines (dry-run, nothing installed)

1. **Pre-release API design review** (`public-api-design-review`)
   - **Trigger:** a spec diff on each release candidate. This is an event, not a calendar date.
   - **Output:** a comment on the spec PR, listing Must-change and Improvement findings.
2. **Quarterly kickoff re-invocation**
   - **Trigger:** the first week of each quarter.
   - **Output:** a patched context file plus a one-line note in the platform team channel.
3. **Integration fleet-health review** (`integration-error-observability`)
   - **Install only once** a named person owns partner follow-through.
   - **Trigger:** weekly, or on an error-rate alert.
   - **Output:** a ranked list of failing integrations, posted to a private channel. It names partners and traffic, so the channel must be covered by your data policy first.

## Questions still open, by the effect they'd have

1. **Q2, session goal.** Is today's goal the project's goal? I assumed it's to decide the response order to the three incidents.
2. **Q3, published surfaces.** Which are under a compatibility promise (REST, webhooks, SDKs)? Many surfaces promote `api-versioning-policy`. A committed spec makes `api-reference-quality` cheap and `public-api-design-review` a quick read.
3. **Q4, contract owner and breaking-change signer.** If there is no named signer, versioning policy becomes #1.
4. **Q5, dates and constraints.**
   - A GA or launch date within a quarter keeps the error contract and the audit up top and defers strategy.
   - A sunset deadline promotes versioning and observability.
   - Limited capacity delays the larger observability build and leaves more room for error-design and the audit.
5. **Q6, one-off or standing, and the effort ceiling.** "Hours only" cuts the list to two cheap entries. "Standing, with headcount" is what the fleet-health routine needs.
6. **Q7, what's already decided.** Any decided item leaves the list entirely.

## Draft `developer-platform-context.md` (not written to disk)

```
# Developer platform context: Hollowbrook Freight
Audience: technology partners (18). Buyer type: unknown.
Published surfaces / compatibility promise / version scheme: OPEN (Q3)
Spec locations: OPEN
Contract owner / breaking-change signer: OPEN (Q4)
In-flight: response to three incidents (2026-10): silent 9-day 40% partner failure,
  50-min outage learned via Twitter, uninformative 400s
Decided: none recorded
Open: root cause of the 40%; follow-up owner for partner alerts
Constraints: date OPEN (Q5), horizon OPEN (Q6), effort ceiling OPEN (Q6)
Stakeholders: boss (requested "better error handling"); AE (received the partner's call)
Session log:
- 2026-10-08: cold start; routed to integration-error-observability; short-list of 5; 3 routines proposed as dry-run
```

I'd keep partner names, partner traffic and unannounced dates out of any memory store and out of this file.