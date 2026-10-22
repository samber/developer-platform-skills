**I can't give you six languages that will hold up in front of a board yet.** The skill I followed says the order depends on who integrates with Halcyon, and I don't know that. Here's what I can give you today.

## What I'd put on the slide now

Two things change the slide before any language does:

- **"Six official SDKs" is a bigger commitment than it looks.** Every official language is a standing maintenance cost. Plaid ships five official SDKs and points 40+ other languages at its OpenAPI spec. Stripe ships seven and Twilio seven, and both are far larger. With about 600 accounts, a smaller official core plus generated coverage is the more defensible plan.
- **Language order comes from your buyers' stacks, not from popularity rankings.** Fintech and enterprise platforms lead with Java, C#, Ruby, and Go. AI and dev-tools platforms lead with Python and TypeScript.

For a workflow-automation product sold to ops teams, I'd guess your integrators are mostly in-house engineers or integration partners. That points to **Python, TypeScript/Node, Java, C#/.NET, Go, and either Ruby or PHP** as a starting hypothesis. It is a guess from the category, not a finding about Halcyon. Label it "provisional" if it goes on a slide before you've checked.

## What to ask before Friday

These take about a day to answer and decide the real list:

1. **Do you have an OpenAPI spec, and is it accurate?** If it exists and is kept current in CI, you can generate SDKs. If it drifts, fix that first.
2. **What do you have today?** For example, existing SDKs (generated or handwritten) or community libraries.
3. **What does API traffic show by language?** Check client `User-Agent` strings or any SDK headers. If you have no telemetry, say so on the slide and plan to add it.
4. **Which languages have customers or sales deals asked for by name?** Ask Sales and Support. Repeated named requests are a strong signal.
5. **Which languages can your team actually maintain for years?** A language nobody on the team can review idiomatically becomes a liability.
6. **Is there a vendor or procurement constraint on hosted generators?** This decides the build model. Note that Stainless, a major SDK generator, was acquired by Anthropic in 2026 and its hosted generator was wound down. Keep the OpenAPI spec as your source of truth and write an exit plan.

## Suggested wording for the slide

> **SDK plan: official core now, expand on evidence**
> - Launch official SDKs in the 3–4 languages our customers use most, confirmed by traffic and deal data (shortlist: Python, TypeScript, Java, Go).
> - Publish the OpenAPI spec so any other language can self-generate a client.
> - Add a language when it reaches a sustained double-digit share of API traffic, or when repeated enterprise deals name it. (This threshold is our own rule, not an industry standard.)

If the CEO has already committed to six, the same logic works: pick six, then rank them by evidence and state which are launch-wave and which follow.

Answer questions 1–5 and I can turn this into a concrete ranked list with a build-vs-generate recommendation. Question 6 tightens the build-model section. The skill also walks through support tiers, versioning, and end-of-life policy, but none of that is needed for Friday.