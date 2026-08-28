# Notice-period and concurrent-version benchmarks

Company-by-company published figures, the audience dimension that actually explains them, and how to cite them without over-promising. Sourced from each platform's own documentation and announcements.

## The benchmark table

| Company              | Scheme                    | Notice / support window                                                                                       | Concurrent versions                                       | Source posture                         |
| -------------------- | ------------------------- | ------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------- | -------------------------------------- |
| Google Cloud         | Path + per-service        | ≥12 months for GA services (ToS "Discontinuation of Services")                                                | Many                                                      | Formal ToS-backed policy               |
| Google Maps Platform | SDK/JS versions           | "Typically 12 months"                                                                                         | Quarterly JS channels                                     | Published deprecations page            |
| Microsoft Graph      | `/v1.0`, `/beta`          | "At least 24 months in advance of retiring it"                                                                | 2 (v1.0, beta)                                            | Microsoft Lifecycle Policy             |
| Azure                | `?api-version=YYYY-MM-DD` | Long deprecation + Breaking Change Review Board approval                                                      | Many date versions                                        | REST API Guidelines                    |
| Shopify              | `YYYY-MM` quarterly       | ≥12 months per version, ≥9 months overlap between consecutive versions                                        | ~4 stable at once                                         | Published versioning page              |
| Stripe               | `YYYY-MM-DD.name`         | No forced sunset; per-account pinning; monthly non-breaking releases + twice-yearly named breaking generation | Effectively unlimited (legacy versions kept indefinitely) | Docs + engineering blog                |
| GitHub               | `YYYY-MM-DD` header       | "At least 24 months after a newer version is released"                                                        | Multiple                                                  | Docs                                   |
| Meta Graph           | `/vXX.0`                  | ≥2 years per version - the clock starts when the _next_ version ships, not this one                           | ~8+ live simultaneously                                   | Docs                                   |
| LinkedIn             | `YYYYMM` header           | "Minimum of one (1) year" per monthly version                                                                 | ~12 rolling                                               | Docs (Microsoft Learn)                 |
| Twilio               | Product/SDK EOL           | SDK lifecycle: Latest → Support (12 months, fixes only) → Deprecated → EOL 12 months after announcement       | Varies by product                                         | Versioning & Support Lifecycle         |
| Salesforce           | `/vXX.0` path             | Very long - v7.0-20.0 retired only in Summer '22; v21.0-30.0 pushed from Summer '23 to Summer '25             | Dozens                                                    | Release notes                          |
| Twitter/X            | `/1.1`, `/2`              | ~7 days' notice for the Feb 2023 free-tier shutdown                                                           | 2                                                         | Company announcement, not a policy doc |

## The dimension that explains the table: audience reachability

The dividing line is not company size or API maturity. The harder it is to identify and contact every consumer, the longer and more conservative the notice period has to be - which is why Google and Shopify land on nearly the same ~12-month public floor while the same companies' internal APIs move in days.

| Dimension             | Internal                              | Partner (B2B)                        | Fully public                                 |
| --------------------- | ------------------------------------- | ------------------------------------ | -------------------------------------------- |
| Change velocity       | Fast; coordinated deploys             | Medium; negotiated                   | Slow; conservative                           |
| Notice period         | Days-weeks; contract tests replace it | Negotiated SLA (often months)        | 12-24 months                                 |
| Communication         | Chat/tickets, coordinated             | Account managers, direct email       | Changelog + dashboard + mass/targeted email  |
| Enforcement at sunset | Consumer-driven contract testing      | Grace periods, sometimes per-partner | Long grace, then fall-forward or hard cutoff |
| Governance            | Lightweight linter + code review      | Design review                        | API council / review board                   |

## How to cite these numbers

- **Every published figure is a floor, not a guarantee.** Salesforce slipped a retirement by two years; Twilio extended one product's EOL three times (October 2023 → April 2024 → December 31, 2025) under customer pressure. Cite as "at least X months," never "exactly X months."
- **Exclude Twitter/X from any average.** Its ~7-day notice was a business-motivated monetization change executed after developer relations was laid off - the counter-example that proves the reachability principle by violating it, not a data point.
- **The staged recommendation a policy can adopt directly:**
  - ≥12 months for any fully public API.
  - ≥24 months when consumers ship mobile apps or are enterprises (app-store update cycles and enterprise change management are slow and outside the provider's control).
  - Contract/SLA numbers for partner APIs.
  - Contract testing instead of notice periods for internal APIs.
- **Concurrent-version cap: 2-3 active** is the cross-source consensus; each additional live version multiplies maintenance, testing, and documentation cost. Shopify's ~4 works only because of strict quarterly automation; Salesforce's dozens are the accumulation to avoid.
