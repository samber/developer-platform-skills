# Nessforth App Marketplace: 10-week plan to Connect

## Bottom line

**"50 partners on stage" can't be 50 shipped, reviewed apps. Reset the number this week.**

- You have zero apps, no reviewer and no pipeline.
- A third party needs 4–6 weeks to build against a new API.
- A new platform typically sees only a minority of committed partners ship on time. Treat that as an assumption and calibrate it on your own week-4 data.
- Realistic outcome for Connect:
  - **10–15 live, reviewed apps.** About half are built by you or co-built with design partners.
  - **25–35 logos in total**, each labeled by status: Live, Beta, or Committed.
- The 50-logo wall is reachable only if unshipped partners are shown as labeled "Coming soon". Don't present them as live apps.

**Next action: book 30 minutes with the VP Marketing in the next two days.** Show the funnel math below and get agreement on the reframed target. A promise she makes on stage that you can't back is worse than a smaller true number.

I assumed Connect is about Dec 12, 2026 and that Week 1 starts Mon Oct 5. Confirm both.

## Decisions needed this week

| # | Decision | My recommendation |
|---|---|---|
| 1 | Redefine "partner on stage" | Three labeled tiers: **Live** (reviewed, listed), **Beta** (in review, demoable), **Committed** (signed, building). Only Live gets a speaking or demo slot. |
| 2 | Debut framing | "Marketplace launches with founding cohort", not "full marketplace GA". Founding cohort is a feature: early-mover perks, featured placement. |
| 3 | Owners | Name one **marketplace lead** (BD or PM, about 60% time) now. Add a **reviewer** and a **developer-experience owner** (docs, sandbox, SDK). |
| 4 | Reviewer | Don't wait for a hire. Use a contract security-minded engineer, or a Nessforth engineer at 50% for 8 weeks. |
| 5 | Incentive budget | Small fund for co-built apps and a hackathon prize pool. Needs an amount from finance. |
| 6 | Legal | Developer agreement, marketplace terms, and revenue-share or "free at launch" decision. Start now. Legal is the longest lead item. |

## Why the checklist can't just be "run": billing is sensitive

Apps will touch invoices, customer PII and payment-adjacent data. Before the first review, extend the doc checklist to cover:

1. **OAuth and scopes:** least privilege, no blanket scopes.
2. **Data handling:** what is stored, where, and retention.
3. **Webhook security:** signature verification, retries, idempotency.
4. **Rate-limit behavior** and graceful failure.
5. **Uninstall:** data deletion on disconnect.
6. **Listing quality:** accurate description, support contact, pricing disclosure.
7. **Pass, fix, or reject rubric** with a written SLA, for example 5 business days.

**Calibrate on your own apps first.** Review the first-party apps in Weeks 3–5. This tests the checklist, finds the vague items, and gives partners real examples.

**Reviewer capacity:** one reviewer handles about 4–5 apps a week. 15 submissions landing in the last week means a two-week queue. Hence the submission deadline below.

## Funnel math (assumptions, recalibrate at Week 4)

Working backward from about 12 live apps, with one known source of leverage:

- **First-party and co-built apps** are the only fully controllable supply. Build 4–6 yourselves.
- **Third-party apps:** assume roughly 1 in 3 interested contacts commits, and roughly 1 in 2 of those ships in time.
- **To get about 6–8 third-party live apps, you need about 40–60 qualified conversations.** That means 150–250 outreach contacts, with warm intros doing most of the work.
- **Where those contacts come from:**
  1. Your existing customers' engineering teams. Ask who already runs scripts or middleware against you.
  2. Adjacent vendors with a reason to integrate: accounting, tax, CRM, ERP, payments and analytics tools.
  3. Implementation agencies and consultancies that already do billing migrations. They get a new revenue line.
  4. Connectors via Zapier, Make or n8n. One listing there is cheap and counts honestly as one.
- **Your own customers matter most.** Nessforth already has customers asking for integrations. Pull the top 10 requests from support, sales and product. That list is your target list.

## Week-by-week plan

| Week | Dates | Focus | Exit criteria |
|---|---|---|---|
| 1 | Oct 5 | Reframe target. Name owners. Start legal. Pull top integration requests. Audit API readiness. | VP signed off on tiers. Target list of 60+. |
| 2 | Oct 12 | Fix developer basics: public docs, sandbox, OAuth app registration, quickstart, app manifest. Begin outreach. Contract reviewer starts. | A stranger can make a first API call in under 30 minutes. 25 outreach contacts sent. |
| 3 | Oct 19 | Developer agreement live. Design-partner calls. Start 4–6 first-party apps. Finalize checklist v1. | 8+ conversations held. First-party builds started. |
| 4 | Oct 26 | **Checkpoint 1.** Count committed partners. Launch a virtual hackathon (2 weeks) with prizes. | See kill rules below. |
| 5 | Nov 2 | Review first-party apps against checklist. Fix checklist. Partner office hours twice a week. | First-party apps pass review. Checklist v2. |
| 6 | Nov 9 | Beta submissions open. Hackathon ends. Draft Connect keynote with real names. | 5+ third-party apps in progress with working API calls. |
| 7 | Nov 16 | **Submission deadline: Fri Nov 20.** Reviewer at full speed. Listing copy and logos collected. | All candidate apps submitted. |
| 8 | Nov 23 | Review, fix, re-review. Short week if US holidays apply. | Every submission has a verdict. |
| 9 | Nov 30 | **Listing freeze: Fri Dec 4.** Final reviews. Marketplace site and listings QA. Announce Committed tier publicly. | Live list locked. Keynote slides final. |
| 10 | Dec 7 | Rehearse demos on prod-like data. Backup recordings for every live demo. Press and partner comms. | Dry run passed. Every on-stage demo has a fallback. |

## Kill rules and checkpoints

- **Week 4 (Oct 26):**
  - Fewer than 15 Committed partners: say so to the VP and move the stage target down to match.
  - Fewer than 6 first-party apps started: add engineering capacity or cut scope.
- **Week 7 (Nov 20):** the deadline is hard. A partner who misses it is shown as Committed, not Live. Moving the deadline for one partner moves it for the review queue too.
- **Any security fail:** the app is not listed. No exceptions for stage-worthy logos.

## Honest framing for the stage

- **Keynote:** one story, 3–5 live demos, a wall showing Live, Beta and Committed logos with clear labels.
- **Do not** show unreviewed apps as available, or count first-party apps without saying they are yours.
- **Do** show the founding cohort with numbers for each tier. Real numbers read as credible, and the audience is developers who will check.

## Risks

1. **Developer experience isn't ready.** The biggest single risk is an API that takes a day to try. Fix before outreach.
2. **Review queue crunch.** Mitigated by the Nov 20 deadline and early first-party reviews.
3. **Legal terms late.** Partners won't commit without a developer agreement. Start in Week 1.
4. **Marketing promises outrunning product.** Lock the public number only after Week 4.
5. **Demo failure on stage.** Pre-recorded fallbacks for every live demo.

## Open questions for you

1. Is the Connect date firm, and is it about Dec 12?
2. Is there a revenue-share or fee decision, or is the marketplace free at launch?
3. Do any customers already build against the API privately, such as scripts or middleware?
4. How many engineers can you spare for first-party apps, and for how many weeks?
5. Is there a budget for the hackathon prize pool and co-build fund?

Answers to these change the numbers above, mainly the first-party count and the legal timeline.