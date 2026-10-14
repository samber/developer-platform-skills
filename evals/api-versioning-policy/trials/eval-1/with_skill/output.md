# Ledgerbird API versioning and deprecation policy (draft v0.1)

## Decision for the CTO

**Recommendation: URI major versioning (`/v1/`, `/v2/`), not Stripe-style date-stamped, account-pinned versioning.** The skill's own ranking puts account pinning last on efficiency. It names two conditions that justify it anyway, and Ledgerbird meets neither.

| Promotion condition for pinning | Ledgerbird |
|---|---|
| Breaking changes wanted many times a year | One shipped in the past year, one queued. That is at or under the roughly 2/year health line. |
| A long tail of integrators you can't force to migrate | 40 partners under signed contracts, each with a named technical contact. All are reachable, and a migration deadline can be written into a contract. |

Three more facts weigh against pinning:

- **Cost.** Pinning needs a gate-and-transformer chain, one module per historical breaking change, maintained forever. Stripe built that with a large team.
- **Missing infrastructure.** You have 3 engineers and no per-account configuration infrastructure. The skill notes that having this infrastructure is what makes pinning cheaper than the effort line suggests.
- **Deadline.** The skill says a hard deadline promotes URI. The queued change must land by end of Q1, and a URI version is an afternoon of routing.

The "pinned forever" half also conflicts with what a standing policy needs to do, which is retire old versions. Stripe pays for permanent compatibility with a transformer chain that only grows. With 40 reachable partners you can instead retire versions on a published schedule.

**What the CTO gets from the Stripe model, delivered more cheaply:**

- **Stability.** Each partner stays on its version until a dated, contractual sunset. Nothing changes under them silently.
- **No drift.** There is no unversioned or default-latest path, so a partner never moves unannounced.
- **A future path.** Re-promotion triggers (section 11) say when to revisit pinning, so the decision is recorded rather than closed.

**Alternatives considered:**

- **Shopify-shaped:** quarterly date versions with fall-forward. It fails on enforcement: silent fall-forward on reconciliation data is a financial-correctness risk. It also needs release automation you don't have.
- **GitHub or LinkedIn-shaped:** a date header, required, with a hard 410. It is a reasonable upgrade later, but it adds header machinery for a team that has had one breaking change in a year.

## Assumptions to confirm

I couldn't run the interview, so these are my assumptions. Correct any that are wrong.

1. **Current state.** `/v1` is live and the queued change becomes `/v2`. Is anything already versioned or deprecated today?
2. **Meaning of "land by end of Q1".** I assume it means `/v2` is generally available by end of Q1, not that `/v1` is retired by then. If partners must be off `/v1` by Q1, no notice window in this policy fits, and the contracts decide.
3. **Existing contract language.** I assume your 40 contracts contain no deprecation-notice commitment, or a shorter one. Have legal check before you publish.
4. **Enterprise partners.** Reconciliation partners are probably enterprises with slow change management. I set the default at 24 months for that reason.
5. **Effort.** I assume at most a few engineer-weeks of machinery, with no new account-level infrastructure.

---

# Ledgerbird API versioning and deprecation policy

## 1. Scope

- **Covered:**
  - The REST API, versioned by URI major version.
  - Webhook event schemas. They follow the same breaking-change definition and notice discipline.
  - Error codes. Retiring one counts as a breaking change.
- **Not covered:** [list unversioned or internal endpoints, if any]. These may change at any time. State the carve-out here, up front.
- **Client SDKs** version separately under SemVer. Their policy lives in [SDK policy location].
- **Partner terms.** Partner agreements may set longer or different terms for a specific partner. Where an agreement conflicts with this policy, the agreement governs.

## 2. Version scheme

- **Scheme:** URI major version (`/v1/`, `/v2/`). A new major version is cut only for breaking changes.
- **No unversioned access.** A request without a version segment returns an error. Ledgerbird never serves a default or latest version, because removing an unversioned path later is itself a breaking change.
- **Cadence:** as needed. We plan to cut a new major version at most about twice a year.
- **Account pinning.** A partner stays on the major version it calls until it migrates. Ledgerbird never moves a partner between versions silently.

## 3. Breaking-change definition

**Breaking (requires a new major version):** any change that makes a previously working client fail. This includes:

- Removing or renaming a field, endpoint, or webhook event.
- Changing a field's type.
- Removing an enum value.
- Adding a required request parameter.
- Changing the status code or content type for the same scenario.
- **Payments-specific additions** (confirm with the team):
  - Changing an amount's unit or precision.
  - Changing currency or rounding semantics.
  - Changing the meaning of a reconciliation status.
  - Changing the set of records a given filter returns.

**Non-breaking (ships into the current version):**

- New resources.
- New optional request parameters.
- New response properties.
- Changes to property order.
- Changes to the length or format of opaque strings, including ID formats. Partners must not parse IDs.
- New webhook event types.
- New values in **open enums**. Open enums: [list the enum fields, for example `status` and `reason_code`]. Partners must tolerate unknown values in those fields.

**Not contractual (may change without notice):**

- Message and detail text.
- Ordering of fields and, where unspecified, of list items.
- Response timing.
- [Others.]

**Security exception.** Ledgerbird may patch any supported version for critical security, privacy, or correctness fixes. We notify named technical contacts at the time and describe the change in the changelog.

**No bypass.** A business-motivated change, such as pricing, packaging, or a field removal for cost reasons, follows this process exactly. The pressure to skip it is highest in those cases.

## 4. Support windows

- **Default notice: at least 24 months** from the date a successor version becomes generally available (GA) to that version's sunset date. The clock starts at **successor GA**, not at announcement. Partner contracts may set a different number for a given partner, and that number takes precedence for that partner.
- **Concurrent versions:** at most 2 active major versions.
- **Dates are firm.** Once announced, a sunset date does not move later. A slipped date counts against our measurement target.
- **First application:** `/v2` reaches GA by end of Q1. `/v1` is deprecated from that day and sunsets no earlier than 24 months later, unless a partner agreement says otherwise.

## 5. Deprecation process

Stages are announce, deprecate, sunset, and removal. We never go directly from announcement to removal.

1. **Announce.** Ledgerbird publishes the changelog entry, the migration guide, and the sunset date. Each partner's named technical contact receives a direct email.
2. **Deprecate.** The old version keeps serving while these signals are live:
   - A `Deprecation` header (RFC 9745) on every response.
   - A `Sunset` header (RFC 8594, which is Informational) once the date is firm.
   - `Link: rel="successor-version"` pointing to the replacement.
   - `deprecated: true` in the OpenAPI document.
3. **Targeted outreach.** Headers alone reach no one, so we also email the contacts of accounts still calling the deprecated version at T-12 months, T-6 months, T-3 months, and T-1 month. The final reminders go to contacts and to the account manager.
4. **Migration support.** Ledgerbird owns the migration, not only the announcement. Each transition ships with:
   - A migration guide with concrete steps and a field-by-field mapping.
   - A staging or sandbox `/v2` for testing.
   - A named support channel.
   - A per-partner migration check-in for partners with significant traffic.
5. **Sunset.** The date arrives and enforcement begins (section 6).
6. **Removal.** This happens after the grace period, and only per section 6.

## 6. Enforcement at sunset

- **Hard cutoff, no fall-forward.** After the sunset date, requests to the retired version return `410 Gone` with a descriptive error body and a successor link. We reject silent fall-forward because a reconciliation integration that quietly gets different semantics produces wrong financial data without any error.
- **Grace period:** 30 days of `410 Gone` before the routes are fully removed, so callers get a diagnosable error and not dropped connections.
- **Removal only on observed traffic.** We remove a version only when telemetry shows zero traffic, or a residue we have explicitly accepted. A date passing proves nothing about who migrated.
- **Per-partner extension.** Because every partner is under contract, an extension for a specific partner is a written contract amendment with a date. It is never an informal "we'll leave it on."

## 7. Governance

- **Detection:** an OpenAPI diff tool (for example oasdiff) runs in CI on every spec change and fails on any change matching section 3's breaking list.
- **Approval:** no breaking change ships without sign-off from [named staff engineer] and [product or CTO delegate]. A flagged diff cannot merge without it.
- **Charter:** with 3 engineers, this approval step is the whole governance model. Add a review board only when the surface outgrows one reviewer.
- **Cadence cap.** If a third breaking change is wanted within a year, the approver convenes a short review of whether the compatibility discipline needs fixing before approving it.

## 8. Measurement

- Breaking changes per year. Target: at most 2.
- Deprecated-version traffic share, reviewed monthly during any active deprecation. A flat line after a reminder email means that channel failed.
- Per-partner migration status for the deprecated version. This is the real completion metric, and you can run it by name with 40 partners.
- Slipped sunset dates. Target: 0.

## 9. Exceptions

- The security exception in section 3.
- Per-partner contract amendments, in writing, as in section 6.
- Anything else requires approval from the same sign-off as a breaking change, and the exception is recorded in the changelog.

## 10. Ownership and review

- **Owner:** [name or role].
- **Review:** annually, or after any breaking change.

## 11. Re-promotion triggers (when to revisit date-pinning)

Revisit Stripe-style pinning if two or more of these hold:

- Breaking changes are wanted more than about 4 times a year, or have been shipped quarterly for two consecutive years.
- Partners can no longer be made to migrate. Concretely, more than a handful hold contracts with no migration obligation.
- The platform team has per-account configuration infrastructure and the headcount to maintain a transformer chain.

Until then, the cost buys nothing Ledgerbird needs.

---

## Next steps before publishing

1. Confirm the assumptions above, especially the meaning of "land by end of Q1" and the existing contract language.
2. Have legal check that publishing a 24-month default doesn't conflict with any partner agreement.
3. Fill in the bracketed values: open enums, named approver, owner, unversioned surfaces.
4. Take the Decision section to the CTO. The shortest honest framing is that you are keeping what he liked, which is stability for existing integrators, and declining the cost, which is an ever-growing chain of transformers.

I did not validate this section by section with you as the skill prescribes, because you asked for the complete draft. Treat each section as open to change. If the scheme changes, the support windows must be rechecked.