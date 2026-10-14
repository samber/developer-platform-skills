# Verdict: path not confirmed

I can't confirm the recruiter's claim. It is a plausible route, but it isn't an established one.

- **No sourced case.** The skill that covers this field found no practitioner account of "internal APIs, then public API platform team." It calls the route a hypothesis.
- **What the evidence shows.** The bar for this work is API-design judgment, a checkable portfolio, and (at some employers) open-source history. It isn't "came through internal API work."
- **The recruiter's "everyone she places" claim.** That is one recruiter's placement pipeline, so it's a selection effect. It doesn't describe the field.
- **Why internal API work is only a partial fit.** Your consumers are your own mobile and web teams. You have no external SLA, no public docs, no formal deprecation notice, and no consumers you can't walk over and talk to. Public API work is judged on exactly those things. Brandur Leach (Stripe, later OpenAI) makes the point that API change gets expensive once even one outside user depends on you.
- **Term check.** Your role is not "platform engineering" in the Kubernetes/Backstage/golden-path sense, which is a different field. You build service APIs, so you're a backend engineer with API-design experience. That's a fine base for this track.

# The 18-month goal

Three years of service APIs is a real base. Whether it gets you onto a public-API team depends on the company type you target, and that matters more than the route:

| Target | Fit for you | Reality |
|---|---|---|
| **Infra/API-first** (Stripe, Twilio-style) | Hardest | Staff-level postings ask for 12+ years and 5+ leading API-design teams. Stripe's posting does welcome people new to infra, but with API-design leadership evidence. Possible at a lower level, and competitive. |
| **Bolt-on public API** on an existing product | Best odds | API work is folded into general backend hiring, so your background fits directly. Expect breadth, and check that the title and level match the real scope. |
| **Enterprise partner/ISV ecosystem** (GitLab-style) | Good for a Partner/Integration Engineer track | GitLab's associate level asks for a bachelor's or equivalent, Ruby/Rails or Go, and an open-source contribution history. |

My recommendation is to target the **Platform Engineer (backend, API-design-weighted)** track at a **bolt-on public API** company. Keep partner-ecosystem enterprises as the second option. Postman found 84% of API teams have 1–9 people, so most seats are generalist ones where your background counts.

I assumed this track and archetype because you didn't say. Correct me if you want API PM instead.

# What to do next

1. **Close the gap inside Tessera.** This is the fastest test of the hypothesis.
   - Ask whether any internal API could be exposed to a partner or customer, or whether a public API is on the roadmap.
   - If so, volunteer for it.
   - If not, treat your current work as practice and run the rest of this plan alongside it.
2. **Build the portfolio that counts, within 2–4 months.**
   - Write 2–3 API design docs or RFCs, with confidential detail removed. Cover versioning, error model, pagination, idempotency, and a deprecation plan.
   - Hold them to a published guideline: Google's AIPs, Microsoft's REST API Guidelines, or Zalando's.
   - Treat the deprecation plan as the main signal, since that's the part internal work rarely exercises.
3. **Add open-source history if you target GitLab-style roles.** Pick one project in the ecosystem you want to be credible in (REST, GraphQL, gRPC, webhooks, or a vendor SDK) and make small, real contributions.
4. **Prepare for the right interview.** Meta, for example, runs API design as a separate round from system design. A typical prompt is "design a payments API" where the users are developers. Judge your answers on clarity and misuse-resistance, not scale.
5. **Learn what you can't see from internal work.** Public docs, SDK ergonomics, rate limits, SLAs, and breaking-change cost are the parts internal work rarely exercises. Reading a few mature public APIs critically is a cheap way to start.
6. **Skip certifications as a gate.** apiMasters is informational at best, and nothing shows employers weight it.
7. **Push the recruiter.** Ask for three specific companies, the exact titles, and whether each has a dedicated platform team or folds the API into backend. Also ask how many of her placements came from purely internal-consumer backgrounds. Her answers are the evidence you currently lack.
8. **Benchmark any offer against the general engineering ladder.** Platform pay rides the general engineering or PM ladder, so compare it to general backend bands at the same level, not to a "platform engineer" title search. I have no dated figure to give you. Pull a live one with its source and date before negotiating.
9. **Check the archetype before accepting an offer.** Ask whether there is a dedicated platform org, an API line item inside general backend, or a partner-ecosystem function. A specialist-sized offer for a generalist seat is the main risk.

# Questions that would sharpen this plan

1. Is a public API plausible at Tessera in the next 18 months?
2. How many hours a week can you give to the portfolio?
3. Which protocol or ecosystem do you want to be credible in?
4. Are you after the fastest next role, or a position that builds API judgment over several employers?
5. Do you have any design docs or open-source work you could make public?

Your answers to 2 and 5 mostly decide whether the 18-month target is realistic.