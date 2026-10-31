# HubSpot Marketplace submission packet

Everything the Ecosystem Quality team reads before approving a listing, plus the tier table. Items marked † change often: verify against current HubSpot developer docs.

## Contents

1. Listing wizard fields
2. Shared data and scopes
3. Setup guide
4. Demo video
5. MCP and agent tools
6. Tiers
7. Deadlines

## 1. Listing wizard fields

Seven tabs: Listing info, App details, Pricing, App features, Support info, Testing info, Review info. Run validation on Review info before submitting.

- **Name and tagline**: your brand, never "HubSpot", "Hub" or "for HubSpot". Integration-specific: what the customer gets from connecting, not your product's general pitch.
- **Icon**: 800x800 px† JPG or PNG, filling the square, no text or wordmark.
- **Categories**: up to 2†. **Search terms**: the words a buyer types.
- **Screenshots**: up to 8† with alt text, showing the app inside current HubSpot UI, placeholder data only, no PII.
- **HubSpot features** up to 10†, **other tools** up to 6†, **languages** the app really supports. Auto-translation at submission overwrites manual translations for the languages left ticked.
- **Pricing**: up to 5 plans†; only plans that include the integration; prices identical to your website; Free only for free-forever or freemium.
- **App features**: one per feature, with the scope groups it needs (HubSpot checks portal compatibility with them).
- **Support**: support email and support languages required; live, public support, ToS and privacy URLs; URL fields max 250 characters†.
- **No data or statistics** in the listing unless you link a case study.
- **App cards**: no sensitive data shown, one primary button per surface, no HubSpot sprocket or other companies' logos, no "inbound" branding.

```
// ✓ Good - names the objects, the direction, and the outcome
Syncs Acme invoices to HubSpot deals both ways, so reps see payment status on the deal record.

// ✗ Bad - general product marketing, unverifiable claim
Acme is the #1 billing platform trusted by 10,000 teams.
```

## 2. Shared data and scopes

Build this table before writing copy; it must match the scopes in your app configuration.

| HubSpot object | Your object | Direction      | Scopes                             | Required? |
| -------------- | ----------- | -------------- | ---------------------------------- | --------- |
| Deals          | Invoices    | Bi-directional | `crm.objects.deals.read`, `.write` | Required  |
| Contacts       | Customers   | HubSpot to app | `crm.objects.contacts.read`        | Required  |
| Line items     | Line items  | App to HubSpot | `crm.objects.line_items.write`     | Optional  |

- Read plus write on one object = bi-directional row.
- A scope only a subset of customers needs = optional or conditionally required, never required.
- Sensitive-data scopes are barred for apps with app cards, agent tools or MCP components.

## 3. Setup guide

Public URL, no login or paywall, specific to the HubSpot integration. To list: install and configure steps. To certify, also: what the app does; install with a screenshot of each step including the scope screen; configure; use (manual and automated); disconnect; uninstall; what disconnecting and uninstalling do to the customer's HubSpot data. Keep screenshots current with the HubSpot UI and the scope list.

## 4. Demo video

- **Listing**: demo video or guided walkthrough of install, configuration and permission use replaces testing credentials†.
- **Certification**: YouTube URL, at least 3 minutes†, audio or captions; purpose and use cases; install; configure; primary features; in-HubSpot interaction; disconnect; uninstall and its data effect; the Uninstall App API call. Promotional videos are rejected.
- **Agent tools**: separate form, 3+ minute† testing video of the runs you tested.
- **MCP component**: configuration, connection test and one successful tool call in Breeze.

## 5. MCP and agent tools

- **MCP listing**: a new standalone app with its own listing; `mcpUrl` on HTTPS with no token in the URL, pointing to a server you own or that its owner delegated to you; component name names the platform ("Acme MCP", never "MCP Server"); 1-5 plain-language `mcpUseCases`; each `mcpTools` entry matches the server function name, and any tool that changes data is `accessType: "write"`.
- **Agent tools**: names start with a verb, 3-7 words, no company attribution; descriptions 50-150 characters†; every object a tool reads as input needs its `.read` scope in the app's required scopes; front-office use cases only (marketing, sales, service).

## 6. Tiers

Tier applies to the developer account, not one app. Tier-ups quarterly on the trailing 12 months†, tier-downs twice a year†. Thresholds†, as attached MRR (12-month average); influenced MRR (deal, or first-90-days install); reviews and rating:

- **Partner**: a live listing.
- **Rising**: $400K; $1K or $5K; 5+ reviews, 3.5+.
- **Leading**: $1M; $5K or $30K; 5+, 4.0+; certification preferred; named technical referent and partnerships owner.
- **Premier**: $7M; $30K or $100K; 10+, 4.0+; certification mandatory; plus executive sponsor and account-mapping data sharing. Exception: $100K+ influenced deal MRR replaces the attached and first-90-days MRR thresholds; every other Premier requirement still applies.

- Attached MRR is HubSpot revenue from customers actively using your app: driving usage among HubSpot's larger customers moves it, listing work does not.
- Influenced deal MRR comes from deals you sourced or supported in HubSpot sales cycles: submit every one in the developer platform, since unsubmitted deals risk not counting. First-90-days MRR counts customers who installed your app within 90 days of buying HubSpot; nobody submits it.
- Leading and Premier activate only after the Partner POC form, due within two weeks†.
- Review and rating thresholds, and certification for Premier, phase in through 2026†; full evaluation applies from January 1, 2027†. No tier-downs during the 2026 launch year†.

## 7. Deadlines

Dated enforcement points; re-check the HubSpot developer changelog before quoting any.

- Classic CRM cards: banned for new listings and certifications; listed and certified apps had to move to app cards by October 31, 2026†.
- From November 2, 2026†: new listings only on a supported platform version (2025.2 or later at announcement); certification and recertification give about 60 days† to migrate.
- Legacy public apps: creation ended in June 2026†; from November 2, 2026† they are rejected for new listings; listed ones are eligible for delisting after the September 2027† enforcement date.
- Projects 2025.2 and older: migrate to the current version by March 2027†.
- v4 APIs: unsupported from March 2027†, with about 60 days† to migrate during certification. Calling any v1-v4 API after September 2027† costs certification.
- Platform versions ship every March and September and turn unsupported 18 months after release.
