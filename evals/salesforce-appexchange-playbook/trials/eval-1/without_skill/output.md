**Do this first: stop the pilots from using `cvnbeta` and register `corvana` today.** Two of the three parts of the plan break, and the third is risky.

I answered from memory of Salesforce 2GP rules and didn't check live docs. Before you act, confirm items 1 to 3 against the current "Second-Generation Managed Packages" guide.

## Verdict

| Part of plan | Status |
|---|---|
| Install latest beta into production | ❌ Blocked by Salesforce |
| Upgrade pilots from beta to GA | ❌ Not possible |
| Namespace `cvnbeta` now, `corvana` at GA | ❌ No migration path |
| Every service class `global` | ⚠️ Permanent API commitment |

## 1. Beta versions cannot go to production

- A beta package version installs only in sandbox, scratch, and Developer Edition orgs.
- Production needs a promoted (released) version. Promotion needs at least 75% Apex coverage.
- You cannot upgrade a beta version to a later version. You must uninstall it first, and uninstalling deletes the package's custom object data.
- Even if installing the beta worked, "upgrade to GA" would wipe the pilots' real data.

**Fix:** a promoted version is already production-ready. "GA" is a business milestone, not a package state. Promote `1.0.0` for the pilots (label it "Pilot" in the version name), then ship `1.0.x` or `1.1.0` as upgrades.

## 2. The namespace is permanent

- A package is bound to its namespace for life. You cannot rename it.
- `corvana` means a new package ID. Nothing upgrades from `cvnbeta` to `corvana`.
- The namespace is baked into all of these:
  - API names (`cvnbeta__Contract__c`)
  - Apex references
  - Flows, reports, and integrations the pilots build
  - Permission sets
- Pilots would have to uninstall (losing data) and migrate it by export and import. Their customizations would break.

**Fix:**

1. Register `corvana` in a namespace org. Link it to your Dev Hub under Setup, Namespace Registries.
2. Check the name against trademark and AppExchange name conflicts first.
3. Create a new 2GP package under `corvana`, with a fresh package ID.
4. Rename the namespace in the codebase, `sfdx-project.json`, and the LWC markup. Do it before any customer install.
5. Keep `cvnbeta` for internal sandbox testing only, then abandon it.

Time: about 1 to 2 hours to register and create the package, plus half a day for the rename and a green test run.

## 3. `global` everywhere

- After promotion, `global` classes, methods, and interfaces are public API. You cannot remove or change their signatures.
- Every type that appears in a global signature must also be global.
- Adding an abstract method to a global interface or abstract class breaks subscribers.
- Your service layer is probably not designed as a stable API. Promoting it for the pilots locks all of it in.
- Your own add-on packages don't need `global` if they share the `corvana` namespace. Use `public` plus `@NamespaceAccessible`, and declare the package dependency. Confirm this against current docs.
- Only SIs and other namespaces need `global`.

**Fix:**

1. Change every service class to `public` before the first promotion.
2. Add `@NamespaceAccessible` where your own add-ons call in.
3. For SIs, expose one small, deliberate global facade, with an interface plus a factory.
4. Add that facade after the pilots tell you what they need.

Beta versions still allow removing global members. Do the cleanup now, before promoting.

## 4. Schema is also sticky after promotion

- Field types and some component deletions are restricted once a version is released.
- Review the contract and clause object model before the `1.0.0` promotion.
- Check required-field choices, relationship types (lookup vs master-detail), and API names.

## Before the pilots start

1. Set up the License Management App (LMA) in your partner business org. This tracks installs and licenses per customer.
2. Run the Salesforce Code Analyzer and fix findings. Listing on AppExchange requires security review, so find problems early. Pilot installs usually go by link, but confirm this with your partner contact.
3. Use an installation key on the package, and share install links only with the three pilot admins.
4. Install into each pilot's sandbox first, as a dry run of the production install.
5. Confirm the Dev Hub that owns the package is the one you want long-term. The Dev Hub is hard to change later.

## Revised plan

1. Register `corvana`, create the package, and rename the code (about 1 day).
2. Change `global` to `public` and add `@NamespaceAccessible` (about half a day).
3. Run test and coverage validation, then set up LMA (about 1 day).
4. Do a pilot dry run in a sandbox with a beta `corvana` version.
5. Promote `1.0.0`, then install in the pilots' production orgs. Upgrade later with `1.x` versions.

**Next, in under 2 minutes:** open the Dev Hub org and check Setup, Namespace Registries for `corvana`. If the name is taken, you need a new name before any other step. Tell me what you find and I'll lay out the rename steps.