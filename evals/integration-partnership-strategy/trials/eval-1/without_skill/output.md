# Threadline integration partner strategy, 2027

## Verdict

Your draft mixes four reasons for picking a partner: relationship, logo size, fashion, and competitor reaction. Only one of those is demand. The evidence you already have points at **payroll and HRIS**, and your draft barely covers it.

Recommended shortlist:

| # | Partner | Role | Commitment |
|---|---|---|---|
| 1 | **Gusto** | Lead partner | Full build, co-marketing, start Q1 |
| 2 | **Rippling** | Defensive and demand-backed | Full build after a 2-week validation |
| 3 | **Payroll/HRIS #3** (ADP, Paylocity, Paycor or similar, picked by data) | Close the payroll gap | Build after win/loss is split by vendor |
| 4 | **Slack** | Low-effort engagement channel | Self-serve build, no partnership slot |
| 5 | **Workday** | Gated option | Discovery only, no build until it passes a gate |

**Drop Notion.** Nothing in your data supports it.

## Why this order

**What the evidence says**
- About 12 lost or at-risk deals last quarter cited missing payroll integrations. That is your strongest signal, and it's tied to revenue.
- 40+ support tickets asked for Gusto sync. That is real, but it measures annoyance, not revenue.
- A competitor announced a Rippling integration in March. That tells you the market is moving, not that Rippling is right for you.

**What the evidence doesn't say**
- Nobody has shown that Slack, Notion or Workday would change a deal or retention outcome.
- The CRM partner-source field is empty, so you have zero data on partner-sourced revenue today.

## Each partner

**1. Gusto: keep, make it #1**
- It's the only pick backed by both customer demand (tickets) and a working relationship (the BD contact from May).
- The relationship is a tiebreaker here, not the reason.
- Their base is small and mid-sized businesses. Check that this matches your ICP.
- Next step: ask the BD contact about their integration program, certification timeline and co-marketing options.

**2. Rippling: keep, validate first**
- Competitor moves are a legitimate input, but a bad sole reason.
- Validation, 2 weeks:
  - Count win/loss mentions of Rippling by name.
  - Count how many open pipeline accounts and customers run Rippling.
  - Read what the competitor's integration actually does and whether customers cite it.
- If fewer than about 3 deals or accounts show up, demote it to the backlog.

**3. Third payroll/HRIS partner: choose by data, not by guess**
- Your ~12 payroll mentions are probably spread across several vendors, and I can't tell which from what you've given me.
- Tag each mention by vendor and rank by ARR at stake.
- Take the top vendor not already on the list. Common candidates for a scheduling product are ADP, Paylocity, Paycor and UKG.
- Reserve the slot until the tagging is done.

**4. Slack: do it, but not as a strategic partnership**
- The CTO relationship is real, but it isn't a reason to spend a partner slot.
- Slack's public API lets you build shift alerts, swap approvals and schedule publishing yourselves.
- Use the CTO's contact for the marketplace listing and a possible co-announcement.
- Scope it as a small product project and ask one metric of it: does Slack-connected usage improve retention or activation?

**5. Workday: option, not a commitment**
- It's the biggest logo, but it brings long enterprise sales cycles, a heavy certification process and a large integration-maintenance burden.
- At $14M ARR, one stalled Workday build can consume a whole team for a year.
- Gate to proceed:
  - At least 3 active enterprise opportunities, each with a named Workday requirement.
  - A customer or prospect willing to co-sponsor the build.
- Until then, spend only on discovery, such as a Workday marketplace review and a prospect interview.

**Notion: drop**
- "Everyone integrates with Notion" is a popularity argument, not a Threadline argument.
- Revisit only if customers or prospects ask for it.

## Fix the data first (weeks 1–2)

Without this, the 2027 plan is guesswork and you can't judge it afterwards.

1. **Tag win/loss notes by integration vendor.** Cover the last 2 quarters, and record ARR at stake per deal.
2. **Count distinct accounts behind the 40+ Gusto tickets.** If it's 40 tickets from 6 accounts, the story is different from 40 accounts. Add the ARR of those accounts.
3. **Make partner-source a required CRM field**, with a short dropdown list. Back-fill the last 12 months from sales memory for closed-won deals.
4. **Add an "integration requested" field** to the CRM and to support tickets, so demand gets counted going forward.

## Scoring rule for any future partner

Score each candidate 1–5 on these, and require a minimum bar on the first two:
1. Revenue or retention evidence from your own data. Required.
2. Overlap with your ICP. Required.
3. Build cost and ongoing maintenance.
4. Partner willingness: a program, a listing, co-marketing.
5. Competitive pressure.

Relationships and logo size go into #4 only. They can't rescue a candidate that fails #1 and #2.

## Sequencing

| When | What |
|---|---|
| Weeks 1–2 | Data cleanup. Gusto BD call. Rippling validation. |
| Q1 | Gusto build starts. Choose the third payroll partner. Slack scoped as a small project. |
| Q2 | Gusto launch plus co-marketing. Rippling build starts if it passed validation. |
| Q3 | Third payroll partner build. Workday gate review. |
| Q4 | Measure partner-sourced pipeline and retention, and set the 2028 list. |

## Success metrics to show the exec team

- Win rate on deals that cited a payroll gap, before and after each launch.
- Percent of customers with an active integration, and their retention vs. those without.
- Partner-sourced pipeline and closed-won ARR, from the new CRM field.
- Gusto-related support tickets, expected to fall after the launch.

## Decisions for the exec team

1. Do they accept payroll/HRIS as the 2027 theme, with Slack as the lightweight exception?
2. Are they willing to hold the Workday build until the gate is met, even though it's the biggest logo?
3. Will they fund the data cleanup in weeks 1–2 before locking engineering capacity?

## Assumptions to correct me on

- The ~12 payroll mentions aren't yet split by vendor, so I can't say Gusto accounts for them.
- I assumed an SMB and mid-market ICP, which fits Gusto and Rippling. If you sell mostly to enterprise, Workday and ADP move up and Gusto moves down.