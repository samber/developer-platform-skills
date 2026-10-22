**Next action:** Open both Orbiton rejection notices and copy the exact rule text each one cites. That text is your checklist. Details in the Gap section. About 15 minutes.

I did not run the interview. You asked for a single final answer and no question tool was available. I assumed you are the **submitter** on Orbiton. The first open question below could change the route.

## Route

**`samber/developer-platform-skills@integration-listing-optimization`**

- It covers the view-to-install funnel on a marketplace you don't own.
- Its method says to read the target marketplace's listing rules before changing anything.
- Your numbers: 2,100 views × 1.4% ≈ **29 installs/month**.
- I can't call 1.4% "terrible" without a comparator. This collection has no Orbiton benchmark. Ask that skill for one, using your category's other listings.

## Your three asks

1. **Funnel at 1.4%:** goes to the routed skill.
2. **"Our own listing standards":**
   - Submitter reading (assumed): this is your internal quality bar for your Orbiton listing. The routed skill covers it.
   - Operator reading: if you plan to run your own marketplace, the route changes. See "Not now".
3. **Exact Orbiton checklist:** no skill covers it. See Gap.

## Short-list

Ordered by value per unit of effort, highest first. Entries 2–5 apply only if Crestline runs its own public API or integration surface. I don't know that yet, because Q1 and Q3 are unanswered.

1. **`integration-listing-optimization`**
   - Attacks: the 1.4% view-to-install gap.
   - Costs: one session, plus listing edits that go back through Orbiton review. Get the checklist first, or an edit may trigger a third screenshot rejection.
2. **`integration-partnership-strategy`**
   - Attacks: whether to pursue an Orbiton certification or badge, and at what depth.
   - Costs: coordination with sales and legal. Payoff comes a planning cycle later.
3. **`integration-error-observability`**
   - Attacks: installs that fail silently after activation.
   - Costs: a log store plus a named owner for follow-up.
4. **`api-reference-quality`**
   - Attacks: undocumented endpoints behind the listing.
   - Costs: one session. Near-free if an OpenAPI spec is committed.
5. **`api-status-communication`**
   - Attacks: payroll customers who learn about an outage from their own customers.
   - Costs: a status pipeline you then run forever.

Re-rank notes:

- Q1 is submitter-side, so ecosystem-execution skills drop out (`app-marketplace-*` and `partner-app-onboarding`). Those are operator-side.
- Surface audit and the error contract sit below the route because they depend on unknown surfaces.
- No date or effort ceiling is known. Q5 and Q6 are unanswered, so nothing was cut for capacity.

## Chain

No chain. The three asks are separate tasks, not a sequence. One dependency matters: get the checklist first, then edit the listing.

## Not now

- **`connector-marketplace-strategy`**
  - Unblock: "our own listing standards" turns out to mean you plan to run your own marketplace.
  - Start here, before any `app-marketplace-*` skill. It holds the evidence gate.
- **`app-marketplace-listing-standards`**
  - Unblock: the same marketplace build verdict.
  - It is the operator-side rulebook, so it does not apply while you are the submitter.

## Gap

**The collection has no skill for per-marketplace submission playbooks.**

- That means Orbiton's screenshot sizes, required fields and review criteria.
- `integration-listing-optimization` is marketplace-generic and does not cover them.
- I will not guess Orbiton's rules. A guessed screenshot size would cost you a third rejection.

Ways to get the real rules:

1. Quote the exact rule text from both rejection notices: dimensions, ratio, format, file size, count.
2. Check Orbiton's partner or developer docs for a listing requirements page.
3. Email the reviewer or partner contact: "Send the full media specification you review against, and tell us whether it changed since our last approval."
4. Compare your **live** screenshots against the rules. The listing has been live 14 months, so either the rules changed or they were never checked on edits.
5. Put the confirmed rules in one file. That file is also your internal listing standard.

## Routines (dry-run, not installed)

1. **Quarterly kickoff re-run.** Output channel: your growth team's channel, with a refreshed context file and a re-route.
2. **Listing defend cycle**, every 30–60 days, using `integration-listing-optimization`. The listing is live and you have view and install data, so it qualifies. Output channel: a short funnel report to the head of growth.

The design-review routine is not proposed. No API spec was mentioned.

## Open questions

1. Do you want a rulebook for your own Orbiton listing, or for a marketplace you would run?
2. Does Crestline expose its own public API or integration surface? Which ones?
3. Is there a date by which the listing must be fixed? What is the effort ceiling?

## Context artifact

I did not write `developer-platform-context.md`, because this repo is not your project. Save this at your project root:

```
# developer-platform-context.md
Audience: Crestline Payroll = submitter on Orbiton Suite marketplace (assumed; unconfirmed)
Published surfaces: Orbiton listing, live 14 months. Own API: unknown
Spec locations: unknown
Contract owner / breaking-change signer: unknown
In-flight (2026-10-08): 2 screenshot-sizing rejections; Orbiton checklist missing
Funnel: ~2,100 views/mo, 1.4% install (~29/mo), no benchmark
Decided: none. Open: submitter vs operator; own API; date; effort ceiling
Session log: 2026-10-08 cold start, no interview. Routed to integration-listing-optimization. Gap: Orbiton playbook.
```

Memory: nothing written. Never store partner names tied to traffic, keys, or negotiated terms.

**Next:** Paste the two rejection notices here. I'll turn the cited rules into your checklist draft.