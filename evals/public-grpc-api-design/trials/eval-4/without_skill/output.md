# Review: `almandine.ledger` v1 proto

I reviewed only what you pasted. I haven't seen the `LedgerEntry` or `LedgerQuery` bodies, and I haven't run `buf` or `protoc`. The findings below come from reading the snippet.

## Blockers (fix before publishing)

1. ❌ **`GetEntry(string)` won't compile.** An RPC must take and return a message, not a scalar. Wrap it as `GetEntryRequest { string id = 1; }`. The wrapper also lets you add fields later, such as a field mask or a revision, without breaking clients.

2. ❌ **`legacy_ref` (tag 4) needs `reserved`.** Dropping the field is not enough. Add `reserved 4; reserved "legacy_ref";` inside the message. Without it, someone will reuse tag 4 and old clients or stored rows will decode garbage into the new field. A ledger probably persists serialized data, so this matters more here than usual. If `legacy_ref` ever shipped to any consumer, run `buf breaking` against the last published version and treat the removal as breaking.

3. ❌ **The enum's zero value is `ACTIVE`.** Proto3 treats an unset field as 0, so an entry or a filter with no status reads as ACTIVE. For a ledger that is risky, and a query can no longer express "any status". Use:
   ```proto
   enum EntryStatus {
     ENTRY_STATUS_UNSPECIFIED = 0;
     ENTRY_STATUS_ACTIVE = 1;
     ENTRY_STATUS_VOIDED = 2;
   }
   ```
   Enum value names are scoped to the package, not the enum, so a bare `ACTIVE` will collide with the next enum that uses it. Renumbering is only free before release.

4. ❌ **Package and path don't match, and there's no version.** The package is `almandine.ledger` but the file is `ledger/ledger_v1.proto`. Proto files should live at `almandine/ledger/v1/ledger.proto` with `package almandine.ledger.v1;`. The package is part of the wire identity (`/almandine.ledger.Ledger/GetEntry`). Changing it after release breaks every client.

## Decisions

5. ⚠️ **Marketing's "v1.2" doesn't go in the proto.** `v1` in the package is the API major version. It changes only on a breaking change, and it stays `v1` across every compatible release. Brand the release v1.2 in the git tag, changelog, docs and SDK versions. Don't encode it in the package, the filename or message names. A `v1_2` package would fork the wire contract for a naming reason.

6. ⚠️ **Don't share `LedgerQuery` between the two RPCs.** Reusing it is DRY in text but couples the two contracts. Search will want free-text, ranking or highlight options, and List will want ordering and pagination. Any field you add for one then shows up on the other. Both RPCs also return a shared `LedgerEntryList`, so they can only evolve together. `buf lint` flags this with `RPC_REQUEST_RESPONSE_UNIQUE` and `RPC_REQUEST_STANDARD_NAME`.
   - To keep it DRY, put the shared filters in a `LedgerFilter` message and embed it in both requests.
   - If the two RPCs really are identical, one of them is redundant. Drop one.

7. ⚠️ **List needs pagination now.** A response that returns every entry is unbounded for a ledger. Add `page_size` and `page_token` to the request and `next_page_token` to the response. Adding them later is wire-compatible but changes behavior for existing callers.

8. ℹ️ **Lint nits:**
   - Service `Ledger` should be `LedgerService` (`SERVICE_SUFFIX`).
   - Add `option go_package` and the other language options.
   - Mark the read RPCs `option idempotency_level = NO_SIDE_EFFECTS;`.

## Things to check in the messages I haven't seen

- ⚠️ Money must not be `double` or `float`. Use `int64` minor units plus a currency code, or `google.type.Money`.
- ℹ️ Timestamps should be `google.protobuf.Timestamp`.
- ℹ️ Check that `LedgerEntry` has no raw-string status field that duplicates `EntryStatus`.

## Suggested shape

```proto
syntax = "proto3";

package almandine.ledger.v1;

import "google/protobuf/timestamp.proto";

option go_package = "github.com/almandine/ledger/gen/ledger/v1;ledgerv1";

service LedgerService {
  rpc GetEntry(GetEntryRequest) returns (GetEntryResponse) {
    option idempotency_level = NO_SIDE_EFFECTS;
  }
  rpc ListEntries(ListEntriesRequest) returns (ListEntriesResponse) {
    option idempotency_level = NO_SIDE_EFFECTS;
  }
  rpc SearchEntries(SearchEntriesRequest) returns (SearchEntriesResponse) {
    option idempotency_level = NO_SIDE_EFFECTS;
  }
}

enum EntryStatus {
  ENTRY_STATUS_UNSPECIFIED = 0;
  ENTRY_STATUS_ACTIVE = 1;
  ENTRY_STATUS_VOIDED = 2;
}

// Filters shared by List and Search. Embedded, so each RPC can evolve its own request.
message LedgerFilter {
  EntryStatus status = 1; // UNSPECIFIED = any status
  // ...your existing LedgerQuery filter fields
}

message GetEntryRequest  { string id = 1; }
message GetEntryResponse { LedgerEntry entry = 1; }

message ListEntriesRequest {
  LedgerFilter filter = 1;
  int32 page_size = 2;
  string page_token = 3;
}
message ListEntriesResponse {
  repeated LedgerEntry entries = 1;
  string next_page_token = 2;
}

message SearchEntriesRequest {
  LedgerFilter filter = 1;
  string text = 2;
  int32 page_size = 3;
  string page_token = 4;
}
message SearchEntriesResponse {
  repeated LedgerEntry entries = 1;
  string next_page_token = 2;
}

message LedgerEntry {
  reserved 4;
  reserved "legacy_ref";
  // ...existing fields
}
```

## Before you ship

1. Move the file to `almandine/ledger/v1/ledger.proto`.
2. Add a `buf.yaml` with the `STANDARD` lint rules and run `buf lint`.
3. Run `buf breaking --against <last published tag>` if anything has shipped.
4. Tag the release `v1.2.0` in git.