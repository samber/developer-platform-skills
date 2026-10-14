# Ledgerwell developer portal: fix order for the March 15 review

**Start here:** this week, add funnel instrumentation. Everything else is ranked on what it shows.

This is the skill's workflow with the interview answers I have. I assume your portal already has self-service keys. Three open questions at the end could re-rank the plan.

## Diagnosis

- Activation is 212 / 1,840 = **11.5%**. 1,628 developers signed up and never made a successful call.
- Docs, catalog and pricing are already public. The skill's default first fix, ungated exploration, is done, so you start one rung up.
- The API isn't the problem. In every quantified rebuild case in the skill's references, only the portal and docs changed, and integration time still collapsed (agency-reported). The best-supported lever is the path from signup to first call.
- OAuth2 is the likely stall point. The skill's sourced practitioner guidance is that "auth is where most developers stall first". Webhooks add a second cliff after the first call.
- ⚠️ I haven't seen your funnel data, so where developers stall is a hypothesis until step 1 below.
- Rebuilding the portal, switching platforms and adding an AI assistant are not first moves for you. They don't attack the 88% gap.

## TTFC target

- Complexity class: OAuth2 plus webhooks. The skill's practitioner anchor is **under one hour** for this class. There is no universal benchmark.
- Use two milestones, because one number hides the webhook cliff:
  - **M1:** signup to first authenticated 2xx call, median under 15 minutes.
  - **M2:** signup to first sandbox settlement webhook received and verified, median under 60 minutes.
- Count a "successful call" as an authenticated 2xx against the sandbox. Use the same definition for the 212 baseline.

## Order of work

### 1. Instrument the funnel (week 1, one engineer, about 3 days)

- Add events for these steps: landing, signup, email verified, credential created, token obtained, first 2xx call, first webhook endpoint registered, first webhook delivered.
- Backfill the last quarter's 1,840 signups from gateway and auth logs.
- Segment the 1,628 non-activators by last step reached. Also split out who never created a credential and who got a token but never called.
- The largest drop-off gets fix priority, even where it differs from my ordering below. Funnel data outranks the default ranking.
- ✅ Gate: a stage-by-stage drop-off chart exists by end of week 1.

### 2. Auto-provisioned sandbox credentials with injected OAuth (weeks 1–3, engineer A)

- Create a sandbox OAuth client at signup. No approval step and no ticket.
- Inject the `client_id` and secret into every quickstart snippet and into the try-it console.
- Replace the OAuth explanation with one copy-paste token request: client-credentials grant, response shown, expiry stated.
- Add a visible test/live toggle on the key dashboard. Test is the default.
- Add sandbox data that makes reconciliation meaningful: a sample bank feed plus ledger entries that match and a few that don't.
- The credential and sandbox mechanics belong to `api-auth-key-management` and `api-test-mode-design`. Use those siblings for the details.
- This is the highest-value fix if step 1 shows the stall between signup and first call.

### 3. Ready-to-run collection and one quickstart (weeks 2–3, technical writer or platform lead)

- Ship a forkable Postman-style collection. It should have a token pre-request script and a working "reconcile this sample feed" call.
- Write one quickstart page that stops at first successful reconcile. Use the `developer-quickstart-guide` sibling for it.
- Postman reports about 1.7x faster first calls on its own platform. That is a vendor number: keep the ratio, don't copy the minutes.
- This is cheap and can run in parallel with step 2.

### 4. Webhook enablement (weeks 3–5, engineer B)

- Add a **Send test settlement event** button in the sandbox.
- Add a delivery log showing request, response and status, with a **Replay** action.
- Add a signature-verification snippet in the main languages, and local tunnel instructions.
- Show failure reasons in plain text, such as "your endpoint returned 401". This belongs to `integration-error-observability`.
- This closes the second cliff, and it matters because an integration isn't real until events flow.

### 5. Error and activation guardrails (week 5, both engineers, part-time)

- Link each auth error to a published error page, such as `invalid_client`, expired token or wrong scope. Use `api-error-design` for the codes.
- Add a "stuck?" prompt in the console after N failed token calls, linking to the matching error page and the support path.
- Make sure the changelog and a status link are visible. These are the maintained-platform trust signals.

### 6. Measure and report (week 6, platform lead)

- Report M1 and M2 medians for the signups since step 2 went live, plus the 7-day activation rate for those cohorts.
- Re-run the step 8 maturity check lightly across Pronovix's six focus areas. Set Priority 1/2/3 for the next quarter.
- Don't report the original 212 / 1,840 against a six-week-old cohort. That cohort won't have matured yet.

## Weekly plan

| Week | Engineer A (part-time) | Engineer B (part-time) | Platform lead / writer |
| --- | --- | --- | --- |
| 1 | Funnel events and backfill | Funnel events and backfill | Name the owner, set up the dashboard |
| 2 | Auto-provisioned sandbox OAuth client | Sandbox sample data | Collection |
| 3 | Credential injection into snippets and console | Webhook test-event button | Quickstart |
| 4 | Test/live toggle, token UX | Delivery log and replay | Error pages |
| 5 | Stuck prompts and guardrails | Signature snippets, tunnel docs | Changelog and status visibility |
| 6 | Bug fixes | Bug fixes | Cohort report to the board |

## Deliberately not in the six weeks

- **Personalized onboarding.** Highest effort, and the skill says a hard deadline demotes it. Revisit if you later sell to several distinct roles.
- **Rebuild or replatform.** The skill's default is a managed platform, and that's a later decision. It matters only if step 2 can't be built on your current stack.
- **AI answer assistant.** Worth adding later. The skill treats it as expected, but it needs good docs underneath. Its deflection numbers are vendor-reported, so baseline your tickets first.
- **RBAC and multi-tenant work.** Matters for enterprise or partner use, not for the first-call gap.
- **Public/partner portal split.** Not needed for this problem.

## What to tell the board

- The goal is activation, not signups. Say "signup to first successful call", not "docs views".
- I won't invent a target before baselining. After week 1, set an activation goal for the new cohorts. I'd frame the result as a trend, not a pass/fail.
- Name the portal's owner now. The skill lists "no named owner" as a top failure mode: portals without one decay quickly.

## Failure modes to watch

- Treating a fast first call as success. A first call isn't an activated integrator, so track repeat calls and webhook receipt in week 2 as well.
- Counting low-intent signups (students, scrapers, duplicate accounts) as activation failures. Check the segment in step 1 before promising a number.
- Hand-written snippets drifting from the API spec. Generate snippets and the reference from the spec.
- Building credential injection but leaving a manual approval step in place. Check for any ticket-gated action in the signup path.

## Open questions that would change the order

1. **Can a developer already create, rotate and revoke a key without a ticket?** If not, that becomes step 2's first task, and the portal-versus-docs-site dividing line applies.
2. **Does the step 1 funnel show most drops before credential creation, or after the first token?** Before means signup and verification friction first. After means the OAuth and snippet work is right.
3. **Who owns the portal after March 15?** If nobody, the gains will decay, and this should be settled before week 1.

**IA skeleton approval:** the skill requires validating the portal's IA section by section before finalizing. I haven't proposed a skeleton here because the first six weeks don't change the IA. If you want the solution-layer pages (reconciliation use cases, which Pronovix finds are the weakest layer on most portals) added after March, I'll propose the skeleton and ask you to approve it section by section first.