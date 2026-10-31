# Lumière Labs 7B on Hugging Face: card contents and AI Act position

**Short answer:** no, you're not good yet. Neither assumption holds.

1. **Marketing:** you can't call this "fully open source". Call it open weights.
2. **Legal:** the AI Act open-source exemption almost certainly does not cover you. You owe the full provider duties, and the deadline has already passed.

Source labels: **[HF]** is Hugging Face docs or policy. **[EU Commission]** is AI Act guidance. **[practitioner]** is reverse-engineering. Re-check live pages before committing money or a date. Treat the legal call as provisional until counsel confirms it.

## 1. Fit verdict

**Publish.** You have weights that developers will load, and the Hub is the default home.

## 2. Verdicts on what you stated

| Claim | Verdict |
|---|---|
| "Fully open source" on HF | ❌ Don't use it. Your license has a revenue gate ($5M, paid above) and a use restriction (no military use). Say "open weights" and name the license. Marketing can still say "free for companies under $5M revenue". |
| "Legal assumed the AI Act exemption covers us, skip the paperwork" | ❌ The exemption needs a free and open-source license with no monetisation. A paid tier above $5M is monetisation, and the use restriction also likely disqualifies you. [EU Commission] |
| "Are we good?" | ⚠️ Not yet. See the AI Act line (section 7) for what you owe. |

## 3. What the license does to the label

- **Wording on the card and in announcements:** "open weights, released under the Lumière Open License".
- **Rename the license.** "Open" in the license name will draw the same "not open source" pushback. Consider "Lumière Community License".
- **Alternative if marketing insists on "open source":** relicense to Apache-2.0 or MIT, with no revenue gate and no military clause.
  - This is a business decision, and it can't be undone for versions already published.
  - It only makes the exemption possible, not automatic. You would still owe the copyright policy and the public training-data summary. The exemption also needs public weights and no systemic risk. [EU Commission]

## 4. Repo layout

I assumed one 7B, base plus optional instruct. Tell me if there are other sizes or variants.

| Repo id | Variant | `base_model` | License | Gate |
|---|---|---|---|---|
| `lumiere-labs/<model>-7B` | base, trained from scratch | omit | `other` / `lumiere-open-license` | click-through (see section 6) |
| `lumiere-labs/<model>-7B-Instruct` | instruct, if you ship one | `lumiere-labs/<model>-7B` | same, and the base license governs it | same |
| `lumiere-labs/<model>-7B-GGUF` | quantized, if you ship one | the parent repo, with `base_model_relation: quantized` | same | same |

Group them in one collection. Don't set `base_model` between sibling sizes. [HF]

## 5. The card

### Metadata

```yaml
---
license: other
license_name: lumiere-open-license
license_link: LICENSE
pipeline_tag: text-generation
library_name: transformers
language:
  - fr   # replace with the real training languages
  - en
datasets:
  - <lumiere-labs/training-dataset>   # only if a Hub dataset exists
tags:
  - open-weights
---
```

- There is no `base_model`, because the model was trained from scratch.
- `library_name: transformers` must be explicit for repos created after August 2024. [HF]
- Weights must be **safetensors**, not `.bin` or `.pth`. [HF]
- Don't use `trust_remote_code` in the main snippet unless the architecture needs it. [practitioner]
- Put a `LICENSE` file in the repo.

### Body sections, in order

1. **Summary and intended use.** Include a line like: "Open weights under the Lumière Open License. Free for organisations under US$5M annual revenue; commercial license required above; military use prohibited. This is not an OSI-approved open-source license."
2. **Copy-run snippet**, tested in a clean environment:
   ```python
   from transformers import pipeline
   pipe = pipeline("text-generation", model="lumiere-labs/<model>-7B")
   print(pipe("<prompt>")[0]["generated_text"])
   ```
3. **Technical specs and hardware needs.** State 7B parameters, the minimum VRAM per precision, and training compute of roughly 3×10²³ FLOP.
4. **Evaluation, with sources.** Prefer `.eval_results/` files over `model-index`. [HF]
5. **Limitations and biases.**
6. **License and compliance links.**
   - Link the full license text.
   - Link the **copyright policy**.
   - Link the **public training-data summary** on the AI Office template.
   - Add: "Commercial license or hosted API: <your form link>".
7. **Citation**, with the arXiv link if you have a paper.

## 6. Gate decision

You have a nameable reason for a gate, namely a custom license with a commercial threshold. Use the lightest option: click-through with automatic approval, and username and email collection off. [HF]

```yaml
extra_gated_heading: "Accept the Lumière Open License to access <model>"
extra_gated_prompt: "By accessing this model you agree to the Lumière Open License at <link>. Organisations above US$5M annual revenue need a commercial license; military use is prohibited."
extra_gated_button_content: "Accept license"
extra_gated_fields:
  I accept the license terms: checkbox
```

- **Don't add company, title or phone fields.** That turns the gate into a lead form on a model you promote as open, and it hands you personal data to manage. [HF]
- **Don't use `extra_gated_eu_disallowed: true`.** It is a license-distribution control, not an AI Act opt-out. [HF]
- **Leads come from a pull funnel.** Use the "commercial license or hosted API" link in the card and the pinned FAQ. You'll get inbound interest, not a list.
- **Skip the gate entirely** if adoption is your top goal and you'd rather the license text alone carry the terms.

## 7. AI Act line

Lumière is a **provider of a general-purpose AI model, and the open-source exemption likely does not apply.**

- **Scope test.** Training compute of about 3×10²³ FLOP is above the indicative 10²³ threshold, and the model generates text. That is the indicative test, "not an absolute rule". [EU Commission]
- **Systemic risk.** You are far below the presumption threshold of 10²⁵ FLOP. No systemic-risk duties apply.
- **Exemption: likely lost.** It needs a free and open-source license without monetisation, public weights, and no systemic risk. Your revenue-gated paid tier and the military-use restriction both undercut the first condition. [EU Commission]
- **Duties you owe**, since the exemption likely fails:
  - **Technical documentation**, kept ready for the AI Office on request.
  - **Downstream information** for the developers who integrate the model.
  - **Copyright policy**, published and linked from the card.
  - **Public training-data summary**, on the AI Office template and linked from the card.
- **Authorised representative: not needed.** The EU representative duty falls on non-EU providers, and you are in Lyon. The exemption analysis does not change that.
- **Timing.** Obligations apply since 2 August 2025, and the Commission has enforced them, including fines, since 2 August 2026. Models placed on the market before August 2025 have until 2 August 2027, but a new release doesn't qualify. [EU Commission] Your documentation and summary should exist **before** you flip the repo public.
- **Routing.** Send the exemption question to counsel with the license text. Counsel might still find a path, but don't plan around one.

I'd suggest counsel also check whether signing the GPAI Code of Practice is worth it. That is outside this playbook, so verify it yourselves.

## 8. Ranked release actions

| # | Action | Owner (to assign) | When |
|---|---|---|---|
| 1 | Start org verification (manual, takes days to weeks) | org admin | now |
| 2 | Legal: copyright policy, training-data summary, technical documentation | legal | before T-3 |
| 3 | Complete card metadata, collection, license file | ML lead | T-14 |
| 4 | Test the copy-run snippet in a clean environment | ML lead | T-3 |
| 5 | Linked Space demo | demo owner | T-3 |
| 6 | GGUF and quantized repos | ML lead | T-0 to week 2 |
| 7 | Daily Papers submission, only if the arXiv version is under 14 days old | researcher | T-0 |
| 8 | Eval results files | ML lead | week 1–2 |

- Default rung: the first three plus a demo.
- **Likes:** never reward or trade for likes. The Content Policy bans it, and sanctions include unranking. Ask people to try the model, not to like it. [HF]

## 9. Space plan

- **Free org:** Static Spaces only (transformers.js or ONNX in the browser). A 7B model won't run that way.
- **Gradio plus ZeroGPU:** needs Team or Enterprise for an org (50 ZeroGPU Spaces), or PRO for a personal account. A Space outside the org loses the author-owned star on the model page. [HF]
- **Details:**
  - Set `@spaces.GPU(duration=...)` to the real worst case. Above 120 s, anonymous visitors can never run it. [practitioner]
  - List the model under `models:` in the Space README.
  - Keep secrets in Space secrets, not `app.py`.

## 10. Cadence

I don't know your release date. Give it to me and I'll turn these into calendar dates.

1. **T-30 or now:** start org verification and set member roles.
2. **T-14:** draft the card, create collections, keep repos private.
3. **T-3:**
   - Flipping a repo public publishes its whole git history. **Recreate the repo**, or squash and delete every PR ref, branch and tag.
   - Scan for tokens.
   - Test the snippet in a clean environment.
   - Make sure the Space is live, linked from the card, and the FAQ is written.
   - Confirm the compliance documents and links are live.
4. **T-0:** flip all repos public together, post the Hub link, and staff the Community tab daily.
5. **Weeks 1–2:** answer every discussion and merge useful PRs.
6. **Week 4 on:** link good community quantizations and fine-tunes in the collection.

## 11. Pinned Community FAQ

```
Title: Start here: FAQ, known issues, where to report bugs

- Hardware: <minimum VRAM> for <precision>; GGUF builds in <collection link>.
- License: Lumière Open License. Free under US$5M revenue; commercial license above; no military use. This is open weights, not OSI open source.
- Known issues: <issue 1>, <issue 2>.
- Bugs in the loading library: <GitHub issues link>. Questions about this model: reply here.
- Fine-tunes and quantizations by the community: set base_model: lumiere-labs/<model>-7B so they appear in the model tree.
- Commercial license or hosted API: <link>.
```

## 12. Launch Post (needs a PRO account)

```
We released <model>: <one-line capability>, open weights under the Lumière Open License.
- Try it: <Space link>
- Weights and card: <model link>
- Paper: <hf.co/papers/id>
Smaller and GGUF variants: <collection link>. Questions in the Community tab.
```

## 13. Measurement

- Report likes, downloads and Space visits as **separate lines**. Never sum Hub downloads with PyPI or npm downloads.
- A download is any GET or HEAD on `config.json`, not deduplicated. [HF]
- Use **derivatives in the model tree** (fine-tunes, quantizations, adapters) as the adoption signal. [HF]
- Target a median time to first staff reply under one business day for the first month (self-set).

## Open questions

1. Release date, and is there an arXiv paper?
2. Languages, and the loading library (I assumed `transformers`)?
3. Which variants ship (base only, instruct, GGUF)?
4. Org plan and verification status?
5. Who owns the cards, the Space and the Community tab?
6. Does legal already have the copyright policy and training-data summary in progress?