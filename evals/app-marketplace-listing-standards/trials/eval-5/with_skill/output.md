# Tidewell "Certified Listings": certification body, badge placement, and lapse handling

I followed the `app-marketplace-listing-standards` skill. It says to interview first. I haven't, so the defaults below rest on assumptions, listed at the end.

## 1. Which certification body? None exists. Don't get one.

- **No ISO, IAB or equivalent body certifies marketplace listing quality.** The skill's research found none across eight benchmarked marketplaces. Every real badge program is operator-proprietary: Atlassian Cloud Fortified, Google CASA, HubSpot App Certification and Salesforce badges.
- **ISO 27001, SOC 2, ISO 9001 and CASA certify an organization's posture, not a listing.** Auditing Tidewell against ISO would not make "Certified Listings" true.
- **"Certified Listings" implies an external certification, which is an unverifiable claim.** The skill's hard rule is to never claim or imply one.

Recommended positioning, named as Tidewell's own and built from three parts:

| Claim | Basis |
|---|---|
| Security | Your own security review, plus recognized attestations. Vendors can show SOC 2, ISO 27001 or CASA on their trust section. If Tidewell wants an audit for itself, SOC 2 or ISO 27001 covers Tidewell's own operations. |
| Accessibility | WCAG 2.2 AA for listing content. |
| Content | Your own published listing rubric. |

For the homepage, change the copy to something like **"Security-Reviewed by Tidewell"** or **"Tidewell Verified"**. Only listings that currently hold the badge may carry it. A blanket "Certified Listings" line is false for every listing that doesn't.

## 2. Where each item shows on a listing

Eligibility belongs to the review process (`app-marketplace-review`). Display rules belong to the listing rulebook.

| Surface | Contents | Rule |
|---|---|---|
| **Dedicated trust tab** (default) | Data-storage location, earned Tidewell badge with review date and status, vendor compliance certifications. | Physically separate from the marketing copy. |
| **Inline chip** | Badge next to the listing name in search and browse. | Cheap complement only. It asserts trust but doesn't substantiate it, and it links to the trust tab. |
| **Vendor-embeddable badge** (your open question) | A badge on the vendor's own website. | Optional. See below. |

**Vendor-embeddable badge: optional, but it's marketing, not trust.** If you offer it, ship a brand-usage rulebook modeled on Google's:

- Use as provided and never alter.
- Clear space of one-quarter of badge height.
- Size equal to or larger than other marketplace badges shown alongside it.
- Mandatory link back to the listing.
- Caption "from Tidewell", not "on Tidewell".

Because the link back leads to the live listing, a buyer sees the current status there. A static image copied onto a vendor's site would keep showing a lapsed badge. The skill doesn't prescribe a hosted or dynamic embed, so that part is my inference. If you can build it, serve the image from Tidewell so it disappears on lapse.

**Don't mix the two badges.** The Tidewell security badge and the "available on Tidewell" promo badge are different things. Don't let the promo badge imply security review.

## 3. When a vendor's badge lapses

Write a currency rule with a stated grace period. Proposed sequence:

1. **Notice at renewal minus N days.** Tell the vendor what is due.
2. **Grace period.** I suggest 30 days. The skill requires a stated grace period but gives no number, so this is my pick. HubSpot gives about 60 days for version migration, which you could use instead.
3. **At grace expiry**, the chip and trust-tab badge come down.
4. **The listing stays live and uncertified.** This follows HubSpot's model. Don't delist, because the content rules (not the badge) govern removal.
5. **The trust tab shows the status** as "lapsed" or "not currently reviewed", not a blank.
6. **Vendor must remove any off-site badge.** The link back to the listing shows the true status in the meantime.
7. **Re-application path.** HubSpot imposes a six-month wait after falling below its threshold. Decide whether you want a cooldown.

**Automation:** manual takedown is the default. Wire badge display to review-program eligibility data so lapses disappear automatically once badges carry quantitative, lapsable thresholds. It's the highest-effort option but the only one that guarantees badges stay current.

**Notice runway:** any new badge requirement applied to already-listed apps needs advance notice, so vendors aren't caught by retroactive rule changes.

## 4. Decisions for you

- Rename the homepage claim away from "Certified Listings".
- Pick a grace period.
- Decide whether to offer the vendor-embeddable badge, and if so whether it's hosted.
- Decide whether to add a re-application cooldown.

## Assumptions I made

I skipped the skill's interview, so these are unconfirmed:

- You have a hybrid or certified-tier curation model.
- Vendors maintain their own listings.
- Badges are lapsable and recertified on a cycle.
- No hard launch deadline.

If any is wrong, tell me. The display rung and the lapse automation depend most on the badge-threshold question.