# Security review submission kit

Load at Security review step 4, when a review comes back Returned or Failed, or before touching OAuth settings. Salesforce's Checklist Builder in the Partner Community generates the exact list per solution; this file covers what it assumes you know.

## Materials by architecture

| Material                                                                                                                                                                      | Native package | Package + external app or service | Mobile client | API only                   |
| ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------- | --------------------------------- | ------------- | -------------------------- |
| Developer Edition test org (managed-released version installed, when packaged)                                                                                                | yes            | yes                               | yes           | yes, connected to your app |
| Code Analyzer report, `sf code-analyzer run --rule-selector AppExchange --rule-selector Recommended:Security --output-file CodeAnalyzerReport.html`; need not be 100% passing | yes            | yes                               | if packaged   | no                         |
| Source Code Scanner (Checkmarx) report, 3 runs per version included                                                                                                           | yes            | yes                               | no            | no                         |
| DAST report (ZAP, Burp or equivalent) per in-scope endpoint                                                                                                                   | no             | yes                               | yes           | yes                        |
| URLs and test credentials for every authenticated external component                                                                                                          | no             | yes                               | yes           | yes                        |
| False-positive write-up                                                                                                                                                       | if flagged     | if flagged                        | if flagged    | if flagged                 |
| Solution documentation, information-security policies                                                                                                                         | yes            | yes                               | yes           | yes                        |

- Extension packages: install the base packages in the same test org; submit an unreviewed base with the extension.
- Include anything you are unsure about. Out-of-scope parts are skipped; missing in-scope parts return the submission.
- Packaged ECAs: share the client key in the documents, never the client secret.
- DAST: fix every finding above informational, attach a screenshot proving the scan hit the right host, send full results, not summaries.
- Mobile: TestFlight or ad hoc build for iOS, a package file for other platforms.
- Agentforce solutions: add the AI details to the listing and test actions and prompts for prompt injection.

## Failure classes, most cited first

```
// ✓ Good - user-mode query, sharing declared, bind variable
public with sharing class InvoiceService {
    public static List<Invoice__c> byStatus(String status) {
        return [SELECT Id, Amount__c FROM Invoice__c WHERE Status__c = :status WITH USER_MODE];
    }
}

// ✗ Bad - no sharing keyword (inherits caller), system-mode read, string-built SOQL
public class InvoiceService {
    public static List<SObject> byStatus(String status) {
        return Database.query('SELECT Id FROM Invoice__c WHERE Status__c = \'' + status + '\'');
    }
}
```

1. CRUD/FLS not enforced on reads and DML, including in `@AuraEnabled` methods and their helpers.
2. Missing `with sharing` on classes reachable from user context.
3. SOQL or SOSL injection through concatenated input.
4. Lightning and Visualforce XSS: unescaped output, `innerHTML`, third-party JavaScript loaded off platform.
5. Secrets in code, custom labels or unprotected custom settings; use protected custom metadata or named credentials.
6. Agentforce actions and prompt templates that pass untrusted record data into prompts without enclosure or hardening.
7. External endpoints: TLS below 1.2, weak session handling, missing authentication on APIs that return Salesforce data.
8. Unusable submission: expired test-org password, missing external credentials, package not managed-released.

## False-positive write-up

One entry per finding, in this shape:

```
Finding: Apex CRUD violation, InvoiceSelector.cls line 42
Why it is not exploitable: runs only inside a Queueable started by an admin-only
  permission set; the record set is filtered by the caller's sharing upstream (line 18).
Evidence: permission set InvoiceAdmin, test InvoiceSelectorTest.testNoAccess shows
  a standard user receives an exception.
```

"By design" or "admin only" with no guarding code path gives the reviewer nothing to verify; name the line that guards it.

## OAuth controls on Connected Apps and ECAs

Mandatory for any partner Connected App or ECA used by more than two customer production orgs; the deadline was May 11, 2026, and the stated sanction is delisting or suspended access to Salesforce. Spring '26 stopped new Connected Apps: build new integrations on an ECA. Existing Connected Apps stay in scope of the same controls.

- PKCE on every authorization-code flow, public or confidential client; confidential clients send both `code_verifier` and `client_secret`.
- Refresh token rotation: the client stores each new refresh token and handles races between parallel refreshes.
- Refresh tokens expire after 30 idle days.
- Refresh-token IP allowlist: avoid broad ranges, 256 addresses at most; check the exemptions for your callback type before enabling it on autoscaling egress.

Each control locks once enabled. Ship the client changes first, test against a sandbox, then enable.
