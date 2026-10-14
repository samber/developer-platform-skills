**Next action:** Pull your funnel data for the first-run tutorial page and find the step where users leave. That takes about 1 hour, and it is the task I'd take first.

I used the `developer-platform-kickoff` router. It routes work and does not do the design itself. All three tasks fall outside `developer-platform-skills`. Gaps and hand-offs are at the end.

## Assumptions

I could not interview you interactively, so I assumed the following. Correct me if any are wrong, because each one changes the ranking.
- **Audience:** your customers' own engineers integrate with the API.
- **Capacity:** one platform engineer is the effort ceiling (the router's "limited capacity" constraint).
- **Decided:** Python and Go are the SDK languages.

## Route

**Tutorial rewrite goes first.**
- It is the route with an active leak: everyone drops off there today.
- It is cheap, reversible, and needs no sign-off.
- The right skill is `samber/developer-relations-skills@developer-quickstart-guide`. It is not in this collection. Recommendation only, not a dependency.

Sequence the three tasks like this:

1. **Tutorial (about 1 hour to diagnose, a day or two to rewrite).**
   - Find where users drop off.
   - If they leave before the page (signup, getting a key), the problem is `developer-portal-design`, not the page copy.
   - Write the final snippets after the libraries are published, so the first call is a few lines of SDK code.
2. **Client libraries (hours, mechanical).**
   - Publish just before the ship date.
   - PyPI versions cannot be re-uploaded, so treat the first release as hard to reverse.
3. **Usage pricing (weeks, needs finance).**
   - Do it last.
   - A published price is hard to walk back in the customer's favour.
   - It needs real per-key usage data first, which `api-auth-key-management` and `api-rate-limit-policy` help you meter.

## Short-list (value per unit of effort, highest first)

1. `public-api-design-review`
   - **Attacks:** unknown flaws in the surface. Generated clients freeze them in code.
   - **Costs:** one session over your spec, with nothing to deploy or roll back.
2. `api-error-design`
   - **Attacks:** first-call failures, which are the usual cause of tutorial drop-off. This is a hypothesis, not a finding.
   - **Costs:** a design session plus an additive backend change.
3. `api-idempotency-retry`
   - **Attacks:** SDK retry defaults that double-charge or double-create.
   - **Costs:** one session plus idempotency support on write endpoints.
4. `api-reference-quality`
   - **Attacks:** undocumented endpoints and missing snippets. It is near-free if an OpenAPI spec is committed.
   - **Costs:** one session plus a CI lint gate.
5. `api-versioning-policy`
   - **Attacks:** shipping SDKs means publishing a compatibility promise.
   - **Costs:** a coordination session with product, and it ships no code.
   - **Re-rank:** if nobody currently signs off on breaking changes, this jumps to rung 1.

**Re-ranks:**
- Limited capacity deleted the second-surface and specialist-protocol classes this session.
- "Customers' own engineers" deleted ecosystem execution and `oauth2-provider-design`.
- Decided languages removed `sdk-portfolio-strategy`.

**Chain** (dependency order): `public-api-design-review`, then `api-error-design`, then `api-idempotency-retry`, then `api-reference-quality`. Each link fixes what the next one would otherwise document or freeze.

## Not now

- `developer-portal-design`: unblocks if funnel data shows users leave before the tutorial, or when capacity frees up.
- `api-test-mode-design`: unblocks if the diagnosis shows first-run users need a sandbox.
- `mcp-server-offering`: unblocks if AI agents turn out to be an audience.
- `webhook-platform-design`: unblocks when customers ask for push events and capacity allows.

## Gaps

1. **Package-registry publishing: no skill in the collection.**
   - This covers PyPI classifiers, Docker Hub descriptions and trust signals. `sdk-portfolio-strategy` picks languages, not publishing.
   - Go has no upload registry. It uses tagged modules through the module proxy and pkg.go.dev, so the Go half needs a different checklist.
   - I could not find a matching skill in the DevRel sibling either.
2. **API monetization: no skill in the collection.**
   - This covers per-call, per-seat and credits. The closest hand-off is `samber/developer-relations-skills@devtools-business-model`.
   - A `devtools-pricing-strategy` skill also appears installed locally. I have not verified its scope.
3. **Quickstart rewrite: belongs to the DevRel sibling.** Use `samber/developer-relations-skills@developer-quickstart-guide`.

## Routines (dry-run, nothing installed)

1. **Pre-release design review**
   - **Skill:** `public-api-design-review`.
   - **Trigger:** a spec-diff PR.
   - **Output:** a comment on that PR.
2. **Quarterly kickoff re-run**
   - **Output:** a PR updating `developer-platform-context.md`.

Capacity is limited, so I stopped at two.

## Context artifact (draft, not written)

I did not write it because this repo is `example-repo`, not Tern Robotics. Save it as `developer-platform-context.md` at the Tern project root:

```
Audience: customers' own engineers (assumed)
Published surfaces: API (version scheme unknown); Python and Go clients (shipping)
Spec location: unknown
Contract owner / breaking-change signer: unknown (ask)
In-flight (2026-10-08): SDK publish; usage pricing (finance); tutorial rewrite
Decided: Python and Go SDKs
Open: pricing meter; where tutorial drop-off happens
Constraints: 1 platform engineer; ship date unknown; horizon unknown
Session log: 2026-10-08 cold start; routed to DevRel quickstart; 3 gaps named
```

**Memory:** I wrote none. When you add memory, keep out partner or customer names tied to traffic, keys or secrets, negotiated rates, and unannounced sunset dates.

## Next

Answer these two questions and I will re-rank the list:
1. Who integrates with you: customers' engineers, partners, or open third-party builders?
2. What is the SDK ship date?