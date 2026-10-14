# Brightpier Marketplace: Listing Field Rules (v2 draft)

## Design decisions

- **Rung chosen: exact per-field limits on every field, plus named rejection triggers, shipped as validation rules inside your partner submission console.** Three things drive this:
  - Your 1,200 listings are all vendor-maintained, which promotes exact limits across the board.
  - Three reviewers reading "demonstrate clear value and establish trust" reject different listings. That is your 1-in-5 dispute rate, and the cause is the rule sheet, not the reviewers. Principles-only rules are deleted, not demoted.
  - The console already exists, so the completion-tracked builder is no longer the high-effort option. Most of these rules can run as submit-time checks.
- **I did not run the full interview, so I assumed some answers.** These are the ones to correct:
  - Buyers self-serve install (this sets the 90-second video cap).
  - There is no certification or badge program.
  - Listings are in one language.
  - Brightpier has a trademark worth protecting in app names.
- **Every number below is a self-set starting value.** No industry standard exists. The benchmarked marketplaces disagree with each other on name caps, hook caps and screenshot ratios. Run the checks against your 1,200 listings before publishing (see Rollout) and move any cap that fails most of the catalog for a legitimate reason.

## How enforcement works

| Class | Meaning | Who enforces |
|---|---|---|
| **B** | Blocking: the console refuses submit | Machine |
| **R** | Reviewer-checked against a written test | One of the three reviewers |

- **Cite a rule ID.** Every rejection names the rule ID it failed. A rejection without an ID is invalid and is reversed on dispute.
- **Silence means approve.** If no rule covers what the reviewer dislikes, the listing is approved. The reviewer logs the gap, and it is reviewed at the weekly calibration (see Dispute handling).

## A. Text fields

| ID | Field | Rule | Class | Rejected when |
|---|---|---|---|---|
| A1 | Name | 3-30 characters. Format `{Function} for Brightpier`, or a name that doesn't mention Brightpier. | B | The name starts with "Brightpier", uses Brightpier's logo or wordmark, or contains "official", "beta", "plugin" or "add-on". |
| A2 | Name consistency | Matches the name shown on the app's install or consent screen. | R | The names differ. |
| A3 | Hook | 1-100 characters, plain text. | B | It has emoji, URLs, prices, or any of: "best", "#1", "leading", "ultimate", "revolutionary", "world-class". |
| A4 | Hook content | States what the buyer gets. | R | It describes only the mechanism (see the pair under A6). |
| A5 | Body | 300-2,000 characters. | B | It is under 300 or over 2,000. |
| A6 | Outcome-first | The first sentence says what changes for the buyer. Every feature claim links to an observable result. | R | The first sentence describes technical mechanics the buyer doesn't evaluate on. |
| A7 | Key features | Exactly 3. Title up to 50 characters, text up to 200 characters. | B | There are fewer or more than 3, or a limit is exceeded. |
| A8 | Keyword spam | Any single term appears at most 5 times in the body and at most once in the hook. | B | A term exceeds those counts, or the text lists more than 3 brands, regions or tools in a row with no sentence of added value. |
| A9 | Misrepresentation | The listing describes what the app does today. | R | It lists a feature the app doesn't have, or hides a required third-party account or its cost. |
| A10 | Prerequisites | Required field `Requires`: write "None" or list each third-party account and its cost. | B | The field is empty. |
| A11 | Outcome claims | Any number or guarantee is a stated figure with a source URL. | R | The text uses "guaranteed", "100%", "always" or "never fails", or an unsourced figure. |

**A6 worked pair (Brightpier phrasing, adapted from Shopify's published pair):**
- Accepted: "Reports that show you sales data in real time."
- Rejected: "Reports that use push technology to deliver sales data with 250ms latency."

**A1 worked pair:**
- Accepted: "Task Tracker for Brightpier."
- Rejected: "Brightpier Task Tracker."

## B. Testimonials

| ID | Rule | Class | Rejected when |
|---|---|---|---|
| B1 | Optional. At most 3. Each one needs the person's full name, role and company. | B | A field is missing or the quote is anonymous. |
| B2 | A testimonial can't carry an outcome guarantee. | R | The quote promises a result the vendor can't source (see A11). |

## C. Media

I picked **1600×900 (16:9)** as the one screenshot geometry. Confirm or change it, then keep one geometry only.

| ID | Asset | Rule | Class | Rejected when |
|---|---|---|---|---|
| C1 | Screenshots | 3-6 images, exactly 1600×900, PNG or JPG, up to 2 MB each. | B | Wrong ratio, size or count. |
| C2 | Screenshot content | At least 1 shows the real app UI. | R | None does. |
| C3 | Screenshot baked-in text | No pricing, review or rating claims in the image. | R | One appears. |
| C4 | Screenshot privacy | No personal data of real people. | R | Any appears. |
| C5 | Screenshot quality | Legible text, no distortion. | R | An image is blurry, distorted or off-topic. |
| C6 | Alt text | Required on every screenshot, up to 150 characters, describes what the image shows. | B | Alt text is empty or a filename. |
| C7 | Icon | 1024×1024 PNG, square. | B | Wrong size, or it shows the Brightpier logo or wordmark. |
| C8 | Video | Optional. Up to 90 seconds, public link, captions on. | B | It runs over 90 s or has no captions. |
| C9 | Video content | Shows the real app. Marketing footage is allowed only in the first 10 s. | R | Marketing footage runs past 10 s. |

C6 and C8's captions follow WCAG 2.2 AA (text alternatives, captions). Only one of the eight benchmarked marketplaces requires this today, so it is cheap to adopt now.

## D. Trust surfaces

Trust is a gate on these fields, independent of the copy. The "establish trust with the buyer" line becomes a set of checks:

| ID | Field | Rule | Class | Rejected when |
|---|---|---|---|---|
| D1 | Landing page URL | Public, no login, HTTP 200 on a page that covers the integration and install path. | B | It is behind a login, or it is a PDF or a code repository. |
| D2 | Support | A contact route that needs no new account, plus a stated response time of at most 2 business days. | B | Either is missing. |
| D3 | Privacy policy URL | Public, and it covers: data collected, use, retention period, access/transfer/deletion request process, and a real contact channel. | R | Any of the 5 items is missing. A physical address alone doesn't count. |
| D4 | Setup guide URL | Public, not behind a login. | B | It is behind a login. |
| D5 | Pricing | The listed pricing matches the vendor's own site. | R | The two differ. |
| D6 | URL fields | All URLs up to 250 characters. A crawler checks that every URL is live. | B | A URL returns an error. |

## E. Discovery fields

| ID | Field | Rule | Class | Rejected when |
|---|---|---|---|---|
| E1 | Category | 1 primary, up to 1 secondary, from the fixed Brightpier list. | B | More than 2 are selected. |
| E2 | Search terms | Up to 5, one idea per term. | B | A term stacks two ideas, e.g. "email marketing for leads". |
| E3 | Category drift | A listing whose category no longer fits the app is marked "uncategorized" and leaves browse until fixed. | R | Not a rejection. Reviewer or sweep applies it. |

The category list itself and the stale-listing sweep are separate design work and are not covered here.

## Dispute handling

This section answers your "another reviewer approved the identical thing" problem.

1. **Disputes must name the rule.** A partner disputes by naming a rule ID, or by pointing to an approved listing that fails the same rule.
2. **Precedent decides.** If the cited listing fails the same rule and was approved, the rule was not enforceable as written. The rejection is reversed, and the rule is fixed at calibration.
3. **Weekly calibration, 20 minutes, all three reviewers.** Review the gap log and every reversed rejection. Each one becomes a new or tightened trigger, or a deliberate "silence means approve" decision.
4. **Move R rules into B rules over time.** Whenever a reviewer-checked rule can be turned into a console check, do it. Every one you move removes a reviewer from that decision.

## Rollout

1. **Run the validator against all 1,200 listings first.** Report the violation count per rule. Adjust any limit that fails most of the catalog for a defensible reason.
2. **Give a notice runway.** Announce the new rules to partners at least 60 days before enforcement. Don't reject already-listed apps retroactively.
3. **Enforce on edit.** After the runway, B rules apply whenever a listing is edited or resubmitted. Run a catalog-wide sweep for the rest on your own cadence.
4. **Keep this rulebook content-only.** Security and functionality gates belong to the review process. A blurry screenshot is rejected under C5 whether or not the app is safe.

## Gates and KPIs

I checked the draft against two of the skill's five rulebook gates:
- **Gate 1 (objective reject criterion per required field): pass.** Every field above has one.
- **Gate 2 (one geometry per visual asset type): pass.** The screenshot (C1) and icon (C7) geometries are single values.
- **Gates 3-5 (taxonomy cap, decay trigger with owner, badge display rule): not met by this document.** E1 sets the cap. The decay owner and consequence need their own section, and badge rules only matter if you run a badge program.

Track these once live (no industry benchmark exists; set your own targets):
- First-pass approval rate.
- Dispute rate. Your baseline is about 1 in 5.
- Rejection-reason distribution. A rising "unclear content" share signals a vague rule, not a careless submitter.
- Review turnaround against listing completeness.

## Open questions

- Confirm or change the 1600×900 screenshot geometry.
- Who evaluates a listing before install: a self-serve user, or an admin doing diligence? If admins, cut C8 to 30 seconds and ban marketing footage entirely.
- Does Brightpier ship versioned platform releases? If so, the decay section can use version-currency enforcement.
- Which languages must listings serve?
- Is a badge program planned?