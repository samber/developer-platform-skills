# Do Brightslot need a Google Workspace Marketplace listing?

**No, not now.** Your integration doesn't need one, and the two marketing asks rest on wrong premises. I answered from knowledge and didn't fetch Google's current docs. Check the three claims marked ⚠️ before you tell marketing.

## Answers to the three questions

| Question | Answer |
|---|---|
| Do we need a listing to connect Google Calendar from our web app? | ❌ No. Calendar OAuth works without any listing. |
| Can we bill through the Marketplace? | ❌ ⚠️ As far as I know, the Workspace Marketplace has no billing or payment system. You charge users yourself, for example with Stripe. |
| Can we pay for Editor's Choice? | ❌ ⚠️ Editor's Choice is an editorial badge Google awards. You can't buy it. |

**Likely source of the billing confusion:** Google Cloud Marketplace is a different product. It is a procurement channel for GCP customers who want to draw down their cloud commit. It is worth considering only if you sell to enterprises that buy through GCP. It is not the same thing as the Workspace Marketplace.

## What you do need: OAuth app verification

- Calendar scopes are **sensitive**, not restricted (⚠️ confirm the exact scopes you request).
- Sensitive scopes require Google's OAuth verification, which is separate from any listing.
- Without verification, users see the "unverified app" warning and you hit a cap of about 100 users.
- Verification needs these items:
  - a verified domain
  - a privacy policy
  - a justification for each scope
  - a demo video of the consent flow
- Request the narrowest scope that works. For example, `calendar.events` or `calendar.freebusy` is easier to get approved than full `calendar`.
- Restricted scopes would also require a CASA security assessment. Calendar scopes shouldn't trigger it, but confirm that against your scope list.

A listing would also require this verification, so it adds work on top of it.

## What a listing does and doesn't give you

**It gives you:**
- A page in the Marketplace, which gets low organic traffic compared with SEO and your own site.
- A trust signal for Workspace admins who allowlist apps.
- A route to domain-wide install by an admin.
- The ability to ship a Calendar or Gmail sidebar add-on, which you don't have.

**It costs you:**
- Google's app review.
- Ongoing compliance and branding upkeep.
- Support obligations.
- Possibly a registration fee (⚠️ check the current developer fee).

## Decision rule

List only if **at least one** of these is true:
1. You want an in-Calendar or in-Gmail add-on, not just a web app.
2. Enterprise prospects say their admins only allow apps from the Marketplace, or ask for domain-wide install.
3. Marketplace search shows real demand for scheduling apps and you can't win that traffic elsewhere.

Otherwise, skip it.

## Next steps

1. **Finish OAuth verification now.** This is mandatory regardless of what marketing decides.
2. **Bill with your own processor.** Don't wait on any marketplace billing.
3. **Get discoverability from SEO.** Build "Google Calendar scheduling" integration pages on your site, plus comparison pages.
4. **Ask sales about admin-install demand.** If nobody has asked for it, revisit the listing in 6 months.
5. **Tell marketing:** Editor's Choice comes from quality, adoption and polish. If you list later, aim for it by building a good product, not by paying for it.

I can draft the OAuth verification checklist or a short reply to marketing next. Tell me which you want.