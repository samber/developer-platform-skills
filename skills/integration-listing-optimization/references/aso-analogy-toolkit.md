# Mobile-ASO analogy toolkit

Audit rubrics and gallery-ordering frameworks from consumer mobile app stores (Apple App Store, Google Play) transfer structurally to B2B integration marketplaces, but the benchmark numbers do not. B2B listing traffic is orders of magnitude lower and the buyer is deliberate rather than impulse-browsing, so no figure below is verified to hold at the same magnitude on AppExchange, HubSpot, Atlassian, Shopify, or Slack. Use the frameworks; quote the numbers only as "in consumer app stores, X - direction likely, magnitude unverified here."

## Converged audit dimensions

Two unrelated authors independently arrived at near-identical weighted audit rubrics: one six-way, one ten-way splitting the same factors finer and adding Keyword Rankings as its own dimension.

| Dimension            | Six-way weight | Ten-way treatment  |
| -------------------- | -------------- | ------------------ |
| Title & Subtitle     | 20%            | split finer        |
| Description          | 15%            | split finer        |
| Visual Assets        | 25%            | split finer        |
| Ratings & Reviews    | 20%            | split finer        |
| Metadata & Freshness | 10%            | split finer        |
| Conversion Signals   | 10%            | split finer        |
| Keyword Rankings     | not separate   | own dimension, 10% |

The convergence, not either weighting, is the finding. Any listing audit should score:

- Title text.
- Description.
- Visual assets.
- Ratings and reviews.
- Keyword and category placement.
- Freshness.
- Conversion signals.

Track **keyword coverage** (terms present in indexed fields) separately from **keyword performance** (whether the listing actually ranks for them). Visual assets plus ratings carry the most combined weight in both rubrics; text metadata alone is a minority of either score.

Data-collection pattern worth copying:

1. Try live listing data first: fetch the public listing page, and capture images rather than relying on screenshot captions, which are usually not text-extractable.
2. Fall back to asking the user to paste their current listing fields.

For a marketplace-generic skill with no API, the fallback is the default path.

## Brand-maturity tiering

Classify the listing before scoring it: **Dominant / Established / Challenger**. A deviation from textbook optimization - brand-only title, no keyword-first strategy, no demo video - is a legitimate deliberate choice for a market leader whose buyers search its name, and a real gap for an unknown entrant. Rule of thumb: before docking points, ask whether this is a mistake or a deliberate choice by a team that has data you don't.

This transfers directly: an established SaaS's marketplace listing can lean on brand recognition in ways a new entrant's cannot, so the same checklist scores them differently. It also interacts with title convention, since at least one B2B marketplace instructs brand-first titles for everyone.

## Gallery ordering: the first-3 rule

Consumer data (two independent sources):

- Roughly 80-90% of store visitors never see past the third screenshot.
- Average scroll rate ~17%.
- The decision takes 6-10 seconds.

The ordering framework this justifies transfers to any marketplace listing with an ordered gallery:

| Position | Content                         | Purpose                                                                                                                                                |
| -------- | ------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 1        | Hero - core value, best feature | Stop the scroll; say what the product does                                                                                                             |
| 2        | Key differentiator              | Why this one over competitors                                                                                                                          |
| 3        | Most-used / most-loved feature  | What users actually value                                                                                                                              |
| 4        | Social proof or outcome         | Ratings, results, testimonials - where the marketplace's rules allow them in images; several B2B marketplaces ban review claims baked into screenshots |
| 5+       | Supporting features             | Settings, integrations, edge cases                                                                                                                     |

Optimal consumer count: 4-6 images - more produced decision paralysis, not conversion.

## Conversion benchmarks (consumer-only numbers)

- **Ratings**:
  - 3.0 → 4.0 stars: +89% conversion.
  - 4.0 → 4.5 stars: +20-30% conversion.
  - A 0.4-star gap vs a competitor: ~25% lost installs from the same search.
  - 4.0 is a hard floor for featuring; below 3.5, visibility drops sharply.
  - 79% of users check ratings before installing.

  The strongest reusable _direction_: rating improvements compound into conversion, so review work is never cosmetic.

- **Screenshots**: well-designed sets lifted conversion 20-35%; A/B winners typically +10-25%.
- **Preview video**: +20-40% on the platform that autoplays it, while only ~6% of visitors tapped play on the platform that doesn't - the evidence behind "demo video is platform-gated, not universal." Check how prominently the target B2B marketplace surfaces video before investing in one.

## A/B significance thresholds

A generic before/after rule reusable on any marketplace with funnel data, at whatever traffic volume - but note B2B listing traffic is low, so reaching significance takes proportionally longer:

- Lift >10%: strong winner, apply immediately.
- 5-10%: meaningful.
- 2-5%: marginal.
- <2%: noise - do not act on it.
