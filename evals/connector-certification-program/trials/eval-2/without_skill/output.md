# Pellucid Connector Certification Program: Design v1

## 1. Recommendation

1. **Build the three levels (Bronze, Silver, Gold), but size them to the real population.** Right now that is 11 community connectors with a few dozen installs. Nobody has asked for this, so the program should be cheap, automated, and reviewed against evidence.
2. **Run the 38 first-party connectors through the same test suite.** They cover 92% of installs. If only the 11 niche connectors carry a badge, the badge will mostly mark the connectors almost nobody uses. First-party connectors get a Gold-equivalent label once they pass. This is the one real strategic choice in the design (see §8).
3. **Define each level by what is tested and what Pellucid promises.** The level never depends on who the partner is or whether they pay. A badge that can't be traced to tests is the main way programs like this lose credibility.
4. **Ship by 31 March 2027** (end of next quarter) with a 90-day review gate after launch.

## 2. Goals and non-goals

**Goals**
- Give customers a trust signal for connectors they install.
- Give community maintainers a clear path from "works" to "Pellucid stands behind it".
- Reuse the same conformance suite for first-party release gating.
- Answer the CEO's competitive concern with a real, defensible badge.

**Non-goals (v1)**
- No paid tiers, fees, or revenue.
- No third-party auditors.
- No partner marketing program.
- No claim of "secure" or "production-ready". Badges state only what was tested.

## 3. Levels

Each level includes everything in the one below.

### Bronze: Verified

Meaning: it installs, runs, and is not obviously unsafe.

| Area | Requirement |
|---|---|
| Packaging | Valid manifest; declares the connector spec version it targets |
| License | OSI-approved license file |
| Ownership | Named maintainer with a working contact; security contact |
| Docs | README with auth setup, supported streams, and known limits |
| Static checks | Dependency vulnerability scan (no known critical/high without a documented exemption); secret scan; no network calls outside declared hosts |
| Smoke test | Passes `check` and `discover`, and reads at least one stream from a sandbox or fixture |

### Silver: Tested

Meaning: it behaves correctly under the conformance suite.

| Area | Requirement |
|---|---|
| Conformance suite | Passes 100% of required cases: schema discovery, type mapping, pagination, full refresh idempotency, incremental sync with state resume, rate-limit and retry behavior, error taxonomy (auth, transient, permanent) |
| CI | Connector's own tests run in CI; suite results published per release |
| Versioning | Semver, changelog, and a deprecation note before breaking changes |
| Maintenance | Issue triage within 5 business days; critical security fixes within 30 days |
| Compatibility | Works on the current and previous connector spec version |

### Gold: Pellucid-Supported

Meaning: Pellucid commits to it operationally.

| Area | Requirement |
|---|---|
| Live testing | Nightly run against the real source API (test account), with failures alerting a named owner |
| Drift detection | Source API changes or schema drift detected and triaged before customers hit them |
| Performance | Meets a throughput and memory baseline set per connector class (REST, database, file) |
| Security | Critical fixes within 7 days; high within 30 days; Pellucid security review once, then on major changes |
| Support | Documented escalation path into Pellucid support; runbook; listed in support SLAs |
| Track record | At least 90 consecutive days at Silver with no lapse |
| Sponsor | A named Pellucid engineer as co-owner |

**Expect Gold to be rare for community connectors.** The honest target at launch is zero to two. The first-party connectors are the natural Gold population.

## 4. Process

1. **Apply.** The maintainer opens a request in the connector registry repo, or a first-party connector is enrolled automatically.
2. **Automated pipeline.** Bronze and Silver checks run in CI with no human step. Results are public: pass/fail per case, with logs.
3. **Human review.** One Pellucid reviewer checks the Bronze docs and ownership items, and Gold items before they are approved.
4. **Issue the badge.** The registry stores a signed record: level, spec version, connector version, date tested, expiry. The UI, docs, and README badge read from that record, so the badge can't be copied onto an uncertified version.
5. **Recertify.**
   - Re-run on every release.
   - Re-run quarterly even without a release.
   - Fail a check and the level drops automatically. The maintainer gets 14 days to fix it before the badge is removed.
6. **Revoke.** Pellucid may revoke immediately for an unpatched critical vulnerability, a license change, or abandonment (maintainer unreachable for 60 days).

## 5. Badge and claim rules

- Names: "Verified", "Tested", "Pellucid-Supported". Show them as Bronze, Silver, and Gold in the UI, with a link to the criteria and the latest results.
- Every badge shows the certified connector version. Newer uncertified versions show no badge.
- Legal and marketing copy says "passed Pellucid's conformance tests", never "certified secure" or "guaranteed".
- Certification does not transfer through forks.

## 6. Ownership and cost

- **Owner:** one product or engineering lead for the connector platform. Name them in week 1.
- **Build:** about 1.5 engineers for 10 to 12 weeks. Most of the effort is turning existing internal connector tests into a reusable conformance suite.
- **Run:** about 0.25 FTE once live. At 11 connectors the review load is trivial. Automation is for consistency and for future growth, not for volume today.
- **Gold infrastructure:** test accounts and nightly runs per Gold connector. This is the main recurring cost, so cap Gold slots at 5 in year one.

## 7. Timeline to 31 March 2027

| Weeks | Work |
|---|---|
| 1–2 | Decisions in §8. Interview the 11 maintainers and a few CS and sales leads. Review support tickets on community connectors. Confirm the owner. |
| 3–8 | Build the conformance suite from existing first-party tests. Add the signed registry record and the public results page. |
| 9–11 | Pilot on 3 first-party and 3 community connectors. Fix criteria that are ambiguous or unfair. |
| 12–15 | Run all 11 community connectors and the remaining first-party ones. Maintainers get 4 weeks of notice and fix guidance. |
| 16–18 | Badge UI and docs, legal review of claim wording, internal enablement for sales and support. |
| 19–21 | Soft launch, then announcement. |
| 22 | Buffer. This is a hard-dated launch with a build-heavy middle, so the buffer matters. |

## 8. Decisions needed before week 3

1. **Do first-party connectors take part?** I recommend yes, because that is where the value is. The alternative is a badge for 11 niche connectors only.
2. **Should Gold be open to community connectors in year one?** I recommend yes, but cap it at 5 slots and require a Pellucid sponsor engineer.
3. **Public or customer-only results?** I recommend public results for Bronze and Silver and customer-visible detail for Gold.
4. **Who owns the program?** Name one person.
5. **Is the quarter-end date fixed?** If it is, cut scope instead of the date: drop nightly live testing from Gold and launch with the Bronze and Silver pipeline only.

## 9. Measuring whether it works

There is no demand evidence today, so define success before launch:

- **Adoption:** at least 8 of the 11 community connectors reach Bronze within 90 days.
- **Quality:** the conformance suite finds real defects in first-party connectors (a sign the suite is worth having).
- **Customer signal:** one or more of: certified connectors cited in sales calls, install rate of certified versus uncertified community connectors, support tickets per connector by level.
- **Cost:** reviewer time stays under 0.25 FTE.

**Review at 90 days.** If nobody uses the badge in buying or support conversations and community participation is low, keep the suite as an internal release gate and shrink the public program. Don't expand it. The suite pays for itself either way.

## 10. Risks

| Risk | Mitigation |
|---|---|
| Badge without substance, as a "me too" feature | Every level maps to published tests; public results |
| Support liability for community connectors | Gold only with a Pellucid sponsor; clear claim wording |
| Maintainer burnout or abandonment | Auto-downgrade, 60-day abandonment rule, a path to adopt orphaned connectors |
| Build effort crowds out roadmap work | Reuse first-party tests; cut Gold live testing first if the date slips |
| Over-investment in a tiny population | Cap Gold slots; run the 90-day review |

## 11. What I'd tell the CEO

We can ship a credible three-level badge by the end of next quarter. Customers haven't asked for it, so we're keeping it small. The first-party connectors, which are 92% of installs, go through the same tests and carry the top label. We'll judge it at 90 days on whether it shows up in real buying and support conversations.