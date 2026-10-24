# Tessaro public roadmap: launch plan

I couldn't run the skill's interview because you asked for the finished plan. Where I assumed an answer, it is marked **[assumed]**. Please correct them. The ones that change the plan are in "Open questions".

## 1. Verdict on your four-part plan

| Your plan | Verdict | Why |
|---|---|---|
| Embed the voting board in the roadmap | ❌ Not at launch | A separate board is the most expensive feedback surface. It needs a named triage owner, and you triage "when you can". The board already holds 1,400 requests untouched for a year. |
| Auto-promote the 10 most-voted to "Next" | ❌ No | "Next" is a promise that sales, prospects and competitors will cite. Votes aren't an engineering decision. Raw counts skew toward free tier: 900 GraphQL votes, nearly all free-tier. |
| Shut the old board on launch day, restart at zero | ❌ Not as planned | A board closed with no notice and no archive is the Microsoft Office 365 UserVoice failure. Voters' expressed demand disappears and the expectation debt is written off. |
| Rank "Later" by vote count | ❌ No | Vote count may be one weighted signal, never the ranking. Weight by segment and account value. |

Your goal is that people see you listen. The plan below serves it without publishing promises you haven't made.

## 2. Diagnosis

- **Trigger [assumed]:** transparency and "show we listen". Sales promises aren't the trigger. If reps are promising unbuilt features, say so. That would make the sales citation rule a hard gate on launch.
- **Capacity:** one person, part-time, no triage owner. This is the binding constraint.
- **Buyers [assumed]:** mostly self-serve developers, plus some enterprise and regulated customers (payments).
- **Osborne risk:** announcing something like GraphQL can stall adoption of the REST API while buyers wait.
- **No proven payoff:** no independent evidence ties public roadmaps to trust or churn. Argue it on trade-offs only.

## 3. Candidate policies

**A. Horizon roadmap, locked items (recommended)**
- Undated buckets, read-only items, one feedback channel.
- Old board frozen read-only, then archived.
- Cost: about 3 owner-hours/month for 12 items, at a quarter hour per item per review, plus a few days of setup.

**B. Direction page and customer briefings**
- Narrative themes, "last reviewed" date and named maintainer, no item-level upkeep.
- NDA briefings for regulated customers.
- Pick this if you can't commit about 3 hours/month, or if the two review cycles in section 6 can't happen before launch.

**C. Interactive board embedded (your plan, cleaned up)**
- Horizon roadmap plus a live voting board.
- Ineligible today. It becomes eligible when a named triage owner exists, the backlog has been through a first pass, and a `not planned` state with reasons exists.
- Revisit in about two quarters.

Dated quarters are also out. They need release phases, a low slip rate, finance review of revenue recognition, and buyers who plan around your dates. I assume none of these hold yet.

**Recommendation: A.** It gives you the visible "we listen" moment with the least promise exposure. Ship it with a path to C.

## 4. Policy draft (Candidate A)

### Purpose
Show customers and prospects what Tessaro is working on and in what order. It is not a delivery commitment and not a vote tally.

### Vocabulary
Define each bucket by engineering state, not by date.

| Bucket | Meaning | Time label |
|---|---|---|
| Exploring | Problem validated, no design committed | None |
| Next | In design or build, named owner, scoped | None |
| Later | Wanted, not yet scheduled | None |
| Shipped | Released, links to changelog | Release date |
| Not planned | Decided against, with reason; stays visible at least one review cycle | None |

- **Proposed** is a separate label for community ideas. A Proposed item never sits in Next or Later by vote alone.
- **No quarters or dates** appear at launch. A quarter appears only beside a release phase, from private preview onward.
- Write items problem-first: "Query payments with one request" rather than "GraphQL API".

### Exclusion gate
Never publish:
- Security and fraud-control work.
- Unannounced deprecations or breaking changes.
- Pricing, packaging and financials.
- Named processors, acquirers, banks or other partners before they announce.
- Compliance and certification timelines.
- Customer-specific commitments.
- Internal plumbing.

You are the edge-case decider. Product lead and counsel are your backups [assumed].

### Feedback surface
- Items are locked.
- Each links to one discussion channel, such as a Discussions category.
- The old board is frozen, not embedded (see section 5).
- Votes are one input to triage, weighted by plan tier and revenue.

### Lifecycle
- **Owner:** you, with a named backup.
- **Cadence:** monthly review. Touch every item and confirm, move, or mark `not planned`.
- **Stable IDs:** each item gets one that survives from Exploring to Shipped.
- **Subscriptions:** per-item watch or a digest.
- **Changelog close:** every shipped item links its changelog entry.
- **Snapshots:** snapshot the page at each review.
- **Cap:** about 12 public items at launch. Setup time is a few days, so take the first month's actual hours as the real budget.

### Slip playbook
1. Change the status on the item: `delayed`, `descoped` or `not planned`. Never delete it.
2. Give a one-paragraph plain reason.
3. Offer a workaround.
4. Notify subscribers.
5. Contract-dependent customers hear first, privately. Legal checks the notice against order-form terms.
6. Keep cancelled items visible for at least one cycle.

## 5. The old board: freeze, then archive

Don't embed it and don't kill it. Use the format-change pattern.

| Date | Change |
|---|---|
| T-14 days | Banner on the old board announcing the move |
| Launch day | Old board set read-only and frozen. New roadmap and feedback channel live |
| Launch + 90 days | Old board archived read-only with redirect |

**What's not changing:** every request stays readable, and no vote or comment history is deleted.

**What happens to open requests:** they stay in the frozen archive. They are not auto-promoted and not deleted. The ones that matter are re-filed into the new channel as they surface. Nobody has to re-vote in bulk.

The untriaged backlog doesn't gate launch. Triage is a separate effort, in section 7.

## 6. GraphQL API (900 votes)

Handle it explicitly, because it's your most visible request.

1. **Segment the votes** before anything else:
   - Voters on paid plans.
   - Voters with live payment volume.
   - Enterprise accounts that asked for it in sales or support.
2. **Make a decision.** Don't let the board make it for you. The outcomes:
   - Decided yes: scope it, assign an owner, and list it in Exploring or Next, problem-first.
   - Decided no: mark it `not planned` with a reason and a condition that would reopen it.
   - Undecided: leave it off the roadmap. Don't put it in Next to look responsive.
3. **Reply publicly** in the feedback channel either way.
4. **Pricing and Osborne check:** if GraphQL touches packaging or competes with the current API, the gate may keep it off the page until announced.

## 7. Timeline (launch about 4 weeks out)

The skill says to publish only after at least two internal review cycles have produced decided statuses. Run them biweekly, not monthly, to fit.

| Week | Action | Owner |
|---|---|---|
| 1 | Inventory contracts naming roadmap items. Check the MSA for a "no reliance on future functionality" clause. Check self-serve terms have an equivalent. Counsel writes the disclaimer | You, counsel |
| 1 | Pick about 12 candidate items. Run each through the exclusion gate | You, product |
| 1 | Segment GraphQL votes and decide its status | You, product |
| 2 | Review cycle 1: assign each item a status and owner | Product |
| 2 | Sales one-pager: cite only the public roadmap, no dates beyond it, order forms need legal approval. Needs sign-off from sales leader and CEO | Sales lead, CEO |
| 3 | Review cycle 2: confirm statuses. Draft items and the frozen-board banner | Product, you |
| 3 | Put the T-14 banner on the old board | You |
| 4 | Final approvals: product, sales leadership, counsel. Finance if any date appears. Launch | All |

**If cycle 2 can't finish, fall back to Candidate B** (direction page) for launch and add item-level detail next month.

## 8. Launch checklist

- [ ] Citation rule signed by the sales leader and CEO.
- [ ] Contract inventory done. Any roadmap item in an order form or side letter reviewed by counsel and finance, and the account owner has contacted the customer.
- [ ] MSA clause and self-serve terms checked.
- [ ] Disclaimer on the page: informational, not a commitment, subject to change, don't rely on it for purchase decisions.
- [ ] Prior slips handled. Any feature promised before the page existed has a communication plan.
- [ ] Two review cycles complete with decided statuses.
- [ ] Every item has a problem-first title, stable ID and channel link.
- [ ] Exclusion gate applied to every item.
- [ ] Old board banner live 14 days before launch.
- [ ] Feedback channel created and linked from every item.
- [ ] Backup owner named.
- [ ] Snapshot taken at launch.

## 9. Measurement

No outcome metric has independent evidence, so measure integrity.

| Metric | Target |
|---|---|
| Items touched each review | 100%; any item untouched for two cycles gets a decision |
| Silent removals | 0 |
| Slip rate of committed items | Track it before ever adding dates |
| Shipped items closed with changelog link | 100% |
| Roadmap items in new order forms | Baseline now, compare quarterly |
| "When will X ship" tickets | Baseline now, compare after launch |

## 10. Path to the interactive board

Revisit Candidate C when all of these hold:
- A named triage owner exists, even at a few hours a week.
- The backlog has had a first triage pass, including the 1,400 old requests.
- A `not planned` state with reasons exists.
- You have run at least two monthly reviews with no silent removals.

Until then, the frozen board plus locked roadmap gives you most of the "we listen" signal without the standing triage debt.

## Open questions (they would change the plan)

1. Are sales or solutions staff promising unbuilt features today? If yes, signing the citation rule becomes a hard blocker, not a checklist item.
2. Does the MSA carry a "purchases not contingent on future functionality" clause, and do the self-serve terms?
3. Do any existing contracts name roadmap items?
4. Can you commit about 3 hours/month, plus a few days of setup? If not, go with B.
5. Are regulated enterprise buyers asking for roadmap evidence? If yes, add NDA briefings alongside the public page.
6. Can the launch date move? Two review cycles may not fit in four weeks.