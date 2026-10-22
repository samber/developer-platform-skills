# Resource design and plan-time rules

Load at workflow steps 3 and 4. Code-level names refer to `terraform-plugin-framework`; check the framework's own docs for exact signatures before writing code.

## Contents

- Constructs and version gates
- API object to construct mapping
- Data source rules
- Naming
- CRUD contract
- Plan modifiers, validators, defaults
- Secrets: sensitive, write-only, ephemeral
- Eventual consistency and async operations
- Import and identity
- Schema versions and state moves
- Provider configuration and credentials
- SDKv2 providers

## Constructs and version gates

| Construct | Use for | Persisted in state | Terraform | OpenTofu |
| --- | --- | --- | --- | --- |
| Resource | an object with a lifecycle the user owns | yes | all | all |
| Data source | read-only lookup, no side effects | yes | all | all |
| Provider-defined function | pure computation (parse an ID, encode a value) | no | 1.8+ | 1.7+ |
| State move (`moved` across types) | renaming or splitting a resource type | - | 1.8+ | 1.10+ |
| Ephemeral resource | short-lived tokens, credentials, tunnels (`Open`/`Renew`/`Close`) | no | 1.10+ | 1.11+ |
| Write-only argument | a secret input to a resource | no | 1.11+ | 1.11+ |
| Resource identity | structured identity for import blocks (`identity` argument) | yes | 1.12+ | 1.12+ |
| List resource | enumerate existing objects for `terraform query` and bulk import | no | 1.14+ | not implemented (open issue) |
| Action | an imperative day-2 operation (restart, rotate, invalidate a cache) | no | 1.14+ | not implemented |

A provider can ship Terraform-only constructs (list resources, actions) without breaking OpenTofu users, provided every resource still imports by a plain import ID and works without them. Re-check OpenTofu's changelog before each major: parity moves.

## API object to construct mapping

- The API exposes create, read, (update), delete for a thing: resource. Prefer many small resources over one resource holding a whole account.
- One resource talks to one API service. Cross-service resources break permission scoping, audit trails and per-service endpoints.
- Singleton settings that cannot be created or destroyed: resource where create adopts the setting and delete resets it to the documented default.
- Attached document (policy, rule set): separate resource referencing the parent.
- One-to-many membership: separate attachment resource. Never offer both an inline list and an attachment resource for the same collection without a conflict warning in both docs: they fight over the list on every apply.
- Enable/disable or start/stop: an attribute of the resource, never a separate "state" resource.
- Long-running job that leaves an artifact: resource whose Create starts it and whose Read polls it.
- Invitation or handshake: resource on the accepting side (Create accepts, Delete leaves).
- Versioned artifact: a separate `<thing>_version` resource.
- Pure RPC with no persistent object: action, or leave it out.
- Transactional records (orders, messages, events, payments): leave them out. They have no desired state to converge to.

## Data source rules

- No side effects, ever: plans run data sources freely.
- Singular data source: zero matches is an error, several matches is an error. Returning the first match makes plans nondeterministic.
- Plural data source (plural noun): returns a list or set; zero matches is valid.
- Ship both for most resource types, and keep plural data sources even after adding list resources: list results are for discovery and import, not for references in configuration.

## Naming

- Type names `<provider>_<noun>` or `<provider>_<service>_<noun>`, snake_case, the noun taken from the API (`CreateWidget` gives `_widget`) so the docs map onto the API reference.
- Attribute names: snake_case of the API field names. Expose the real identifier under its real name; add `id` only when it is the API's ID.
- Names are public API: renaming one later is a major-version change.

## CRUD contract

- Create: send the planned values, wait until the object is usable, then Read and set every attribute from the API response.
- Read: set every attribute the API returns. On "not found", remove the resource from state and return no error, so the next plan proposes recreating it. Erroring forever traps users in a state they cannot plan past.
- Update: send only attributes that changed between plan and state; then Read back.
- Delete: treat "already gone" as success; wait until the API confirms deletion when dependants could race it.
- Match API errors by type or status code, never by message text.
- Diagnostics: summary `Error <operation> <Type>`, detail `<operation> <Type> (<id>): <cause>`; attach attribute paths for field errors.
- No side effects in provider configuration: registering services, creating default objects or calling write endpoints at configure time fails under least-privilege credentials and runs on every plan.

## Plan modifiers, validators, defaults

- `RequiresReplace` only on fields the API truly cannot update. Each one turns an edit into destroy-and-recreate; say so in the field docs.
- `UseStateForUnknown` on computed values stable across updates (IDs, creation timestamps), so plans do not show "(known after apply)" noise.
- An attribute with a default must be Optional and Computed. Never add a default that differs from the API default: existing objects show a diff on upgrade.
- Optional+Computed attributes must either keep the prior state value or be legitimately unknown at plan. Returning a different value after apply causes "Provider produced inconsistent result after apply".
- Validators (`terraform-plugin-framework-validators`): lengths, regexes with a message, `OneOf`, ranges, `ExactlyOneOf`/`ConflictsWith`. Syntax errors fail at plan instead of halfway through an apply.
- Server-side normalization (case, ordering, formatting): normalize in the provider with a semantic-equality custom type or plan modifier, and document it. Removing a normalization later is itself a breaking change.
- Use sets for collections the API treats as unordered; lists only where order means something. Switching between the two later is breaking. When the API returns an ordered collection in arbitrary order, either the API adds a position field (then a list sorted by it) or the provider uses a set; ask the API team before choosing, because the choice is permanent.

## Secrets: sensitive, write-only, ephemeral

Key the construct on who creates the value:

| Who creates it | Construct | Stays out of state |
| --- | --- | --- |
| User supplies it, API never returns it (password, client secret) | write-only argument plus a `<name>_wo_version` attribute | yes |
| API generates it and returns it once (integration key) | `Sensitive` computed attribute: set at create, preserved on Read, null after import; rotate by replacing the resource | no - document it |
| Short-lived credential another provider or resource consumes | ephemeral resource | yes |
| Any value that must only be hidden in plan output | `Sensitive: true` | no - still stored in plaintext |

- An API-generated one-time secret becomes write-only only if the API lets callers supply the secret instead; ask for that, it removes the secret from state.

- Write-only arguments cannot be Computed and cannot sit in sets or set-nested blocks. Terraform cannot diff them, so users bump `<name>_wo_version` to push a new value.
- Write-only needs Terraform and OpenTofu 1.11+. Below that minimum, ship a `Sensitive` attribute beside the write-only one, `ConflictsWith` between them, and steer users with the `PreferWriteOnlyAttribute` validator.
- A non-secret field the API accepts but never returns: keep it a normal attribute, preserve its prior state value on Read, and document that drift on it is undetectable. Write-only is for secrets: it removes drift detection and plan visibility.

## Eventual consistency and async operations

Diagnose the class before writing a retry:

1. Not yet visible: a write returned, a read 404s or returns stale values briefly. Retry not-found or wait for the written value only in the reads that follow your own create, update or delete, never in the plain Read that refresh runs. Require two consecutive good reads when the API sits behind replicas.
2. Temporarily refused: a dependency has not propagated. Retry only the specific typed error, bounded.
3. Asynchronous completion: status moves `CREATING` to `ACTIVE`. Poll a status function until the target state, failing fast on terminal error states.

- Never retry broad error classes (every 400, every 5xx): a misconfiguration turns into a long hang ending in a vague timeout.
- Size retry windows from the API's published propagation time. A starting point, not a standard: about three times it, leaving headroom for slow regions and loaded replicas; operation timeouts at about twice the worst case observed in the sandbox. Tune both from nightly test timings, name each constant and document it.
- Expose user-configurable `timeouts` (the `terraform-plugin-framework-timeouts` module) for create, update and delete wherever the API runs long operations.
- Async create: when the 202 carries the object ID, write the ID to state before polling. If polling times out, return the error with the ID in state: Terraform marks the resource tainted and the next apply replaces it instead of creating a duplicate. Without an ID in the 202 there is no safe recovery; that is a gate FAIL.
- Rate limits: honour `Retry-After` on 429, throttle client-side to the documented quota, and document a safe `-parallelism` for large configurations (Terraform defaults to 10 concurrent operations).
- Publish the propagation window you designed for (seconds to low minutes).

## Import and identity

- Every resource supports import. Single-ID resources pass the ID straight through; composite IDs use a documented delimiter grammar shown in the docs examples (`import.sh`, `import-by-string-id.tf`, and `import-by-identity.tf` once identity ships).
- Read must leave a state from which `-generate-config-out` writes valid HCL: never populate both sides of a `ConflictsWith` or `ExactlyOneOf` pair.
- Changing the import ID format is breaking.
- Add resource identity (Terraform and OpenTofu 1.12+) as an addition, never as the only path: older binaries of both still import by ID.
- List resources (Terraform 1.14+) let users discover existing objects and generate configuration in bulk; pair them with identity.

## Schema versions and state moves

- Any change to the stored shape of state (type change, attribute moved into a nested object) needs a schema `Version` bump and a state upgrader.
- Implement an upgrader from every prior released version straight to the current one; the framework does not chain them. Define the prior schema so the upgrader reads typed state, and set the whole new state.
- A missing upgrader for a stored version fails every plan for users on that version.
- Renaming or splitting a resource type: ship the new type, deprecate the old one, and implement a state mover on the new type so users can write a `moved` block (Terraform 1.8+, Plugin Framework only).

## Provider configuration and credentials

- All auth attributes Optional (never Required, which blocks environment variables), secrets Sensitive, no defaults on credentials.
- Precedence, highest first: provider block, environment variables, shared credentials file, platform identity. Resolve secrets as a complete set.
- Guard unknown values on auth attributes (wired from another resource's output), or the provider silently authenticates as the wrong identity.
- Validate credentials eagerly with one cheap identity call at configure time, behind a `skip_credentials_validation` flag; skip it when any credential attribute is unknown at plan.
- Name every source tried and the docs URL when no credentials resolve. Never log secret values.
- Set a `User-Agent` carrying the provider name and version so API logs show provider traffic.

## SDKv2 providers

- Build new providers on the Plugin Framework: HashiCorp recommends it for new functionality, and state moves and newer constructs exist only there.
- Migrating an existing SDKv2 provider: mux both servers in one binary (`tf5to6server` plus `tf6muxserver`), move one resource at a time, and keep provider schemas identical in both servers.
- Migration traps: blocks must stay blocks (nested attributes change HCL syntax); SDKv2 collapsed unset values into zero values, so decide null explicitly; keep every attribute name, type and `id`.
- Prove each migrated resource with the old acceptance tests unchanged plus an upgrade test (apply with the last release, plan with the new build, expect no changes).
- Bump `terraform-plugin-go`, framework, mux, SDKv2 and testing modules together when Terraform core adds protocol RPCs.
