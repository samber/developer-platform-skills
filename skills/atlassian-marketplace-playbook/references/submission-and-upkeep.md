# Submission and upkeep reference

Every figure here changes; confirm it against current Atlassian developer docs before quoting it.

## Platform dates

| Date        | Change                                                                  |
| ----------- | ----------------------------------------------------------------------- |
| 17 Sep 2025 | Only Forge apps accepted for new Marketplace submissions                |
| 16 Dec 2025 | No new Data Center app submissions (Bitbucket DC exempt)                |
| Jan 2026    | Forge consumption usage billed to developers (first invoice 1 Feb 2026) |
| Mar 2026    | Apps with a Connect descriptor stop receiving updates                   |
| 30 Mar 2026 | No Data Center sales to new customers                                   |
| 30 Mar 2028 | Last Data Center license, app and expansion sales to existing customers |
| 30 Jun 2026 | Marketplace bug bounty programs public or scheduled public              |
| end 2026    | Cloud Fortified phased out; Atlassian Enterprise Certified replaces it  |
| 31 Jan 2027 | Connect end of support: critical security patches only                  |
| 28 Mar 2029 | Data Center end of life                                                 |

## Revenue share and payouts (Paid via Atlassian)

| Framework of the latest listed version                      | Partner share from 1 Oct 2026 |
| ----------------------------------------------------------- | ----------------------------- |
| Forge (no Connect module or Connect scope, OAuth, Forge UI) | 83%                           |
| Connect, or any Connect module or scope                     | 75%                           |
| Data Center                                                 | 75%                           |

- 100% of Forge revenue until $1M lifetime Forge revenue, summed across the partner's Forge apps. Connect-era revenue of a migrated app does not count.
- Payout within 30 days after the month in which $500 profit accrues.
- Refunds: full within 30 days; 31-60 days at Atlassian's discretion, partner approval past $1,500.

## Submission packet

1. ECOHELP access for the submitter, confirmed by opening a test ticket.
2. Partner verification (KYC/KYB): identity form, ID check, business check; 2-3 business days, once per partner.
3. App security questionnaire (Forge variant): authentication, data security, secrets, vulnerability management. Fail answers block the listing.
4. Partner security questionnaire: informational.
5. Privacy & Security tab: data stored and where, personal data, API-token use (none, unless Atlassian granted an exemption), one justification per scope, trust-center link.
6. Scope and egress list for the reviewer: each scope with the feature that calls it; each remote host with the data sent and why.
7. Privacy policy, End User Terms, DPA if a processor, documentation URL, support contact.
8. Test access: credentials and sample data on your SaaS and any third-party service.
9. Listing fields: see samber/developer-platform-skills@integration-listing-optimization.

Official review: 10-15 business days for approval, 5-10 for the security workflow; Platinum, Gold and Silver partners get expedited SLAs. Cloud minor versions publish instantly with no security checks.

## Major-version triggers (Forge)

Adding or changing scopes; adding egress or remotes; changing an egress category; `inScopeEUD` false → true; enabling licensing; adding, removing or changing an auth provider or its client ID; adding a dynamic web trigger. Removing egress is minor; removing a scope is major. Each major re-enters Marketplace review; majors that escalate no privilege can be pushed with `forge version bulk-upgrade`.

Also re-reviewed as a new app type: an edition, Atlassian Government Cloud, Isolated Cloud, multi-app compatibility, and any payment-model change.

## Security bug-fix SLAs and enforcement (cloud)

| Severity (CVSS) | Fix within | Missed deadline                                                                     |
| --------------- | ---------- | ----------------------------------------------------------------------------------- |
| Critical (≥9.0) | 10 days    | App hidden                                                                          |
| High (≥7.0)     | 4 weeks    | Hidden on day one without badges; with badges, badges removed, hidden after 15 days |
| Medium (≥4.0)   | 12 weeks   | Same as High, once 3 breaches are open                                              |
| Low (<4.0)      | 25 weeks   | Same as High, once 4 breaches are open                                              |

Bug-bounty findings get two weeks of triage, then count as accepted. No partner response for 90 days hides the app; a failed Security Threat Assessment or exhausted contact can pause it, which stops it working for existing customers. Extensions only for a breaking change for customers, an Atlassian platform cause or dependency, a third-party block, or a changed risk.

## Marketplace bug bounty (Bugcrowd)

- Atlassian pays the platform and triage; the partner funds the reward pool, minimum $5,000 upfront†, and pays every bounty.
- Allow at least 3 weeks† from request to launch. Programs must be public.

## Atlassian Enterprise Certified gates

Forge-only with no Connect modules; SOC 2 Type II or ISO 27001 report and badge; public trust center from an accepted provider list (Vanta, Drata, SafeBase and others); annual pen test (Atlassian's Bugcrowd pentest or an approved CREST vendor); public bug bounty; architecture or data-flow diagram and data residency when end-user data is stored remotely; published logging contents and retention, subprocessors, incident-response process and a Statuspage URL on the listing; no PAT collection, no broad egress wildcards, no EOL Node runtimes, CI vulnerability gating; 24/5 security contact answering within 8 business hours. Checks run largely automatically against trust-center document titles and Ecoscanner.

## Partner tiers (reviewed annually)

| Tier     | Annual cloud gross sales | From Forge | Bug bounty scope                   | Support to Atlassian                            |
| -------- | ------------------------ | ---------- | ---------------------------------- | ----------------------------------------------- |
| Silver   | $150K                    | -          | most-installed paid cloud app      | < 48 h                                          |
| Gold     | $750K                    | $10K       | paid cloud apps with 100+ installs | < 24 h, SOC 2/ISO 27001 audit scheduled         |
| Platinum | $3M                      | $150K      | all paid cloud apps                | < 24 h, SOC 2/ISO 27001, validated trust center |

Every tier requires all paid apps to be Paid via Atlassian and at least one paid cloud app.
