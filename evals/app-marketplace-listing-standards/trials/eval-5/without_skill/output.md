# Tidewell: "Certified Listings", trust badges, and lapse handling

## 1. Which certification body?

**Don't pick one. No ISO audit makes "Certified Listings" true.**

- ISO doesn't audit anyone. Accredited certification bodies audit against ISO standards.
- ISO/IEC 27001 certifies an organization's security management system, within a stated scope. That would be Tidewell's. It says nothing about any vendor's app.
- "Certified Listings" tells a buyer that an independent party certified each listing. Today the only reviewer is Tidewell. That gap is the risk. Misleading-claims rules (FTC Act §5 in the US, the UCPD in the EU, CMA guidance in the UK) look at the buyer's impression, not your intent. Have counsel confirm.

Options:

| Option | What it supports | Cost and effort |
|---|---|---|
| **A. Rename** to "Security Reviewed" or "Verified", with published criteria | A true claim today | Days |
| **B. Get ISO 27001 or SOC 2 Type II for Tidewell itself** | "Tidewell is ISO 27001 certified". Useful for enterprise buyers. | Months. Keep it a separate claim from listings. |
| **C. Independent assurance over the review program.** An outside security firm re-tests a sample of badged listings each year and publishes a summary. | "Reviews independently spot-checked" | Moderate |
| **D. Accredited scheme certification of the review process** (ISO/IEC 17065 or 17020 body) | A real "Certified" claim | Heavy. Probably premature. |

**Recommendation:** do A now, B if enterprise buyers ask for it, and C once the review has run for a few cycles. Reserve "Certified" for D. Name the badge "Tidewell Security Reviewed" or similar. Don't blur the line between a Tidewell review and a third-party certificate.

## 2. Homepage

- Drop "Certified Listings".
- Say "Security-reviewed listings" only if the claim is true as worded. If only some listings are reviewed, show a count ("212 of 540 listings reviewed") or link to the criteria. Don't imply all listings are.
- Link the claim to a public page covering scope, method, cadence, and what the review doesn't cover.

## 3. Vendor-held badge: yes, with constraints

The risk is that a badge on a vendor's own site is Tidewell speaking, with no context beside it.

- **Serve it from Tidewell, not as a downloadable PNG.** It's an image or script from a Tidewell URL, so its state follows the real status.
- **Link it to a verify page** showing the app, the review date, the expiry, the scope, and the current status.
- **Scope it to one app and one version line,** never to the vendor as a whole.
- **Put terms of use in the vendor agreement.** Cover allowed placement, no alteration, removal on lapse, and revocation for misuse.
- **Print the date on the badge** ("Reviewed 2026-09") so a stale one is visibly stale.

## 4. Where it shows on a listing

Use three visually distinct tiers. Never one shared "trust" style.

1. **Tidewell review, top tier.**
   - Search card: small badge only.
   - Listing header: one chip with the date ("Security reviewed · Sep 2026").
   - "Security" tab: scope, date, expiry, what was tested, what wasn't, and a findings summary.
   - Search filter: "Security reviewed".
2. **Vendor-held third-party certificates** (SOC 2, ISO 27001, and so on).
   - Security tab only.
   - Label each with its source and say whether Tidewell checked the document.
   - Show the certificate's scope and expiry. An ISO 27001 certificate often covers one office or product, not the app you're listing.
3. **Vendor self-declarations.**
   - Separate section, labelled "Vendor-reported". No badge styling.

## 5. When a badge lapses

Treat expiry and revocation as different events.

| State | Trigger | Listing | Vendor's embedded badge | Who is told |
|---|---|---|---|---|
| **Current** | Review valid | Chip shown | Active | n/a |
| **Due soon** | 60 and 30 days before expiry | Unchanged | Active | Vendor only |
| **Lapsed** | Expiry passes (add a short grace period only if you accept the risk) | Chip removed. Neutral line: "Last reviewed Sep 2026". The listing stays up and keeps its search position, but drops out of the "reviewed" filter. | Flips to "expired" or blank, automatically | Vendor. Installed customers aren't alerted. |
| **Revoked** | Failed re-review, a material unfixed finding, an incident, or badge misuse | Chip removed with a status note. Review the listing's visibility. | Disabled | Vendor and installed customers, using wording legal has approved |

Also:

- **Re-review early on trigger events.** Examples are a major version, new permission scopes, a new data-handling pattern, or a reported breach.
- **Keep the review history** on the verify page.
- **Don't shame lapses.** Most are paperwork delays. Reserve warning styling for revocation.
- **Enforce the terms.** If a vendor leaves a static badge image on their site after lapse, send a notice, then escalate under the agreement.

## 6. What I need from you to firm this up

- What the review covers today (code, pentest, questionnaire, or something else), and how often it runs.
- Whether every listing is reviewed or only some.
- Whether enterprise buyers are asking for SOC 2 or ISO 27001 from Tidewell itself.

This isn't legal advice. Run the final wording of the badge name, the homepage claim, and the revocation notices past counsel before launch.