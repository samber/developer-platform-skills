# Pre-send check for the Ferncastle partnerships board deck

⚠️ **I couldn't verify any of this against live sources.** Web search was denied in this session, and I wasn't allowed to touch `skill-wip/`. Everything below comes from memory, and I rate my confidence per item. Please check the ✅/⚠️ items against the vendors' partner portals before the deck goes out.

## 1. Partner program slides

### Salesforce: "target Crest, eventually Summit"

- ℹ️ **Tier names:** I recall Salesforce's current partner program using Ridge → Crest → Summit, with Summit as the top tier. So "Crest now, Summit later" is plausible as a ladder.
- ⚠️ **Confidence is moderate.** The program was renamed and restructured relatively recently. Confirm the names and order on Salesforce's partner site.
- ⚠️ **The slide should say what each tier requires for an ISV.** For an ISV the gates are tied to AppExchange, not to services-partner points. Likely gates are listing and security review, customer count, and installs or revenue through AppExchange. A board will ask "what does Crest cost us and what do we get?" If the slide doesn't answer that, add a row for each of these:
  - entry requirement
  - timeline
  - benefit
  - owner
- ⚠️ **"Eventually Summit" is too soft.** Either give a trigger (for example, an ARR or sourced-pipeline threshold) or cut it. Board slides with "eventually" get read as "no plan."
- ⚠️ **Make sure the slide is about the ISV track.** Salesforce has separate tracks and requirements for ISV and consulting partners, and tier names can look identical across both.

### Atlassian: Silver/Gold/Platinum, "Gold needs $500K in cloud sales"

- ✅ **Tier names:** Silver/Gold/Platinum is a real Atlassian structure.
- ❌ **I can't confirm the $500K figure.** Treat it as unverified.
- ⚠️ **Which Atlassian program is this?** Atlassian runs two distinct programs, so first confirm which one the slide describes:
  - the **Solution Partner** program (resellers and consultants)
  - the **Marketplace Partner** program (app vendors)

  For a DevOps tooling ISV, Marketplace is almost certainly the relevant one. The Solution Partner thresholds don't apply to you.
- ⚠️ **Thresholds change.** Atlassian has been moving customers and thresholds toward cloud and has revised the program more than once. Check the date on whatever source your $500K came from, and cite the source and "as of" date in the slide footer.
- ⚠️ **Is $500K annual, trailing, or cumulative?** And is it cloud-only or total Marketplace sales? Whichever it is, the slide must say, because it changes whether Gold is reachable for a company your size.

### Cross-slide consistency

- Put both programs on one comparison (requirement, cost, benefit, target date, and your current position relative to each threshold). Right now one slide targets a tier and the other lists tiers, so the board can't compare them.
- Show where Ferncastle sits today. "We are at $X of the $500K" turns a fact into a decision.

## 2. The stats

### Slide 2: "83% of enterprise buyers cite integrations as a purchase-decision factor"

- ❌ **I don't recognize this figure and can't tie it to a source.** If it has no named source, publisher, year, and sample, cut it or replace it.
- ⚠️ **Wording issue even if the number is real.** "Cite as a factor" is the weakest possible claim. Most buyers will "cite" integrations when prompted from a checklist. That doesn't show integrations decide purchases.
- ⚠️ **Check the sample.** "Enterprise buyers" in a survey run by an integration or iPaaS vendor is typically a self-selected, interested sample, and the question is usually multiple-choice and leading.
- ⚠️ **Headline-stat risk.** It's the opening claim of the deck, so it carries the most scrutiny. A board member searching for it and finding nothing damages the rest of the deck.

### Slide 9: "ecosystem-qualified deals are 53% more likely to close and close 46% faster"

- ❌ **Same problem: I can't verify the numbers or tie them to a source.** The pairing resembles the vendor-run partner-ecosystem benchmark reports that circulate in this space, but I can't confirm which, if any, it came from. Don't attribute it to one without checking.
- ⚠️ **It's a correlation presented as an effect.** Deals that have an ecosystem or partner touch are usually bigger, further along, and run with better-fit customers. "Ecosystem-qualified" deals are selected into that group. The numbers don't show that the ecosystem caused the better outcome.
- ⚠️ **"53% more likely" is ambiguous.** Is it relative (say 20% → 30.6%) or percentage points? Say which, and give the baseline.
- ⚠️ **Definitions matter.** What counts as "ecosystem-qualified": partner-sourced, partner-influenced, or marketplace-listed? The three behave very differently.
- ⚠️ **The two numbers don't add independent evidence.** If they come from one report and one definition, they're one data point.

### What to do instead (strongest option for a board)

At $18M ARR, Ferncastle probably has enough closed deals to compute this yourself:

1. Tag closed-won and closed-lost deals in the CRM by whether an integration or partner was involved.
2. Compare win rate and sales-cycle length, controlling for deal size and segment.
3. Show the result with the n, the period, and the definitions.

An internal number, even a modest one, is more credible to a board than an unsourced industry figure. It also feeds the partner program decisions on the other slides.

If you must use external stats, label them on the slide: "Source: [publisher], [year], n=[X], [who was surveyed]". Frame them as directional, not proof.

## Fix list before sending

1. ❌ Source or cut the 83% (slide 2).
2. ❌ Source, define, and caveat or replace the 53%/46% (slide 9). Prefer your own CRM data.
3. ⚠️ Verify Salesforce tier names and ISV-track requirements on the Salesforce partner site.
4. ⚠️ Verify the Atlassian $500K threshold, its program (Marketplace vs Solution Partner), its basis (annual or cumulative), and an "as of" date.
5. ⚠️ Add requirement, cost, benefit, and timeline per tier, plus Ferncastle's current position.
6. ⚠️ Replace "eventually Summit" with a trigger or drop it.

If you grant web access, or paste the source links behind the 83% and the $500K, I can re-run this as a verified check.