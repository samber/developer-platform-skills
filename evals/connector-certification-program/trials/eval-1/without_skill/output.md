# Ferrowell connector certification: v2 design

## 1. Diagnosis

The two v5 breakages and the support tickets point to four root causes. Neither of the VP's fixes addresses any of them.

| Cause | Evidence |
|---|---|
| Verified is a point-in-time opinion | A one-time call, no expiry, no re-test when the API changes |
| Verified is not tied to API compatibility | Two Verified connectors broke on v5 and nothing flagged it first |
| Verified does not say who supports what | Customers assumed Ferrowell supports it, so tickets came to you |
| Gold auto-Verified decouples the badge from quality | Verified follows partner-sourced revenue, not review |

## 2. Why I recommend against the two VP proposals as written

**1,000 MAU before GA**
- It tests popularity, not reliability. Neither of the two broken connectors would have been caught by it.
- It is a chicken-and-egg gate. Connectors need GA visibility to get users. Niche connectors (a vertical ERP, a regional payments tool) may never reach 1,000 and can still be excellent.
- It pushes partners toward gaming MAU, or toward keeping connectors in beta forever, where customers still install them.
- Keep usage as a signal. Use it to rank review capacity and to earn a "Popular" label. Never use it as a quality gate.

**Verified mandatory for every connector**
- It dilutes the badge. If every connector is Verified, the badge means nothing, and it will carry the same "you support this" assumption on all 85.
- It cannot scale. A review call per connector, plus re-review, will exceed your solutions team's capacity.
- It makes the failure mode worse. Today two Verified connectors broke and you got the tickets. Mandatory Verified would make that every connector.
- What the VP is trying to solve (customers can't tell what is safe or who supports it) is real. The fix is a mandatory **baseline** plus a **meaningful, expiring** Verified. See below.

## 3. The design: three levels

### Level 1: Listed (mandatory for every connector in the catalog)

Everything in the catalog meets this. It is automated, so it scales.

- Named partner support contact and a public support channel on the listing.
- Listing text states plainly: "Built and supported by [Partner]. Ferrowell supports the platform, not this connector."
- Automated contract tests run nightly against the current API version.
- Declared API versions supported, shown on the listing.
- Security baseline: OAuth/secret handling checklist, signed partner agreement.
- Auto-delist path: contract tests failing for 14 days, or an unreachable support contact, moves the connector to "Unmaintained" (hidden from search, existing installs keep working).

### Level 2: Verified (earned, expiring, opt-in)

Verified means "Ferrowell reviewed this, tested it continuously, and the partner has a contractual response commitment." It does not mean Ferrowell supports it.

Requirements, in addition to Listed:
1. Solutions-team review: security, error handling, rate limits, data handling.
2. Contract test coverage above an agreed threshold, with a pass-rate floor (for example 99% over the trailing 30 days).
3. Partner support SLA: a first response time (for example 1 business day for P1) and a published escalation path.
4. API-change commitment:
   - The partner joins the sandbox and beta for each new API version.
   - The connector passes contract tests on the new version before that version goes GA.
   - The partner ships a fix within an agreed window for any breaking change Ferrowell announced with the notice period below.
5. **Expiry:** Verified lasts 12 months and re-verifies automatically if contract tests pass. It is suspended (not revoked) on any major API version until the connector passes again.
6. **Automatic suspension:** if contract tests fail for 7 days, the badge shows "Verification lapsed" until fixed.

### Level 3: Ferrowell-supported (optional, scarce)

Reserved for connectors Ferrowell maintains or contractually supports. Only these tickets are owned by Ferrowell support. Start with zero or a handful. It gives you a clear answer to "who do I call", and it stops Verified from carrying that meaning.

### Gold partners

- Remove automatic Verified. Gold becomes a commercial tier, not a quality tier.
- Gold benefits instead: a priority review queue, a named solutions contact, and co-marketing. Gold connectors pass the same Verified bar.
- Honest risk: Gold partners will see this as losing a benefit. Offer a 90-day grace period (section 6) and a faster review lane as the trade.

## 4. GA criteria (replaces the MAU gate)

Stages: **Beta → GA**.

| GA gate | Threshold (starting point, tune after 2 quarters) |
|---|---|
| Contract tests | Pass on current API version, coverage threshold met |
| Production exposure | Running in at least 5 distinct customer tenants for 30 days (beta) |
| Error rate | Below a set threshold in those tenants |
| Support | Named contact, tested once with a real ticket |
| Docs | Setup, auth, limits, and known issues published |
| Security | Baseline checklist complete |

The "5 tenants" figure is a floor to show real-world exposure, not a popularity test. Adjust it if your tenant base is small. If your platform data shows it excludes legitimate niche connectors, lower it rather than raising MAU.

## 5. API change management (the actual v5 fix)

- **Notice:** 90 days of sandbox and beta access before any breaking API version reaches GA.
- **Compat dashboard:** each connector shows pass/fail against the upcoming version. Share it with partners from day one of the beta.
- **Release gate:** do not move customers to a new version by default until Verified connectors covering a set share of installs pass. Define the share (for example 90%).
- **Customer protection:** customers stay pinned to the old version for connectors that haven't passed, until sunset.
- **Post-mortem on the two broken connectors:** find out which of the four causes in section 1 applied to each. This tells you whether the notice period or the test coverage was the gap. I don't have this data, so treat the thresholds above as a starting point.

## 6. Transition plan for the existing 85 connectors

| When | Action |
|---|---|
| Week 0-2 | Announce the model to partners. Rename the current badge's meaning: clarify the support statement on all listings immediately. This costs nothing and cuts ticket confusion first. |
| Week 2-6 | Onboard all 85 to Listed via automated checks. Ranked by install count, since roughly half of all installs sit in these connectors. |
| Week 4-12 | Re-review all currently Verified connectors, including Gold auto-Verified, highest installs first. Show "Verification under review" for any not yet re-reviewed after day 90. |
| Week 12+ | Opening of Verified applications for any Listed connector. |

Review capacity is the constraint. Estimate it before committing to the dates: reviews × hours per review ÷ team hours per week. If it doesn't fit, review by install rank and let lower-install connectors stay at Listed longer.

## 7. Customer and support changes

- Listing page shows level, supporting party, API versions tested, and last test date.
- Support intake form: if the ticket is about a partner connector, route to the partner contact automatically and tell the customer who owns it. Ferrowell keeps platform issues.
- Add a "connector" field to tickets so you can measure misrouted tickets.

## 8. Metrics

- Tickets about partner connectors that Ferrowell had to redirect (target: down 70% in two quarters).
- Share of installs on Verified connectors with passing tests.
- Verified connectors that lapse on a new API version.
- Time from API beta to Verified compatibility.
- Partner reviews completed versus capacity.

## 9. What to tell your VP

- Both ideas aim at the right outcome: customers should know what is trustworthy. Neither would have stopped the v5 breakage.
- A mandatory baseline for everything, and a Verified that is earned, tested continuously, and expires, achieves the goal without overloading the team.
- Offer to run both models against the v5 incident in a one-page comparison if the VP wants evidence.

## Open questions to answer before launch

1. How many connectors are currently Verified, and how many of those are Gold auto-Verified?
2. Can your platform measure per-connector error rate and per-tenant exposure today?
3. Do partner agreements allow you to impose SLAs and delisting, or do contracts need amending?
4. What is your solutions team's real weekly review capacity?
5. Do you want a Level 3 at all, or is it premature?