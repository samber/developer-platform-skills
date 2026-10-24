# Lattivo public roadmap design

**Recommendation:** Don't publish the page yet. Launch it when the CEO and VP Sales have signed a one-line citation rule. With that rule signed, the right page is a horizon roadmap: undated, locked, at most 10 items. Everything else in this document is the design to publish once that gate clears.

I ran the `public-roadmap-strategy` skill from your background, so I didn't interview you. Where your answer was missing, I list it under "Unknowns" at the end.

## 1. What the roadmap must fix

Your trigger is sales promising unbuilt work. Two deals closed on "SSO group sync by March", and it isn't staffed. The cause is that no externally sayable roadmap exists, and nothing limits what reps may promise.

A public page fixes that only as the sales-safe subset, with a citation rule enforced. Without the rule, reps screenshot "Next" items into deals and the page makes the problem worse.

"Like Stripe's" means dated quarters, the most demanding posture. Lattivo fails three of its four promotion conditions:

| Condition for dated quarters | Lattivo | Passes? |
| --- | --- | --- |
| Release phases exist | Engineering tags "beta" in Slack ad hoc | ❌ |
| Few items slipped last year | 3 of 9 slipped (33%) | ❌ |
| Buyers plan around your dates | Unknown | ❓ |
| Finance reviewed ASC 606 exposure | Not done | ❌ |

Dated quarters are ineligible now. Revisit them after two quarters with phases running and a slip rate you've measured.

## 2. The VP Sales objection

The skill is explicit here: when the trigger is sales promises and leadership won't sign the citation rule, every public posture is off the table. Publishing then hands reps a bigger catalogue to promise from.

His position, "fine with the page, won't sign anything about what reps say", is the one combination that doesn't work. A few points for the conversation:

- **The rule isn't a script.** It names one source: cite only the public page, at the commitment level printed on it. Managers enforce it. That is what "that's what managers are for" already means, and the rule gives them something concrete to enforce.
- **He owns enforcement.** The rule makes him the escalation path and the enforcer, not a person told what to say.
- **You have evidence.** Two deals closed on an unstaffed feature. That is a revenue risk to him, because those customers will be told it slipped.
- **The CEO can sign it without him.** The skill asks for the sales leader and the CEO, but the CEO is the one who wants the page. Don't launch on an unsigned rule. If the VP still refuses, the fallback is no public page, with the rest of this plan running (section 9).

The rule, which fits in 5 lines:

1. Reps, SEs, customer success, DevRel and execs on stage cite only the public roadmap, at the state printed on it. No dates beyond what the page shows.
2. Anything deeper goes through a formal channel with product present: a private-preview enrollment or an NDA briefing.
3. No roadmap item goes in an order form, SOW or side letter without legal and finance approval.
4. A deal that depends on an unbuilt feature goes to product for a decision: commit it through the roadmap, or decline it. It never goes to a rep's judgment.
5. When an item a deal referenced slips, the account owner tells the customer before the public update, after legal checks the notice.

## 3. Candidate bundles

| | A. Horizon roadmap (recommended) | B. Direction page + NDA briefings | C. Dated quarters ("like Stripe") |
| --- | --- | --- | --- |
| Shape | Undated buckets by engineering state, locked items | Narrative themes, undated, plus briefings for the 60 MSA accounts | Quarter on every item, capped by a phase |
| Hours/month | About 3.5 h | About 2 h page, plus about 1 h per briefing | Over 4 h, plus finance review |
| Fixes sales promises? | Yes, with the rule | Partly: briefings are where dated promises get made | Adds a date for every rep to promise |
| Status | Eligible once the rule is signed | Eligible once the rule is signed | ❌ Ineligible now |

A fits your 4 hours and answers "what's coming" without a single date. B is cheaper, but it gives sales less to cite. Add briefings to A later if enterprise procurement asks for roadmap evidence. They don't fit this budget now.

## 4. Policy draft

### 4.1 Purpose

The roadmap gives customers and staff one sayable version of what's coming. It states order and state of work, never delivery dates. It is not a contract, a changelog or a feature request board.

### 4.2 Posture

- **Chosen:** horizon roadmap.
- **Rejected:**
  - Dated quarters: no phases, 33% slip rate.
  - Direction page: less citable by sales.
  - Voting board: no triage owner.
  - NDA briefings: no hours for them.

### 4.3 Vocabulary

Buckets are defined by engineering state, so none of them smuggles in a date.

| State | Meaning | What a customer may rely on |
| --- | --- | --- |
| Exploring | Problem validated, no committed staffing | Nothing. We may drop it. |
| In build | Named owner, staffed this quarter | We are building it. No date. |
| Rolling out | Invite-only access exists | Access can be requested. Terms follow the beta rules you write (see section 6). |
| Shipped | Released | Link to the changelog entry. |
| Delayed / Not planned | Visible negative states, with a reason | Kept visible for at least one review cycle. |

- **No dates.** A quarter appears only on items that have a release phase. You have none yet, so no quarters at launch.
- **Slack "beta" is not a state.** It stays a note on the item until access rules are written down.
- **Titles are problem-first:** "Sync identity-provider groups to account roles", not "SSO v2". Engineering can then change the solution without breaking the promise.

### 4.4 Exclusion gate

Never public, for the public page and for any briefing:

- Security work and hardening.
- Unannounced deprecations, which go through your deprecation process first and then link both ways.
- Pricing and packaging, and anything that would cannibalize a current plan.
- Partner and payroll-provider names before they announce too. Name the capability instead.
- Competitive bets.
- Customer-specific commitments, which belong in the customer's order form.
- Internal plumbing.

Payroll adds one more to watch. Items driven by tax or regulatory change often have external fixed dates. Decide with counsel whether any of those may carry a date. Default: they don't.

You decide edge cases. Record each decision here so the next editor doesn't re-argue it.

### 4.5 Legal and sales guardrails

**Disclaimer**, on the page itself, subject to counsel's wording:

> This roadmap is for information only. It is not a commitment to deliver any feature, and plans and timing may change at our discretion. Please make purchasing decisions based on features available today.

- **Contract clauses:** you've confirmed both the MSA and the click-through terms have future-functionality clauses. Before launch, counsel should confirm two things: that the click-through wording is equivalent, and that it covers public statements as well as contract promises.
- **Residual risk:** the clause doesn't override an order form, and it can't exclude misrepresentation claims. Never publish an item you know is off.
- **Private company:** use the customer sentence only. No securities safe-harbor language.
- **Finance:** no dates means low ASC 606 exposure for the public page. Finance still needs to review the two SSO deals.
- **Citation rule:** the five lines above, signed.

### 4.6 Feedback surface

- **Items are locked.** Each links to one feedback channel: a form or Discussions category that feeds your support triage. No voting board. You have no triage owner, and a board nobody triages is the worst state.
- **Revisit a board** only once a named triage owner exists and the feedback loop runs. Feedback triage itself belongs to `developer-feedback-loop`, not this policy.

### 4.7 Lifecycle

- **Owner:** you, with a named backup. Not "product".
- **Cadence:** monthly, touching every item: confirm, move, or mark Delayed or Not planned.
- **Marking public:** a public flag in the internal tool, set only on items that pass the gate. The internal roadmap is never the public one minus a few rows.
- **Stable IDs:** `LT-001` and so on, kept from Exploring to Shipped.
- **Surface:** a markdown file in a repo or a docs page, one section per item, with a subscription channel (changelog RSS or an email digest). Git history gives you a snapshot at each review.
- **Closing:** every Shipped item links its changelog entry.
- **Deprecations:** link both ways once announced.

### 4.8 Slip playbook

1. Change the status on the item itself. Never delete it.
2. Give a one-paragraph plain reason.
3. Offer a workaround.
4. Notify subscribers and every account that was shown the item.
5. Customers with a contract dependency hear privately from the account owner, days before the public update. Legal checks the notice first.
6. Keep cancelled items visible for at least one review cycle.

### 4.9 Measurement

| Metric | Baseline | Target |
| --- | --- | --- |
| Freshness (items touched each review) | n/a | 100% |
| Silent removals | n/a | 0 |
| Slip rate on committed items | 3 of 9 (33%) | Track; don't move to dated quarters until it's low |
| Close rate (shipped items with a changelog link) | n/a | 100% |
| Roadmap items in new order forms or side letters | 2 deals last quarter | 0 without legal and finance approval |
| "When will X ship" tickets and sales questions | Count before launch | Compare each quarter |

### 4.10 Approvals

Product, VP Sales and CEO (citation rule), counsel, and finance for the SSO deals. Record each with a date.

## 5. Your 4 hours a month

Budget about a quarter hour per public item per monthly review. Ten items is about 2.5 h. Add about 1 h for slip notices, changelog closing and the snapshot. That leaves about 30 minutes of slack.

Cap the page at 10 items. Setup is days, not hours, and it won't fit in 4 h/month: see the setup time under "Unknowns". Replace this estimate with your actual time after the first month.

## 6. Preview phases

Slack "beta" can't carry a customer promise. For now the roadmap says nothing about phases. To get to dated quarters later, write the preview program: what each phase promises on SLA, change notice and data terms. That is the `api-beta-program` skill's job. It also raises the odds you pass the dated-quarters conditions.

## 7. Before launch: clean up commitments that already exist

These are launch preconditions, not extras.

1. **SSO group sync.** Decide this week: staff it for March, or tell the two customers it won't make March. Both options need legal to read the two contracts first. The account owners then call the customers, before anything is published.
2. **Contract inventory.** Search all ~60 MSAs, order forms and side letters for named roadmap items. Counsel and finance review each one.
3. **The three slips from last year.** Identify who was told to expect each item and handle them as slips under 4.8.
4. **Clause check.** Counsel confirms the click-through terms, as in 4.5.
5. **Citation rule signed.**

## 8. Timeline

| When | What |
| --- | --- |
| Week of Oct 26 | CEO and VP Sales meeting on the rule. SSO decision. Contract search starts. |
| End of Oct | First monthly review: every candidate item gets a decided status. |
| By mid-Nov | Rule signed. Counsel on disclaimer and clauses. SSO customers contacted. |
| End of Nov | Second review. Publish only if every precondition in section 7 is green. |

The skill says to publish only after two internal review cycles have produced decided statuses, and that is the real constraint on the date. The end-of-November target holds only if the checklist is green. If the rule isn't signed or a contract review is open, launch slips. Tell the CEO that now, not on Nov 30.

## 9. If the VP still refuses

Run a no-page version, which is a real option and not a failure:

- Keep and improve the changelog.
- Publish a short "how we decide" page.
- Start the private-preview program (section 6).
- Run the contract cleanup in section 7 anyway.

Re-promote the horizon roadmap once the rule is signed. Launching without the rule gives sales a larger catalogue to promise from.

## Unknowns

- **Regulated customers:** whether procurement at any of your enterprise accounts asks for roadmap evidence. If they do, add NDA briefings alongside the page.
- **Whether buyers plan around your dates:** this decides dated quarters later.
- **Setup time and legal/finance capacity:** the skill's question 8 asks for these. You gave only the monthly 4 hours. Page build, disclaimer, sales one-pager and the contract search need a few days from other people.
- **Order forms and side letters:** whether any besides the two SSO deals already name roadmap items.
- **Which customer-facing roles exist beyond sales:** the rule covers SEs, customer success, DevRel and execs.

Counsel should review the disclaimer, the click-through clause and any contractual notices before anything goes out. This is a policy shape, not legal advice.