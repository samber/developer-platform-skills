**Next action:** list your ~180 endpoints grouped by tag, then mark each one "config" or "operational data". That takes about 30 minutes. Everything below depends on that split.

## Verdict on your sketch

| Your idea | Verdict |
|---|---|
| Cover all 180 endpoints in v1 | ❌ Push back. Terraform manages config, not operational data. |
| Messages, sends, delivery events | ❌ No resources. |
| Contacts | ❌ No resource. Data source only. |
| Inline members plus `workspace_member` | ❌ Pick one: `workspace_member`. |
| `marrowgate_template_state` resource | ⚠️ Use a `paused` attribute on `marrowgate_template` instead. |
| `data.marrowgate_contact` returns first match | ❌ Error on multiple matches. |
| Rename `title` to `display_label` | ❌ Keep `title`. |
| Sending domain setting | ✅ Singleton resource, with explicit destroy semantics. |

## Pushbacks

**1. "Cover everything" is the wrong goal.**
- Messages, sends and delivery events are append-only and immutable. They have no desired state to converge to.
- A resource for them makes `plan` meaningless. Every apply would create a new message.
- A delivery-events data source would be unbounded and change on every read. It breaks plan stability. Use the API or SDK for these.
- Contacts are high-cardinality PII. A contact resource puts personal data in every state file and makes plans slow.
- Result: 180 endpoints become about 5 resources and 3-4 data sources.
- Coverage is worth more than breadth. Every resource you ship is a permanent compatibility promise.

**2. Inline members and `workspace_member` both owning the same data.**
- Two owners of one list means a perpetual diff.
- With inline `members` in a `marrowgate_workspace` config and a separate `marrowgate_workspace_member`, each apply removes the other's entries. This is the known `aws_security_group` inline-rules problem.
- Ship only `marrowgate_workspace_member`.
- Its import ID is `workspace_id/member_id`.
- `marrowgate_workspace` gets no `members` attribute.
- If you later want authoritative membership, add a separate `marrowgate_workspace_members` resource. Do not add it now.

**3. Pause and unpause as a resource.**
- A `_state` resource has an ambiguous destroy. Destroy could unpause the template, or leave it paused, or do nothing. Any choice surprises someone.
- It also lets two resources fight over one template.
- Put `paused` (bool) on `marrowgate_template`. Its Update calls the pause or unpause endpoint.
- If pause is a one-off operational command, not desired state, use a Terraform action instead. That needs Terraform 1.14 or later and plugin-framework support. Check your minimum supported version first.
- Keep the separate resource only if pausing has its own lifecycle, such as a different owner or permissions. I doubt that.

**4. `data.marrowgate_contact` "first match".**
- First match is nondeterministic. The API's ordering can change, and a plan can then silently point at a different person.
- Behavior:
  - Zero matches: error.
  - More than one: error, with the count and the suggestion to look up by `id`.
  - Exactly one: return it.
- Offer `id` as an alternative lookup, and make `id` and `email` mutually exclusive.
- Contact data in state is PII. Expose only the fields people need, such as `id`, `email` and `status`. Mark the rest sensitive, or leave them out.
- If email is unique per workspace, require `workspace_id`.

**5. `display_label` for `title`.**
- Do not rename attributes.
- Users read the API docs and the SDK, and they expect the same names. Renames break `terraform import` mental models, support answers, generated docs, and every future spec diff.
- Rename only on a real collision or a Terraform reserved name: `id`, `provider`, `count`, `for_each`, `depends_on`, `lifecycle`, `connection`, `provisioner`.
- Use snake_case if the API uses camelCase. That is a convention, not a rename.
- If `title` is just a plain string, keep `title`.

**6. Sending domain setting.**
- Treat it as a singleton: `marrowgate_account_sending_domain`.
- Create adopts and updates the existing setting. It does not create a second one.
- Destroy resets to the API default, or does nothing if there is no reset endpoint. Document which in the resource docs.
- If domains have DNS verification, expose the required records as computed attributes. Do not block apply on verification. Expose `verified` instead.
- If an account can hold several domains, this is a list resource, not a setting. Check the spec.

**7. Generating from OpenAPI.**
- `tfplugingen-openapi` is still experimental. Use it for schema skeletons, not finished resources.
- Specs do not say which fields are computed, sensitive, immutable (needs replace), or write-only. You must decide each one.
- Generate a plain API client with `oapi-codegen`. Hand-write the CRUD layer.
- Use `terraform-plugin-framework`, not SDKv2.
- Cover these concerns up front, because the spec will not:
  - Pagination.
  - Rate limits and retry with backoff.
  - Eventual consistency (read-after-write).
  - 404 on read means remove from state.
  - Idempotency keys on create.
  - Import for every resource.

## Proposed v1 scope

Resources:
1. `marrowgate_workspace`
2. `marrowgate_workspace_member`
3. `marrowgate_template`, with a `paused` attribute
4. `marrowgate_segment`, only if segments are rule definitions. If membership is a static list of contacts, skip it.
5. `marrowgate_account_sending_domain`, a singleton

Data sources:
1. `marrowgate_workspace`
2. `marrowgate_template`
3. `marrowgate_contact`, by `id` or `email`
4. `marrowgate_segment`, optional

Not in v1: messages, sends, delivery events, contact resource, team-member resource (covered by `workspace_member`), and anything the endpoint split shows is operational.

## Estimates

All times assume one developer and a sandbox account for acceptance tests.
- Endpoint triage: 30 minutes.
- Scaffold and client generation: about 1 day.
- Each resource with tests and import: half a day to 1 day. The template is the longest, because of `paused`.
- Total: about 5-7 days for the 5 resources and 4 data sources.

## Gates

These checks must pass:
- `go build ./...`
- `go test ./...`
- `TF_ACC=1 go test ./...` against the sandbox
- `golangci-lint run`
- `tfplugindocs generate`, then check that the docs are committed

Also, for each resource, break the code on purpose (for example, drop a field from Update) and confirm the acceptance test fails.

## Questions

1. Are contact emails unique, per account or per workspace?
2. Do pause and unpause use dedicated endpoints, or a field on template update?
3. Are segments rule definitions or static member lists?
4. Does the sending domain have one value per account, or a list?
5. Do workspace members have roles, and can a member exist in several workspaces?

**Next:** send me the endpoint list grouped by tag, or answer questions 1-5, and I'll lock the v1 scope.