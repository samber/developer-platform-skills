**Do not submit next week. Do not plan a Linkwise listing at all: HubSpot excludes this architecture.**

Next action (2 min): open the Linkwise OAuth app in HubSpot developer account and note its distribution type and `platformVersion`. That answers the open question below.

## Verdict: excluded

The eligibility rules bar these categories:
- White-label integrations embedded invisibly in another vendor's product.
- Token or credential brokering.
- Developer-only infrastructure.

Linkwise is all three. Customers embed it, their users see the customers' brands, and it brokers HubSpot tokens.

The rule names your case directly. Unified-API vendors' customers list their own branded apps, never the infrastructure. No install count cures an excluded architecture, so 400 portals changes nothing.

The reasons below are also real, but they only matter if the exclusion did not apply.

## Other blockers

1. **Timeline.** Initial review takes 10 business days†. One Draft bounce adds another 10 business days†. Next week is impossible even for an eligible app.
2. **One app ID and one OAuth client per listing.** One shared Linkwise client serving every customer's brand does not fit that model.
3. **Install count.** 400 portals on one OAuth app conflicts with the 25-install cap† for unlisted marketplace-distribution apps. Private OAuth caps at 10† (100† from a Solutions Partner portal). Either the app is a legacy public app (see 4) or something else is going on.
4. **Legacy app risk (assumption: yours is legacy).** Legacy public apps are rejected for new listings from November 2, 2026† (2 days from today). A legacy app with over 25 installs cannot list. Migrating it enforces the 25-install cap†.
5. **Do not run `hs app migrate` yet.** Your 400 live installs could break. Get a written answer from HubSpot first (below).

## Plan B

1. **Today:** check the app's distribution type and `platformVersion` (the next action above).
2. **This week:** write to HubSpot support, or your Technology Partner Manager if you have one (App Listings > More > View listing details). Cite the install count and ask three things:
   - What happens to installs above 25?
   - Do new installs error?
   - Is there a cap exception?

   Do not migrate without a written answer.
3. **Next 2 weeks:** build a "list your own HubSpot app" kit for your customers. Each customer gets their own developer account, branded app, and OAuth client with marketplace distribution. The kit covers:
   - the scope-to-Shared-data table;
   - the setup-guide template;
   - the packet checklist.

   Each customer needs 3 unaffiliated active installs† of its own. This is the only listing route HubSpot permits for your model, and it gives your customers the visibility.
4. **For legitimacy now:** use public proof that needs no listing: a HubSpot-specific setup guide and a security page.
5. **Decide later:** a Linkwise-owned listing is possible only for a separate, visibly branded, standalone Linkwise app. Examples are an app card or a workflow action that Linkwise sells directly to HubSpot users. That is a different product from the white-label connector.

Is such a Linkwise-branded product on your roadmap? If yes, ask me and I will run the full building/piloting plan for it.

Questions that would change this:
- Is your OAuth app legacy, or built on projects? (Next action, above.)
- Does any customer already have its own HubSpot developer app?
- Does Linkwise sell anything to HubSpot users directly, without a customer's brand?

Also separate: whether HubSpot is worth this effort at all, or which partner program to join first, belongs to `samber/developer-platform-skills@integration-partnership-strategy`. Want me to run it?

† Verify against current HubSpot developer docs and changelog.