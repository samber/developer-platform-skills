# Hugging Face templates

Replace every `<...>`. Delete fields that do not apply rather than leaving them empty.

## Contents

- Model card YAML skeleton
- Quantized variant card
- Eval-results file
- Dataset card YAML skeleton
- Space README header
- Gate prompt (click-through, no PII)
- Pinned Community tab FAQ
- Discussion replies
- Provider-support request
- Launch Post

## Model card YAML skeleton

```yaml
---
license: apache-2.0 # or: other + license_name + license_link
pipeline_tag: <text-generation>
library_name: <transformers>
language:
  - en
base_model: <org/base-model> # omit for a model trained from scratch
datasets:
  - <org/training-dataset>
tags:
  - <domain-tag>
new_version: <org/newer-model> # only on the OLD card, once a successor exists
---
```

Body sections, in order: one-paragraph summary with intended use; copy-run usage snippet; technical specs and hardware needs; evaluation with sources; limitations and biases; license and training-data summary links; citation with the arXiv link (creates the `arxiv:` tag).

✓ Good - snippet a reader runs unedited:

```python
from transformers import pipeline
pipe = pipeline("text-generation", model="<org>/<model>")
print(pipe("<prompt>")[0]["generated_text"])
```

✗ Bad - snippet that needs a local path, a private package or an unpublished checkpoint:

```python
model = load("/data/ckpt/final_v3.bin")
```

## Quantized variant card

```yaml
---
base_model: <org>/<model>
base_model_relation: quantized
license: <same as base>
---
```

State the quantization method, bits, file per hardware tier, and the measured quality delta against the base.

## Eval-results file

One YAML file per benchmark in `.eval_results/` of the model repo. The benchmark must be an official Hub benchmark dataset; `task_id` comes from its `eval.yaml`. `model-index` in the card is the older format; prefer `.eval_results/`.

```yaml
# .eval_results/<benchmark>.yaml
- dataset:
    id: <org/benchmark-dataset>
    task_id: <task from eval.yaml>
  value: <score>
  date: "<YYYY-MM-DD>"
  source:
    url: <link to the run or report>
    name: <Model Card | paper | leaderboard>
```

## Dataset card YAML skeleton

```yaml
---
license: cc-by-4.0
task_categories:
  - <text-classification>
language:
  - en
size_categories:
  - <10K<n<100K>
configs:
  - config_name: default
    data_files:
      - split: train
        path: data/train-*.parquet
---
```

Body: collection process, consent and licensing of sources, personal-data handling, known gaps, intended and out-of-scope uses.

## Space README header

```yaml
---
title: <Model name> demo
sdk: gradio
short_description: <one line shown on the thumbnail>
models:
  - <org>/<model>
---
```

## Gate prompt (click-through, no PII)

Use with automatic approval and username and email collection turned off in the gating settings.

```yaml
---
extra_gated_heading: "Accept the <License name> to access <model>"
extra_gated_prompt: "By accessing this model you agree to the <License name> at <link>."
extra_gated_button_content: "Accept license"
extra_gated_fields:
  I accept the license terms: checkbox
---
```

✗ Bad - a lead form on a model you call open:

```yaml
extra_gated_fields:
  Company: text
  Job title: text
  Phone: text
```

## Pinned Community tab FAQ

```
Title: Start here: FAQ, known issues, where to report bugs

- Hardware: <minimum VRAM> for <precision>; GGUF builds in <collection link>.
- Known issues: <issue 1>, <issue 2>.
- Bugs in the loading library: <GitHub issues link>. Questions about this model: reply here.
- Fine-tunes and quantizations by the community: set base_model: <org>/<model> so they appear in the model tree.
- Commercial support or hosted API: <link>.
```

## Discussion replies

Bug that belongs in the library repo:

```
Thanks for the repro. This is in <library>, not the weights: tracked at <issue link>. Workaround until <version>: <one line>. Closing here so the fix discussion stays in one place.
```

Community PR adding eval results:

```
Thanks. We checked the score against <source>; merging. If you ran it with a different harness version, add it to the source field so readers can compare.
```

Off-topic or promotional thread:

```
Closing as off-topic for this model. For <topic>, the HF forum is the better place: <link>.
```

## Provider-support request

Post through "Ask for provider support" on the model page.

```
Requesting Inference Providers support for <org>/<model> (<task>, <params>B, <license>). Use case: <one line>. Weights in safetensors; chat template included. We can help with serving configs: <contact>.
```

## Launch Post

Needs a PRO account. Followers see it in chronological order.

```
We released <model>: <one-line capability>, <license>.
- Try it: <Space link>
- Weights and card: <model link>
- Paper: <hf.co/papers/id>
Smaller and GGUF variants: <collection link>. Questions in the Community tab.
```
