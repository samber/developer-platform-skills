**Decision: don't announce a public beta.** Run a private preview with a design-partner start, and ship `invoice.memo` as a normal GA field. GA at week 10 is at risk (see the timeline), so treat it as a target, not a promise.

## Why not the public beta

- **The shape is open.** Every public caller freezes whatever you ship first. A wrong shape then costs a version bump.
- **Public preview comes after a private one.** It is skipped only when the change is low-risk and needs volume. Neither is true here.
- **The payload is bank transactions.** That is personal and financial data. A public preview runs on click-through terms, with no signed data carve-out and no DPA coverage.
- **The launch moment belongs at GA.** A beta blog post spends it on a surface you plan to break.

Put a quiet "apply for early access" page up instead. It builds the waitlist for the next wave and doesn't announce the beta. Launch planning is out of scope for this skill, so use the `launch` skill for the GA announcement.

## `invoice.memo`: leave it out of the beta

- It is an additive field on an existing resource. The skill's pre-check says such a field skips the beta and ships GA under `api-versioning-policy`.
- A beta label would add a stage nobody needs. It would also tie memo's release to the reconciliation exit review.
- Free text can carry personal data, so run `public-api-design-review` on it. Document the length limit and whether it is searchable.
- If reconciliation matches on memo, ship memo first.

## Program shape: hybrid private preview

- **Ranking.** Open shape and a new resource family push toward design partners. The clock pushes the other way. Build is 4 weeks, plus 8–12 weeks of partner sessions. That totals 12–16 weeks against your 10, so the hybrid wins.
- **How it works.** It is a private preview where the first sessions run design-partner style on the open question: which of the three designs.
- **Size.** 3–5 accounts. Cap it from your capacity, not demand.
- **Alternative.** Pure design partners, with GA moved to about week 14. This is more efficient for evidence, but only if leadership accepts the new date.

## Owner

"Platform team as a group" is ruled out by the skill. An ownerless beta becomes a perpetual one. Name one owner and one backup before anything else.

## Orvantis ($600k)

Product decides against the entry criteria. Sales does not.

- **Admit Orvantis if all of these hold:**
  - It has a real reconciliation pain: a ticket or a workaround in its code.
  - It plans a real integration inside the window.
  - It names an engineer who attends the sessions.
  - It signs the pre-GA terms.
  - It states intent to pay at GA.
- **If it fails the first three:** send the substitute offer. That means a design review under NDA, a sandbox with synthetic data, the freeze and GA dates, and first place in the next wave. This still keeps the deal moving.
- **Data.** Default is test or synthetic data. Orvantis can use live bank data only under a per-account addendum that legal signs.
- **Production.** Grant a signed production exception if Orvantis needs it. It also counts toward the GA criterion.
- **Concentration.** Its asks must not fill the backlog. Otherwise this becomes custom development for one customer.
- **Dates.** Give Orvantis the exit-review and GA target dates, framed as targets, and don't put the GA date in the contract.

## Stage contract (private preview)

The figures below are illustrative. Replace them with what your team will honour.

| Row | Private preview |
|---|---|
| Access | Invite. Allowlisted per organization after signed terms. |
| Availability | No SLA. Not on the status page. |
| Support | Shared channel, reply within 2 business days. One named answerer. |
| Breaking changes | Allowed. Direct notice to each technical owner at least 1 week ahead. |
| Removal | 30 days. 90 days for accounts with a production exception. |
| Production use | Unsupported, except under a signed exception naming the account. |
| Pricing | Free. GA price announced before the exit review. |
| Data and compliance | Synthetic or test data by default. DPA, certifications and indemnity do not cover the preview. Overrides any MSA or DPA that promises coverage on "all services". Live data only under the signed addendum. Counsel signs the wording. |
| Limits | Published per-organization limits on reconciliation jobs. |
| Marking | Preview version on the wire. SDK pre-release channel. "Preview" badge on every operation. |
| Discontinuation | Export of results for 30 days. Enrolled accounts told privately first. |

- **Wire.** Use a stability suffix on your version scheme, for example a `.preview` version enabled per organization. Keep these operations out of the GA spec and GA SDKs.
- **SDKs.** If the beta adds SDK methods and there is no pre-release channel, that blocks enrollment. Raw-HTTP partners can enroll without one.
- **Access.** Key it on the organization, never on a request percentage.
- **Flag expiry.** The expiry alerts the owner on the exit date. It never disables access.
- **Production use.** Detect it server-side.

## Timeline

Assumption: a 2-week partner release cycle. Correct it if yours differs.

| Week | Milestone |
|---|---|
| 0 | Name owner and backup. Write the stage contract and charter. Start legal on terms and the addendum. Recruit 3–5 accounts from tickets. Check Orvantis against the criteria. |
| 1 | Design sessions on the three designs, using mocks and synthetic data. Pick the shape by end of week. Design review at beta level. Security review. |
| 1–5 | Build, 4 weeks. Give partners incremental drops from week 3. |
| 5 | Enrollment gate signed. Private preview opens with the allowlist. |
| 6 | Contract freeze. |
| 8 | Exit review. |
| 10 | GA target. |
| 12 | Overlap window ends. Then hand over to `api-versioning-policy`. |

**This is tight.** Partners get about 3 weeks of feedback on partial builds before the freeze. Check with engineering whether the 4 weeks start at the shape decision (week 1) or earlier. If the shape isn't picked in week 1, GA slips.

**Exit rules to write down before enrollment:**
- **GA** needs all of these:
  - Enough accounts activated.
  - At least one account on final-shape production traffic under a signed exception.
  - No open blocker.
  - Docs, SDKs, support and GA pricing ready.
- **Kill** on any one of these:
  - Activation is below the floor.
  - The problem is disproved.
  - Cost to serve exceeds what GA pricing can carry.
- **Extension:** one only, at most half the time box (about 2 weeks), with the failed criterion written down.

## Cohort and cadence

- **Selection.** Same persona, different workflows. No partner above about a third of traffic. Score candidates on the rubric: reject any with a `-` on evidence, intent, or technical owner.
- **Activation event.** First successful reconciliation match on production-shaped data. Define it before enrollment opens.
- **Cadence.** Weekly design sessions in weeks 1–2 (30–60 min, agenda sent ahead). Then a kickoff call and biweekly office hours. One private channel with a named owner.
- **Treat one partner's ask as a data point.** Ship a change only when it recurs across partners.
- **Changes.** Every change gets a changelog entry, a private one is fine. No changes after the freeze.
- **Outcome.** Tell enrolled accounts first, then the waitlist, then the public changelog. Templates are in the playbook's section 4.

## Enrollment gate

Sign all five before the first account enrolls:
- Program owner has steps 1–4 written.
- Design review at beta level.
- Security review.
- Legal sign-off: terms, data carve-out, precedence clause.
- Support channel staffed.

## Open questions

The interview isn't finished. Answers could change the plan:
1. Who is the named owner, and how many hours per week can they give?
2. How are your API versions surfaced (path, header or date)? Do SDKs have a pre-release channel? Does a changelog exist?
3. Does Orvantis have a ticket or workaround as evidence, and a named engineer?
4. Do enterprise contracts promise SLA or DPA coverage on "all services"?
5. Is reconciliation billable?
6. Are any beta, preview or early-access labels already live anywhere?

**Next (about 2 minutes):** answer question 1 with a name and weekly hours. Everything else follows from it. Drafting the charter and stage contract after that takes about 2 hours, with legal review on top.