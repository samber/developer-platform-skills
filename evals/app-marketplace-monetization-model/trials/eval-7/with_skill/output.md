# Fee schedule and circumvention plan

I read `app-marketplace-monetization-model/SKILL.md` and its two fee and rails references. I did not open the payout and tax reference.

The skill asks one interview question at a time. This is a one-shot deliverable, so I could not do that. I state my assumptions below, and each one changes the design if it is wrong.

## Assumptions to confirm

1. The take-rate level (18%) is already decided. The skill says to stop and use `connector-marketplace-strategy` if it isn't.
2. Paid apps are marketplace-billed (platform is merchant of record), or will be when 18% starts. Your 18% folds in card-processing cost, which only makes sense if you run the card rails.
3. The second-largest app currently bills its own customers, so it is in the developer-billed legacy population.
4. 18% is not yet being collected. You said the agreement is silent, so I treat nothing as owed today.

## Part 1: the fee schedule

### 1a. 18% all-in: keep one number, but publish the breakdown next to it

**The skill's rule:** keep processing as a separately labeled line. A share that silently includes processing reads as a higher take than it is, and it can't be compared with competitors' headline rates.

**How that applies:** the rule targets *silent* inclusion. Your stated goal is a single number the partner pays, which the rule does not block. Publish both:

> **18% all-in. This covers the platform share (~15%) and card processing at cost (~3%).**

This also happens to match the benchmark stack. Shopify charges 15% plus a separate 2.9% processing line, about 17.9% in total.

**Why the breakdown matters:** without it, partners compare your 18% against Salesforce, Shopify and Atlassian headline rates of 15% and conclude you take 3 points more.

**Risks to fix before you publish:**

- **Processing cost is not a flat percentage.** Fixed per-transaction and per-payout fees weigh more on small tickets.
  - Managed marketplace rails also charge per active account per month and per payout. At low per-developer volume, those fees can outweigh the percentage you collect.
  - A fixed 18% means you absorb all the variance.
  - Model unit economics per active developer, not per transaction.
- **Refunds and disputes.** Check with your rails provider whether processing fees are returned on a refund. If they aren't, state in the schedule who bears that cost.
- **The waiver tier breaks the single number.** The skill's default waiver is a revenue-exemption tier, anchored at about $1M. Under an all-in 18%, "0% below the threshold" would make you eat processing on every small developer.
  - Decide explicitly: either the exempt tier is processing-only (~3%), as Shopify does, or the platform absorbs it.
  - Auto-enroll eligible developers. Opt-in waivers silently charge qualifying developers the full rate.
- **Developer-billed apps pay for nothing they use.** If an app bills through its own processor, you carry no processing cost for it. Charging it "18% all-in" overcharges by the processing slice. Either set a different rate for that population or move them to marketplace billing (see Part 2).
- **Notice.** Commit in writing to six months' notice for any rate change, per the sourced pattern, and publish it with the schedule. Fixing a headline number makes later changes more visible.

### 1b. $2,500 per submission: the number and the unit both need work

**What the skill says:** flat program fees are justified when they price a real cost, such as the security review, or filter spam without deterring developers. Benchmarks:

| Marketplace | Fee |
|---|---|
| Salesforce | $999 one-time per paid app, plus $150 annual listing fee |
| Shopify | $19 one-time registration |

$2,500 is about 2.5x the highest benchmark. It is defensible only if it matches your actual review cost, and I have no data on that.

**Define the unit.** "Per submission" is ambiguous. My recommendation is one fee per new app, not per resubmission or version.

- Include a fixed number of fix-and-resubmit rounds (2, as my suggestion) in the fee. Otherwise you tax developers for fixing what you rejected.
- Charge a smaller fee only for major re-reviews, such as new scopes or a new data-access class.
- Do not charge existing listed apps. Apply the fee only to submissions after the effective date.

**Check the effect on supply.** A large fee filters small and hobbyist developers, and so does a small one, but you may lose real partners. If you cannot show the review costs about $2,500 in staff time, start near the benchmark and raise it with evidence. This is my judgment, not a sourced figure.

**Gate 2 of the skill's measurement checklist** requires each instrument to name a collection mechanism, an enforcement pair and a notice commitment:

| Instrument | Collected by | Enforcement | Notice |
|---|---|---|---|
| 18% all-in | Netted at source before payout (marketplace-billed) | Anti-circumvention clause with delisting path (Part 2) | 6 months for changes |
| $2,500 review fee | Charged at submission, review does not start until paid | No payment means no review and no listing | Effective date announced, applies to new submissions only |

If an app stays developer-billed, the only collection route is an audited self-reported share. The skill treats that as a starved option that loses on enforcement, so keep it only for the legacy path.

## Part 2: the "pay here instead" link

### What this is

It is the circumvention pattern the skill describes. Circumvention pressure rises with the rate. At 18% against roughly 3% for their own checkout, a high-revenue app has about a 15-point incentive to route around you. Expect other large apps to follow.

### What not to do

- **Do not call it a violation or threaten delisting today.** The agreement is silent, and 18% isn't collected yet, so there is nothing to enforce. A threat you cannot back up with the contract burns trust with your second-largest partner.
- **Do not claim back-share on past revenue.** There is no basis for it.

### What to do, in order

1. **This week: gather facts, take no action.**
   - Capture screenshots and dates of the link.
   - Check whether any existing clause covers it, such as acceptable use or steering. Have counsel confirm.
   - Find out whether the 190 installs came through the marketplace or were existing customers. That decides what a fair rule can cover.
2. **Talk to the partner before you write a rule.** Ask why they added it. The answer picks the fix:
   - *Margin on the 18%:* a rate or incentive conversation.
   - *Pricing model your checkout can't support* (for example, usage-based): fix the rails menu.
   - *Existing contracts or invoicing:* a grandfathering conversation.
3. **Amend the agreement for everyone, prospectively.** Add an anti-circumvention clause with a delisting path, announced with the same six months' notice as the fee change, and effective on the same date as 18%. One change event, one notice. Publishing it to all partners also avoids looking like you are targeting one app.
   - **Scope:** routing billing for marketplace-acquired installs or marketplace-sold paid features off-platform.
   - **Carve-outs:** customers acquired outside the marketplace, existing contracts through a stated tail period, and free apps.
   - **Audit right:** include one, because the legacy path relies on self-reported revenue.
4. **Escalation ladder:**
   1. Written notice.
   2. A cure period (30 days, as my suggestion).
   3. Pause new installs.
   4. Delisting.

   Delisting 190 installs hurts your own customers, so treat it as the last step and give existing installs a transition path.
5. **Offer a carrot alongside the clause.** This app is a legacy developer-billed population with measurable off-platform revenue. The skill says that back-book is exactly what justifies a migration incentive.
   - Examples: a time-limited reduced rate for moving to marketplace billing, or a differential rate that favors the on-platform path.
   - Size it from this app's actual off-platform revenue. I won't invent a figure.
   - Give the legacy path a stated end date, as Atlassian does.

### Success check

Track circumvention incidents and their resolution, as the skill's measurement section specifies.

## Decisions I need from you

1. Is 18% already collected anywhere, or only announced?
2. What is your actual review cost per app, and does "per submission" mean per app or per version?
3. Do you keep a revenue-exemption tier, and if so, is it processing-only or fully absorbed?
4. Are marketplace-acquired and direct customers distinguishable in your data for this app?
5. What processing rate does your rails provider charge you?

None of this is legal or tax advice. Route the amended agreement and the published tax split through counsel before shipping.