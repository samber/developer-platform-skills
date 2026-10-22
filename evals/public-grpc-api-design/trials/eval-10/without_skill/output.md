# Sablefen `catalog.v2` plan: sanity check

All four items need changes. Items (1) and (2) contradict each other, and (3) is the riskiest.

## Summary

| # | Item | Verdict | Fix |
|---|------|---------|-----|
| 1 | v2 imports v1 messages | ❌ | Copy the 40 messages into v2 |
| 2 | `sku_code` → `product_code`, delete 3 fields | ⚠️ | Fine inside v2, but verify the semantics and the usage data, and reserve the removed fields |
| 3 | Ship unbaked realtime inventory in v1 | 🔴 | Ship it in `v1beta1` instead |
| 4 | Resource names change | ⚠️ | Needs a translation layer and a migration plan |

## (1) Importing v1 types into v2 ❌

**It contradicts (2) and (4).** An imported v1 message keeps its v1 shape.
- It still has `sku_code`, so the rename isn't "across the board".
- It still has the three fields you meant to delete.
- Its `google.api.resource` / `resource_reference` annotations and `name` pattern docs still describe the v1 hierarchy.
- A v2 message that nests an imported v1 message drags all of that in transitively.

**It couples v2's lifecycle to v1's.** You can't remove or evolve v1 without breaking v2. Sunsetting v1 becomes impossible, because deleting `catalog/v1/*.proto` breaks every v2 consumer. Any additive v1 change, including (3), leaks into v2 automatically.

**It leaks across languages.** Go, Java and TS consumers of v2 must also generate and vendor v1. Package-per-version lint rules and per-package `buf breaking` checks become harder to reason about.

**Fix:**
- Make v2 self-contained. Copy the 40 messages with a script, then apply the rename and deletions in one reviewed pass. It's mechanical and cheap.
- If some types are truly version-neutral leaves (`Money`, `Timestamp`-like wrappers, pagination), move them to something like `sablefen.common.v1`. Don't do this for catalog entities.
- Write a v1↔v2 conversion layer in the server. Don't rely on shared Go types between versions.

## (2) Rename and deletions ⚠️

Both are fine in a new package, since v2 has no compatibility obligation to v1. Check these first:

1. **Confirm `sku_code` and `product_code` mean the same thing.** In many catalogs a product has many SKUs. If so, "for clarity" makes it less clear, or wrong. If they differ semantically, do not rename.
2. **Verify "nobody uses" the three fields with data.** Check server request and response logs across partners, not just your own clients. Partners may read fields you don't know about.
3. **Reserve the deleted fields.** Use `reserved <numbers>; reserved "<names>";` in v2. Do this if v2 shares field numbers with v1 or may be bridged to it on the wire. Never reuse those numbers.
4. **Keep field numbers stable for renamed fields** if you want a gateway or transcoder to bridge v1 and v2 cheaply. The rename is wire-compatible but changes the JSON name (`skuCode` → `productCode`) and generated identifiers.
5. **Check string-typed references to field names.** Field masks, `filter`, `order_by` expressions, error details and docs all name fields as strings. The compiler won't catch these and they break silently.
6. **Publish a mapping table.** Include old name, new name, and removed fields with their replacements, in the migration guide.

## (3) Shipping unbaked realtime inventory in v1 🔴

**Don't.** v1 is a stable contract, and everything you add to it is permanent.
- Under `buf breaking` (WIRE/FILE rules), you can't remove or reshape it later. "Harden later" really means either a v1 breaking change or a permanent wart.
- Partners will build against it immediately, which is exactly why they're asking.
- It will have to be carried into v2, or the two versions diverge. With plan (1), v2 would inherit the unbaked messages automatically.
- It also extends v1's life. New features on v1 give partners a reason to stay.

**The "second import path" cost is small.** It's one extra import line. A permanent API commitment is expensive by comparison.

**Fix, best first:**
1. Ship it as `sablefen.catalog.v1beta1` or `sablefen.inventory.v1beta1`. Follow AIP-181 stability levels: alpha and beta packages may break, and the docs say so.
2. Graduate it into `catalog.v2` (or a stable `inventory.v1`) once it's hardened. Put the beta-to-stable promise and a rough timeline in the docs.
3. If you refuse a separate package, at minimum put it in its own file and service, mark it `experimental` in comments and options, and get partners to acknowledge in writing that it may break. This is weaker, because a mark in v1 doesn't stop `buf breaking` from blocking you.

## (4) Resource name changes ⚠️

Resource names are identifiers that partners persist in their databases, caches and logs. Changing the hierarchy changes every one of those identifiers.

**Fix:**
- Keep the leaf ID stable across versions. Only the parent path should change.
- Ship a deterministic v1-name → v2-name mapping, documented and implemented in the server.
- Make v2 accept legacy v1 names on lookup during a transition window, or provide a batch translation RPC. Otherwise partners must re-crawl everything.
- Update the `resource` patterns, `resource_reference` annotations, and the `parent` and `name` doc strings in v2. This is one more reason not to import v1 types (item 1).
- Decide whether v1 and v2 are two views over the same data or two migrated datasets. Writes through v1 must be visible in v2, and the other way round.
- Check cross-references that embed names, such as order lines pointing to products, to make sure none still carries a v1-style path.

## Missing from the plan

- **A v1 deprecation and sunset timeline,** with usage telemetry per partner and a date partners can plan around.
- **A migration guide:** the rename table, the name mapping, removed fields, and before/after examples.
- **An alpha period for v2.** Consider `v2alpha1` or `v2beta1` first, so partners can try the rename and hierarchy change before it freezes.
- **Both versions served concurrently** from one backend, with `buf breaking` enforced per package and v1 frozen to bug fixes only.
- **Language packaging:** distinct `go_package`, `java_package` and similar options per version, so v1 and v2 can coexist in one binary.

## Suggested order

1. Confirm the SKU/product semantics, and pull usage data for the three fields to delete.
2. Ship realtime inventory as `v1beta1` this month. This is the only time-sensitive item.
3. Scaffold a self-contained `catalog.v2alpha1` by copy, with the rename, deletions, `reserved` entries and new resource patterns.
4. Build the v1↔v2 server conversion and name translation.
5. Publish the migration guide and sunset dates, then promote to `v2`.

I haven't seen your actual `.proto` files, so I'm assuming a standard `buf` and AIP-style setup. If any of these assumptions are wrong, for example there's no resource-name annotations or you don't run `buf breaking`, parts of (1) and (4) soften. The conclusions on (1) through (3) hold either way.