# Brightwell Data embedding model: gating on Hugging Face

**Don't set up the lead gate.** Release the model open, with the Apache-2.0 license in the card. Capture leads through a pull funnel on the model page instead (details below).

Labels: **[HF]** is Hugging Face's own docs and policy. **[practitioner]** is reverse-engineered. **[EU Commission]** is AI Act guidance. I haven't re-checked live pages, so re-check plan limits and policy wording before committing a date.

## Fit verdict

**Publish.** You ship weights developers will load, so the Hub is the right home. The open question is gating, not whether to publish.

## Verdict on the VP's plan

Manual approval with company, title, phone and team size, and SDRs rejecting students, fails on five counts.

1. **Access is granted per person, not per company.** [HF] Every engineer, notebook and CI job at a prospect must request access separately. Each one waits for an SDR before the model loads. A pipeline that calls `SentenceTransformer("brightwell/...")` fails until someone has been approved and has set a token.
2. **The people you most want will not fill it in.** This is the lowest-adoption option in the gate ranking (adoption cost `-`, compliance cost `---`). The skill's own bad-example template is "a lead form on a model you call open": company, job title and phone. Developers evaluating embeddings will pick a model with no form.
3. **You take on personal data.** Gating hands you requesters' email addresses and the duty to handle them. [HF] A phone number adds more PII. That means a privacy notice, a retention rule, a review queue and an SDR-hours cost.
4. **It contradicts the Apache-2.0 license.** Apache-2.0 has no field-of-use limits, so rejecting students is a use restriction in practice. You can't call the model "open source" and also screen users. [HF-style naming rule from the skill] If you really want to screen, the honest label is "open weights" under a custom license, which is a different product decision. Send this to counsel.
5. **Gating has no technical effect on spread.** Apache-2.0 lets any approved user redistribute the weights, so mirrors and re-uploads will appear. You pay the adoption cost and don't keep the exclusivity.

Also, a download is any GET or HEAD on a query file, not deduplicated, and a clone or CI cache miss counts. [HF] Hub downloads are not leads or users, and the VP's "every download becomes a lead" goal can't hold even with a gate. Tell the VP that early.

## Gate decision

| Option | Adoption | Compliance | Verdict |
|---|---|---|---|
| **Open, license in card** | +++ | + | **Choose this** |
| Gate, automatic approval, no PII, click-through | ++ | ++ | Only if you need recorded acceptance of terms. Apache-2.0 doesn't, and it yields no leads. |
| Gate, manual approval, custom fields | - | --- | The VP's plan. No nameable reason beyond lead capture. |
| Gate, approval by your own system | --- | --- | For paid access. Not your case. |

**Reason to leave it open:** gate only for a reason you can name. Apache-2.0 plus an embedding model has no dual-use or staged-access reason. Lead capture is not one that justifies the cost.

## Where leads come from instead

Expect a pull funnel, not a list.

1. **Card and pinned FAQ**: add a "commercial support, SLA or hosted API" link to your own form. This is the nameable, honest funnel.
2. **Linked Space** (see Spaces demo below): a visitor who tries it is a warmer signal than a download.
3. **Community tab**: staff it. Companies that ask questions there are your best leads; note them in the CRM by hand.
4. **Derivatives in the model tree** (fine-tunes, quantizations): the adoption signal for an open model. [HF] Fine-tuners are real users.
5. **Publisher Analytics**: daily counts on Team or Enterprise, not deduplicated. Unique downloaders exist only as an Enterprise Plus log export. [HF] Neither gives names.

Give the VP this framing: the Hub builds the audience and the card routes buyers to you. Sales should measure form submissions from the card link, not downloads.

## Repo layout

Fill the sizes and ids from your release. I assumed one family.

| Repo id | Variant | `base_model` | License | Gate |
|---|---|---|---|---|
| `brightwell/<embed-large>` | main | omit (from scratch) | apache-2.0 | none |
| `brightwell/<embed-small>` | smaller size, trained separately | omit; never point at the sibling | apache-2.0 | none |
| `brightwell/<embed>-GGUF` or ONNX | quantized | `brightwell/<embed-large>`, `base_model_relation: quantized` | apache-2.0 | none |

Group them in one collection. Set `pipeline_tag: feature-extraction` and `library_name: sentence-transformers` or `transformers`, plus `license`, `language` and `datasets`. Ship **safetensors** weights, not pickle-only `.bin`. Keep `trust_remote_code` out of the main snippet. [HF]

## Ranked release actions

Today is 2026-10-31, so the release is about 2026-11-14 and you are at T-14. The cadence compresses.

| # | Action | Owner | Date |
|---|---|---|---|
| 1 | **Start org verification now.** It is manual and takes days to weeks. [practitioner] Set member roles. | Admin | Today, 10-31 |
| 2 | Complete card metadata and create the collection. Repos stay private. | Model owner | By 11-04 |
| 3 | Write and test the copy-run snippet in a clean environment. | Model owner | By 11-07 |
| 4 | Linked Space demo, plan checked. | Demo owner | By 11-10 |
| 5 | Recreate the repos, or squash `main` and delete every old PR ref, branch and tag. Scan for tokens and eval data. | Model owner | 11-11 (T-3) |
| 6 | Pinned FAQ with the commercial-support link. | Community owner | 11-11 |
| 7 | **Flip all repos public together**; post the Hub link; staff the Community tab daily. | Everyone | 11-14 (T-0) |

Skip Posts and the org blog unless you have a PRO or Enterprise org. Submit a Daily Papers entry only if there is an arXiv paper and it is under 14 days past its first version. [HF]

## Space plan

- Check the plan first. A free org can host **Static Spaces only**; Gradio and Docker need Team or Enterprise. [HF]
- For an embedding model, a Static Space with transformers.js or ONNX running in the browser fits a free org. Otherwise use a Gradio Space with ZeroGPU on a Team or Enterprise org.
- Host the Space **inside the org**. A Space outside it loses the author-owned star. List the model under `models:` in the Space README.
- Don't make the Space a thin ad for a paid API; it sits next to the Content Policy's product-advertising line. [HF]

## AI Act line

- Embedding models usually fall outside the general-purpose AI test, which needs more than 10^23 FLOP **and** the ability to generate text, audio, images or video. [EU Commission]
- It is not an absolute rule. Record the argument and route it to counsel.
- A public Hub repo is downloadable in the EU, so a non-EU company can't use "no EU customers" as a defense. [EU Commission]
- Apache-2.0 without monetisation likely fits the open-source exemption. A gate with approval screening would undercut that argument, which is one more reason to stay open.

## Filled templates

Card header:

```yaml
---
license: apache-2.0
pipeline_tag: feature-extraction
library_name: sentence-transformers
language:
  - en
datasets:
  - <brightwell/training-dataset>
tags:
  - embeddings
---
```

Pinned Community tab FAQ:

```
Title: Start here: FAQ, known issues, where to report bugs

- Hardware: <min RAM/VRAM> for <precision>; GGUF/ONNX builds in <collection link>.
- Known issues: <issue 1>, <issue 2>.
- Bugs in the loading library: <GitHub issues link>. Questions about this model: reply here.
- Fine-tunes and quantizations: set base_model: brightwell/<embed-large> so they appear in the model tree.
- Commercial support, SLA or hosted API: <your form link>.
```

If you need the click-through anyway (it records acceptance and collects no PII), use the skill's template with automatic approval and username and email collection off:

```yaml
extra_gated_heading: "Accept the Apache-2.0 license to access <model>"
extra_gated_prompt: "By accessing this model you agree to the Apache License 2.0 at <link>."
extra_gated_button_content: "Accept license"
extra_gated_fields:
  I accept the license terms: checkbox
```

## Measurement plan

- Report likes, downloads and Space visits as separate lines, each with its counting rule. Never sum Hub downloads with PyPI or npm, or model with dataset downloads. [HF]
- Primary adoption signal: derivatives in the model tree.
- Lead signal: submissions of the card's commercial-support form, with source tagged.
- Community tab: median time to first staff reply under one business day for the first month (self-set target).
- Don't read a flat download curve in week one as failure. Downloads accrue to small, stable models over years. [HF]

## Rules to remember

- Never reward or trade for likes. [HF]
- Don't promise an inference widget; providers choose what they serve. [HF]

## Questions I assumed answers to

- **Org plan?** If it's free, the Space must be Static.
- **Is there an arXiv paper, and when was v1?** This decides Daily Papers.
- **Do you ship your own loading library?** If yes, library registration becomes worth the time.
- **Is the VP open to a fallback?** If they insist on lead capture, the least-bad version is the pull funnel above plus a pinned "tell us your use case" invitation. That is not a gate.