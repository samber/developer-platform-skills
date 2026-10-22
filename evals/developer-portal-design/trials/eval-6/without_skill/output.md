**Recommendation:** don't put one number in the business case. Put a range, label it as assumptions, and commit to a measured number after a 2-week pilot with a holdout group.

## What to tell leadership

**Headline:** "Plan for about 80 fewer tickets a month, roughly 20% of volume. Floor is about 35 and ceiling about 130. We replace the estimate with a measured figure after the pilot."

**Why not 240 (the 60% figure):**
- The 60% is your gut read. It is not measured.
- Those users already had a search box and still filed a ticket, so they are the people self-serve already failed. Many answers may be buried, unclear, or missing.
- A chat widget does not remove every how-to ticket. It removes the ones where the bot finds the right page, answers correctly, and the user accepts the answer.

**Model (every factor is an assumption until measured):**

`removed = 400 × share how-to × answer exists in docs × bot answers correctly × user does not file anyway`

| Scenario | How-to | In docs | Correct | Accepts | Removed/mo |
|---|---|---|---|---|---|
| Low | 60% | 60% | 60% | 40% | ~35 |
| Base | 60% | 80% | 75% | 55% | ~80 |
| High | 60% | 90% | 85% | 70% | ~130 |

The ranges are my estimates. They are not benchmarks.

Vendor deflection claims of 50–70% usually count chats that ended without a ticket. That is not the same as tickets removed.

**Money:** removed tickets × your fully loaded cost per ticket, minus run cost. Run cost is small, likely tens to a few hundred dollars a month in model and hosting fees at this scale, plus maintenance time. Insert your own cost per ticket.

**Also say:**
- Wrong answers can create tickets and hurt trust. The design below limits this.
- Value beyond deflection: a log of questions the docs could not answer. That becomes a prioritized docs backlog.
- Your 60% matters less than the share of tickets where the docs already hold the answer. The audit below measures that share.

## Step 1: Audit 100 tickets (about half a day to a day)

1. Pull 100 random tickets from the last 3 months.
2. Label each: how-to / bug / account / feature request / other.
3. For each how-to ticket, label whether the answer exists in the docs: yes, partially, or no.
4. Test: could you find it with the current search in under 2 minutes?
5. Replace the "How-to" and "In docs" columns above with your real numbers.

If many answers are "partially" or "no", fix the docs first. A chatbot over bad docs gives confident wrong answers.

## Step 2: Build

**Architecture: retrieval-augmented generation (RAG) over the docs.**

1. **Ingest.**
   - Read from the docs source (markdown), not from crawled HTML.
   - Split by heading.
   - Store the URL, anchor, product, version, and last-updated date on each chunk.
   - Re-index on every docs deploy.
2. **Retrieve.**
   - Use hybrid search: keyword (BM25) plus embeddings, then a reranker.
   - Take the top 5–8 chunks.
   - Filter by product and version when the page context is known.
3. **Answer.**
   - Use one strong model (Sonnet-class) with a strict prompt: answer only from the retrieved chunks.
   - Every claim must carry a citation link to the page and anchor.
   - If retrieval is weak, say "I couldn't find this" and hand off to a ticket. Do not guess.
4. **Gate.** Before showing an answer, run cheap checks:
   - Is the answer supported by the retrieved text?
   - Is the question in scope (not billing, bugs, or account issues)?
   - A small model or a classifier can do this. TypeSafe Jev fits these yes/no and routing judgments well.
5. **Escalate.**
   - Show a "Still stuck? Contact support" button on every answer.
   - It opens the ticket form pre-filled with the conversation and the cited pages.
   - This turns failed deflections into better tickets and cuts agent triage time.
6. **Safety.**
   - Treat user text as untrusted (prompt injection).
   - Don't log PII.
   - Rate-limit per session.
   - Never let the bot promise refunds, dates, or SLAs.
   - Keep it read-only with no tools.

**Placement matters more than model choice.** Put the widget on the docs pages and also on the support form, as "Try this first" before the user submits. That is where the tickets you want to remove come from.

## Step 3: Evaluate before launch

1. Build a golden set of 150 real questions from the audit, each with the correct answer and source page.
2. Score three things:
   - Answer correctness.
   - Citation validity (does the link support the claim?).
   - Correct refusals (does it decline questions that docs cannot answer?).
3. Run this set on every prompt, model, or index change.
4. Launch gate: set your own bar. A reasonable start is at least 85% correct on answerable questions and under 5% confident-wrong answers.

## Step 4: Roll out and measure

1. Week 1: internal staff and support agents only.
2. Weeks 2–3: 50% of docs visitors see the widget. The other 50% are the holdout group.
3. Compare tickets per 1,000 docs visitors between the two groups. That difference is your real deflection. Do not use "chat ended without a ticket" or thumbs-up rates as the deflection number.
4. Track alongside:
   - Resolved-by-bot rate (the "Did this answer your question?" yes rate).
   - Escalation rate.
   - Share of "couldn't find" answers.
   - Cost per conversation.
5. Weekly: read the "couldn't find" and thumbs-down queries. Fix or write the missing docs. This loop is where lasting ticket reduction comes from.

## Cheaper alternatives to compare

- **Fix search** (synonyms, ranking, no-result logging). Cheap and helps everyone.
- **Suggested articles on the ticket form.** Small build, often catches much of the same deflection.
- Mention these in the business case. They set the baseline the chat widget must beat.

## Next action

Pull 100 random tickets from your ticketing tool and start labeling. About 3 hours for the labeling. Send me the counts and I'll rebuild the table with your real numbers.

I did not inspect your repo or any internal files, so every number above is a modeled assumption, not a measurement.