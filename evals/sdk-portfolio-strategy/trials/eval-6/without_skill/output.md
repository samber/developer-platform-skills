# Orbital Grid SDK Portfolio: Tier Definitions and Promotion Policy (draft v0.1)

I didn't interview you first, so the assumptions below are mine. Correct them before this goes to the CTO.

## 0. Assumptions and open questions

- I assumed the portfolio is three first-party SDKs (Python, Go, Java) plus the Rust crate. I assumed no other third-party clients exist.
- I assumed you have one public API with a published spec, and that you can fund a small conformance suite.
- **Open question 1:** Does the author of `orbital-grid` know about the CTO's plan? Nothing below should be announced until they do.
- **Open question 2:** Who owns the crate name on crates.io, and who owns the trademark on "Orbital Grid"? The author may hold a name that matches your brand. Counsel must settle this, and this document doesn't.
- **Open question 3:** Who owns the support and security-response obligations? This policy only works if named people hold them.
- All numeric thresholds are defaults I set. Replace them with your own data where you have it.
- Licensing, contributor agreements and trademark terms go to counsel.

## 1. Principle

A tier describes **what we promise users**, not who wrote the code. Each tier is a bundle of obligations we can keep. Quality alone never earns a tier. The Rust crate may be better than anything we'd write, but "official" means we answer the pager for it.

Authorship only matters for one question: can we keep the promise if the author leaves?

## 2. Tier definitions

| | **Official** | **Certified** | **Community** | **Preview** |
|---|---|---|---|---|
| Who owns it | Orbital Grid org | Independent maintainer(s) | Anyone | Orbital Grid org |
| Registry and name control | We hold owner rights | Author holds; we hold at least one co-owner seat (see criterion C5) | Author | We hold |
| API coverage | 100% of GA API, same-day support for new endpoints (default: within 1 release cycle) | All endpoints in the certified API version(s); gaps documented | Unspecified | Declared subset |
| Conformance suite | Must pass every release in CI | Must pass on each certified version | Optional | Partial |
| Security | Our disclosure process, advisories, dependency scanning, signed releases | Author's process plus a documented contact we can reach; we re-review each major version | None promised | Our process |
| Versioning | SemVer; deprecation notice (default: 6 months) | SemVer; no deprecation promise from us | None | None; may break |
| Support | Our support channels, SLA applies | Issues go to the author; we triage API-side defects | None | Best effort |
| Docs | Primary quickstarts and reference | Listed with a "Certified" badge and quickstart link | Directory listing only | Labeled beta |
| Brand use | Uses our name | "Certified for Orbital Grid" mark, license-limited | No mark | Our name, "preview" label |
| We can remove it | N/A (we maintain) | Yes, on defined triggers (section 5) | Yes | Yes |

Plus one status, **Archived**: read-only, with a published successor and end-of-life date.

Rules that apply to every tier:
- A tier is a claim about a **specific major version range**, never about the project forever.
- Docs, the SDK directory and the badges show the tier and the supported API version.
- No project has two tiers. Official SDKs also pass the Certified checks.

## 3. Promotion criteria

Each criterion is pass or fail with evidence. Unknown counts as fail.

**Community → Certified**
- C1. Open-source license on our approved list; no copyleft that blocks use in customer products.
- C2. Passes the conformance suite against the current GA API version.
- C3. Security review done: dependency audit, no known unpatched advisories, unsafe-code or memory-safety review where the language needs it (Rust `unsafe` blocks in particular).
- C4. Maintainer commitments: a named security contact, a response target for critical issues (default: 5 business days), and public docs.
- C5. Continuity: at least two people with publish rights, **or** a signed agreement giving us a recovery path (registry co-owner seat or documented transfer on abandonment).
- C6. Release hygiene: SemVer, changelog, CI, reproducible builds, tagged releases.
- C7. Real usage evidence, not a raw download count. Download totals include CI, mirrors and bots. Use recent-version downloads, reverse dependencies and customer reports instead. The crate's 60k is a lead to check, not proof.

**Certified → Official** (all Certified criteria, plus)
- O1. Ownership: we hold registry owner rights, the repo (or an org-owned fork with a clear lineage), signing keys and CI secrets. Two or more of our people have publish rights.
- O2. Legal: counsel signs off on license, contributor rights (CLA or DCO), trademark and name rights.
- O3. Staffing: at least two named maintainers on our payroll (or contracted), one of them an engineering owner. This applies to every Official SDK, and your Python/Go/Java teams must already meet it.
- O4. Operations: on-call for security issues, a documented release process, SLA terms published.
- O5. Roadmap fit: parity with API releases through our release process, tested in the same CI as the other SDKs.
- O6. Idiom and DX review against the other Official SDKs (error handling, auth, retries, pagination, observability).
- O7. Author agreement, if the original author is not joining us. Use a written maintainer agreement that covers credit, decision rights, compensation or sponsorship, and what happens if the author leaves.
- O8. Funding for 24 months is approved (default).

**Community → Preview, Preview → Official** is for SDKs we write ourselves. Promote on O1–O6 plus a coverage gate and one release cycle of internal use.

## 4. Promotion process

1. **Nomination.** Anyone files a request using the criteria checklist. A DevRel or SDK-owning engineer is the sponsor.
2. **Triage, 10 business days (default).** Check C1, C2, C7. Reject or continue.
3. **Review.** Security, legal (for O2) and engineering review run in parallel. Each reviewer returns pass, fail or unknown with evidence.
4. **Decision.** A small council decides: the SDK engineering lead, the security lead, and DevRel. A tie goes to the CTO. Decisions and reasons are written to a public log, except security details.
5. **Announce** only after all agreements are signed.
6. **Review date.** Every tier assignment has a re-review date (default: 12 months for Certified, at each major version for Official).

## 5. Demotion and removal

Triggers, each with a clock:
- Failing the conformance suite on a current GA API version for more than 30 days.
- An unpatched critical vulnerability for more than 30 days (default).
- No release or maintainer response for 6 months while the API has changed.
- A license change that breaks C1.
- The owner of the Certified project breaks the mark rules.

The ladder is Official → Certified (if we hand maintenance over) or Archived. Certified → Community → delisted. Give notice (default: 60 days) and write the migration path first. Exercise the ladder at least once in the first two quarters, or it will not work when you need it.

## 6. What this means for the portfolio today

1. **Python, Go, Java:** audit them against O1–O8 now. If one fails, say so and fix it, because a policy that its authors don't meet is not credible. Record the result in the public tier table.
2. **The Rust crate:** it enters at **Community**. I recommend fast-tracking it to **Certified** as the first goal. That needs only C1–C7 plus the author's agreement to the mark license, and it delivers most of the user benefit in one quarter.
3. **Official is a separate decision.** It requires the author's agreement and your O1–O8. If the author declines to transfer or share ownership, Certified is the correct permanent tier. The alternative is a fork or rewrite, and that discards the quality that made the crate attractive.

## 7. Risks to put in front of the CTO

- **The value is the author's time, not the code.** Making the crate official changes the author's incentives and workload. Offer paid sponsorship or a contract, credit, and decision rights. Without those, a promotion can lose you the author.
- **Single-person bus factor.** Rank this first among the risks. C5 and O3 exist for it.
- **Name collision.** An independent crate named `orbital-grid` may confuse users about who supports it today. Settle the name before any announcement.
- **Pressure to hit "next quarter."** A date set before the author has agreed is a commitment you can't keep. Commit to the Certified timeline and let Official follow the negotiation.
- **Signaling to other community maintainers.** Once Rust gets a path, every other community SDK will ask for one. The criteria above are the answer, so apply them the same way to each.
- **Policy drafted around one case.** The criteria must read as neutral to everyone. Have someone outside the Rust discussion review them.

## 8. Metrics (baselines first)

- Share of SDK users by tier, from telemetry or the API's user-agent header.
- Conformance pass rate per SDK per API release.
- Time to patch a critical advisory per tier.
- Time from API release to SDK parity per tier.
- Number of Certified and Community projects, and how many left or were demoted.

Record a baseline for each before setting targets.

## 9. Decisions I need from you

1. Do you want four tiers, or three (drop Preview)?
2. Is the council's make-up above right, and who breaks ties?
3. Does the author already know? If not, who talks to them first?
4. Is there budget for sponsorship or a contract for the author?

Once those are answered, the next step is to run the three existing SDKs through O1–O8 and publish the first tier table.