# Chrome Web Store setup for Brightdesk (30 customers, enterprise IT push)

## Short answer

Do not publish 30 public extensions with swapped logos and names. The store bans that as repetitive content (violation **Yellow Nickel**). It also applies across affiliated publishers, and abusing the exceptions can cost the whole developer account. Your account also starts with two extension slots†.

Publish one Brightdesk item instead. Each customer's logo, name and domains load at runtime after sign-in. Customer IT force-installs that one item by its extension ID. Use a per-customer build only where a contract requires the customer's own name in Chrome.

† = verify against current Chrome Web Store docs. The item limit and badges changed in 2026.

## Assumptions

You didn't answer these, so I assumed the following:

1. The extension is Brightdesk's companion to its web app. It does one thing, such as an agent or admin sidebar or widget.
2. It needs a Brightdesk login, so reviewers need a demo tenant (see Test instructions).
3. Some features may need to run on customers' own domains, such as their helpdesk or site.
4. Most enterprise customers manage Chrome through Google Admin. Some use another management tool.
5. It's a first submission with no launch date yet, and zero active users.

If any of these is wrong, tell me and I'll rework the matching section.

## Distribution plan, ranked by efficiency

| Rung | Setup | Use for |
| --- | --- | --- |
| 1 (default) | One public or unlisted "Brightdesk" item. After sign-in it loads the tenant's logo, name and domains. | All 30 customers. |
| 2 | Private publishing to a customer's Google Workspace organization. Each item is a separate build and review. | A customer that wants an item only in its own admin console. |
| 3 | Unlisted white-label build per customer, sent to that client only. | A contract that says the customer's own name must appear in Chrome. |
| 4 | A separate public listing per customer. | Never. It's banned. |

### Rung 1: one item for every tenant

- **Runtime branding.** Your "config file swap" becomes a tenant config served by your API after sign-in. Remote config, data and images are allowed. Remote logic is not. Shipping a different script per customer, or fetching code from a CDN, returns **Blue Argon**.
- **Public or unlisted.** Public gives you store discovery. Unlisted suits customers who refuse a public item. Both work for force-install by ID.
- **One review per release.** You review once for all 30 customers instead of 30 times.
- **Limit of rung 1.** Customers see "Brightdesk" in the store and in Chrome's extension list. Their brand shows only inside the extension UI.

### How enterprise IT pushes it

1. Customer IT force-installs the extension by ID from the management console (Google Admin or another tool). No per-user action is needed.
2. Give IT a one-page note with the extension ID and the permissions the extension declares. Tell them where the tenant is configured (the sign-in domain).
3. Force-installed users cannot disable or remove the extension. Test your update path on a managed profile before launch.

### Rung 2: private publishing to the customer's organization

- It needs a customer who manages Chrome through Google Admin. Their admin approves your link, then sees and force-installs the item.
- Each item is a separate build and review. Add this to the description: `THIS EXTENSION IS PUBLISHED TO <DOMAIN NAME> ONLY`.
- If the customer revokes approval, the item stays published but can't update. Agree up front who owns the item, or transfer it to them through support.

### Rung 3: per-customer white-label build

- Use it only when a contract requires the customer's name in Chrome. Make it unlisted and send it to that client only.
- Put this exception statement in both the description and the single purpose field: `THIS IS A WHITE LABEL ENTERPRISE EXTENSION FOR <CUSTOMER NAME>`.
- Every such build uses a slot and needs its own review for every release.
- **Ask Chrome Web Store support first** whether private or unlisted items count toward the item limit. That's undocumented. Ask before you scale rungs 2 and 3, and request an increase if needed.

## Host access, if customer domains are involved

`content_scripts.matches` counts as host access, so moving `<all_urls>` there narrows nothing. Layer it like this:

1. **Required hosts:** only Brightdesk's own origins (app and API).
2. **Customer domains, in order of preference:**
   1. `activeTab` for click-triggered features.
   2. Optional host permissions for the customer's domain, requested from a user gesture. Then register content scripts with `scripting.registerContentScripts`.
   3. A per-customer build with that host required (rung 3).
3. **Avoid `<all_urls>` and `https://*/*` as required permissions.** Broad hosts get the slowest review and the "read and change all your data" warning. Use them only if the single purpose truly spans every page.

**Force-install catch:** required permissions are granted silently, but optional hosts still prompt each user. If the extension must run on a customer's domain without a click, choose between one Enable click per user and a per-customer build. Test the choice on a managed profile.

## Account setup (do this first)

1. **Use a dedicated company mailbox**, such as `chrome-store@brightdesk.com`, as the developer email. It can't be changed later. A personal-address account moves only through a new account plus an item transfer request.
2. **Turn on mandatory 2-Step Verification.**
3. **Declare Trader status** with company details. They show publicly in the EU.
4. **Add teammates as members with roles.** Never share one login.
5. **After first publish, opt in to Verified CRX Uploads.** Every later package must then be a CRX signed with your private key.
   - Keep the key in CI secrets or an HSM, not in the Google account.
   - A lost key takes up to a week† to replace.
6. **Publish from CI** through the Chrome Web Store API with a dedicated service account, never a person's OAuth token. That scope grants full publish rights, so guard it like a production secret.
7. **Restrict third-party app access in your Workspace** so no unverified app can obtain the Chrome Web Store scope. In December 2024 a phished employee granted a malicious OAuth app publish access. No 2-Step Verification prompt fired, and the attacker's update reached installs.
8. **Alert on any published version that CI didn't produce.** Keep a rollback runbook.

## Submission packet

### Permission-to-feature map (template, fill from your manifest)

Every entry in `permissions`, `optional_permissions`, `host_permissions` and `optional_host_permissions` gets a row. A row with no shipped feature means you delete the permission. Reviewers assume you use every permission, and an unused one returns **Purple Potassium**.

| Permission | Required or optional | Feature | Justification (dashboard text) |
| --- | --- | --- | --- |
| `https://app.brightdesk.com/*` and API origin | required | Sign-in and tenant sync | Signs the user in to their Brightdesk workspace and loads their organization's settings. |
| `activeTab` | required | Click-triggered action | Reads the current page only when the user clicks the Brightdesk button. |
| customer domain | optional | Panel on the customer's domain | Requested only when a workspace admin enables the panel for their domain. |

Write how the extension uses the permission, never what the permission does.

### Privacy tab

- **Single purpose.** One sentence, for example: "Lets agents engage with their organization's Brightdesk conversations from the browser." Keep it narrow. A sidebar plus an unrelated tool is two extensions.
- **Remote code.** Answer "No, I am not using remote code" if all logic ships in the package. Tenant config is data, not code.
- **Data types.** Tick everything the code collects, stores locally or transmits. That includes analytics, error reports and `chrome.storage.sync`. Page URLs count as browsing activity: collect them only for a feature the listing describes, with disclosure and consent first, over HTTPS.
- **Privacy policy URL.** The policy, the Privacy tab and the code must all say the same thing. A mismatch is a rejection.
- **Limited Use.** Certify the statements and publish this on your own site: "The use of information received from Google APIs will adhere to the Chrome Web Store User Data Policy, including the Limited Use requirements."

### Test instructions (reviewers need access)

A login wall without credentials returns **Yellow Magnesium**. Use a permanent seeded demo tenant with no SSO, no MFA and no expiring trial:

```
Account: reviewer@<your-demo-domain> / <password in this field only>
Tenant: permanent demo workspace, seeded with sample conversations; no SSO, no MFA, no expiry.
1. Click the toolbar icon and sign in.
2. <steps to each feature, including the optional host prompt on the demo customer domain>
Server allowlists accept any IP. Video walkthrough: <URL>
```

Also show an "account required, sign in" state inside the extension.

### Package rules

- Build the package in CI, with the manifest at the root and a version higher than the last.
- Ship all logic inside the package.
- Minify at most. Obfuscation returns **Red Titanium**.
- Target modern Chrome. Legacy polyfills have been flagged†.

## Release and timeline

1. **Untick auto-publish and stage the approved build.** An approved build waits up to 30 days†, then reverts to draft.
2. **Expect a long review.** Google says a few days to a few weeks†. Queues reached 3-4 weeks† in April 2026. Plan one rejection round.
3. **Don't cancel and resubmit to speed things up.** Cancelling resets your queue position†. Escalate to support after three weeks†.
4. **Launch plan, working back from your date:**
   - Submit at least 6-8 weeks before launch.
   - If approval may miss a fixed date, demo a local build and announce the listing as coming.
   - Publish on launch day.
5. **Updates.** Every update is fully reviewed, and the live version stays until the new one publishes.
   - Add new access as optional permissions behind an in-product "Enable" button.
   - A new required permission with an install warning disables the extension for every user until they accept. Force-installed fleets would break silently.
   - Promote to required only in a major version, after testing the upgrade by packing two CRX versions locally.
6. **Partial rollout and rollback.**
   - Partial rollout is available only above 10,000† seven-day users, so it won't apply at launch.
   - Rollback republishes the previous version under a new version number in minutes, with no review.
   - Keep storage migrations backward compatible.

## If it goes wrong

- **Rejected:** the live version stays, but the violation can trigger re-review of it. Fix every cited point in one resubmission.
- **Warning:** you get 7-30 days† to ship a fix while the item stays live.
- **Takedown:** the listing 404s. After weeks unresolved, Chrome disables existing installs.
- **Appeal:** once per violation†. Frivolous appeals can cost future appeal rights. Clarify through support first, then appeal with evidence:

```
Item: <extension ID>, violation <ID>, version <x.y.z>.
The flagged <permission or code> is used by <feature>: <file:line>.
User flow: <steps>, recording: <URL>. Test account: see Test instructions.
We request reinstatement of version <x.y.z>.
```

## Decisions I need from you

1. Does the extension need to run on customer domains without a click? That decides between optional hosts and per-customer builds.
2. Do any contracts require the customer's name in Chrome itself, and for how many of the 30? That sets how many rung 3 builds you need.
3. What share of enterprise customers use Google Admin? That decides whether rung 2 is an option.
4. Should rung 1 be public or unlisted? I'd start public unless customers object.