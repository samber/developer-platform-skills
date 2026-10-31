# Verdict: start Monday, but change the plan first

The plan has one flaw. **The "flip" to a public app probably doesn't exist.** Fix that, plus a few smaller risks, and engineering can still start Monday.

I haven't checked Shopify's live docs in this session. Confirm items 1 and 2 with your Partner Dashboard and Shopify partner support before you commit.

## Blockers (settle before kickoff)

1. **Distribution method is chosen once per app.**
   - As I understand it, Shopify fixes this when you create the app record. A custom-distribution app can't be converted to a listed public app.
   - The Q1 "flip" would really mean a new app record with a new client ID. Every brand would reinstall and re-authorize, and webhooks and tokens would need re-registering.
   - Budget that migration now, or avoid it (see "Recommended shape" below).

2. **Custom distribution may not reach three brands cleanly.**
   - Multi-store install is easy only when the stores sit under one Plus organization. Three separate brands usually don't.
   - Otherwise you get one install link per store. Confirm this works for your three before you promise a date.
   - Custom apps created directly in the store admin were being phased out for new creation. Check which creation path is current.

3. **Peak season.**
   - Monday is Nov 2, so go-live on live Plus stores would land in the BFCM freeze.
   - Brands will likely refuse inventory-write changes in November and December.
   - Real feedback may not arrive until January. That undercuts the "feedback over the next quarter" premise.
   - Ask each brand now whether they will go live before the freeze, or run read-only or shadow mode until it ends.

## Design risks (these decide whether Q1 is a flip or a rewrite)

4. **Don't build a one-off for three brands.** It will hard-code SKU mappings, location IDs, and one ERP tenant per brand. Public-app readiness takes these from day one:
   - multi-tenant data model and per-shop token storage
   - managed install and OAuth, session tokens, and the mandatory GDPR/privacy webhooks
   - Shopify Billing API hooks, even if they stay off for the pilot
   - tenant onboarding that needs no engineer: location mapping, SKU matching, and a configurable source of truth

5. **Inventory semantics are where syncs fail.**
   - Decide one-way (ERP to Shopify) or two-way. Name the source of truth per field.
   - Use idempotent writes and compare-before-set. Handle multi-location and reserved or committed quantities, and don't use `available` as a single number.
   - Plan for GraphQL cost-based rate limits and webhook gaps: combine webhooks with a scheduled reconciliation job.
   - Define behavior on ERP downtime and on oversell.
   - Ask each brand for its location count and SKU volume. A flash sale is the worst case.

6. **Public listing is a separate workstream.**
   - Review plus any "Built for Shopify" requirements (performance, Polaris and App Bridge, listing assets, support) take weeks and often a few rounds.
   - Q1 holds only if you submit in December or early January. Assign an owner now, or the listing slips to Q2.

## Commercial and legal

7. **Billing.** Public apps must charge through Shopify Billing, and Shopify takes a revenue share. Custom apps are not bound the same way.
   - Do the three brands pay via your ERP contract? Then moving to a public listing changes how everyone else pays, and may conflict with existing contracts. Decide the pricing model before Q1.

8. **Data protection.** The sync touches only inventory and locations, which is lighter than customer data. Still, you become a processor for three brands, so you need a DPA, a security review, and access scoping. Request only inventory and location scopes, and re-review before adding more.

9. **Support and SLA.** "Custom" often becomes "bespoke support forever." Agree in writing that the three brands are design partners, with a defined feedback cadence and a clear end to pilot terms.

## Recommended shape

- **Option A (my pick):** Build one multi-tenant codebase from day one. For the pilot, use the distribution path Shopify confirms works for these three stores. Create the public app record in Q1 from the same code, and schedule the reinstall as a planned, communicated migration.
- **Option B:** Create the public app now and submit for review early, using dev stores and the brands' staging for feedback. Go live as soon as approved. This is the least rework, but live feedback depends on review timing. Ask Shopify partner support whether any unlisted or limited-install path exists for this.
- **Not recommended:** a per-brand custom build with a promised flip.

## Questions I need answered

1. Are the three brands under one Plus organization, or separate?
2. Will they go live before the BFCM freeze, or only after?
3. Is the ERP the sole source of truth for inventory, or two-way?
4. How do customers pay for this today: ERP license, or a new fee?
5. Who owns Shopify review and listing, and when does it start?

## Before Monday

- [ ] Confirm distribution options and the reinstall impact with Shopify partner support.
- [ ] Get each brand's go-live date against the freeze.
- [ ] Get engineering to commit to the multi-tenant, billing-ready architecture.
- [ ] Settle the billing and pricing model.
- [ ] Name an owner for the Q1 listing submission.

If those five are done, kick off Monday. If they aren't, start with architecture and the Shopify questions, and write code once they are answered.