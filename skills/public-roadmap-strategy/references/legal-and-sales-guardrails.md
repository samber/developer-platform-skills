# Legal and sales guardrails

Read during SKILL.md step 5. These are shapes to hand to counsel and the sales leader, not legal advice: final wording, jurisdiction and contract terms belong to the company's lawyers.

## Page disclaimer shape

Four elements; Atlassian and GitLab carry all four, GitHub and Heroku carry subsets:

1. Informational only.
2. Not a commitment, promise or legal obligation to deliver any feature.
3. Timing and content may change at the company's sole discretion.
4. Should not be relied upon in making purchasing decisions.

```
// ✓ Good - all four elements, placed on the roadmap page itself
This roadmap is for information only. It is not a commitment to deliver any
feature, and plans and timing may change at our discretion. Please make
purchasing decisions based on features available today.

// ✗ Bad - softens the commitment without disclaiming it, invites reliance
These are the features we're excited to ship this year!
```

Repeat the disclaimer in every NDA briefing deck, on the first slide, not in a footer.

## Forward-looking statements

- **Listed companies:** securities safe-harbor language on roadmap material (Salesforce release decks carry it), plus the customer sentence: "Customers who purchase our services should make the purchase decisions based upon features that are currently available."
- **Private companies:** borrow only the customer sentence. The safe-harbor framework protects securities disclosures, which a private company does not make.

## Contract clause shape

The "Future Functionality" clause states that the customer's purchase is not contingent on delivery of any future functionality or features, nor on any oral or written public comments about future functionality. Salesforce's MSA carries it, and the clause is widely copied. Check the MSA has it, and that the self-serve click-through terms carry an equivalent, before the roadmap goes public.

What it does not do: it reduces reliance claims from contracted customers, but in many jurisdictions it cannot exclude misrepresentation, unfair-practice or deceptive-advertising claims. Never publish an item known to be off.

**The override:** many variants exempt features "expressly provided in any Order". Anything written into an order form, SOW or side letter binds regardless of the page disclaimer or the MSA clause.

## Revenue recognition (ASC 606)

- The rules below are ASC 606 (US GAAP); IFRS 15 is the equivalent elsewhere.
- Unspecified updates delivered "when and if available" form a stand-ready obligation, recognized over time. This is the normal SaaS case.
- A specified upgrade can be a separate performance obligation, deferring the revenue allocated to it until delivery.
- EY advises reviewing roadmap communications, including feature descriptions and release dates, for a customer's "valid expectation of specified upgrades".
- Consequence: undated, unspecified updates usually create no obligation; dated, specified ones may, whether they sit in a deal or on a public dated roadmap. Involve finance whenever a dated commitment reaches any customer.

## Documentation rule

GitLab's documentation style guide forbids promising future features in docs ("We cannot guarantee future feature work, and promises like these can raise legal issues") and requires a templated disclaimer near any unreleased-feature content. Apply the same rule to docs and blog posts: describe what exists; link the roadmap item for what does not.

## Sales rules one-pager outline

Hand this to the sales leader and the CEO for sign-off; enablement owns rollout. It covers anyone customer-facing: reps, solutions engineers, customer success, DevRel, executives on stage.

1. **The one source:** reps may cite the public roadmap only, at the commitment level printed on each item (phase, and quarter only if shown).
2. **Phase language:** "in private preview, we can request access for you" is allowed; "it ships in Q1" is not, unless the page says so.
3. **Deeper previews:** NDA briefing or private-preview enrollment, product present, disclaimer on slide one.
4. **Written and spoken channels:** no dates in emails, proposals, decks or keynotes beyond what the page shows.
5. **Order forms:** any roadmap item in an order form, SOW or side letter needs legal and finance approval before signature.
6. **Escalation:** a deal that depends on an unbuilt feature goes to product for a decision (commit it through the roadmap, or decline it), never to a rep's judgment.
7. **Slip duty:** when a roadmap item a deal referenced slips, the account owner tells the customer before the public update goes out, after legal checks the notice against the order-form terms.

## Roadmap in the NDA briefing

- Show the public items plus, at most, items product has approved for that account under NDA.
- Never show unannounced deprecations, security work or partner names, even under NDA (same exclusion gate as the public page).
- Record what was shown to which account (account, date, items, attendees), so a later slip reaches everyone who saw the item.
- Name a briefing owner in product; briefings come out of the same monthly hours as the public page.
