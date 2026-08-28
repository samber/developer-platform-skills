# Versioning case studies

Named, dated, citable examples - the conservative platforms whose mechanics are worth copying, and the cautionary tales whose failure was process, not scheme. Sourced from each platform's own documentation, engineering blogs, and contemporaneous reporting.

## Stripe: date-based, account-pinned versioning

The highest-engineering-investment point on the scheme spectrum, and the named case study for it.

- **Account pinning:** an account's first-ever API request locks it to the version current at that moment, forever, unless it explicitly opts into a newer date. New accounts always start latest; existing integrations never move unless they choose to.
- **Version every breaking change, ship continuously:** no periodic big-bang releases - a new version is cut whenever a backwards-incompatible change ships, each stamped with its date. The current documented cadence: monthly releases containing only backward-compatible changes, plus a twice-yearly _named_ release (e.g. `2024-09-30.acacia`) opening a new breaking generation - the name is a human discoverability aid on top of the date identity.
- **Gates and transformers (per third-party analysis of the public design):**
  - A gate at the request boundary strips parameters the caller's pinned version can't send.
  - The engine computes every response against the single latest schema.
  - A descending chain of transformers, one module per historical breaking change, downgrades the response step by step until it matches the pinned version.
  - Engineers maintain only the current code path plus the transformer chain.
- **The proof point:** "To date, we've maintained compatibility with every version of our API since the company's inception in 2011" (Stripe engineering blog).
- **Brandur Leach's framing (stripe.com/blog/api-versioning, 2017):** "When it comes to APIs, change isn't popular. While software developers are used to iterating quickly and often, API developers lose that flexibility as soon as even one user starts consuming their interface."
- **The trade-off to state plainly:** callers get effectively permanent compatibility; Stripe carries an ever-growing transformer chain forever. Weigh against actual surface size and change frequency - never adopt reflexively because Stripe does it.
- **The SDK split (the citable illustration that contract and library versioning are separate policies):** Stripe's client SDKs use conventional SemVer; the date scheme applies only to the wire contract. The SDK's major-bump trigger - "to add a required parameter, change a type, property, method, or parameter" - is materially stricter than the API-version rule, because a library's compiled surface breaks in ways a tolerant HTTP caller doesn't.

## Conservative platforms

- **Shopify.**
  - Quarterly `YYYY-MM` versions released "every three months at the beginning of the quarter, at 5pm UTC" - a citable cadence down to the release time.
  - ≥12 months' support per version, ≥9 months' overlap between consecutive versions. The actual retirement schedule is published (version `2025-07` documented as accessible until July 16, 2026) - what "publish an actual sunset date" looks like in practice.
  - Retired versions **fall forward** to the oldest still-accessible version.
  - Shopify carves out unversioned surfaces that "may change at any time" - a policy only has to cover what the provider has chosen to version, as long as that boundary is stated up front.
  - Its GraphQL Admin API uses the same date scheme as REST: one unified versioning story across paradigms.
- **LinkedIn.** Monthly `YYYYMM` versions in the `LinkedIn-Version` header (since June 2022), each supported "a minimum of one (1) year." The sharpest counter-design to Stripe's sticky pinning: an omitted or deprecated version header returns an error - the latest version is never applied by default, so nothing drifts silently. Its "Breaking Change Exceptions" clause - the right to patch any version "for any critical security, privacy issues, or bug fixes" - is the standard shape of the security escape hatch.
- **AWS.** Date-based per-service API versions (S3 = `2006-03-01`), but the distinguishing behavior is near-total **non-retirement**: wire versions almost never die; SDKs abstract version selection, and AWS recommends locking the API version in production code. Breaking changes surface one layer up, at SDK major-version boundaries. Caveat: this stability comes from a hyperscaler's willingness to carry old code paths indefinitely - likely costlier for a small team than Stripe-style transformers.
- **Azure / Microsoft Graph.** `?api-version=YYYY-MM-DD` with `-preview` suffixes, governed by the Breaking Change Review Board. Graph specifically: ≥24 months' notice, only `v1.0` and `beta` live concurrently, and the SDK's previous major stays supported "for 12 months from the release date of the latest major version, for security fixes only" - a concrete number for the client-library half of the policy.
- **Google Maps Platform.** "Typically 12 months" of deprecation. JavaScript API v2 was fully turned off May 26, 2021, forcing remaining integrations to v3; IE11 support ended as two distinct dated events (banner warning August 2021, discontinuation November 2022) - "announce, then wait, then remove" done as separate milestones. A documented May 2026 removal wave (Heatmap Layer, Drawing Library, `DirectionsService`, `DistanceMatrixService`) shows a long notice period and a disruptive hard removal are not mutually exclusive.
- **PayPal / Braintree.** PayPal REST runs a three-tier current/previous/legacy posture (`/v1/`, `/v2/`, SOAP/NVP legacy-but-supported) rather than strict two-version. Braintree publishes per-major SDK support status and deprecation dates directly in each SDK's README - a deprecation schedule with no dedicated changelog site - and publishes consumer-side cadence guidance: update client SDKs at least yearly, server SDKs at least every two years.
- **The cross-cutting pattern:** every conservative platform pairs its notice window with a graceful-degradation behavior or a clearly-scoped exception (Shopify's fall-forward and unversioned carve-out, LinkedIn's security clause, AWS's non-retirement, Braintree's legacy tier). The long window alone is never the whole policy.

## Cautionary tales

Each failure below is a _process_ gap, not a scheme gap - all three run path versioning, and the scheme was never the point of failure.

- **Meta Graph API - aggressive but documented, and still the fall-forward cautionary tale.**
  - The 2-year guarantee dates to f8 2014, where Mark Zuckerberg reframed "Move Fast And Break Things" into "Move Fast With Stable Infra" - a public, deliberate velocity-for-stability trade.
  - The clock starts at the _next_ version's release: Meta's own worked example is v2.3, released March 2015, expired August 2017, two years after v2.4 shipped.
  - The dangerous part: expired-version calls silently fall forward. "Meta does not return an error. It quietly reroutes your calls to an older, still-usable version, and your app keeps running while its behaviour changes underneath you."
  - Well-documented, yet it still generates persistent complaints about code rot and forced quarterly regression testing: documented ≠ noticed.
  - Meta's own Marketing API hard-fails expired calls on a ~90-day window: one company, two enforcement styles, justified by consumer sophistication.
- **Discord - governance friction from an inconsistent default.**
  - Version v6 was simultaneously the default and deprecated for about 1.5 years; on April 30, 2022 the default jumped straight to v10, skipping v7-v9. Developer reaction: the jump "just seems kind of abrupt for people who have relied on the default."
  - A deprecated-yet-default version is a breaking-change-adjacent event before anything is removed.
  - Discord's historical unversioned access drew the direct criticism worth quoting: "APIs should not allow unversioned access to avoid issues with changing defaults."
- **Twitter/X - the business-motivated breaking change with no process.** February 2, 2023: "Starting February 9, we will no longer support free access to the Twitter API, both v2 and v1.1" - ~7 days' notice, two orders of magnitude off every benchmark. It broke integrators who were willing to pay (Echobox reported its access "cut off without notice"), and the structural cause was named in contemporaneous reporting: developer relations had been laid off, so no one was left to execute a communication plan. Cite it when arguing that governance and notice discipline matter _most_ when the motive is monetization rather than engineering - that is exactly when skipping the process is most tempting.
