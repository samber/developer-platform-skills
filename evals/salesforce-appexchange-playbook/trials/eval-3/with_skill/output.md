## Do this first

**Answer to both asks: no.** Don't put bulk-export in the fix version, and don't appeal the TLS finding. Fix all three findings in a fix-only version, then ship bulk-export as the next version on top of it.

## Why the fix version stays fix-only

- Any change beyond the flagged issues forces a full initial review and a new fee.
- On a failed review you change nothing else. You keep the same package ID and namespace, rescan, and start a follow-up review (fee due).
- Bundling does not save a fee. Either way you pay one review fee ($999†). Bundling gets you the longer initial-review path, and a finding in the new bulk-export code would block your fixes from listing.
- A new version built on the last passed version as ancestor lists without a new review. So the split path should cost no second fee.
- Ordering matters here. A version cut before its ancestor has passed does not get that treatment. Build bulk-export on a branch now, but don't cut its package version until the fix version passes.
- Confirm the "lists without review" point for a feature this size in Product Security office hours. Periodic re-reviews will still cover the new code.

## The three findings

| Finding | Action | Scope |
|---|---|---|
| CRUD/FLS, `InvoiceController.cls:88` | Fix | Each finding is one example of a class. Fix every instance: all queries and DML, including `@AuraEnabled` methods and their helpers. Use `WITH USER_MODE` or `AccessLevel.USER_MODE`, put `with sharing` on every class, and use bind variables in SOQL. |
| Stored XSS, `invoiceTable` LWC | Fix | Sweep every LWC and Visualforce page for unescaped output, `innerHTML`, `lwc:dom="manual"` and off-platform JavaScript. Stored XSS usually means untrusted record data is rendered somewhere, so check every place that renders it. |
| TLS 1.0, `legacy.ledgerly.io` | Fix, don't argue | Disable TLS 1.0 and 1.1 on the host. This takes hours. Take the site down or redirect it if that is quicker. |

### Why not appeal the TLS finding

- A failed test has no appeal. The channel is Product Security office hours. "Request a Second Look" applies to Returned reviews (materials missing), not Failed ones.
- The no-fee route needs all findings to be false positives. Two of your three are real, so the fee is due regardless.
- A dispute costs you a 2-4 week† retest cycle to win a point that a quick config change closes.
- First check the "app never calls it" claim. Look in:
  - the DAST host list and the URLs you submitted
  - Connected App/ECA callbacks
  - Remote Site Settings, Named Credentials and CSP Trusted Sites
  - static resources, docs and in-app links
- If the host is in none of those, add a short out-of-scope note to the resubmission. Do it in addition to fixing the host, not instead of it.
- Check TLS 1.2 or higher on every other external endpoint the app uses. This class is "TLS below 1.2", not one host.

## Steps

1. This week: freeze a `fix-only` branch from the failed version. Fix all three classes and nothing else.
2. Run Code Analyzer and the Checkmarx scanner (3 runs per version included†). Run DAST on every in-scope endpoint and attach a screenshot that proves the scan hit the right host.
3. Check the test org, credentials and docs. A dead test org stalls verification.
4. Cut the fix version as a new minor version and start the follow-up review in the Partner Console wizard. Pay the fee.
5. In parallel, build bulk-export on a separate branch, off the fix branch. Run the same scans on it, since data export is a CRUD/FLS and sharing risk. Don't package it yet.
6. After the pass, cut the bulk-export version with the passed fix version as ancestor. Then do the push upgrade: sandboxes for a week, then production in batches.

## Timeline

Engineering fix: 1-2 weeks (my estimate). Retest: 2-4 weeks†. That puts the pass around mid-December to mid-January, counting from 2026-10-30. Bulk-export ships right after the pass.

If bulk-export is bundled, add the initial-review path: verification 1-2 weeks† plus first test 3-4 weeks†. The date moves out accordingly, and a second failure costs another 2-4 weeks† plus another fee.

## Assumptions

- This is a managed 2GP package with an external service. The `legacy.ledgerly.io` finding suggests the DAST scope was broader than the package.
- The review was a Failed result, not Returned.
- Bulk-export adds no new external endpoint. If it does, it adds DAST scope.

† Verify fees, durations and review rules against current Salesforce partner docs before quoting them.