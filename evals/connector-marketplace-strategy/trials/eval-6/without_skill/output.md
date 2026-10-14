# Onwards Labs marketplace: sanity check and seeding sequence

**Verdict: don't run the plan as written. Keep the marketplace shell, but cut the launch to about 10 to 12 connectors and move the hackathon and fund behind gates.**

**Next action (under 2 minutes):** send finance a one-line ask: "Can we hold a ring-fenced envelope, amount to be set by 2026-11-06, released in tranches against the gates below?" Everything in the plan that costs money waits on this answer.

I had no demand data from you, so every connector choice below is a placeholder. Step 1 replaces it with a counted list.

---

## 1. Plan check

| Plan element | Verdict | Why |
|---|---|---|
| 60 connectors, every category | ❌ Cut to about 10 to 12 | The minimum credible pool is set by coverage of customer demand, not by count. A buyer opens the marketplace to find their accounting system and HRIS. Nobody counts the list. |
| $50k hackathon in month one | ❌ Move to month 5 or later, and shrink it | There is no surface, community, or builder pool to hold it on. |
| Build fund | ⚠️ Keep the idea, but it needs approved money and a trigger | Finance has approved nothing. A fund with no liquidity behind it is a promise you can't keep. |
| Fixed date, 4 months | ✅ Constraint, not a problem | It favors the one rung you control: connectors you build yourselves. |

### Why 60 connectors fails
- **Capacity.** 60 connectors must be built by you, since your supply is 31 portal developers, mostly internal customer teams, and none of them are vendors.
- **Maintenance.** Each connector is maintained forever against other vendors' API changes. Sixty connectors mean a permanent on-call burden before you know which ones anyone uses.
- **Concentration of demand.** In expense management, usage concentrates in accounting/ERP, card feeds, and HRIS. BI, procurement, and travel are long tail. Spreading evenly across "every category" puts effort where adoption is lowest.
- **Money data.** Connectors that touch ledgers and card data need security review. You can't push 60 through in four months, and an unreviewed one is worse than a missing one.

### Why the month-one hackathon fails
- **No surface.** The API has had no outside developers yet. Docs, sandbox, and versioning don't exist in a form strangers can use. Participants would build on something that changes under them.
- **No audience.** There is no Discord, no meetups, no community. The 31 registered developers are internal teams at customers, so the people you'd invite have no business reason to enter a contest.
- **Wrong output.** Hackathon projects are demos, not maintained connectors. They don't fill the demand list, and you'd still owe the review queue.
- **Wrong money.** $50k of prizes for a few dozen possible entrants is about $1k+ per participant. It also competes with the fund for the same unapproved dollars.
- **Buzz needs a reach.** Buzz needs an audience that cares. You have none yet, so the event creates PR with no one to receive it.

### Why the fund needs a trigger
- A fund is a subsidy to builders. Finance hasn't approved any subsidy, so announcing one at launch is an unfunded public promise.
- Pay builders against **named gaps** on your demand list, on milestones, with no take-rate. A generic "build fund" attracts low-value connectors in crowded categories.

---

## 2. Gates (pass, fail, or unknown)

| Gate | Status | Resolver and date |
|---|---|---|
| Counted demand (≥5 requested complements, customers named) | **Unknown** | Pull sales-lost notes, support tickets, and CS requests. By 2026-10-23. |
| Externalizable interfaces (your own connectors can run on the public API) | **Unknown** | Eng audit. By 2026-10-23. |
| Builder supply beyond internal customer teams | **Fail today** | Integrators recruited by 2026-12-18. |
| Staffing (named owners for review, support, partner coordination) | **Unknown** | Name owners by 2026-10-23. |
| Envelopment risk (an ERP or card issuer bundles the same connectors) | **Unknown** | Name the one or two vendors that could. By 2026-10-23. |
| Security review function for third-party code | **Unknown** | If none exists, partner-built connectors stay behind the review queue and stay few. |

If the demand list or the interface audit fails, stop and fix that first. A marketplace launch on that foundation would be empty at best.

---

## 3. Recommended rung

Of the three candidates, the recommendation is **A, with a small slice of B**.

| | Who builds | You operate | Earliest signal |
|---|---|---|---|
| **A. Vendor-built connectors plus documented API (recommended)** | You build 10 to 12; customers' internal teams use the API | Connector maintenance, API versioning | Connector activation per account in the first 30 days |
| **B. Partner-built, listed (a few, from integrators)** | 2 to 3 integrators or agencies, paid on milestone | Listing standards, review queue, escalation | First partner connector passing review |
| **C. Full 60-connector launch** | You | Everything, forever | Not recommended; no signal arrives before the date |

Why A: the fixed date makes your own delivery the only dependable supply. The rung also teaches you which connectors customers actually adopt before you pay anyone to build more.

Why only a slice of B: partner-built connectors are the best ratio on the ladder, but the first partner who earns money from you acquires a claim on your roadmap. That's fine at 2 to 3 partners and unwise at 20.

Rungs deleted for now: installable third-party apps and a runtime platform. You have no standing team, no review function, and no builders for them.

---

## 4. Builder economics (one line per archetype)

- **Customers' internal teams (your 31 developers):** need no business case, only low friction. They are your cheapest and first supply. They build glue for their own company, not marketplace listings, so don't count them as connector supply.
- **Integrators and agencies:** they monetize hours. Offer referral flow, certification, and milestone pay. Don't offer revenue share.
- **Independent software vendors:** with 2,400 customers, reachable demand per connector is small. Illustration with made-up numbers: if 5% of customers want a given connector, that's about 120 accounts. That rarely funds a product line. Don't pitch ISVs until adoption data exists.
- **Take-rate:** 0% at launch and until the marketplace has liquidity.

For each partner, ask: "If we don't do this, what changes for you?" Answers like "nothing really" mean you have a logo, not a complementor.

---

## 5. Seeding sequence

Dates assume today is 2026-10-08 and launch is Monday 2027-02-08 (17 weeks out). Shift everything if the date differs.

### Phase 0: Count demand and unlock money (Oct 12 to Oct 23)
1. Build the demand list: the last 10 or more connector requests, each with customer names, from sales-lost notes, support tickets, and CS. Rank by number of accounts.
2. Interview the 31 portal developers, 20 minutes each. Ask what glue they already built. Unofficial glue is the strongest demand evidence.
3. Eng audit: can your own connectors run on the public API without privileged paths?
4. Name owners for review, support, and partner coordination. Name the one or two vendors that could bundle your connectors.
5. Finance ask: ring-fenced envelope in tranches (see section 6).

**Gate to proceed:** ≥5 requests with customers named, and an API audit with a plan for any private-path gaps.

### Phase 1: Stable surface (Oct 26 to Nov 20)
1. Ship the documented API and webhooks, a sandbox tenant, versioning, deprecation policy, and rate limits.
2. Publish the roadmap boundary: what Onwards builds itself, and with how much notice before it absorbs a partner's work.
3. Recruit a founding cohort of 5 to 8 customer developer teams, hand-picked to cover the top demand items. Give them early sandbox access and a direct channel to your engineers.

### Phase 2: Vendor-built connectors in waves (Nov 2 to Jan 22)
Placeholder order, replace with your counted list:

| Wave | Target date | Contents (placeholder) |
|---|---|---|
| 1 | Dec 4 | 3 connectors: the accounting systems with the most accounts |
| 2 | Jan 8 | 4 to 5: remaining top accounting/ERP, HRIS, and card feeds |
| 3 | Jan 22 | 2 to 3: next-ranked demand, plus buffer for slippage |

- **BI:** serve with a documented export and webhooks, not connectors. Customers' own teams can wire it.
- **Procurement and travel:** defer unless the demand list says otherwise.
- **Dec 21 to Jan 1:** hold as slack; don't plan builds in it.
- Label every connector by owner ("built by Onwards") and publish a "request a connector" board that feeds the demand list.

### Phase 3: Recruit integrators (Nov 16 to Dec 18)
1. Shortlist 5 accounting or finance-systems integrators that already serve your customers.
2. Offer: certification, referral flow, early API access, milestone-paid builds if finance approves.
3. Aim for 2 to 3 signed partners and 1 to 2 partner-built connectors passing review by launch. If none pass, ship without them.

### Phase 4: Launch hardening (Jan 25 to Feb 5)
- Run each launched connector end to end with a founding-cohort customer.
- Dogfood the review and support path with a test partner.
- Set the launch page to say what's live, what's partner-built, and what's on the roadmap.

### Launch: Monday 2027-02-08
- ~10 to 12 live connectors, documented API, sandbox, request board, public roadmap.
- Announce to the 2,400 customers first (in-product placement, CS outreach). Public PR comes second.

### Phase 5: After launch
| When | Action |
|---|---|
| Feb 8 to Mar 5 | Weekly office hours; GitHub Discussions or a forum for developers. Skip Discord until there are ≥20 active builders. |
| Early March | Gate review (section 7). If passed, release tranche 2: named bounties against the top unmet demand items. |
| March to April | Customer build sprint: your founding cohort plus integrators, small prizes only. |
| About May 2027 | Hackathon decision, **only if** the gate below passes. Then run it at $5k to $10k, themed on the top unmet connectors, aimed at integrators and customer teams. |

---

## 6. Money, staged (my defaults, not industry benchmarks)

| Tranche | Release trigger | Use |
|---|---|---|
| 0 (now) | None | $0 beyond existing eng time |
| 1 | Phase 0 gate passes (Oct 23) | Integrator milestone payments for 1 to 2 launch-ready connectors, if you want them by Feb 8 |
| 2 | March gate review passes | Named bounties on top unmet demand items |
| 3 | May gate passes | Hackathon ($5k to $10k), not $50k |

Set the total envelope after Phase 0 so it is sized to the gaps on the demand list.

---

## 7. Measurement and kill criteria

Baselines to record by Oct 23: demand-list size, registered portal developers (31), active portal developers (unknown, measure it), accounts using the API.

| Metric | Target | Date |
|---|---|---|
| Connector coverage of demand list | ≥70% of top-10 requested | Feb 8 |
| Accounts with ≥1 active connector | Set after Phase 0 baseline | Mar 31 |
| Time from signup to first working integration | Record baseline | Mar 31 |
| Active builders outside Onwards (shipped anything) | ≥10 | Apr 30 |
| Top-5 connectors' share of usage | Watch; very high = five partnerships, not a marketplace | Ongoing |

**Gate for tranche 2 (March 5):** ≥30% of launch-live connectors activated by at least one customer account, and the founding cohort shipped ≥3 working integrations.

**Gate for the hackathon (May):** ≥10 active external builders and ≥2 integrators already shipped.

**De-escalate or stop if:**
- By Dec 4, wave 1 is not shipped: cut wave 3 and delay launch of the marketplace listing for non-wave-1 connectors.
- By Mar 31, fewer than 10% of accounts have an active connector: pause tranches 2 and 3, and put effort into the top 3 connectors only.
- By Jun 30, zero external builders have shipped: close the build fund and keep the marketplace as a vendor-built catalog.

---

## 8. Obligations you are accepting (owners to name)

- API stability and deprecation notice period (suggest ≥6 months): **eng lead**
- Roadmap boundary and notice before absorbing a partner's feature: **ecosystem lead**
- Support path when a partner's connector breaks a customer: **support lead**
- Security review of every connector touching ledger or card data: **security owner**
- Wind-down terms if the program stops (notice, export): **ecosystem lead plus legal**

---

## Open questions I could not answer from your brief

1. Does a security review function exist for third-party connectors? If not, Phase 3 shrinks to one partner or none.
2. Is the launch date fixed to a customer commitment or to a board date? It decides whether wave 3 is cut or the date is held.
3. What does finance need to release even tranche 1: a business case, or only a ceiling?

**Next action:** do step 1 of Phase 0 today. Export the last 90 days of "do you integrate with X" requests from sales and support into one sheet with customer names.