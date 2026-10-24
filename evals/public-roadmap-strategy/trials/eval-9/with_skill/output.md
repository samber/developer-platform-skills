**Next action (today, 10 min):** email your legal lead and ask for every order form, SOW, side letter, RFP answer and security questionnaire that mentions residency. Do not publish anything before that comes back.

I read the skill and its three references. I skipped the interview and worked from your facts. Assumptions and open answers are at the end.

## Bottom line

Do not ship "residency: Next" first. The page is the last step, and it doesn't fit the full roadmap you want by month end.

Three reasons:

1. **A slip already hurt trust.** The skill says to fix that communication before adding surface. The H1 promise on stage was a committed item, and it was missed silently.
2. **Two order forms name residency.** An order-form item is a binding deliverable, whatever the MSA future-functionality clause says. Those two customers must hear from their account owner before the public page shows anything.
3. **"Next" has to be true.** The skill defines Next as an engineering state: in build, with a named owner. If residency isn't staffed, the page can only say "Exploring". A page that re-promises it a second time costs more trust than silence.

## Recommended bundle: repair first, direction page by month end, horizon roadmap in January

This is the candidate I recommend. The other two are below it.

| Piece | What | When |
|---|---|---|
| Residency repair | Private notices, then an email to all customers and the 300 attendees | W1–W3 |
| Direction page | Themes, undated, with residency as an honest item | By month end |
| Horizon roadmap | Now / Next / Later with 5–8 items | After 2 decided review cycles, about January |
| Customer briefings | Same gate, same disclaimer, product present | Offer from W3 |

Why this fits:
- **Enterprise buyers.** Customer briefings rank second on value for you, and regulated residency buyers often need them.
- **6 hours a month.** A hard deadline plus low owner hours promotes the direction page.
- **Two-cycle rule.** The skill says to publish a horizon roadmap only after two internal reviews produced decided statuses. You can't finish that by month end.

The other candidates:

- **B. Horizon page with 5 items by month end.** This is the CEO's version. It breaks the two-cycle rule, and it fails unless the citation rule is signed (below). It also leaves residency as the one item with a public history.
- **C. Dated quarters ("like Stripe").** Ineligible. You have no preview phases, residency just slipped, and finance hasn't reviewed it. It becomes eligible when all four hold: phases exist, few items slipped, buyers plan around dates, and finance has reviewed ASC 606 exposure.

## Hour budget (6h, my estimate, replace after week 1)

| Task | Time |
|---|---|
| Ask engineering the residency state (below) | 1h |
| Brief legal and finance on the contract inventory | 0.5h |
| Write and review the private notice | 1h |
| Draft the direction page | 1.5h |
| Write the citation one-pager for CEO and sales sign-off | 0.5h |
| Public email, page QA, approvals | 1.5h |

Legal and account owners carry the rest of the contract work. Your 6h covers the product side only.

## Steps

**1. Get the residency truth (W1, 1h).** Ask engineering three questions:
- Is it staffed, with a named owner?
- What is the earliest honest private-preview start?
- What is the blocker?

Then pick the state:
- **In build, with an owner:** it may show as `Next`, with no date. A quarter appears only from private preview onward, and you have no previews.
- **Not staffed:** it shows as `Exploring`. The CEO either funds it or accepts that status. That's a product decision, and the CEO should make it knowingly.

**2. Contract inventory (W1–W2, legal runs it).** For each hit:
- Legal and finance review it.
- The account owner calls the customer.
- Finance checks revenue-recognition exposure: a dated, specified feature can defer revenue.
- Include the stage statement. Ask counsel whether it counts as a "public comment" under the MSA clause.

**3. Private notice to the two order-form customers (W2).**
- The account owner calls first.
- Legal checks the notice against the order-form terms before it goes out. A slip can trigger notice, credit or termination rights.
- They hear it days before the public update.

Notice (third-party text, written in plain prose):

> Subject: Multi-region data residency: timing update
>
> At our user conference last October we said multi-region data residency would be live in the first half of this year. That did not happen, and we should have told you sooner. Your order form references residency, so we are telling you directly before anything is published.
>
> Where it stands: [in build with a named owner / still being scoped]. [Earliest honest milestone, or "we cannot yet give a date".] Until it ships: [workaround or interim control, if any]. Your account owner, [name], will walk you through the order-form terms and what we can offer.

**4. Public acknowledgment (W3, after step 3).** Email all customers and the conference attendees, and add a changelog entry. Use the slip template:

> **Update: Multi-region data residency is [delayed / not yet scheduled].**
> What changed: At our user conference we said residency would be live in the first half of the year. It is not. [One-paragraph plain reason.]
> What this means for you: Status is [Next / Exploring]. We are not giving a date until it reaches private preview.
> Workaround: [what to use meanwhile].
> Questions: [one channel].

**5. Citation rule (W1–W3, 0.5h).** This is a launch gate. Sales and the CEO sign a rule covering anyone customer-facing, including execs on stage:
1. Cite only the public page, at the status printed on it.
2. Give no dates in emails, decks or keynotes unless the page shows that date.
3. Legal and finance approve any roadmap item written into an order form.
4. A deal that depends on an unbuilt feature goes to product, not to a rep.
5. Account owners tell contract-dependent customers about a slip before the public update.

The CEO's own stage statement caused this, so the CEO must sign it. If the CEO or sales leader won't sign, every public posture is deleted. Fix sales governance first, with no page.

**6. Direction page (W3–W4).** Contents:
- Three to five themes in problem-first wording, for example "Keep contract data in the region your customers require".
- A status per item: `Exploring`, `Next` or `Later`, each defined by engineering state and carrying no date.
- A negative state (`not planned` / `delayed`) that stays visible for at least one review cycle.
- A "last reviewed" date and a named maintainer.
- A link to the changelog.
- The disclaimer on the page, not in a footer:

> This roadmap is for information only. It is not a commitment to deliver any feature, and plans and timing may change at our discretion. Please make purchasing decisions based on features available today.

Counsel approves the final wording.

**7. Exclusion gate.** Keep these off the page: pricing or packaging (if residency is a paid add-on, check it for the Osborne effect), partner and cloud-provider names, security work, and customer-specific commitments. Those two commitments live in the order forms, not on the page.

**8. Feedback and lifecycle.**
- Roadmap items are read-only.
- Every item has a stable ID and links to one feedback channel.
- One owner and one backup review monthly: confirm, move, or mark `not planned`.
- Close shipped items with a changelog link.
- Snapshot the page at each review.

## Launch checklist

- [ ] Engineering gave the residency state.
- [ ] Contract inventory complete, with legal and finance review.
- [ ] Both order-form customers contacted by their account owners.
- [ ] Citation rule signed by the sales leader and CEO.
- [ ] Counsel approved the disclaimer.
- [ ] Public acknowledgment sent after the private notices.
- [ ] Direction page has an owner and a review date.

## Measurement

- **Freshness:** 100% of items touched each review.
- **Silent removals:** zero.
- **Slip rate:** track it before moving to dated quarters.
- **Close rate:** 100% of shipped items closed with a changelog link.
- **Sales incidents:** roadmap items in new order forms. Baseline this month.
- **"When will X ship" volume:** compare before and after.

## Assumptions and open questions

- **Quarter-end timing.** You say it's November. The system date I have is late October, so I used week numbers rather than calendar dates.
- **Citation rule.** Whether the CEO will sign is unanswered. If not, drop to no public page, which flips the plan.
- **MSA exceptions.** I assumed the clause exempts features "expressly provided in any Order". Counsel should confirm.
- **Slip rate.** I don't know how many other expected items slipped last year. If many did, the January horizon page needs more than two review cycles.
- **Other mentions.** I assumed no residency mentions beyond the two order forms. The inventory may find more.

**Next:** send the inventory request to legal, then book 30 minutes with engineering for step 1.