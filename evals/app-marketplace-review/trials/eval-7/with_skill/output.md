# Handling the Pallas spend-analytics submission, and the written rule

I read `SKILL.md` and its re-review and benchmark references. The skill's interview was skipped because you asked for a one-shot answer. I assumed three things, and each moves a verdict if wrong:

- **Data sensitivity:** a ledger holds financial data, so this is the top tier (interview Q2 answer d).
- **Review shape:** Pallas runs a single hard gate.
- **Update propagation:** I don't know whether updates auto-propagate to installed tenants.

## Decision

**Return the submission as "changes required". Don't approve, and don't treat it as a delisting or ban case.** Send two separate findings, each citing a specific policy, and let the developer cure each one.

| # | Finding | Verdict | Cure |
|---|---|---|---|
| 1 | `ledger.write` is justified only by a future roadmap, and the screenshots show read-only charts and exports. | **Fail** | Drop `ledger.write`, then resubmit. |
| 2 | The backend calls two endpoints that weren't declared. One resolves to a third-party enrichment vendor. | **Hold** until disclosed, then decide. | Disclose both endpoints and the data flow. |

I'd keep them as two findings. The scope can be fixed by editing the manifest. The endpoints can only be judged once the developer discloses what they send.

### 1. `ledger.write` fails scope necessity

- **Policy:** high-risk scopes need demonstrated necessity, not declared intent. This is the skill's scope-minimization rule, modeled on Shopify's per-scope requirements.
- **Evidence:** the justification says "planned" and "Q3 roadmap", so no shipped feature uses the scope. The screenshots confirm every shipped feature is read-only.
- **Why not "approve and trust them":** write access to a customer's ledger is the highest-impact grant on the platform. Granting it now means every installed tenant carries that risk for a feature that doesn't exist.
- **Why not "approve with write disabled":** you can't enforce a promise not to use a granted scope.
- **Message to the developer:** this is a clean path. Ship read-only now. When auto-reconciliation ships, adding `ledger.write` triggers a full re-review, with a working feature to review. That is faster for them than arguing about it today.

### 2. The undeclared endpoints need a data-flow disclosure

An enrichment call is plausible for spend analytics, for example vendor-name normalization from `vendors.read`. So don't assume bad faith. The unknown is what leaves Pallas's data boundary, because a third-party endpoint receiving financial data is a subprocessor.

Before any verdict, do these in order:

1. **Capture the payloads yourself.** Run the app in a test tenant seeded with canary values, and record exactly which fields reach each endpoint. This is the skill's "data-access review beyond the grant". Don't rely on the developer's description alone.
2. **Send the developer a disclosure request** covering, per endpoint:
   - the owner and the purpose;
   - the exact data fields sent;
   - retention;
   - the subprocessor agreement and its location.
3. **Identify the second endpoint.** Don't judge it until you know who owns it.
4. **Classify the result:**
   - **Vendor names or IDs only, disclosed, with an agreement in place:** clears, provided it is listed in the app's privacy and security disclosure.
   - **Ledger amounts, transactions, or bank details leaving the boundary, undisclosed:** a data-handling violation. Escalate to your security team as a partner-level concern, not only an app rejection.
   - **No answer, or answers that contradict the captured traffic:** treat it as non-response. The skill's publisher-level enforcement ladder applies. Repeated unaddressed review exchanges are grounds for escalating consequences, separate from this one app.

### Why the combination matters

An over-broad scope plus undeclared egress is the pattern a bad-faith submission would also produce. Each finding alone has an innocent explanation. Together they justify the full traffic capture above and a closer reviewer pass. They don't justify a rejection on suspicion.

### Process points

- **Cite the policy in the rejection.** The appeal path needs something to argue against.
- **Name the independent human appeal.** If the developer disputes the decision, a different reviewer decides, with a stated turnaround. If you serve EU business users, this also covers your P2B mediation exposure.
- **Once `ledger.write` is gone, the tier drops.** The app is then read-only on ledger and vendor data. It stays at the sensitive tier only if the endpoint review shows financial data leaving.
- **Check whether the new endpoints are a post-approval update.** If they appeared in a later version of an already-approved app, they are an update-trigger event under the rule below. Here they are a first submission, so they are simply undeclared.

## Written rule for the next reviewer

Paste this into the review policy. It follows the skill's requirement that every trigger be self-assessable by the developer before submitting.

> **R-7: Write scopes and external endpoints**
>
> **Scope necessity.**
> 1. An app may request only the scopes that a shipped, reviewable feature uses.
> 2. For every requested write scope, the submission must name the feature that uses it, and the reviewer must see that feature working in the supplied screenshots, video, or test tenant.
> 3. A justification that cites a roadmap, planned feature, or future capability fails this rule. The reviewer rejects the scope and cites R-7.1.
> 4. Rejecting a scope does not reject the app. The developer may resubmit without it.
>
> **Escalation trigger (developer self-assessable).** Any request for a write scope on customer ledger, vendor, or payment data moves the app up one review tier. Adding such a scope later is a full re-review event, not a minor update.
>
> **External endpoints.**
> 1. Every host the app's backend contacts with customer data must be declared in the submission, with owner, purpose, exact data fields sent, retention, and subprocessor agreement.
> 2. A host observed in testing that is not declared gets a disclosure request. Review stops until the developer answers.
> 3. The reviewer verifies by capturing payloads in a canary-seeded test tenant. The developer's description is not enough.
>
> **Outcome by finding.**
> - Disclosed, matches captured traffic, agreement in place: clear.
> - Undeclared host, customer data limited to what the developer disclosed: return with corrections, then re-review.
> - Financial or ledger data leaving the boundary without disclosure, or answers contradicting captured traffic: escalate to security as a partner-level concern.
> - No response within the stated window: apply the publisher non-responsiveness ladder.
>
> **Minor-update definition.** An update is minor only if it adds no new scopes, no new external endpoints, no change in data handling, no payment-model change, and no new app type. Anything else gets a full re-review.
>
> **Every rejection under R-7 cites the rule number and the specific finding.**

## Self-check against the skill's gates

- **Gate 1 (objective escalation trigger):** passes. "Write scope on ledger, vendor, or payment data" is self-assessable.
- **Gate 2 (objective minor-update definition):** passes. It is the five-item list.
- **Gate 3 (every enforcement rung has an owner, notice period and evidence):** only partly covered. R-7 names the evidence but not the owner or notice period for each rung. Pallas needs to fill those in.
- **Gate 4 (publish-channel control):** out of scope for this case. If updates auto-propagate, you also need the 24-48 hour propagation hold from the skill's section 4.

## Open items for you

- **Q1:** how did you observe the two endpoints, from static analysis or from runtime traffic? A runtime capture is already close to step 1 above.
- **Q2:** does Pallas's current policy already define a subprocessor disclosure field? If not, R-7's endpoint clause is new for developers, so give it a notice runway before applying it to listed apps. The skill's benchmark is six months, from Atlassian's program docs.