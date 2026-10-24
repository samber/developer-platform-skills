**Decision: cohort is 4 accounts, not 18. Coldspring is in. Brightmoor, Routeweave and the "first 15" are not.**

Next action: send the screener (below) to all 40 waitlist accounts today. About 1 hour of PM time.

## Why 18 fails

- Total capacity is 9 h/week (6 engineer + 3 PM).
- Program overhead takes about 3 h/week: changelog, flags, legal loop, instrumentation.
- That leaves about 6 h. Spread over 18 accounts, each gets 20 minutes a week.
- The skill budgets several hours per active partner per week.
- Even at the bare minimum, about 1.2 h per partner gives a ceiling of 5 accounts.
- Plan 4 seats and keep 1 in reserve. Take the lower of the capacity cap and the shape's typical size.

## Shape

Private preview, run hybrid. Make the first sessions design-partner style on the one open question in the `crew-dispatch` shape.

- Confirm with me: is the request and response shape decided, or still open?
- If it is open (it is a new resource model), promote to design partners. At 3-5 accounts that size already fits.

## Cohort

| Seat | Account | Verdict | Reason |
|---|---|---|---|
| 1 | Coldspring Services | **In**, conditional | Ticket #4471 is evidence of the exact problem. Sprint is booked, so a real build sits in the window. |
| 2-4 | Waitlist, screened | **Open** | Admit only accounts that score no `-` on rows 1-3 of the rubric. Not the first 15 by list order. |
| 5 | Reserve | Held | Replaces a stalled seat, or goes to Routeweave in wave 2. |
| none | Brightmoor Mechanical | **Out** | Fails rows 1-3. |
| none | Routeweave | **Out of wave 1** | Fails row 7 and breaks capacity. |

**Coldspring conditions (all before enrollment):**
1. Name a technical engineer who will attend the biweekly sessions.
2. Check that ticket #4471 matches the `crew-dispatch` shape, not just the pain.
3. Sign the pre-GA terms.
4. Sign a data addendum if they send live jobs. Dispatch payloads carry technician names and customer addresses, which is personal data by nature. Default is synthetic or test data. Live data needs a per-account addendum that legal signs.
5. Watch traffic share. Over about one third of beta traffic breaks the concentration rule.

**Brightmoor Mechanical:**
- Row 1 fails: "sounds interesting" is not evidence.
- Row 3 fails: the account rep collects feedback, so there is no named engineer.
- Row 2 is unknown.
- The $400k renewal is the reason for access. That is access as a closing tool, and these accounts rarely activate.
- Substitute offer: design review under NDA, sandbox with synthetic data, the GA and freeze dates, first place in the next wave.
- Re-score only if Brightmoor names an engineer, shows a workaround in their code, and plans a build in the window.
- Even then it needs every entry criterion plus the data addendum.
- Tell sales not to tie the renewal to preview access.

**Routeweave:**
- It white-labels you to about 300 HVAC shops. That multiplies support and notice budget, and a kill notice must reach those shops through Routeweave.
- Your 9 hours cannot cover that.
- It could also dominate beta traffic.
- Ask for the evidence: a ticket or workaround, a named engineer, and a written plan to notify its shops.
- With that, it is a wave-2 or public-preview candidate.
- If it does enroll, bar any downstream exposure of the preview in writing.

## Workflow fix: all-HVAC is a risk, not a plus

Same persona with different workflows is what makes cross-partner patterns real. Five HVAC shops on the same two-tech-per-job flow test one workflow five times. You would freeze a shape that fits HVAC and breaks elsewhere.

- Admit at most 1 two-tech HVAC account from the waitlist, with Coldspring counting as one if it fits that workflow.
- Fill the other seats with different workflows: 3+ crew, multi-trade jobs, solo or on-call techs.
- Search support tickets and issues for dispatch complaints before leaning on the waitlist. Those accounts have evidence by definition.

## Waitlist screener (send to all 40)

Four questions, all required:
1. What dispatch problem do you have today? Link a ticket or describe your workaround.
2. Who is the engineer who will attend biweekly sessions? Give a name.
3. When will you build against `crew-dispatch`? Give dates inside the window.
4. Would you pay for it at GA?

Scoring: `+`, `0` or `-` per row, using the playbook rubric. Rows 1-3 must have no `-`. Row 4 rewards a workflow the cohort lacks.
- No answer means no seat.
- Everyone else gets the waitlist reply.

Time: about 2 hours to score the replies.

## Program terms to set before anyone enrolls

These are proposals. Change any figure you will not honour.

| Item | Proposal |
|---|---|
| Cadence | Kickoff call, then biweekly office hours, plus one private channel |
| Channel owner | Named person, reply within 2 business days |
| Activation event | First production-shaped dispatch created through the API for a real job |
| Enrollment closes | Week 2 |
| Mid-point activation check | Week 6. Floor: 3 of 4 enrolled accounts activated. |
| Contract freeze | Week 9 |
| Exit review | Week 12 |
| Extension | One only, at most 6 weeks, with the failed criterion written down |
| Flag expiry | Alerts the owner on the exit date. It never disables access. |
| Access key | Per organization, never a percentage rollout |
| GA needs | At least 1 account on production traffic with a signed production exception, no open blocker, SDK and docs ready, GA pricing set |
| Kill if | Fewer than 3 accounts activated at the exit review, or the problem statement is disproved |

I don't know your GA target date. If it is closer than build time plus 8-12 weeks, keep the hybrid and compress these dates backward from GA.

## Gate: sign these before the first account enrolls

- [ ] Program owner named, with a backup.
- [ ] Stage contract written (all 11 rows) and published.
- [ ] Wire mechanism chosen: version suffix, separate path, or per-org opt-in.
- [ ] SDK pre-release channel exists. This blocks any account that uses SDK methods. Partners on raw HTTP may enroll without it.
- [ ] Design review passed at beta level.
- [ ] Security review: auth scopes, authorization checks, abuse limits.
- [ ] Legal signs the pre-GA terms, the data carve-out or addendum, and a clause that overrides MSA or DPA coverage of "all services".
- [ ] Support channel staffed at the stated response time.
- [ ] Activation event instrumented. Production-use detection running.

## Messages

**Brightmoor, via sales (send as-is):**

> Subject: Crew dispatch - early engagement for Brightmoor Mechanical
>
> Crew dispatch reaches GA on or about [date]. Its contract freezes on [date]. Preview access is limited to accounts with a planned integration and a named engineer. What we can offer now: a design review with your integration architect under NDA, a sandbox with synthetic data, and first place in the next enrollment wave.

**Everyone else on the waitlist:**

> Thanks for your interest in crew dispatch. The current cohort is full. We open the next wave or public preview around [date] and will write to you then. Meanwhile: [docs link].

## Open questions for you

1. Is the `crew-dispatch` shape decided or still open?
2. What is the GA target date?
3. Do Coldspring and Routeweave have named engineers?
4. Does legal exist to sign a data addendum, and how fast?

Next: send the screener to the 40 and the Brightmoor substitute to sales today.