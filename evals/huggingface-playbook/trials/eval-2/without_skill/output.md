# Setting up the HF gate for the Brightwell Data embedding model

**Recommendation:** don't ship manual approval with phone and team size. Release the model ungated and capture leads some other way. If the VP insists on a gate, use the light auto-approve version in section 3. You have two weeks, so do the first three items in section 4 first.

## 1. Why the plan as written will backfire

| Problem | Effect |
|---|---|
| Apache-2.0 allows anyone to redistribute | Someone re-uploads an ungated mirror within days. You keep the friction, and the mirror gets the downloads, the likes and the community. |
| Manual approval adds latency | A new embedding model gets attention in the first 72 hours. Users who wait a day for an SDR will use a competitor's model. |
| Tooling breaks on gated repos | `sentence-transformers`, TEI, vLLM, Docker builds and CI all need an `HF_TOKEN`. Many projects and benchmark harnesses won't add your model. |
| Rejecting students | Students and hobbyists write the tutorials, benchmarks and blog posts that drive adoption. They are your unpaid marketing. |
| Phone and team size | These fields have the highest drop-off. Phone is also the riskiest personal data to collect under GDPR. People will enter fake values and the lead data will be worse for it. |
| "Every download is a lead" | Downloads are not people. CI pulls, mirrors and repeat downloads inflate the count, so the SDR queue fills with noise. |
| A gate on an open license is a mixed signal | The community reads "Apache-2.0 plus a form" as bait. |

Open models also see far more production use than the download counts suggest. The leads you want are the ones who need support, SLAs, hosting or fine-tuning. They will identify themselves if you give them a reason.

## 2. Recommended setup: ungated model, pull-based lead capture

1. **Keep the model repo public and ungated.** This maximizes downloads, integrations and leaderboard presence.
2. **Add an opt-in call to action at the top of the model card.** Example: "Running this in production? Get the fine-tuning guide, eval suite and support options" with a link to a short form (email and use case only).
3. **Gate something valuable but separate**, such as a `brightwell-data/<model>-enterprise-pack` repo. It could hold:
   - fine-tuning recipes
   - domain eval sets
   - a larger or quantized variant
   - an ONNX/TensorRT build

   That gate can be manual with a richer form, because the people who ask for it have already shown buying intent.
4. **Offer a hosted API or playground** (free tier, key on signup). Signups there are real, consented and tied to usage.
5. **Add a community entry point** (Discord or newsletter) in the card and README. Leads from there are consented and warm.
6. **Track intent signals.** Watch for companies that star the repo, open issues, or sign up for the API or the pack. Score those signals instead of scoring downloads.

## 3. If the VP still wants a gate on the main model

Use auto-approval with minimal fields. In the model card YAML:

```yaml
---
license: apache-2.0
extra_gated_prompt: >-
  This model is Apache-2.0 and free for any use, including commercial.
  We ask for a few details so we can send release updates and
  understand who uses it. Your Hugging Face email is shared with
  Brightwell Data. See our privacy notice: <URL>.
extra_gated_fields:
  Company or organization: text
  I am using this model for:
    type: select
    options:
      - Personal / learning
      - Research / academic
      - Company project (prototype)
      - Company project (production)
  I agree to receive release updates from Brightwell Data (optional): checkbox
---
```

Then set access to auto-approve in the repo settings (gating mode "auto"). Rules:

- **Auto-approve everyone.** Never reject students. Segment them instead: the "Personal / learning" and "Research" answers route to a nurture list, and the SDRs only see "Company project (production)".
- **Drop phone and team size.** Enrich company size from the company name or email domain with a tool like Clearbit, Apollo or Attio.
- **Keep every field except the use-case dropdown optional**, or the drop-off will hit you.
- **Don't make marketing consent a condition of access.** Keep consent optional and separate. This is a legal point to check with whoever owns GDPR at Brightwell, because the lawful basis for the stored data depends on it.
- **Put the privacy notice and the retention period in the form.**
- **Set an SLA of minutes, not days.** Auto mode removes the queue, and any future manual path needs one.

## 4. Two-week plan

1. **Today (10 minutes):** ask the VP what a lead is. Is it an email, a company, or a production use case? This definition decides the whole design.
2. **Days 1-3:** get legal and privacy to review the form text, the data retention policy and the lawful basis. Decide ungated (section 2) or light gate (section 3).
3. **Days 3-7:** build the CTA, the landing page, and the enterprise-pack repo, if you chose section 2. Set up the enrichment and CRM routing.
4. **Days 7-10:** test the gate on a private test repo with a throwaway HF account, covering the real flow end to end. Check that `HF_TOKEN` works in a clean Docker build and that `sentence-transformers` loads the model.
5. **Days 10-14:** write the release post, push to MTEB or the leaderboards you care about, and prepare the SDR playbook.
6. **Release day:** monitor signups and traffic every few hours for the first 72 hours. If signups or downloads collapse because of the gate, you can switch the repo to ungated in settings.

## 5. What to tell the VP

- Gated-and-manual caps adoption and moves it to mirrors.
- Collecting less data converts better, and the data is more accurate.
- You get higher-quality leads by gating a separate high-value asset and by offering the API, because those people have already chosen to talk to you.
- A light auto-gate is the fallback if they need a hard number of captured emails at launch.

## 6. Open questions for you

- Is Brightwell primarily selling hosted inference, support, or something else? The CTA and the enterprise pack depend on it.
- Does the model already have mirrors or a pre-announcement audience? If it does, a gate will hurt more.
- Who owns GDPR sign-off for the form?
- Is there a launch KPI beyond leads, such as MTEB placement or integration count?