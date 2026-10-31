# Sample portfolio strategy: Thornbury Ledger, 2026-10-30

**Answer: build the reference app, narrowly. Do not build 7 quickstarts. Do not build a gallery.**

Omar's 50 hours a quarter cannot fund all three. Enterprise deals stall on "show us the whole onboarding-to-payout pattern", and only the reference app answers that.

**Status: unapproved - assumed.** I delivered the whole document at once because the interview could not run. The assumptions are listed below.

## Assumptions

1. Inventory is unknown. I did not guess. Existing sample repos, if any, are out of scope until listed.
2. Omar's 50 hours cover build and upkeep together. One-off hours were not given.
3. The sandbox simulates card success and failure. It may not simulate KYC verification outcomes, dispute lifecycle events or payout settlement timing. This is unconfirmed.
4. Head of product is the sign-off owner, and the fallback decider when Omar is absent.
5. SDK API traffic share by language is not measured. Node is assumed to dominate.
6. This is a standing policy, not a one-off cleanup.

## 1. Inventory and baseline

- Register: `unknown`. Row count, owners, red count and CI state are all unknown, and each is a finding.
- First action: run a secret scan and a dependency vulnerability scan on every existing sample repo. A hit overrides every later verdict.
- Then create one register row per repo, with a shared scenario ID across languages.

## 2. Portfolio shape

Chosen: **reference-app anchored, held to one pattern, on top of the lean core.**

- Why this shape: the flow is regulated and multi-service (KYC, cards, payouts, disputes), and deals stall on it. That is the condition the skill sets for promoting a reference app.
- Rejected, gallery-led: it needs curated intake, one repo per template and per-template telemetry. Vercel's page rests on a large team. One engineer at 50 hours cannot staff it.
- Rejected, lean golden path alone: it leaves "production pattern" thin, which is the exact deal-stall reason.
- Rejected, 7-language parity: it costs the most upkeep and serves the deals least.

## 3. Artifact types and coverage

| Job | Artifact | Languages | Status |
| --- | --- | --- | --- |
| Evaluate without installing | Hosted collection (sandbox API) | n/a | Serve |
| First call | Flagship quickstart, one repo, one folder per language | Node, Python, Java | Serve (Node first) |
| Integrate one workflow | Scenario samples in one shared repo: payout scheduling, webhooks, dispute events | Node, plus one more language by API traffic | Serve |
| Learn the production pattern | **One reference app**: seller onboarding to scheduled payout, plus docs architecture page | Node only | Serve |
| Start a project | Starter or deploy template | n/a | **Not served.** Add when telemetry shows framework concentration. |
| Mobile or device | none | n/a | **Not served.** Add if a mobile SDK reaches tier 1. |
| Coding agent | Canonical index plus agent guide | n/a | Serve (cheap, comes with step 7) |

**Language tiers**
- Supported: Node, Python, Java. Python and Java get quickstarts only, after the conference.
- Tier 2 (Go, Ruby, PHP, .NET): community-labelled or absent. Publish the tier table. A silent gap reads as neglect.

**Reference app scope (cap it, or it becomes a second product)**
- Included: seller onboarding, KYC document upload, a card-capture step, payout scheduling, and payout and dispute status driven by webhooks.
- KYC upload and card capture use provider-hosted or tokenized fields only. The app never stores documents or card numbers. A copied sample then never pulls a developer into card-data or KYC-document scope.
- Dispute *handling* (evidence submission, representment) is **not in the app**. It becomes a scenario sample and a docs page. Add it to the app only after the conference, if tickets name it.
- Name it a "reference architecture, sandbox only". Do not call it "production-grade". One part-time owner cannot back that promise, and developers will copy the code into production.

**Capacity, steady state, per quarter (all estimates self-set; no vendor publishes these)**

| Item | Hours |
| --- | --- |
| Reference app, Node (full dependency tree, infra, security review) | 16 |
| Flagship quickstart, 3 languages at about 4 | 12 |
| Scenario samples, 3 scenarios in 2 languages at about 1 | 6 |
| Hosted collection | 1 |
| Shared CI harness | 4 |
| **Total** | **39 of 50** |

The 11-hour slack absorbs sandbox gaps and fixture cleanup.

**One-off build hours, the real constraint.** The reference app alone is about 40 hours to build (self-set). That is already close to Omar's whole quarter.

**Sequence for the 10 weeks (conference about 2027-01-08; holiday weeks cut real time)**
1. Weeks 1-2: scans, shared CI harness, sandbox gap check, Node tiny quickstart (about 8 hours).
2. Weeks 3-8: Node reference app (about 40 hours).
3. Weeks 9-10: rehearsal, recorded demo as fallback, freeze. No new features.
4. After the conference: Python and Java quickstarts, then scenario samples.

**Decision needed from you:** this plan needs about 48 build hours before the conference. That leaves no slack. Either add 20-30 one-off hours (a contractor, as Twilio did), or cut KYC upload to a stubbed step. Do not cut CI.

## 4. Triage

No inventory, so no verdicts. Apply rules 1-8 in order once the register exists. Any existing red row on the adoption path (quickstart, auth, first call) is fixed in place, never archived for lack of an owner.

## 5. Freshness contract

Every kept artifact signs this contract.

1. CI against the sandbox on a weekly schedule, on every SDK release and on every API version change.
2. Sandbox-only keys in CI secrets, never exposed to fork pull requests, rotated on a schedule. Fixtures cleaned up each run. Runs paced under sandbox rate limits.
3. Grouped dependency updates: minor monthly, patch quarterly, security alerts any time. Automerge only behind green sandbox CI.
4. Red-build SLA (self-set): owner ticket the same day, fix-or-deprecate decision after 7 days red, archive after 30 days deprecated. Head of product decides when Omar is absent.
5. Pin SDK major, runtime and API version per artifact.

Flows the sandbox does not simulate (KYC verification outcomes, dispute lifecycle, settlement timing) are labelled **"compiled, not run"** in the README until they are.

## 6. Archive rules

Triggers:
- Red past the SLA with no fix scheduled.
- No named owner for one review cycle, outside the adoption path.
- Superseded by a newer artifact.
- Its SDK major or API version reached end of life.
- Low usage and red together: retire first.

Sequence: banner with successor link, swap every sales-deck and docs link, redirect in the index, last secret scan, stop bots and CI, then archive read-only. Never delete.

## 7. Discoverability

- One machine-readable index in the samples org, owned by Omar. Fields: ID, type, job, languages, status, successor.
- It drives the docs links, GitHub topics and template flags, an agent guide, and a scaffold CLI (`samples create`) that writes sandbox keys into `.env`.
- Ship `.env.example`, never `.env`. License MIT or MIT-0.
- Sales decks link to the index entry, never to a raw repo.

## 8. Measurement

Tag all sample API traffic with the sample ID through the SDK user-agent or app-info field. Four signals per artifact:
1. Invocations (scaffold or clone).
2. Time to first successful sandbox call.
3. Tickets naming the sample.
4. CI pass rate.

Business signal to add, with a baseline set in the first quarter: stalled enterprise deals that moved after the reference-app link. Stars and forks are reported, never used for decisions.

**Pass gate, current status**
- Named owner and contract for every kept artifact: Omar, pending his acceptance.
- Upkeep within capacity: 39 of 50 hours, but build hours are **not** within capacity (see section 3).
- Sections approved: none.

## Open questions, most blocking first

1. Can you add one-off build hours, or accept a stubbed KYC step?
2. Does the sandbox simulate KYC outcomes, disputes and payout timing? Which does it not?
3. What is the existing sample inventory? Send the org listing.
4. What share of API calls comes from each SDK?
5. Does Omar accept ownership?

**Next (2 minutes):** answer question 3. Paste the samples org listing, or say "none".