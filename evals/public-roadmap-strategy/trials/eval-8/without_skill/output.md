Verdict: keep the Now / Next / Later columns. Change four of the other six decisions and drop one claim. Below, each decision with its fix, then the final vocabulary.

## Sanity check

1. **Columns and book credit: partial.**
   - Now / Next / Later comes from Janna Bastow (ProdPad, 2012), not from the book.
   - I could not confirm that the book covers this format. Check it before you credit it for the format.
   - Safe wording: credit Bastow for the format. Cite the book only for the ideas you took from it, such as outcome-based roadmaps.
2. **"Next = about two months": change it.**
   - Now / Next / Later is deliberately fuzzy about time. Your definition gives Next a length, and quarter labels add a second time system.
   - A quarter is 3 months and Next is 2, so the two systems disagree.
   - Define the columns by confidence, not duration.
3. **Quarter on every card: change it.**
   - A quarter label on a research idea reads as a date promise. Users will quote it back to you.
   - I could not verify your claim about GitHub's roadmap. Even if it is true, it does not oblige you to copy it.
   - Put a quarter on Now and Next cards only. Later and exploring cards get no date.
4. **Card titles: change them.**
   - "Rate limiter v3" and "Dashboard 2.0" name a solution and imply a version promise.
   - "Auth revamp" says nothing: it does not tell the reader what changes for them.
   - Title each card with the user outcome. Put the version in the card body.
5. **Delete what won't happen: change it.**
   - Silent removal makes users assume you forgot. It also hides your track record.
   - Move the card to a "Not planned" column with a one-line reason. Close the linked issue with the same reason.
6. **"beta" whenever engineering says so: change it.**
   - An unwritten rule gives inconsistent tags. Users will read "beta" as a stability promise.
   - Define the stage by written criteria. Product sets the tag, with engineering input.
7. **Rewrite ROADMAP.md each quarter: change it.**
   - A full rewrite erases shipped, moved and dropped items. It conflicts with your own "Not planned" and accountability needs.
   - Edit in place all quarter. At quarter end, move Shipped cards to an archive and keep the file's git history.

## Final vocabulary

### Columns

| Term | Definition |
|---|---|
| **Now** | In active work. We expect to ship it in the current quarter. |
| **Next** | Committed to build after Now. Scope is settled. Order may change. |
| **Later** | We want to do this. Scope and timing are open. |
| **Exploring** | We are researching the problem. No commitment. |
| **Shipped** | Released. Kept for one quarter, then archived. |
| **Not planned** | Considered and declined, with a reason. |

### Card rules

- **Title:** the user outcome, for example "See and raise per-key rate limits". Do not use version numbers or "revamp" in titles.
- **Quarter label:** Now and Next cards only, in the form `Q4 2026`. If a card slips, change the label and add a one-line note on the card.
- **Stage tag:** one per card, set by product, never by column.
  - `private beta`: invited users only. It may break or change.
  - `public beta`: open to everyone. The API may still change. No SLA.
  - `GA`: stable, covered by the SLA and the deprecation policy.
  - Engineering saying "it's in beta" starts the review. It does not set the tag.
- **Dropping a card:** move it to Not planned with a one-line reason and close the issue.

### Maintenance

- Edit `ROADMAP.md` in place during the quarter.
- Each quarter, run a review: archive Shipped cards, re-sort Next, and re-check Later against the criteria.
- Link the archive and `CHANGELOG` from the README.

### README disclaimer

> Roadmap items are plans, not promises. Dates are quarters, shown only for Now and Next. Dates and scope can change.

### README credit (draft)

> Format: Now / Next / Later, created by Janna Bastow. Outcome-based framing informed by *Product Roadmaps Relaunched* (Lombardo, McCarthy, Ryan, Connors; O'Reilly, 2017).

Check that last citation against your copy of the book. The authors and year are from memory.

Next: decide whether Exploring is its own column or a tag on Later cards. That is the one open choice, about 2 minutes.