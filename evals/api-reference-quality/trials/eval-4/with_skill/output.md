# Hexavolt API reference plan: one quarter (about 13 weeks)

## Verdict

**Next action (this week):** run the census (step 1 below). Do not start with the try-it console.

Leadership asked for a try-it console and Stripe-style samples. That is stage 4 of a five-stage rollout. Stage 4 sits on stages 1 to 3, and your setup lacks all three:

- **Drift is structural.** The docs are hand-edited Docusaurus pages. Every finding an audit would produce will come back, because a page edited by hand is a second copy of the contract. No spec linter protects pages nobody regenerates.
- **The swagger file is unverified.** "Mostly right" is not a source of truth. Nothing tests it, so a console built on it would execute wrong examples against your own API.
- **The language tabs are not per-language parity.** A widget that converts curl into Python, TypeScript and Java HTTP-client syntax is relabeled curl. It does not call your official SDKs, and it can never show SDK idioms such as pagination helpers, typed errors or retries. This audit does not count it as parity.

**Recommended tier: the full generated-docs migration.** Two things drive this:

- The reference is hand-maintained, which is the first condition that promotes the migration.
- You have a full quarter funded, which makes the effort affordable.

The ranking moves on your answers like this:

| Answer | Effect |
| --- | --- |
| Hand-edited docs | Promotes the migration |
| A quarter of effort | Makes the migration affordable |
| Safe staging cluster | Keeps contract tests in scope; without it they would be deleted from the menu |
| Standing-gate mandate (unanswered) | Would reinforce the migration; a one-off cleanup would demote it |
| Hard deadline inside the quarter (unanswered) | Would make lint-only the first increment |

The rollout is sequenced so each stage ships value on its own. If the quarter is cut short, you still keep the lint and contract gates, which are the cheap and durable part.

Nothing below is measured yet. I have not seen your swagger file, docs or SDKs, so I invent no coverage numbers. Step 1 produces them.

## Questions that change the plan

Answer these in one batch. I proceed on the stated assumptions until you do.

1. **Swagger version and location.** Is it 2.0 or 3.x, and does it live in the same repo as the API code? *Assumption: 2.0, separate repo. A 2.0 spec needs conversion to OpenAPI 3.x in week 1.*
2. **How are the three SDKs produced?** Are they generated from the spec or hand-written? *Assumption: hand-written. That favors a CI-tested snippet repo over regenerating the SDKs (see stage 4).*
3. **Audience.** Are readers third-party integrators, internal developers, or coding agents? *Agent readers fail differently, since they invent calls from ambiguous annotations. Route that work to the `coding-agent-docs-optimization` skill. The same spec feeds both.*
4. **Is the quarter a one-off cleanup or a standing gate you keep for years?** *Assumption: standing gate.*
5. **Staging cluster limits.** Are there per-key rate limits, test-data isolation, and is the data safe to reset? *The try-it console will expose staging to anyone who loads the docs.*
6. **Team.** Who owns the docs, and is there a docs-platform engineer or only API engineers?

## Plan by stage

### Weeks 1-2: Census and stage 1 prerequisites

**Census.** Diff the swagger file against the published pages in both directions, and against the SDK method lists.

| Operation | In spec? | In published reference? | In SDKs? | Discrepancy |
| --- | --- | --- | --- | --- |
| *(one row per operation)* | | | | |

- Live-but-undocumented operations are blockers, because integrators guess.
- Documented-but-removed operations are blockers, because they destroy trust in the surrounding pages.
- Probe beyond the spec. Check gateway logs on staging and prod, SDK internals, and support tickets that name endpoints the docs lack. Spec-inference research (RESTSpecIT, 2024, preprint) found undocumented-but-valid routes in shipped production APIs, so "in the swagger" does not mean "complete".

**Audit.** Grade every operation on the 15-row rubric. Three rows are the ones usually skipped:

- error codes with cause and fix
- idempotency and retry safety, which matters for a metering API where a retried usage write could double-count
- ordering constraints, such as "register the meter before posting readings"

**Report.** Produce coverage percentages for operations, parameters, responses (at least one 4xx each), error codes with cause and fix, and snippet parity. Add a findings table by severity. The report's first paragraph states that hand-maintained docs mean every finding recurs.

**Deliverable:** the census table, the audit report, and a decision on how to render docs from the spec.

### Weeks 2-5: Stage 1, adopt the source of truth

Goal: no reference page is ever edited independently of the spec.

1. Convert the swagger file to OpenAPI 3.x and fix what the census found. Every operation gets an `operationId` and description, every parameter a type, required flag, constraints and example, and every response code is listed.
2. Render the reference from the spec. You have two routes:
   - **Stay on Docusaurus** with a spec-to-pages generator plugin. This is the smaller migration but is not in the skill's tooling catalog, so check its maintenance status and try-it support before committing.
   - **Move the reference to a spec-driven platform** from the catalog: Redocly, Stoplight, Bump.sh, Mintlify, ReadMe or Zuplo. You get try-it and `x-codeSamples` rendering out of the box. Docusaurus can keep guides and tutorials.
3. Delete the hand-written endpoint tables. Keep hand-written prose only for guides, and keep those out of the reference to avoid quadrant drift.

**Pass:** zero reference pages edited outside the spec.

### Weeks 3-6: Stage 2, lint gate (overlaps with stage 1)

- Add **Spectral**, **Redocly CLI** or **Vacuum** to CI on every PR that touches the spec. Vacuum has example-based rules, which target the most common gap in public specs: parameter examples are absent from 86.95% of 2,529 public specs (OASQuali, peer-reviewed, ICWE 2026).
- Minimum ruleset: per-operation description and `operationId`, documented responses including a 4xx, examples on parameters and schemas.
- Start at warn severity. Flip to fail-on-warn once the spec is clean.

**Pass:** zero lint errors at the chosen ruleset. Alternatively score at least 80/100 on RateMyOpenAPI. 80 is that tool's default bar, not an industry average.

### Weeks 5-8: Stage 3, contract tests against staging

Staging is safe to call, so this rung stays on the menu.

- Run **Schemathesis** against staging in CI. Property-based tests generate inputs from the schema. They check that no generated input yields a 500 and that every response matches the documented schema.
- Add **oasdiff** for breaking-change diffs between spec versions. Do not use Optic, which was archived in January 2026.
- **Expect findings.** Practitioners report 5 to 15 issues on a first run against a production schema (practitioner consensus). That is normal and means the spec was inaccurate, not that the tool is broken. Fix the spec or the API, then close the loop.
- Use isolated test accounts and clean up the data these runs create.

**Pass:** CI fails on any generated-input 500, any schema-violating response, and any undiffed breaking change.

### Weeks 8-12: Stage 4, snippet parity and try-it console

This is the part leadership asked for. It goes here because it depends on stages 1 to 3.

**Per-language samples (Python, TypeScript, Java).** The samples must call your official SDKs, not translated curl. Two ways:

- **If the SDKs are generated:** generate `x-codeSamples` overlays from the same generator (Speakeasy, Fern, Stainless or APIMatic) so samples and SDKs change together.
- **If the SDKs are hand-written (my assumption):** build a Twilio-style snippet repo with one sample per operation per language. CI runs every sample against staging or a fake server before merge, and snippets are versioned with SDK releases. Regenerating three SDKs just to get samples is poor value.

Retire the curl-conversion widget for SDK languages. Keep curl as the one honest raw-HTTP tab.

**Try-it console.** Embed the platform's console, with a pre-filled test key for logged-in users. That is the Stripe pattern.

- **Point it at staging only.** Use a scoped test key, with rate limits and a daily data reset.
- **Teach the ID scheme in examples.** Stripe uses typed resource-ID prefixes such as `ch_` and `cus_`. If your IDs are not typed, ask the API team whether they can be, or at least make example IDs consistent.
- **Cost of staying on staging.** Staging is not production behavior. State on the console page that it runs against a sandbox.

**Pass (the full-migration tier's gate):** every shipped language has a working sample on every operation. That is 100% of operations × 3 languages, enforced in CI.

**About evidence for the console.** Postman reported developers 1.7x to 56x faster with a ready-to-run collection. Its Moneris case study claims about 10x faster time-to-first-call and 225% more registrations. Both are vendor-produced and bundle the console with better onboarding generally. Do not quote them to leadership as expected results. Measure your own time-to-first-call before and after. The practitioner target is under 10 minutes.

### Week 12-13: Stage 5, institutionalize

- Every API-changing PR carries its spec change, and the docs follow from it. Add this to PR review.
- Put documentation expectations into the engineering ladder. Stripe does this.
- Schedule a quarterly re-audit against support tickets and docs-search queries.
- **Escalation trigger:** persistent "inconsistent docs" complaints or "dig through source" behavior means a dedicated docs owner and stricter gates, not another audit pass.

## Gates and what "done" means

| Gate | Threshold | In scope? |
| --- | --- | --- |
| Census coverage | 100%: every operation, parameter, response (at least one 4xx each), error code with cause and fix; zero documented-but-removed endpoints | Yes |
| Lint | Zero errors at the chosen ruleset | Yes |
| Contract tests | Zero violations | Yes, because staging exists |
| Snippet parity | 100% of operations × 3 languages | Yes, at the full-migration tier |

The 100% census gates are this audit's own definition of done, not a published benchmark. The integrator who hits the one undocumented endpoint gets no partial credit.

Track these trends but never gate on them:

- time-to-first-call, before and after
- share of support tickets caused by missing or wrong reference content
- docs-search queries that return no result

## Benchmark: Stripe and Twilio

Compare against their mechanisms, not their reputation.

| Mechanism | Stripe or Twilio | Hexavolt today | Closed by |
| --- | --- | --- | --- |
| Reference generated from the spec | Stripe | No, hand-edited | Stage 1 |
| Live test keys embedded in samples | Stripe | No | Stage 4 |
| Typed resource-ID prefixes | Stripe | Unknown | Stage 4, with the API team |
| Docs quality in engineering ladders | Stripe | Unknown | Stage 5 |
| Per-endpoint error tables | Twilio | Unknown, probably partial | Audit row 7, then lint |
| CI-tested snippet repo | Twilio | No, translated curl | Stage 4 |

## Risks

- **Scope pressure.** Leadership will ask for the console in week 2. The answer is that the console on a lying spec ships wrong examples to prospects, and the gates are what keep it right.
- **First contract run is noisy.** Budget a week for fixes, since 5 to 15 findings is normal.
- **Staging exposure.** A public console against staging needs rate limits, key scoping and data reset.
- **Platform choice stalls stage 1.** Decide it in week 2, using the census numbers. Do not run a long evaluation.

## Deliverables by week

| Week | Deliverable |
| --- | --- |
| 2 | Census, audit report, platform decision |
| 5 | OpenAPI 3.x spec as the single source; reference renders from it |
| 6 | Lint gate failing CI |
| 8 | Contract tests and breaking-change diff failing CI |
| 12 | SDK-based samples for all operations in all 3 languages; try-it console live on staging |
| 13 | PR-review rule, ladder language, first time-to-first-call measurement, quarterly re-audit scheduled |