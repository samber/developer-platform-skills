# Hugging Face launch plan: T-2 days (today Oct 18, launch Oct 20)

I read the skill and its templates file. I had no answers on license, variants or training compute, so those parts are conditional. Labels: **[HF]** is what Hugging Face publishes, **[EU Commission]** is AI Act guidance, **[practitioner]** is reverse-engineered. Re-check the live pages for plan limits and policy wording before you commit.

## Fit verdict

Publish. You ship weights and a demo, so the Hub is the right home.

## Your two plan items

**1. Daily Papers on launch day: not possible.**
- Submission closes 14 days after the arXiv date. [HF]
- Sept 30 + 14 days = **Oct 14**. On Oct 20 you will be 20 days past the first version, so the window closed 4 days ago.
- A v2 does not reopen it. [practitioner]
- Don't plan the launch around a Daily Papers bump. Check the live Daily Papers page, since I can't verify here that the rule is unchanged.
- What still works: put the arXiv link in the card's citation section. That creates the `arxiv:` tag and ties the paper page to the model.
- Replace the bump with the levers that do move trending: send visitors straight to the model page, and make the Space and the card good on day one. [HF]

**2. `@spaces.GPU(duration=300)` everywhere: change it today.**
- "To be safe" is the wrong rule. The skill says to set duration to the real worst case.
- The platform refuses a run when the visitor's remaining daily quota is below the declared duration. [practitioner]
- Anonymous visitors get 2 min (120 s) a day, so at 300 s they can never run the demo. Free accounts get 5 min, which allows one run at most. [HF]
- Shorter declared durations also get queue priority. [HF]
- Generation takes about 20 s, so declare roughly 30–45 s. Measure the worst case on your longest allowed input, add margin for model load, and use that number.
- Set it per function. A longer duration only belongs on a function that really runs longer.

**Your Team plan is fine for this demo.** [HF]
- Gradio Spaces need Team or Enterprise for an org, and you have Team.
- Team allows 50 ZeroGPU Spaces.
- Team members get a 40 min/day visitor quota. Everyone else gets the lower quotas above, which is why the duration matters.

## Repo layout

I don't know your variants, so fill this in. The rules:

| Repo id | Variant | `base_model` | License | Gate |
|---|---|---|---|---|
| `<org>/<model>` | main | the parent model, or omit if trained from scratch | `<id>` | open (default) |
| `<org>/<model>-<size>` | each separately trained size | **do not** point to a sibling size | same | open |
| `<org>/<model>-GGUF` | quantization (if shipping) | `<org>/<model>`, `base_model_relation: quantized` | same as base | open |

- Group all variants in one collection. [HF]
- One repo per variant. A folder per variant has no URL and no download count. [HF]

## Last-48-hour actions, ranked by value per hour

**Today (Oct 18, T-2)**
1. **Fix the ZeroGPU durations** (see above).
2. **Start org verification if it isn't done.** It is manual and takes days to weeks, so it probably won't land by Oct 20. Don't block the launch on it, but start now. [practitioner]
3. **Check the org's joiners.** If you added an email domain, anyone with a matching address can join. Audit the members and set them to read. [HF]
4. **Complete the card metadata** while repos are still private:
   - `pipeline_tag`, `library_name` (explicit `transformers` if relevant), `license`, `base_model`, `datasets`, `language`.
   - Cite the arXiv link.
   - Use the YAML skeleton in the templates file.
5. **Weights must be safetensors.** Pickle-only `.bin` or `.pth` files trigger scan warnings and stop enterprise reviewers. [HF]
6. **Decide on `trust_remote_code`.** Keep it out of the main snippet unless the architecture needs it. If it does, say so in the card and the FAQ. [practitioner]
7. **Create the collection** and check that the org page shows it. [HF]

**Tomorrow (Oct 19, T-1)**
8. **Clean the git history before going public.** Flipping a repo public publishes all of it: old checkpoints, eval data, tokens, early card text. [HF]
   - The safest route is to recreate the repo.
   - If you squash `main` instead, also delete every PR ref, branch and tag that predates the squash. Squashed files survive in PR refs, and a squash can't be undone.
9. **Scan history for tokens yourself.** The Hub's push scan only emails verified secrets. [HF]
10. **Test the copy-run snippet in a clean environment.** It must run unedited, with no local paths, private packages or unpublished checkpoints.
11. **Make the Space live and linked.**
    - Put it under the **org**, not a personal account, or you lose the author-owned star on the model page. [HF]
    - List the repo under `models:` in the Space README.
    - Keep API keys in Space secrets.
    - Warm the Space the day before, because free CPU Spaces sleep after 48 h. [HF]
12. **Write and pin the Community tab FAQ** from the template. Name an owner for the first month.
13. **Decide the AI Act position** (below) and link the copyright policy and training-data summary from the card.

**Launch day (Oct 20, T-0)**
14. **Flip all repos public together.**
15. **Post the Hub link on your channels.** Link the Hub page, not your site, so traffic lands where trending is counted. [HF]
16. **Staff the Community tab daily.** Aim for a first staff reply in under one business day for the first month (a target you set yourself).

**Weeks 1–2:** answer every discussion and merge useful PRs such as eval results. Don't read a flat download curve in week one as failure. [HF]

## Do not do

- **Don't ask anyone to like the model in exchange for anything.** The Content Policy restricts "incentivizing manipulation of Hugging Face Hub metrics (e.g., exchanging rewards for likes)", and sanctions include unranking. [HF]
- **Don't ask the whole company to like it at 9am.** Rewards are banned outright. A spike of zero-history accounts also invites a moderation look. [practitioner] Drive real visitors instead.
- **Don't promise an inference widget.** It shows only if an Inference Provider chooses to serve the model. Fallbacks:
  - `widget:` output examples in the card
  - "Ask for provider support" on the model page
  - a linked Space
  - self-hosting [HF]
- **Don't gate the model for leads.** Grants are per individual user, and you take on handling their personal data. Use a "commercial license or hosted API" link in the card and the pinned FAQ instead. Gate only for a reason you can name, such as a custom license with a commercial threshold. [HF]

## Gate decision

Open, with the license in the card. That is the default for an adoption goal. If your license has a commercial threshold, use the click-through gate: automatic approval, with username and email collection off.

## EU AI Act

I can't call this without three inputs: training compute, output modality, and where you are incorporated.

- The indicative test: more than 10^23 FLOP of training compute **and** a model that can generate language (text or audio), text-to-image or text-to-video. [EU Commission]
- Embedding, reranking and classification models usually fall outside it. Speech recognition and text-to-speech models are inside the modality test. [EU Commission]
- A public Hub repo is downloadable in the EU, so having no EU customers doesn't take you out. [EU Commission]
- Every provider owes a copyright policy and a public training-data summary on the AI Office template. [EU Commission]
- The open-source exemption needs a free, open-source license with no monetisation. Revenue-gated or use-restricted licenses likely lose it. [EU Commission]
- Obligations apply since 2 Aug 2025, and the Commission enforces them, including fines, from **2 Aug 2026**. That date may already have passed for your launch. [EU Commission]
- Send the final call to counsel.

## Space plan

| Item | Plan |
|---|---|
| SDK / hardware | Gradio + ZeroGPU, org-owned |
| Plan check | Team covers Gradio and 50 ZeroGPU Spaces |
| `@spaces.GPU` | Measured worst case plus margin, about 30–45 s, set per function |
| README | `models:` lists `<org>/<model>`, plus `short_description` |
| After launch | Request a community GPU grant if the demo gets traction |

## Measurement plan

- Report likes, downloads and Space visits as three separate lines, each with its counting rule.
- A download is any GET or HEAD on `config.json` (the default query file). It is not deduplicated, so clones and CI cache misses count. [HF]
- Never add Hub downloads to PyPI or npm numbers, or model downloads to dataset downloads.
- Treat fine-tunes and quantizations in the model tree as the adoption signal after week 4. [HF]
- Publisher Analytics on Team gives daily non-deduplicated counts. [HF]

## Questions I need answered

1. What license are you using, and do you inherit a base model's license?
2. What are the variants: sizes, GGUF or other quantizations, a dataset?
3. What is the rough training compute, the output modality, and where are you incorporated?
4. Is the org already verified, and who holds admin?
5. Who owns the Community tab and the Space for the first month, and how many hours a week do they have?

The filled templates (card YAML, Space README header, pinned FAQ, provider-support request, launch Post) are in `references/templates.md`. I can fill them once I have your answers.