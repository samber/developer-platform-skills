# Where to start: Larkspur Freight partner API

**Next action (30 min, this week):** book a meeting with your CRO and the head of engineering. Get one name for "who can approve a breaking change once it is public." That is a people problem, and it needs no spec. Every later step depends on it.

I followed the `developer-platform-kickoff` skill (SKILL.md and `references/skill-routing.md`). This is a cold start. I ran no interview, so any item marked "assumed" below is open for you to correct.

## Detection

- **Your repo is not on this machine.** I could not read it. I used what you told me: a README and a CHANGELOG only, no spec, no docs site, nothing public.
- **No `developer-platform-context.md` exists.** That means a cold start.
- **Nothing is published.** There is no compatibility promise to inherit.

## Route

**`api-integration-surface-strategy`** is the one skill for the immediate task.

- Nothing is public, and nobody has decided which surface to build.
- "An API for partners" is a surface question with no audience attached. The skill's boundary rules treat that as the strategy question in disguise.
- Expect half a day to a full day. This is my estimate, not a figure from the skill.

Two things to settle in that session:

1. **Who are the "partners"?** The skill's Q1 offers customers' own engineers, technology partners, an open third-party ecosystem, AI agents, or a mix. The answer decides what the short-list contains.
2. **What problem does the CRO's "API" solve?** Your pain is two engineers on bespoke CSV drops, which is a cost problem. The CRO's ask may be a revenue or partner problem. One API may not fix both. A bulk export or push surface could remove the CSV work without a "partner API" at all.

## Short-list

The list is ordered by value per unit of effort. You asked for the first moves, so only the first four are runnable now.

1. **`api-integration-surface-strategy`** (the route).
   - It attacks the fact that nobody has decided which surface exists, for whom, or in what order.
   - It costs one decision session with product, engineering and the CRO. It ships no code.
2. **`api-versioning-policy`**.
   - It attacks the missing breaking-change definition and signer. Everything you build later ships into a surface nobody owns.
   - It costs a policy session plus sign-off from engineering, product and probably legal.
   - It is a co-lead with #1, not a follower. Run #1 first, because the version scheme depends on the paradigm chosen.
   - Start the signer conversation in parallel, as in the next-action step above.
3. **`api-error-design`**.
   - It attacks the integrator support tickets you would otherwise open on day one.
   - It costs one design session, then an additive backend change per endpoint class.
   - Run it once the first surface is picked. It is cheap to do before launch and expensive to retrofit.
4. **`api-auth-key-management`**.
   - Partners need an identity before you can meter or attribute anything.
   - It costs a design session plus a credential store and a rotation path.
   - If Q1 turns out to be an open ecosystem acting on your users' data, `oauth2-provider-design` replaces it.

`api-rate-limit-policy` (#5) and `webhook-platform-design` (#6) follow only if the surface decision calls for them.

Two skills were re-ranked on your answers:

- **"Nothing public yet" moved macro strategy to rung 1 and deleted the surface-audit class.** The audit class is `public-api-design-review` and `api-reference-quality`. There is no surface to audit, and the audit-first default would have been the wrong opening.
- **"Nobody signs off on breaking changes" moved `api-versioning-policy` to rung 1 as well.** The skill says to do this whatever the session wanted.

## Chain

Dependency order:

1. `api-integration-surface-strategy` hands over the chosen surface and audience.
2. The chosen surface's own skill designs it.
3. `api-versioning-policy` defines what you will and won't break in it.

Publishing before step 3 means negotiating every later change case by case.

## Not now

- **`public-api-design-review`**: after the first draft spec is committed. It then becomes the pre-release gate.
- **`api-reference-quality`**: after a spec exists to audit against.
- **`bulk-data-sharing-design`**: only if the surface strategy picks bulk export as the CSV replacement.
- **`integration-partnership-strategy`**: once Q1 resolves to technology partners and you can rank them from demand data, such as your CSV-drop inventory.
- **`developer-portal-design`, `api-test-mode-design`**: once a first surface is chosen and an external beta is planned.
- **`integration-error-observability`**: after the first partner is live and someone owns the follow-up.
- **`sdk-portfolio-strategy`**: once the API surface is stable enough to wrap.

Not mentioned, because they are off the table: the marketplace skills, the GraphQL/gRPC/SQL/MCP surface skills, and ETL connectors. Nothing says you need them.

## Gap

None for this task. The DevRel work (docs site structure, quickstart, tutorials) is not covered here. Install `samber/developer-relations-skills` when you reach it, starting at `developer-relations-kickoff`.

## Routines (dry-run, nothing installed)

1. **Pre-release design review**: runs `public-api-design-review` on each spec diff. It stays dormant until the first spec is committed. Output goes as a comment on the spec PR.
2. **Quarterly kickoff re-run**: re-runs this kickoff and patches the context file. Anchor it to the start of each planning cycle. Output goes to the context file's session log and a short summary in your platform channel.

I proposed no deprecation sweep, fleet-health review or listing cycle. None of their triggers exist yet.

## Open questions

These would re-rank the list.

- **Q1: exact audience.**
  - Customers' own engineers: delete the ecosystem skills and move key management up.
  - Technology partners: move `integration-partnership-strategy` and error observability up.
  - AI agents: move `mcp-server-offering` up.
- **Q5: a landing date.** If your planning cycle has a hard date within a quarter, demote macro strategy to "not now". Only do that deliberately, because it removes the foundation.
- **Q5/Q6: capacity.** "Two engineers already consumed" suggests limited platform-engineering capacity. If it is confirmed, the build-heavy skills drop out and the session stays on policy and design.
- **Q6: one-off or standing.** "Hours only" cuts the list to a minimum. "Headcount and sign-off available" lifts macro strategy further.

## Context artifact (draft)

I did not write this to disk, because your repo isn't in this workspace. Putting it in the wrong repo would pollute it. Save it as `developer-platform-context.md` at your repo root. I skipped persistent memory because the skill derives it from this file. It also needs a diff and your approval before anything is committed.

```markdown
# Developer platform context

## Audience and buyer
- Assumed: technology partners / customer integrators (OPEN: confirm Q1)
- Buyer: CRO (sponsor)

## Published surfaces
- None. Bespoke per-customer CSV drops (private, not a public surface).

## Spec locations
- None.

## Ownership
- Contract owner: unassigned
- Breaking-change signer: unassigned (OPEN, top priority)

## In-flight work
- (2026-10-08) Choosing the first surface for "API for partners".

## Decided vs open
- Decided: CRO wants a partner API next planning cycle.
- Open: audience, surface, versioning owner, landing date, effort ceiling.

## Constraints
- Landing date: next planning cycle (exact date OPEN)
- Horizon: OPEN (one-off vs standing)
- Effort ceiling: OPEN (two engineers currently absorbed by CSV drops)

## Stakeholders
- CRO: sponsor
- Platform PM: owner of this process
- Engineering lead: TBD, likely contract owner
- Signer for breaking changes: TBD

## Session log
- 2026-10-08: cold start. Routed to api-integration-surface-strategy. Versioning policy co-lead. Interview not run; assumptions marked OPEN.
```

## Pass bar

- **Routing and the ordered short-list:** done.
- **Routines:** shown as dry-runs, each with an output channel.
- **Interview:** not run. I had no interactive question tool, so I derived answers from your message and listed the rest as open questions instead of inventing them.
- **Artifact:** drafted above but not written to your repo. It needs you to save it.