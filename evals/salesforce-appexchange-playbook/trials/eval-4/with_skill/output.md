**Short answer: Checkout can't carry this pricing, and Docuvane's Toronto base probably rules it out too. Launch on the managed 2GP + Channel Order App (COA, offline PADA) path. Card-on-file for everything is not available, and invoices don't go away.**

## 1. Assumptions

You didn't answer these, so I assumed:

- **In-org footprint:** the managed package puts objects, UI or automation in the customer's org. That follows from a security-reviewed managed package, so Checkout would otherwise be possible.
- **Stage:** security review passed, so you're between Building and Listed. I assume you aren't yet a listed partner with a signed PADA. If you already are, skip step 1 of the actions below.
- **Currency and customers:** USD and CAD buyers, in the US and Canada.
- **Date and team:** no target date and no stated engineering capacity. Weeks below are relative to today, 2026-10-30.
- **OAuth:** an External Client App (ECA) or Connected App is in use. I don't know how many customer production orgs run it.

## 2. Listing and payment path

**Path: managed 2GP + COA (offline PADA).** Each of your facts moves the choice:

| Your fact | Effect |
|---|---|
| $0.02 per document processed (metered) | Checkout covers per-seat or per-org, one-time or monthly/annual subscriptions only†. Usage-based pricing belongs on COA†. |
| Three-year contracts with custom discounts | The GTM app allows 12-month orders, no auto-renew, and seat-based deals only†. Negotiated multi-year deals go through COA†. |
| Toronto company | Checkout requires a company in the US, UK or EU†. Canada isn't listed. |
| $300 per org per month | This alone would fit Checkout. It is also the only part that fits. |

**What this means for the card-on-file idea:**
- **No Checkout for metered or enterprise deals.** The usage fee can't be billed through Checkout, so a card-only model fails on the pricing alone.
- **COA means you bill outside Salesforce.** You report each order through the COA within one business day of the sale†. Procurement still gets an invoice or a contract. Card-on-file can't be the universal rail.
- **Don't split the model to keep Checkout for the $300 fee.** Switching Checkout ↔ non-Checkout, or changing pricing units, sends the listing back to approval†. A hybrid also isn't a documented option. Ask your account manager in writing before building anything around it.
- **Don't re-incorporate in the US, UK or EU just to reach Checkout.** It wouldn't fix the metered pricing, and it's a legal and tax decision well beyond this launch.

**Revenue share:** set in your PADA, commonly 15% for ISVforce (your app sold to Salesforce customers)†. Checkout's 15% + $0.30 per card payment† is irrelevant on this path.

**Ways to give procurement what it wants without Checkout:**
- Sell the $300 platform fee as an annual prepay and invoice it once.
- Take card payment on your own billing side for small orgs, but only if your account manager confirms it is compatible with the PADA.
- Offer a committed-usage tier for enterprise: a fixed document volume per year, with overage priced at $0.02.
- Keep three-year terms as negotiated COA contracts, with the discount schedule written into the order.

## 3. Irreversible-choice register

| Choice | Status | Owner | Decide by |
|---|---|---|---|
| Listing type: packaged solution (managed 2GP) | Already fixed by the package | Product lead | Done |
| Namespace | Already fixed by the package | Eng lead | Done. Confirm it's the product brand. |
| Global Apex and Visualforce | Permanent once released. Check the released version's global surface is a small facade. | Eng lead | Before the next version |
| Protected components | Internal custom settings, metadata types, labels and permissions must be protected. Once released unprotected, they stay. | Eng lead | Before the next version |
| **Pricing path: COA, metered + enterprise** | Switching later sends the listing back to approval† | Founder/CFO | Before listing submission |
| OAuth controls (PKCE, refresh rotation, IP allowlist) | Can't be turned off once enabled. Ship client changes first, test in a sandbox, then enable. | Security lead | Before enabling |

## 4. Security review plan

The review has passed, so there is no new submission. Treat it as a baseline for future versions:
- **Ancestry:** build every new version on the highest passed managed-released version, so it lists without a new review.
- **Scope changes:** any new in-scope endpoint or Salesforce-data path forces a review. This includes any billing or usage-reporting endpoint you add for COA reporting.
- **Top three risks to keep clean:** CRUD/FLS on queries and DML, `with sharing`, and SOQL injection.
- **OAuth:** if the ECA or Connected App runs in more than two customer production orgs, the OAuth controls are mandatory. The deadline was May 11, 2026†, and the sanction is delisting. Confirm yours are enabled.

## 5. Timeline

I can't date this without your target date. In sequence, with no review failure, since the review is already passed:

1. **Weeks 0–1:** apply to the Partner Community if you aren't yet a partner. Open the PADA conversation with the account manager.
2. **Weeks 1–6 (estimate):** negotiate COA terms and the PNR share. Get listing approval. Both the signed PADA and listing approval must precede publishing.
3. **Week 6 onward:** publish, and set up the COA order process.
4. **First paid install:** expect it after publishing. Practitioners estimate 4–9 months from signup to the first paid install†. The security review is behind you, so you should land at the short end, but I can't put a date on the PADA negotiation.

If a hard date matters, tell me and I'll count back from it.

## 6. Maintenance calendar

- **Three yearly Salesforce releases:** test each in a preview sandbox. Move API calls off any retiring version.
- **Push upgrades:** use sandboxes for a week, then production in batches, off-peak, 3–4 weeks after a major release.
- **Re-review:** periodic, fee due ($999†). Keep the security contact on Company Info current. A missed re-review expires every version.
- **COA duties:** report each order within one business day of the sale†. File cancellations as the PADA requires, usually 30+ days before renewal†.
- **Revenue share and review fees:** unpaid ones expire the review and pull the listing.
- **OAuth controls:** track the enablement date and the rotation behavior in your client.

## Questions for your Salesforce account manager

1. Is a Toronto company eligible for Checkout, and in which currencies?
2. Can Checkout carry the flat monthly fee while COA carries metered and enterprise deals on one listing?
3. How is usage-based billing reported through COA?
4. What PNR share applies to Docuvane?

† Verify every Salesforce figure, fee, share, eligibility rule and duration against current Salesforce partner docs before quoting it.