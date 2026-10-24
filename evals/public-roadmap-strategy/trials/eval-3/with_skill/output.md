# Pinnacle Ledger public roadmap: items for the repo

I read the `public-roadmap-strategy` skill and its references, then ran your nine Jira items through its exclusion gate. The skill applies the same gate to NDA briefings, so the "same list as the NDA briefings" plan doesn't survive it. Only 4 of the 9 items are publishable, and one of those needs legal review first.

## Gate result

| Jira | Decision | Reason |
|---|---|---|
| PL-301 auth token replay fix | ❌ Exclude | Security work. Publishing it tells attackers where the gap is. |
| PL-287 sunset v1 ledger endpoints | ❌ Exclude | Unannounced deprecation. Announce it through your versioning process first, then link the notice from a roadmap item. |
| PL-312 Starter price increase and Growth tier | ❌ Exclude | Pricing and packaging. A new tier can also stall Starter purchases (Osborne effect). |
| PL-298 Tarnbrook Bank sync | ⚠️ Publish without the name | Partner that hasn't announced. Name the capability, not the vendor. |
| PL-305 SAML mapping for Harrowgate | ⚠️ Hold | Customer-specific commitment made in a renewal. It belongs in their order form. |
| PL-320 Postgres 17 and billing split | ❌ Exclude | Internal plumbing. |
| PL-290 Key rotation v2 | ✅ Publish | Rewritten problem-first. |
| PL-315 Bulk export to warehouse | ✅ Publish | |
| PL-322 Multi-entity consolidation | ✅ Publish | |

## Items to commit

Use new public IDs (`RM-###`), not Jira keys. Keys would show the gaps where the excluded items sit. The statuses below are proposals. The skill defines buckets by engineering state, not by date, so please confirm each against reality. No item carries a quarter, because a date is allowed only from private preview onward.

```markdown
**Rotate API keys without downtime** `RM-101`
Status: In design [confirm]  Timing: none
What it solves: Replace a leaked or expiring API key while the old and new keys both work during an overlap window, so integrations don't break mid-rotation.
Who it's for: Teams running production integrations against the ledger API.
Discuss: <link to one feedback thread>
Updates: <date> - added to roadmap.
Shipped: -
```

```markdown
**Export ledger data to your own data warehouse** `RM-102`
Status: Exploring [confirm]  Timing: none
What it solves: Move large volumes of ledger data into the customer's warehouse for reporting and analysis, without paging through the API.
Who it's for: Finance and data teams that report outside the product.
Discuss: <link>
Updates: <date> - added to roadmap.
Shipped: -
```

```markdown
**Consolidate multiple legal entities in one view** `RM-103`
Status: Exploring [confirm]  Timing: none
What it solves: Combine the books of several entities into a single consolidated view, so group-level reporting doesn't require manual merging.
Who it's for: Customers with more than one legal entity.
Discuss: <link>
Updates: <date> - added to roadmap.
Shipped: -
```

```markdown
**Sync ledger with your bank accounts** `RM-104`
Status: Exploring [confirm]  Timing: none
What it solves: Keep ledger entries and bank transactions in step automatically, without manual import.
Who it's for: Customers who reconcile against bank feeds.
Discuss: <link>
Updates: <date> - added to roadmap.
Shipped: -
```

- **RM-104** names no bank. Add the partner name only after Tarnbrook announces.
- **PL-305** is a possible fifth item, and I have not drafted it. You could publish a general "Map custom SAML attributes" item with no customer name. Do that only after counsel and finance have reviewed Harrowgate's order form. The promise itself stays in their contract.

## Repo contents

- A README with the disclaimer on the page itself:
  > This roadmap is for information only. It is not a commitment to deliver any feature, and plans and timing may change at our discretion. Please make purchasing decisions based on features available today.
  Counsel approves the final wording.
- A vocabulary section defining what a customer may rely on in each status.
- Items read-only. Debate goes in one linked Discussions thread. This is the cheapest feedback surface.
- A named owner and a monthly review. Every item gets touched each review.
- A `shipped` label plus a changelog link when an item closes.
- A `not planned` or `delayed` state, with a reason, for any item that slips. Never delete an item.
- Start from a fresh repo. Don't commit the Jira export or its history, because they contain the excluded rows.

## The NDA briefings

I'd push back on naming the partner there. The skill's gate applies to NDA decks too:

- Never show unannounced deprecations, security work, or partner names, even under NDA.
- Show the public items, plus at most items product has approved for that account.
- Put the disclaimer on slide one.
- Log which account saw which items, so a later slip reaches everyone who saw them.

An NDA binds the attendees, but it doesn't cover a leak by the partner, or a sales rep who repeats it afterward.

## Before you publish

The "this week" timeline is at risk on these:

1. **Review cycles.** The skill says publish only after at least two internal review cycles have produced decided statuses. If these statuses are new, you're early.
2. **Citation rule.** The sales leader and CEO need to sign the rule that limits what anyone customer-facing may promise. Without it, a public page gives reps a bigger catalogue to promise from. The skill says to fix sales governance first and publish later in that case.
3. **Contract inventory.** Check every order form, SOW and side letter for roadmap items. Harrowgate is one known case. A feature written into an order form binds you whatever the disclaimer says.
4. **MSA clause.** Check that your MSA and self-serve terms say purchases aren't contingent on future functionality.
5. **Pricing and v1 sunset.** Neither is on the page, so your pricing announcement and v1 deprecation notice need their own channels and timing.
6. **Interview answers I'm missing.** I haven't asked the interview questions, so I assumed a horizon roadmap alongside your enterprise briefings. Tell me about your buyer mix, how often last year's expected items slipped, and how many owner hours you have, and I can re-rank the posture.

Once the preconditions are met, I can draft the full policy document section by section.