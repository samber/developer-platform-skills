# Quillstream beta terms: audit trail

I followed the `api-beta-program` skill but could not run its one-question-at-a-time interview or its section-by-section sign-off. Instead, every number below is a proposal and every unanswered interview question is in "Open items". Legal still has to sign the wording. This is not legal advice.

## 1. What was wrong with the draft

| Draft line | Problem | Fix |
|---|---|---|
| "covered by the standard 99.9% SLA" | Your MSA's SLA applies to "all Quillstream services", and this line makes the beta one of them. A breach would be a contract claim on an unfinished feature. | Say the preview has no SLA, and add a precedence clause. |
| "run on the same infrastructure" | It reads as a quality promise and adds nothing for the customer. | Delete it. |
| "Use at your own risk" | It sets no breaking-change notice, support, pricing or data rules. A label with no rows gets its guarantees set by the first escalation. | Use the stage contract in section 3. |
| Nothing on data or DPA | The feature returns signer name, email, IP address and timestamp, which is personal data by nature. The usual line, "don't send personal data", would make the beta unusable. And your DPA promises coverage on "all services". | Use synthetic data by default. Allow live data only under a signed per-account addendum (section 4). |
| Put the 99.5% SLO in the terms | Anything in the terms is a promise. 99.5% in writing sits below the 99.9% your enterprise customers already have, and it invites a claim when you miss it. | Keep the SLO out of the terms and out of the contract table (section 6). |

## 2. Decisions

1. **Shape: private preview.** It gives evidence from real integrations at a support load you control. Design partners are only worth the extra effort if the response shape is still open.
2. **Two stages only: Private preview and Public preview.**
   - The Early Access badge becomes Private preview.
   - The Beta badge becomes Public preview.
   - Audit trail starts in Private preview and does not go to Public preview before GA, because its payload is personal data and the DPA does not cover Public preview.
3. **Labs: retire the badge, don't adopt it as a stage.** Nobody wrote terms for it, so its callers assume promises nobody made. Run the rescue in section 5.
4. **Experimental: not now.** A third lane is justified only for a domain that changes faster than your preview cadence. A new label would also need all eleven rows below filled in and published. If the platform lead has a concrete fast-moving candidate, bring it back with the rows drafted. Until then, batch breaking changes into a new Public preview version.
5. **Pre-check:** if audit trail is an additive endpoint following an existing pattern, it could ship GA under your versioning policy with no beta. I assumed the new personal-data surface justifies a beta. Confirm that.

## 3. Company-wide stage contract (publish once, link from every beta)

All figures are proposals. Replace each with a number your team will honour.

| Row | Private preview | Public preview |
|---|---|---|
| Access | Invite. Allowlisted per organization after signed preview terms. | Self-opt-in in the dashboard on paid plans. |
| Availability | No SLA. Not on the status page. | No SLA. Incidents posted on the status page under "Preview". |
| Support | Shared channel with the product team, reply within 2 business days. | Forum category, best effort. |
| Breaking changes | Allowed. Direct notice to each technical owner at least 2 weeks ahead. | Only in a new preview version. The previous preview version stays available 90 days. |
| Removal | 30 days' notice. 90 days for accounts with a signed production exception. | 90 days' notice. |
| Production use | Unsupported, unless a signed production exception names the account. | Discouraged. Detected and contacted. |
| Pricing | Free. GA pricing announced at least [X] days before GA. | [Decide]. GA price published at public preview start. |
| Data and compliance | Test or synthetic data only. The DPA, certifications, data-location commitments and indemnity do not cover the preview, except under a signed data addendum. Preview data is deleted at the end of the overlap window. | Same, with no addendum route. No personal data. |
| Limits | [e.g. 1,000 audit-trail requests per day per organization]. Published. | [Decide]. Published. |
| Marking | `preview` version enabled per organization. SDK pre-release channel. "Private preview" badge on every operation and field. | Same version, self-opt-in. "Public preview" badge. |
| Discontinuation | Export of preview results for 30 days. Enrolled accounts told privately first. | Same, plus a banner on docs and dashboard. |

## 4. Publishable text: audit-trail preview terms

> **Audit Trail: Private Preview Terms**
>
> Audit Trail is in **private preview**. These terms apply to it in addition to our stage contract at [link]. If these terms conflict with your Master Services Agreement, Service Level Agreement or Data Processing Agreement, including any language covering "all Quillstream services", these terms prevail for Audit Trail.
>
> **Availability.** No SLA applies. Audit Trail is not covered by the Quillstream platform SLA and is not shown on the status page.
>
> **Support.** Via your shared preview channel. We reply within 2 business days.
>
> **Changes.** We may change or break Audit Trail during the preview. We will notify your technical owner directly at least 2 weeks before a breaking change ships. Every change is listed in the preview changelog.
>
> **Removal.** We will give at least 30 days' notice before removing Audit Trail or ending the preview. Accounts with a signed production exception get at least 90 days.
>
> **Production use.** Production use is unsupported unless a signed production exception names your account. We detect production use and will contact you.
>
> **Your data.**
> - Audit Trail returns signer names, email addresses, IP addresses and timestamps.
> - During the preview, use test-mode or synthetic envelopes only.
> - Our DPA, certifications, data-location commitments and indemnity do not apply to Audit Trail unless your account has signed the Audit Trail Data Addendum, which extends the DPA terms it names.
> - Preview data is deleted at the end of the overlap window after GA or discontinuation.
> - Do not rely on preview output as your legal record of a signing. Format and content may change.
>
> **Pricing.** Free during the private preview. We will announce GA pricing at least [X] days before GA.
>
> **Term.** The private preview ends on or before **[date]**. At the exit review we will either take Audit Trail to GA, extend it once, or discontinue it. We will tell enrolled accounts first.
>
> **Feedback and confidentiality.** [Feedback licence and confidentiality clauses: counsel to supply.]

### Audit Trail Data Addendum: outline for counsel

- It names exactly which DPA terms extend to the preview (processing instructions, security measures, subprocessors, deletion). Everything else stays excluded.
- It covers deletion of preview data at the end.
- It states who is controller and who is processor for signer data. Signers are your customers' counterparties, not your customers.
- It carries the precedence clause.
- Open question for counsel: IP addresses and emails of third-party signers raise a transfer and retention question. Decide this before any account signs.

## 5. Retiring Labs

1. **Inventory** the two Labs endpoints: first shipped (2023), last shape change, callers over the last 90 days, accounts with production traffic, owner.
2. **Grandfather every production caller.** Nothing they call changes until their endpoint has a decision.
3. **Decide per endpoint**, each with an owner and a date:
   - **GA as-is:** the shape is stable and has production callers, and the API design review passes at GA level with zero must-change findings.
   - **Next version with migration:** the shape needs breaking fixes or the review finds any must-change.
   - **Kill:** usage is near zero.
4. **Tell production callers privately** before any public relabel or notice.
5. **Retire the Labs badge publicly** once both endpoints have a decision. The Beta and Early Access badges can be renamed any time after the contract in section 3 is published.

## 6. The 99.5% SLO

- **Keep it internal.** It stays out of the terms and out of the contract table.
- **It has one job:** it is a GA criterion. GA requires the SLO to be met over a sustained window.
- **Optional:** you may tell partners in the kickoff call something like "our internal goal is 99.5%, a non-contractual target we may miss". Do not write it in anything customers sign.
- **Don't offer an SLA on the preview.** That route exists only for a frozen shape where enterprise buyers need production pilots. Neither condition holds here.

## 7. Open items (before the first account enrolls)

These come from the skill's interview. I could not ask them.

1. **Program owner and backup, by name,** and weekly hours. An ownerless beta becomes a perpetual one.
2. **GA target date.** The exit review, freeze and extension dates are derived backward from it. Rule: freeze is at least one partner release cycle before exit review, and the Public preview time box is at most 12 months.
3. **Is it billable?** This sets the pricing row.
4. **Version scheme and SDK pre-release channel.** If the SDK gains audit-trail methods and no pre-release channel exists, that blocks enrollment (raw-HTTP partners may still enroll). The preview must be a version suffix, a separate endpoint or an opt-in per organization, and GA reference docs and generated clients must exclude it.
5. **Cohort:** about 5 to 20 accounts, capped by capacity. Entry needs evidence of the problem, a planned integration, a named engineer, signed terms and intent to pay. A sales-requested account that fails those gets a design review under NDA, a sandbox with synthetic data and a place in the next wave.
6. **Enrollment gate, signed by:** the program owner (steps 1 to 4 written), a design review at beta level, a security review (scopes, authorization, abuse limits), legal (terms, addendum, precedence clause) and support (channel staffed at 2 business days).
7. **Per-account enablement,** with an expiry that alerts the owner on the exit date. It must never disable access by itself.
8. **Production-use detection** (live keys, sustained volume), so unexpected use leads to a conversation.
9. **Exit criteria in writing:** GA when all criteria hold, kill when any one fails, one extension of at most half the time box.

Should I draft the program charter next (exit criteria, backward timeline, enrollment record)?