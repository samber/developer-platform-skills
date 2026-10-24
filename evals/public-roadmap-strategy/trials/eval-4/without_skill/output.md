**Start here:** book 90 minutes this week with your PM or eng lead. Ask one question: "Which of the top 10 requests would we commit to building in the next two quarters?" Your plan turns on that answer, because a public "Next" column is a promise.

I'd keep your idea of a public roadmap with an embedded board. I'd change four of your decisions.

## What to change

| Your plan | Problem | Change |
|---|---|---|
| Auto-promote top 10 to Next | Votes aren't commitments. GraphQL has 900 free-tier votes and may never ship. Duplicates split votes, and some of the 1,400 requests may already be built or obsolete. | Promote by human decision with an eng owner. Show the rest as "Under consideration". |
| Shut down the old board the day the roadmap goes live, start with zero requests | About 1,400 voters get no notice, the 900 GraphQL voters lose their signal, and a roadmap with nothing on it looks dead. | Export everything and run the old board read-only for 60 days. Carry the useful requests over. Email the voters. |
| Rank Later by vote count | Votes track crowd size, not payments value. Free-tier accounts dominate, so you'd rank by who is loudest. | Show votes, but sort by triage score: paid voters, payment volume, strategic fit. |
| Triage "when I can" | The board already went a year untriaged. A public roadmap makes the same neglect visible. | Set a fixed weekly budget and a status SLA (below). |

## Timeline (about 4 weeks, launch ≈ 2026-11-24)

**Week 1: decide and measure (about 6 hours)**
1. Export all 1,400 requests with voter emails, tiers and dates.
2. Join the voter emails to billing. Count voters who are paid, and weight by plan or payment volume. Do this at least for the top 50.
3. Hold the 90-minute eng session. Output: for each top-10 item, one of `Next`, `Later`, `Under consideration`, `Not planned`. Each needs a one-line reason.
4. Write the GraphQL answer first (see below).

**Week 2: triage the board (about 6 hours)**
1. Read the top 100 by votes, about 3 hours. Merge duplicates, mark shipped items, and tag each by area and by paid-voter count.
2. Handle the tail of about 1,300 in bulk. Don't read each one. Mark requests older than 12 months with 2 votes or fewer as "archived, resubmit if still relevant".
3. Write 5 canned replies: shipped, merged, planned, not planned, needs info. Triage speed depends on these.

**Week 3: build the roadmap**
1. Set the columns: `Now`, `Next`, `Later`, `Under consideration`, `Shipped`, `Not planned`.
2. Set the Next rule: an eng owner exists and the item is realistic within about two quarters. Cap Next at 5 to 7 items. Fewer promises, kept, beat ten broken ones.
3. Add a banner on the roadmap: "Roadmap shows intent, not dates or commitments."
4. Seed Shipped with 5 to 10 items from the last year, tagged "you asked, we built". This makes the roadmap look alive from day one.
5. Invite 10 to 20 trusted paid customers for a private preview. Collect feedback.

**Week 4: launch**
1. Send the announcement to the community and to all old-board voters. Segment the email: voters on items now in Next or Shipped get a personal note naming their request.
2. Switch the old board to read-only with a banner and redirect to the new roadmap. Keep it live for 60 days, then archive. Never delete it.
3. Post a changelog entry and a community post. Link the roadmap in the docs navigation.

## GraphQL (900 votes)

Do not hide it and do not auto-promote it. Publish a direct reply:
- If you'll build it: put it in Next or Later with a one-paragraph reason.
- If you won't: mark it "Not planned" and give the reason. Offer an alternative (SDKs, REST patterns).
- If unsure: mark it "Under consideration" and say what you need to learn, with a decision date.

State the paid-voter count honestly if asked. A clear no earns more trust than a silent yes.

## Ongoing triage: 45 minutes per week

1. Review new requests (15 minutes). Apply a canned reply or a status.
2. Update paid-voter counts on the top 20 (10 minutes).
3. Monthly (extra 60 minutes): review Next with eng, move shipped items, update the changelog.

**SLA to publish:** every new request gets a first response within 10 business days. Anything slower, say so on the board. If you can't hold 45 minutes per week, ask for a second owner before launch, not after.

## Metrics (check at 30 and 90 days)
- Share of new requests with a status within 10 business days (target: above 90%).
- Next items shipped on schedule (target: at least 70% within two quarters).
- Paid-account share of new votes, to see whether free-tier skew is easing.
- Complaints about the old board closure (target: under 10).

## Risks
- **Broken promise in Next:** the cap and the eng-owner rule are your control.
- **Free-tier backlash over de-prioritization:** publish the triage criteria so the ranking isn't a surprise.
- **Roadmap goes stale:** the 45-minute routine is the guard. A stale roadmap is worse than none.

## Open questions
1. Can you join voter emails to billing data, or only to account IDs?
2. Does the vendor board support import or read-only mode? Check this before committing to week 4.
3. Who in eng can sign off on Next items?

**Next action:** export the board and send your PM or eng lead the 90-minute session invite today.