# Nimbus Telemetry developer portal: where we stand

**Verdict: Level 1 of 5, "Ad hoc".** The portal has the right pieces but no owner, no change communication, and no operational transparency. Reaching Level 2 ("Owned") takes one accountable owner at about 1 FTE, plus roughly 6 to 8 weeks of focused work. It doesn't need a team.

**Basis:** I scored this from your description only. I haven't seen the portal, its analytics, or its support inbox. The 5-level scale is my own framing, not a published standard. The weakest points below are worth checking against the real portal before the VP sees the score.

## Scorecard

Each dimension is scored 0 to 5. The overall level is set by the weakest dimension, because developers hit the gaps, not the averages.

| Dimension | Score | Evidence from your description |
|---|---|---|
| Reference (OpenAPI) | 2 | It exists, which is the hardest part. Accuracy depends on "an engineer happens to notice." |
| Onboarding (getting-started, key dashboard) | 2 | Both exist. Nobody verifies that a new developer can reach a first successful call. |
| Change communication (changelog) | 0 | None. Developers can't tell what changed, what broke, or what was deprecated. |
| Operational transparency (status page) | 0 | None. During an incident, developers can't tell whether the fault is theirs or ours. |
| Support and feedback loop | 1 | An email address only. There is no triage owner, no response target, and no way to turn tickets into doc fixes. |
| Ownership and governance | 0 | Nobody owns it. This is the root cause of the other gaps. |
| Measurement | 0 | Nothing in your description suggests tracking of time-to-first-call, search, 404s, or ticket themes. |

**Overall: Level 1.** The strongest dimensions score 2 and the weakest score 0.

## What each level means

1. **Ad hoc (today).** Assets exist and get fixed by chance.
2. **Owned.** A named owner, a basic update process, and a changelog and status page that exist and are used.
3. **Reliable.** Docs ship with the code. Reference is generated from the spec and checked in CI. Support themes feed doc fixes. Basic metrics are reviewed monthly.
4. **Managed.** Funnels are measured, such as signup to first call. SDKs, samples, and migration guides exist. Content is audited quarterly.
5. **Strategic.** The portal is a product with a roadmap, community channels, and feedback that drives API design.

## What it takes to reach Level 2

The first four items are the minimum for Level 2. The rest make the first four stick.

1. **Name one owner (week 0).**
   - Give them the portal's quality as a goal. This is the actual headcount ask.
   - A technical writer or developer-experience engineer fits best. A part-time engineer will repeat today's pattern.
2. **Launch a changelog (weeks 1 to 2).**
   - Backfill 3 to 6 months of notable changes.
   - Add a rule that every API-affecting PR needs a changelog entry.
   - Add a deprecation-notice format with dates.
3. **Launch a status page (weeks 1 to 2).**
   - Use a hosted service. It takes days, not weeks.
   - Wire it to existing monitoring and agree who posts incident updates.
4. **Fix the support email (weeks 1 to 2).**
   - Set a response target, such as one business day.
   - Name an owner for the inbox.
   - Tag every ticket by cause: docs gap, bug, or confusion.
5. **Audit the existing content (weeks 2 to 4).**
   - Run the getting-started guide cold, as a new developer. Time it and record where it breaks.
   - Diff the OpenAPI spec against real API behavior on the top 10 to 20 endpoints.
   - Fix what's broken and list what's missing.
6. **Add a "last reviewed" date and an issue link to every page (weeks 3 to 4).** This makes staleness visible and gives readers a reporting path.
7. **Set up a lightweight update process (weeks 4 to 6).**
   - Make a docs check part of the API-change review checklist.
   - Keep the docs in a repo with owners assigned per area.
8. **Start measuring (weeks 4 to 8).**
   - Track time-to-first-call, top search queries, top 404s, and ticket themes.
   - Review them monthly with the VP.

### Done criteria for Level 2

- A named owner, with portal quality in their goals.
- A changelog with entries for the last two releases.
- A status page that has been used for at least one real or test incident.
- The inbox has an owner, a response target, and tagged tickets.
- A new developer completes getting-started within a known, documented time.
- Every page shows a review date.

## Headcount

**Ask for one hire, or one reassigned person, at 1 FTE.** The Level 2 work is small but constant, and it fails when it's a side task. That's your current state.

- Part-time engineers can't hold this. The pattern from the last three years is that the work only happens when somebody notices.
- A team of two or more isn't justified until Level 3. By then the metrics from step 8 will show whether the portal drives signups and cuts support load.
- One decision for the VP: if the owner is an engineer, protect their time explicitly. If they're a writer, make sure they have engineering access to review API changes.

## Risks and unknowns

- **Unverified accuracy.** The OpenAPI reference may be more or less stale than assumed. The step 5 audit settles this in a week.
- **Unknown demand.** Without current metrics, I can't say how many developers hit the gaps. The support inbox is the quickest proxy: read the last 100 emails and tag them.
- **Tooling.** If the spec is hand-written rather than generated from code, drift will continue until Level 3 work (generation and CI checks) is done.

## Suggested ask to the VP

Approve 1 FTE owner for the portal. Target Level 2 in about 8 weeks, with the changelog and status page live in the first 2. Review the metrics at 90 days and decide then whether Level 3 needs more headcount.