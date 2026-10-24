# Sorrelton public roadmap vocabulary (final)

I checked your draft against the `public-roadmap-strategy` skill. Six of your seven choices change. The skill says to interview first, one question per message. You asked for a finished answer, so I've assumed the default **horizon roadmap** posture (Now / Next / Later, undated, read-only items). The last section lists what would change this.

## What changed from your draft

| Your draft | Verdict | Final |
|---|---|---|
| Credit Now/Next/Later to *Product Roadmaps Relaunched* | ❌ | Credit **Janna Bastow (ProdPad)**. |
| "Next" = within about two months | ❌ | Define buckets by **engineering state**, not time. AWS's "a couple of months out, give or take" is the pattern to avoid. A time window is a date customers and sales will hold you to. |
| Quarter label on every card, including ideas still being researched | ❌ | **No quarters at launch.** If you add them later, only on items in private preview or later, and always next to the phase. GitHub does date in-design items, but that is not a rule to copy. Its relaunch left quarters passing unshipped. |
| Titles like "Rate limiter v3", "Auth revamp", "Dashboard 2.0" | ❌ | **Problem-first titles.** Version names promise a solution, so changing the design breaks the promise. |
| Remove what won't happen | ❌ | Mark it **`not planned`** with a reason. Keep it visible for at least one review cycle. Deleting erases what people already cited in deals and plans. |
| `beta` tag whenever engineering says so | ⚠️ | Until beta has written access rules, show it as a **note** on the item, not a phase. |
| Rewrite ROADMAP.md from scratch each quarter | ❌ | **Edit in place and snapshot.** A full rewrite is the bulk-reset anti-pattern, and Terraform's overwritten `ROADMAP.md` is the example to avoid. |

## Final vocabulary

### Columns (what a customer may rely on)

| Column | Engineering state | Customer may rely on | Time label |
|---|---|---|---|
| **Now** | In build. Named owner, work started. | We are building this. | None |
| **Next** | Design settled and an owner assigned, but build has not started. | This is queued after Now. It is an order, not a date. | None |
| **Later** | Direction chosen or still being explored. No staffing commitment. | We believe this matters. It may change or be dropped. | None |

### Item states

- **`exploring`**: for ideas still being researched. These sit in **Later** with no timing at all.
- **`delayed`** and **`descoped`**: set on the item itself, with a one-paragraph reason and a workaround.
- **`not planned`**: includes cancelled items. Give a reason and the condition that would change it. Keep it visible for at least one review cycle.
- **`shipped`**: close the item with a link to the changelog entry.
- **`proposed`**: a separate label for community requests. A popular request never reads as a plan.

### Phases and the beta note

- **Phase labels** (`exploring`, `in design`, `private preview`, `public preview`, `GA`) describe what customers may rely on, not when.
- **Beta:** show "Engineering calls this beta" as a note on the item. Once the access rules, SLA and change-notice terms are written (`api-beta-program`), map it to `private preview` or `public preview`.
- **Quarters, if you add them later:** allowed only on items in `private preview` or later, always next to the phase ("Q1 – private preview"). They also need the four promotion conditions from step 2 of the skill. Finance sign-off on revenue-recognition exposure is one of them. Don't print a bare quarter.

### Card format

```markdown
**<Problem-first title>** `RM-###`
Status: <Now/Next/Later> · <phase or exploring>
Timing: none
What it solves: <one or two sentences, from the user's side>
Discuss: <link to a Discussions thread; items are locked>
Updates: <dated status changes, newest first>
Shipped: <changelog link, added on close>
```

### Titles

Examples only. Replace each with the real customer problem.

- "Rate limiter v3" → "Know your remaining rate limit before you hit it"
- "Auth revamp" → "Scope an API key to one project"
- "Dashboard 2.0" → "Find the slowest endpoints in one view"

### README

> Now / Next / Later is a framework by Janna Bastow (ProdPad). Columns describe engineering state, not dates. This roadmap is for information only. It is not a commitment to deliver any feature, and plans and timing may change at our discretion. Please make purchasing decisions based on features available today.
>
> Maintainer: `<name>` · Last reviewed: `<date>`

Counsel approves the final wording of the disclaimer.

### Maintenance, replacing the quarterly rewrite

1. Keep each card as its own GitHub issue with a stable `RM-###` ID. `ROADMAP.md` becomes an index that links to them. A file cannot give per-item subscriptions or locked comments, but issues can.
2. Review **monthly** and touch every item: confirm it, move it, or mark it `not planned`.
3. Snapshot at each review, for example `archive/2026-11.md`. Don't rely on git history alone to show what you promised.
4. Fill the gate before listing anything. Never publish security work, unannounced deprecations, pricing, partner names, competitive bets, customer-specific commitments or internal plumbing.

## What would change this, and what must happen before launch

- **Launch preconditions:**
  - Sales leadership and the CEO sign the citation rule: reps cite only the public page, at the level printed on it.
  - Inventory every existing contract that names a roadmap item.
  - Handle pre-page slips first.
  - Check the MSA and self-serve terms for a "purchases not contingent on future functionality" clause.
- **If sales will not sign the citation rule:** the skill says to publish nothing yet and fix sales governance first.
- **If you really want dated quarters:** that is the "like Stripe" rung. It needs existing preview phases, few slips last year, buyers who plan around your dates, and finance review.
- **If you have regulated enterprise buyers:** add NDA customer briefings alongside the page.
- **If you want a voting board:** it needs a named triage owner. Locked items with debate in Discussions is the default.

If any of these differ from what I assumed, tell me which. I'll re-rank the posture and redo the affected sections.