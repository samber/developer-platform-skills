**Next action, today:** stop work on `cvnbeta` and register `corvana` as the namespace in a Developer Edition org linked to your Dev Hub. Check it is free first. Nothing is released yet, so all three problems are still cheap to fix. After the first promotion, none can be undone.

## Verdict

| Plan item | Verdict |
|---|---|
| Install latest beta in pilot production orgs, then upgrade to GA | ❌ Impossible. Betas install only in scratch orgs and sandboxes, and they never upgrade. |
| Ship as `cvnbeta`, switch to `corvana` at GA | ❌ A namespace is fixed to the package at creation. A rename means a new package and no upgrade path. |
| Every service class `global` | ❌ Global Apex can never be removed once released. |
| Three pilots in production | ⚠️ Possible only on a released version behind an installation key. Also see the OAuth trigger below. |

## 1. Beta in production

- Pilots need a **promoted, managed-released** version and its installation key.
- Promotion never reverses. Only one beta per minor version can be promoted.
- A version built with `--skip-validation`, or without `--code-coverage`, cannot be promoted. Apex coverage must be 75% or more†, with every trigger covered.
- Install on each pilot's **sandbox first** and let it run about a week. Push to production only after that.
- Pilot data is real contract data. Run Code Analyzer on the package before the first production install, even though the security review comes later.

## 2. Namespace

- `cvnbeta` prefixes every component API name: `cvnbeta__Contract__c`, `cvnbeta__Clause__c`, and so on. It also prefixes the Apex and LWC references to them.
- Pilots would store real data in `cvnbeta__` objects. Moving to `corvana` later would mean exporting and reloading that data under a different package, plus a rework of anything that references the old names.
- Fix:
  1. Create a new package under the `corvana` namespace.
  2. Port the source. This is a rename, not a redesign.
  3. Never promote any `cvnbeta` version.
  4. Keep the old betas for scratch-org dev only.
- Estimate: 1 to 2 engineering days for the rename and rebuild, if the source is in a clean SFDX project. Allow 1 week if API names are hard-coded in LWCs and tests.
- If a second package of yours will share code with this one, put both in the same namespace.

## 3. Global service classes

- Global Apex is permanent, and so is any method signature you expose on it. Every global class you ship becomes a public API you support forever.
- Fix, using two tiers:
  - **Your own add-on packages:** keep services `public` and mark them `@namespaceAccessible`. This works only if the add-ons share the `corvana` namespace.
  - **SIs and subscribers:** expose one small, versioned `global` facade.

```apex
// Internal: callable by your own packages in the same namespace, invisible to subscribers.
public with sharing class ContractService {
    @namespaceAccessible
    public static List<Contract__c> byStatus(String status) {
        return [SELECT Id FROM Contract__c WHERE Status__c = :status WITH USER_MODE];
    }
}

// Public surface: small, versioned, hard to remove later.
global with sharing class ContractApiV1 {
    global static List<Id> openContractIds() { /* delegate to ContractService */ return null; }
}
```

- Add a deliberate review step before each new `global` keyword.
- The same rule covers protected components. Mark internal custom settings, custom metadata types, labels and permissions **protected**. Once released unprotected, they stay unprotected.

## 4. OAuth trigger

- Three pilots means three customer production orgs. OAuth controls are mandatory for any Connected App or External Client App used by more than two†, so the pilots cross the line.
- This applies only if your SaaS connects through a Connected App or ECA. You have not said whether it does.
- If it does, use an ECA. Spring '26 stopped new Connected Apps†.
- Required controls: PKCE, refresh-token rotation, a 30-idle-day refresh-token expiry†, and an IP allowlist of at most 256 addresses†.
- Each control **locks once enabled**. Ship the client changes first, test in a sandbox, then enable.

## Assumptions

I could not ask, so each gap below carries an assumption:

1. **In the org:** objects, UI and Apex. Your SaaS probably also runs an analytics engine outside Salesforce. I assume **package plus external service**, so DAST applies to that service as well as Code Analyzer and Checkmarx.
2. **Stage:** building. You joined the partner program in June and are not yet in review.
3. **Pricing:** unknown. I assume a paid per-seat subscription, which makes Checkout the default candidate.
4. **Editions:** unknown. Professional and Group orgs reach the API only through a reviewed managed package with an API token.
5. **First paid install:** no target date given, so I counted forward from today.

## Listing and payment path

Managed 2GP, because you have objects, UI and Apex in the org. The payment rail is open.

- **Checkout:** fits per-seat subscriptions. It takes 15% of net revenue plus $0.30 per card payment†. It requires a company in the US, UK or EU, a non-OEM deal, and the clickthrough PADA.
- **Channel Order App (COA, offline PADA):** fits usage-based, tiered or negotiated multi-year deals. The PNR share is set in your PADA, commonly 15%†. Each sale must be reported within one business day†.
- **Open question:** which pricing model, and in which country is Corvana incorporated? That answer moves the rail.

Switching free ↔ paid, Checkout ↔ non-Checkout, or pricing units later sends the listing back to approval.

## Irreversible-choice register

Names are roles, since I don't know your team. Dates assume pilots start in November 2026.

| Choice | Decision | Owner | Decide by |
|---|---|---|---|
| Namespace | `corvana`, new package, abandon `cvnbeta` | Tech lead | Mon 2026-11-02 |
| Global API | Facade only; the rest `public` + `@namespaceAccessible` | Tech lead | Fri 2026-11-06, before the first promotion |
| Protected components | Mark all internal settings, metadata, labels and permissions protected | Tech lead | Same date |
| Listing type | Packaged Solution | Product | Before listing creation |
| Pricing path | Checkout vs COA | Product / finance | Before listing creation |
| OAuth controls | Enable after client changes pass sandbox test | Security / platform | Before pilot 3 reaches production |

## Security review plan

- **In-scope endpoints:**
  - every `@AuraEnabled` method behind the three LWCs;
  - every external endpoint that authenticates users or moves Salesforce data;
  - written permission before scanning anything third-party.
- **Scanners:** Code Analyzer (`--rule-selector AppExchange --rule-selector Recommended:Security`), Checkmarx source scan, and DAST such as ZAP or Burp on every in-scope endpoint.
- **Top three risk classes for your build:**
  1. CRUD/FLS missing on queries and DML in service classes and `@AuraEnabled` helpers. Use `WITH USER_MODE`.
  2. Missing `with sharing` on classes reachable from user context.
  3. SOQL injection and LWC XSS. Use bind variables, avoid `innerHTML`, and load no off-platform JavaScript.
- **Test org:** Developer Edition with the managed-released version installed. Don't let its password expire.
- **Lightning Ready certification:** mandatory for new submissions.
- **Submission week:** week of 2027-01-11, after about 6 weeks of scanning from the first sprint. This is an estimate.

## Timeline

Counting forward from today, with one failed review included:

| Date | Event |
|---|---|
| 2026-10-30 to 11-06 | Namespace, global and protected decisions. New package built. |
| Mid-Nov 2026 | Released version promoted. Pilot sandboxes installed. |
| Late Nov 2026 | Pilot production installs, after the sandbox week. |
| 2027-01-11 | Review submitted. Fee $999†. |
| About 2027-01-25 | Verification done (1 to 2 weeks†). |
| About 2027-02-22 | First test result (3 to 4 weeks†). Assume it fails. |
| About 2027-03-08 | Every instance of each finding class fixed, nothing else changed. |
| About 2027-04-05 | Retest passes (2 to 4 weeks†), new fee due†. |
| Mid-April 2027 | First paid listed install, after listing approval and the signed PADA. |

- Practitioners estimate 4 to 9 months† from signup to first paid install. From your June start, that is late October 2026 to March 2027, so this timeline sits at the late end.
- The fastest honest option for a paid install earlier than that does not exist. A pass on the first test would bring it forward by roughly 6 weeks.
- Resubmission rule: a failed review is resubmitted with the flagged issues fixed and nothing else. A bundled new feature forces a full initial review and a new fee.
- Pilots do not wait for any of this. They run on the released pilot version, then get a push upgrade to the reviewed version.

## Maintenance calendar

- **Each version:** build it on the highest managed-released version that has passed review, so it lists without a new review. Build it after that ancestor has passed.
- **Pushes:** own test orgs, then customer sandboxes for a week, then production in batches. Avoid customer quarter-end. Don't auto-assign a new feature's permission set to existing users.
- **Salesforce releases:** test all three yearly releases in preview sandboxes. Move API calls off any retiring version.
- **Re-reviews:** expect periodic ones†, with a fee. Keep the security contact on Company Info current, because a missed re-review expires every version.
- **OAuth:** controls in place before pilot 3 reaches production. Refresh-token and IP-allowlist behaviour re-checked on any change to your egress.
- **COA, if chosen:** report each order within one business day†. File cancellations per the PADA, usually 30 or more days before renewal†.

† Salesforce figure. Verify against current Salesforce partner docs before quoting it.

## Open questions

Reply with these and I'll re-rank the plan:

1. Does your SaaS connect through a Connected App or ECA today, and in how many customer production orgs?
2. Which editions do the three pilots run?
3. What is your pricing model, and where is Corvana incorporated?