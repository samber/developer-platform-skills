# API governance and the v1 sunset

## Summary

1. **Governance:** Don't build a council. Ship a lightweight policy, a CI check, and one named owner within a week, and don't freeze shipping.
2. **v1 sunset:** Keep March 1 as the public date, but earn the cutoff instead of just flipping it. Run brownouts, do personal outreach to all 31 accounts, and grant a few written, dated, per-account extensions. Set a hard final date.

One flag first: today's date is 2026-10-03, so March 1 is about five months away, not six weeks. If you meant a different date, the plan below still works with the checkpoints shifted.

## Front 1: the governance council

### Why not the full version

- A council, a charter, review rotations, and a Google-scale compatibility doc suit hundreds of engineers and many API teams. You have 12 people and one API.
- A rotation across a handful of engineers means each person reviews rarely, so nobody builds the skill.
- A freeze on shipping costs a quarter of product progress to fix a risk that a checklist handles.
- The VP's real worry is probably "we make breaking changes carelessly." A policy plus enforcement answers that. A committee does not.

### What to propose instead (about one week of work)

1. **One-page compatibility policy.**
   - It lists what counts as breaking: removed or renamed fields, new required inputs, changed types, changed error codes, changed semantics.
   - It lists what counts as non-breaking: additive optional fields and new endpoints.
   - It states the versioning rule, and the deprecation rule: minimum notice period, `Deprecation` and `Sunset` headers, a migration guide, and per-account usage tracking.
2. **Automated breaking-change check in CI.** Use `oasdiff` or an equivalent on the OpenAPI spec. A breaking diff fails the build unless a named owner approves it. This enforces the policy, which prose alone never does.
3. **One named API owner.** That person gives an async review of about 30 minutes on any public API change. Add a backup. Don't build a rotation yet.
4. **Adopt, don't author.** Reference Google's AIP or similar guidelines for naming and pagination, and write down only your deviations.
5. **A PR template checklist.** Is it breaking? Is the spec updated? Are the docs updated? Is there a deprecation path?

### How to pitch it to the VP

- Frame it as "Google-grade enforcement at our size." The CI gate and the policy are the real "like Google" part. The committee is not.
- Use the v1 sunset as the case study. It shows the exact failure the policy prevents.
- State the trigger for revisiting. Reconsider a council at roughly 30 or more engineers, or when more than one team ships API changes.
- Ask for an explicit "no freeze." Shipping continues under the checklist.

### Ask to confirm with the VP

- Does "before we ship anything else" mean a hard freeze, or a requirement that nothing ships without the policy? Offer the second.
- Does the migration tooling for v1 customers count as "anything else"? It should be exempt.

## Front 2: the v1 sunset

### Principle

You honored the window, and that is your protection. But 14% of traffic across 31 accounts is not a fringe tail, and ops being right on process doesn't change who gets hurt. The aim is to cut off the stragglers who can't be moved, not to be proven right at 00:00 on March 1.

### Step 1: triage the 31 accounts this week

Pull these for each account:
- share of v1 traffic
- revenue and contract status
- last-seen date
- which endpoints they call
- whether anyone has engaged with the migration guide

Expect a power law, where a few accounts carry most of the 14%. Sort them into three buckets:
- **Dormant or unreachable:** safe to cut on the date.
- **Engaged and migrating:** needs a short runway.
- **Active, silent, and valuable:** needs a person to call them.

### Step 2: personal outreach, not another announcement

- A named human (engineer or CSM) contacts every account that carries real traffic.
- Ask what blocks them. Offer migration help, a sandbox, or a pairing session.
- Log every contact. You need that record both to defend the cutoff and to learn from it.
- Cadence: first contact now, a follow-up at T-60 days, a final notice at T-30, and a last notice at T-7.

### Step 3: brownouts before the cutoff

Brownouts are scheduled, announced, temporary v1 shutdowns. They flush out forgotten integrations that nobody read the email about.
- Run three: roughly 1 hour at T-4 weeks, 4 hours at T-2 weeks, and 24 hours at T-1 week.
- Announce each one by email and in the dashboard.
- Run them during business hours, with the team watching.

### Step 4: make the cutoff itself safe

- Return **410 Gone**, with a JSON body containing a migration link and a support contact. Don't drop connections or return a bare 5xx.
- Keep sending `Deprecation` and `Sunset` headers until then.
- Make the kill switch **reversible in under five minutes**, and write the rollback runbook.
- Flip it on a weekday morning, with people on call. Avoid a Friday or a weekend.
- Add a **per-account allowlist** to the switch so you can exempt specific accounts without a code change.

### Step 5: the extension rule

- No global slip. The public date stays March 1.
- Active, engaged accounts that aren't done can get a **written, dated, per-account extension**, 30 to 45 days at most, with a named owner and a milestone.
- Set a **hard final date** for the allowlist, for example April 15. Then it is removed, with no further extensions.
- This costs little: if v1 is cheap to keep running, a few allowlisted accounts are a small price against churning a paying customer.

### Checkpoints

| When | Decision |
|---|---|
| This week | Account triage done, outreach started |
| T-4 weeks | First brownout, go/no-go on the bucket plan |
| T-2 weeks | Review remaining traffic by account. Decide which extensions to grant |
| T-1 week | Final notice, runbook rehearsed |
| March 1 | Flip. Allowlisted accounts stay |
| Hard final date | Remove the allowlist |

### What to tell ops

- March 1 stays the date, and it will be enforced.
- The flip comes after brownouts and outreach, with a rollback ready.
- A small set of named exceptions is the price of not churning paying customers. It is time-boxed and has an end date.

### Where the two fronts connect

The sunset is your live test of the new policy. Write down what you learn (usage tracking by account, outreach cadence, brownouts, extension rules) and fold it into the one-page deprecation section. That gives the VP a concrete result to show, instead of a charter.