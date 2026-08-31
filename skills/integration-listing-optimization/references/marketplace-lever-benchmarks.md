# Five-marketplace lever benchmarks

Submitter-side comparison of Salesforce AppExchange, HubSpot App Marketplace, Atlassian Marketplace, Shopify App Store, and Slack Marketplace. All five platforms actively change listing rules (image-uniqueness rules, recategorizations, search-engine migrations) - verify current specs against official docs before acting on any guidance below.

## Ranking factors: confirmed vs inferred

| Marketplace            | Officially confirmed                                                                                                                                                                                                                                                                                                  | Practitioner-inferred                                                                                                                                                                                                                                                                                                                                                                                           |
| ---------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Atlassian              | Search runs on OpenSearch (replaced Algolia, 2026), relevance scored via NDCG; "more reviews and a higher rating improve your engagement score and search rank"; "rich media drives engagement and trial starts"; relevance prioritized over keyword matching alone. All verbatim from Atlassian's own rankings page. | Summary field (250-character cap) as the primary search-relevance string.                                                                                                                                                                                                                                                                                                                                       |
| Shopify                | "Built for Shopify apps appear higher in Shopify App Store search rankings" - the clearest official badge-ranking statement on any of the five.                                                                                                                                                                       | Name + subtitle ≈80% of keyword ranking weight (one tracker's estimate); install velocity over lifetime totals; listing view-to-install conversion; review recency weighted, especially the last 90 days ("50 reviews in 30 days outranks 500 static reviews"); uninstall rate feeding back negatively. Search drives ~60% of installs; one app reported +11.8% installs from changing only its featured image. |
| Salesforce AppExchange | Nothing on the search algorithm. The Trailblazer Score (a partner-health metric) is confirmed to influence "enhanced AppExchange visibility" - partner-level, not per-listing. Security Review is a listing gate, not a ranking factor: failing it delists.                                                           | Clean SEO title/description/categories/keywords drive indexing; media quality supports engagement and dwell; review volume/recency and install counts matter. The 2026 unified marketplace's intent-based search reportedly rewards outcome-oriented language - recent and still settling, treat as emerging.                                                                                                   |
| HubSpot                | Nothing.                                                                                                                                                                                                                                                                                                              | Install growth, ratings/reviews, certification status, content quality, internationalization - from third-party grader criteria and general practitioner guidance.                                                                                                                                                                                                                                              |
| Slack                  | Nothing published, and no analytics surface exists to reverse-engineer one from. Discoverability runs on editorial curation, categories, and the app's own external marketing.                                                                                                                                        | Nothing exists to infer from.                                                                                                                                                                                                                                                                                                                                                                                   |

## Native submitter analytics

| Marketplace            | What submitters get                                                                                                                                                                                                                                                                                                                      | How                                                                                   |
| ---------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------- |
| Shopify                | Fullest stack: partner-dashboard installs/uninstalls/net installs, ratings, revenue, API error rates; officially supported GA4 Measurement ID and Meta Pixel wiring that passes server-side install events, giving a complete listing-view → install-click → install funnel per shop. Largest third-party tracker ecosystem of the five. | Partner dashboard; Distribution → Manage listing → Tracking (must be wired manually). |
| Atlassian              | Richest native funnel: sales data, license report, evaluations/leads, marketing-funnel and evaluation insights (paid apps; up to 24h lag). Do not confuse with "Atlassian Analytics", a separate end-user BI product.                                                                                                                    | Manage Vendor screen, mirrored by the sales-report REST API.                          |
| Salesforce AppExchange | Free to any partner with an active listing: tile views, hovers, unique visitors, lead events, installs, by traffic source - plus top AppExchange search terms driving visits and installs. A separate post-install telemetry API serves churn/renewal work, not listing conversion.                                                      | Partner Community, Publishing → Analytics tab.                                        |
| HubSpot                | Active-install counts ("unique production accounts, unaffiliated with your organization, showing successful app activity within the past 30 days") plus customer feedback. No view→install funnel - a confirmed gap, not an extraction miss.                                                                                             | Developer account, Development → App Listings.                                        |
| Slack                  | Nothing. No views, installs, conversion, or search-term data for publishers; Slack itself monitors usage/uninstalls and contacts the developer. Self-build instead: your OAuth token store is the install ledger; subscribe to the `app_uninstalled` (and org-level uninstall) events for churn.                                         |

## Review mechanics and enforcement

All five ban incentivized reviews by agreement. Enforcement maturity diverges - Shopify is the only one with a published graduated-penalty schedule and documented mass takedowns.

- **Shopify**: policy states incentivizing reviews risks "removal of a portion of reviews, demotion or delisting of your app, or termination of your Partner account"; the ban covers incentives "through the app or external channels", and genuine reviews tied to untrusted reviewers can be unpublished collaterally. Sanctioned mechanics are prescribed:
  - In-product asks at natural moments that never block workflow.
  - Asks after positive support interactions.
  - Merchant opt-out.
  - Collection routed through the Reviews API.

  Email campaigns to active users convert at 5-10% **[corroborated practitioner report]**.

- **Atlassian**: solicitation is platform-driven. Customers are auto-invited 30 days after purchase, and a listing needs 10 reviews before a star rating displays. Publishers get a copyable review link and one public reply per review, and a reviewer must have the app installed or have uninstalled within 14 days.
- **Salesforce AppExchange**: actively coaches solicitation:
  - Target specific customers.
  - Time the ask to a success milestone.
  - Solicit even from evaluators.
  - Engage negative reviews publicly to get them amended.
  - Keep reviews fresh.

  The Trusted Reviews program badges reviews from high-credential community members, so reviewer credibility is weighted visibly. The incentive ban is explicit for consulting listings; the app-listing wording is thinner but the principle is contractual.

- **HubSpot**: reviewer attestation - reviewers confirm they are actual users, one review per app, no reviewing your own, your employer's, or a competitor's app. A dedicated ticket type exists for reporting violations, but no active solicitation mechanic is documented.
- **Slack**: no review or rating system exposed to submitters at all - no tactic to execute and no policy to violate.

## Listing field constraints submitters optimize within

The operator-side rulebooks converge on one skeleton - short hook string, benefit-led body, fixed-geometry gallery, capped video, capped categories, off-listing trust surfaces gating approval - but the specifics diverge, so never carry one marketplace's numbers to another:

- **Title convention**: Shopify instructs brand-first naming ("QTeck Announcement Bar", not "Announcement Bar QTeck") - the opposite of mobile keyword-first advice. Atlassian's 250-character summary is the load-bearing search string. Establish which fields the target marketplace indexes before writing.
- **Search terms [official, Shopify]**: up to five complete words, one concept per term ("email marketing" valid; "email marketing for leads" not).
- **Screenshot geometry**: no universal ratio exists.

  | Marketplace | Ratio                                 |
  | ----------- | ------------------------------------- |
  | Shopify     | 1600×900                              |
  | Atlassian   | 1840×900                              |
  | Slack       | 1600×1000                             |
  | Salesforce  | 700×467 (roughly 3:2)                 |
  | HubSpot     | content-correctness rules, not pixels |

  Shopify's 2026 image-uniqueness rule hard-rejects duplicate and logo-only images. Common content bans: browser chrome, sensitive data, pricing/review claims baked into images.

- **Video ceilings**:

  | Marketplace | Ceiling                                                                    |
  | ----------- | -------------------------------------------------------------------------- |
  | Atlassian   | ≤30 seconds, function demo only, anti-marketing tone                       |
  | Slack       | 30-90 seconds                                                              |
  | Shopify     | 2-3 minutes, promotional tone allowed, screencast capped at 25% of runtime |
  | AppExchange | 1-3 minutes                                                                |

- **Taxonomy caps**:

  | Marketplace | Caps                                                              |
  | ----------- | ----------------------------------------------------------------- |
  | Salesforce  | one category plus two industries (tightest)                       |
  | Atlassian   | two of ten, with a staleness downgrade to "uncategorized"         |
  | Shopify     | broader categories plus up to 25 structured features per category |
  | HubSpot     | operator-curated persona collections layered over self-selection  |

- **Freshness signals**: Atlassian downgrades category-stale apps, Slack names an unmaintained listing a removal-risk trigger, and Shopify treats update recency as a freshness signal. This is why the defend stage's 30-60 day refresh exists.

Exact character-limit tables for AppExchange's and HubSpot's long-form fields are not fully published anywhere - they surface only inside each platform's own listing builder. Read them there at submission time.

## Badges with confirmed effects

- **Built for Shopify** - the only badge on the five with a vendor-official ranking-boost statement. Highest-priority pursuit where eligible.
- **Atlassian Cloud Fortified / Runs on Atlassian** - enterprise-procurement trust; no quantified ranking lift published. **[official programs, unquantified effect]**
- **HubSpot Certified App** - search-filter and curated-collection eligibility; losable and re-appliable on a cooldown.
- **Salesforce** - Security Review is a gate, not a badge (failure delists); the Trailblazer Score is the visibility-adjacent lever.
- Generic "trust badges lift conversion 15-30%" figures originate in consumer e-commerce storefronts, not B2B app listings - never quote them at face value here.

## Practitioner ecosystem

Depth is uneven - deepest where the platform exposes data worth analyzing:

- **Salesforce AppExchange**: Invisory, AppX, Salesforce Ben, Beyond The Cloud, Synebo, Peeklogic; Salesforce's own Summit-tier listing consultation.
- **Shopify**: AppJubilee, Prys, Fusionmetrics, AppstorePulse, Big Moves Marketing - all grounded in Shopify-native signals.
- **Atlassian**: thin - aety.io, SaaSJet's Marketplace Reporter; Atlassian's own docs are the primary framework.
- **HubSpot**: thin - third-party listing graders and HubSpot Academy's certification course.
- **Slack**: none, because there is no data or review surface to build a discipline on.
- **Mobile-ASO firms** (Gummicube, Phiture, SplitMetrics and peers): consumer app-store specialists whose frameworks are frequently analogized to B2B marketplaces - treat any advice taken from them as analogy, however confidently it is stated.
