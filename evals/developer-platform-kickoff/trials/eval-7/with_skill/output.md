# Saltmarsh Analytics: OAuth for third-party apps, then metering, then attribution

## 1. Decision: run `oauth2-provider-design`

Choose OAuth. The routing rules settle it. A third-party app acting on your customers' dashboards on their behalf is the OAuth case. API keys cover a customer's own backend calling you for itself. The kickoff says apps acting on user data cannot ship on API keys.

Why keys fail here, in order of weight:
1. **No consent.** A customer cannot see or approve what an app can do. A key has no consent screen.
2. **Bad revocation.** A key per app gives one secret access to every customer, so a leak hits everyone. A key per app and customer means customers paste secrets into third-party tools. Neither lets one customer cut off one app without the app's cooperation.
3. **No write safety.** Apps will *write* dashboards. OAuth gives a scope taxonomy (read and write split) and tiered app verification. A static key has one blast radius.
4. **Bad attribution.** A key identifies a secret, not an (app, customer) pair. That breaks the metering and "which app broke" questions below.

Where Security is right: operating OAuth is harder than operating keys. Meet that concern directly:
- Use short-lived access tokens, refresh rotation, and one per-app kill switch.
- Keep **API keys for customers' own engineers**. That is a separate audience, owned by `api-auth-key-management`.

The session itself must settle:
- The OAuth 2.1 baseline.
- The scope taxonomy, with read and write separated.
- The consent screen.
- Token lifetimes.
- Which verification tier gates write scopes.

I made this decision from your description and the collection's declared scopes. I did not audit your stack.

## 2. How to meter and bill it

**Metering: `api-rate-limit-policy`**, next after OAuth.
- Every request should carry a stable tuple: **app (`client_id`) + customer (tenant) + grant**. OAuth supplies this. Keys cannot.
- Meter and limit on (app, customer), not on the app alone. One noisy customer then can't starve an app's other customers, and one noisy app can't starve a customer's other apps.
- That session sets the quota and burst numbers, the header family, and the 429/`Retry-After` contract.
- A published limit can only be loosened later, never tightened. Set the numbers carefully.

**Billing: the collection has no skill for this.** API monetization (usage pricing and packaging) is a named coverage gap, so I won't invent a design. Open questions you must answer first:
- Who pays: the app developer, the customer, or Saltmarsh through a plan add-on?
- Which unit is billed: calls, writes, or seats?

You can still build the metering ledger now. It will serve any billing model you pick.

Two skills you might expect to apply don't yet:
- `app-marketplace-monetization-model` applies only if you run a marketplace, and only after `connector-marketplace-strategy` returns a build verdict.
- `samber/developer-relations-skills@devtools-business-model` covers the revenue model upstream, if you want to pick one.

## 3. How to tell a customer which app broke

**Route: `integration-error-observability`.**
- Log every request with `client_id`, tenant, grant ID and a correlation ID that survives into a support ticket.
- Aggregate error rates per app. Apps would see their own logs. Saltmarsh would get a fleet view. Notify the app owner, with cooldowns.
- Caveat: that skill is written for what an *integrator* sees. A customer-facing "app X is failing on your dashboards" view is an adjacent use. Treat it as a check item for that session, not a given.
- Per-app attribution depends on OAuth identity. That is why OAuth goes first.

## 4. Ordered chain (dependency order)

1. `oauth2-provider-design`: issues the (app, customer, grant) identity.
2. `api-rate-limit-policy`: meters and limits on that identity.
3. `integration-error-observability`: splits errors by that identity.

This is the kickoff's auth → limits → observability chain, with OAuth in place of keys.

## 5. Short-list, by value per unit of effort

Re-ranks, stated out loud:
- A third-party builder ecosystem moved OAuth to rung 1 as a prerequisite.
- It also moved ecosystem work above debuggability.

| # | Skill | Bottleneck it attacks | Session cost |
|---|---|---|---|
| 1 | `oauth2-provider-design` | The undecided credential model that blocks everything below | Policy session, then an auth-server build and a data-protection review |
| 2 | `api-rate-limit-policy` | Noisy neighbours and nothing to bill on | Policy session plus gateway config. Limits can only loosen later |
| 3 | `api-error-design` | Apps recover only from errors they can parse | One design session plus an additive backend change |
| 4 | `integration-error-observability` | "Which app broke" | A log store with retention, and a named person to contact app owners |
| 5 | `api-test-mode-design` | Outside developers need somewhere safe before touching real customer dashboards | An isolation model you run forever |
| 6 | `api-versioning-policy` | Apps pin to your API, and a breaking change needs a defined signer | Coordination across product, security and legal. Move it to rung 1 if nobody can name who signs off |

**Not now:**
- `app-marketplace-review`: after OAuth, and after `connector-marketplace-strategy` returns a build verdict.
- `partner-app-onboarding`: after OAuth, once you want a signup-to-first-app journey.
- `app-marketplace-monetization-model`: only if a marketplace exists.

## 6. Gap

API monetization (usage-based pricing and packaging) has no skill in this collection. You still have to make the billing-model decision yourself.

## 7. Assumptions to confirm

The kickoff's interview needs answers I don't have. I assumed the audience is an open ecosystem of third-party builders, which you stated. Each answer below can move the ranking:
- **Surfaces already public?** If nothing is public yet, drop any surface audit and put `api-integration-surface-strategy` first.
- **Who signs off on a breaking change?** If nobody, versioning moves to rung 1.
- **Launch date or audit window?** A compliance window promotes OAuth and the rate-limit policy.
- **Effort ceiling?** If limited, `api-test-mode-design` moves to "not now".

## 8. Routines (dry-run, nothing installed)

1. Pre-release API design review, triggered by the spec diff. Output channel: your call, such as an engineering channel.
2. Quarterly kickoff re-invocation. Output channel: a platform check-in reminder.

I did not write `developer-platform-context.md`, because the working directory is a different project. I also saved nothing to memory. Tell me where it should live and I'll write it.

**Next action:** run `oauth2-provider-design`. Bring Security into that session so they see the revocation and kill-switch design.