# Tallow-ASR launch checklist (Hugging Face)

Today is Sat 2026-10-31 and launch is Tue 2026-11-03 (T-0). That is 3 days, so the usual T-30 to T-0 cadence is squeezed into the steps below. Plan limits and policy wording change, so re-check the live pages before you spend money or commit to a date.

Labels: **[HF]** = Hugging Face docs or policy, **[EU Commission]** = AI Act guidance, **[practitioner]** = reverse-engineered, not official.

## Fit verdict

**Publish.** You ship loadable ASR weights, so the Hub is the right home.

## Verdicts on your plan

| Plan item | Verdict | Fix |
|---|---|---|
| One repo with a subfolder per size and `/gguf` | ❌ Change | Use one repo per variant, grouped in a collection. A folder has no URL, no search entry and no download count. [HF] |
| Weights are `pytorch_model.bin` | ❌ Change | Convert to safetensors. Pickle files get import-scan warnings, and enterprise reviewers stop at them. GGUF is not pickle. [HF] |
| Gradio demo Space under the org | ❌ Not on a free org | A free org can host Static Spaces only. Gradio and Docker need Team or Enterprise, billed per seat for every member. [HF] See the Space plan below. |
| Raffle three RTX cards among everyone who likes the repo | ❌ Drop it | The Content Policy restricts "incentivizing manipulation of Hugging Face Hub metrics (e.g., exchanging rewards for likes)". Sanctions include unranking, which is the opposite of trending. [HF] |
| Open-source on Tuesday | ✅ Keep | Compress the cadence. Org verification is manual and takes days to weeks, so it will probably not finish by Tuesday. [practitioner] |
| GGUF build | ✅ Keep | A GGUF repo makes llama.cpp-family tools show up in "Use this model" for compatible formats. [HF] |

## Repo layout

Confirm the license, which size the GGUF is built from, and the loading library (see Open questions). Rows assume Apache-2.0 and `transformers`.

| Repo id | Variant | `base_model` | License | Gate |
|---|---|---|---|---|
| `tallowmere/tallow-asr-tiny` | tiny, safetensors | none (trained from scratch) | `<license>` | open |
| `tallowmere/tallow-asr-small` | small, safetensors | none | `<license>` | open |
| `tallowmere/tallow-asr-medium` | medium, safetensors | none | `<license>` | open |
| `tallowmere/tallow-asr-<size>-gguf` | GGUF quantization of `<size>` | `tallowmere/tallow-asr-<size>`, `base_model_relation: quantized` | same as base | open |
| Collection "Tallow-ASR" | groups all of the above | n/a | n/a | n/a |

- Never set `base_model` between the sibling sizes. It draws a false lineage. [HF]
- Create one GGUF repo per size you actually ship.
- The first two collections show on the org page, so make Tallow-ASR the first. [HF]

## Ranked release actions

Owners are placeholders. Assign them today.

| # | Action | Owner | Date |
|---|---|---|---|
| 1 | Start org verification and add the email domain. Then audit joiners and set them to read: a matching email address lets anyone join. [HF] | `<admin>` | Sat |
| 2 | Convert the `.bin` weights to safetensors. Check that transcripts and WER on a fixed test set match the originals. | `<ML eng>` | Sat |
| 3 | Write complete card metadata for each repo (YAML below). | `<owner>` | Sun |
| 4 | Create the repos as private. Create the collection. | `<owner>` | Sun |
| 5 | Test the usage snippet in a clean environment: no local paths, no private packages, no `trust_remote_code` unless the architecture needs it. | `<eng>` | Sun |
| 6 | Build the Space (see Space plan). | `<eng>` | Sun to Mon |
| 7 | Build the GGUF repo. State the quantization method, bits, file per hardware tier, and the measured WER delta against the base. | `<ML eng>` | Sun |
| 8 | Add the AI Act links to the cards (copyright policy, training-data summary). | `<counsel/owner>` | Mon |
| 9 | Submit to Daily Papers, only if an arXiv paper exists and its first version is under 14 days old. A v2 does not reopen the window. [HF][practitioner] | `<owner>` | Tue |
| 10 | Add eval results as `.eval_results/` files, but only against official Hub benchmark datasets. | `<ML eng>` | Week 1 |
| 11 | File an "Ask for provider support" request. | `<owner>` | Tue |
| 12 | Register the library in `huggingface.js`, only if you ship your own loading library. It is high value but slow, so plan it for after launch. [HF] | `<eng>` | Week 2+ |

## Gate decision

**Open, license in the card.** Adoption is the goal and no dual-use risk is named. Gating collects requesters' emails and creates a duty to handle them. [HF]

If you want leads, put a "commercial license or hosted API" link in the card and the pinned FAQ, pointing to your own form. Expect a pull funnel, not a list.

## Space plan

The demo is needed for adoption, but a Gradio Space is not available on a free org. Options, in order of preference:

1. **Static Space under the org**, running in the browser (transformers.js or ONNX). It is free and keeps the org-owned star on the model page. Browser-side ASR is realistic for tiny and probably small. This needs an ONNX export, so decide today whether it fits.
2. **Upgrade the org to Team** and run Gradio plus ZeroGPU (50 ZeroGPU Spaces for a Team org). [HF] Seats are billed for every member, so check the live price and limit members first. Set `@spaces.GPU(duration=...)` to the real worst-case audio length. The platform refuses a run when the visitor's remaining daily quota is below the declared duration. Above 120 s, anonymous visitors can never run it. [HF][practitioner]
3. **Gradio Space on a personal PRO account.** This works, but the Space loses the author-owned star on the model page. [HF] Use it only as a fallback.

Whichever you pick:

- Load weights from the Hub repos and list them under `models:` in the Space README. That is how the Space appears on the model page. [HF]
- Keep keys in Space secrets, never in `app.py`.
- Don't promise an inference widget. It appears only if an Inference Provider serves the model. [HF] The Space is your fallback.
- Free CPU Spaces sleep after 48 h without visits. [HF]

## EU AI Act line

- **Modality:** speech recognition falls inside the "can generate language (text or audio)" test. [EU Commission]
- **Compute:** the indicative threshold is 10^23 FLOP of training compute. Tell me your rough FLOP for the largest size. A single-task model above it may exceptionally fall outside if it lacks significant generality. Record either argument and route it to counsel. [EU Commission]
- **Territory:** a public Hub repo is downloadable in the EU, so it counts as placed on the EU market even with no EU customers. Non-EU providers outside the exemption also owe an EU authorised representative. [EU Commission]
- **Obligations:** every provider owes a copyright policy and a public training-data summary on the AI Office template, and both must be linked from the cards. Obligations have applied since 2 Aug 2025. Enforcement, including fines, starts 2 Aug 2026. [EU Commission]
- **Exemption:** it needs a free and open-source license with no monetisation. The copyright policy and the training-data summary apply to every provider regardless. Send the final call to counsel.

## Cadence

| When | Task |
|---|---|
| **Sat 10-31** | Start verification. Convert to safetensors. Create private repos and the collection. |
| **Sun 11-01** | Write cards and run the clean-environment snippet test. Build the GGUF repo. Start the Space. Write the FAQ. |
| **Mon 11-02** | Recreate the repos, or squash `main` and delete every old PR ref, branch and tag. Squashing cannot be undone. [HF] Scan history for tokens, eval data and old checkpoints. Space live and linked. Final snippet test. Pin the FAQ. |
| **Tue 11-03 (T-0)** | Flip all repos public together. Post the Hub link on your channels. Submit Daily Papers if eligible. Staff the Community tab daily. |
| **Weeks 1 to 2** | Answer every discussion. Merge useful PRs (eval results, card fixes). |
| **Week 4 on** | Link good community quantizations and fine-tunes from the collection. |

Flipping a repo public publishes its whole git history. If these repos already exist with training history, recreate them instead of flipping. [HF]

## Getting on trending without a raffle

Trending "is influenced by the number of likes in the past few days", and visits count too. [HF] What to do instead:

- Ask people to try the model, never to like it in exchange for anything. This applies in the pinned FAQ, the Post and every channel.
- Link every external post to the Hub model page, not your website.
- Concentrate your launch traffic in the first days.
- Grow org followers before Tuesday.
- Unrewarded likes from colleagues are not named in the policy, but a spike of brand-new accounts invites a moderation look. [practitioner] Ask staff who already have Hub accounts to try the demo, and don't run a push.
- Don't read a flat download curve in week one as failure. Likes go to new releases in their first weeks, and downloads build over months. [HF blog]

## Filled templates

**Model card YAML (each size).** Repeat for tiny, small and medium.

```yaml
---
license: <license>
pipeline_tag: automatic-speech-recognition
library_name: transformers # set explicitly; required for repos created after Aug 2024
language:
  - en # list every supported language
datasets:
  - <org/training-dataset> # omit if private
tags:
  - speech
---
```

Body, in order:

1. Summary and intended use.
2. Copy-run snippet.
3. Specs and hardware needs.
4. Evaluation with sources.
5. Limitations and biases.
6. License, copyright policy and training-data summary links.
7. Citation with the arXiv link.

**Usage snippet** (run it unedited in a clean environment before launch):

```python
from transformers import pipeline
pipe = pipeline("automatic-speech-recognition", model="tallowmere/tallow-asr-small")
print(pipe("sample.wav")["text"])
```

**GGUF card.**

```yaml
---
base_model: tallowmere/tallow-asr-<size>
base_model_relation: quantized
license: <same as base>
---
```

**Space README header** (replace `sdk: static` with `sdk: gradio` only after you have a plan that allows it).

```yaml
---
title: Tallow-ASR demo
sdk: static
short_description: Try Tallow-ASR speech recognition in your browser
models:
  - tallowmere/tallow-asr-tiny
  - tallowmere/tallow-asr-small
---
```

**Pinned Community FAQ.**

```
Title: Start here: FAQ, known issues, where to report bugs

- Hardware: <minimum VRAM> for <precision>; GGUF builds in <collection link>.
- Known issues: <issue 1>, <issue 2>.
- Bugs in the loading library: <GitHub issues link>. Questions about this model: reply here.
- Fine-tunes and quantizations by the community: set base_model: tallowmere/tallow-asr-<size> so they appear in the model tree.
- Commercial support or hosted API: <link>.
```

**Provider-support request** (via "Ask for provider support" on the model page).

```
Requesting Inference Providers support for tallowmere/tallow-asr-<size> (automatic-speech-recognition, <params>M, <license>). Use case: <one line>. Weights in safetensors. We can help with serving configs: <contact>.
```

**Launch Post** (needs a PRO account; followers see it chronologically).

```
We released Tallow-ASR: open speech recognition in tiny, small and medium, <license>.
- Try it: <Space link>
- Weights and card: <model link>
- Paper: <hf.co/papers/id>
GGUF variants: <collection link>. Questions in the Community tab.
```

**Discussion replies:** use the three templates in `references/templates.md` for library bugs, community PRs adding eval results, and off-topic threads.

## Measurement plan

- Report likes, downloads and Space visits as three separate lines, each with its counting rule.
- A model download is any GET or HEAD on `config.json`, not deduplicated, so clones and CI cache misses count. [HF]
- Never sum Hub downloads with PyPI or npm downloads, or model downloads with dataset downloads.
- Use derivatives in the model tree (fine-tunes, quantizations, adapters) as the adoption signal. [HF]
- Publisher Analytics needs Team or Enterprise, and unique downloaders need an Enterprise Plus export. On the free plan you only see the public counters. [HF]
- Target: median time to first staff reply under one business day for the first month (self-set).

## Open questions

Answer these before Monday:

1. Which license? Do you inherit terms from a base model?
2. Which size is the GGUF built from, and for which runtime?
3. Is there an arXiv paper, and what is its first-version date?
4. What are the rough training FLOP of each size, and where is Tallowmere incorporated?
5. Do you ship your own loading library, or use plain `transformers`?
6. Do the repos already exist privately with history?
7. Who owns the Community tab, and for how many hours a week?
8. Would you pay for Team, or do you prefer the Static Space?