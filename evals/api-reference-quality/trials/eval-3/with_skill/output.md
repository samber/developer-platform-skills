# Corven API documentation quality: three slides with sourced stats

I took every figure below from the evidence file bundled with the `api-reference-quality` skill (`references/measured-evidence.md`). I did not re-fetch the original papers or reports. Open the DOIs and URLs yourself before the review.

The evidence base has no dollar figure for what bad docs cost, and no reliable ROI multiplier for a try-it console. Those two gaps are covered in slides 2 and 3.

---

## Slide 1: How bad is API documentation industry-wide?

**Headline:** Incomplete docs are the measured norm, not the exception.

| Stat | Source | Evidence quality |
|---|---|---|
| Mean documentation quality is **67.11%** across **2,529** public OpenAPI specs. | OASQuali: Decrop, Vandeloise, Heymans, Perrouin (Univ. of Namur), ICWE 2026, Springer LNCS 16625, DOI 10.1007/978-3-032-29372-5_7 | Peer-reviewed |
| **86.95%** of specs have no parameter examples. | Same paper | Peer-reviewed |
| Description and example quality falls from **42.18% to 24.00%** as APIs grow. | Same paper | Peer-reviewed |
| **39%** of developers call inconsistent docs their biggest roadblock. | Postman, 2024 State of the API (5,600+ respondents) | Survey self-report |
| **44%** of developers dig through source code to understand an API. | Same report | Survey self-report |
| "Lack of documentation" was the #1 obstacle to consuming APIs at **54.3%**. | Postman, 2020 State of the API, reaffirmed 2023 | Survey self-report |
| Standardization is the top API challenge at **52%**. | SmartBear, 2023 (1,100+ practitioners) | Survey self-report |

**Caveats to say out loud:**
- **67.11% is a score, not a failure rate.** OASQuali measures spec metadata quality across five dimensions: format, version, metadata, servers, and descriptions/examples. Don't say "a third of docs are wrong."
- **The survey figures are perception.** The 39% and 44% are self-reported, not measured.
- **Nothing here is logistics-specific.** These are cross-industry numbers.

**Supporting claim:** Spec inference testing found undocumented but valid routes and parameters in shipped production APIs (RESTSpecIT, Decrop et al., arXiv 2402.05102, 2024). It is a preprint. It supports "a spec doesn't guarantee complete docs", not a prevalence number.

---

## Slide 2: What does it cost?

**Headline:** The cost is real, but the hard evidence is about behavior, not dollars.

| Stat | Source | Evidence quality |
|---|---|---|
| **44%** read source code to understand an API, so integrators are doing engineering work the docs should do. | Postman 2024 | Survey self-report |
| Almost **10%** of undocumented exceptions findable in the Android platform API showed up in real crashes (901,274 crash records, 3,539 apps). | Kechagia, Fragkoulis, Louridas, Spinellis, *Journal of Systems and Software*, 2018 | Peer-reviewed |
| Only **76.6%** (59 of 77) of real APIs gave fully successful automated tool generation from their specs. Failures came from missing auth schemes, malformed base URLs, and undocumented runtime headers. | "From REST to MCP", arXiv 2507.16044, 2025 | Preprint |

**Do not cite the Kechagia 10% as a REST statistic.** It is an Android platform study. Present it only as "undocumented failure surface has a measurable downstream cost."

**No sourced dollar figure exists in this evidence base.** Do not put a made-up "$X per year lost to bad docs" on the slide. A CPO will ask for the derivation. Build Corven's own number from three inputs:

1. **Support tickets** caused by missing or wrong reference content, per month. Tag a sample of 50–100 to get the share.
2. **Cost per ticket.** Use your support team's loaded cost.
3. **Partner onboarding time.** Take the median days from signup to first successful call. If the time is lost, you can also estimate revenue delayed.

I can build the cost model if you give me ticket and onboarding data.

---

## Slide 3: ROI of a try-it console, and the "10x" claim

**Headline:** Recommend try-it as good practice. Don't present 10x as an ROI number.

**The vendor claims, with what they actually say:**

| Claim | Source | What it is | Why it breaks in review |
|---|---|---|---|
| "At least 10x, maybe more" faster time-to-first-call, plus a **225%** rise in developer registrations | Postman, Moneris customer story, 2025 | Vendor customer story | It bundles the console with sandbox testing and better onboarding generally. It does not isolate the console. |
| **1.7x–56x** faster, with "20x" as the headline aggregate | Joyce Lin, "Improve Your Time to First API Call by 20x", Postman Blog, April 2023 | Vendor experiment | It tests a ready-to-run collection, not an embedded console. Its own range spans a 33x spread. One publisher went from 17 to 10 minutes, which is 1.7x. |

**What to say to the CPO:**
- The "10x" is almost certainly the Moneris story. Postman sells collections and consoles, so it has a direct commercial interest.
- Neither figure is a controlled, independent result. Neither isolates the console's effect.
- Cite both only as named vendor case studies.

**What supports the recommendation instead:**
- **Practitioner consensus.** Stripe's docs embed live, personalized test keys in the code samples. GitBook grades interactive try-it as the difference between good and great reference docs. This is expert opinion, not measured ROI.
- **A target you can defend:** first successful call in under 10 minutes. That is the practitioner consensus bound (Mintlify's stated 5–10 minute target). It is a borrowed target, not an industry average.

**How to get a real ROI number:**
1. Measure Corven's current time-to-first-call now. Use a stopwatch test with 5 new integrators, or use API key creation to first 2xx in your logs.
2. Ship the console.
3. Measure again, and track the share of tickets about missing or wrong reference content.
4. Report your own before/after figure. That number will survive the review.

**Sequencing risk:** the skill's rollout treats the console as stage 4 of 5. It assumes the reference already renders from the spec and that lint and contract gates exist. A console on a hand-maintained, drifting reference puts a live "Send" button on pages that may be wrong. If Corven's reference is hand-written, the structural fix comes first. The skill's default package is a spec linter in CI plus contract tests, which takes days of setup.

---

## Possible challenges and how to answer them

| Challenge | Answer |
|---|---|
| "Is 67% bad?" | It's a mean score across five metadata dimensions, so it shows incompleteness, not failure. The sharper stat is that 87% of specs have no parameter examples. |
| "Where's the dollar cost?" | None is published that I'd defend. Slide 2 gives the model and the inputs Corven needs to produce its own. |
| "Vendor says 10x." | It's a vendor customer story that bundles the console with other onboarding changes. We'll measure our own before and after. |
| "Do these apply to logistics?" | No stat here is logistics-specific. Say so before someone else does. |

## Questions that would sharpen this

The skill asks these before an audit. Your answers decide whether slide 3's try-it recommendation is the right first move:
1. Is there an OpenAPI spec, and is the published reference rendered from it or hand-written?
2. Which SDK languages do you ship, and are snippets generated or hand-written?
3. What CI gates touch the spec or docs today?
4. Who reads the reference: partners, first-party teams, or coding agents?
5. Is there a safely callable sandbox or staging environment?