# Harrowgate Voice: Hugging Face release plan and card checklist

**I can't confirm counsel's position. Two of its three points don't hold, and the third does the opposite of what they intend.** I'm not a lawyer, so counsel makes the final call. They should work from the points below.

Labels: **[HF]** is what Hugging Face publishes. **[EU Commission]** is AI Act guidance. **[practitioner]** is my own reading. Re-check live pages before committing money or a date.

## 1. Fit verdict

**Publish.** You ship weights developers will load, and the Hub is the default home.

## 2. Verdict on each point counsel made

| Counsel's claim | Verdict | Why |
|---|---|---|
| "We have no EU customers, so the AI Act is irrelevant." | ❌ Wrong | A public Hub repo can be downloaded in the EU, which places the model on the EU market. Non-EU providers outside the exemption also owe an EU authorised representative. Being a Delaware company doesn't change this. [EU Commission] |
| "TTS isn't general-purpose, so it's out of scope." | ⚠️ Not safe to assume | The indicative test has two parts: more than 10^23 FLOP of training compute, and the ability to generate "language (text or audio), text-to-image, or text-to-video". Your 2e23 is about 2x the threshold, and TTS generates audio, so it sits inside the modality test. The guidance calls this "not an absolute rule". A single-task model may exceptionally fall outside if it lacks significant generality. That is an argument counsel can write down and own, not a default. [EU Commission] |
| "Turn on the EU block and call it done." | ❌ Wrong | `extra_gated_eu_disallowed: true` only works on gated repos. It is a license-distribution control, not an AI Act opt-out. [HF] It would also force you to gate an Apache-2.0 model, and gating has no reason you can name here (see section 5). |
| "Open license, so exemption applies" (the likely fallback) | ⚠️ Probably partial | The exemption needs a free and open-source license with no monetisation, public weights, and no systemic risk (presumed above 10^25 FLOP). Apache-2.0 and 2e23 fit those conditions. The exemption only lifts technical documentation, downstream documentation and the EU representative. The copyright policy and the public training-data summary still apply. [EU Commission] |

**Decision for counsel:** either the single-task argument holds, or you are a GPAI provider with the open-source exemption. Both need a written record.

**Monetisation risk:** the Community FAQ template links a "commercial support or hosted API" page. If Harrowgate sells a hosted TTS API, counsel must decide whether that is "monetisation" that voids the exemption. This is my reading, not Commission guidance. [practitioner]

**Timing:** obligations have applied since 2 Aug 2025. Commission enforcement, including fines, started 2 Aug 2026, which is already past. A November 2026 release has no grace period. The 2 Aug 2027 date is only for models released before Aug 2025. [EU Commission]

## 3. Repo layout

| Repo id | Variant | `base_model` | License | Gate |
|---|---|---|---|---|
| `<org>/<model>-3B` | Base TTS weights, safetensors | omit (trained from scratch) | `apache-2.0` | none |
| Collection `<model> family` | Groups future sizes and quantizations | n/a | n/a | n/a |

- Future fine-tunes and quantizations get their own repos with `base_model` pointing at the parent. Never set `base_model` between sibling sizes. [HF]
- Ask me if you want a GGUF or quantized repo. It only pays off for a laptop or local-app audience. [HF]

## 4. Release actions, ranked by value per hour

| # | Action | Owner | When |
|---|---|---|---|
| 1 | Start org verification. It is manual and takes days to weeks. [practitioner] | `<admin>` | Today |
| 2 | Complete card metadata. | `<owner>` | T-14 |
| 3 | Create the collection. | `<owner>` | T-14 |
| 4 | Write and test the copy-run snippet in a clean environment. | `<owner>` | T-3 |
| 5 | Build the linked Space demo (section 6). | `<owner>` | T-3 |
| 6 | Submit Daily Papers if there is an arXiv paper. The window closes 14 days after the first arXiv version. [HF] | `<owner>` | T-0 |
| 7 | Add `.eval_results/` files, only for official Hub benchmarks. | `<owner>` | Weeks 1-2 |
| 8 | Library registration, only if you ship your own loading library. | `<owner>` | Later |

**Note:** I don't know your release date or who owns the Community tab and for how many hours a week. Fill those in.

## 5. Gate decision

**Open, license in card.** Gating needs a reason you can name, and you have none. Apache-2.0 has no use restrictions, and a lead form would contradict your open-source positioning. [HF]

- Gating collects requesters' email addresses and makes you handle them.
- Grants are per individual user, never per company.
- Gating won't give counsel an AI Act opt-out.
- Don't use `extra_gated_eu_disallowed`.

## 6. Space plan

- **Plan check:** a free org can host Static Spaces only. Gradio and Docker need Team or Enterprise. A personal PRO account works but loses the author-owned star on the model page. [HF]
- **Likely choice:** a 3B TTS model is too heavy for in-browser transformers.js. I'd use Gradio + ZeroGPU, which needs the paid plan above. [practitioner]
- Set `@spaces.GPU(duration=...)` to the real worst case. Above 120 s, anonymous visitors can never run it. [HF] [practitioner]
- List the repo under `models:` in the Space README so the Space appears on the model page.
- Keep API keys in Space secrets, and scan git history for tokens before going public. [HF]

Which org plan do you have?

## 7. AI Act line

- Provider: yes, as the entity placing the model on the EU market. [EU Commission]
- Indicative GPAI model: yes (2e23 FLOP, audio generation). Counsel may argue the single-task exception.
- **Duties that apply either way:**
  - A copyright policy.
  - A public training-data summary on the AI Office template. Link both from the card.
- **Duties lifted only if the open-source exemption holds:**
  - Technical documentation.
  - Downstream documentation.
  - EU authorised representative.
- Counsel confirms the exemption (monetisation question above) and checks that the compute figure includes all training runs.

## 8. Cadence

If release is R, and R is about 30 days out, T-30 is today.

1. **T-30 or now:** start verification, set member roles, and get counsel's AI Act decision in writing.
2. **T-14:** card drafted, collection created, repos private.
3. **T-3:** recreate the repo, or squash and delete every old PR ref, branch and tag. Scan for tokens, test the snippet clean, make the Space live and linked, write the pinned FAQ. Squashing cannot be undone. [HF]
4. **T-0:** flip repos public together, post the Hub link, staff the Community tab daily. Submit Daily Papers if you are inside the window.
5. **Weeks 1-2:** answer every discussion and merge useful PRs.
6. **Week 4 on:** community quantizations and fine-tunes appear in the model tree. Link the good ones.

## 9. Card checklist and filled template

**Metadata (card YAML)**
- [ ] `license: apache-2.0`
- [ ] `pipeline_tag: text-to-speech`
- [ ] `library_name` set explicitly (transformers repos created after Aug 2024 need it). [HF]
- [ ] `language` listed
- [ ] `datasets` only if public
- [ ] No `base_model`, since it is trained from scratch
- [ ] No `extra_gated_*` fields

**Files and snippet**
- [ ] safetensors weights only, no `.bin` or `.pth`. [HF]
- [ ] Copy-run snippet tested in a clean environment, with no local path or private package.
- [ ] No `trust_remote_code` unless the architecture truly needs it. If it does, say so in the card and FAQ. [practitioner]

**Body sections, in order**
- [ ] Summary and intended use.
- [ ] Usage snippet.
- [ ] Specs and hardware needs.
- [ ] Evaluation with sources.
- [ ] Limitations and biases. Include misuse risk such as voice cloning. [practitioner]
- [ ] Links to the **copyright policy** and **training-data summary**.
- [ ] Citation with the arXiv link.

**Before public**
- [ ] Git history scanned for tokens, old checkpoints and unreviewed text.
- [ ] Space linked via `models:`.
- [ ] Pinned FAQ written.
- [ ] No rewards offered for likes. [HF]

```yaml
---
license: apache-2.0
pipeline_tag: text-to-speech
library_name: <transformers>
language:
  - <en>
datasets:
  - <org/training-dataset>
tags:
  - <tts>
---
```

```python
from transformers import pipeline
pipe = pipeline("text-to-speech", model="<org>/<model>-3B")
audio = pipe("<prompt text>")
```

*(Check the snippet matches your real loading code before publishing.)*

**Space README header**

```yaml
---
title: <Model name> demo
sdk: gradio
short_description: <one line shown on the thumbnail>
models:
  - <org>/<model>-3B
---
```

**Pinned Community FAQ**

```
Title: Start here: FAQ, known issues, where to report bugs

- Hardware: <minimum VRAM> for <precision>.
- Known issues: <issue 1>, <issue 2>.
- Bugs in the loading library: <GitHub issues link>. Questions about this model: reply here.
- Fine-tunes and quantizations: set base_model: <org>/<model>-3B so they appear in the model tree.
- Commercial support or hosted API: <link, only after counsel clears the monetisation question>.
```

## 10. Measurement

- Report likes, downloads and Space visits as separate lines, each with its counting rule. A download is any GET or HEAD on `config.json`, not deduplicated. [HF]
- Never sum Hub downloads with PyPI or npm downloads.
- Use derivatives in the model tree (fine-tunes, quantizations) as the adoption signal. [HF]
- Target: a staff reply on the Community tab within one business day for the first month (self-set).
- Don't read a flat download curve in week one as failure. [HF blog]

## Open questions for you

1. What is the release date?
2. Which org plan do you have: free, Team or Enterprise?
3. Do you sell a hosted TTS API?
4. Is there an arXiv paper, and does it have a date?
5. Who owns the cards, the Space and the Community tab?