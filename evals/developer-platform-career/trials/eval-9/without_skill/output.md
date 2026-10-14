# Applying for Partner Engineer with NDA-covered work

## Short answer

Apply now, but not with your CV as-is. Partner Engineer is close to your job, but not the same one. Rewrite the CV, build one small public artifact in parallel, and offer to design live in interviews.

## 1. It's not quite the same job

| | You today | Partner Engineer (typical) |
|---|---|---|
| Side | Customer of platforms | Vendor of the platform |
| Audience | Your internal systems | External ISV developers |
| Output | Working flows | Working flows, plus docs, samples, office hours, certification reviews |
| Success | Uptime, fewer errors | Partner adoption and time-to-first-integration |
| Extras | | Product feedback loop, sometimes co-sell, travel, escalations |

Your edge is that you live the pain the partners feel. Your gap is that you haven't taught or supported outside developers, and the recruiter can't see that from your CV.

## 2. Ask the recruiter first (5 minutes)

1. Which product or platform do partners build on, and what are the extension points (APIs, SDKs, marketplace)?
2. Who are the partners: ISVs, SIs, or both? Is the role pre-sales, post-sales, or both?
3. Is there a quota, a co-sell target, or on-call?
4. What does the interview loop look like? Is there a take-home, a live design, or a portfolio review?
5. Is public work expected, or is a design discussion enough?

Question 5 settles most of your NDA worry. At this level, most loops are live design discussions, not portfolio reviews.

## 3. CV rewrite: same facts, ecosystem vocabulary

NDA usually covers documents, names, and numbers. It does not cover your skills or generic descriptions. Check your contract if unsure.

Swap internal-ops phrasing for partner-facing phrasing:

- **Before:** "Maintain iPaaS flows between ERP and WMS."
- **After:** "Designed and operated event-driven integrations across ERP, warehouse, and third-party carrier APIs, with idempotent retries, dead-letter handling, and replay."
- **Before:** "Fixed integration errors."
- **After:** "Cut recurring integration failures by X% by standardizing error classification and alerting. Mean time to resolve dropped from X to Y."
- Add a line showing you've worked with outsiders: "Onboarded two external carriers onto our integration layer, writing the technical spec, test plan, and cutover checklist."
- Add a line showing you've explained things: "Wrote runbooks and trained support staff on triage."

Rules:
- Anonymize: "mid-size manufacturer", "two third-party carriers". Keep the Marrowfield employer line, since that is public.
- Use ranges or relative numbers (percentages, order of magnitude), not exact internal figures.
- Only claim what you did. If you never wrote partner-facing docs, don't say you did.

## 4. Build a public substitute (2–3 weekends)

Pick **one**. They are ordered strongest first.

1. **A small integration on the target company's own public API or SDK.**
   - Build it, write a quickstart, and note where the developer experience was rough.
   - This is the closest thing to the job itself and proves you've read their docs.
2. **A reference implementation of the reliable-integration patterns you use daily.**
   - Retries with backoff, idempotency keys, a dead-letter queue, and replay.
   - Use public sandbox APIs and fake data, with a clear README and an architecture diagram.
3. **A short article, "Error handling between ERP, WMS and carrier APIs: patterns that survive production."**
   - Keep it generic and use no internal examples.

Clean-room rules:
- Use no code, schema, naming, diagram, or number from Marrowfield, even reworded.
- Work on your own time and equipment.
- Read the IP clause in your employment contract. If unsure, ask HR or a lawyer.
- Don't mention carriers or tools in a way that could identify the employer's setup.

**Redacted design doc as a writing sample:** only with written permission from Marrowfield. Otherwise, write a fresh design doc for a fictional company with a similar shape. It is no worse a sample, and it carries no legal risk.

## 5. Turn the NDA into a signal

Tell the recruiter and the hiring manager something like:

> "My design docs are under NDA, so I can't share them. I'm happy to walk through a design live on a whiteboard, and I've published [artifact] as a public example of how I think."

Hiring managers in this space read that as professionalism. Prepare 3 stories with generic details:
- An integration that failed in production: cause, fix, prevention.
- Onboarding an external party (a carrier) onto your layer: friction and how you removed it.
- Explaining a technical issue to a non-expert.

Also prepare to do a design exercise live. A typical prompt: "Design a reliable integration between a partner's ERP and our API."

## 6. Sequence

1. **Today:** reply to the recruiter, ask the 5 questions, and ask for the job description.
2. **This week:** rewrite the CV and write a short cover note.
3. **Next 2–3 weeks:** build the artifact. Send the link as a follow-up to the recruiter, which gives you a reason to re-contact them.
4. **Don't wait for the artifact to apply.** Big-company pipelines take weeks, and the work can land mid-process.

## 7. Two checks before you commit

- Compare level and comp. Moving from a customer-side senior role to a vendor-side one can be a lateral move or a step down.
- Ask yourself whether you want to teach and support outside developers daily. If not, this will feel like a different job.

I can draft the recruiter message and the rewritten CV bullets if you paste your current CV.