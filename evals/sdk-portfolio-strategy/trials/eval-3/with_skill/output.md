# Bellwether Analytics: SDK versioning and runtime policy for API v3

**Verdict:** the plan half holds. Cut 3.0.0 as a major: the SDK surface really breaks. Do not make "SDK major = API major, same day, all five" the policy. Do not bundle the runtime drops into that release without checking telemetry first.

I followed `sdk-portfolio-strategy`, steps 5 and 6 mainly. Its interview would normally ask nine questions one at a time. You asked for the deliverable directly, so I made assumptions and list them at the end.

## 1. What holds, what doesn't

| Part of the plan | Verdict | Why |
|---|---|---|
| 3.0.0 is a major bump | ✅ Holds | New auth changes client construction. New pagination changes the return types of every list call. Both are breaking changes to the SDK's own surface, so a major is correct. |
| Same version number "so nobody gets confused" | ❌ Wrong tool | A published mapping table prevents the confusion. Lockstep numbering only hides it, and it creates the problems below. |
| All five GA on API-flip day | ⚠️ Good goal, bad promise | It's good for integrators. As a hard rule it lets the slowest language gate the other four, in a 5-week window. |
| Drop Node 16 and Go 1.21 | ✅ Defensible, ⚠️ not as a one-off | Both are long past upstream end-of-life. But two ad-hoc drops mean no runtime policy for Python, Java and Ruby. |
| Bundle runtime drops with the auth and pagination break | ⚠️ Check first | Anyone on Node 16 or Go 1.21 can't use API v3 until they upgrade their runtime as well. |

### Problems with lockstep numbering

1. **A future SDK-only break forces a choice.** Say the Go SDK renames a method after launch. Either Go becomes 4.0.0 and the numbers diverge, or all five bump to 4.0.0 and four of them break integrators for nothing.
2. **API v4 forces an SDK major.** The reverse of problem 1: a non-breaking API change would still force every SDK to bump just to keep the numbers aligned.
3. **The 2.x line gets orphaned.** If SDK major tracks API major, 2.x has no defined life beyond "the old one."
4. **Slip risk.** If Ruby isn't ready on flip day, you either delay the API or break the number alignment publicly.

The SDK skill's rule: bump an SDK major only when the SDK's own surface breaks, never merely because the API released a new version. This time both happen together, so you'll probably end up with five 3.0.0s anyway. The policy just must not promise that.

## 2. Policy to write down

### Policy A: SDK package version

- Each SDK uses SemVer, per package.
- A major bump happens only when that SDK's public surface breaks (renamed method, changed constructor, changed return type).
- An API version change never forces an SDK major. An SDK major never requires an API change.
- Language SDKs may have different version numbers over time. The mapping table (Policy C) is the source of truth.

### Policy B: API version

- Owned by the API versioning policy (`api-versioning-policy`), not this document.
- Record only the boundary: **SDK 2.x speaks API v2. SDK 3.x speaks API v3 only.**
- SDK 3.x does not auto-detect or fall back to v2.

### Policy C: Mapping table

Publish it on the docs site and in each README. Update it on every release.

| SDK major | API version | Status |
|---|---|---|
| 3.x (Python, Node, Go, Java, Ruby) | v3 | Active |
| 2.x (Python, Node, Go, Java, Ruby) | v2 | Maintenance (see Policy E) |

Per-language rows are needed the moment a language's version diverges.

### Policy D: Runtime support window

This is the one new thing to write. Proposed, self-set rule (not copied from a vendor):

- Each SDK supports every host-language version still supported upstream when the SDK releases.
- It also supports versions up to **12 months past upstream end-of-life**, the low end of Stripe's documented 1 to 2 year extended window.
- Runtime drops happen **only in a SDK major**, never in a minor or patch.
- Announce every drop at least one minor release ahead, in the changelog and the README.
- Never drop a runtime that still carries more than a set share of that SDK's traffic without a decision on file (see section 3).

Consequences of this rule, from upstream lifecycles as I know them. Verify the dates before publishing:

- **Node 16:** end-of-life September 2023. Dropped.
- **Node 18:** end-of-life April 2025. Also dropped under a 12-month window, which goes beyond what you asked.
- **Node 20:** end-of-life April 2026. Still supported until April 2027.
- **Go 1.21:** unsupported upstream since 2024. Dropped.

You didn't mention Node 18, so decide deliberately: keep it (needs a longer grace) or drop it with Node 16.

For Python, Java and Ruby, apply the same rule. For Java, state the floor in terms of LTS releases. Also record the minimums that 2.4.x currently declares, so nobody drops a runtime by accident.

### Policy E: 2.x lifecycle

- **Support commitment:** security and critical fixes only, no new features.
- **End-of-support date:** never earlier than the API v2 sunset date, which is owned by the API versioning policy.
- **Floors to check against:** at least 12 months of maintenance after 3.0 GA (Azure's floor), and a public announcement at least 6 months before maintenance ends (AWS). These are floors from other vendors, not a standard.
- **No silent archive:** follow the sequence: final release, announcement, archive.
- Ship a final 2.x release before launch that adds deprecation warnings pointing to the migration guide. Do this inside the 5-week window.

### Policy F: Release cadence

- Release on change, with no fixed monthly train. The coordinated v3 launch is a one-time event, not a cadence.
- Don't publish releases just to keep a rhythm.

### Policy G: Launch coordination

Coordinate **availability**, not **numbers**.

- Target: all five 3.0.0 packages on registries at API v3 GA.
- Publish release candidates (`3.0.0-rc.N`) against a v3 preview or sandbox as early as it exists. If none exists, build one. It gives integrators something to test in the 5 weeks, and it surfaces auth and pagination problems before GA.
- If a language isn't ready, the API still flips. That language's row in the mapping table reads "3.x pending" with a date, and 2.x keeps working against v2 until the sunset date.

## 3. Before you commit: three checks

1. **Traffic by runtime.** Do you have `User-Agent` or SDK-header telemetry? The skill treats this as the evidence base. Find the share of requests coming from Node 16 and from Go 1.21 SDKs. If it's low single digits, drop them in 3.0 as planned. If it's material, ship the 3.0 majors first and drop the runtimes in a later major, so integrators don't take two migrations at once.
2. **Customers who can't upgrade.** Check whether named accounts sit on Node 16 or Go 1.21. They'd be locked out of API v3 entirely, with only the v2 sunset date to protect them.
3. **Spec and build model.** Does a generator produce the SDKs, or are they handwritten? This decides whether five languages in 5 weeks is realistic.

## 4. Five-week sequence

1. **Week 1:** record runtime minimums from 2.4.x, pull telemetry, decide the Node 18 question, publish the mapping table skeleton.
2. **Weeks 1 to 2:** write the migration guide (auth, pagination, runtime changes).
3. **Weeks 2 to 3:** cut the final 2.x release with deprecation warnings, and the first `3.0.0-rc.1` against v3 preview.
4. **Week 4:** release candidates in all five languages, with integrator feedback.
5. **Week 5:** go/no-go per language, then GA together with the API flip.

## 5. Assumptions I made

- All five SDKs are official and in-house, and the five-language set doesn't change in this release.
- The API versioning policy and v2 sunset date exist or will be decided elsewhere. I didn't invent a date.
- Upstream end-of-life dates above come from my own knowledge, not a live lookup. Verify them before publishing.
- The 12-month grace and the 12-month 2.x floor are my proposals. Change them if your support capacity says otherwise.

## 6. Questions for you

1. Do you have SDK telemetry, and what share of traffic is on Node 16 and Go 1.21?
2. Are the SDKs generated or handwritten?
3. Does a v3 sandbox exist for release candidates?
4. When is the API v2 sunset?
5. Keep or drop Node 18?