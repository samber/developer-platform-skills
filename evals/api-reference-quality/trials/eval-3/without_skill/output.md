I couldn't verify anything for this. Web search and fetch were both denied permission in this session, so every figure below is from memory. Check each one against its primary source before it goes on a slide. I've marked my confidence and left out anything I couldn't attribute.

## Slide 1: How bad is API documentation?

| Stat | Source | Confidence | Check at |
|---|---|---|---|
| About 39% of respondents named inconsistent documentation as the biggest roadblock to consuming APIs. | Postman, State of the API Report, 2023 edition | Medium-high on the figure. Medium on the edition year. | postman.com/state-of-api |
| Documentation ranks near the top of the resources developers rely on when learning a new API. | Postman State of the API, several editions | Qualitative only. I don't trust my recall of the exact percentages. | Same page. Pull the exact number from the edition you cite. |

I would not add more "industry is bad" stats without checking them. Several widely repeated figures online trace back to vendor blogs rather than surveys.

## Slide 2: What poor documentation costs

| Stat | Source | Confidence | Check at |
|---|---|---|---|
| About 61% of developers spend more than 30 minutes a day searching for answers. About a quarter spend more than an hour. | Stack Overflow Developer Survey 2024, "knowledge silos" section | Medium-high | survey.stackoverflow.co/2024 |
| Teams with high-quality documentation were about 2.4x more likely to meet reliability targets. | DORA / Accelerate State of DevOps, 2021 | Medium | dora.dev/research |
| Developers spend roughly 17 hours a week on maintenance and bad code, about $300B a year in lost global GDP. | Stripe and Harris Poll, "The Developer Coefficient," 2018 | Medium-high | Search the title. |

Two caveats will come up in review:
- **Stripe/Harris figure:** it is about maintenance in general, not documentation. Don't present it as a documentation cost.
- **DORA figure:** it is a correlation. Say "associated with", not "causes".

For a logistics API, the numbers that will carry weight are your own: support tickets per integration, partner onboarding time, and integrations stalled before their first call. A rough sizing is (integrations per year) × (extra engineering days from unclear docs) × (loaded day rate), plus the cost of support tickets that docs would deflect.

## Slide 3: ROI of a try-it console, and the "10x" claim

**Don't use the 10x claim.** I know of no independent study behind it.
- **Likely meaning:** vendors usually mean time to first successful API call, measured against a baseline with no sandbox. That is not developer productivity.
- **Likely source:** the number almost certainly comes from the vendor's own customer or marketing data.
- **Review risk:** if the CPO asks for the study and there isn't one, the other slides lose credibility too.
- **If it matters:** ask the vendor for the methodology, sample size, and baseline in writing. Cite it only as "vendor-reported".
- **Related claims:** I also half-remember vendor figures for "time to first call". I couldn't attribute them, so I left them out.

What you can defend is a model built on your own data:
1. **Baseline:** measure your current median time to first successful call for new integrators. Use the logs.
2. **Pilot:** put the console on a subset of endpoints or partners and re-measure.
3. **Value:** (days saved per integration) × (integrations per year) × (loaded day rate), plus tickets deflected × cost per ticket.
4. **Cost:** build or license, plus ongoing maintenance of the sandbox and its data.
5. **Presentation:** show conservative, expected, and optimistic cases. Label the pilot as a hypothesis test.

## Before the review

1. Open each source above and confirm the number, edition year, and wording.
2. Re-run the searches with web access enabled. I can do that and add working links if you grant the permission.
3. Tell me your own baseline numbers and I'll build the ROI model.