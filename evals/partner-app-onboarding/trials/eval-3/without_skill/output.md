# Plan: Building on Perrin: cut first-pass review failures

## Next action this week

Pull the review data for last quarter's submissions and answer three questions. Do this before spending course budget.

1. How many submissions and how many unique developers? Marketplace size suggests a small n, so 22% may be only a handful of apps.
2. How many failures were repeat developers, and how many had already taken the 4-hour course?
3. How did the failures split by reason? OAuth scope misuse and missing deletion webhooks are the two big ones. What is the rest?

## Recommendation

Don't make the 4-hour course the gate. Make the **automated preflight check** the gate. Use a short course to support it.

Why:
- **Both top failure modes are mechanical.** A scope check compares requested scopes with the endpoints the app calls. A deletion webhook check sends a test deletion event and verifies the response. A linter catches both in minutes, with no knowledge test.
- **A course can't prove an app is compliant.** A developer can pass the quiz and still ship an app that requests `admin` and has no webhook. Only a check run on the actual app proves compliance.
- **The cost of a gate lands on a small marketplace.** With about 60 apps after 14 months, every developer who abandons submission is a large share of growth. A 4-hour mandatory course adds friction for every submitter, including the 78% who pass first time.
- **Nothing shows that the course reduces failures.** Compare failure rates for developers who took it with those who didn't. The comparison is confounded, because motivated developers self-select into courses, but it is still the first evidence you can get.

If the head of ecosystem still wants a mandatory element, require it only where it targets the failures: a short module plus quiz, required once per developer account before their first submission.

## Workstreams

### 1. Preflight checks (highest leverage, build first)
- **Scope linter.** Compares the requested OAuth scopes with the API calls observed or declared. It flags unused or over-broad scopes and says which scope to drop.
- **Deletion webhook tester.** Sends a signed test deletion event to the app's endpoint. It checks the response code, idempotency, and the time to acknowledge.
- **Manifest validator.** Covers the remaining failure reasons found in the data pull.
- **Delivery.** Ship it as a CLI plus a "Run preflight" button in the submission UI.
- **Gate.** Submit stays disabled until preflight passes. This blocks the actual failure modes and costs compliant developers about a minute.
- **Error messages.** Each failure links to the exact doc section and a code sample.

### 2. Course rebuild
- **Split the 4 hours into modules** that a developer can take non-linearly.
  - **Core (about 45 min):** OAuth scopes (least privilege, worked examples of misuse), data deletion webhooks (the contract, a reference implementation, testing), and the review checklist.
  - **Optional tracks:** everything else, taken by interest.
- **Build around the failures.** Use anonymized real rejected submissions as case studies: "here's the app, here's why it failed, fix it."
- **Make it hands-on.** Learners run the preflight against a sandbox app and fix it. This beats multiple-choice questions.
- **Assessment.** A short practical check: fix a broken sample app until preflight passes. No trivia quiz.
- **Format.** Text and code first, with video only where it earns its cost. It is easier to keep current when scopes or APIs change.

### 3. Docs and templates
- **Starter template** with correct scopes and a working deletion webhook handler. Developers start compliant instead of learning to become compliant.
- **Review checklist** published verbatim. Reviewers and developers use the same list.
- **Anonymized rejection reasons** page, updated each quarter.

### 4. Gate decision (end of quarter, with data)
Run the gate as a pilot. Make preflight mandatory for everyone from launch. Offer the core module as recommended, and require it only for first-time developers. After 6 to 8 weeks, compare against last quarter's baseline.

## Timeline (today is 2026-10-09; quarter ends 2026-12-31)

| Weeks | Work |
|---|---|
| 1-2 (Oct 12-23) | Data pull, failure analysis, interview 5 to 8 recent rejected developers, decide scope |
| 3-6 (Oct 26-Nov 20) | Build the scope linter and webhook tester, internal dogfooding with reviewers |
| 5-9 (Nov 9-Dec 11) | Write the core module and sandbox exercise, test it with developers who have open or recent submissions |
| 8-10 (Nov 30-Dec 18) | Preflight gate live, course core released |
| Jan | Read results (the holiday slowdown lowers submission volume and weakens the signal) |

Interviews matter here. Ask rejected developers whether they didn't know, couldn't find it, or misread the docs. That decides whether the problem is education, docs, or tooling.

## Budget allocation (suggested split of the course budget)

- About 50% on the preflight tooling, which is engineering time.
- About 30% on the core module, sandbox exercise, and case studies.
- About 10% on docs and templates.
- About 10% reserved for the optional tracks, and only if the data justifies them.

I don't know your budget figure, so these are proportions. Adjust them once the data shows which failure reasons dominate.

## Metrics

- **Primary:** first-pass review pass rate. Baseline is 78%. Target is 90% or higher within two full quarters. Set the target after you see n.
- **Secondary:** median time from submit to approval, reviewer hours per submission, and the share of failures from OAuth scope or deletion webhook (target near zero).
- **Guardrail:** submission volume and developer drop-off at the submit step. If submissions fall more than the pass-rate gain justifies, the gate is too heavy.
- **Course health:** core module completion rate, and failure rate for completers versus non-completers.

## Risks and open questions

- **Small n.** With about 60 apps, quarterly rates move on one or two submissions. Track the count alongside the percentage.
- **Static analysis limits.** Scope checks can't see every runtime call. Start with declared-versus-requested scopes and expand coverage over time.
- **Maintenance.** Preflight rules and course content need an owner when scopes or policies change.
- **Head of ecosystem buy-in.** The ask is a mandatory course. Show them the data and frame the preflight gate as a stronger enforcement of the same goal. It fixes the two named failures and does not depend on whether someone sat through four hours.
- **Open question:** does the existing 4-hour course already cover these two topics? If it does and failures continue, that is strong evidence against making it mandatory.

## Decisions I need from you

1. Can you share the submission and failure data (counts, reasons, repeat developers)?
2. Is engineering capacity available for the preflight tooling this quarter? It is the main dependency.
3. Is the head of ecosystem open to a mandatory preflight in place of a mandatory course, or is the course itself the requirement? That changes the pilot design.