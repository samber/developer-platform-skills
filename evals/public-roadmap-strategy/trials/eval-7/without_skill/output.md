**Publish a public "Now / Next / Later" roadmap on your docs site, with dated quarters on a small committed tier only.** It carries a disclaimer, a dated change log, and a frozen snapshot each quarter for procurement. Your first step is to book 30 minutes each with legal and finance this week (details below).

## What goes on the page

1. **Shipped**: last 2 quarters, each linking to its changelog entry.
2. **Committed, with a target quarter**: the next milestone (public preview or GA) per item, at most 2 quarters out.
3. **Planned, no date**: shown as "Next" with no quarter.
4. **Exploring, no commitment**: shown as "Later", with a feedback link.
5. **Deprecations**: dates come straight from your deprecation process. Banks read these first.

Every item shows its stage (private preview, public preview or GA), its last-changed date, and a link to its Discussion thread.

## Rule for earning a dated quarter

An item gets a quarter only if all of these hold:

- It is already in private preview or later.
- It has a named engineering owner and funded capacity.
- Your internal forecast lands in the first two months of that quarter. If it lands in the last month, publish the next quarter. This buffer protects your 11-of-12 record.

Moving an item earlier is fine at any time. A slip is any miss of the published quarter end. Keep the dated set small, around 4 to 6 items at launch.

## What not to publish

- Prices and packaging.
- Customer names.
- Security fixes.
- Compliance-certification dates. Put those on a trust page, because auditors and banks hold you to them.
- Anything under an exclusivity or NDA commitment.

## Disclaimer text for the page

> "This roadmap shows our current plans as of [date]. Items and timing may change and are not commitments or a promise to deliver any feature. Do not rely on it when deciding to purchase. See your agreement for terms on future functionality. Changes are recorded in the change log below."

Have legal edit this. I haven't seen your MSA or self-serve terms, so don't treat my wording as vetted.

## Procurement evidence

- Add a "Last updated" date and a "Recent changes" log on the page.
- Each quarter, freeze a dated snapshot (PDF plus a git tag) at a stable URL. Procurement can then cite "roadmap as of 2026-Q4" and it won't change under them.
- Do not publish a "92% on-time" figure now. 12 items is too small a sample. Track on-time rate quietly and publish it after two quarters, once you have at least 10 data points.

## Citation rule for sales leadership and the CEO to sign

1. Sales may cite roadmap items only by linking the public page with its snapshot date.
2. Only Committed items may be called "targeted" for a quarter. Planned and Exploring items get no timing.
3. Required wording: "Our public roadmap, as of [date], lists X targeted for [quarter]. It is not a commitment."
4. Never write roadmap items into order forms, SOWs, or RFP answers as "will deliver". Use "targeted" and attach the snapshot. Any exception goes to you and legal.
5. NDA briefings are allowed. They must never contradict the public page, and each one gets logged.
6. You own every page change. When a Committed item slips, the CSMs for affected accounts hear it before the page changes. Set a fixed lead time, such as 5 business days.
7. Breaking the rule goes to the sales leader. Name that owner in the signed document.

## Feedback loop

- Create one Discussions category, "Roadmap feedback", with one pinned thread per Committed and Planned item.
- DevRel already triages weekly. Add a monthly digest to you of 10 minutes or less: top-voted items and new requests.
- Add a note on each thread: "Account-specific or confidential requests go through your account team, not here." Banks shouldn't post sensitive details publicly.

## Finance and legal (30 minutes each)

You said finance has never looked at this, so they come first.

- **Finance:**
  - Confirm that a public dated roadmap, plus customers budgeting around it, creates no revenue-recognition effect. Your facts help: no order forms name items, and the clause exists.
  - Confirm no discounts or credits get tied to roadmap items.
  - Agree what happens if a slip triggers a customer claim.
- **Legal:**
  - Confirm that the future-functionality clause covers statements on a public page, in both the MSA and the self-serve terms.
  - Approve the disclaimer.
  - Confirm that whatever the MSA says about regulated customers needing notice of material changes doesn't conflict with the slip-notice step.

## Upkeep: under 2 hours a month

| When | Task | Time |
|---|---|---|
| Monthly | Diff the internal roadmap against the public page, flip statuses, log changes, trigger slip notices | 45 min |
| Monthly | Read the DevRel digest | 10 min |
| Quarter end | Cut the snapshot, review the dated set, promote or retire items, update the on-time tracker | +2 hours |

That averages about 1.5 hours a month. Generate the page from one YAML file in a repo so edits stay small.

## Three-week plan

1. **Week 1:**
   - Pick the items and apply the dating rule.
   - Hold the legal and finance sessions.
   - Get the citation rule signed.
2. **Week 2:**
   - Build the page and the Discussion threads.
   - Set up the snapshot process.
   - Run a 20-minute sales and CSM briefing.
   - List the accounts to pre-brief.
3. **Week 3:**
   - Fix whatever legal and finance flagged.
   - Pre-brief 2 to 3 bank customers.
   - Hold a go/no-go.
   - Launch with a changelog entry and a customer email.

If legal or finance isn't done by the end of week 2, launch without dates. That means Shipped, Next, Later, and Deprecations only. Add the dated tier at the next quarter's snapshot.

**Next (under 2 minutes):** send the two 30-minute invites to legal and finance, and attach the disclaimer and the dating rule above.