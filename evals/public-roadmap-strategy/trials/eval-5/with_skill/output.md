# Brightmoor Systems: what has to change before the dated quarterly roadmap launches

I followed the `public-roadmap-strategy` skill and its two references. This is a review for you and counsel to act on. I'm not a lawyer and none of it is legal advice. All final wording goes to counsel, or to outside counsel while your counsel is away.

**Recommendation: don't launch it as planned.** Four things block it, and the data room plan should be dropped.

## Blockers, ranked

### 1. The disclaimer is wrong for a private company

- **Why it fails:** Brightmoor files nothing with the SEC. A line about "risks and uncertainties described in our SEC filings" points to documents that don't exist.
- **Safe harbor:** The PSLRA safe harbor protects forward-looking statements in securities disclosures by reporting companies. A private company can't borrow it, so it protects nothing here.
- **Side effect:** Securities language on a customer page makes the page look like a securities disclosure. That works against you if the same page goes to investors.
- **The fix:** Delete the paragraph. Use a short customer-facing disclaimer with these four elements, on the page itself:
  1. The page is for information only.
  2. It is not a commitment, promise or obligation to deliver any feature.
  3. Plans and timing may change at your discretion.
  4. Purchase decisions should rest on features available today.
- **Draft for counsel to edit:**
  > This roadmap is for information only. It is not a commitment to deliver any feature, and plans and timing may change at our discretion. Please make purchasing decisions based on features available today.
- **Related surfaces:** Put the same text on the first slide of any NDA briefing deck. Also check docs and blog posts for sentences that promise unbuilt features.

### 2. The four order forms override everything else

- **The override:** A feature written into an order form binds you, whatever the page disclaimer or the MSA clause says. The "not contingent on future functionality" clause usually exempts anything "expressly provided in any Order".
- **Before launch:**
  1. Inventory the four forms: item, customer, date or phase promised, remedies, renewal date. Also search for SOWs and side letters, because there may be more than four.
  2. Counsel and finance review each one.
  3. Each account owner talks to the customer. If the public item will differ from the order-form wording, or a date is shaky, they hear it privately before the page goes live.
- **Public page:** Customer-specific commitments don't go on it. They stay in the order form, and the public item is rewritten problem-first, with no customer name.
- **Revenue recognition:** A dated, named feature published to every customer is what ASC 606 reviews look for. It can become a separate performance obligation and defer revenue. Finance, and likely your auditors, must review before any date goes public.

### 3. The self-serve terms have a gap

- **The gap:** About 2,000 click-through accounts have no "future functionality" clause. Your MSA protects only contracted customers, and a dated page reaches all 2,000 self-serve accounts with nothing behind it.
- **Counsel's decision:** Whether to add an equivalent clause to the click-through terms. That includes how to give existing accounts notice of the change under your terms' amendment mechanism. Counsel should also sign off in writing on the residual risk for existing contracts.
- **Limits of the clause:** In many jurisdictions it can't exclude misrepresentation or deceptive-advertising claims. The page's own accuracy is the residual exposure. Never publish an item you already know is off.

### 4. Dated quarters is the most demanding option, and you haven't shown it's eligible

The skill treats dated quarters as the starved option. It has the highest compliance cost and the lowest efficiency, and each date is a standing liability. It needs all four conditions below.

| Condition | Status |
|---|---|
| Release phases exist (private preview, public preview, GA) | Unknown. You need to tell me. |
| Few items customers were told to expect slipped last year | Unknown. Get the number. |
| Buyers plan budgets or migrations around your dates | Plausible: four order forms name items. |
| Finance has reviewed revenue-recognition exposure | Not done. |

Two more gates apply before any public posture:

- **Sales rule:** If the real trigger is "sales keeps promising unbuilt features", every public posture is off the table until the sales leader and CEO sign the citation rule. Otherwise reps get a bigger catalogue to promise from. Four roadmap items in order forms suggests this is live.
- **Customers vs investors:** If the real driver is the raise, you are using a customer page to do an investor's job (see section 5).

## Candidate bundles

| Bundle | What it is | Fit |
|---|---|---|
| **A. Horizon roadmap (recommended)** | Undated buckets defined by engineering state ("in build, named owner"). Locked items with one feedback channel. Dates only for items in private preview or later, each with its phase. | Answers "what's coming" and gives sales a citable source without a date liability. Cheapest to keep honest. |
| **B. Horizon roadmap plus NDA customer briefings** | A, plus a briefing deck with the disclaimer on slide one and a log of who saw what. | Best if enterprise buyers need roadmap evidence. Briefings follow the same sales rules, because NDA decks are where dated promises get made. |
| **C. Dated quarters (ineligible today)** | A quarter on every item, each capped by a phase. | Becomes eligible once all four conditions in the table hold. If you launch it anyway, use "Q1 – private preview" rather than a bare "Q1". A bare quarter reads as general availability. |

Bundle A is my recommendation. Move to dated quarters after at least two review cycles, a measured slip rate and finance sign-off. Counsel's absence is a reason to ship the least risky version first.

## 5. Keep the roadmap page out of the data room

- **Different reader, different regime:** The public page is written for customers, with "don't rely on this for purchasing". Investors will rely on what they see, and fundraising communications carry their own anti-fraud exposure. The skill routes investor-facing reuse of roadmap material to counsel.
- **Diligence risk:** In diligence, investors will compare the page, the order forms and your slip history. If any of the four commitments conflict with the page, or dates move, that surfaces as a finding.
- **What to do:** Build a separate investor roadmap or strategy document.
  - It has its own disclaimers, written by counsel.
  - It is consistent with the public page and uses the same status labels.
  - It contains nothing the exclusion gate keeps off the public page unless counsel agrees.
- **Wait until counsel is back for this one.** Link the public page from the data room only if counsel clears it.

## 6. The remaining launch checklist

Each item is a precondition. Items that already satisfy it can be ticked.

1. **Exclusion gate applied row by row.** Keep these off the page:
   - security fixes;
   - unannounced deprecations;
   - pricing and packaging;
   - items that would cannibalize a current plan;
   - partner names and M&A;
   - competitive bets;
   - customer-specific commitments;
   - internal plumbing.

   Name the person who decides edge cases. Record the gate in the policy.
2. **Citation rule signed by the sales leader and the CEO.** It covers reps, solutions engineers, customer success, DevRel and executives on stage:
   - cite only the public page, at the printed commitment level;
   - no dates in emails, proposals or decks beyond what the page shows;
   - legal and finance approve any roadmap item in an order form;
   - a deal that depends on an unbuilt feature goes to product, not to a rep's judgment.
3. **Vocabulary defined on the page.** Cap every date with a phase, and date only items in private preview or later. Add visible `not planned` and `cancelled` states with reasons. Label community proposals separately from vendor plans, and write items problem-first.
4. **Owner, backup and cadence.** Name one owner and a backup, with monthly reviews. Publish only after at least two internal review cycles have produced decided statuses. Each item gets a stable ID and a subscription channel. Shipped items close with a changelog link, and you snapshot the page at each review.
5. **Slip playbook written, and pre-page commitments handled.** The four order-form items are the pre-page commitments. For any slip: change the status on the item (never delete it), give a plain reason and a workaround, and notify subscribers. Contract customers hear privately from the account owner first, after legal has checked the notice against the order-form terms.
6. **Feedback surface.** Default to locked items with one discussion link. Don't launch a voting board without a named triage owner.
7. **Approvals recorded:** product, sales leadership and CEO, counsel, finance (because dates appear). Record dates, and don't launch without all of them.

## What to do in the three weeks counsel is away

- **Get coverage:** Ask your counsel for a delegate, or engage outside counsel for a one-time review of the disclaimer, the clause and the four forms. If no one is available, hold the launch. The risk of waiting is small compared with a binding date on a page that can't be reversed.
- **Do now:** Pull the four order forms and look for others. Compute last year's slip count. Get finance into the dated-items conversation. Draft the citation rule for the sales leader and CEO. Run the exclusion gate on the internal roadmap. Write the slip playbook.
- **Not before approval:** Don't publish. Don't change the self-serve terms. Don't send anything roadmap-related to investors.

## Questions the skill would normally ask first

I haven't had your answers to these, so some of the above rests on assumptions:

1. What triggered the roadmap: sales promises, customer requests, the raise, or leadership transparency?
2. Do you run private preview, public preview and GA phases today?
3. How many items did customers expect last year that slipped?
4. Will the sales leader and the CEO sign the citation rule?
5. How many product-manager hours per month can go into upkeep?
6. What is the launch date, and is this a one-off page or a standing practice?

Answers to 1, 2, 3 and 4 could move the recommendation between bundles A, B and C, or to no public page at all.