# Not clear to launch ❌

Transport and authentication are fine, but they aren't the gap. The gap is **authorization**. "Every call requires a valid bearer token" means every customer you onboard can call every method, including the internal ones. A valid token proves who the caller is. It says nothing about whether they may call `DrainNode`.

## Blockers (fix before the 14th)

1. 🔴 **Internal and admin methods are reachable by customers.**
   - `DrainNode` lets a customer take infrastructure out of rotation, which is an outage on demand.
   - `SetFeatureFlag` lets a customer change behavior for every tenant.
   - `ReindexShipmentCache` lets a customer trigger expensive work, which is a cheap denial-of-service.
   - `DumpRuntimeConfig` can leak config and possibly secrets, and the dump is the usual starting point for further attacks.
   - `DebugEcho` is low risk by itself. It still expands the attack surface and shows up in your public API.

   **Fix:** remove these from the customer-facing surface entirely. Put them in a separate proto service (for example `AdminService`) and serve it on a separate listener or port that isn't exposed at the edge, such as an internal-only or VPN-only address. Don't rely on a role check inside the shared endpoint as your only control. If you keep a role check as defense in depth, make it deny by default, so a new method with no policy is rejected.

2. 🔴 **Server reflection exposes the whole API to customers.** With reflection on, any customer can run `grpcurl list` and see every method and message, including the admin ones. That makes the problem above trivial to find and exploit. Your support engineers do need it.

   **Fix:** keep reflection only on the internal listener, or gate it behind an authenticated staff identity. Turn it off on the customer endpoint. Customers get the published `.proto` files or a generated SDK instead. Support can keep using grpcurl against staging and production through the internal path.

3. 🟠 **No evidence of tenant isolation on the business methods.** Authorization means two checks, and the user's description covers neither:
   - Which methods may this caller invoke?
   - Which objects may this caller see? `GetShipment` and `ListShipments` must filter by the token's tenant, and `GetShipment` on another tenant's ID must return not-found or permission-denied.

   An internal service often assumes one trusted tenant, so this is a common hole. Check it with a test that uses two tenants' tokens.

## Also check before launch (not necessarily blockers)

- **Token scopes or claims:** do customer tokens carry anything that distinguishes them from staff or service tokens? If staff and customers share one issuer with no role claim, the fix above needs that claim first.
- **Rate limits and quotas** per tenant, especially on `ListShipments` (pagination caps) and `QuoteRate`. This was never needed for an internal service.
- **Error and log hygiene:** internal errors and stack traces should not reach customers, and logs shouldn't contain bearer tokens.
- **Request limits:** max message size, deadlines, and keepalive settings on the public listener.
- **Audit logging** of admin calls, so you can tell whether anyone has already called them.
- **Production history:** if the endpoint or reflection has been reachable by anyone outside the company, check logs for past calls to the admin methods.

## Minimum path to "clear"

1. Move `DrainNode`, `DumpRuntimeConfig`, `SetFeatureFlag`, `ReindexShipmentCache` and `DebugEcho` to an internal-only service and listener.
2. Disable reflection on the customer listener and keep it on the internal one.
3. Add a negative test: a valid customer token calling each removed method gets `UNIMPLEMENTED` or `PERMISSION_DENIED`, and `grpcurl list` on the public endpoint doesn't show them.
4. Add a cross-tenant test for `GetShipment` and `ListShipments`.
5. Re-run the check against the real public hostname, not just staging.

Steps 1 to 3 are likely small, since splitting a service and adding a second listener is routine. This is a launch-day risk, not a long delay. I haven't reviewed your code or configuration, so this is based only on what you described. If you want, I can look at the gRPC server setup and interceptors to confirm the current behavior.