# Localization posture for the Halyard rulebook

**Recommendation:** translate listings freely, but never let a translation imply that the app supports the language. Treat these as two separate things with separate rules.

## Why the free pipeline is not the answer

- Your Japanese buyers are not asking whether the listing reads in Japanese. They are asking whether the app works in Japanese.
- "Supports Japanese" covers at least five claims, and machine translation (MT) answers none of them:
  - the UI is localized
  - the documentation is localized
  - support staff answer in Japanese, in JST hours
  - the app handles multibyte text and Japanese names, dates, and currency correctly
  - the contract and invoice can be in Japanese
- A fluent Japanese listing for an English-only app makes the buyer's question worse. It looks like a "yes" and becomes a broken promise after signing.
- MT is cheap, but the cost of review and liability is not. Plan for that cost, not the compute.

## Rules to put in the rulebook

**1. The publisher's original text is the source of truth.**
- Translations are derived display copies.
- Label each one "Machine-translated" and link to the original.
- A translation is never the basis of a contractual or compliance claim.

**2. Some fields are never machine-translated.**
- Pricing, permission and scope descriptions, security and compliance claims, and legal terms are excluded.
- Render these from human-reviewed locale templates or structured data.
- A mistranslated permission scope is a trust and security problem, not a typo.

**3. Language support is a separate, structured declaration.**
- Make it a required field on every listing from day one.
- Declare each dimension separately, each as Full, Partial, or None, with the locale list:
  - UI
  - documentation
  - support (channels and hours)
  - data handling (Unicode and locale formats)
- The publisher attests to the declaration.
- The "Supports Japanese" filter reads only this field, never the translated text.
- Use `pt-BR`, not `pt`.

**4. Add a "Verified" tier later.**
- A native reviewer or an automated locale test confirms the declaration.
- Launch it only for ja, de, and pt-BR, and only after the declaration field has real data.
- Do not badge anything at launch. An unearned badge is worse than none.

**5. Misrepresenting language support is a violation.**
- A declaration that proves false means badge removal and, if repeated, delisting.
- Publishers get a clear, enforceable standard, and so do you.

**6. Enterprise buyers get the specific answer.**
- Show the per-dimension declaration on the listing, so the buyer sees "UI: Full, Docs: Partial, Support: English only".
- Optionally let publishers add Japan-specific fields, such as JST-hours support, Japanese contract available, and invoice format. Do this only if buyers keep asking.

**7. Quality gates for the MT pipeline.**
- Keep a glossary and a do-not-translate list for product and brand names.
- Spot-check with a native reviewer for each launch locale, starting with the highest-traffic listings.
- Japanese register and German formal address (Sie) need explicit handling.
- Give publishers an "edit or approve this translation" path. Approved translations drop the MT label.

## Sequencing

1. **Now:** ship the declaration field and the MT labeling rule. Retrofitting declarations onto a populated catalog is far harder than starting with them.
2. **At office openings:** turn on MT listings for ja, de, and pt-BR, with the filter driven by declarations.
3. **After there is data:** add the Verified tier and any Japan-specific fields.

## Assumptions to check

- I assume publishers are third parties who control their own app's language support. If Halyard builds or resells apps itself, rule 5 changes.
- I did not check Japanese or German consumer and contract law on translated terms. Have counsel confirm that the MT label is enough protection for legal-adjacent text.
- I assume the in-house pipeline can handle ja, de, and pt-BR at acceptable quality. Test it on 50 real listings with native reviewers before committing.