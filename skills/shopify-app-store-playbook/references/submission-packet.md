# Shopify App Store submission packet

Fill every item before pressing **Submit your app**. Figures marked `†` change without notice: check the live App Store requirements page.

## Configuration (App Store review page)

- App URL and redirect URLs tested: install lands on the OAuth grant screen, then the app UI. Shopify-managed installation (Shopify CLI config) handles this.
- Domains and API contact email free of "Shopify", "Example" or misspellings of Shopify.
- Compliance webhooks subscribed (customer data request, customer redact, shop redact).
- App icon 1200 x 1200 px†, JPEG or PNG, no Shopify marks, no pricing.
- Emergency developer contact: email and phone that someone reads.
- Automated checks on the review page all green.

## Listing

- Primary language and at least one listing; languages field lists only languages the app UI supports.
- App card subtitle: the merchant benefit in one phrase, no stats, no keywords added for search.
- App details: features at a high level, no other apps of yours, no stats, no "first/best/only", no testimonials.
- Feature media and 3-6 screenshots at 1600 x 900 px†: real app UI, unique images, no browser chrome, no pricing, no reviews, no Shopify logo.
- Pricing details: every plan, trial length and charge, matching the plans in billing exactly.
- Up to five search terms†, one idea each; categories and tags that match the primary function.
- Requirements: "Merchant must have online store" when the app embeds in themes; geographic or plan requirements.
- Support: email always on file, plus an optional portal or phone.

## Test access

- Testing instructions that reach every feature, step by step, including any step inside your own UI.
- A dedicated test account on your service exempt from 2FA, OTP and SSO, or static verification codes; credentials keep working after publish.
- Test accounts for every third-party service the app connects to, with dummy data.
- Screencast in English or with English subtitles: install, onboarding, core features, plan change.

## Protected customer data

- Opt out when the app reads no customer data.
- Otherwise request Level 1, plus each Level 2 field (name, address, email, phone) with a one-line reason per field, and complete the data protection details. Submit the request before the app enters review.

## Embedded app checks

- Latest App Bridge script first in every document; session tokens; works with third-party cookies blocked.
- GraphQL Admin API only; expiring offline access tokens requested (`expiring=1`).
- No web errors (404, 500, 300 redirects), no switching between embedded and standalone.
- Theme changes only through theme app extensions, with setup instructions and a deep link.
- Plan upgrades and downgrades work from inside the app; charges appear in the merchant's charge history.
- Uninstall, reinstall: OAuth runs again, the merchant returns to the workflow without duplicate-record errors.

## Review notes

- Anything a reviewer could misread: why a sensitive scope is needed (`read_all_orders` beyond 60 days†, checkout or pixel scopes), why a connection to your service is required, billing exemption request if any.
- Keep one owner on the submission contact inbox with `noreply@shopify.com` allowed.
