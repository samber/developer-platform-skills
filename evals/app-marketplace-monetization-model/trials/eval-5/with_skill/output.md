# Teardown: small-developer fee waiver draft

**Verdict:** the shape is right, because a revenue-exemption tier is the skill's default rung. The mechanics break it in four places. Two are fatal: the manual application, and the per-entity allowance. Don't ship the draft as written.

I couldn't run the skill's interview one question at a time, so the assumptions I made are listed at the end. Verdicts 1 and 4 flip depending on them.

## Findings, worst first

### 1. 🔴 Per-entity $400K allowance is a loophole

- Each company entity gets its own allowance, so a large vendor can split itself into entities.
- Example: a $4M/year vendor pays $600K at 15%. Split into 11 entities at about $364K each, it pays $0. Forming an LLC costs a few hundred dollars.
- The precedent runs the other way. Apple aggregates associated accounts toward the cap. Atlassian aggregates per partner company. Shopify taxes very large developers at the full rate regardless.
- The draft's own motivation ("several apps under different entities") is a real case, but the fix is one allowance per vendor group.
- The split also defeats your anti-circumvention logic. Splitting entities reroutes revenue just as billing off-platform does.

### 2. 🔴 Manual application is the "opt-in waiver" failure mode

The skill names this directly. Apple's and Google's manual enrollment means a qualifying developer who misses the paperwork silently pays full rate. Your version adds delay on top:

- A vendor who applies the day after a quarterly review waits up to about 3 months for the review. The waiver then starts the following quarter. Worst case is about 6 months at 15%.
- Take a $300K/year vendor, which is $25K/month and $3,750/month in fees. Six months is about $22.5K overpaid, and nothing in the draft credits it back.
- New vendors are the worst case. They're the ones a small-developer waiver should attract, and they wait the longest. "Trailing 12 months" is also undefined for a vendor with 2 months of history.
- There are three different evaluation dates: application, review, and start of quarter. Any of them can be stale by the time the waiver applies.
- One partner-ops person on a quarterly cycle is also a single point of failure, with no stated criteria or appeal.

**Fix:** default eligible vendors in. The platform computes eligibility itself.

### 3. 🟠 Cliff at $400K

- The draft reads as 0% under $400K trailing and 15% on everything once over.
- A vendor at $399K pays $0. At $401K it pays $60,150. Two thousand dollars of extra sales cost about $60K.
- Rational responses are to stop selling at $399K, move billing off-platform, or split entities (finding 1).
- The sourced programs mostly avoid the cliff by exempting the first $1M and charging 15% only above it.
- Apple's revert-for-the-rest-of-year rule is the one cliff-like precedent. Your draft is silent on mid-quarter crossings entirely.
- A rolling trailing-12 window evaluated quarterly makes it worse. Vendors flip in and out of eligibility, and one lumpy annual prepay can disqualify them.

**Fix:** a marginal exemption, meaning 0% on the first $400K and 15% above.

### 4. 🟠 Waiver is unverifiable unless you are merchant of record

- The draft never states the merchant-of-record posture, and the skill says to fix that first.
- Under developer-billed, revenue is self-reported. An application form attesting "under $400K" can't be checked.
- That also means the 15% itself is an audited self-reported share, the skill's starved option.
- Charging 15% is the skill's promotion condition for marketplace-billed. Revenue is then netted at source, so the platform already knows each vendor's revenue.
- Under marketplace-billed, the form is unnecessary for eligibility. The waiver becomes a rate of 0 in the netting engine.

### 5. 🟠 Undefined terms and unwaived instruments

- **"Marketplace revenue"**: it's unclear whether this is gross, net of refunds, or net of tax and processing. Prepaid multi-year contracts need a rule too.
- **"Pays 0%"**: it's unclear which instruments this waives. Processing pass-through should stay as a separate labeled line, as Shopify does with its 2.9%. Review and registration fees should stay unless you decide otherwise.
- **Rail costs**: managed marketplace rails carry per-account and per-payout flat fees. At 0% share, you eat them on every small vendor. Run the unit economics per active developer.
- **The threshold**: $400K sits below the $1M anchor all sourced programs cluster around. That's allowed, but it needs data. What share of vendors and GMV does it cover? Level and tiers belong to `connector-marketplace-strategy`, so confirm it was decided there.

### 6. 🟡 Missing enforcement and notice

The skill's gate 2 requires every fee instrument to name its collection mechanism, its enforcement pair, and its notice commitment. The draft has none of these.

- No anti-circumvention rule or delisting path.
- No false-attestation penalty.
- No notice period for changing the threshold or rate.
- The waiver doesn't alter the tax split. Say so in the published terms.

## Rewritten waiver

1. **Prerequisite:** marketplace-billed posture. Revenue is netted at source before payout.
2. **Shape:** 0% revenue share on the first $400K of gross marketplace revenue per vendor group per calendar year, then 15%. Revenue is net of refunds, excluding tax and processing, and counted when charged. Annual reset is the default. Lifetime (Shopify's 2025 change) is a one-way tightening, so decide deliberately.
3. **Enrollment:** none. The netting engine applies it from a vendor's first dollar, so there's no review wait and no non-retroactive gap.
4. **Vendor group:** entities under common control (over 50% ownership or the same beneficial owner or parent). Signals include shared payout account, tax ID, partner account, and domain. One allowance covers all apps in the group.
5. **The one form that stays:** an affiliate disclosure, completed at onboarding. Misrepresentation revokes the waiver, back-charges via later payouts, and opens the delisting path.
6. **Partner-ops role:** handles exceptions only, such as group disputes and appeals, under a stated SLA. Add automated flagging of new entities clustering just under the cap.
7. **Unchanged:** processing pass-through, review and registration fees, hold windows, and the tax split.
8. **Commitments:**
   - An anti-circumvention rule with a delisting path.
   - Six months' notice for unfavorable changes; favorable changes take effect immediately.
   - A published schedule with worked examples.

Two points on the fixes. The marginal shape removes the cliff but not the entity-splitting gain, so the vendor-group rule is needed on top of it. With both, the most any group can save is $60K a year.

## Gates

Against the skill's three measurement gates:

- **Gate 1 (merchant of record stated):** the draft fails, and the rewrite passes.
- **Gate 2 (collection, enforcement, notice named):** the draft fails, and the rewrite passes.
- **Gate 3 (payout timeline and tax split published):** out of scope here.

Post-launch, track:

- Waiver coverage among eligible vendors. It should be about 100%, and a gap means the default-in rule failed.
- Net take against billing-ops cost.
- New-entity clustering just under $400K.
- Circumvention incidents.

## Assumptions and open questions

1. **Who bills the end customer today?** I assumed 15% means you move to marketplace-billed. If you stay developer-billed, finding 4 becomes the main problem.
2. **How many vendors and how much GMV sit under $400K?** This is the cost of the waiver, and I don't have it.
3. **Is there a back-book of off-platform billing vendors?** If so, a migration incentive might be worth adding.
4. **Do you have a legacy developer-billed population that can't migrate in one cycle?** That would keep the configurable posture alive for now.