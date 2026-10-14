# Ledgerwell SDK portfolio: which languages, in what order

I followed the `sdk-portfolio-strategy` skill and its three reference files. The skill wants a one-question-at-a-time interview, but you asked for the full answer in one go. So I filled the gaps with assumptions, listed at the end, and the whole thing is a draft until you approve each section.

## Answer

**Build Java and .NET (C#) as official SDKs, in that order unless your account split says otherwise. Do not build nine official SDKs this year. Python, JavaScript and C++ don't make the cut on the data you have.**

| Order | Language | Tier | Why |
|---|---|---|---|
| 1 | Java | Official | Your confirmed audience. |
| 2 | .NET (C#) | Official | Your confirmed audience. |
| Conditional | Ruby | Community tier, with a promotion gate | About 2 of 40 customers (~5%), below the add threshold. |
| Conditional | Go | Not built | Fintech platforms add it (Plaid, Stripe), but none of your 40 customers uses it. |
| Not now | Python, JavaScript/TypeScript | Spec-driven self-service | Popular, but absent from your customer base. |
| Not now | C++ | Declined, written down | No evidence of demand. |

If Java and .NET are close to evenly split, ship whichever has the larger pipeline or open deals first. If you can't tell, ask sales which language shows up in the next quarter's deals.

## Why the TIOBE and Stack Overflow order is the wrong input

- **Documented practice.** Every documented case maps the buyer's stack first. Plaid has five official libraries (Ruby, Node, Python, Java, Go). Stripe, Twilio and OpenAI/Anthropic also map their buyers' stacks. None of them names TIOBE, Stack Overflow or Octoverse as a decision input.
- **Your vertical.** Fintech and enterprise platforms front-load Java, C#, Ruby and Go. The Python-and-JavaScript-first order is the AI and dev-tools pattern, and that isn't your buyer.
- **Your data.** You have 40 integrated customers who told you their languages. Build for those 40 before you build for a survey of all developers.
- **Going the other way.** A popularity-first order means shipping Python and JavaScript for customers who don't use them, while the Java and .NET shops stay on curl.

ℹ️ Python is the one popularity-chart pick I'd keep an eye on. "Enterprise finance teams" often script reconciliation in Python. Your 40 customers don't show it, so don't build it on a guess. Put it on the telemetry watch list (below).

## The VP's "nine languages"

Nine official SDKs by year-end isn't a good commitment, and "official" is the problem word. In this skill, official means a support commitment, not a build method. Plaid's five official SDKs are generated. Every official language is a standing review, release and support obligation, with a vendor-estimated cost of multiple engineer-years if handwritten. About 11 weeks remain, and your confirmed demand covers two languages.

I'd bring the VP three candidate portfolios:

- **A. Lean core plus self-service tail (recommended).**
  - Two official SDKs, Java and .NET.
  - You publish the OpenAPI spec and point everyone else at generators. Plaid does this: 5 official libraries, 40+ languages via the spec.
  - The result is a polished, supported SDK for 100% of current customers except the Ruby couple.
- **B. Broad coverage on a generator.**
  - Six to ten languages from one pipeline.
  - This gets you to nine, but at the price of a large standing review and support load, for languages with no customers.
  - If the VP insists on the number, use my own synthesis, not a published pattern: label two languages official and the rest "generated, community-tier preview" with a non-guarantee. Don't call them official.
- **C. Handwritten flagship plus generated rest.**
  - You handwrite one language and generate the rest.
  - It only pays off when one language carries most of the revenue traffic, and you haven't told me that's true.

**A is the recommendation.** Its pitch to the VP: every customer you have gets an official SDK, the rest of the world gets the spec, and each added language has to earn its place with traffic or deal requests.

## Draft strategy, by workflow step

All seven steps are drafts. Per the skill, none is final until you approve it.

**1. Surface decision.** I assume SDKs were already chosen as an integration surface for your integrating developers. You said you're "finally doing real client libraries". If that decision was never made explicitly, run `api-integration-surface-strategy` first.

**2. Language order.**
- **Official:** Java, then .NET.
- **Ruby:** community tier, with the promotion gate in step 3.
- **Add-a-language threshold:** a sustained double-digit share of API traffic, or repeated named enterprise-deal requests for that language. This is self-set. No vendor publishes a numeric threshold.
- **What the threshold means for you:** at 40 customers, double-digit is about 4 or more accounts. Ruby is at about 2.
- **Telemetry:** add client `User-Agent` or SDK headers now, so the data confirms this mapping.

**3. Tiers and promotion gate.** Use the two-tier shape (Stripe, Twilio and Plaid use it):
- **Official** carries a support commitment.
- **Community** carries an explicit non-guarantee, and support requests route to the community repo.
- Encode quality in the package version and metadata, not only a docs page. For example, GA means 1.0 or higher.
- Promotion gate, labeled as inferred synthesis. Only one promotion is cleanly documented, Anthropic's Ruby SDK, where it turned on a namespace transfer. A community SDK becomes official when all four hold:
  - sustained usage;
  - feature completeness (auth, pagination, retries);
  - the maintainer cooperates on the package name;
  - you commit to supporting it.

**4. Build model.**
- **Default:** a commercial generator driven by the OpenAPI spec, if the spec is a real source of truth.
- **Banks may force a step down.** If your customers' security teams or your procurement need self-hosted or air-gapped generation, the hosted rung is deleted. Then the choices are Speakeasy or the free OpenAPI Generator.
- **The free generator is credible for you.** Plaid generates its official Java SDK with it. Budget curation time, because its Java output is widely described as non-idiomatic.
- **Vendor risk.** Re-check any vendor's status before signing:
  - Stainless was acquired by Anthropic (May 2026) and its hosted generator was wound down.
  - Fern was acquired by Postman (January 2026).
- **Guardrails:** the OpenAPI spec, not a vendor DSL, is the source of truth; prefer a self-hostable generator; write an exit plan into the decision record before signing.
- **Spec first:** if the spec drifts from the API, fixing it is week one, because every generated option depends on it.

**5. Three versioning policies (never merged).**
- **SDK package:** SemVer per package. A major bump happens only when the SDK's own surface breaks, never merely because the API shipped a new version.
- **API version:** owned by `api-versioning-policy`. Record the scheme here and pin the boundary.
- **Runtime support window:** tie it to upstream Java and .NET lifecycles plus a stated grace window.
- **Mapping table:** publish a table from SDK major version to supported API versions, as Stripe and AWS do.
- **Cadence:** with generated SDKs, release on change. A fixed monthly train fits handwritten ones. Cadence is a predictability promise, not a productivity metric.
- **Bank runtimes (my judgment, not from the skill):** bank customers often run older Java versions and .NET Framework. Confirm which runtimes your 40 customers actually use before you set the window.

**6. EOL playbook.** Adopt Sentry's evidence-gated shape. Build the case first, including the revenue at risk from accounts using only that SDK. Then cut the final release, announce, archive, and clean up 6-12 months later. Observed announcement-to-archive windows run 6-24 months. Azure's floor is 12 months of critical fixes after deprecation.

**7. Community policy.**
- List community SDKs with a non-guarantee, in Twilio's wording: "not supported by [Ledgerwell], and we can't speak to their accuracy/completeness".
- Support requests route to their repo.
- When a community SDK's language crosses the threshold, invoke the step 3 promotion gate instead of building a competitor.
- Ruby is the first test case.

## Assumptions to confirm

1. **Spec state.** Is your OpenAPI spec a linted source of truth in CI, drifting, or nonexistent? This gates every generator option.
2. **Self-hosting.** Can procurement and security accept a hosted generator, or is self-hosted generation a hard requirement for a bank-facing vendor?
3. **In-house skills.** Which languages can your team review idiomatically and maintain for years? Java and .NET fluency makes those two nearly free.
4. **Account split.** How many of the 40 are Java versus .NET, and does one carry most of the revenue traffic? That decides option C and the Java/.NET order.
5. **Telemetry.** Do you have per-language traffic data today? If not, plan to instrument it.
6. **Deadline.** Is there a deal or launch date that promotes one language ahead of this order?
7. **Policy or catch-up.** Is this a one-off catch-up, or a portfolio policy the team will run for years? A policy mandate would promote the tier, threshold and EOL work above shipping one more SDK.
8. **Effort ceiling.** What are your engineer-hours, and how much standing maintenance per extra language are you willing to take on?

## Next step

Tell me which candidate shape you pick (A, B, C or a blend), and answer questions 1, 2 and 4. I'll validate the sections one at a time. The skill also expects me to record the approved language order, build model, tier policy, versioning split and EOL thresholds in `developer-platform-context.md`, once you've approved them.