**Next action:** Fix the spec before anything else. Today it can't drive any build model, handwritten or generated.

**Status:** This is a draft strategy, 7 of 7 sections written, 0 of 7 approved by you. I couldn't run the skill's one-question-at-a-time interview, so the assumptions I made are listed at the end. Please confirm or correct them.

## Verdict

1. **Generate all five SDKs from your OpenAPI spec with a self-hosted generator.** Add a thin hand-curated layer in the one or two languages that carry the most traffic.
2. **Drop "official means handwritten".** Official is a support commitment. It is not a build method. Plaid's five official SDKs (Ruby, Node, Python, Java, Go) come from the free OpenAPI Generator.
3. **Five handwritten SDKs with 4 engineers is the losing option.** Vendors estimate hand-maintaining many languages at multiple engineer-years of standing cost. That estimate is vendor-sourced, so treat it as order of magnitude. Speakeasy describes the usual end state as "SDKs with divergent behavior" across languages.
4. **Your security rule removes hosted generators.** Stainless (Anthropic wound down its hosted product in 2026) and Fern (now Postman) are out. That also protects you from their lock-in risk.
5. **Your worry is partly right.** Free-generator output is widely described as technically correct but non-idiomatic. The fix is custom templates, a curated ergonomics layer, and a review gate. It is not handwriting everything.

## Candidate portfolios

| Shape | Fit for you |
|---|---|
| A. Lean core (2–3 official) + spec for self-service | Cheapest. Contradicts your plan to ship all five. Right if telemetry shows 2 languages dominate. |
| B. Five generated, one pipeline | Fits 4 engineers. Output quality depends on template effort. |
| **C. Handwritten flagship + generated rest** | **Recommended.** Hand-polish only the top-traffic language. |

Choose the flagship from telemetry, not from taste. Don't start wave 2 until the telemetry is in.

## The strategy, by section

### 0. Precondition: repair the spec (2–4 weeks, my estimate)

1. Lint the spec with Spectral, run in your network.
2. Run contract tests of the spec against a staging copy of the real API. Schemathesis is one self-hostable option. Triage every mismatch.
3. Add a CI gate: spec lint and contract tests must pass before any SDK build.
4. Make the spec, not a generator config, the single source of truth. If your framework can emit OpenAPI from code, consider that.

Generating from a drifting spec ships the drift into five languages at once.

### 1. Surface decision

I assume the SDK surface is already chosen for your 1,200 API customers. If it isn't, stop and settle that first (`api-integration-surface-strategy`).

### 2. Language order

- **Start now:** add SDK or `User-Agent` headers to API traffic and log per-language share. Collect for 4–6 weeks.
- **Provisional order, until data arrives:** logistics integrators are enterprise backend. Expect Java, Python, Node, PHP and Go in that rough range. This is a guess. Replace it with your own numbers.
- **Add-a-language threshold (self-set, not an industry standard):** a sustained double-digit traffic share, or repeated enterprise-deal requests naming the language.
- **Wave 1:** the top 2–3 languages by traffic. **Wave 2:** the rest.
- **PHP:** it is the likeliest to fall below threshold. If it does, make it community tier plus spec. Don't build it just because it was on the list.

### 3. Tiers and promotion gate

- **Two tiers:** official (with a support commitment) and community (with an explicit non-guarantee, support routed to their repo).
- **Quality signal:** use version numbers and package metadata. Keep `0.x` or beta until the SDK meets the GA checklist below, then go to 1.0.
- **Official GA checklist (my synthesis, not a published standard):**
  - Auth, pagination, retries and typed errors all work.
  - CI runs against a fake API.
  - Docs have snippets.
  - A named owner exists.
- **Promotion gate for a community SDK:**
  - Sustained usage.
  - Feature completeness.
  - Maintainer agrees to transfer the package name.
  - Your support commitment.
  - The only documented promotion is Anthropic's Ruby SDK, which turned on namespace donation.

### 4. Build model

- **Rung:** free OpenAPI Generator, self-hosted. Your hard rule deletes the hosted rung.
- **Speakeasy** was self-hostable and air-gapped at the last snapshot. Re-verify that with the vendor. Also ask whether its licensing makes any call-home. That would break your rule.
- **Curation budget:** custom templates per language, an idiomatic-review checklist, and a blind review by an engineer who lives in that language.
- **Pilot first:** generate one language and have a native engineer judge it against your "machine barfed" bar. If it fails after template work, make that language the handwritten flagship. Move one language, not all five.
- **Exit plan, in the decision record:** the spec is the source of truth, the generator is pinned and mirrored internally, and templates live in your repo.
- **Snippet parity:** the docs snippets come from the same pipeline (`x-codeSamples` or a CI-tested snippet repo). Assign an owner.
- **Check with security:** "no external SaaS" may also cover pulling dependencies (Maven, npm, PyPI) and publishing to public registries. Use internal mirrors for pulls. Get an explicit ruling on publishing, because customers need public packages.

### 5. Three versioning policies (never merge)

1. **SDK version:** SemVer per package. Bump the major only when the SDK's own surface breaks.
2. **API version:** owned by `api-versioning-policy`. Record the scheme and the boundary here.
3. **Runtime support window:** follow upstream language lifecycles plus a stated grace window. Example: supported LTS Node versions, the latest Go versions. Set the numbers per language.

Publish a mapping table from SDK major to supported API version(s).

- **Cadence:** release on change. A generated portfolio releases naturally that way.
- **Don't** release just to hit a calendar.

### 6. Deprecation and EOL playbook

Follow Sentry's evidence-gated shape.

1. **Build the case first.** Use registry trends, usage, and revenue at risk from accounts using only that SDK. Refresh the exclusive-usage count before any EOL talk.
2. **Execute in order:** final release, then announcement, then archive. The announcement is a pinned issue naming the successor and the timeline, with a README banner and a registry deprecation marker.
3. **Clean up 6–12 months after archive.** De-index the old docs but keep them reachable, and redirect to the successor.

Announcement-to-archive floors seen across vendors run 6–24 months. Azure's floor is 12 months of critical fixes. AWS's maintenance windows differ by document: 12 months in the core SDK policy, 6 in Powertools. Pick your number and write it down.

### 7. Community policy

- List community SDKs with a disclaimer, in the Twilio and Plaid style.
- Route support to their repos.
- Publish the spec so anyone can generate their own client.
- Revisit the list when a language crosses the step-2 threshold.

## Plan and effort

1. Telemetry headers: 1–2 days.
2. Spec repair plus CI gates: 2–4 weeks.
3. Generator pilot in one language, with templates and native review: 2–3 weeks.
4. Wave 1: roughly 4–6 weeks after the pilot passes. Wave 2 follows.

These are rough estimates for a 4-person team. Pace them against your real deadline.

## Assumptions to confirm

1. **Vertical:** I assumed enterprise backend / mixed.
2. **Existing SDKs:** I assumed none official, and possibly some community ones.
3. **Telemetry:** I assumed you have none today.
4. **In-house fluency:** unknown. If your team is strong in two of the five languages, those become cheap flagships.
5. **Deadline and effort ceiling:** unknown. A hard deadline favors generating all five now.
6. **Registry publishing:** not yet ruled on by security.

**Next:** which languages does your team write fluently, and is there a launch or deal deadline? Those two answers re-rank the wave order.