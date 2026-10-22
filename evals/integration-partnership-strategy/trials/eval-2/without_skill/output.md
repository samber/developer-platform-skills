# Rebuilding Bellwright's partner revenue number

I haven't seen your data, so the output below is a method and a template. The final figure comes from the audit in section 4. Expect it to be much smaller than $31M, and don't promise a number to the CFO before the audit.

## 1. Why $31M failed

- **The test was too weak.** "Partner logo appears anywhere in the opportunity notes" measures a mention, not an effect. In HR-tech the most common mention is an integration partner (HRIS, payroll, ATS) that the customer already uses. That is a technical requirement, not partner work.
- **The tagging was retroactive.** Dana tags deals in the last week of the quarter, after the outcome is known. Finance will call that retrofitting.
- **The source was a hand-edited sheet.** It isn't a system of record, has no audit trail, and has no definition of "touched".
- **The numerator and denominator were mismatched.** $31M is closed-won, probably including multi-year contract value or renewals. $40M is ARR. 77.5% is a ratio of two different things.
- **Credit wasn't exclusive.** A deal with a partner mention counted in full. No split, no tiers.

Own this in the first minute of the Q3 meeting: "The old number used a loose definition. Here is the rebuilt one, and Finance co-owns it."

## 2. The definition

Report three tiers per deal. Each deal lands in exactly one tier, so nothing is double-counted.

| Tier | Test | Evidence required |
|---|---|---|
| **A. Partner-sourced** | The partner created the opportunity (referral or intro) | Partner field set at opportunity creation, or a registered deal/referral record dated before the opportunity |
| **B. Partner co-sold** | A partner took a documented active role in the sales cycle (joint calls, partner-led evaluation, partner as implementer named in the order form or SOW) | Dated activity or meeting record, or a named partner on the contract, dated before close-won |
| **C. Partner-mentioned** | The partner is named, but with no active role (customer uses their integration, logo in notes) | Notes only. Reported as a count, never as revenue |

- **Headline number = Tier A + Tier B.** Show A and B separately beneath it. A is the hard floor, and A+B is the defensible ceiling.
- **Tier C stays out of the headline.** Showing its size lets you say what you excluded.
- **Revenue measure:** new-business ACV, first-year annualized, taken from the finance system of record (billing or ERP), not from the CRM amount field. Keep new logo and expansion as separate lines. Exclude renewals and multi-year TCV.
- **Time rule:** partner evidence must be dated before the close-won date. For Tier A, it must also precede or coincide with opportunity creation.
- **Denominator:** total new ACV booked in the same period, from Finance. Do not use ARR. Report the share as a percentage of new bookings, plus a trailing-four-quarter view to smooth quarter spikes.

## 3. Fix the system so the number stays clean

1. **Add structured CRM fields on the Opportunity:** Partner (lookup), Partner Role (Referral / Co-sell / Implementation / Integration-only), Partner Added Date (system-stamped), Added By.
2. **Make the role required to move past the proposal stage** whenever Partner is set.
3. **Lock the fields after close-won.** Only RevOps or Finance can edit them, with a logged reason.
4. **Retire Dana's sheet as a source.** She becomes the reviewer of exceptions, not the tagger of record.
5. **Have Finance own the dashboard query.** Partnerships can't mark their own homework.

## 4. Re-audit the past four quarters

The goal is a restated historical number before the Q3 meeting.

1. **Pull the population.** Take every closed-won deal from the last four quarters from Finance, not from Dana's sheet. Record the count and the total ACV.
2. **Mark Dana's tagged subset.** Note how many deals she tagged and their ACV.
3. **Audit with a written rubric** (the tier table above).
   - If Dana's tagged set is a few hundred deals or fewer, audit every deal.
   - Otherwise sample about 60 deals, stratified by deal size, and always include the top 20 by ACV.
   - Have two reviewers score a subset independently and report their agreement.
4. **Evidence per deal.** Look for email threads, meeting invites, partner-registered deals, and SOWs. If the evidence doesn't exist, the deal is Tier C, even if the partner genuinely helped. State this rule up front.
5. **Extrapolate honestly.** Apply the sample's tier mix to the population and report a range (low = A only, high = A+B).
6. **Write a one-page reconciliation:** $31M → minus Tier C → minus non-ACV items (multi-year, renewals) → final A+B. Finance will trust a bridge more than a new number.

Output table to fill in:

| Quarter | New ACV (Finance) | Tier A ACV | Tier B ACV | Tier C count | A+B % of new ACV |
|---|---|---|---|---|---|
| Q4 | | | | | |
| Q1 | | | | | |
| Q2 | | | | | |
| Q3 | | | | | |
| **Trailing 4Q** | | | | | |

## 5. Show partners change outcomes, not just appear

Finance accepts attribution more readily when it comes with a comparison. Compare Tier A+B deals with similar non-partner deals (same segment, size band, and quarter) on:

- Win rate
- Sales cycle length
- Average ACV
- First-year retention (if you have enough history)

Present whatever you find. If partner deals close faster or retain better, that supports the headcount. If they only look the same, the case rests on sourced pipeline alone. Don't hide a null result.

## 6. Build the headcount case on marginal capacity

The CFO killed the request because the number looked inflated. A restated number won't be enough on its own. Tie the three heads to what they will add:

- **Current load:** active partners per partner manager, and how many partners are unmanaged.
- **Demonstrated yield:** Tier A ACV per partner manager, using the restated figure.
- **Untapped capacity:** registered partners with no activity, and the pipeline they could produce at the yield of your active partners.
- **Cost and payback:** fully loaded cost of three heads against conservative incremental Tier A ACV (use the low end of your range, and ramp time of two to three quarters).
- **Downside case:** what happens if the heads deliver half the projected yield. Show that the case still holds, or say where it doesn't.

Frame the ask as a staged commitment (for example, one head now and two gated on hitting a Tier A target) if the numbers are thin. A staged ask is easier to approve than a flat three.

## 7. Pre-wire the CFO and Finance

1. **Meet FP&A before the Q3 meeting.** Ask: "What evidence would you accept for partner attribution?" Adopt their answer where it differs from mine.
2. **Share the rubric and the bridge first.** Let them challenge the definitions before they see the headline.
3. **Get Finance to co-sign the restated number.** A number the CFO's own team computed is far harder to dismiss.
4. **Agree on a forward reporting cadence:** a quarterly number, computed by Finance from the structured fields.

## 8. Timeline

| Step | Owner | Effort |
|---|---|---|
| Agree definitions with FP&A | You + FP&A | 1 meeting |
| Pull the population from Finance | FP&A | 1–2 days |
| Audit (full or sample) | You + Dana + a second reviewer | 3–5 days |
| Reconciliation bridge and comparison | You | 2 days |
| CRM field changes | RevOps | 1–2 weeks (can run in parallel) |
| Pre-wire and Q3 ask | You | 1 week |

## 9. Risks to watch

- **The audit may show a small Tier A+B share.** Decide now that you'll present it anyway. A small, defensible number beats a large one that gets rejected again.
- **Dana may feel blamed.** The old method was a reasonable shortcut without a definition. Involve her as a co-reviewer.
- **Tier B is the contested tier.** If Finance rejects it, fall back to Tier A as the headline and show B as upside.
- **Some partner value is real but unprovable** (for example, an integration that makes deals closeable). Say so, keep it in Tier C, and don't count it as revenue.

If you can share the closed-won count and the tagged count for the last four quarters, I can size the audit and build the reconciliation bridge.