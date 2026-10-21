# Vendor stage precedents

Vendor terms change; re-read the current page before quoting one to a customer.

## Contents

1. Stage vocabularies and promises
2. Guarantees beyond SLA
3. Stage on the wire
4. Notice rules before GA
5. Durations
6. Kill case studies

## 1. Stage vocabularies and promises

| Vendor | Pre-GA labels | SLA | Breaking changes |
|---|---|---|---|
| Google Cloud | Early Access (invite-only, may carry confidentiality terms) and Preview; product labels Alpha and Beta folded into Preview in 2020, while API versions keep alpha and beta channels (AIP-185) | none | allowed, without prior notice |
| AWS | "Beta Service" covers beta, preview, pre-release, experimental | excluded | allowed; may suspend or terminate at any time |
| Microsoft Azure | private preview, public preview, Early Access Preview | excluded | allowed between preview versions |
| Microsoft Graph | `/beta` endpoint, "(preview)" | unsupported in production | without notice |
| Stripe | private preview, Frontier (self-serve, for fast-moving domains, breaking changes more likely), public preview | not stated | "expected" (private), "some expected" (public) |
| GitHub | private preview, public preview | none | not stated |
| Twilio | pilot, private beta, public beta | excluded | allowed |
| Shopify | `unstable` (may be removed, no guarantee it ships); release candidate (the next stable version, may still change until release) | unsupported | allowed |
| Salesforce | pilot, beta, developer preview | excluded | allowed; pilots need a signed non-GA agreement |
| Atlassian | experimental, preview, per operation | not stated | experimental without notice |
| Vercel | alpha, beta, private, limited and public beta | beta outside the Enterprise SLA | allowed |
| Databricks | Private Preview and Beta (no SLA, no API stability); Public Preview with an SLA and a stable API (the outlier) | public preview only | none at public preview |

## 2. Guarantees beyond SLA

- **Data (the industry default, not one vendor's quirk):**
  - Google's pre-GA terms drop its data processing terms, data location commitments, SLA and indemnity, and tell customers not to process personal data in pre-GA offerings.
  - AWS says beta services are for evaluation and should not process sensitive data; beta content may be deleted and does not migrate to GA.
  - Azure's DPA processing, GDPR, data security and HIPAA BAA terms do not apply to previews unless the preview states otherwise.
- **Confidentiality:** Google Early Access and Vercel limited betas carry confidentiality or NDA terms; AWS treats beta materials and test observations as confidential and vendor-owned.
- **Pricing:** Google typically announces GA pricing at Preview; some Azure previews bill normally.
- **Discontinuation:** every vendor above reserves the right to change or discontinue a preview without notice.

## 3. Stage on the wire

| Mechanism | Example |
|---|---|
| Stability suffix in version and package | Google `v1alpha`, `v1beta`, `v1`; `gcloud beta` |
| Dated preview version | Azure `2022-07-07-preview`; Stripe `.preview` versions in the version header |
| Separate endpoint and SDK modules | Microsoft Graph `/beta` with separate Beta SDK modules |
| Unstable path version | Shopify `unstable` |
| Preview media type in `Accept` (retired) | GitHub `*-preview` media types, most graduated together in 2021 |
| Separate spec artifact per stage | Stripe keeps private-preview operations out of GA OpenAPI artifacts |

Lesson from GitHub: removing graduated preview headers from a shared SDK broke self-hosted servers still on older releases; keep the header configurable while any supported release needs it.

## 4. Notice rules before GA

| Vendor | Rule |
|---|---|
| Google Cloud pre-GA terms | changes without prior notice |
| Google AIP-185 | alpha removable without notice; beta removable after a sufficient deprecation period, 180 days recommended |
| Azure | a preview version may become unavailable as early as 90 days after a newer version ships: an availability floor, not advance notice |
| Microsoft Graph | beta changes without notice; production use unsupported, yet common in practice |
| Atlassian | experimental without notice; preview on shorter windows than the 6-month GA minimum |
| Shopify | `unstable` may be removed; stable versions get 12 months |

## 5. Durations

- Google Cloud: average Preview about six months. Google Maps Platform describes Preview as typically reaching GA within 12 months.
- Cloudflare R2: about six months of closed beta with design partners, then about four months of open beta with published per-bucket limits.
- Long tails: GitHub's Checks API preview ran over two years; Gmail stayed in beta over five years, dropped partly because enterprise buyers would not adopt a product labelled beta.
- Design partners (practitioner advice, not vendor policy): 8-12 weeks at 30-60 minutes per partner per week, or 3-6 months.

## 6. Kill case studies

Honeycode is the beta case. The GA cases set the ceiling for notice and migration help, not the floor.

| Case | Stage when killed | Notice | Migration help | Verdict |
|---|---|---|---|---|
| Amazon Honeycode (2023) | beta, about three and a half years in | about 6 months; signups closed at once | export without formulas; usage free after notice | product site silent until signup |
| Parse (2016) | GA | about 12 months | migration tool, open-sourced server, provider guides | the standard to copy |
| AWS CodeStar (2023) | GA | about 12 months | underlying resources untouched | good scoping |
| Google Reader (2013) | GA | about 3.5 months | data export | short runway |
| Google+ APIs (2019) | GA | progressive failures before the date | per-project lists of methods used | not every scope had a migration path |
