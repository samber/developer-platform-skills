# Tidewick Certified: tightened criteria (draft v1)

**Next action:** before launch, run the telemetry query in section 4 across all ~200 integrations. Every number below marked 🎯 is a proposed default. Calibrate it so roughly 10–20% of integrations qualify. If 60% pass, the badge means nothing. If 0% pass, nobody will apply.

## 1. What changed and why

| # | Original | Problem | Fix |
|---|---|---|---|
| 1 | High-quality, well-structured code | Subjective. Tidewick may not see partner code. | Replace with observable checks (C1). |
| 2 | Responsive support | No number, no clock. | Response and resolution targets, measured from tickets (C2). |
| 3 | Well documented | Reviewer opinion. | Checklist of required artifacts (C3). |
| 4 | 99% uptime | Uptime of what? Whose fault? Over what window? | Telemetry-based reliability, with errors attributed by cause (C4). |
| 5 | Premier partner | Program tier, not integration quality. | Keep as an eligibility gate, not a quality criterion (G1). |
| 6 | 3 joint enterprise customers | "Joint", "enterprise" and "customer" are undefined. | Define each term and require active usage (C5). |
| 7 | Passes our review | Circular. It re-checks 1–6. | Delete as a criterion. Replace with a review process and an outcome rule (section 5). |

## 2. Structure

- **Gate (G1):** eligibility. Fail it and the integration is not reviewed.
- **Criteria (C1–C5):** all must pass. Each is measured per integration, not per partner.
- **Certification is per integration.** A partner with five integrations can certify one.

## 3. Criteria

### G1. Eligibility
- The partner is Premier in the partner program on the application date and when the badge is renewed.
- The integration has been generally available (not beta) for at least 90 days 🎯. Without this the telemetry window can't be filled.

### C1. Engineering quality (replaces "high-quality, well-structured code")
Pass all of these. Tidewick checks the first four from telemetry or by running the integration, so it needs no source access.

1. **Contract conformance:** the integration passes Tidewick's integration test suite against the current SDK or spec version. Name the suite in the program guide.
2. **Schema stability:** at most 1 unannounced breaking schema change in 12 months. Announced means at least 30 days 🎯 of notice through the changelog.
3. **Pagination, rate-limit and retry behavior:** the integration honors source-API rate limits, and `429`/`5xx` retries use backoff. The test suite verifies this.
4. **Malformed-response rate:** under 0.1% 🎯 of calls fail with parse or schema errors (see error taxonomy, section 4).
5. **Supply chain (needs source or attestation):** no known critical CVEs in dependencies, and secrets are stored in Tidewick's credential store. The partner attests to this and Tidewick spot-checks it.

If Tidewick does not want to require source access, state that and use the attestation route for item 5. Decide this now, because partners will ask.

### C2. Support responsiveness (replaces "responsive partner support")
Measured over the trailing 90 days from the shared ticket queue.

| Severity | First response | Resolution or workaround |
|---|---|---|
| Sev 1: data not flowing for any customer | 1 business hour 🎯 | 1 business day 🎯 |
| Sev 2: degraded or partial data | 1 business day 🎯 | 5 business days 🎯 |
| Sev 3: question or minor defect | 2 business days 🎯 | Best effort |

- Pass: at least 90% of tickets in each severity meet the target.
- Minimum volume: if there were fewer than 5 tickets, the partner runs a scripted test ticket per severity.
- A named support contact and an escalation path are on file.

### C3. Documentation (replaces "well documented")
All of these exist, are public or customer-accessible, and were updated within the last 12 months 🎯:

- Setup guide covering auth, permissions, and the minimum scopes required.
- Data dictionary: every table and field, its type, and its sync behavior (full or incremental).
- Known limitations and unsupported objects.
- Troubleshooting page that maps the integration's top 10 error codes to fixes.
- Changelog with dated entries.
- A cold-start test: a Tidewick reviewer who has never used the integration completes setup using only the docs, in under 60 minutes 🎯, without contacting the partner.

### C4. Reliability (replaces "99% uptime")

**Definition.** Success rate = successful calls ÷ eligible calls, measured per integration over a rolling 90 days from Tidewick call telemetry.

- **Eligible calls** exclude errors that are not the partner's fault. See the taxonomy in section 4.
- **Pass:** at least 99.5% 🎯 success rate, and no single calendar month below 99% 🎯.
- **Minimum volume:** at least 100,000 eligible calls 🎯 in the window. Below it, the integration can't be certified yet.
- **Incident rule:** every outage over 1 hour 🎯 needs a written post-incident summary within 5 business days.

Why not "99% uptime": 99% allows about 7 hours of downtime a month. As a call success rate, it also lets 1 call in 100 fail silently. Telemetry gives a stricter and more honest measure than a status-page figure the partner reports about itself.

### C5. Joint customers (replaces "3 joint enterprise customers")
- **Customer:** a distinct paying Tidewick account, counted once per parent company 🎯.
- **Enterprise:** needs a definition you can verify. Proposal: annual contract value above $X, or more than N seats. 🎯 *Product team: pick one.*
- **Joint:** the account uses both Tidewick and the partner's product, and the integration is active in production.
- **Active:** at least 1 successful sync per week for the trailing 90 days. Telemetry proves this, so no self-reported references are needed.
- **Pass:** at least 3 accounts meet all four terms.
- Each counted customer consents to being named, or stays anonymous in the evidence file.

## 4. Telemetry: error-code attribution (do this first)

You have per-integration call telemetry with error codes. That is the main asset here. Map every code to one owner before you publish C4. Proposed starting buckets:

| Bucket | Examples | Counts against partner? |
|---|---|---|
| Partner / source API fault | `5xx`, timeouts, connection resets, schema mismatch, malformed payloads | Yes |
| End-customer config | `401` expired credentials, `403` missing permission, quota exhausted by customer | No |
| Tidewick platform fault | Internal errors, scheduler failures | No |
| Rate limiting | `429` | Only if the integration ignores `Retry-After` or retries without backoff |

Steps:

1. Pull 90 days of calls for all integrations and bucket them with the table above. Resolve every unmapped code by hand.
2. Compute each integration's success rate, malformed-response rate, and active-customer count.
3. Plot the distributions and check how many integrations would pass C4 and C5 at the proposed thresholds. Adjust the 🎯 numbers.
4. Spot-check 10 integrations. Check that the failures the attribution blames on the partner really are the partner's.

Watch for a trap: a `401` can be a partner bug (their token refresh is broken). If one integration has a `401` rate far above its peers, treat it as a partner fault.

## 5. Process (replaces "passes our review")

1. **Apply:** the partner submits the evidence file (docs links, support contact, customer list).
2. **Automated check:** Tidewick runs the G1, C4 and C5 queries and the C1 test suite.
3. **Human review:** a Tidewick reviewer runs the C3 cold-start test and the C2 test tickets. Publish the review checklist so the outcome is predictable.
4. **Decision:** certified only if every item passes. Tidewick tells the partner within 15 business days 🎯, with the specific failures if rejected.
5. **Appeals:** the partner may reapply after fixing failures, with no cooldown.

## 6. Keeping the badge

- **Recertify every 12 months** 🎯. C4 and C5 are re-measured from telemetry each quarter.
- **Warning:** if C4 or C2 falls below threshold for one quarter, the partner has 60 days 🎯 to fix it, with the badge intact.
- **Suspension:** two consecutive failing quarters, or a Sev 1 unresolved for more than 5 business days, removes the badge until the partner re-passes.
- **Premier lapse:** the badge is suspended at the next recertification point unless the partner is back at Premier.

## 7. Decisions needed before launch

1. **Enterprise definition** (C5): the ACV or seat threshold.
2. **Source access** (C1): required, or attestation only.
3. **Thresholds:** confirm every 🎯 after the telemetry run.
4. **Per-integration or per-partner badge:** this draft assumes per-integration.
5. **Benefits of the tier:** this draft covers qualification only. If certified integrations get no extra promotion, co-marketing or support, partners will skip the effort.

## 8. Risks to check

- **Gaming:** a partner could point three internal test accounts at the integration to meet C5. The "distinct paying parent company" rule and the active-usage check cover this.
- **Survivorship:** a high success rate on low volume proves little, hence the minimum call volume.
- **Premier as a proxy:** if Premier is based on revenue or spend, the best integration from a smaller partner is excluded. Decide whether that is intended, or offer an exception path through a Tidewick sponsor.