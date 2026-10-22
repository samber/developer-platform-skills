# Perrin Labs: partner app onboarding and course plan

**Recommendation: don't gate submission on the 4-hour course.** Spend the budget on three things instead:
- a pre-submission validator;
- two short, hands-on modules aimed at the two failure causes;
- a credentialed course that earns a review fast lane.

Mandatory certification stays as a pre-defined escalation if the numbers later justify it.

I couldn't run the skill's interview here. The assumptions below are mine, so please correct any that are wrong.

## 1. Why not the mandatory gate

1. **22% is under the escalation bar.** The skill promotes mandatory pre-submission certification only when first-review fail rates stay above roughly 30-40% (a self-set threshold) after a validator already exists. You are below that bar, and I'm assuming there is no validator yet.
2. **The failures are mechanically checkable.** OAuth scope misuse and missing data-deletion webhooks are things a script can detect before submission. A validator catches them at the moment of submitting, which is cheaper than asking a partner to remember hours of video.
3. **A course can't show it's a knowledge gap rather than a docs gap.** The skill requires failure analysis to trace to partner knowledge gaps, not docs gaps, before it promotes mandatory certification. Missing deletion webhooks may simply be buried in the docs, and you haven't tested that.
4. **No major marketplace does this.** Shopify, Atlassian, Slack, HubSpot and Salesforce all keep education non-gating (platform-documented). Their reviews are where quality gets enforced.
5. **Your 22% is not a bad number.** Salesforce is reported at about 50% first-time fail (a third-party relay of its own estimate). Shopify's community threads describe 2-3 rejection cycles.
6. **The gate adds friction before the review step.** The only drop-off evidence available is from general developer-tool funnels, not marketplace data. It shows the largest leak before the first API call (80-95% drop-off after "Get Started"). A 4-hour wall before submit adds a leak at a new point.
7. **A gate hides its own cost.** You only see failures among people who submitted. Partners who bail at hour 2 never appear in your fail rate, so the metric could improve while the ecosystem shrinks.

**Caveat on the data.** I don't know the submission count. With about 60 listed apps over 14 months, last quarter's cohort may be small, so 22% could be a handful of apps. Check whether the fails come from a few repeat partners or from many first-timers before you commit.

## 2. Assumptions (the skill's interview)

| # | Question | Assumed answer | Changes the plan if... |
|---|---|---|---|
| 1 | What do partners build? | Marketplace apps | Private integrations also in scope: the validator must cover them |
| 2 | What exists today? | Signup and a live journey, being revisited | There is no sandbox at signup: fix that first |
| 3 | Time to a first working app? | Days | Weeks-to-months: guided stages earn more overhead |
| 4 | Data sensitivity? | High (B2B analytics, customer data) | It is low: deletion-webhook checks matter less |
| 5 | Who are the partners? | A mix of ISVs and small teams | All ISVs: add named managers for that segment only |
| 6 | Standing support capacity? | Unknown | There is none: office hours get deleted from the plan |
| 7 | Deadline? | This quarter, spend-or-lose budget | Hard external date: cut scope in section 4 |
| 8 | Goal? | Compounding ecosystem asset | One-off for specific waiting partners: skip the credential |
| 9 | Effort ceiling? | Budget exists; engineering hours unknown | Engineering is zero: the validator drops to a checklist plus a docs lint |

## 3. Journey design (skill steps 1-6)

1. **Stages.** Name them Plan, Build, Submit, Launch, Grow (Atlassian-style, adapted). Each stage gets an owner and a metric.
2. **Entry gate.** Keep self-service signup. If commercial sellers are on the platform, use agreement-split entry: build is ungated, selling needs an agreement and KYC/KYB.
3. **Provisioning.** Keep instant dedicated dev tenancy at signup, with OAuth test credentials. Audit that nothing sits behind review. The validator in section 4 depends on sandbox activity.
4. **Education posture.** Move from implied-mandatory to a **credentialed education loop**: named, displayable, non-gating, refreshed continuously.
5. **Support.** Docs plus forum first. Add office hours only if you have a platform engineer to staff them. They fit your recurring hard step, which is the review gate.
6. **Commercial decisions late.** Pricing and monetization model are asked at launch, never at signup.

**Disclose every post-launch threshold in the onboarding docs.** Publish the review checklist there too, in the same words the reviewers use.

## 4. What the budget buys (build order)

1. **Failure analysis (weeks 1-2, low cost).**
   - Pull every first-pass rejection from the last 2-4 quarters.
   - Tag each by cause, partner type, new vs repeat partner, and whether the docs covered it.
   - This decides whether any of the rest is a docs fix, a tooling fix or a knowledge fix.
2. **Pre-submission validator (weeks 2-8, the biggest item).** Partners run it against their sandbox app before the submit button.
   - **OAuth scope check:** requested scopes against the endpoints the app actually called in the sandbox, flagging unused or over-broad scopes.
   - **Deletion webhook check:** a registered endpoint that responds correctly to a synthetic deletion event.
   - Its output reuses the reviewers' wording, with a link to the fix.
   - Run the same checks in review as a pre-filter, so the validator and reviewers can't drift.
3. **Two targeted modules (weeks 4-9).** About 20-30 minutes each, built around the sandbox rather than slides. One covers least-privilege OAuth scopes, the other data-deletion webhooks. Each ends in a short hands-on check, and each is linked from the matching validator error.
4. **The "Building on Perrin" course, re-cut (weeks 6-11).**
   - Split the 4 hours into modules. The two above come first, and the rest stays optional.
   - Add an assessment that issues a credential, shown on the partner profile and listing.
   - **Incentive instead of gate:** completing it earns something concrete. A review fast lane is the strongest candidate, if reviewers can honor it.
5. **Funnel instrumentation (weeks 1-4, before anything ships).** The baseline has to exist before the changes land.

Order matters: instrumentation and failure analysis come first because they set the baseline and tell you where to aim items 2-4.

## 5. Funnel instrumentation (step 7)

Track four checkpoints:
1. signup → sandbox/credentials provisioned
2. provisioned → first API call
3. first API call → first app submitted
4. submission → approval

Also track:
- **Time-to-first-submitted-app.** This is a self-defined metric, so label it that way in every report.
- **First-pass fail rate by cause**, with the OAuth-scope and deletion-webhook categories split out.
- **Resubmission cycles per app.**
- **Submissions per quarter.** This is the guardrail against a funnel that gets cleaner by shrinking.
- **Validator adoption and pass rate**, and **module completion**.

Baseline against your own first quarter and watch quarter-over-quarter trend. The skill sets no absolute pass bar, so I'm not inventing one.

**Don't read course completers vs non-completers as proof.** Partners who finish a course differ from those who don't. Treat that comparison as a hint only.

Working thresholds from the skill:
- If checkpoint 2 takes longer than about 10 minutes, fix that friction before anything else in this plan.
- If time-to-first-submitted-app far exceeds review duration, the bottleneck is docs and enablement, not the review team.

## 6. Escalation rule for the mandatory gate

Decide this now, so the debate isn't reopened on opinion:

- Revisit **mandatory certification** only if, after the validator has run a full quarter, the first-review fail rate is above about 30-40% **and** the failure analysis traces to partner knowledge gaps, not docs gaps.
- If it triggers, prefer the **narrowest version**: require the relevant 20-30 minute module only for a partner's **resubmission** after failing in that category. Don't use the full 4-hour course.
- Use this to answer the head of ecosystem directly: the gate isn't rejected, it has a trigger.

## 7. Risks and open items

- **Submission count and concentration:** unknown, see the caveat in section 1.
- **Reviewer capacity** to honor a fast lane: confirm before promising it.
- **Validator maintenance:** every API or policy change has to update it, so give it an owner.
- **Sandbox fidelity for the webhook check:** the validator can only test what the sandbox can fire.
- **Engineering hours for the validator are unconfirmed.** If they aren't available, fall back to the docs-lint and checklist version (see the assumptions table).

## 8. Next step

Send me the last 2-4 quarters of first-pass rejections (cause, partner, and whether it was their first submission) and the engineering hours available for the validator. I can then turn this into a dated 12-week plan with owners.