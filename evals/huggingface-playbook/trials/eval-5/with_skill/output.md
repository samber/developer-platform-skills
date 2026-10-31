**There is no setting for this.** The Inference box on a model page isn't something you switch on for your own repo. Nobody at Kestrel can enable it for `kestrel-ai/kestrel-vision-2b`, so tell the CEO that now, before the webinar plan depends on it.

**Why [HF]**
- The widget appears only when an Inference Provider serves the model.
- Hugging Face says providers "autonomously choose" what they deploy.
- Big models have the box because providers picked them up, not because their owners flipped something.

I've read the playbook but can't see your live Hub page. Provider policies change, so re-check the model page before you commit to a date.

**What you can do before the 12th**

1. **Request provider support (about 5 minutes).** On the model page, use "Ask for provider support" and paste this:
   ```
   Requesting Inference Providers support for kestrel-ai/kestrel-vision-2b (<task>, 2B, <license>). Use case: <one line>. Weights in safetensors; chat template included. We can help with serving configs: <contact>.
   ```
   - This is a request, not a guarantee. Don't put "try it live on the Hub box" in the webinar plan.
   - It only has a chance if the weights are safetensors, the chat template is included, and the license is stated.

2. **Check the card metadata today.** The page has been up three weeks, so check these fields in the card YAML:
   - `pipeline_tag` (probably `image-text-to-text`; confirm which one fits)
   - `library_name` (models created after August 2024 need `library_name: transformers` set explicitly)
   - `license`
   - `base_model` (if the model is a fine-tune)
   - `datasets`
   - `language`

   Missing metadata hurts the widget, the code-snippet tab and search. It doesn't create the box on its own, but it is the cheapest fix. [HF]

3. **Add static examples.** The card's `widget:` YAML supports `output` examples. These are frozen example outputs, not a live inference box, but the page then shows something to try.

4. **Link a demo Space.** This is the usual substitute for a webinar. Check the org plan first [HF]:
   - Static Spaces (transformers.js or ONNX in the browser) are free for everyone.
   - Gradio and Docker Spaces need Team or Enterprise for an org.
   - A free personal account can host 2 ZeroGPU Gradio Spaces. That works, but a Space outside the org loses the author-owned star on the model page.
   - List `kestrel-ai/kestrel-vision-2b` under `models:` in the Space README so it appears on the model page.
   - Set `@spaces.GPU(duration=...)` to the real worst case. Above 120 s, anonymous visitors can never run it.
   - Keep API keys in Space secrets.

5. **For a guaranteed live demo, self-host it.** Use Inference Endpoints, TGI or vLLM. Always-on latency costs money, so budget it for the webinar.

**My recommendation:** do items 1, 2 and 3 today. For the webinar, build the Space (item 4) and treat a provider picking the model up as a bonus. If the demo must work live in front of the audience, add the self-hosted fallback (item 5).

**Questions that decide the Space route**
- Is the `kestrel-ai` org on the free plan, or on Team or Enterprise?
- Is the org verified? Verification is manual and takes days to weeks [practitioner], so start it now if it isn't.
- Who owns the Space and the Community tab until the 12th?

**For the CEO:** the Inference box is Hugging Face's decision, not ours. The page-side fixes, the support request and a linked demo Space are ours to do this week.