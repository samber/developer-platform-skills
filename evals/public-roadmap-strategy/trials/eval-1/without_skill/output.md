# Lattivo public roadmap: design

## Decisions to make first

1. **Dateless.** 3 of 9 promised items slipped last year (33%), so no future date is credible. The page uses Now / Next / Exploring. Dates appear only on shipped items, linked to the changelog.
2. **Staffed gate.** An item enters "Next" only if a named team has capacity booked. SSO group sync would be "Exploring" today. The page makes that visible, and this gate stops the March-SSO problem from recurring.
3. **No rep script, a paper gate instead.** Your VP Sales won't sign a rule on what reps say, so don't ask for one. Ask for a rule on contracts, which is not speech:
   - Any roadmap dependency in an order form, side letter, RFP answer or security questionnaire goes through product sign-off.
   - Your MSA's entire-agreement and future-functionality clauses should already make verbal promises non-binding. Counsel must confirm that.
   - Give reps something to offer: "need more than the page? Product runs an NDA roadmap briefing."
   - Revisit after two quarters if off-page promises keep surfacing (see Metrics).
4. **Not literally Stripe's.** As far as I know, Stripe's public surface is mostly a changelog, versioned APIs and preview labels, not a dated item list. Tell the CEO "like Stripe" means credibility from shipped history, not a promise list.

## Page structure

One page next to the changelog and docs, with a short header: "Direction, not commitment. Dates are deliberately absent."

| Section | Contents | Cap |
|---|---|---|
| Recently shipped | Last 90 days, each linked to its changelog entry | 6 |
| Now | Staffed and in build | 4 |
| Next | Staffed, scheduled, not started | 4 |
| Exploring | Problem validated, no staffing or design yet | 6 |
| Moved / dropped | Items that left Now or Next, with a one-line reason | rolling 6 months |
| Sunsetting | Links to your existing deprecation process | as needed |

Caps keep it to roughly 10 to 14 items and keep the monthly edit small.

**Entry template**
- Customer problem, in one sentence, with no solution detail.
- Status.
- "Last reviewed" date.
- "What this does not include", one line (this is where scope slips get caught).
- A feedback link.

**Never on the page:** dates, named customers, deal sizes, pricing, or "by Qx".

## Preview phases

Engineering's Slack "beta" tag stops counting. A feature may be called a preview only if it meets the entry criteria.

| Label | Entry criteria | Terms |
|---|---|---|
| Private preview | Invited accounts, product-approved | No SLA, may change or be removed on short notice |
| Public beta | Documented, opt-in, on the changelog | No SLA, 30-day notice of breaking change |
| GA | Documented, supported, in the SLA | Standard deprecation process |

Ask counsel to confirm both the click-through terms and the MSA exclude preview features from SLA and deprecation guarantees. If they don't, amend the click-through now. The 60 MSAs need only be checked, not re-papered.

## Feedback without a voting board

- Add a "Tell us what you need" link on the page that goes to a support form with a roadmap tag.
- Support tags requests by item or by new problem.
- Each month, count the tags per item as one input into the roadmap. Do not publish the counts.
- Each quarter, publish "What we heard" as three lines on the page.
- Skip the voting board. With about 1,100 self-serve accounts and no moderation capacity, it would create expectations you can't service.

## Monthly routine (4 hours)

| Time | Task |
|---|---|
| 60 min | Reshuffle the internal roadmap as you do today. Tag each item `public: yes/no` and apply the staffed gate. |
| 45 min | Update the page. Log every move in "Moved / dropped". Never delete silently. |
| 45 min | Triage the support tags. |
| 30 min | Deal-desk sign-offs and roadmap-briefing requests. |
| 30 min | Check shipped items against changelog links, then publish. |
| 30 min | Buffer. |

The page is regenerated in the same sitting as the internal reshuffle, so the two never drift apart. A **moved** item is one that left Now or Next without shipping. Count them, because that count is your slip metric.

## Launch plan (target: end of November 2026)

**Launch month costs about 10 to 12 hours, not 4.** Borrow help from docs or product marketing, or move the date.

1. **By Nov 1.** Audit every promise already made:
   - Search the CRM and email for roadmap language.
   - Pull the 9 items from last year.
   - Pull the two "SSO group sync by March" deals.
   - For each, check whether it is in writing and what the contract says.
2. **By Nov 8.** Counsel reviews the disclaimer and the preview and entire-agreement clauses. Draft disclaimer: "Forward-looking and subject to change. Not a commitment. Not part of any agreement. Purchasing decisions should not rely on it."
3. **By Nov 15.** Fix the two SSO deals before the page goes live, because the page will expose the gap. You or the CEO talk to those customers and reset expectations. Check first whether SSO is written into either contract.
4. **By Nov 20.** Draft the page, tag the preview phases, and ask engineering to stop using ad hoc "beta".
5. **By Nov 24.** Brief sales: what the page is, what the NDA briefing is, and what goes through the deal desk. Position it as help, not a gag.
6. **By Nov 30.** Publish with a changelog entry.

## Metrics (review at 6 months)

- Slip rate of Now items. Baseline 33%, target under 15%.
- Off-page promises found at deal desk. Target zero in the second quarter.
- NDA briefings requested.
- Support tags per quarter.
- Percentage of shipped items that were previously on the page.

## What I'd push back on

- **The VP's position.** Without a speech rule, reps can still promise anything. The deal desk catches written commitments but not verbal ones. If the metric above stays nonzero, ask the CEO, who set the goal of "one page for everyone", to own the rule instead of your VP.
- **A dated roadmap.** With a 33% slip rate, dates will become the next batch of broken promises.
- **Legal.** A disclaimer helps but doesn't override a rep's written promise. I'm not a lawyer, so confirm the clause wording with counsel.

## Open questions for you

1. Is SSO written into either of the two deals? That decides how urgent step 3 is.
2. Who can cover the launch-month hours?
3. Where does the page live (docs site or marketing site), and who can publish there without an engineering ticket?