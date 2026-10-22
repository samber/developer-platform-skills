**Put a range in the business case, not a single number. Also commit to measuring it.**

Use the paragraph below as the deliverable text for leadership.

> We receive ~400 tickets/month. A sample audit (n=100, due before launch) will confirm what share are "how do I" questions answerable from existing docs. Our working estimate is 60%, about 240 tickets. Published figures for AI docs assistants (vendor-reported, not independent) put deflection at 20–40% of total tickets. Applied to our volume, that is 80–160 tickets/month. We plan on **~80/month (20%)**, treat 40/month (10%) as the floor, and will report actuals after a 12-week measured pilot. We are not committing to the high case.

Next action (about 2 hours): pull 100 random tickets from the last 3 months. Tag each one as "answered on a specific docs page: yes / no / partly". Record the page URL when yes.

## Why a range, not one number

- **The 60% is a rough read.** A sample of 100 gives about ±10 points at 95% confidence. That is enough to defend it.
- **"Answered somewhere in docs" is not "deflectable."** These customers already had a working search box and still filed a ticket. They either didn't find the page, didn't trust it, or didn't try. The assistant only fixes the first of these.
- **Every deflection figure is vendor-reported.** The skill's references say the same: validate against your own baseline before claiming ROI.
- **Low volume makes the signal noisy.** 400 tickets/month has a month-to-month standard deviation of roughly 20 (Poisson). A 40-ticket drop is not reliably visible in one month. A 80-ticket drop shows in 1–2 months. Judge the floor case over 3 months.

| Case | Share of all tickets | Tickets/month | What must be true |
|---|---|---|---|
| Floor | 10% | 40 | Assistant answers some of the 240, many users never try it |
| Plan | 20% | 80 | About a third of how-to tickets removed |
| Ceiling | 40% | 160 | Two thirds of how-to tickets removed. Don't promise this |

Cheaper fix to price alongside it: if the audit shows most answers exist but are hard to find, fixing IA and search may beat the chatbot. Include that option in the case.

## How to build it

This is the developer-portal-design skill, step 5 (search plus AI assistant). I read it and its three references in full. The skill targets external API-consumer portals. I'm assuming your docs site is customer-facing, which fits.

**Default: buy, don't build.**
- 900 pages is small. A hosted RAG answer product is the lowest-effort path. Vendors report weeks to deploy, against 6–12 months of internal development. That figure is vendor-reported.
- Candidates, depending on your docs platform: Mintlify (built-in assistant), Algolia AskAI (extends search), kapa.ai or Inkeep (standalone widget).
- Custom build is justified only if you have a compliance or data-residency requirement no vendor meets. Even then it needs a named, permanent owner.

**Design requirements (reject any vendor missing these):**
1. **Every answer cites a linkable source page.** No citation, no answer.
2. **Says "I don't know" when docs don't cover the question.** It must not guess.
3. **Sits next to the existing search box.** Don't replace search. Search plus "Ask AI" is the standard pattern.
4. **Unanswered and low-confidence questions go to a docs backlog.** The assistant doubles as a content-gap detector.
5. **Handoff to a ticket.** When it can't answer, it opens the ticket form with the conversation prefilled. Without this you risk a worse experience, not fewer tickets.
6. **Auto-resync on docs publish.** Stale answers are worse than none.

## How to measure it

1. **Baseline, 4 weeks before launch:**
   - Add a required ticket-form field: "Did you search the docs or use Ask AI first?"
   - Tag every ticket "how-to" or "other".
2. **Launch to a holdout if traffic allows.** Show the widget to 50% of visitors for 4 weeks. Compare ticket rates per visitor. This is the only way to separate the widget's effect from seasonality or releases.
3. **Track these metrics:**
   - How-to tickets per month (the headline number).
   - Assistant sessions with no ticket within 24h.
   - "I don't know" rate.
   - Citation click-through.
   - Handoff-to-ticket rate.
4. **Read the "I don't know" log weekly.** It is your docs backlog.
5. **Treat deflection as a watched trend, not a pass/fail gate.** Also watch ticket quality: a falling count with rising escalation severity is a bad trade.

## Optional: classify the audit with Jev

If hand-tagging 100 tickets feels slow, you could run the whole backlog through TypeSafe Jev. Use one Noul per ticket: "Does `ticket.text` ask a how-to question rather than report a bug or request a change?" Check the output against your hand-tagged sample before trusting it. I designed this from the skill text and did not probe the live API.

## Open questions (they change the answer)

I proceeded on these defaults. Tell me if any is wrong.
1. **Audience:** customers using a product or API, not internal staff. If internal, this skill doesn't apply.
2. **Docs platform:** unknown. It re-ranks vendors (a Mintlify site should start with Mintlify's built-in assistant).
3. **Data residency or compliance limits:** assumed none. A yes here is the only thing that promotes a custom build.

**Next:** run the 100-ticket audit, then send me the yes/no/partly counts. I'll turn them into the final range for the business case.