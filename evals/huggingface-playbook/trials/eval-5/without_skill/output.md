**There's no toggle for this.** The old "enable Inference API" switch no longer exists. The page box is now driven by Inference Providers, third parties like Together, Fireworks and Novita that serve models on the Hub. The box only appears if a provider serves your model. A three-week-old 2B vision model almost certainly has no provider yet. I haven't checked the live page, so this comes from how the Hub works, not from your repo.

## What you can check today (about 10 minutes)

1. Open the model's **Files → README.md → Edit** (the YAML block at the top).
2. Confirm `pipeline_tag` is set, for example `image-text-to-text` or `image-classification`. Without it, no widget can render.
3. Confirm there is no `inference: false` line. If there is one, that is what is hiding the box.
4. Set `library_name` (for example `transformers`) so the Hub can detect the architecture.
5. Make sure the repo is public and not gated or private. Widgets don't work on those.

Even with all of that correct, the box stays absent until a provider picks the model up. Providers choose models mostly by demand and architecture support. You can ask providers directly, or ask the HF team through your org contact if you have one.

## What will work before the 12th

Don't count on the serverless box. Use one of these instead:

- **Gradio demo in a Space (best for a webinar).** Create a Space with your demo, ideally on ZeroGPU or a small GPU. Link it from the model by adding `models: [kestrel-ai/kestrel-vision-2b]` to the Space's README metadata. The model page then shows it under "Spaces using this model". You control the experience and the uptime.
- **Dedicated Inference Endpoint.** On the model page, go to **Deploy → Inference Endpoints (dedicated)**. This is paid, per hour of GPU. It gives you a real API you can call live. It's not a free box on the page.
- **Pin the Space link in the model card** with a "Try it" badge or link at the top of the README.

## What to tell the CEO

"The one-click Inference API is gone. The page box depends on third-party providers hosting the model, which we don't control. We'll ship a Space demo linked from the model page before the 12th, and approach providers in parallel."

Start with the Space. It can be live in an afternoon, and it's the only option fully in your hands.