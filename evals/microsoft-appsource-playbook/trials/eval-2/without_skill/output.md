Yes, there are four problems. Two are structural: the Contact Me flip and the live-card test. I wrote this from memory and haven't checked it against current Partner Center docs, so verify the points marked ⚠️ before you commit.

## 1. Contact Me, then "flip" to transactable ⚠️

- **The flip probably isn't a flip.** The listing option (Contact Me, Free trial, or Sell through Microsoft) is fixed per SaaS offer once it's published. I believe moving to transactable means creating a new offer with a new offer ID.
- **What you'd lose.** The new offer doesn't inherit the listing URL, any ratings, or whatever search ranking the old one built. You'd also have to unpublish the old one, because Microsoft pushes back on duplicate listings for the same product.
- **"In the catalog" has little value.** A Contact Me listing only generates leads. It also needs a lead destination (CRM or email) wired up and monitored.
- **Q2 is real engineering, not a switch.** Transacting needs:
  - a landing page that resolves the purchase token
  - the fulfillment API v2 (subscription lifecycle webhooks)
  - a payout and tax profile, plus the extra certification review
- **Policy risk for your segment.** Marketplace policy expects the product to be relevant to Microsoft customers, which usually means it integrates with or extends Microsoft or Azure. If Pingwell has no Microsoft integration, an API monitor may be rejected or questioned at certification. Check the SaaS certification policy before you build anything.

**Recommendation:** skip Contact Me and go straight to a transactable offer. If you need a catalog presence sooner, accept that the Contact Me offer is throwaway and plan its retirement.

## 2. Plan design

- **Pricing model is permanent per plan.** A plan is either flat-rate or per-user, and I believe it can't be changed after publishing. Published plans can't be deleted, only hidden from sale. So "flat monthly now, per-seat later" means new plans next to the old ones, and existing subscribers stay on the old ones.
- **Meter dimensions are hard to undo.** Dimension IDs are permanent, and you must emit usage events yourself through the Metering Service API (aggregated hourly). Decide the API-call meter's ID, unit, and included quantity now, even if you ship it later.
- **Price changes are constrained.** Increases need advance notice, and the rules differ by term. Don't plan on repricing quickly.
- **Plan the tier ladder once.** Draft flat, per-seat, and metered together before publishing anything. The cheapest mistake is the one you make on paper.

## 3. Teams app selling "the same offer" ⚠️

- **The Teams app doesn't sell anything itself.** It's a separate Teams app offer that links to a SaaS offer, and the purchase happens through that SaaS offer.
- **Order matters.** The SaaS offer has to exist and be transactable first, so Teams can't ship alongside a Contact Me listing. If it's in scope, it comes after Q2.
- **Use one set of plans and one fulfillment backend.** Teams and the web listing should feed the same webhook and landing page. Build it to be idempotent, since the same tenant may arrive from both paths.

## 4. Testing checkout on the live offer with a corporate card ❌

Don't do this.

- **It's a real purchase.** Marketplace bills through the buyer's Microsoft billing account, so your card gets charged. You create a real subscription, trigger production webhooks, and may generate taxes, invoices, and a payout. Refunds and cancellations on marketplace subscriptions are slower and more restricted than a normal SaaS refund.
- **It pollutes your data.** A fake customer lands in your metrics, in Microsoft's reporting, and possibly in co-sell signals.
- **It tests too late.** A defect found live is already public.

**Test like this instead:**

1. Use the Preview audience step. List your own Azure subscription or tenant IDs, and only those buyers can see and buy the offer before you go live. I believe preview purchases aren't billed, but confirm that.
2. Create a private plan at a nominal price (or a private offer) restricted to your test tenant for the end-to-end billing path.
3. Exercise every lifecycle webhook: subscribe, change plan, change quantity, suspend, unsubscribe, reinstate.
4. Send metered usage events from a test subscription before the real meter goes live.
5. Do a go-live smoke test with one hidden, low-price plan and cancel it immediately. Keep that as the only live transaction.

## Suggested sequence

1. Check the Microsoft relevance policy for non-Microsoft products.
2. Draft the full plan and meter design.
3. Build the fulfillment integration (landing page, webhooks, metering).
4. Create the transactable offer and test it in preview.
5. Go live.
6. Submit the Teams app linked to that offer.

Want me to turn this into a checklist with the Partner Center fields for each step?