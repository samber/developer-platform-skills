# Marrowgate Terraform/OpenTofu provider: go/no-go and v1 plan

I followed `terraform-provider-offering` and all five of its references.

**Verdict:** go, but not as "generate 180 endpoints and ship everything". Ship a hand-owned core of about 6 resources. Four of your sketches break the provider contract, and I've pushed back on them below. No resource can ship yet. Every gate row is UNKNOWN until your API team answers the questions at the end.

## 1. Ship decision and path

- **Signals (need 2 of 4):** I have no evidence for any of them. The inputs are customers asking for Partner-badged providers, an existing community provider, long-lived config objects, and customers scripting the API in CI. Workspaces, templates, segments, sending domain and team members are long-lived config objects, so that is one signal. Question 2 gets you the second.
- **Path, assumed vendor-owned hand-written on the Plugin Framework (protocol 6).** I assume no usable community provider exists. If one does, run the community-provider audit first, because transfer-adopt ranks above a rewrite.
- **Why not generated, full coverage:** that rung is promoted only when the API has "well over a hundred resource types" and the spec carries semantics such as sensitive, write-only, sets and normalization. 180 endpoints is roughly 25–35 objects, because each object takes about 5–6 endpoints. Your spec's semantics are unverified. A generated schema inherits every spec gap as a perpetual diff, and every attribute name becomes a public contract.
- **Where generation helps:** use it for schema and model scaffolding on simple synchronous objects. Keep CRUD hand-owned for anything async or eventually consistent.
- **Effort ceiling:** this moves with questions 7 and 8 below. A near deadline keeps this path.

## 2. Scope: what is and isn't a Terraform object

| API area | Construct | Why |
| --- | --- | --- |
| messages, sends, delivery events | **left out** | Transactional records have no desired state to converge to. They would be plan noise and unreadable state. |
| contacts | **no resource in v1**; data sources only | Probably created constantly by your customers' apps, which makes them records, not configuration. This depends on Q3. Contacts are also PII, and a data source writes them into state. |
| workspaces | resource and data source | Long-lived configuration. |
| workspace membership | one attachment resource (see push-back 1) | One-to-many membership. |
| team members | resource, shape pending Q10 | Depends on whether a member is an account-level user or an invitation. |
| templates | resource and data source | Configured once and kept. |
| segments | resource and data source | Same. Rule ordering is an open question. |
| sending domain | singleton resource | See push-back 5. |

Realistic v1: about 5–6 resources and 3–4 data sources. Everything else is "left out" with a written reason, not "later".

## 3. Push-back on your sketches

1. **`marrowgate_workspace` inline members plus `marrowgate_workspace_member`: pick one.** The skill says never to ship both without conflict warnings, because they fight over the list on every apply. Ship the attachment resource only.
   - Keep `marrowgate_workspace` free of any members block.
   - Adding an inline list later is possible but needs a conflict design. Removing one later is a major.
   - Members should be a `set` unless the API means an order.
2. **`marrowgate_template_state` (pause/unpause): drop it.** Enable/disable is an attribute of the resource, never a separate "state" resource.
   - Put it on `marrowgate_template` as `paused` or `status`, using the API's real field name.
   - A separate resource would fight the template resource over that field on every plan.
   - If pause is a pure RPC with no field to read back, it is an action. That is Terraform 1.14+ only, and it is the first thing cut.
3. **`data.marrowgate_contact` returning the first match: reject.**
   - A singular data source errors on zero matches and on several matches. "First match" makes plans nondeterministic, so an unrelated contact insertion silently re-points your config.
   - If email is unique in your API, the singular lookup errors on zero results. That is deterministic.
   - If it isn't unique, ship a plural `marrowgate_contacts` filtered by email. Zero results is valid there.
   - Pick a lookup key per Q3 below.
4. **`display_label` for `title`: don't rename.** Attribute names are snake_case of the API's field names, so the docs map onto the API reference.
   - Every rename is a major-version change later.
   - If `title` is truly unclear, put the explanation in `MarkdownDescription`, or fix the name in the API.
   - A provider vocabulary that diverges from the API also lowers the case for anyone adopting or auditing it.
5. **Sending domain.** It is a singleton that cannot be created or destroyed, so it becomes a resource whose Create adopts the setting and whose Delete resets it to the documented default.
   - Q9 asks you to confirm it really is one object per account. If an account can hold several domains, it is a normal resource.
   - DNS verification is likely an async or propagation step, which makes it a gate row.
   - DKIM or DNS records are computed outputs and not secrets. Any returned private signing key is.
6. **"Cover everything in v1."** Coverage is not a goal. A resource ships only when its gate column holds no FAIL or UNKNOWN, and an object with an unfixed FAIL moves to the next minor. Tag `0.x` while the resource map is moving, and promise compatibility from `1.0.0`.

## 4. Gate matrix (all UNKNOWN until answered)

Cells: `UNKNOWN`, with `n/a` where the check cannot apply. Owner and due dates are blank for you to set.

| Check | workspace | workspace_member | team_member | template | segment | sending_domain |
| --- | --- | --- | --- | --- | --- | --- |
| Stable server-assigned ID | UNKNOWN | UNKNOWN (composite?) | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |
| GET returns writable fields | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |
| In-place update | UNKNOWN | UNKNOWN (role change?) | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |
| Idempotent create | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | n/a (singleton) |
| Bounded propagation (seconds) | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN (DNS) |
| Pollable async op, ID in 202 body | UNKNOWN | n/a? | UNKNOWN (invites) | n/a? | UNKNOWN (rebuild?) | UNKNOWN |
| Deterministic normalization/order | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN (HTML?) | UNKNOWN (rules) | UNKNOWN |
| Secrets identified | UNKNOWN | n/a | UNKNOWN | n/a | n/a | UNKNOWN |
| Documented rate limits | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |

Template bodies are the likely normalization trap, since servers often re-render HTML. Segment rules are the likely ordering trap.

Cut rule: an object with an unfixed FAIL at the cut moves to the next minor. It never ships with a known perpetual diff.

## 5. Resource map (draft)

Type names take the noun from the API, so rename these if your operation names differ.

| API object | Construct | Type name | ID / import | Mutable | Replace-only | Preserved (never returned) | Secrets | Collections | Consistency | Timeouts |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| workspace | resource, singular and plural data sources | `marrowgate_workspace` | plain ID | ? | ? | ? | ? | none | ? | default |
| membership | attachment resource | `marrowgate_workspace_member` | `workspace_id/member_id`, documented | role? | member and workspace IDs | none | none | n/a | ? | default |
| team member | resource (shape per Q10) | `marrowgate_team_member` | plain ID | ? | email? | ? | none | none | invite = async? | create |
| template | resource, singular and plural data sources | `marrowgate_template` | plain ID | title, body, `paused` | ? | ? | none | variables as `set` | ? | default |
| segment | resource and data source | `marrowgate_segment` | plain ID | ? | ? | none | none | rules: `set` unless API orders them | rebuild async? | create and update |
| sending domain | singleton resource | `marrowgate_sending_domain` | plain ID or the singleton's key | ? | none | ? | possible key | DNS records `set` | DNS verify = async | create |
| contacts | plural data source only | `data.marrowgate_contacts` | n/a | n/a | n/a | n/a | PII in state | list | n/a | n/a |

Rules that apply to every row:

- Every resource imports by plain ID. `ImportStateVerifyIgnore` lists the Preserved column plus API-generated secrets, and nothing else.
- Skipped construct rungs, with the reason:
  - **Write-only arguments:** apply only if Q9 or Q10 reveals a user-supplied secret.
  - **Ephemeral resources:** no short-lived token has been identified.
  - **Identity plus list resources, actions, functions:** none are v1. Actions and list resources are Terraform-only. Identity needs Terraform and OpenTofu 1.12+, and import by plain ID covers older binaries.

## 6. Plan-time behaviour (applied to every resource)

- **Read:** set every returned attribute, preserve the ones the API never returns, and remove the resource from state on 404. Delete treats "already gone" as success.
- **Plan modifiers:** use `RequiresReplace` only where the API can't update, and `UseStateForUnknown` on IDs and creation timestamps. Defaults must match the API's own.
- **Validators:** use them for emails, enums, domain syntax, and `ExactlyOneOf` or `ConflictsWith` pairs.
- **Eventual consistency:** diagnose the class per row, then use bounded waiters on typed errors after create, update and delete. Never retry broad error classes.
- **Provider config:** every auth attribute is Optional with an environment fallback, secrets are Sensitive, and unknown values are guarded. No write calls at configure time. Send a `User-Agent` carrying the provider name and version.
- **Rate limits:** at Terraform's default parallelism of 10, you need client-side throttling and `Retry-After` handling. Document a safe `-parallelism` value.
- **Minimums:** default to the oldest upstream-supported Terraform and OpenTofu minors, and record them. Write-only arguments need 1.11+ on both.

## 7. Tests

- **Per resource:** `_basic` ending in an import step, `_disappears`, an update test per mutable attribute, and a replacement test per replace-only attribute.
- **Data sources:**
  - Singular: errors on zero and on several matches.
  - Plural: returns empty without error.
- **Template:** pause then unpause by changing one attribute, asserting the planned action is an in-place update.
- **Never** set `ExpectNonEmptyPlan`. A PR that adds it must link the API bug it works around.
- **Upgrade tests:** apply the last release, plan the new build, expect no changes.
- **Import config generation:** use `-generate-config-out` and run `terraform validate` on the result.
- **Sandbox:** use a dedicated Marrowgate account with prefixed `tf-acc-test-<random>` objects, sweepers before and after each nightly, and a `tofu` lane.
- **Sending domain:** one test account per domain, because it is a singleton.
- **CI:** no fork-PR runs with sandbox credentials. A green nightly gates every release.
- **Sandbox quotas:** raise them for the parallel suite. If sandbox accounts don't exist, build one with `api-test-mode-design`.

## 8. Release checklist

1. Create public repo `<final-org>/terraform-provider-marrowgate` (lowercase). Q6 must confirm the org before anything else, because a later move breaks every user's `source`.
2. Add `terraform-registry-manifest.json` with protocol `6.0`.
3. Generate an RSA 4096 signing key with an expiry reminder, plus an offline backup and revocation certificate. Store it as CI secrets, and pin every action to a commit SHA.
4. Copy the GoReleaser config and tag-triggered workflow from `hashicorp/terraform-provider-scaffolding-framework`. Build linux, darwin, windows and freebsd on amd64 and arm64.
5. Rehearse with a local snapshot build, then tag `v0.1.0-beta1`.
6. Register the provider and key on registry.terraform.io. Submit the provider and key through the `opentofu/registry` web issue forms the same day.
7. Tag from the default branch, then verify `terraform init` and `tofu init` on a clean machine, with `OPENTOFU_ENFORCE_GPG_VALIDATION=true` for the OpenTofu check.
8. Enable GitHub immutable releases and never retag or delete a version.

## 9. First-release plan

| Week | Track A (provider) | Track B (API and release) | Decision |
| --- | --- | --- | --- |
| 1 | Fill the gate matrix with the API team, check for a community provider | File an API ask for every FAIL row | **D1:** path chosen |
| 2–3 | Scaffold, provider config, `marrowgate_workspace` | Signing key, GoReleaser, both registries rehearsed | |
| 4–6 | Remaining v1 resources and data sources | Sandbox, sweepers, nightly CI | **D2:** cut list, still-FAIL objects move out |
| 7 | Upgrade tests, import config generation | Docs generated, upgrade guide drafted | |
| 8 | Prerelease tag, early-customer trial | OpenTofu provider and key submitted | **D3:** go or slip |
| 9–10 | Fixes from the trial | `0.x` tag, announcement | |

- If time runs out, cut actions and functions first, then list resources, then the least-used data sources.
- **Never cut** import support or upgrade tests.

## 10. Versioning and deprecation schedule

- Tag `0.x` until the map is stable, then `1.0.0`. After that, apply the bump test: does an unchanged config plus existing state produce a diff, an error or a different object? Yes means major.
- Majors at most once a year. Every removal or rename is deprecated in a minor first and removed in the next major, with an upgrade guide.
- A renamed resource type ships beside the old one, with a state mover.
- Align API field sunsets with `api-versioning-policy`. A sunset becomes a provider deprecation one minor earlier.
- Start the changelog now in the HashiCorp format: BREAKING CHANGES, NOTES, FEATURES, ENHANCEMENTS, BUG FIXES.

## 11. Done when

- Every resource's acceptance suite passes with no `ExpectNonEmptyPlan`.
- Upgrade tests pass from the last release.
- `terraform init` and `tofu init` both install the latest version.
- No removal has shipped in a minor since 1.0.0.

Track Registry downloads per major, open perpetual-diff and "inconsistent result after apply" issues, nightly flake rate per resource, and deals or reviews where the provider tier came up.

## 12. Questions I need answered

Each answer changes a gate row or a path. I've marked each as UNKNOWN until you reply.

1. Does a Terraform provider for Marrowgate exist (community, partner or internal)? If so, its address, license, downloads, open issues, last release and whether the maintainer responds.
2. What is the real demand? Deals or security reviews asking for a Partner-badged provider, customers scripting the API in CI, support tickets, or requests for Pulumi or Crossplane?
3. Which objects do customers configure once and keep, and which do they create constantly? Specifically:
   - Are contacts created by customers' apps at volume?
   - Is email unique per contact?
4. Per object:
   - Is there a stable server-assigned ID, and does GET return every writable field?
   - Is there an in-place update?
   - Is create idempotent?
   - How long until an object is readable after create, update and delete?
   - Do async operations return the object ID in the 202 body?
   - Are collections ordered and kept in order?
   - Are rate limits documented?
   - How far has the OpenAPI spec drifted from the real API?
5. Who owns the provider, who is on-call for its issue queue, and is there a sandbox account?
6. What tier is the target (Partner or Partner Premier)? Do OpenTofu users matter? What are the oldest Terraform and OpenTofu versions customers run? Which GitHub org is final?
7. By when must v1 land, and what is the effort ceiling? Say which answer moves which rung of the path.
8. Does the spec carry vendor extensions for sensitive, write-only or async fields? That decides whether generation could be promoted later.
9. Sending domain: one per account, or several? What is the documented default that Delete should reset to? Does verification poll, and is any key returned once?
10. Team members: account-level users or workspace-scoped invitations? Does the API return a role, and what happens on accept?

When you answer these, I'll re-score the gate matrix and fix the cut list at D2.

## 13. Memory record

I couldn't write it from this session. Paste this as its own section in `developer-platform-context.md`, or into whichever memory system you use:

```
## Marrowgate provider (2026-10-24)
Path: vendor-owned hand-written, Plugin Framework (assumed; Q1 open).
Namespace: <final org>, TBD (Q6).
Min versions: oldest upstream-supported Terraform/OpenTofu minors; write-only needs 1.11+.
Gate matrix: all UNKNOWN until Q4 answered.
Resource map: workspace, workspace_member (attachment only), team_member, template (paused attribute), segment, sending_domain (singleton). Left out: messages, sends, delivery events, contacts (data source only).
Deprecation schedule: none yet; starts at 0.x.
```