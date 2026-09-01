# Proto governance reference

Detail behind SKILL.md steps 2-3. Sources: google.aip.dev (AIP-121, 127, 180, 181, 185, 191, 192, 215), buf.build documentation, and the buf breaking/lint rule sets.

## AIP file and package rules (step 2 detail)

**Package ↔ directory mirror (AIP-191, AIP-215):**

| Rule                          | Correct                                           | Violation                                                |
| ----------------------------- | ------------------------------------------------- | -------------------------------------------------------- |
| Package ends in major version | `example.library.v1`                              | `example.library`                                        |
| Directory mirrors package     | `example/library/v1/book.proto`                   | `example/library/book_v1.proto`                          |
| No version in filename        | `book.proto` inside `v1/`                         | `v1.proto`, `library_v1beta1.proto`                      |
| Per-language options set      | `option java_package = "com.example.library.v1";` | option omitted, raw proto path leaks into generated code |

The api-linter's `proto-package` check fails a directory with a version segment whose package misses it, and vice versa.

**File content ordering (AIP-191):** file-level order, blank line between blocks:

1. Copyright/license notice.
2. `syntax` statement.
3. `package` statement.
4. Imports (alphabetical).
5. File-level options.
6. Service definitions.

Within a file:

- Standard methods before custom methods.
- Parent resources before child resources.
- Request/response messages follow their methods in the same order.

**Resource orientation (AIP-121, 131, 132, 136):** model the API as named resources in a collection hierarchy, exposed through the standard methods List, Get, Create, Update, Delete. A custom method uses the `:verb` suffix on the transcoded surface (`POST /v1/videos:process`) and is justified only when no standard method fits. Reference another resource by its resource name (AIP-122), never by embedding another API's message type inline - inlining tangles the generated client's dependency graph across API boundaries.

**Version semantics (AIP-185):** major version only - `v1`, never `v1.0` or `v1.4.2`; Google APIs expose no minor/patch segment. `v1` is reserved for the stable channel; `v1beta1`/`v1alpha1` are pre-stable channels. Mirror the version as the first URI path segment of the transcoded surface.

## buf lint rules that operationalize the conventions

The STANDARD lint set turns the AIP style rules into CI checks - cite the rule name in review findings:

| Rule                                                       | Enforces                                                                                                                                                                      |
| ---------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `PACKAGE_VERSION_SUFFIX`                                   | last package component matches `v\d+`, `v\d+beta\d*`, etc.                                                                                                                    |
| `SERVICE_SUFFIX`                                           | service names end in `Service`                                                                                                                                                |
| `RPC_REQUEST_STANDARD_NAME` / `RPC_RESPONSE_STANDARD_NAME` | each RPC has `<Method>Request` / `<Method>Response` wrappers                                                                                                                  |
| `RPC_REQUEST_RESPONSE_UNIQUE`                              | no message shared between RPCs - "sharing a Protobuf message between RPCs means every change to that message ripples across every RPC that references it" (buf's own wording) |
| `ENUM_ZERO_VALUE_SUFFIX`                                   | every enum zero value ends in `_UNSPECIFIED`                                                                                                                                  |
| `UNARY_RPC` (opt-in category)                              | forbids streaming RPCs - enable once the surface commits to unary-only (SKILL.md step 4)                                                                                      |

## buf breaking mechanics (step 3 detail)

`buf breaking` diffs the current schema against a reference (Git branch/tag, BSR module, tarball, or Buf image) and fails on incompatible changes. Buf ships over 40 lint rules and 50 breaking-change rules in opinionated default sets; CI wiring is `buf breaking --against <ref>` per PR via the official `bufbuild/buf-action`.

**Four rule categories, strictest first** (a stricter category implies every looser one):

1. **FILE** - generated-code breakage per file; the default, and the right choice for a public surface. Matters for languages with file-specific generated imports (C++, Python).
2. **PACKAGE** - generated-code breakage per package; forgives moving a definition between files within one package.
3. **WIRE_JSON** - binary wire format or JSON encoding breakage.
4. **WIRE** - binary wire format only.

**AIP-180 traps the tooling catches that reviewers miss:**

- An existing component must not be removed within a major version.
- "Renaming a component is semantically equivalent to remove and add" - a rename is always breaking, never a safe refactor.
- Moving a field into or out of a `oneof` breaks generated Go stubs specifically.
- Moving a message to a different file breaks generated imports - the file path is part of the generated-code contract, which is why teams reorganizing protos "for readability" break consumers.

**The blind spot, restated precisely:** breaking-change detection does not work on changes to custom options like `google.api.http`. The transcoding annotations defining the public HTTP mapping are not compatibility-checked at all - the dedicated annotation check in SKILL.md step 3.3 is the only gate covering them.

**BSR review flow:** with instance-wide breaking-change enforcement on, a non-compliant push enters a review queue where repository owners approve or reject before it lands - a paper trail of schema evolution, plus notifications and a safe revert path. Direct Protobuf analogue of Confluent Schema Registry's compatibility modes for Avro/Kafka. Non-buf alternative: Salesforce's `proto-backwards-compat-maven-plugin`, checking against a committed `proto.lock` file.

## Version evolution and deprecation

**Two legitimate evolution strategies (AIP-185):** channel-based (long-lived `v1beta1`/`v1` channels updated in place) and release-based (increment `v1beta1` → `v1beta2` for an incompatible beta-only change). Constraints either way: a new major version must not depend on a previous major version of the same API, and stable resources keep identical resource names across majors so a v2 client can address a resource a v1 client created.

**Deprecation mechanics (AIP-181, AIP-192):** the `deprecated = true` option is available on messages, enums, enum values, and services (since protobuf 2.6.0), not just fields - Java emits `@Deprecated`, C++ clang-tidy warns on use. AIP-192 additionally requires a deprecation comment on every deprecated component stating why and what to use instead, so generated docs explain the replacement rather than just flagging staleness.

**Channel-differentiated sunset expectations:**

- Alpha may be removed without notice.
- Beta may be removed after a deprecation period with 180 days as the recommended floor.
- An in-place breaking change to a _stable_ component is "an extreme course of action" reserved for security or regulatory necessity, never routine.

Concrete notice windows and sunset communication for your own program are `samber/developer-platform-skills@api-versioning-policy`'s territory; these channel semantics are what that policy plugs into for gRPC.
