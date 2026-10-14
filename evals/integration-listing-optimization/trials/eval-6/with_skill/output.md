# Fernlight launch: upload checklist for Atlassian Marketplace and Shopify App Store

**Answer: the kit can't be used as-is on either marketplace.** Next action: cut a 30-second Atlassian video, cut images 1 and 2, strip the badge from images 3–6, and re-export for Atlassian at 1840×900.

The skill says to interview first. I skipped that to give you the checklist now, so the "Assumptions" section below lists what I assumed. Specs come from the skill's reference file, which warns that both platforms change listing rules often. I did not check the live docs, so re-verify each spec before you submit.

## Why the kit fails

| Asset | Shopify | Atlassian | Fix |
|---|---|---|---|
| Video, 2:40 with voiceover, logos, "from $19/mo" card | ✅ Fits the 2–3 min ceiling and allows promo tone. ⚠️ Screencast must be ≤25% of runtime. ⚠️ The price card and logos are unverified. | ❌ Ceiling is ≤30 s, function demo only, anti-marketing tone. | Two cuts, below. |
| Image 1: marketing homepage | ❌ Not an in-UI product shot. Likely shows browser chrome and a pricing claim. | ❌ Same problem. | Drop it. |
| Image 2: logo on gradient | ❌ Shopify hard-rejects logo-only images. | ❌ Not product proof. | Drop it. |
| Images 3–6: product views with 5-star badge | ⚠️ Review claims baked into images are a common ban. | ❌ Same ban. A rating claim also contradicts the platform, which shows no stars until 10 reviews. | Re-export without the badge. |
| 1600×900 export | ✅ Matches Shopify. | ❌ Atlassian wants 1840×900. | Re-export a second set. |

## Shared prep (do once)

1. ⬜ Strip the 5-star badge from images 3–6.
2. ⬜ Cut images 1 and 2 and replace them with in-UI shots of Fernlight's value. That leaves 4 valid images, which fits the 4–6 range for a gallery.
3. ⬜ For each marketplace, order the gallery as hero → key differentiator → most-loved feature, then supporting shots. The first three images do most of the work. This ordering rule comes from consumer app stores, so treat it as an analogy.
4. ⬜ Add a caption to every image.
5. ⬜ Crop out any sensitive data and any browser chrome.
6. ⬜ Check that no two images are duplicates. Shopify enforces this.
7. ⬜ Get written permission for each customer logo before it appears in any video.
8. ⬜ Collect your buyer's real search words from support tickets and sales notes. They feed the title and summary fields on both marketplaces.
9. ⬜ Submit both listings early. Both marketplaces review before go-live, and I have no lead-time figures. Confirm timelines in each console, then work back from the same-day date.

## Atlassian Marketplace checklist

**Video**
1. ⬜ Cut a version of 30 seconds or less.
2. ⬜ Show how the product works. Remove the promo voiceover, the customer logos, and the "from $19/mo" card.
3. ⬜ Keep the tone neutral and descriptive.

**Screenshots**
4. ⬜ Re-export at **1840×900**. Do not upload the 1600×900 files.
5. ⬜ Upload the 4 in-UI images with captions and no badge.

**Text fields**
6. ⬜ Write the **summary**, capped at 250 characters. It is the main search string, though that is practitioner inference rather than official. Put your buyer's words in it.
7. ⬜ Pick up to 2 of the 10 categories. Revisit them later, because stale categories get downgraded.

**Reviews**
8. ⬜ Expect no star rating at launch. A listing needs 10 reviews before stars display.
9. ⬜ Rely on the platform's auto-invite, sent 30 days after purchase. Copy the review link for your own sanctioned asks.
10. ⬜ Plan one public reply per review.
11. ⬜ Offer no incentives, and no reviews from your own team or from review swaps. Penalties include delisting.

**Analytics**
12. ⬜ Open the vendor console and confirm you can see the view → evaluation → purchase funnel. Paid apps see a lag of up to 24 hours.

## Shopify App Store checklist

**Video**
1. ⬜ Keep the 2:40 cut, since it fits the 2–3 minute ceiling.
2. ⬜ Confirm the screencast footage is ≤25% of runtime.
3. ⬜ Check the current rules on logos and prices in video before upload. If you can't verify them, cut the "from $19/mo" card. It also risks conflicting with your Shopify billing setup.

**Screenshots**
4. ⬜ Upload the 1600×900 set: 4 unique in-UI images, captioned, with no badge, logo-only image, or pricing text.

**Text fields**
5. ⬜ Name the app **brand-first**, like "Fernlight [function]". Shopify instructs this, and it is the opposite of Atlassian-style keyword-first titles.
6. ⬜ Write a subtitle with your buyer's words. Name plus subtitle carry roughly 80% of keyword weight, but that figure is one tracker's estimate. Plan on direction, not magnitude.
7. ⬜ Add up to 5 search terms. Each must be a complete word or concept, like "email marketing", not "email marketing for leads".
8. ⬜ Choose your categories, then add up to 25 structured features per category.

**Reviews**
9. ⬜ Collect reviews through the Reviews API.
10. ⬜ Put in-product asks at natural pauses, never blocking the user's workflow, with an opt-out.
11. ⬜ Ask after positive support interactions.
12. ⬜ Send an unconditional email ask to all active users. Practitioners report a 5–10% conversion.
13. ⬜ Offer no incentives of any kind. Shopify publishes a penalty ladder that ends in Partner-account termination.

**Analytics**
14. ⬜ In Distribution → Manage listing → Tracking, wire your GA4 Measurement ID and Meta Pixel by hand. It does not happen automatically. This gives you the full view → install-click → install funnel.
15. ⬜ Check the partner dashboard for installs, uninstalls, and revenue.

## After launch

1. ⬜ Name one owner for each listing.
2. ⬜ Refresh each listing every 30–60 days.
3. ⬜ Watch uninstall rate, because churn hurts ranking and a better listing can't outrun it.
4. ⬜ Re-verify both marketplaces' rules each cycle.
5. ⬜ Treat lifts under 2% in any before/after comparison as noise.

## Assumptions and open questions

- I assumed Fernlight is an unknown entrant, so I did not treat the brand-only title as a deliberate choice.
- I assumed both listings are pre-submission. Tell me if either is already live.
- I assumed you have no existing reviews. If you do, send the count, average, and recency of the newest ten.
- I don't know whether Fernlight has a badge or security review in progress (Built for Shopify, Atlassian Cloud Fortified). Built for Shopify is the only badge with an official ranking boost, but earning it takes a quarter or more, so it is not a launch-day item.
- Please send your buyer's search words so I can draft the Atlassian summary and the Shopify subtitle and search terms.