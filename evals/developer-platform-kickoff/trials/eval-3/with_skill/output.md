**Next action (10 min):** pull two numbers from your CRM and support tool. First, deals lost or stalled over a missing integration in the last 12 months. Second, requests for integrations you don't have. Don't write the rulebook before you have them.

## Route

**Run `samber/developer-platform-skills@connector-marketplace-strategy` first.** Your task is the wrong altitude for the screenshot and rejection rules.

- You asked for the submission rulebook and a 15% cut. The 15% is a take-rate decision, and a take-rate set before demand evidence exists is the case this skill is built to catch.
- The skill gate is build, join, or buy. "Build" needs four triggers, each with cited evidence:
  1. Customer pull for integrations.
  2. Third parties asking to build on you.
  3. Procurement friction from one-off integration requests.
  4. Capacity to staff the full partner lifecycle.
- Your current evidence:
  - **Customer pull:** not stated.
  - **Supply:** two unprompted partner asks is a real but thin signal. Nine of eleven integrations are self-built, which is first-party seeding, not partner supply.
  - **Procurement friction:** not stated.
  - **Staffing:** not stated.
- The CEO announcement and June date are decided and off the table. The form the announcement takes is still open. The skill's fallback for a failed gate is a curated partner catalog, which you can still unveil at the June conference.
- That skill's default is zero take while seeding. Its default curation level is hybrid: open admission with a minimal automated bar, plus a separate certified tier.
- A flat 15% is the mature-marketplace rate. Salesforce AppExchange charges it, and earns it because 91% of its customers use at least one marketplace app. With two inbound asks you don't have that distribution yet.
- The usual fix is a volume tier. Shopify charges 0% on the first $1M a year, then 15%. Treat this as the skill's default, not a verdict. It depends on your answers to the questions below.

## Where your three asks land

- **Screenshots and rejection reasons:** `app-marketplace-listing-standards` covers listing content and objective reject criteria.
- **Security and permission rejections:** `app-marketplace-review`.
- **The 15% level:** `connector-marketplace-strategy`. The collection mechanics, meaning billing, payouts and VAT, are in `app-marketplace-monetization-model`.

## Short-list

Ordered by value per unit of effort.

1. **`connector-marketplace-strategy`**
   - **Attacks:** an unevidenced build decision and an unjustified take-rate.
   - **Costs:** about 90 min per section if you have the evidence at hand. Needs sign-off from the CEO, finance, security and legal.
   - **Re-rank:** a take-rate was proposed before demand evidence exists, so this goes to rung 1 outright.
2. **`api-versioning-policy`**
   - **Attacks:** third-party builders freezing whatever your API does today.
   - **Costs:** one policy session, plus a named breaking-change signer.
   - **Re-rank:** promoted if the signer question (Q4 below) comes back empty. If you have no public API yet, `api-integration-surface-strategy` replaces it.
3. **`oauth2-provider-design`**
   - **Attacks:** apps acting on customer data on API keys.
   - **Costs:** a policy session, plus a data-protection review of scopes and the consent screen.
   - **Re-rank:** a third-party builder audience makes this a prerequisite, not an option.
4. **`partner-app-onboarding`**
   - **Attacks:** the path from signup to a first submitted app. Your two inbound partners are the natural pilot.
   - **Costs:** a design session, plus sandbox tenancy.
5. **`app-marketplace-listing-standards`**
   - **Attacks:** inconsistent submissions, and the rulebook you were asked to write.
   - **Costs:** one session once the curation level is set.
6. **`app-marketplace-review`**
   - **Attacks:** unreviewed apps touching employee schedules, availability and pay data. That is medium-to-high sensitivity.
   - **Costs:** a standing reviewer function that scales with submissions.
7. **`app-marketplace-monetization-model`**
   - **Attacks:** paid apps with no billing rail, payout rule or tax owner.
   - **Costs:** payment-facilitator and per-jurisdiction VAT obligations.
   - **Re-rank:** if you ship only free apps in June, this moves to "Not now".

## Chain

Dependency order, not ranked.

1. `connector-marketplace-strategy` hands over the build/catalog verdict, curation level and take-rate level.
2. `app-marketplace-listing-standards` hands over the listing contract.
3. `app-marketplace-review` hands over the rejection and revocation rules.
4. `app-marketplace-monetization-model` hands over the collection mechanics.
5. `app-marketplace-launch-marketing` hands over the reveal plan.

A second chain runs in parallel: `oauth2-provider-design`, then `partner-app-onboarding`, then `app-marketplace-review`. Apps need delegated auth before a partner journey means anything.

## Not now

- **`app-marketplace-launch-marketing`:** unblocked by a "build" verdict plus a named founding cohort.
- **Free-only launch:** moves `app-marketplace-monetization-model` here.

## Gaps

- **Certification program design:** test suites, renewal cycles and tier badges. The strategy skill's default hybrid model needs a certified tier, and the collection has no skill for it.
- **Product-to-platform decision:** the DevRel collection covers this. Install `samber/developer-relations-skills` and see its `developer-ecosystem-strategy`.
- **Producing the June conference itself:** install `samber/dev-event-organizer-skills`.

Both installs are recommendations, not dependencies.

## Open questions

I'm a one-shot run, so I batched these instead of asking one per message. Reply with letters.

1. **Audience:** you said partners and third-party builders (b/c). Confirm?
2. **Published surfaces:** do you have a public API today?
   - (a) REST with a committed spec
   - (b) REST without a spec
   - (c) the eleven integrations use private endpoints
   - (d) nothing public
3. **Owners:** who owns the API contract, and who signs off on a breaking change?
4. **Effort:** what is your ceiling?
   - (a) one-off, hours
   - (b) one-off, a week
   - (c) standing, a few hours a week
   - (d) standing, headcount and sign-off available
5. **Demand:** which of these exist?
   - (a) deals lost over missing integrations
   - (b) recurring requests
   - (c) procurement friction
   - (d) none
6. **Staffing:** can you staff review, partner support and a sandbox as a standing commitment?
7. **Data:** how sensitive is the data apps would touch?
   - (a) high
   - (b) medium
   - (c) low

## Context artifact draft

I did not write this to disk. This repo is not your project, and you should review the draft before it is committed. Save it as `developer-platform-context.md` at the Nimbus Rota repo root.

```markdown
# Developer platform context - Nimbus Rota

## Audience
Technology partners and third-party app builders (to confirm).

## Published surfaces
Unknown. Open question 2.

## Contract owner / breaking-change signer
Unknown. Open question 3.

## Constraints
- Landing date: June 2027 user conference (marketplace announced internally by the CEO).
- Horizon and effort ceiling: unknown, open question 4.

## In-flight work (2026-10-08)
- Submission rulebook assigned: screenshots, rejects, 15% take on paid apps.
- Re-routed to the build/join/buy gate first.

## Decided
- Marketplace is announced and tied to the June conference.

## Open
- Build vs curated catalog vs join.
- Take-rate level and tier axis.
- Curation level.
- Free-only vs paid apps at launch.

## Evidence
- 11 live integrations, 9 first-party.
- 2 unprompted partner build requests.
- Demand evidence: not yet collected.

## Session log
- 2026-10-08: cold start, routed to connector-marketplace-strategy.
```

## Routines (dry-run, not created)

1. **Quarterly kickoff re-invocation.** It re-routes against this context file. Output channel: a patch to `developer-platform-context.md` plus a message to you. Anchor it to the June conference calendar.
2. **Pre-release API design review**, fired on spec diffs. Only add it once question 2 confirms a committed spec. Output channel: a PR comment on the spec diff.

Approve either and I'll schedule it.

## Memory

I wrote none. When I do, these stay out of it:

- Partner names tied to API traffic.
- Keys and secrets.
- Negotiated take-rates.
- Unannounced sunset dates.
- Unpatched security findings.

Memory goes in a `memories/` directory in the Nimbus Rota repo, and I'll show you the diff before it's committed.

## Next step

Answer the seven questions, starting with 2 and 5. Then run `connector-marketplace-strategy`, which takes about 90 minutes if the demand numbers are ready.