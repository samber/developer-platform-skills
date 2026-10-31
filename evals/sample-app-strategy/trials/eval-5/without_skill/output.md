# Recommendation: build the reference app, but cut its scope. Do not build the 7 quickstarts or the gallery now.

## Why

1. **The stall is about the pattern, not the first call.** Enterprise buyers ask to see the whole onboarding-to-payout flow. A quickstart shows one API call in one language, so seven of them don't answer that question.
2. **The full "production-grade" app doesn't fit your capacity.** My unmeasured estimate for the full app is 300+ engineering hours. That covers KYC upload, card capture, payout scheduling, disputes, webhooks, auth, tests and docs. Omar has 50 hours a quarter, which is roughly 50–65 hours before the conference. The full app needs a second engineer, or a smaller scope.
3. **"Production-grade" is a liability when the app handles KYC documents and card data.** Customers will copy it. If it stores identity documents or lets card numbers touch the server, you have published unsafe patterns, and a conference audience will notice.
4. **The quickstarts cost more than they look.** Seven languages at roughly 10–15 hours each (my estimate) is about 70–100 hours. After that you carry seven things to keep in sync with every API change. A gallery of one app is an empty page.

## What to build (scope cuts)

**Name it a "reference implementation of the onboarding-to-payout pattern", not "production-grade".**

- **One language: Node.** It is tier 1 and the most common marketplace stack. I'm assuming that. Check it against your SDK download numbers.
- **The app never touches sensitive data.**
  - Card capture uses tokenized or hosted fields, so the app only handles tokens.
  - KYC documents go straight to the API or a hosted upload, and the app never stores files.
  - Both depend on your API offering these. I haven't verified that it does. If it doesn't, that is a product gap to raise now, and it changes the plan.
- **Four flows:**
  - Seller onboarding with KYC status driven by webhooks.
  - Card capture.
  - Payout scheduling.
  - Disputes as a webhook-driven state machine.
- **The "production" part is the patterns, not the polish:**
  - Idempotency keys.
  - Webhook signature verification.
  - Retries.
  - A state machine for every status change.
  - Error and failure paths shown on purpose.
- **Sandbox only.**
  - Use test cards and synthetic KYC documents.
  - Never use real documents, even for the demo.
  - Show failures such as a rejected KYC check or a disputed payout, because that is where trust is built.
- **Ship alongside it:** a one-page sequence diagram of the whole flow, and a short README. These are the cheapest and most reusable pieces.

## Plan and budget

| Weeks | Work | Owner and hours (estimate) |
|---|---|---|
| 1–2 | Sequence diagram, pattern doc, scripted sandbox walkthrough. Show them to 3 stalled-deal contacts. | Omar ~10h |
| 3–7 | Build the thin Node app. | Second engineer ~80–120h, Omar reviews and owns the design (~30h) |
| 8 | Freeze scope. Record a full demo video. | Omar ~10h |
| 9–10 | Rehearse and harden. Write the fallback plan. | Whoever demos |

**Checkpoint at the end of week 2.** If the 3 stalled-deal contacts say the diagram and walkthrough would unblock them, the app is justified. If they ask for something else, such as a security review or compliance answers, redirect the effort there.

**Demo risks to cover:**
- Sandbox downtime. Keep the recorded video as a fallback.
- Conference Wi-Fi.
- Anything that looks like real PII on screen.

## After the conference

- **Quickstarts:** do tier 1 (Python, Java) first, as a "first payout" path. Treat tier 2 (Go, Ruby, PHP, .NET) as on-demand, driven by inbound requests or a deal that needs it. Auto-generating snippets from the SDKs is cheaper than hand-written quickstarts.
- **Gallery:** build it only once you have three or more apps worth listing. Candidates are a second-language port of the reference app or a dispute-only example.

## What I don't know

- Whether the API supports hosted KYC upload and card tokenization (assumed).
- Whether anyone besides Omar can build this (assumed yes).
- How many deals stalled, and whether the blocker is engineering evaluators or security and compliance reviewers. If it is the latter, a reference app alone won't fix it. The week-2 check should settle this.
- Whether any quickstarts already exist.