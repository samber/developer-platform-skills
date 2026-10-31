# Lumière Open License model card and AI Act check

## Short answer

1. **No, you are not covered by the open-source exemption.** Legal's assumption is wrong on two independent grounds (below).
2. **Do not write "fully open source" in the card.** Write "open weights" or "source-available".
3. **Even a truly open-source model would not skip everything.** Two obligations always apply, so some paperwork is unavoidable.

I'm not your lawyer. Have counsel confirm this before release, especially the dates.

## Why the exemption does not apply

Article 53(2) of the AI Act (Regulation 2024/1689) exempts only models released under a "free and open-source licence". That means a licence allowing access, use, modification and distribution, with weights and architecture public. Recitals 102–103 add that monetisation takes a model out of the exemption.

| Your term | Problem |
|---|---|
| Paid above $5M revenue | This is monetisation. It also discriminates by who the user is, which the open-source definition forbids (OSD #5). |
| No military use | This is a field-of-use restriction (OSD #6). It is a legitimate choice, but it is not open source. |
| Free only below $5M revenue | A free tier does not change this. The licence as a whole is not free and open-source. |

The Open Source Initiative's Open Source AI Definition 1.0 fails you on the same two points. It also requires detailed training-data information. So the marketing claim is wrong under the AI Act and under the OSI definition. It also exposes you to a misleading-advertising complaint.

## Are you in scope?

Yes.

- **Provider:** you trained the model, you are in Lyon, and publishing on Hugging Face places it on the EU market.
- **General-purpose AI model:** the Commission's July 2025 guidelines use an indicative test. A model trained with more than 1e23 FLOP that generates text is presumed general-purpose. At about 3e23 FLOP you pass that test.
- **Systemic risk:** the presumption starts at 1e25 FLOP, and you are about 33 times below it. Articles 55 and 56 do not apply unless the Commission designates you, which is unlikely.
- **Timing:** the obligations have applied since 2 Aug 2025. The AI Office has had enforcement powers since 2 Aug 2026. The grandfathering to Aug 2027 is only for models placed on the market before Aug 2025, so it does not cover a new model.
- **Fines:** up to 3% of worldwide turnover or €15M, whichever is higher (Art. 101).

## What you owe (Art. 53)

| Obligation | Exemption would have removed it? | Do now |
|---|---|---|
| (a) Technical documentation (Annex XI) | Yes, if open source | Prepare it and keep it ready for the AI Office on request. It is not public. |
| (b) Information for downstream providers (Annex XII) | Yes, if open source | Put it in the card or a linked doc. |
| (c) Copyright policy, including honouring text-and-data-mining opt-outs | No | Write it and publish a link. |
| (d) Public training-content summary, using the Commission's template | No | Publish it and link it from the card. |
| Cooperate with authorities (Art. 53(3)) | No | Name a contact. |

The exemption would only have saved (a) and (b). A good model card covers most of that anyway. Changing your licence to Apache 2.0 would therefore buy little.

Consider signing the GPAI Code of Practice (July 2025). It gives you a recognised way to show compliance.

**Check before you publish:** 3e23 FLOP for 7B parameters implies about 7T training tokens (compute ≈ 6 × parameters × tokens). Your data summary must be consistent with that. The Digital Omnibus proposals may shift some AI Act timelines, so have counsel confirm the dates.

## What to put on Hugging Face

**YAML header:**

```yaml
---
license: other
license_name: lumiere-open-license
license_link: LICENSE
language: [<languages>]
library_name: <transformers|...>
pipeline_tag: text-generation
tags: [text-generation, open-weights]
---
```

**Card body (replace every `<...>` with a real value):**

```markdown
# <Model name> (7B)

Open-weights text-generation model trained from scratch by Lumière Labs (Lyon, France).

## License
Released under the **Lumière Open License** (see LICENSE). This is **not** an
OSI-approved open-source licence.
- Free for organisations with annual revenue under US$5M.
- Commercial licence required above that threshold: <contact/URL>.
- Military use is prohibited.
Weights, architecture and usage instructions are public. Training data is not released.

## Model details
- Parameters: 7B
- Architecture: <details>
- Training compute: approx. 3 × 10^23 FLOP
- Training data: see the public summary: <link to Commission-template summary>
- Context length / tokenizer: <...>
- Release date: <...>

## Intended use and out-of-scope use
<intended uses> / <out-of-scope>, including military use (prohibited by licence).

## Evaluation
<benchmarks, methodology, dates>

## Limitations, bias and safety
<known failure modes, languages, hallucination, evaluation gaps>

## EU AI Act information
Lumière Labs is the provider of this general-purpose AI model under Regulation (EU) 2024/1689.
- Training content summary: <link>
- Copyright policy (incl. text-and-data-mining opt-out compliance): <link>
- Integration information for downstream providers: <link or section>
- Contact: <email>

## Citation
<...>
```

## Messaging for marketing

- Use "open weights, free for companies under $5M revenue" or "source-available".
- Avoid "open source", "fully open" and "open" used alone as a claim about the licence.
- Consider renaming the licence (for example, "Lumière Community License"). "Open License" invites the same confusion.
- If the open-source label really matters, the options are Apache 2.0 or MIT, which drops the revenue tier and the military ban. A fully OSI-conformant release would also need training-data information.

## Next steps

1. Decide with counsel whether you keep the licence and drop the "open source" claim (recommended).
2. Draft the training-content summary from the Commission template, and have data and ML check it against the ~7T-token figure.
3. Write the copyright policy and the Annex XI and XII documents.
4. Fill in the card and publish only after items 2 and 3 exist, since the card links to them.
5. Decide whether to sign the Code of Practice.