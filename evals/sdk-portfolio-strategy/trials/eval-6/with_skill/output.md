# Orbital Grid SDK portfolio: tier definitions and promotion policy (draft)

I couldn't run the skill's one-question-at-a-time interview or the section-by-section approval, so this is a full draft. Everything marked **[self-set]** or **[inferred]** is our own choice, not a published industry standard. Section 8 lists the inputs that would change it.

## 1. Recommendation up front

- **Write and approve the gate before anyone promises the crate to the CTO.** The gate is policy for the whole portfolio. The `orbital-grid` crate is its first test case, not its author.
- **Promote in two steps: Community → Official Preview → Official GA.** Next quarter's realistic outcome is Official Preview, provided the maintainer agrees. Preview carries a lighter commitment and keeps the decision reversible.
- **"Better than what we'd write" is a quality argument, not a demand argument.** Demand evidence comes from API traffic by client language and from named deal requests (section 4, gate 1).
- **Official means a support commitment, not a build method.** A crate written by an outside developer can be official. Plaid's five official SDKs are generated, and the Anthropic Ruby SDK took over a community gem's name. The Anthropic Ruby case is the only clean community-to-official promotion on record. It turned on the maintainer donating the package name and cooperating, not on a vendor decision alone.

## 2. Tier definitions

| Tier | Languages today | What we commit to | What we don't |
|---|---|---|---|
| **Official GA** | Python, Go, Java | Tracks every API release, security fixes within the stated window, bug triage, docs and snippet parity, the runtime support window (section 6), EOL notice per section 7 | New-feature parity on day one of an API preview |
| **Official Preview** | none (Rust would enter here) | Security fixes, issue triage, named owner. Breaking changes allowed with notice. Version `0.x`. | Production-grade stability, any EOL window |
| **Community-listed** | any language | Listing on our SDK page with a disclaimer, spec access | Support, accuracy, completeness, updates. Requests route to the SDK's own repo. |
| **Spec-only (self-service)** | everything else | A published, linted OpenAPI spec | Anything about generated clients |

Notes:

- **Two-tier plus Preview, not full numbered tiers.** Numbered tiers (MCP-style) only pay off when "official" stops discriminating. Revisit above roughly 6 official SDKs **[self-set]**.
- **Encode the tier where users look, not only on a docs page:**
  - GA means version ≥1.0 and a README banner.
  - Preview means `0.x` and a README banner.
  - Community SDKs must not use our name in a way that implies official status.
  - Google Cloud does this with version ≥1.0 plus a PyPI classifier. Cargo has no equivalent classifier, so version plus README is the mechanism.
- **State the Preview policy explicitly.** Google's Alpha/Preview libraries can be deleted before reaching GA. Ours must say which model it follows. I propose: Preview gets at least 90 days, then promotes or sunsets with 90 days' notice **[self-set]**.

## 3. Promotion path

1. **Community-listed → Official Preview** requires gates 1–6 (section 4) and a written decision record.
2. **Preview → GA** requires:
   - At least 1 month in Preview (borrowed from Azure's beta gate).
   - No known critical bugs.
   - Three reference customers external to Orbital Grid (also Azure's beta gate).
   - Passing the full gate, including the runtime window and API mapping table.
3. **Cadence:** gate reviews run on a fixed calendar, quarterly **[self-set]**, not on request. This stops any individual deal or executive from creating a one-off exception.
4. **Demotion** uses the same gate in reverse and the EOL playbook (section 7). Official is not forever.

## 4. The promotion gate

The rubric is **[inferred]** synthesis. Only the community-status checks (part of gate 3) and the beta checks (part of step 2) come from published policies, Looker's and Azure's respectively. Every gate is checkable and has a named evidence source.

| # | Gate | Passing evidence |
|---|---|---|
| 1 | **Demand.** A sustained double-digit share of API traffic in that language, or repeated named deal requests **[self-set]**. | Client-language telemetry via `User-Agent` or SDK header, and CRM deal notes. Crates.io downloads alone do not count: they include CI re-downloads and don't show API usage. |
| 2 | **Completeness.** Auth, pagination, retries, timeouts, typed errors, and 100% of the public spec's operations or a documented exclusion list. | Spec-coverage diff, run in CI |
| 3 | **Support infrastructure.** Automated tests, packaging, docs, and examples. Not built on a deprecated technology. Tested by enough distinct users. | These are Looker's reasons for staying community. CI link, docs link, user count from telemetry. |
| 4 | **Maintainer cooperation and namespace.** A written agreement covering the points below. | Signed agreement |
| 5 | **Capacity.** At least 2 people able to ship a release (a bus-factor floor), and one in-house engineer who can review idiomatic code for the next few years. | Named owners |
| 6 | **Security and licence.** A licence compatible with our distribution, a vulnerability-disclosure channel, a dependency audit, and 2FA or trusted publishing on the registry account. | Audit report |

Gate 4 for the crate covers these points:

- **Crate name.** The crate is already `orbital-grid`, so no rename is needed. Crates.io allows co-owners and teams, so we can add an org owner rather than demand a transfer.
- **Repository.** Decide whether to transfer it, fork it, or keep it in place under an agreement.
- **Licence and contributors.** Check the licence and the contributor history for relicensing risk.
- **Trademark.** The crate uses our company name. Confirm the trademark position before we put an "official" badge on it.
- **Credit and compensation.** Credit the maintainer in the README, as the Anthropic Ruby README does. Decide whether the maintainer is paid, sponsored, or hired. This is a business decision that needs your input.
- **Maintainer's right to say no.** A maintainer may decline, and the policy must not assume yes.

## 5. Build-model exception

The portfolio default is a single build model with at most one flagship exception. An adopted handwritten crate is an exception by definition.

- **Allowed exception:** record it as one, with the reason ("maintained by an external contributor, adopted under agreement").
- **Exit plan:** write it before signing. If the maintainer leaves, we either fork and maintain, or deprecate per section 7.
- **Consistency check:** Rust's API types should come from or be diffed against the OpenAPI spec, so the crate cannot drift from the API.

## 6. Versioning (three separate policies)

1. **SDK package version:** SemVer per package. A major bump only when the SDK's own surface breaks, never because the API shipped a new version.
2. **API version:** owned by the API versioning policy. This document only records the boundary.
3. **Runtime support window.** Rust needs an explicit MSRV (minimum supported Rust version) policy. For example, the last 4 stable releases, tied to upstream release cadence **[self-set]**. State the equivalent for Python, Go, and Java in the same table.

Publish a mapping table from SDK major version to supported API version(s). Stripe and AWS both maintain this artifact. Release cadence: pick one of the two documented models, a fixed monthly train (Azure) or on-change (AWS, Google), and state it. Don't publish releases just to hit a cadence.

## 7. EOL for any official SDK

Apply Sentry's evidence-gated shape:

1. **Build the case first:** platform health, registry trends, and revenue at risk from accounts that use that SDK exclusively.
2. **Execute in order:** final release → announcement → archive.
   - Pin a deprecation issue that names the why, the successor, and the timeline.
   - Add registry deprecation markers and README banners.
   - Notify support and GTM.
3. **Clean up 6–12 months after archival.** Keep retired docs reachable but de-indexed, and redirect to the successor.

Timeline floors from published policies:

- AWS commits to at least 24 months of GA support and at least 6 months' maintenance notice. Its maintenance-phase length differs by document (12 months in the core SDK policy, 6 in the Powertools docs).
- Azure's floor is 12 months of critical fixes (3 years if breaking changes are involved).
- Observed announcement-to-archive range across vendors is 6–24 months.

Proposed for Orbital Grid **[self-set]**: 12 months minimum from announcement to archive for GA SDKs.

## 8. Community policy

- Community SDKs are welcomed and listed with this wording, adapted from Twilio: "not supported by Orbital Grid; we can't speak to their accuracy or completeness."
- Support requests route to the community repo, not our tickets.
- When a community SDK's language crosses the gate-1 threshold, invoke the gate rather than building a competitor from scratch.

## 9. Open inputs and risks

- **Rust demand is unproven.** The skill's language-order rule says official SDKs go only to languages that the vertical map and telemetry confirm. Industrial IoT and edge devices plausibly favour Rust **[inferred]**, but I haven't seen your telemetry. If Rust sits below the threshold, the CTO's request fits only as a strategic-vertical or named-deal exception. Record it as such rather than bending the threshold.
- **I haven't audited Python, Go, and Java against this table.** They may not meet GA today (spec coverage, runtime window, mapping table). Audit them before publishing the tiers, or the policy will be false on day one.
- **Questions for you:**
  1. What share of API traffic is Rust, and do you have client-language telemetry?
  2. Is a linted OpenAPI spec the source of truth in CI?
  3. Who in-house can review Rust long-term?
  4. Has anyone contacted the crate maintainer, and does the budget cover compensation?
  5. Is there a hard deal deadline behind "next quarter"?
- **Next step:** approve section by section. I'd start with the tier table and gates 1 and 4, because the maintainer conversation depends on them.