# Northvane AppExchange plan: board slides, tightened and stress-tested

I couldn't make either slide airtight as written. Neither claim can be defended in front of a board yet.

## What to do first (about 2 hours)

1. Find the source for "~80% ranking weight". Check whether it is Salesforce documentation or a third-party blog.
2. Find the source for "+89% conversion". Check whether it came from AppExchange data or a generic e-commerce study.
3. Pull your own listing numbers: monthly visitors, visit-to-lead rate, lead-to-close rate, and ACV.
4. Replace the bracketed fields below with those numbers.

## Why the current wording fails

**Slide 1: "~80% of ranking weight"**
- To my knowledge, Salesforce does not publish AppExchange ranking weights. An exact-looking 80% will draw "where does that come from?" from the first skeptical director.
- "Highest-leverage move" is a comparison, and the slide doesn't show what it is compared against. Reviews, install count, and category placement are plausible competing levers.
- Ranking is also not conversion. A better title can raise impressions without fixing a 3.9-star listing that visitors reject on sight.

**Slide 2: "3.9 → 4.4 drives +89% conversion, worth ~$400K"**
- **+89% is the weakest number.** Rating-to-conversion lifts in the public literature come mostly from consumer e-commerce. A B2B enterprise listing behaves differently, and a 0.5-star jump is not a documented +89% anywhere I can point you to.
- **The review math is the strongest point in your favor, and the draft omits it.** Your 47 reviews average 3.9, so they hold about 183 stars in total.
  - New 5-star reviews needed to reach 4.4: **about 40**, since (183.3 + 5n) / (47 + n) = 4.4 gives n ≈ 39.2.
  - If new reviews average 4.5 instead, you need about 235.
  - After 24 months, 47 reviews works out to roughly 2 per month. At that pace, 40 more reviews takes about 20 months. The target is a review-velocity problem, not a rating problem.
- **$400K has no visible arithmetic.** "At current traffic" hides every input. A board will ask to see the chain.
- **The two slides compete.** Slide 1 says titles are the biggest lever. Slide 2 says ratings are. Pick one headline lever, or present them as sequenced.

## Replacement slides (defensible versions)

**Slide 1 — Discoverability**

> **Title: Our listing is easy to miss. A rewritten title and subtitle is the cheapest first fix.**
> - Today: [rank / position] for "[target search term]" in [category].
> - Change: rewrite title and subtitle around the [N] terms buyers actually search.
> - Cost: [X] days of effort, no spend.
> - Measure: impressions and click-through rate, 30 days before vs. 30 days after.
> - Success: [target]% more listing views. We will report results either way.

Do not cite a ranking weight unless you can source it. If you can, add the source in a footnote. If you can't, drop the number.

**Slide 2 — Rating and conversion**

> **Title: At 3.9 stars from 47 reviews, our rating costs us deals. Fixing it takes about 40 new 5-star reviews.**
> - Gap: 3.9 → 4.4 needs about 40 new 5-star reviews. We averaged about 2 per month over two years.
> - Plan: in-app and CS-led review requests to [N] active accounts, targeting [X] reviews per month.
> - Timeline: [N] months at the target rate.
> - Value (scenario range, not a forecast):

| Scenario | Conversion lift | Added ARR |
|---|---|---|
| Conservative | +[10]% | $[A] |
| Base | +[25]% | $[B] |
| Upside | +[45]% | $[C] |

The scenario values are placeholders. Replace them with a lift range you can source or measure.

> - Assumptions are on the appendix slide.

## Appendix slide: the ARR model

ΔARR = monthly listing visitors × visit-to-lead rate × lift × lead-to-close rate × ACV × 12

Fill in each term with a Northvane number, with its source in the footnote. A reverse check shows how demanding your original figure is: $400K in new ARR at an ACV of [X] means [400K ÷ X] additional closed deals per year.

## Questions the board will likely ask

- **Where does the 80% come from?** Answer: [source], or "directional, so we're testing it."
- **Why 4.4 and not 4.0?** Answer with the reviews-needed math above.
- **What if we get the reviews and conversion doesn't move?** Answer: we run a 60-day pre/post check and stop spending if the lift is below [threshold].
- **Is the rating the cause, or are bad reviews a symptom?** Read the low-star reviews first. If they cite product gaps, review solicitation alone won't lift the rating.

## Caveat on my own inputs

I haven't seen your traffic, conversion, or ACV data, so every bracketed figure is yours to supply. I also can't confirm what Salesforce publishes about ranking. Verify that claim against their documentation before the meeting.