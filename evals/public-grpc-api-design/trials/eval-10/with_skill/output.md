# Sablefen v2 proto plan: sanity check

All four points have a problem. Two break hard rules, and one of those is permanent. Fix them in this order: **#3, #4, #1, #2**.

## 1. v2 importing v1 messages: ❌ don't

A new major version must not depend on the previous one (AIP-185, step 2 of the skill). Copying the 40 messages is the price of a major version.

- **v1 can never be sunset.** Every v2 consumer's generated code pulls in v1. Deprecating v1 means breaking v2.
- **v1 changes leak into v2.** A v1 fix, deprecation, or `reserved` field changes v2's generated surface.
- **Generated imports tie the packages together.** `buf breaking` FILE checks v1 against `main`, so v2 inherits any file move you make there.

Fix:

- Make `sablefen/catalog/v2/` self-contained. Generate or copy the unchanged messages once, then let them diverge.
- Give every RPC its own `<Method>Request` and `<Method>Response` in v2. Reusing v1's wrappers breaks `RPC_REQUEST_RESPONSE_UNIQUE` in spirit and re-couples the packages.
- Share logic in the server with a v1↔v2 mapping layer. Don't share it in the proto.
- Reference resources by resource name (AIP-122), never by embedding another API's message type.

## 2. Rename `sku_code` to `product_code` and delete three fields: ✅ in v2 only, with five conditions

A rename is remove-and-add, so it is always breaking (AIP-180). That is acceptable in a new major version and not in v1.

- **Leave v1 alone.** If partners need a bridge, add `product_code` to v1 as a new additive field. Mark `sku_code` with `deprecated = true` and an AIP-192 comment saying what replaces it.
- **Reserve the deleted fields.** In v2, `reserved` both the tag numbers and the names of the three removed fields. A later "reuse" would silently corrupt old data.
- **Check "nobody uses" against data.** Look at request logs or gateway metrics, not team memory. Fields in a published proto are used by someone you haven't met.
- **Watch the JSON and URL fallout.** The rename changes the transcoded JSON key (`skuCode` → `productCode`). It also changes any `google.api.http` path or query params, `FieldMask` paths, and filter strings that mention it. `buf breaking` doesn't inspect these, which is the known blind spot. Add the annotation-snapshot diff or a contract test on the transcoded routes.
- **Publish a field mapping table.** Include `sku_code` → `product_code` and the three deletions in the migration guide.

## 3. Shipping the unfinished realtime inventory in `sablefen.catalog.v1`: ❌ the worst item

"Harden it later" is exactly what `v1` forbids. Beta functionality under `v1` is the review finding the skill flags by name.

- **`v1` means stable forever.** Once it's in v1, your own `buf breaking` FILE gate blocks every hardening change. Your only escapes are a v2 break or the "extreme course of action" reserved for security or regulatory needs.
- **Streaming makes it worse.** If "realtime" means a stream, you are locking in an unvalidated call shape on a public surface.

Fix:

1. Ship it as `sablefen.catalog.v1beta1`, or better, a feature package such as `sablefen.inventory.v1beta1`. Either way it is a pre-stable channel and signals that.
2. Refer to products by resource name. Don't import v1 messages, so the beta doesn't pin v1's file layout.
3. State the beta terms in the docs: the API may change, and it can be removed after a deprecation period (180 days is the recommended floor).
4. Graduate it into v2 stable, since v2 is already coming. Hardening then costs nothing in compatibility.

The "second import path" cost is small. Partners adopting v2 already import a second package, and one extra import is cheap next to a frozen API.

Streaming decisions to record (step 4):

- Is it server-streaming? That is the only mode to reach for first. It maps to SSE and Connect.
- Is there a unary Get/List alternative for polling? Add one so the feature is reachable without streaming.
- Do browsers need it? Client and bidi streaming are walled off from browsers over HTTP/1.1.
- Is the edge L7 and HTTP/2-aware, with keepalive below the load balancer's idle timeout?
- If the surface is otherwise unary, enable `UNARY_RPC` lint, or record the exception.

## 4. Changing resource names in v2: ❌ as stated

Stable resources must keep identical resource names across majors, so a v2 client can address what a v1 client created (AIP-185). A reorganized hierarchy that renames them violates that. Anything created through v1 becomes unreachable from v2.

Pick one per resource:

- **Preferred: keep the name format.** Treat the name as an opaque ID. Express the new hierarchy through new fields or relationships, such as a `parent`/`category` reference, or a new resource type.
- **If the hierarchy must move: make it a new resource type.** Give it a new collection and a defined mapping from the old resource. Ship a documented lookup, for example a custom method `:resolveLegacyName`, as an explicit and temporary bridge. Flag this as a conscious deviation from the rule in the design doc.

Whichever you pick:

- The `/v2/` URL segment mirrors the package.
- Test both directions across the boundary: a v1-created resource read through v2, and a v2 client against the v1 server. "Schema parses" is not "RPC succeeds".
- Make the cross-version tests a CI gate. `buf breaking` can't compare v1 against v2 because they are different packages.

## Gates to add (all four must pass)

- `buf breaking --against main` (FILE category) is green on every merge to v1.
- `buf lint` STANDARD is on, plus the `google.api.http` snapshot diff.
- `UNARY_RPC` lint is on, or each streaming method has a recorded tradeoff and (for bidi) a non-streaming alternative.
- Reflection is off in production, and the internal-RPC exposure audit is done before launch.

## Structural checks for v2

- Directory mirrors the package: `sablefen/catalog/v2/`. No version in filenames.
- Set per-language package options such as `java_package`.
- Every enum zero value ends in `_UNSPECIFIED`.
- Each removed field is `reserved`.

## Questions I couldn't answer from your message

These could change the advice above, and I didn't ask them first. Your answers would settle each:

1. Is the surface used by SDK-mediated consumers, raw-proto integrators, or browsers? Browser clients rule out a raw gRPC edge, so you need Connect-RPC or transcoding.
2. Does a public REST surface already exist that v2 must stay consistent with? That raises the stakes on the annotation-diff gate.
3. Is "realtime" a server stream, or push of a different shape? That decides the streaming posture in #3.
4. What is the ship date for v2, and the effort ceiling? Together they decide how much of the migration guide and the cross-version test suite you can build.

I haven't verified anything against your actual protos. This review rests on your four points and the skill's rules.