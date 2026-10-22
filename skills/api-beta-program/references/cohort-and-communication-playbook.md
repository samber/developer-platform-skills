# Cohort and communication playbook

## Contents

1. Selection rubric
2. Pre-GA terms checklist
3. Free-rider and overfit signals
4. Outcome message templates
5. Rationalizations

## 1. Selection rubric

Score each candidate account `+`, `0` or `-` per row; admit only accounts with no `-` on rows 1-3.

| Row | `+` | `-` |
|---|---|---|
| 1. Evidence of the problem | ticket, issue or workaround in their code | "sounds interesting" |
| 2. Integration intent | real build planned inside the window | evaluation only |
| 3. Technical owner | named engineer attends the cadence | only a buyer or a rep |
| 4. Workflow diversity | adds a workflow the cohort lacks | duplicates an existing partner |
| 5. GA fit | the account you want as a customer at GA | first signup on the waitlist |
| 6. Concentration | preview: stays under about a third of beta traffic; design partners: asks would not fill the backlog alone | would dominate |
| 7. Downstream reach | direct integration, or a platform partner with a plan to notify its own customers | redistributes to many accounts with no notice path |

## 2. Pre-GA terms checklist

Route final wording to counsel. Terms that hold up are the ones that cover IP, confidentiality, data and pricing; participation duties are rarely enforced, so the cadence is a relationship, not leverage.

- Reference to the stage contract.
- Feedback licence: the vendor may use feedback without obligation.
- Confidentiality: scope, and whether the partner may publish benchmarks or test results.
- No SLA, no support beyond the stated channel.
- Data: what may not be sent; any DPA or certification carve-out; whether beta data carries into GA or gets deleted.
- Precedence: these terms override MSA or DPA language promising coverage on "all services".
- Liability cap and indemnity exclusion for the preview.
- Production exception, when granted: the account, the surface, and the notice it earns.
- Pricing during the beta and how GA pricing gets announced; any partner discount with its term.
- Term and termination: program end date, either side may exit on short notice.
- Outcomes: GA, extension or discontinuation, with the notice each carries.
- Optional: reference or case-study rights at GA, negotiated now because launch is too late to ask.

## 3. Free-rider and overfit signals

- No activation event after the first month: the account is evaluating, not building.
- Requests arrive only through a rep: access was a sales tool.
- One partner's asks fill the backlog: the program is drifting into custom development; log the ask and move on unless it recurs.
- The partner cannot say what they would pay at GA: treat their usage as reach, not demand.

## 4. Outcome message templates

**GA (to enrolled accounts, before the public changelog):**

```
Subject: <Feature> reaches GA on <date> - what changes for <account>

<Feature> leaves private preview on <date>. Your integration calls <operations>.
What changes: <beta path or version> becomes <GA path or version>; <field changes>.
Overlap: the beta surface keeps working until <date>.
Pricing: <GA price, any partner discount and its term>.
Migration guide: <link>. Questions: <channel>, answered by <team>.
```

**Extension:**

```
Subject: <Feature> preview extended to <new date>

The exit review on <date> found <criterion not met>. We are extending once, to <new date>.
What changes in the extension: <scope, cadence, limits>.
Nothing changes in your access or terms.
```

**Kill:**

```
Subject: <Feature> preview ends on <date>

We are discontinuing <feature>. Reason: <one paragraph, plain language>.
Your account calls <operations>; these stop working on <date>.
Before then: export your data with <tool or link>; consider <named alternative>.
Billing for <feature> stopped today (or: is credited from today, per your order form).
We will contact you on <date> to check your migration.
```

**Sales substitute (for a requested account that fails the entry criteria):**

```
Subject: <Feature> - early engagement for <account>

<Feature> reaches GA on or about <date>; its contract freezes on <date>.
Preview access is limited to accounts with a planned integration and a named engineer.
What we can offer now: a design review with your integration architect under NDA,
a sandbox with synthetic data, and first place in the next enrollment wave.
```

**Waitlist reply:**

```
Thanks for your interest in <feature>. The current cohort is full; we open the next
wave or public preview around <date> and will write to you then. Meanwhile: <docs link>.
```

## 5. Rationalizations

| Shortcut | Why it fails |
|---|---|
| "Call it beta, define it later." | Undefined rows get defined by the first angry customer, usually as GA promises. |
| "The big customer needs it; let them run production." | Production use without a signed exception and notice rules freezes the shape for one account and blocks every fix. |
| "Set the flag to expire on the exit date." | An expiry that disables access cuts every account at once on that date; expiry alerts the owner, the outcome decides access. |
| "Signups prove demand." | Signups measure reach; only activation and production use measure demand. |
| "Extend it again, we're close." | A second extension is a deferred decision; perpetual betas lose enterprise buyers and teach integrators the label means nothing. |
| "Turn off the flag; nobody uses it." | Production detection, not belief, says who uses it; a silent 404 breaks integrations you never knew about. |
| "Sales can promise early access." | Access as a closing tool fills the cohort with accounts that never activate. |
