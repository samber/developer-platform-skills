**Next action:** Don't put 30% in the deck. Put the plan below in it and take it to the exec team.

## Answer to "can we commit to 30%?"

No. Four reasons:

1. **It's a vendor's marketing claim.** I haven't seen the page, so I can't check it. You describe it as a vendor citing a figure with no method, sample or date. Treat it as a hypothesis, not a benchmark.
2. **A 10-15x lift over baseline is not a normal result for a listing rulebook.** Most of the funnel sits outside a listing's control: traffic quality, product-market fit, trial friction.
3. **"Click-through from listing to free trial" is not "listing views to trials".** That is a different denominator. Views to click, click to signup and signup to trial start multiply. Your 2-3% baseline and their 30% may measure different steps.
4. **A promise to partners is a debt.** Miss it once and every other number in the deck gets discounted.

Fernway has no number of its own yet. Until you have one, don't promise partners a conversion figure.

## What to promise partners instead

Promise three things you control:

- A **published definition** of the metric: views, trial starts, dedupe rules, bot filtering.
- A **measured baseline**, published by a stated date.
- A **range, not a point**, after the test. It is labeled as Fernway's own measurement. Partners get their own listing's number against the platform median.

Draft wording: *"Listings that follow the rulebook are measured against comparable listings that don't. We publish the baseline by [date] and the measured range by [date]. We don't guarantee a conversion rate, because it depends on your product and traffic."*

## Pass/fail bar for the rulebook

Set the bar **before** looking at data. Write it into the deck as pre-registered.

**What "good" means:** listings that follow the rulebook convert views to trial starts better than comparable listings that don't.

**Design (randomize, or the result is selection bias):**

1. Pick eligible listings. Randomly assign half to adopt the rulebook now. The other half wait and adopt later.
2. Don't let partners self-select. Volunteers are already your best listings, and that would fake a win.
3. Record at least 3 baseline periods for every listing before the change.
4. Run for a fixed window, then compare the two groups.

**Primary metric:** trial starts divided by unique listing views, per listing.

**Gates (all must pass):**

| Gate | Pass | Source of threshold |
|---|---|---|
| Conformance | At least 90% of treated listings pass the rulebook checklist at audit | self-set, hypothesis |
| Effect | Relative lift in the primary metric is at least +20% and the 95% confidence interval's lower bound is above 0 | +20% self-set, hypothesis. Choose it before the test. |
| Guardrail: quality | Trial-to-activation rate is not worse than control (within the CI) | baseline |
| Guardrail: harm | Support tickets and refunds per 100 trials are not higher | baseline |
| Data integrity | Both groups clear the minimum sample below | convention |

Fail any gate and the verdict is "not proven". It is not "mostly good".

**Sample size, back-of-envelope (80% power, 5% significance, 2.5% baseline):**

- To detect a +20% relative lift (2.5% to 3.0%): about **17,000 views per group**.
- To detect a +50% lift (2.5% to 3.75%): about **3,100 views per group**.
- Below about 30 trial starts per group, report the raw counts, not a rate.
- Listings are the real unit. Views from one listing are correlated, so analyze per listing (or cluster by listing). If you have only a few dozen listings, expect wide intervals and say so.

## What to put in the deck (6 slides)

1. **The ask and the decision.** "Approve the rulebook for rollout if it clears a pre-agreed bar."
2. **What we are not promising.** Show the vendor's 30% claim with its problems: no method, different denominator, 10x+ lift. Say it is excluded.
3. **The bar.** The gate table above. State that it is fixed in advance.
4. **The test design.** Randomized staged rollout, 3 baseline periods, and the window with dates.
5. **What partners hear.** The three promises and the draft wording above.
6. **Risks and blind spots.** Be explicit about these:
   - small listing count means wide intervals
   - bot and duplicate views must be filtered
   - "trial start" must mean one definition on every listing
   - seasonality or a launch spike during the window will contaminate it
   - the rulebook's effect may vary by category

## Open questions (they change the numbers above)

1. How many listings are eligible, and what are their monthly views? This sets whether a +20% test is feasible.
2. Is Fernway's real baseline known? Is the 2-3% yours or the vendor's?
3. Is the trial-start event instrumented per listing today?
4. When is the exec meeting? A window under about 4 weeks probably can't reach the sample size.

**Next:** Answer question 1 (listing count and views per month). I'll turn the sample-size table into exact test length and drop it into slide 4.