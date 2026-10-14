**Do this first (30 min):** Ask your manager which Tessera service has the most external-facing potential. Candidates are partner integrations, patient or provider data exchange, and anything FHIR-shaped. Then write down the one that could plausibly go public.

**Verdict: the path is real but not automatic. Don't confirm the recruiter's claim as stated.**

- Internal API work is a legitimate on-ramp. It gives you REST/gRPC design, auth, pagination, observability, and schema design.
- "Everyone she places came through it" is a claim about her placements. Selection bias applies, because she places people into the roles she fills.
- Internal-only work does not teach the hard part of public APIs. Your only consumers are your own mobile and web teams, so you can coordinate a breaking change in a Slack thread. External consumers can't be coordinated that way.
- Hiring managers for public API roles look for evidence of these skills:
  1. Versioning and backward compatibility.
  2. Deprecation with real timelines.
  3. Docs, SDKs, and a quickstart.
  4. Rate limits, quotas, and abuse handling.
  5. Auth for third parties (OAuth scopes, API keys).
- Without that evidence, "3 years of internal APIs" reads as a backend generalist.

**18 months is feasible. Treat it as a gap-closing plan, not a waiting game.**

Months 0–3: act as if your internal API had external consumers.
1. Treat the mobile app as an external client. Pin API versions and never break an old version silently.
2. Write a deprecation policy and run one deprecation end to end.
3. Add an OpenAPI spec as the source of truth. Generate docs and a client SDK from it.
4. Measure time-to-first-successful-call for a new internal dev. That is your DX metric.

Months 3–9: get near real external consumers.
1. Volunteer for any partner, vendor, or customer integration at Tessera. Healthcare companies usually have some.
2. Push for a pilot external API or sandbox. Propose it with a business case, not as a tech project.
3. If Tessera has no public API plan, learn that now. It decides whether you stay or leave.

Months 9–18: make the move.
1. Show shipped evidence: an OpenAPI spec, SDK, versioning policy, a migration you ran, and one writeup.
2. Target companies that already ship public APIs and hire for platform or API teams. Healthcare and fintech value your domain experience.
3. Keep a public artifact: an open-source API client, a design-review blog post, or a conference talk on versioning.

**Check the recruiter's claim in 1 hour.**
1. Pull 10 job posts for "API platform" or "developer platform" engineers.
2. List the required skills.
3. Count how many ask for public-API evidence versus internal API experience.

**Next, in under 2 minutes:** open Tessera's repo list and name the one service you would expose publicly first. Then send me the name, and I'll help draft the pitch to your manager.