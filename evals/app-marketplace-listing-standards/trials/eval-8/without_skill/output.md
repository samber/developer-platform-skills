# Pre-publish check: Quillrock listing standards

**Verdict:** the OAuth section is fine to include if you split it. ⚠️ The hidden demo-video penalty should not ship as planned: disclose it.

## 1. OAuth scope audit and re-review triggers in the same doc

Security's "one page for partners" goal is reasonable. Two things to check first.

**Keep the partner-facing rules in. Keep the detection mechanics out.**

| Publish | Keep internal |
|---|---|
| Which scopes need justification | How you detect scope drift or abuse |
| Least-privilege expectation | Audit sampling, thresholds, tooling |
| What triggers a re-review | Reviewer checklists and escalation paths |
| Review timeline and what happens to the live listing meanwhile | Anything that would let a vendor game the check |

Partners need to know the rules. Publishing how you catch violations helps an attacker avoid them.

**Make the re-review triggers concrete and testable.** Vague wording like "significant changes" gives partners nothing to plan around. For example:

- A new scope, or any scope upgrade (read → write, user → admin), forces re-review before the update goes live.
- Removing scopes never triggers re-review.
- Changes to the redirect URI, the data-handling declaration, or the publisher entity also trigger it.
- State what happens to the existing listing while the review is pending. Options are: the old version stays live and the update is held, or the listing is paused. Pick one and say so.
- State the review SLA. Partners will ask.

**Structure suggestion:** put the doc in two layers. Layer 1 has the listing requirements (content, media, support, pricing). Layer 2 is a "Security and permissions" section with a short summary at the top, so partners who only need the rules can stop there.

## 2. Ranking down listings without a demo video, and not saying so

**Problem 1: it defeats its own purpose.** You want vendors to "get the hint". A penalty nobody is told about is not a hint. Vendors will see lower traffic, blame the algorithm or the product, and file support tickets or churn. The nudge only works if they know the cause.

**Problem 2: trust and legal exposure.**
- Undisclosed ranking factors that disadvantage business users are what transparency rules target. If any of your partners sell into or operate from the EU, the Platform-to-Business Regulation (EU 2019/1150) requires platforms to describe the **main parameters** of ranking in their terms. A demo-video penalty plausibly qualifies. Have legal confirm whether it applies to you.
- Even where no law applies, a hidden penalty tends to leak, through partner comparisons or a reverse-engineered ranking. "The marketplace secretly punished us" is a worse story than "the marketplace asks for a demo video".
- Your doc is titled as listing *standards*. If the standards say one thing and ranking does another, the doc is misleading by omission.

**Recommendation:** disclose it as a ranking signal. You lose nothing, because disclosure is what produces the behavior you want.

Suggested wording for the doc:

> **Search ranking.** Search results are ranked by relevance to the query and by listing quality signals, including install and retention performance, review ratings, and listing completeness. Listings with a demo video are treated as more complete and rank higher than otherwise-equivalent listings without one. We may adjust these signals over time.

Notes on the wording:
- Frame it as a **boost for completeness**, not a penalty. Mechanically it is the same, but it is more accurate if the effect is a tiebreaker rather than a heavy demotion.
- You don't have to publish weights or exact formulas. Naming the factor is enough.
- Make sure the effect is proportionate. A video should not outrank a clearly better-matching app.

**Before you publish, also check:**
- Does the ranking change apply to existing listings, and how long do vendors get to add a video? A grace period (30 to 60 days) avoids an overnight traffic drop.
- Are there app types where a video is impractical (APIs, background integrations)? Decide on an exemption or an alternative asset, such as a screenshot walkthrough.
- Have you measured whether demo videos actually correlate with install quality? If they don't, the signal is arbitrary and harder to defend.

## Open questions for you

1. Does Quillrock have EU-based partners or end users? That decides how urgent the ranking disclosure is.
2. Should the pending-review state keep the old version live or pause the listing? That is a security and product call.
3. Is the video signal a tiebreaker or a heavy factor? That decides whether "boost" wording is honest.