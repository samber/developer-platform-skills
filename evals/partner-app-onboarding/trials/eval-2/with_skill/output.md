# Partner program for Northvale: where I'd push back

**Biggest pushback:** the review comes too early. Partners wait 2-4 business days, with no sandbox and nothing to build, before they've produced anything worth reviewing. That is the "sandbox behind the review gate" failure mode. Move human review to the end, where it protects your utility customers.

I couldn't run the skill's interview, so I made assumptions. Corrections are listed at the end.

## Assumptions

| Question | Assumed answer | Source |
|---|---|---|
| Q2: what exists today | Designing from zero | You said so |
| Q4: data sensitivity | **High**, because utilities are regulated critical infrastructure | Inference |
| Q5: who the partners are | A mix, probably integrators and commercial ISVs | Guess |
| Q1: what partners build | Private integrations for shared customers | Guess |

## Pushbacks, ranked

### 1. Registration is a reviewed gate

- **What's wrong:** four of the five ecosystems studied let anyone sign up with a form. Build access is granted before any human review. Review sits at app submission, where it protects end customers.
- **Why it costs you:** your whiteboard copies the Salesforce shape, which is the outlier. Its cost scales with every applicant. It also needs a countersigned company-level agreement and a documented admission decision per applicant, and removing an admitted partner means terminating a contract.
- **When a reviewed gate is justified:** when build complexity is weeks-to-months, or when you must know who is building before granting any data access.
- **Your case:** the second condition is plausible for utilities, but it doesn't justify the whiteboard design. A sandbox with synthetic data grants no data access. You can stay ungated at the sandbox and gate where real data enters.
- **Proposed fix:**
  - Self-service signup with a click-through program agreement, which needs one legal sign-off and then none per partner.
  - Instant sandbox.
  - Gate production access and customer-tenant installs, which is where the sensitivity actually lives.
- **Evidence caveat:** the drop-off figures (80-95% leave after "Get Started") come from general developer-tool research, not marketplace-partner data. They show the direction but not your numbers.

### 2. Credentials arrive by email after approval

- **Timing:** provision the sandbox and credentials at signup, not after review. A free dev tenant with no time limit and no payment info is what "decouple building from approval" looks like as infrastructure.
- **Delivery (my addition, not from the skill):** don't email credentials to a utility-sector partner. Issue them in-portal, with MFA, rotatable.
- **Cost check:** a dedicated tenant per partner has real cost for field-service software. That depends on your effort ceiling (Q9), which I don't have.
- **Fallback:** if tenant cost is prohibitive, step down to a shared multi-tenant dev environment with synthetic data. Don't gate on review to save cost.

### 3. The security review is a surprise at the end

- **What's wrong:** your whiteboard has "submit for security review" as the last box. Partners meet the requirements at first rejection.
- **Evidence:** developer threads at two studied platforms describe 2-3 rejection cycles. One gated platform's own estimate is a ~50% first-time fail rate, relayed by third parties.
- **Fix:** publish the review checklist inside onboarding docs, and ship a pre-submission validator, an automated checker partners run themselves.
- **When to escalate:** if first-review fail rate stays above roughly 30-40% (self-set threshold) after the validator exists, then consider heavier education.
- **Out of scope here:** review mechanics (SLA, fee, criteria) belong to `app-marketplace-review`.

### 4. No named stages, owners, or metrics

An unnamed stage never gets an owner or a metric. Your whiteboard has five boxes and no stage model.

- **Atlassian's model:** Plan, Build, Launch, Grow.
- **Salesforce's model:** seven milestones.
- **My suggestion:** adapt Atlassian's, with sandbox access landing in Plan/Build and review at Launch.

### 5. Missing from the whiteboard entirely

- **Education:** make it optional and parallel, available from day one and required by nothing. All five ecosystems do this. Don't gate submission on certification.
- **Support:** start with docs plus a community forum. Add office hours for the security review, since that's the recurring hard step. Use named partner managers for commercial ISVs only.
- **Commercial decisions:** keep pricing and seller or distribution agreements at launch, never at signup. If you sell through partners later, this becomes a seller track: agreement signature plus KYC/KYB, gating selling and never building.
- **Hidden thresholds:** disclose any post-launch bars in the onboarding docs, such as install counts or tenure before certification or featured placement. Partners who hit them after "finishing" onboarding churn.
- **Funnel instrumentation:** instrument four checkpoints before launch:
  1. signup to sandbox provisioned
  2. provisioned to first API call
  3. first API call to first app submitted
  4. submission to approval

  Time-to-first-submitted-app is a metric you coin, so label it self-defined in reports. Also baseline against your own first quarter and track the trend, because there's no industry pass bar.

## What I'd keep

- Review of the company before it can sell or touch customer data. That belongs in the design, just later.
- A security review before listing. For your sector, that's non-negotiable.

## Proposed shape (v0, pending your answers)

1. Signup form plus click-through agreement.
2. Instant sandbox with synthetic data and in-portal credentials.
3. Build, supported by docs, forum, an optional learning track, and a published review checklist.
4. Pre-submission validator.
5. Security review, with office hours.
6. Production and customer-tenant access, gated here.
7. Commercial or seller agreement at first listing.

## Answers that would change this

- **Q3, time to first working app:** if it's weeks-to-months because of tenant complexity, a guided pre-launch stage becomes justified.
- **Q4, data sensitivity:** if partners need real utility data to build at all (not just to ship), the reviewed gate gets promoted back. The synthetic-data sandbox split is the thing to test first.
- **Q5, who the partners are:** if mostly commercial ISVs transacting through you, switch to agreement-split entry.
- **Q7-Q9, deadline, goal, effort ceiling:** these re-rank the rungs and can delete some outright.

Your answers to Q3, Q4 and Q5 would let me firm this up. I haven't saved any of these choices to memory, because none are validated yet.