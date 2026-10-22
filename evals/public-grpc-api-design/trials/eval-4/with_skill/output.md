# Review: `almandine.ledger` protos (first cut)

I read the skill and its governance reference. I did not have the proto file itself, so this review covers what you described. Your answers to the questions at the end could change the verdict on gRPC at the public edge and the stable-versus-beta choice.

## Verdict

Do not publish as is. Four findings are blockers: package version, file path, bare-scalar and shared messages, and the enum zero value. Fixing them now costs nothing, because none of it is public yet. After publication each fix would be a breaking change.

## Blockers

### 1. Package and path carry no valid version (AIP-215, AIP-191)
- `almandine.ledger` has no major-version suffix. `buf lint` flags it as `PACKAGE_VERSION_SUFFIX`.
- `ledger/ledger_v1.proto` puts the version in the filename, and the directory doesn't mirror the package.
- Fix: put the file at `almandine/ledger/v1/ledger.proto` with `package almandine.ledger.v1;`.
- Also set `go_package`, `java_package` and the other per-language options, so generated code doesn't leak the raw proto path.

### 2. "v1.2" can't be encoded (AIP-185)
- Public API versions are major-only. The package says `v1`, and the transcoded URL starts `/v1/...`. There is no `v1.2`.
- Marketing can say "Release 1.2", or name SDK and docs releases that way. That label must not appear in the package, URLs or directories.
- "Second iteration" is internal history. For external developers this is the first published `v1`.
- Check what you are promising. `v1` means stable. If the surface may still change shape, publish as `v1beta1`. Shipping beta behavior under `v1` is a review finding in itself.

### 3. `GetEntry(string)` uses a bare scalar (AIP-131)
- Every RPC needs its own `<Method>Request` wrapper. A wrapper can gain fields later without breaking anything. A scalar can't.
- Fix: `rpc GetEntry(GetEntryRequest) returns (LedgerEntry)`, with `string name = 1;` carrying the resource name (AIP-122).

### 4. `LedgerQuery` and `LedgerEntryList` are shared between RPCs
- This violates `RPC_REQUEST_RESPONSE_UNIQUE`. In buf's words, every change to the shared message "ripples across every RPC that references it".
- DRY is the wrong goal for a public contract. `List` and `Search` will diverge. `Search` will want free-text and ranking fields that `List` should never expose.
- Fix: give each RPC its own request and response: `ListEntriesRequest`/`ListEntriesResponse` and `SearchEntriesRequest`/`SearchEntriesResponse`.
- If the shared part is a stable set of filter fields, put them in a nested message that both requests embed. Keep the top-level messages separate.
- Ask whether `SearchEntries` needs to exist. If it only repeats `List` with a filter, drop it and use List with a `filter` field (AIP-132). If it stays, it is a custom method and gets the `:search` suffix (AIP-136).

### 5. `ACTIVE = 0` is the enum zero value
- Every zero value must be `<ENUM>_UNSPECIFIED` (`ENUM_ZERO_VALUE_SUFFIX`). Otherwise an unset field silently reads as `ACTIVE`, which is dangerous on a ledger.
- Values should also carry the enum-name prefix, which buf's `ENUM_VALUE_PREFIX` enforces.
- Fix:
  ```proto
  enum EntryStatus {
    ENTRY_STATUS_UNSPECIFIED = 0;
    ENTRY_STATUS_ACTIVE = 1;
    ENTRY_STATUS_VOIDED = 2;
  }
  ```
- Check for stored or serialized data and internal clients that treat 0 as `ACTIVE`. They need migrating before this ships.

### 6. Removing `legacy_ref` without reserving its tag
- Add `reserved 4; reserved "legacy_ref";` inside `LedgerEntry`. A future developer reusing tag 4 would corrupt old data and old clients.
- Ask whether any external consumer or stored payload ever saw that field. If yes, the removal broke AIP-180 and should have gone through `deprecated = true` first.
- If it was internal only, it is fine. Run `buf breaking` against the last internally tagged commit to confirm.

## Should fix

- **Service name.** `Ledger` should be `LedgerService` (`SERVICE_SUFFIX`).
- **No `google.api.http` annotations.** AIP-127 wants an HTTP mapping on every RPC. For example:
  - `GET /v1/{name=...}` for Get.
  - `GET /v1/...entries` for List.
  - `POST ...entries:search` for Search.
  - `buf breaking` does not check these annotations. Add a CI snapshot diff or a contract test of the routes, or a URL change could pass every gate.
- **Pagination.** `ListEntries` needs `page_size`, `page_token` and `next_page_token`. Adding them later is awkward, and an unbounded ledger list is a production risk.
- **Streaming.** Everything here is unary, which is the right default. Enable the `UNARY_RPC` lint category so a streaming RPC can't slip in later.

## Corrected skeleton

```proto
syntax = "proto3";

package almandine.ledger.v1;

import "google/api/annotations.proto";

option go_package = "…/almandine/ledger/v1;ledgerv1";
option java_package = "com.almandine.ledger.v1";

service LedgerService {
  rpc GetEntry(GetEntryRequest) returns (LedgerEntry) {
    option (google.api.http) = {get: "/v1/{name=…}"};
  }
  rpc ListEntries(ListEntriesRequest) returns (ListEntriesResponse) {
    option (google.api.http) = {get: "/v1/…/entries"};
  }
  // Keep only if it differs from List (free-text, ranking); otherwise drop.
  rpc SearchEntries(SearchEntriesRequest) returns (SearchEntriesResponse) {
    option (google.api.http) = {post: "/v1/…/entries:search" body: "*"};
  }
}

message LedgerEntry {
  reserved 4;
  reserved "legacy_ref";
  string name = 1;
  EntryStatus status = 2; // other fields unchanged
}

message GetEntryRequest { string name = 1; }

message ListEntriesRequest {
  int32 page_size = 1;
  string page_token = 2;
  // filter fields…
}
message ListEntriesResponse {
  repeated LedgerEntry entries = 1;
  string next_page_token = 2;
}

message SearchEntriesRequest { /* search-specific fields */ }
message SearchEntriesResponse { repeated LedgerEntry entries = 1; }
```

The `…` placeholders stand in for your real resource paths and fields, which I haven't seen.

## Gates to add before publishing
1. `buf lint` with STANDARD plus `UNARY_RPC`, as a hard CI check.
2. `buf breaking --against <main>` with the FILE category on every PR.
3. A diff or contract test for the `google.api.http` routes.
4. A cross-version test: old client against new server and new client against old server.

## Questions that could change the design
1. **Is public gRPC the right edge?** Most platforms keep gRPC internal and publish REST or transcoded JSON.
   - Who are the consumers: your own generated SDKs, raw-proto integrators, or browsers?
   - If browsers call this directly, raw public gRPC is out. My default would be Connect-RPC in front.
2. **Does gRPC already run internally?** If so, you must audit the service definition for admin, debug and monitoring RPCs before opening it. Also turn server reflection off in production.
3. **Is there a public REST surface this must stay consistent with?**
4. **Is it `v1` or `v1beta1`?** See finding 2.
5. **Was `legacy_ref` ever visible outside the company?** See finding 6.
6. **What is the ship date, and is this contract shared by several products for years?** This decides how much effort goes into the gateway choice.
7. **Not yet reviewed:** the error model (`google.rpc.Status`, with the HTTP-mapping traps), and auth and TLS (OAuth2 plus per-method scopes). Send me those parts of the design.