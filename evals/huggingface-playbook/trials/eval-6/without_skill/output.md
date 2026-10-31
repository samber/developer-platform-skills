**Date check:** you said today is Oct 18, but my system clock says Oct 31. If the clock is right, your launch has already passed, so tell me and I'll rework this. The rest assumes your dates.

## 1. Daily Papers: submit now, not on launch day

- **Age risk.** On Oct 20 your paper will be 20 days old on arXiv. I can't confirm Daily Papers' current age rules from memory, so don't wait to find out on launch day. Open `huggingface.co/papers/submit` today, enter the arXiv ID, and see whether it accepts the paper.
- **If it's accepted, submit it now.** Submitting now costs you little. The listing date is the day you submit, so a launch-day submission is the only way to get the bump on the day.
- **If it's rejected as too old,** the paper page still works. The launch bump then comes from the paper page being linked to the model, not from a Daily Papers listing.
- **Claim authorship** on the paper page (`huggingface.co/papers/<arxiv-id>`) so the authors are verified.
- **Link the paper to the model.** Put the arXiv URL (`https://arxiv.org/abs/<id>`) in the model card. That adds the `arxiv:<id>` tag, and the model then appears on the paper page. Do the same in the Space README and any dataset cards.
- **Ask co-authors to upvote** and share the link on launch day. Don't organize upvote rings.

## 2. ZeroGPU: `duration=300` everywhere is a mistake

**Why:**
- The `duration` you set is the budget a call asks for. The GPU time actually used is what gets billed to quota, but the requested value still hurts you.
- A long `duration` lowers your queue priority. ZeroGPU docs say shorter durations queue faster.
- A visitor whose remaining daily quota is below the requested duration can be refused outright. Logged-out and free visitors have small quotas, so on launch day many of them will hit "quota exceeded" on a 20-second job.

**What to do:**
- Set `duration` to about 2–3× the real runtime. For ~20 s generation, use `@spaces.GPU(duration=60)`.
- If runtime varies with input, such as image size or token count, pass a function that computes the duration from the arguments instead of a constant.
- Time the worst-case input on the Space and set the value from that. Don't use 300.
- Your Team plan covers hosting ZeroGPU Spaces and gives members higher quota. It doesn't change what anonymous visitors get, so test as a logged-out visitor.

## 3. Other things for the next 48 hours

**Model repo**
1. Do a clean-environment load test. In a fresh venv, run exactly the snippet from your model card, with no cached or local files.
2. Check the metadata: `license`, `pipeline_tag`, `library_name`, `base_model`, `language`, plus eval results in `model-index` if you have them.
3. Make sure the model card has a short quickstart, intended use, limitations, and a BibTeX block for the paper.
4. Keep repos private until launch, then flip public. Check that the Space doesn't need the private model while the Space is public, or that the flip order is right.
5. Check that file sizes and formats are what you intend (safetensors, no stray checkpoints). If you have quantized or GGUF variants, upload them before launch.

**Space**
1. Pin dependency versions in `requirements.txt` and the Gradio/SDK version in the README.
2. Load the model at module scope, outside the `@spaces.GPU` function, so cold starts don't eat the GPU budget.
3. Set a queue limit (`max_size`) and concurrency so launch traffic degrades gracefully.
4. Add examples that finish in under 20 s so first-time visitors get a result fast.
5. Rehearse as a logged-out user and as a free logged-in user. Watch the quota messages.

**Launch day**
1. Create a Collection for the paper, model(s), Space, and dataset.
2. Link the Space from the model card and the model from the Space.
3. Turn on discussions and notifications for the org. Assign someone to answer the first-day issues.
4. Prepare the announcement post with one link, the paper page, which collects the model and Space.
5. Decide who flips visibility, and when, so the model, Space, and paper link all go live together.

If you tell me the model's task and size, I can write the exact `@spaces.GPU` setup and a model-card skeleton.