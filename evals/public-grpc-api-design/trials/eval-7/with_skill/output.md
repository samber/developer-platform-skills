❌ **Not clear to launch.** Auth and transport are necessary. They do not close the exposure hole. Two blockers remain, and both are fixable before the 14th.

## Blockers

**1. Five internal RPCs sit on the public service.** The skill's exposure audit (step 7) is mandatory for any internal-first service, and "TLS and auth switched on do not close this hole."

- Your bearer check proves the caller is a valid customer. It does not prove the caller may drain a node.
- Any customer token can currently call these:
  - `DrainNode`: operational outage lever.
  - `SetFeatureFlag`: changes behavior for all tenants.
  - `ReindexShipmentCache`: load and DoS lever.
  - `DumpRuntimeConfig`: likely leaks secrets and topology. Unverified: check what it returns.
  - `DebugEcho`: may echo headers, including the caller's bearer token. Unverified: check.
- ⚠️ Per-method scopes (step 7.4) are only defense in depth. The fix is to take these RPCs off the public contract.

**2. Server reflection is on.**

- Step 7.1 says to disable reflection in production. Once the port is public, reflection lets attackers list every method, including the five above.
- It also leaks any other RPC you forget to remove.
- Staging counts if customers or the internet can reach it. Check that.

## Fix, in order

1. **Split the proto.** Move the five admin and debug RPCs to a separate internal service, ideally its own package and its own listener or port. The public edge never routes to it. About 1-2 hours.
2. Do this before the 14th. After launch, removing an RPC from a public `v1` is a breaking change. Today nobody depends on it.
3. **Disable reflection** in production, and in any externally reachable staging. About 15 minutes.
4. **Keep support's grpcurl workflow** without reflection:
   - Give support a `.protoset` (`buf build -o api.protoset`) or the `.proto` files. They run `grpcurl -protoset api.protoset ...`.
   - Keep reflection on only for the internal admin listener, reachable by VPN or mTLS only.
   - Support's daily workflow survives.
5. **Re-run the audit** on the remaining surface. Confirm the descriptor lists only `CreateShipment`, `GetShipment`, `ListShipments` and `QuoteRate`. Check this with `grpcurl -protoset ... list`, not by trusting the code.

## Pre-launch checks (same skill, not blockers yet)

Status is unknown for each of these. I cannot see your repo or config.

- **Per-method scopes:** is each RPC checked against a token scope? Example: `shipments.read` vs `shipments.write`. Authenticated is not enough.
- **Tenant isolation:** can customer A read customer B's shipment by ID or list? (My addition, not from the skill. It is the most common leak on a service that started internal.)
- **Rate limiting:** over-quota returns `RESOURCE_EXHAUSTED` with a `RetryInfo` detail.
- **Errors:** use `google.rpc.Status`, with specific codes. `DebugInfo` is stripped from `details` before it leaves. Stack traces never appear in `message`.
- **Proto hygiene:**
  - Versioned package, for example `halcyon.freight.v1`.
  - One dedicated Request and Response message per RPC.
  - Enum zero values are `_UNSPECIFIED`.
  - `buf lint` passes.
  - `buf breaking` runs in CI as of this release.
  - If you transcode to JSON, also snapshot the `google.api.http` routes. `buf breaking` does not check them.
- **Streaming:** the four business methods are unary. Enable the `UNARY_RPC` lint so a streaming method cannot slip in.
- **Edge:** if the edge terminates TLS, it must be HTTP/2-aware at L7. An L4 balancer is not acceptable for gRPC. Set client keepalive below the balancer's idle timeout (AWS ALB defaults to 60 s).

## Questions that could change the design

These do not block the go/no-go above. Answer them when you can.

1. Do any customers call from a browser? If yes, raw public gRPC is not enough. Step 6 says put Connect-RPC in front, or transcode to JSON.
2. Are customers SDK users, or will they generate their own stubs from your protos? Raw integrators need the published protos and a stable versioning story. Step 1's gate says dual-publish an HTTP surface unless the audience is control-plane engineers fluent in generated-SDK tooling.
3. Does a public REST API exist that this must stay consistent with?

## Next action

Open the service `.proto` and list every RPC. Move the five admin and debug RPCs into `internal/admin/v1/admin.proto`. Then paste the remaining public RPC list here and I will run the full audit on it.

**Timeline:** about half a day for steps 1-5. That leaves slack before the 14th. ⏳

I read `SKILL.md` and `references/public-grpc-case-studies.md`. I did not open the other two references (`proto-governance-reference.md`, `grpc-error-http-mapping.md`), and the verdict above does not depend on them.