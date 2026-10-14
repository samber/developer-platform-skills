# Localization posture for the Halyard listing rulebook

Recommendation: **auto-translate with vendor override for listing text, plus a separate vendor-declared "product language support" field.** The two are independent axes. Your Japanese buyers asked about the second one, and the pipeline only gives you the first.

## Assumptions

The skill asks ten interview questions first. I'm answering without them, so I assumed the following. Correct me if any are wrong, because the first two change the answer.

- **Q6:** Japanese, German and Brazilian Portuguese within 12 months, with English staying the source language.
- **Q4:** Japan enterprise buyers are admins doing diligence, not self-serve installers.
- **Q7:** There is no region gating that hides listings by distribution region. If there is, region-locked becomes mandatory on top of this.
- **Q2:** The catalog is vendor-maintained, so a vendor writes the English source.

## Why this rung

The skill's default for one primary market is opt-in per market, which is the honest floor. Two facts re-rank the menu:

- **Q6 names three markets, not one.** Opt-in per market would leave most listings English-only in all three regions.
- **You already own a machine-translation pipeline.** That is the asset the skill says to amortize, so auto-translate with override is the promotion.

Your "basically free" claim covers only the translation step. The real costs are elsewhere:

- Machine output carries Halyard's name, and the skill ranks this rung last on trust of the language claim.
- Reviewers can't enforce content triggers in a language they don't read.
- Vendors' overrides go stale.

The rulebook has to price those in.

## The Japan question needs its own rule

"Supports Japanese" means the product runs in Japanese. It does not mean the listing page reads in Japanese. The skill ranks all-or-nothing capability declaration as the only rung where a language claim is guaranteed true in the product. It also says to promote that rung when buyers treat language support as a purchase-blocking claim. Your buyers have asked twice.

Auto-translating every listing creates a trap. A machine-translated Japanese page can read as "this app supports Japanese" when the app is English-only. The skill's misrepresentation trigger covers this: the listing must describe what the app actually does.

The fix is to decouple the two claims. Don't make the vendor commit to all-or-nothing for every listing, which the skill rates as the highest vendor effort for the least reach. Make it a separate, structured declaration.

## Draft rulebook text

**1. Listing translation (auto-translate with override)**

- Every listing is machine-translated from the English source into ja, de and pt-BR by default.
- A vendor may replace any one language's text. Overrides are vendor-authored content and are subject to every rejection trigger in section 3 of the rulebook.
- Every machine-translated page shows a visible label: "Machine-translated from English. Product language support is listed under Language support." The label is not removable by the vendor.
- App name and trademark naming order ("X for Halyard") are never translated.
- The English source is the only version reviewed for rejection triggers. Translations are derivative and inherit its approval.
- Deleting an override reverts to machine translation only after a visible confirmation to the vendor. Shopify reverts silently, and the skill's benchmark notes it.

**2. Product language support (declared field)**

The vendor declares, per language, a level for each of four surfaces:

| Surface | Levels |
|---|---|
| App UI | none / partial / full |
| Documentation | none / partial / full |
| Support channel | none / English-only / native-language |
| Data handling (locale, encoding, name and address formats) | tested / untested |

- Only "full" UI may be shown as "Supports Japanese". "Partial" must say which parts are missing.
- A vendor who declares a level that a reviewer or buyer report disproves gets a misrepresentation violation. The listing is rejected or downgraded under the decay policy.
- The field is machine-readable so buyers can filter on it. Japan admins can then filter for "UI: full, support: native-language" without reading prose.
- This is a vendor attestation, not a certification. Don't describe it as verified by Halyard, and don't imply an external body certifies it. The skill says none exists for listing quality.

**3. Trust surfaces**

- The privacy policy, landing page and support page are gated in the source language, as before.
- Each listing states the support channel's response language. A Japan buyer needs to know whether "2 business days" means a reply in Japanese.

**4. Media**

- Screenshots and video are not machine-translated. Chrome shows that unlocalizable assets are an accidental gap.
- A localized listing may show English-UI screenshots only if the Language support field says the UI is not fully localized.
- Optional per-locale screenshots are allowed. They must meet the same geometry as the source (one published ratio per asset type).

**5. Decay**

- When the English source changes, machine translations regenerate automatically.
- Vendor overrides older than the source change are marked stale. The page falls back to machine translation, with the label, until the vendor re-confirms the override.
- The Language support declaration is re-confirmed at every recertification or sweep. This follows the skill's default decay rung of staleness downgrade plus policy-as-violation with a calendar sweep.
- Notice runway: new requirements apply to existing listings only after a published notice period.

## What to ship first

The skill says to ship rungs that are policy text first when a date is fixed. Sequence:

1. **Language support field and the "Supports Japanese" rule.** This is policy text plus a form field. It answers the question your Japanese buyers have already asked, so it comes first.
2. **Machine-translation default with the visible label.** Switch it on per language, not all three at once.
3. **Override path and staleness handling.** These can follow once there is real override volume.

Don't wait for the sales offices to open. The declaration only has value if vendors have filled it in before the first Japan deal closes.

## Rulebook gates

Check the localization section against the skill's gates:

- **Objective reject criterion (gate 1):** "Language support level declared as full but UI not localized" is checkable by a reviewer or a buyer report. Translation label removal is machine-checkable.
- **Decay trigger with owner and consequence (gate 4):** the override-stale fallback to machine translation has an owner (the platform) and a stated consequence (the label returns).

Track these KPIs once live:

- **Override rate per language.** It shows where machine translation isn't trusted.
- **Disputes citing a language-support claim.** A high count means the field levels are ambiguous.
- **Japan filter usage and listing-to-install conversion for filtered buyers.** Treat these as direction, not targets.

## Questions that would change this

1. Is distribution-region selection a visibility control today? If yes, region-locked is forced on top of this.
2. Who reviews Japanese or German vendor overrides: no one, a machine check, or a native reviewer? This sets the effort ceiling (Q10) and may argue for fewer overrides at launch.
3. Are the two Japanese enterprise asks about the UI, the docs, or support in Japanese? The field levels above should match what they actually mean.