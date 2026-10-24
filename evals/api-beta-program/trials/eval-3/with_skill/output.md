**Next action:** don't build the proposal as written. Fix three things first (below), and answer the five questions at the end.

## Verdict on the three proposals

| Proposal | Verdict | Why |
|---|---|---|
| One header `X-Meterline-Beta: forecast,alerts` | ❌ Change | Wrong mechanism, and it couples two features. |
| Beta operations in main OpenAPI | ❌ Reject | Stable SDKs would ship beta methods to everyone. |
| "Beta" note on docs overview | ⚠️ Not enough | Label each operation and field too. |

### 1. Header problem

- A request header fits one field. It becomes a maintenance trap as flags accumulate.
- Graduating it later breaks pinned clients that still send it.
- One header for both features ties their fates together:
  - The forecast shape is still being argued. Its exit date and breaking changes will differ from alerts'.
  - Graduating or killing one forces a decision on the other.
- A request header does nothing for webhooks. Alerts are deliveries to the customer, not requests from them.
- A header anyone can send is self-serve. You want per-account control instead.

**Do this instead:**

- **Forecast:**
  - You already version by date, so use a dated preview version: `Meterline-Version: 2026-03-01.preview`.
  - Enable it per organization, not per user and not by percentage.
  - An org that is not enrolled gets an explicit error, never a silent ignore.
  - Each breaking change gets a new preview version (for example `2026-05-12.preview`).
- **Alerts:**
  - Opt in per webhook endpoint, or use preview event types such as `usage.threshold_alert.preview`.
  - Mark the stage in every delivery, for example a `Meterline-Stage: private-preview` header and a `stage` field in the payload.
  - Also enable per organization.
- Don't add an `X-` prefix to any new header. Your existing version header doesn't use one.

### 2. OpenAPI and SDK problem

- If beta operations go into the main spec, your next regular release publishes beta methods to every stable npm and PyPI user.
- Keep them out of the GA spec:
  - Use a separate spec artifact, or tag the operations and exclude them when generating GA clients.
  - Generate beta SDKs from the beta artifact only.
- **No prerelease channel means SDK enrollment is blocked.** Six of your eight accounts use the SDKs. The skill says that blocks enrollment for any beta that adds SDK methods or types.
- Your options:
  1. Set up a channel before enrolling those six. It can be a separate package such as `@meterline/sdk-beta` and `meterline-beta`, or a prerelease tag (npm dist-tag `beta`, PyPI `b1`). If you use tags, guard so `latest` never moves. Plan the setup with `sdk-package-publishing`.
  2. Enroll only the partners who integrate over raw HTTP now. SDK partners wait for the channel, and it must exist before any public preview.
- Skip SDK support for beta event types. Webhook payloads are just JSON for partners.

### 3. Docs

- Add a "Preview" badge on every beta operation, field, event type and webhook page.
- Keep the overview note and add the per-operation labels. The overview note alone gets missed.

## Recommended shape

**Run two tracks under one stage contract.** Each track gets its own charter, exit date and freeze date.

| Track | Shape | Size |
|---|---|---|
| Threshold alerts (new webhook surface) | Private preview | 5-8 accounts, capped by capacity |
| `usage.forecast` (shape open) | Design partners, or hybrid: private preview with the first sessions run design-partner style on the open question | 3-5 accounts |

- Choose design partners for forecast because the shape is still being argued.
- Pick 3-5 accounts for forecast from the 8, chosen for different workflows.
- Alternative: one private preview for both. This is simpler, but it is weaker evidence on forecast and keeps the two features coupled.
- Public preview comes later, after private preview. It does not replace it.
- Ranking: effort and value run design partners > private preview > public preview. Efficiency runs private preview > design partners > public preview.

## "Enroll 8 next week" is at risk

Steps 1-5 must be written and signed off before the first account enrolls. Today none of them exists. This is my judgment, not a fact about your team.

**Enrollment gate, all required:**

1. **Program owner:** named, with a backup.
2. **Stage contract and charter:** written, including exit criteria.
3. **Design review:** passed at beta level, with `public-api-design-review`.
4. **Security review:** auth scopes, authorization checks, abuse limits.
5. **Legal and support:** pre-GA terms signed, and the support channel staffed.

**Entry criteria per account:**

- Evidence of the exact problem (a ticket or a workaround in their code).
- A real integration planned inside the window.
- A named technical owner.
- Signed pre-GA terms.
- Intent to pay, if billable.

**Realistic plan:**

- Enroll next week only if the gate is signed. Start with the raw-HTTP accounts.
- Enroll SDK accounts when the channel exists.
- If sales requested any of the 8 and they fail the first three entry criteria, offer a substitute. Options are a design review under NDA, a sandbox with synthetic data, the freeze and GA dates, and first place in the next wave.

## Stage contract

Publish one table per company, not per feature. Fill all 11 rows. An empty row is a promise you'll be held to anyway.

Draft for private preview. The figures are illustrative, so replace them with what you will honour:

| Row | Private preview |
|---|---|
| Access | Invite. Allowlisted per organization after signed terms. |
| Availability | No SLA. Not on the status page. |
| Support | Shared private channel. Named owner replies within 2 business days. |
| Breaking changes | Allowed. Direct notice to each technical owner at least 2 weeks ahead. Changelog entry every time. |
| Removal | 30 days' notice. 90 days for accounts with a production exception. |
| Production use | Unsupported unless a signed exception names the account. Detect it server-side (live keys, sustained volume, deliveries to production hosts). Detection starts a conversation. |
| Pricing | Free. GA pricing announced by a stated date. |
| Data and compliance | See below. |
| Limits | Published caps (for example, N alert rules per org, N forecast calls per day). |
| Marking | Preview version, preview event types, `stage` field, SDK beta channel, badges. |
| Discontinuation | Data export. Per-account list of operations called. Banner on every entry point. |

**Data row:** you're a metering API, so payloads probably carry customer identifiers or billing-relevant data. If so, "no personal data in preview" makes the beta unusable. Offer test-mode or synthetic data by default. Allow live data only under a per-account addendum that legal signs, and a precedence clause that overrides any MSA or DPA promising coverage on "all services".

**Alerts are billing-adjacent.** A wrong alert looks like a wrong bill. State that clearly in the terms.

## Exit criteria

Write these before anyone enrolls. Set the dates backward from your GA target.

| Date | Rule |
|---|---|
| Exit review | A dated review, ideally within 6 months. Past 12 months it is a perpetual beta. |
| Freeze | At least one partner release cycle before the exit review. |
| Mid-point check | Halfway between enrollment close and exit review. |
| Overlap ends | GA plus at least one partner release cycle, or the GA deprecation window if production traffic sits on the beta. |

- **GA when all of these hold:**
  - Minimum accounts activated.
  - At least one account on production-shaped traffic on the final shape.
  - No open blocker.
  - Design re-review passed.
  - Docs and SDKs ready.
  - GA pricing set.
  - Internal SLO met for a sustained window.
- **Kill when any of these holds:**
  - Activation below the floor.
  - Problem disproved.
  - Cost to serve above what GA pricing can carry.
- **Extension:** one only, at most half the original time box. A second extension is a deferred decision.
- **Flag expiry:** the beta flag alerts the owner on the exit date. It never disables access by itself.
- **Define the activation event per account before enrollment opens.** For example: first alert delivered and acknowledged by the partner's system, and first forecast call from a production-shaped workflow.

## Feedback and change rules

- **Private preview:**
  - Kickoff call, then biweekly office hours, plus one private channel.
  - Name one owner and a response time.
- **Design partners (forecast):**
  - Weekly or biweekly 30-60 minute sessions with the agenda sent ahead.
  - Ask what they built, what blocked them, what they worked around, and what they would pay for.
- **Requests:** treat one partner's request as a data point. Ship it only if it recurs or matches the problem statement.
- **Concentration:** no partner should dominate beta traffic or fill the backlog.

## Five answers I need to finish the charter

1. **Owner and capacity:** who owns this by name, and how many hours a week do they and engineering have for partners?
2. **GA target and horizon:** what is your GA date, and is this a one-off or the template for every future beta? If it's the template, write the company-wide stage contract first.
3. **Data and contracts:** does beta traffic carry personal or regulated data? Do enterprise contracts promise SLA, DPA or certification coverage on "all services"?
4. **Existing labels:** do you use preview, beta or early-access labels anywhere today (docs, console, contracts)? How old is the oldest? If one is already live with no exit date, run the existing-beta rescue first.
5. **Why beta and billing:** are specific customers or a sales deal driving this? Is either feature billable? Is the alerts payload shape decided, or open too?

If it helps, I can draft the full charter and the 3-column stage contract next. Answer the five questions above and I'll start there.