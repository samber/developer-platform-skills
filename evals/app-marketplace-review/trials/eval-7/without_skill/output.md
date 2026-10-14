**Decision: return the submission as "Changes requested". Do not approve it, and do not reject it.** Two separate problems need answers, and neither is proof of bad intent.

## Why

1. **`ledger.write` has no current use.** The justification describes a Q3 roadmap feature, and the screenshots show only read-only charts and exports. Nothing in the submission needs the scope today.
2. **Write access to a ledger is the highest-risk scope you grant.** It can change customers' financial records. Grant it only for functionality that exists and that you can see.
3. **The two unseen endpoints are a separate issue, and it applies even if `ledger.write` is dropped.** One endpoint resolves to a third-party enrichment vendor. If it receives data obtained through `ledger.read` or `vendors.read`, customer financial data leaves the app for a third party. That needs disclosure whatever the scopes are.

## Steps

1. **Check what the endpoints actually receive (about 30 min).** Run the app in your review sandbox and capture its traffic. Record the request payloads for both endpoints. Record whether any ledger or vendor fields go to the enrichment vendor.
2. **Check whether `ledger.write` is exercised.** Look for any write call to the ledger API in the captured traffic. If you see one, that is a different finding: the scope is in use despite the stated justification. Escalate it.
3. **Send the message below.** Set the status to "Changes requested".
4. **Re-review in full when they respond.** Do not wave it through because the fix is small.

## Message to the developer

> Your submission cannot be approved yet. Two items need action.
>
> 1. **`ledger.write`.** Remove it. We grant a scope only for functionality that exists in the submitted build. Your auto-reconciliation feature is not in this build. When it ships, submit it as a scope upgrade with screenshots and a description of every write operation.
> 2. **Network endpoints.** Your backend calls two endpoints that you did not declare. One of them is operated by a third-party data-enrichment vendor. For each endpoint, tell us: who operates it, what it is for, which fields it receives, whether any of them come from ledger or vendor data, and whether the vendor retains or reuses that data. Add the vendor to your privacy policy and sub-processor list.
>
> We will review again as soon as we receive both.

## Written rule for reviewers

**Rule: scope and data-flow justification**

Applies to every submission that requests an OAuth scope or calls an external endpoint.

1. **Match each scope to something the reviewer can see.** Each requested scope must map to functionality that exists in the submitted build and appears in the screenshots or demo. A justification that refers to a future feature, a roadmap, or "planned" work does not count.
2. **Handle write scopes more strictly than read scopes.**
   - A write scope on ledger or other financial records needs a description of every write operation, and the reviewer must see it exercised in the sandbox.
   - A mismatch between a write scope and the visible functionality blocks approval.
   - A second reviewer must approve any write scope on financial records.
3. **Unused scopes are removed, not deferred.** The developer resubmits as a scope upgrade when the feature ships. Do not approve a scope "in advance".
4. **Capture outbound traffic for every submission.** Compare the observed endpoints with the endpoints the developer declared.
   - Any undeclared endpoint blocks approval until the developer explains it.
   - Any endpoint operated by a third party that receives customer ledger or vendor data requires the developer to disclose the recipient, the fields sent, the purpose, and the retention terms. The disclosure must appear in the developer's privacy policy.
5. **Do not assume intent.** An unexplained endpoint or scope is a request for information, not a rejection. Reject only when the developer's answer shows undisclosed data sharing, or when the build uses a scope it did not justify.
6. **Record the outcome using one of four statuses:** Approved, Approved with reduced scopes, Changes requested, or Rejected. Write the reason in terms of rule numbers above. Use the same status for the same facts, so that two reviewers reach the same result.

## Assumptions to check

- I have not seen Pallas's existing policy documents. Align the rule's wording and status names with what you already use.
- I assumed a scope upgrade after approval triggers re-consent for installed customers. If your platform behaves differently, adjust step 3 of the rule.

**Next action:** capture the sandbox traffic for the two endpoints and write down what each receives. That result decides whether you send the message as written or escalate.