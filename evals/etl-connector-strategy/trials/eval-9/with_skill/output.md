# Poking holes in "six ELT source connectors in year one" (Kestrel Compliance)

I followed the `etl-connector-strategy` skill and its three references. This isn't the full strategy document. The skill's own gate stops it at step 1, so the output is the holes plus a replacement plan.

## Verdict

Don't approve the plan as written. It fails the skill's **demand-validation gate** (step 1) and the platform-selection step (step 2).

- You have no named evidence of demand. Your own answers put you at interview option 1(d), hypothesis only.
- You don't know which platforms your customers use, which is option 2(d). The skill says to suspend the workflow until that is found out.
- Platform choice is therefore a guess, and "the six biggest" is a guess about the wrong variable. Platform size says nothing about what Kestrel's customers run.

The budget is fine. The sequencing is the problem: you plan to spend 2 FTE on a build before you have found out whether anyone needs it.

## The holes

### 1. You're building on hypothesis (step 1)

- The skill's rule is "approve no connector build on hypothesis". Acceptable evidence is named and verifiable:
  - tickets that name a platform;
  - lost-deal notes citing data-stack mismatch;
  - API logs showing hand-rolled extraction;
  - procurement questionnaires asking about warehouse sync.
- "So we're never the reason a deal stalls" is a claim about deals. Does one lost or stalled deal cite this? If none does, the plan is aimed at a problem you haven't observed.
- A connector built without evidence "serves nobody measurable and still bills its 15-30% every year" (failure mode: building on hypothesis).

### 2. "Six biggest" is the wrong selection rule (step 2)

- The skill says to build where customer stacks are, never where it's fashionable. It also says to start with one platform, and add a second only after the first connector's maintenance load is measured.
- Six in parallel means no measured load, and no learning carried from one to the next.
- Platform "biggest" is the platform's market share. What matters is the share of Kestrel's data-team customers on it.
- Only customers with a warehouse and a data team extract anything. You don't know what fraction of your 600 that is.
- Your reference material covers three archetypes, not six platforms:
  - Fivetran, a curated platform that gatekeeps entry.
  - Airbyte, an open-contribution platform that gatekeeps labels.
  - Singer/Meltano, an open-spec ecosystem with no gate and no floor.
- I have no vetted program data for any other platform you may have in your six. Don't plan timelines for those until someone reads their partner docs.

### 3. The cheapest path may not need your engineers

- The skill's default rung is the platform-managed listing, where the platform builds and maintains the connector. You supply API docs and a contact. That rung has the lowest effort and the lowest maintenance exposure.
- Fivetran's Partner-Built program is closed to new source partners as of the 2026-08-30 snapshot. Re-verify that before you commit.
- That leaves two live Fivetran routes:
  - By Request. It runs six phases, with two to eight weeks of API analysis up front, and it can reject the source. Fivetran quotes about 30 days once accepted.
  - The Connector SDK, a Python connector you write and maintain.
- The queue path can cost near zero FTE. If you plan to spend 2 FTE building six connectors, check whether the platforms would build some of them for you.
- The catch is that managed listings suit stable, non-dynamic schemas. Dynamic or custom schemas get steered to the SDK. Compliance products often have tenant-specific frameworks, controls and evidence fields. That's my inference about Kestrel, not something I know, so check it.

### 4. The maintenance bill arrives in year two, and you haven't named an owner

- Annual upkeep is 15-30% of build cost, up to 50% in high-change phases. These are vendor-published figures, so treat them as an order of magnitude.
- It is per connector, and nothing amortizes across connectors. Practitioner framing says self-built maintenance is "manageable at three to five sources" and "punishing across more than ten".
- Six connectors on the SDK or custom path put you in that zone before counting API drift.
- Your budget covers four quarters. Who owns the connectors in month 13? That is interview question 4, and you haven't answered it. Without a named owner, the skill calls this the documented decay path, the same one that killed the Singer tap ecosystem.
- Upstream breakage arrives unannounced. A study of 1,068 API specs (ICSME 2020) found 87.3% of breaking versions shipped with no deprecation notice. That includes your own API's changes, which break your connectors. Plan on alerting and monitoring, not on reading changelogs.

### 5. You haven't audited your own API

- The skill calls the extraction-readiness audit (step 4) "the single highest-ROI investment in the whole strategy". It cuts cost on every path, and it also helps customers who hand-roll pipelines today.
- Your answer to interview question 3 is unknown. The things to check:
  - a stable incremental cursor or reliable `updated_at`;
  - a bulk/backfill path separate from UI-style CRUD;
  - a delete signal;
  - `429` responses with `Retry-After`;
  - additive versioning with published sunset dates.
- If you have only UI-grade CRUD endpoints, six connectors would hit the same wall six times: rate-limited backfills, missed deletes, flaky incremental syncs. They would also fail certification for reasons no connector code can fix.
- Fixing the API first may be the best use of an early slice of the 2 FTE.

### 6. "CDC" is a trap, especially for a compliance product

- Never write "CDC support". A SaaS source can only ship incremental polling with eventual consistency. Log-based CDC needs the database's transaction log, which an external platform and your public API don't get.
- The honest sync model misses two things:
  - changes made and overwritten within one poll interval;
  - hard deletes, wherever there is no deletion feed.
- Kestrel's data is audit-relevant. A silently missed delete in a customer's warehouse could be a real problem in a compliance setting, and it's exactly the failure the skill warns about. Customers' auditors may notice. That's my inference, so confirm it.
- Customer-facing wording should say "incremental sync", state the poll interval, and name what it misses. If customers report missed deletes, build a vendor-side change/deletion feed. Don't promise one at launch.

### 7. No revenue line, and don't let one sneak into the case

- No ETL/ELT platform pays a source vendor. The only revenue-share proposal, Airbyte's in 2021, shipped as flat bounties of $10-150 per task.
- A connector is a cost center bought for distribution, retention and support-cost deflection. Justify it with ticket-deflection and retention math. A revenue line will die at the first finance review.
- Platform partner programs exist (Fivetran's enhanced one, Airbyte's), but they are mainly reseller and SI motions. Neither publicly offers source vendors paid placement or priority.

### 8. "Cover the data ecosystem" may not mean ELT connectors

- The budget wording is wider than your plan. Some of that demand may be better served by sibling surfaces:
  - "Files in our bucket" is `bulk-data-sharing-design`.
  - "Live SQL against our data" is `sql-jdbc-access-design`.
  - Whether ELT connectors are the right surface at all is `api-integration-surface-strategy`.
- The skill routes mismatched demand out to those. If customers' data teams want evidence delivered straight to their warehouse or bucket, a connector is the slowest way to give it to them.

## Replacement plan: stage-gated, not six-at-once

You can keep the 2 FTE and four quarters. Make each stage release the next.

**Stage 0: find out (weeks 1-4, about 0.25 FTE).** This is the step the skill says to suspend on. You have 600 customers, so ask all of them.
1. Send a short survey to every customer and active prospect. Ask whether they have a data team or warehouse, which extraction platform they run, and what they use it for.
2. Mine support tickets, CRM lost-deal notes, and security questionnaires for platform names.
3. Check API logs for high-frequency paginated scans from service accounts. That is hand-rolled extraction, and it's the strongest evidence you can get.
4. Output: a ranked table of platforms by number of named customers and deals.

**Gate A.** Proceed only if you have named evidence, such as three named-platform tickets in a quarter or one lost deal citing the gap. Those thresholds are the skill's suggested examples, so set your own. If the evidence is thin, improve the raw API or direct-to-storage delivery and name the signal that would reopen the decision.

**Stage 1: audit and fix the API (about 1 FTE, quarters 1-2).** Grade every in-scope resource pass or fail on the readiness checklist, or write an explicit exclusion note. Fix the cursor, the bulk path, the delete signal and the versioning policy first.

**Stage 2: one platform, whichever Stage 0 ranks first.**
1. Default to the platform-managed queue (Fivetran By Request or the Airbyte equivalent).
2. Escalate to the SDK only if the queue rejects you, your schema is too dynamic, or you need control of the cursor logic.
3. Choose with the skill's re-ranking questions in hand: deadline, compounding versus one-off, and effort ceiling.

**Gate B.** Before the second platform, measure the first connector's real maintenance hours per month, its sync success rate (the Airbyte-style bar is 95% or more), and ticket deflection.

**Stage 3: second platform, or certification, depending on Gate B.** Aim for certification only once the connector holds up in real syncs. Mind the clocks: Fivetran requires promotion from private preview to beta within six months.

**Throughout, name the month-13 owner now.** Fund monitoring, alerts on sync failures and schema-drift errors, and a standing budget. Marketplace-tier listings carry no platform SLA, so you are the support.

If the evidence is strong, six platforms may still be right eventually. But you reach them one at a time, each justified by named customers, with the maintenance load measured between steps.

## What I still need from you

The skill asks one question per message. In a single response I can't wait for answers, so these are the open ones. Answer them and I'll re-rank the build-path menu and draft the strategy document section by section.

1. **Demand evidence:** any tickets, lost deals, or hand-rolled API usage? (You said no. I'll assume option (d) unless you've since found some.)
2. **Customer stacks:** unknown. Stage 0 answers it.
3. **API readiness:** do you have a stable incremental cursor or `updated_at`, a bulk path, and a delete signal? (a) all three, (b) cursor only, (c) UI-grade CRUD only, (d) unsure.
4. **Month-13 owner:** a named team with standing budget, a side-task, or nobody yet?
5. **Deadline:** is a specific deal or competitive evaluation waiting on this?
6. **Compounding or one-off:** a standing distribution asset, or a checkbox for one deal?
7. **Effort ceiling:** engineering weeks up front, and hours per month after launch.
8. **Which six platforms** did you mean? I can only vouch for program data on Fivetran, Airbyte, and the Singer/Meltano family.

## Caveats

- The platform program data is a snapshot dated 2026-08-30. Re-verify each program before committing, and especially whether Fivetran Partner-Built is still closed to new sources.
- The maintenance percentages and build-cost ranges come from integration-tooling vendors who sell their own products.
- My notes on Kestrel's schema and audit sensitivity are inferences from the product category, not facts about your product.