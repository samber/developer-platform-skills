# Halvard Analytics alliance: governance reset

Date: 2026-10-09. I'm working from your description only, so check the assumptions at the end.

## 1. Diagnosis

- ❌ **No shared goal.** Two calls were slide swaps. Nobody owned the integration outcome.
- ❌ **No engineering channel.** The teams never worked together, so Halvard's silence went unnoticed.
- ❌ **No change-notice duty.** They re-platformed their API and you learned it from a customer. Your integration may already be broken or stale.
- ❌ **Executive sponsors absent.** Nobody noticed month three.
- ℹ️ **Legal form is not the cause.** Cadence, ownership and obligations failed. Those fail in a JV too.

## 2. Answer to legal: JV or not?

**Recommendation: no JV now. Keep the alliance and add a binding governance schedule.**

Why a JV would not have fixed this:
- A JV adds an entity, capital, a board and shared liability. It still needs the same cadence, owners and escalation rules.
- Halvard went quiet for lack of a forcing mechanism. A JV board is one such mechanism, but a contract can supply it more cheaply.

When a JV becomes worth it (revisit at the 6-month review):
- You co-develop a single product sold under one brand.
- You share revenue beyond a simple referral or rev-share.
- You hold jointly owned IP that neither side can license alone.
- You need shared customer contracts or a shared liability umbrella.

Otherwise, use these instruments:
1. **Alliance agreement amendment** with a Governance Schedule (section 3).
2. **Joint Development Agreement (JDA)** covering IP ownership, who builds what, and licensing of the integration.
3. **API change and support covenant** (section 5).
4. **Exit and step-in terms**: termination for inactivity, with integration code and customer support handover.

Questions for counsel:
- Does the current agreement already contain notice, SLA or termination-for-inactivity clauses we can invoke now?
- Who owns the integration code and any joint IP today?
- Does the API re-platform breach any compatibility or notice term?
- Are mutual customers promised an integration we can't currently deliver? Is there exposure?

## 3. Governance model

### Three tiers

| Tier | Who | Cadence | Purpose |
|---|---|---|---|
| Executive Sponsors | 1 exec per side | Quarterly, 60 min | Strategy, resources, unblock escalations, go/no-go |
| Alliance Leads | 1 named owner per side | Weekly, 30 min | Run the plan, track the RAID log, own the scorecard |
| Joint Engineering | Tech lead plus 1-2 engineers per side | Twice weekly 15-min standup plus a shared channel | Build, API contract, test |

### Roles and decision rights

| Role | Owner | Decides |
|---|---|---|
| Executive Sponsor (each side) | Name them this week | Resourcing, scope changes over 20%, escalations, termination |
| Alliance Lead (each side) | Name them this week | Roadmap order, release dates, scorecard sign-off |
| Integration Tech Lead (each side) | Name them this week | API contract, versioning, test plan |
| Joint customer success owner | One per side | Mutual customer issues, comms |

Rules:
- **One accountable owner per side.** Committees do not own anything.
- **Decisions in writing.** A shared decision log, updated within 24 hours of each meeting.
- **Disagreement.** The Alliance Leads have 5 business days, then it goes to the Sponsors, who have 10 business days. If still stuck, follow the contract's dispute clause.

### Meeting rules
- **Banned:** slide-deck status presentations.
- **Standing agenda for the weekly call:**
  1. Scorecard changes.
  2. Blockers.
  3. Decisions needed.
  4. Customer issues.
  5. Next week's commitments.
- Pre-read is a one-page scorecard, sent 24 hours ahead.
- Each side's quarterly business numbers go in an async doc. They are not discussed live.

## 4. Scorecard (shared, reviewed weekly)

| Metric | Target | Red trigger |
|---|---|---|
| Integration milestones on plan | ≥ 90% | Slip over 2 weeks |
| Both-team meeting attendance | 100% of Alliance Lead calls | 2 consecutive misses |
| Engineering response to a channel message | ≤ 2 business days | > 5 business days |
| API change notices given in advance | 100% | Any unannounced breaking change |
| Mutual customers live on the integration | Set in a 30-day baseline | No growth for 2 quarters |
| Open critical bugs | 0 older than 10 days | Any older than 10 days |

## 5. API change covenant (put in the contract)

1. **Advance notice** of any breaking API change: at least 90 days, with a migration guide and a sandbox.
2. **Versioning:** old and new versions run in parallel for at least 6 months after the new one is generally available.
3. **Change feed:** a shared changelog channel and a named contact on each side.
4. **Contract tests:** a shared automated test suite runs on each side's CI. A failure pages both Integration Tech Leads.
5. **Remedy:** if either side breaches, it fixes the breakage at its own cost within 30 days. Repeated breach triggers the exit terms.
6. **Reciprocity:** the same duties apply to your API.

## 6. Escalation ladder and health triggers

| Signal | Action |
|---|---|
| Missed call or unanswered message | Alliance Lead pings the counterpart. |
| 2 weeks of silence, or a scorecard red | Sponsors get a written alert within 2 business days. |
| 30 days red | Sponsor-to-sponsor call. Reset the plan or descope. |
| 60 days red, or a covenant breach | Counsel issues formal notice and invokes the contract's cure period. |
| 90 days with no cure | Exit options: terminate, convert to a loose referral partnership, or evaluate a JV. |

## 7. Plan for the next 30 days

**Week 1 (by 2026-10-16)**
1. ✅ Name your Executive Sponsor, Alliance Lead and Integration Tech Lead.
2. ✅ Your sponsor emails theirs. Say plainly that you learned of the API re-platform from a customer, and ask for a sponsor call within 7 days. Keep it factual and non-accusatory.
3. ✅ Your engineers read Halvard's new API docs and run your existing integration against it. Record what breaks.
4. ✅ Send counsel the questions in section 2 and the current agreement.
5. ✅ Ask the mutual customer, with their consent, what they saw and whether they are affected.

**Week 2 (by 2026-10-23)**
1. Hold the sponsor call. Agree to the three-tier model, the scorecard and the API covenant in principle.
2. Run a joint engineering kickoff and open the shared channel.
3. Write down the integration scope: what ships, for whom, by when. Cut it to a first release you can finish in 90 days.

**Week 3 (by 2026-10-30)**
1. Counsel drafts the Governance Schedule, the JDA terms and the API covenant.
2. Alliance Leads finalize the roadmap and baseline the scorecard.

**Week 4 (by 2026-11-06)**
1. Sponsors sign off the amendment.
2. First full weekly cadence runs. Publish the first scorecard.
3. Fix the quarterly Sponsor review date.

## 8. Checkpoints

- **Day 30 (about 2026-11-09):** the cadence is running, the contract is signed or in final review, and the integration is tested against the new API.
- **Day 90 (about 2027-01-07):** first release shipped to at least one mutual customer.
- **Month 9 (about 2027-04):** formal review. Continue, restructure, or exit. Revisit the JV question using the triggers in section 2.

## 9. Assumptions to confirm

- The current agreement is a contractual alliance with no JV entity. It may or may not have notice or termination-for-inactivity clauses.
- Halvard still wants the alliance and went quiet from neglect, not intent. If their silence was deliberate, skip to the section 6 escalation.
- You have not yet checked whether the re-platform broke your integration. Week 1, step 3 settles that.
- This is a governance design, not legal advice. Counsel should confirm the contract mechanics.