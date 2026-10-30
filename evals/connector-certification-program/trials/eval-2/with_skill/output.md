# Pellucid Data connector certification charter, v1, 2026-10-30

**Verdict: don't launch Bronze/Silver/Gold. Ship ownership labels by end of next quarter and re-check on 2027-04-30.**

The go/no-go gate fails on two of three conditions. Under the skill, ownership labels only is a complete outcome, not a deferral.

Next action: take section 0b and section 1 to the CEO. Section 2 and the plan at the end are what you can show them as live by the deadline.

I couldn't run the interview, so every answer I assumed is marked in section 0. Correct those first.

## 0. Inputs

| # | Interview question | Answer | Asked or assumed |
|---|---|---|---|
| 1 | What do partners build? | Data connectors on an ELT catalog | Given |
| 2 | Who builds what customers install? | Pellucid 38 connectors, about 92% of installs. 11 community connectors, a few dozen installs total. No partner-built connectors mentioned. | Given. I assumed partner-built = 0. |
| 3 | Who reads the badge? | (d) Nobody has asked: not customers, procurement or sales. | Given |
| 4 | Per-connector production telemetry with a platform-vs-connector fault split? | Unknown. Treated as not yet affordable. | Assumed |
| 5 | How often does the platform ship contract-breaking changes? | Unknown | Assumed |
| 6 | Reviewer capacity and kit appetite | Low: no dedicated certification reviewer | Assumed |
| 7 | Does a certified tier exist? | (a) None | Assumed from "launch a badge" |
| 8 | Deadline | End of next quarter, taken as 2027-03-31 | Given (CEO). Date assumed. |
| 9 | One-off or compounding? | One-off competitive-parity signal. No buyer demand shows it compounds. | Assumed |
| 10 | Effort ceiling | Small: days of policy and listing work, no headcount | Assumed |
| 11 | Fee to partner? | No | Assumed |

Re-ranking:

- **Q2 and Q3** failed the gate, which removed every quality-tier rung.
- **Q8** (a hard date) promotes rungs that ship as policy text and an existing listing page.
- **Q10** (low effort ceiling) deletes the kit, telemetry and manual-review rungs instead of demoting them. They return only if section 1's re-check triggers fire.

One question could change the verdict. What is the other ~8% of installs: custom or unlisted connectors, or partner-built ones? If it is partner-built, re-run the partner-share condition.

## 0b. Proposals evaluated

| Proposal (who) | Verdict | Rule it meets or breaks |
|---|---|---|
| Three levels, Bronze/Silver/Gold (CEO) | **Rejected** | Metal ladders of three or more tiers are deleted: buyers can't tell the rungs apart. The names also invite criteria based on partner status, which certifies the relationship, not the connector. |
| Certification live by end of next quarter (CEO) | **Changed** | Gate fails on outside reader and partner share. Delivered as ownership labels live by 2027-03-31, with a dated re-check. |
| Match the competitor's "Certified Partner Connector" badge (CEO, via competitor) | **Rejected as a design input** | A badge is a promise to a reader. Nobody has asked for one, and Pellucid has nothing to certify: it builds the connectors customers install. |
| Certify the 11 community connectors (implied) | **Rejected** | A few dozen installs across all 11 can't reach any telemetry minimum volume. Every telemetry criterion would read "insufficient data". |
| Certify Pellucid's own 38 (implied) | **Rejected** | The operator owns the connectors buyers use, so owning them first-party beats certifying anyone. Section 2 labels them "Pellucid-maintained". |

## 1. Go/no-go

- **Outside reader: fails.** Question 3 is (d). No buyer or procurement team has asked.
- **Partner share: fails.** Pellucid builds about 92% of installs. Community connectors carry a few dozen installs, far below the roughly-a-fifth bar. None of the most-installed connectors is partner-built.
- **Evidence: not yet affordable (assumed).** The kit isn't built. Telemetry has no fault split, and the skill counts that as not affordable. Not decisive, since two conditions already fail.
- **Decision: ownership labels only. Re-check 2027-04-30, or earlier if a trigger fires.**

Re-check triggers (self-set starting values; any one reopens the decision):

1. Partner-built plus community connectors reach 20% of installs.
2. A partner-built or community connector enters the top 10 by installs.
3. Three or more deals or security questionnaires in one quarter ask for certification or a verified connector.
4. Per-connector telemetry with a fault split exists. That makes the kit and telemetry rungs affordable.

## 2. Labels

| Label | Meaning to a buyer | Maintained by | Earned by |
|---|---|---|---|
| Pellucid-maintained | Built, released and supported by Pellucid | Pellucid | Default for the 38 first-party connectors |
| Community | Contributed by a third party. Pellucid doesn't maintain or support it. | The contributor | Meeting the listing bar |
| Partner-maintained | Built by a partner company, not Pellucid | The partner | Reserved. None exist today; add it when the first one lists. |

There is no earned quality label. Ownership is the only discriminator buyers need today.

**Listing bar** (what any connector needs to appear at all; it isn't a label criterion):

- A manifest that validates against the schema.
- A stated license.
- A named maintainer contact.
- A named security contact.
- No secrets in fixtures.

Each is a yes/no check on the static layer, verified once at listing and again at the annual contact check in section 6. Nothing here is a quality claim.

## 3. Criteria

None. No quality label exists, so there are no thresholds to measure. Thresholds written now would be borrowed numbers with no baseline.

When trigger 4 fires, the first draft starts here:

`production success rate | threshold set from the best first-party connectors' measured baseline | trailing 28 days | at least 200 syncs | operator telemetry | single Certified label`

## 4. Kit

None. A conformance kit would serve 11 connectors with a few dozen installs. Build it only after a re-check trigger fires, and the conformance-kit reference defines its layers.

## 5. Support routing

| Label | First contact | Who fixes | Response commitment | Sentence shown on listing |
|---|---|---|---|---|
| Pellucid-maintained | Pellucid support | Pellucid | Your plan's existing support terms | "Built and supported by Pellucid. Contact Pellucid support." |
| Community | The maintainer's published channel | The maintainer | None | "Contributed by <maintainer>. Not maintained or supported by Pellucid. Contact <maintainer channel>." |
| Partner-maintained | The partner's published channel | The partner | Set by the partner, shown on the listing | "Built and supported by <partner>. Contact <partner channel>." |

Pellucid support answers platform-side questions on community connectors, such as platform status and API limits. It doesn't debug the connector's code.

## 6. Renewal

- **Pin:** none. There is no quality badge to pin to a kit or platform version.
- **Triggers:** none for labels.
- **Calendar floor:** an annual check of maintainer and security contacts on every Community and Partner-maintained listing. Contacts expire on their own.
- **Release signal:** a connector with no release and no maintainer response for 6 months enters the section 7 ladder.
- **Notice before new listing-bar items apply:** 90 days.

## 7. Decertification ladder

This ladder covers community and partner listings, since no earned badge exists to suspend. Every number is a starting default.

| Rung | Trigger | Owner | Notice | Customer action |
|---|---|---|---|---|
| Warning | No release and no maintainer response for 6 months, or a failed annual contact check | Catalog owner | 30 days to the maintainer | None |
| Marked unmaintained | Warning unanswered after 30 days. The listing says "unmaintained". | Catalog owner | The maintainer is told the same day | None |
| New installs blocked | 90 days marked unmaintained, abandonment, or maintainer exit | Catalog owner | 14 days to the maintainer | Existing users notified |
| Existing installs disabled | Only after rung 3, and only with a migration path | Head of integrations (assumed role) | 60 days' customer notice | Notified, with a first-party replacement where one exists |

- **Adoption before rung 3:** offer a connector above 10 installs to a new maintainer or to Pellucid first.
- **Ladder clock:** the contact check and the release check run every month on the first business day. Each counts failures over a trailing 6-month release window.
- **Dispute route:** the head of integrations decides within 10 business days. The listing stays during the dispute, except on the security fast path.
- **Security fast path:** an unpatched critical vulnerability blocks new installs within 3 days.

## 8. What the label buys

- **Buys:** a label and a catalog filter by owner. Nothing more is justified without criteria.
- **No** rank weight, no co-marketing slots, no triage promise for non-first-party connectors.
- **Fee to partner:** none, so no refund rule.
- **Badge use:** labels appear only on the listing page, and only for the connector versions the listing describes.
- **Agreement clauses to add** (for Legal to draft):
  - Pellucid may mark a listing unmaintained or block new installs.
  - The maintainer owns support for the connector.
  - Pellucid disclaims liability for community code.

## 9. Transition

None. No program is running, so no existing badge needs a fate.

## 10. KPIs and review date

- Community and partner share of installs. This is the trigger-1 metric, read monthly.
- Count of certification asks from buyers, procurement and sales, logged as they arrive. This is trigger 3.
- Tickets about community connectors that land at Pellucid support instead of the maintainer. A high number means the support sentence isn't working.
- **Review date: 2027-04-30.** Re-run the go/no-go with these numbers.

## 11. Gate check

| Gate | Pass / fail | Evidence in this charter |
|---|---|---|
| 1. Go/no-go recorded with each condition | Pass | Section 1 |
| 2. Every criterion has all five fields | Pass, trivially | Section 3 has no criteria, because no quality label exists |
| 3. Every tier carries a support sentence | Pass | Section 5, all three labels |
| 4. Every badge names its pinned versions | Pass, trivially | No quality badge exists |
| 5. Every ladder rung names trigger, owner, notice, customer action | Pass | Section 7 |

## Plan to the deadline

Time figures are my estimates for a low-effort team.

1. **Week of 2026-11-02, 30 minutes:** walk the CEO through section 0b and section 1. Ask them to approve ownership labels as the deliverable.
2. **By 2026-11-30, about 1 day:** publish the labels, support sentences, listing bar and ladder as policy text.
3. **By 2026-12-18, about 2–4 engineering days:** show the label on all 49 listings (38 + 11), and add the catalog filter by owner.
4. **From 2027-01:** log every certification ask in a CRM field, and read the monthly install share.
5. **By 2027-03-31:** answer Q4 and Q5. If there is no per-connector attribution or fault split, add them to the roadmap as the work that makes certification affordable later.
6. **2027-04-30:** re-check against the four triggers.

For the competitor comparison, sales can say Pellucid builds and supports the connectors covering about 92% of installs, and the 11 community connectors are labelled as unsupported. That is a more checkable promise than a badge nobody has asked for.

I didn't write a project memory entry. If you want the verdict, label names and triggers saved for later runs, say so and tell me where they belong.