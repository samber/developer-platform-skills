**Next action:** cut the cohort from 18 to 12 and run a 5-question screen on the waitlist this week. About 20 minutes to write the form, then 1 hour to score replies.

## Verdict

Not final as planned. Four problems, ranked:

1. **Capacity.** You have 9 h/week combined.
   - 18 accounts leaves 30 min each per week.
   - Onboarding an API product takes about 1.5 h each. That is 27 h up front, or 3 full weeks of your combined time.
   - A 30-min call per account every 2 weeks costs another 4.5 h/week.
   - 12 accounts, staggered, is the ceiling.
2. **"First 15" selects on signup order, not fit.** Early signup measures enthusiasm.
3. **Uniform HVAC cohort is a weakness, not a plus.** 15 two-tech HVAC shops tell you the same thing 15 times. You learn nothing about solo techs, 3+ crews, other trades, or multi-day jobs. You risk shipping a resource shaped only for two-tech HVAC.
4. **Two of the three sales accounts carry hidden costs.** Details below.

## The three sales accounts

| Account | Decision | Why |
|---|---|---|
| Coldspring | **In. Anchor.** | Real problem (#4471), sprint booked, will integrate fast. |
| Brightmoor | **Conditional seat** | "Sounds interesting" is weak signal. A rep relaying feedback filters it. A preview bug could hit a $400k renewal. |
| Routeweave | **Scoped seat** | A reseller is not an end user. White-label exposure reaches 300 shops, and unfinished work ships under their brand. |

**Coldspring terms**
- Reserve 2 of the 6 engineer hours per week for them.
- Confirm sprint dates against your readiness date. If the resource is not ready by their sprint, they lose the sprint and you lose goodwill.
- Check their workflow. If it differs from two-tech HVAC, they fill a diversity slot too.
- Say in writing: preview API may break, don't build prod on it.

**Brightmoor conditions**
- Condition: a named dispatcher or ops user joins a 30-min call by a set date. The rep may attend but not relay.
- If no user appears, they are a demo audience, not a cohort member.
- State in writing that the preview is separate from the renewal. Promise no GA date and no pricing.
- Open a shared Slack channel or email thread with their user. Do not route through the rep.

**Routeweave scope**
- One seat. Two or three shops that Routeweave nominates, with dispatch volume, as the real users.
- Resource enabled only on those sub-tenants. No white-label surface, no exposure to the other ~297.
- **Check first:** can you flag per sub-tenant? If not, enabling on the Routeweave tenant exposes all 300. Then defer them.
- Schedule a separate product-level talk about white-label later. That is a different conversation from the preview.

## Waitlist: 9 seats, chosen by screen

**Screening form (5 questions):**
1. Trade and typical crew size per job (1, 2, 3+).
2. Job types: single-visit or multi-day.
3. How do you dispatch today? (spreadsheet, another tool, own code)
4. Do you have someone who can call our API within 2 weeks?
5. Will you do a 30-min call every 2–3 weeks?

**Selection rule:** drop anyone who answers no to Q4 or Q5, then fill the seats below. Within a bucket, pick the best Q3 fit (current dispatch pain). Break remaining ties by signup order.

| Seats | Profile |
|---|---|
| 4 | Two-tech HVAC. This is your baseline for consistent signal. |
| 2 | Other trade (plumbing, electrical) with crews |
| 1 | 3+ tech crews |
| 1 | Solo or 1-tech |
| 1 | Multi-day jobs |

If a bucket has no qualified applicants, give the seat to the next-best HVAC. A gap in a bucket is itself a finding: your waitlist is narrower than your market.

## Final cohort: 12

- Coldspring (anchor)
- Brightmoor (conditional)
- Routeweave (scoped, 2–3 shops)
- 9 waitlist seats from the table above

**Waves:**
- **Wave 1, week 1 (8 accounts):** Coldspring, Brightmoor, Routeweave, plus 5 waitlist (2 baseline HVAC, 3 outside the baseline profile).
- **Wave 2, week 3 (4 accounts):** the rest of the waitlist seats, after onboarding docs absorb wave 1's questions.

The 31 other waitlist companies get a short email today: "Cohort full, next wave after preview; you stay on the list." Don't promise a date.

## Time budget at steady state (weekly)

| Who | Hours | Spend |
|---|---|---|
| Engineer | 2 | Coldspring |
| Engineer | 4 | Bugs and API questions for the other 11 |
| PM | 2 | About 4 calls (12 accounts, one call every 3 weeks each) |
| PM | 1 | Synthesis |

This is tight. Weeks 1–2 of each wave will overshoot. If wave 1 runs over, delay wave 2 instead of cutting call time.

## Run rules (write on one page)

1. One shared feedback channel per account. No intermediaries.
2. Preview terms: no SLA, API may change, no GA or pricing commitment.
3. Question to answer: does crew-dispatch fit crews other than two-tech HVAC?
4. Exit rule: if wave 1 produces zero feedback from a given account after 3 weeks, replace them.
5. Support SLA internal only: reply within 1 business day. Do not state externally.

## Open questions

These change the answer:
1. Can you enable the resource per sub-tenant for Routeweave?
2. Is the resource stable by Coldspring's sprint start? What is the date?
3. Does Brightmoor have a named dispatcher who will talk to you?
4. Are all 40 waitlist companies active accounts, or just email signups?

**Next:** write the 5-question form (20 min) and send it to the 40 waitlisted companies today.