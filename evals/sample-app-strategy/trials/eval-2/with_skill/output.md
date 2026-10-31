# Sample portfolio strategy: Quillhaven (messaging and voice API), 2026-10-30

**Status: unapproved, assumed.** I got your answers in one batch, so no section is approved yet. Assumptions are marked ⚠️ and listed at the end.

## Answer first

Ship a lean portfolio that fits Lena's 30 hours a quarter:

- **Quickstart (send-SMS):** Node, Python, Java and Go in one repo, one folder per language.
- **Scenario samples:** one shared repo, 8 language-cells.
  - Node: verify-OTP, webhooks, number lookup, Conversations, inbound voice callback.
  - Python: verify-OTP, webhooks, number lookup.
- **Android sample app:** Kotlin, one flow, ships Q3.
- **Vercel template:** Node only, ships Q2.
- **Hosted collection:** a Postman-style explorer, in place of the browser playground.

Not served: the contact-center reference app and the browser playground. Ruby, PHP, .NET and Swift get no samples. They are labelled in a public tier table.

The PM's "every sample in every language" needs about 70 hours a quarter before the reference app and playground. Lena has 30.

## 1. Inventory and baseline

- ⚠️ I assume no sample repos exist today. If any exist, their upkeep comes out of the 30 hours, and they get a secret scan and a triage pass (step 4) before anything below starts.
- Planned register, one row per repo or top-level directory. Owner is Lena for every row. Last green CI is `never` (not built yet).

| ID | Type | Job | Languages | Upkeep h/qtr (self-set) |
| --- | --- | --- | --- | --- |
| `quickstart` | flagship-form quickstart, priced as tiny | first call | Node, Python, Java, Go | 6 |
| `scenarios` | scenario samples, shared repo | integrate | Node ×5, Python ×3 | 8 |
| `android-app` | mobile app | mobile | Kotlin | 8 |
| `vercel-template` | deploy template | start a project | Node | 2 |
| `explorer` | hosted collection | evaluate | n/a | 1 |

## 2. Portfolio shape

**Recommended: lean golden path, plus the mandatory mobile app and one deploy template.**

- **Gallery-led:** rejected. It needs curated intake and a repo per template, and you have one template.
- **Reference-app anchored:** rejected. A reference app costs about 16 h a quarter, which takes the steady state to 41 h against 30 h. Its voice half also cannot run in CI.

## 3. Artifact types and coverage

| Job | Artifact | Verdict |
| --- | --- | --- |
| Evaluate | hosted collection | ✅ ship; playground ❌ |
| First call | quickstart (send-SMS), 4 server folders | ✅ ship |
| Integrate one workflow | scenarios repo | ✅ ship |
| Production pattern | docs architecture page, no reference app | ⚠️ not served as an app |
| Start a project | Vercel template, Node | ✅ ship |
| Mobile | Android sample | ✅ ship, protected |
| Coding agent | canonical index plus agent guide | ✅ ship (step 7) |

**Why each cut or kept:**

- **Playground, not served:** step-up needs evaluators bouncing at setup, and you have no signal. The sandbox also cannot show voice. Add it when time-to-first-call data shows setup drop-off.
- **Contact-center reference app, not served:** add it when all three hold.
  - Deals are driven by contact-center buyers.
  - The sandbox can simulate inbound voice.
  - About 16 h a quarter is free.
- **Send-SMS scenario:** merged into the quickstart. Same code, one row.
- **Android:** the Kotlin SDK is tier 1, so the last artifact serving it is never cut. It is sequenced late instead.

**Language tiers:**

| Tier | Languages | What ships |
| --- | --- | --- |
| Supported, full | Node, Python, Java, Go | quickstart in all four |
| Supported, dominant | Node (48% of traffic), Python (31%) | scenario samples |
| Supported, new product | Node | Conversations, one language first |
| Supported, mobile | Kotlin | Android app |
| Community label or absent | Ruby, PHP, .NET, Swift | tier table plus docs snippets only |
| Not added yet | Java third in scenarios (9%) | first expansion if capacity appears |

Node and Python carry 79% of traffic. Ruby, PHP, .NET and Swift are under 2% each. A published tier table keeps the gap from reading as neglect.

**Scenario matrix** (rows are scenarios, columns are server tier-1 languages):

| Scenario | Node | Python | Java | Go |
| --- | --- | --- | --- | --- |
| send-SMS (quickstart) | tested | tested | tested | tested |
| verify-OTP | tested | tested | missing | missing |
| webhooks | tested | tested | missing | missing |
| number lookup | tested | tested | missing | missing |
| Conversations | tested | missing | missing | missing |
| inbound voice callback | present-untested | missing | missing | missing |

Parity is 4/4 for the quickstart. For the 5 non-quickstart scenarios across 4 server languages, it is 7/20 = 35% tested.

**Capacity (hours are self-set; no vendor publishes upkeep hours):**

| Cost | Hours |
| --- | --- |
| Quickstart, 4 languages × 1.5 | 6 |
| Scenario cells, 8 × 1 | 8 |
| Android | 8 |
| Vercel template | 2 |
| Collection | 1 |
| **Steady-state upkeep** | **25 of 30** |

The quickstart is priced at the tiny-quickstart rate because it has one route and no frontend. If it grows to include voice and Conversations, reprice it at about 4 h per language.

**Phasing.** Building also uses Lena's 30 hours, because ⚠️ I assume there are no separate one-off hours. Build cost is about 55 h in total (self-set), so it spreads across three quarters:

| Quarter | Build | Upkeep | Slack |
| --- | --- | --- | --- |
| Q1 | 23 h: CI harness and index 4; quickstart Node and Python 5; five Node scenarios 10; Python OTP 2; collection 2 | 3 | 4 |
| Q2 | 18 h: Python webhooks and lookup 4; quickstart Java and Go 4; Vercel 4; Android start 6 | 10 | 2 |
| Q3 | 10 h: Android finish | 17 | 3 |
| Q4 | 3 h: architecture page (if docs does not own it) | 25 | 2 |

Slack is thin in every quarter. If any quarter slips, cut in this order: Vercel template, then the Q4 architecture page. Never cut Android.

## 4. Triage

Not applicable if there is no inventory. ⚠️ Rerun this step if repos exist.

## 5. Freshness contract

- **CI:** scheduled weekly against the sandbox with test keys, plus a run on every SDK release and API version change. One shared harness for all folders.
- **Credentials:** sandbox-only keys in CI secrets, never exposed to fork PRs, rotated on a schedule. Clean up test messages and numbers after each run, and pace calls under sandbox rate limits.
- **Dependency bot:** Renovate, minor updates monthly and patch updates quarterly, grouped. Security alerts at any time. Automerge only behind green CI.
- **Red-build SLA (self-set):** automated owner ticket the same day, a fix-or-deprecate decision after 14 days red, archive after 30 days deprecated. ⚠️ The fallback decider when Lena is absent is unnamed. The SLA never fires without one.
- **Version pins:** each folder pins its SDK major, runtime and API version, checked against the SDK support window.
- **Labels the sandbox forces:**
  - **Inbound voice callback:** "compiled, not run". Add a handler test using a signed recorded payload. That checks your parsing and signature code, not the platform's behaviour.
  - **Webhooks:** ⚠️ I assume the sandbox delivers outbound webhooks. If it does not, apply the same label.
  - **Any voice step:** in the reference app or playground, the same label would apply. The sandbox gap is a main reason both are cut.

## 6. Archive rules

- Triggers:
  - Red past the SLA with no scheduled fix.
  - No owner for one review cycle, outside the adoption path.
  - Superseded by a merged or newer artifact.
  - SDK major or API version reached end of life.
  - Low usage and red together: retire first.
- Sequence: README banner with successor link, remove from every surface, redirect in the index, last secret scan, stop bots and CI, archive read-only. Never delete.
- Lena is the only owner. Name a sign-off owner (see the open questions).

## 7. Discoverability

- One `samples.json` in the samples org, owned by Lena. Fields: ID, type, job, languages, status, successor.
- It drives the docs links, GitHub topics and template flags, and the agent index and guide.
- Scaffold CLI: only if Quillhaven has a CLI. Otherwise ship `.env.example` plus the index.

## 8. Measurement

Tag every sample's API calls with its sample ID in the SDK user-agent or app-info field. Four signals per artifact:

1. Invocations (deploy button, template use, clones).
2. Time to first sandbox call from those credentials.
3. Support tickets naming the sample.
4. CI pass rate over the quarter.

Stars and forks are reported, never used to decide. Q1 sets the baseline, and the first review is end of Q1. This also tells you whether Java or Go samples, a playground or a framework template are worth adding.

**Pass gate:**

- ✅ Every kept artifact has a named owner and a freshness contract.
- ✅ Steady-state upkeep is within capacity (25 of 30 h).
- ✅ No archives yet.
- ❌ Sections not approved.

**Security and licensing:**

- Ship `.env.example`, never `.env`, with test keys only.
- License the samples MIT or MIT-0.
- Run secret scanning on every repo.
- The OTP sample must show rate limiting and abuse handling.

## Where the PM doc and this plan disagree

"Every sample in every SDK language" would mean:

- 6 scenarios × 7 server languages = 42 cell-hours, before the 30 h is even considered.
- That is about 70 h a quarter once you add the quickstart and two mobile apps.
- It adds roughly 16 h for a reference app and 8 h for a playground on top.

Parity is the quickstart's job, and it gets 4 of 4. The "second-class" worry is handled by the published tier table, not by unmaintained code.

## Open questions

1. ⚠️ Is the 30 hours all of Lena's time, build included? I assumed yes. Separate build hours would pull the phasing forward a quarter.
2. ⚠️ What does the Kotlin SDK do: OTP entry, a Conversations client, or something else? I assumed one sandbox-runnable flow. Does Lena know Android?
3. ⚠️ Does the sandbox deliver outbound webhooks and Conversations events?
4. Who signs off on archiving, and who decides when Lena is out?
5. Is there a CLI that could scaffold samples, and what sample links exist in sales decks?
6. Does anything exist today? Send the repo list and I will run step 4.