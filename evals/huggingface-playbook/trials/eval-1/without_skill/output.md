# Tallow-ASR launch checklist (launch day: Tue 2026-11-03)

## 0. Decisions to make now (3 of them change the plan)

1. ⚠️ **The like-raffle.** I recommend dropping it.
   - Hugging Face trending is driven by likes. Paying people to like (a raffle entry per like) is incentivized engagement. It can get the repo down-ranked or flagged, and a ranking built on it looks bad for a speech-model launch.
   - It is also a legal sweepstakes in most countries. You would need official rules, eligibility by country, a no-purchase clause, prize tax and reporting, and GDPR handling for winners' contact details. Rules differ by country, and the user-facing rules for France/EU are strict.
   - Better: raffle among people who *do something* with the model. Examples are a public Space or fine-tune built on Tallow-ASR, a WER report on their own audio, or an accepted bug fix. Likes then come on their own.
   - If you keep it anyway, have legal sign off on the rules before Tuesday and read the HF content policy first.
2. ⚠️ **One repo with subfolders.** I recommend splitting.
   - `from_pretrained("tallowmere/tallow-asr")` fails unless `config.json` is at the root. Users must pass `subfolder=`, and many tools (pipelines, GGUF loaders, the "Use this model" button, Inference Providers) ignore subfolders.
   - Download counts, model-card metadata (base model, quantization, size), and the file browser all become ambiguous.
   - Suggested layout:
     - `tallowmere/tallow-asr-tiny`, `-small`, `-medium`
     - `tallowmere/tallow-asr-GGUF`, with the quant type in each filename
     - one **Collection** `Tallow-ASR` grouping them all
   - Trade-off: likes split across 4 repos. If concentrated likes matter more to you, keep a single "hub" repo and decide that on purpose.
3. ⚠️ **`pytorch_model.bin` as the shipped weights.** Convert to **safetensors**.
   - `.bin` files are pickles. HF shows scan warnings, and security-minded users won't load them.
   - Keep the `.bin` only if you need it for reproducibility.
   - Check that the converted model gives identical outputs on a fixed audio set.

## 1. Free-plan constraints to check (Sat–Sun)

- [ ] Confirm the org is on the free plan, who the admins are, and that 2FA is on for all 25 members.
- [ ] Spaces on free hardware are CPU-basic only (2 vCPU, 16 GB). A medium ASR model on CPU will be slow, and a launch-day crowd will queue.
- [ ] ZeroGPU and GPU Spaces need a paid plan or billing. Decide: pay for a GPU Space for launch week, or serve **tiny/small (or the GGUF build)** on CPU.
- [ ] Add a billing method and a spending cap if you upgrade hardware.
- [ ] Free Spaces sleep after inactivity. Plan a warm-up request on Tuesday morning.
- [ ] Check the private-storage quota. Stage uploads as **private**, then flip to public at launch.
- [ ] Assign an org owner who can flip visibility on Tuesday and who is reachable.

## 2. Model repos (Sat–Mon)

For each size:

- [ ] `config.json`, `preprocessor_config.json`, tokenizer files and `generation_config.json` at the repo root.
- [ ] Weights in safetensors, with a clean file list (no checkpoints, optimizer states, or stray training files).
- [ ] README/model card with front-matter: `pipeline_tag: automatic-speech-recognition`, `library_name`, `license`, `language`, `base_model` if any, `model-index` eval results.
- [ ] Card body:
  - intended use and out-of-scope use
  - languages supported
  - training data summary, with licenses for any third-party data
  - known limits (accents, noise, long-form, hallucination on silence)
  - the 5-line quickstart, tested
- [ ] WER/CER on public benchmarks (LibriSpeech, Common Voice, FLEURS) with the exact eval script, plus latency/RTF per size on named hardware. Numbers must be reproducible.
- [ ] Consider submitting to the Open ASR Leaderboard.
- [ ] License is explicit, with a LICENSE file. Check it against training-data licenses.
- [ ] Remove anything private from files and git history (internal paths, hostnames, dataset names, API keys, W&B links). Scan with `trufflehog` or `gitleaks`.
- [ ] Fresh-machine test using only the public instructions, while the repo is still private (use a read token): `pip install transformers`, load, transcribe a sample.

## 3. GGUF build (Sat–Mon)

- [ ] State which runtime loads it (name and minimum version). GGUF for ASR is not standard across tools.
- [ ] List the quants you ship (e.g., F16, Q8_0, Q5_K_M, Q4_K_M) and the WER delta of each against F16.
- [ ] Publish SHA256 for each file.
- [ ] Test on macOS arm64, Linux x86_64 and Windows, CPU only. Record RTF.
- [ ] Put a copy-paste run command in the card.
- [ ] Add `base_model` and `quantized_by` metadata so the GGUF links back to the originals.

## 4. Gradio demo Space (Sun–Mon)

- [ ] Create `tallowmere/tallow-asr-demo`, with Space-level metadata and a short description.
- [ ] Inputs: microphone, upload, and 3 example clips (clean, noisy, accented) that you have rights to use.
- [ ] Model picker for tiny/small/medium, with the cost in speed stated.
- [ ] Cap audio length (e.g., 60 s) and file size, so one user can't stall the queue.
- [ ] Use `demo.queue(max_size=...)` and set concurrency limits. Show a clear "busy" message.
- [ ] Pin dependency versions in `requirements.txt`.
- [ ] Privacy: state that audio is not stored. Make sure the code does not log audio or transcripts. Add this to the Space README.
- [ ] Load-test locally with ~50 concurrent requests. Record the failure mode.
- [ ] Keep a fallback ready: the same model on a laptop via the GGUF build, or a recorded demo video.
- [ ] Link the Space from every model card, and link the model cards from the Space.

## 5. Launch assets (Mon)

- [ ] Launch post covering what it is, the numbers, the sizes, license, and how to try it in 30 seconds.
- [ ] 60–90 s demo video or GIF with captions.
- [ ] Code repo on GitHub (training/eval/inference scripts) if applicable, with a README that matches the model cards.
- [ ] Short copy for each channel:
  - X/LinkedIn thread
  - r/LocalLLaMA and r/MachineLearning (follow each sub's self-promo rules)
  - a Show HN post, where the title says what the thing is and how it differs
  - your Discord/newsletter
- [ ] Ask 5–10 friendly people (not employees) to try it on Monday and give real feedback. Don't ask them to like or upvote. Both HN and Reddit penalize voting rings.
- [ ] Note the news calendar: Tue 2026-11-03 is US Election Day, so social feeds will be noisy. Consider launching Wed or Thu if the date isn't fixed by something else.
- [ ] Write the FAQ and "known issues" list now, so replies on Tuesday are fast.

## 6. Launch day (Tue, in order)

1. [ ] 08:00 Final smoke test of all repos (still private) and the Space.
2. [ ] Flip the 4 repos to **public**, then the Collection and the Space.
3. [ ] Open each public URL in a logged-out browser and confirm the model card renders, files download, and the widget or Space works.
4. [ ] Run the quickstart one more time from a clean environment against the *public* repos.
5. [ ] Publish the blog post, then the social posts and Show HN, staggered through the day.
6. [ ] Staff a rota: one person on HF Discussions/GitHub issues, one on social, one on Space health (queue length, errors, hardware).
7. [ ] Keep a running list of bugs and questions. Reply within hours, not days.

## 7. Launch week (Wed–Mon)

- [ ] Daily: check Space logs, queue times, and Hub discussions.
- [ ] Fix model-card or quickstart errors the same day. Pin the answer to repeated questions in a Discussion.
- [ ] Track downloads, likes, Space visits, GitHub stars, and first third-party Spaces/fine-tunes. Note which channel drove which.
- [ ] Reshare community builds. This does more for trending than anything you can ask for.
- [ ] If you run a raffle, make it merit-based (see §0), announce rules up front, pick winners with a logged random draw, and contact them privately.
- [ ] Monday retro: what broke, what to fix, what to write next (benchmarks deep-dive, fine-tuning guide, a streaming demo).

## Things that go wrong most often

- The model card quickstart doesn't run on a clean machine.
- The Space dies at 20 concurrent users on CPU-basic.
- The GGUF needs a runtime version nobody has.
- Training-data licenses conflict with the license you chose.
- Internal paths, dataset names, or tokens in the config or git history.
- Likes-for-prizes gets flagged and the story becomes the raffle, not the model.

If you tell me which of the three §0 decisions you pick, I can turn this into the day-by-day owner assignment for your 25 people, or draft the model card and Space README.