# Short answer: I can't confirm it, and I'd push back before you ship

Two of counsel's premises look wrong. The "EU block" fix also conflicts with your own license.

**Next action:** send counsel the three questions in section 3 before you publish. Details below. I'm not a lawyer, and I worked from memory of the Act and the Commission's July 2025 GPAI guidelines without browsing. Have counsel verify the citations.

## 1. Why "no EU customers" doesn't settle it

- The AI Act (Reg. 2024/1689, Art. 2(1)(a)) covers providers who place a GPAI model on the EU market, wherever they're established.
- Customers aren't the test. Making the weights available to people in the EU is the test, and a public Hugging Face repo does that.
- Delaware and Austin don't matter for scope.

## 2. Why "TTS isn't general-purpose" is a risky assumption

- The Commission's guidelines use an indicative test: training compute above **1e23 FLOP** and the model generates language, in text **or audio**. Your ~2e23 FLOP speech model meets both parts.
- The guidelines also say models above the line can fall outside GPAI if they're narrow. I recall transcription as an example. A single-task TTS model has a real argument here.
- That argument is a position you must document and defend. It isn't a default exemption, and counsel's "it's not a chatbot" reasoning doesn't make it.
- You're far below the 1e25 FLOP systemic-risk threshold, so the heavy obligations don't apply either way.

## 3. Questions for counsel

1. Was a GPAI-scope assessment done against the 1e23 FLOP and audio-generation indicator? Is the "narrow model, not significantly general" conclusion written down?
2. Does an EU block fit with Apache-2.0? Apache-2.0 allows no geographic restrictions. If you add one to the license, it's no longer Apache-2.0. If you add it only to gating or terms, you must show it works and isn't circumvented. Either way you probably lose the open-source exemption, because that requires a license that permits access, use, modification, and distribution.
3. Will you sell a hosted API or paid support for this same model? If so, the exemption may fail on monetization (Recital 103).

## 4. Your three realistic paths

| Path | What it means | Catch |
|---|---|---|
| **A. Apache-2.0, comply** | Publish openly and use the open-source exemption. | You still owe a copyright policy and a public training-data summary (see the card checklist). Monetization must stay clear of Recital 103. |
| **B. Exclude the EU properly** | Use a non-Apache license or terms that explicitly exclude EU distribution and use, with real gating. | You give up "Apache-2.0" and "open source" branding. The guidelines treat a good-faith, uncircumvented exclusion as meaning you didn't place the model on the EU market. A toggle alone may not be enough, and third-party mirrors are a residual risk. I couldn't verify that Hugging Face offers a native country block, so check what your gating setting actually does. |
| **C. Narrow-model position** | Argue the model isn't GPAI and document why. | It's defensible but untested. Combine it with A's card items as cheap insurance. |

I'd lean to **A + C**: the exemption is available, the card items are low-cost, and it keeps the Apache-2.0 promise.

## 5. Model card checklist (Path A)

**Required even with the open-source exemption**
- [ ] Copyright policy, published or linked, covering how you honor text-and-data-mining opt-outs (robots.txt and similar machine-readable signals)
- [ ] Public training-content summary, using the Commission's template: provider and model identity, modalities, data volume bracket, main data sources (public datasets, licensed, scraped with top domains), opt-out handling, and illegal-content filtering
- [ ] Contact point for rightsholder complaints

**Needed to claim the exemption**
- [ ] License file is unmodified Apache-2.0 with no added geographic or field-of-use limits
- [ ] Weights, architecture, and usage information public
- [ ] Written note on monetization: no paid access to this model, or why it doesn't void the exemption

**Good practice, and required if you lose the exemption (Annex XI/XII)**
- [ ] Architecture, parameter count (3B), modality (text to speech), and context limits
- [ ] Training compute (~2e23 FLOP) with method of estimate, and energy use if known
- [ ] Intended and out-of-scope uses, and an acceptable-use statement
- [ ] Languages and voices supported, known failure modes, and evaluation results
- [ ] Integration notes for downstream developers

**Voice-specific**
- [ ] Ban on impersonation, fraud, and non-consensual voice cloning in the card and usage terms
- [ ] Watermarking or provenance support for outputs, or an honest note that none exists. Art. 50(2) requires machine-readable marking of synthetic audio for AI systems, which would cover a hosted demo or Space. Check whether the Digital Omnibus has shifted its dates.
- [ ] Consent and provenance statement for voice training data, including any personal data and its legal basis
- [ ] Note on US voice-likeness laws such as state right-of-publicity statutes

**Process**
- [ ] Written scope assessment saved (section 3, question 1)
- [ ] Decide whether to sign the GPAI Code of Practice, which is optional but gives a presumption of conformity
- [ ] Calendar a recheck. The Commission's GPAI enforcement powers began 2 Aug 2026, with fines up to 3% of turnover or €15M.

## 6. Bottom line

Don't treat the EU block as "done". It may not satisfy the Act, and as described it breaks the Apache-2.0 promise. Either comply with the light open-source track (Path A) or switch to a license that excludes the EU (Path B). Get counsel's written answer to the three questions first.