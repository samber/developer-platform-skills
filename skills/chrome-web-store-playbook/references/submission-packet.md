# Submission packet

## Permission-to-feature map

One row per entry in `permissions`, `optional_permissions`, `host_permissions` and `optional_host_permissions`. A row with no shipped feature means delete the permission.

| Permission               | Required or optional | Feature that uses it                           | API calls                                    | Justification (dashboard text)                                                        |
| ------------------------ | -------------------- | ---------------------------------------------- | -------------------------------------------- | ------------------------------------------------------------------------------------- |
| `activeTab`              | required             | "Save to Acme" button                          | `scripting.executeScript` on click           | Reads the selected text on the current page only when the user clicks "Save to Acme". |
| `https://app.acme.com/*` | required             | Sign-in and sync                               | `fetch` to the Acme API                      | Signs the user in to their Acme workspace and syncs saved items.                      |
| `https://*/*`            | optional             | Inline panel on the customer's helpdesk domain | `permissions.request` from the settings page | Requested only when an admin enables the panel for their helpdesk domain.             |

Write how the extension uses the permission, never what the permission does.

## Privacy tab answers

- Single purpose: one sentence naming the focus area, e.g. "Saves web page snippets to the user's Acme workspace."
- Remote code: "No, I am not using remote code" when all extension logic ships in the package. An iframe or sandboxed page loading your web app is exempt under policy; describe it in the single purpose and justifications.
- Data types: tick everything the code collects, stores locally or transmits, including analytics, error reports and `chrome.storage.sync`.
- Limited Use: certify all three statements; publish on your own site: "The use of information received from Google APIs will adhere to the Chrome Web Store User Data Policy, including the Limited Use requirements."

## Test instructions

```
Account: reviewer@acme-demo.com / <password in this field only>
Tenant: permanent demo workspace, seeded with sample tickets; no SSO, no MFA, no expiry.
1. Click the toolbar icon and sign in.
2. Open https://demo.acme-helpdesk.com/ticket/42, click "Save to Acme".
3. Settings > Helpdesk panel > Enable, accept the host permission prompt.
Server allowlists accept any IP. Video walkthrough: <URL>
```

## Labelled variants

- Beta item title: `Acme Clipper BETA`; description opens: `THIS EXTENSION IS FOR BETA TESTING. Production version: <URL>`.
- White-label build (unlisted, sent to the client only), description and single purpose field: `THIS IS A WHITE LABEL ENTERPRISE EXTENSION FOR <CUSTOMER NAME>`.
- Per-host build, host permissions limited to that host: `THIS EXTENSION IS LIMITED TO <HOST NAME> ONLY`.
- Build published privately to one domain: `THIS EXTENSION IS PUBLISHED TO <DOMAIN NAME> ONLY`.

## Common violation IDs

| ID                                    | Cause                                                            | Fix                                                            |
| ------------------------------------- | ---------------------------------------------------------------- | -------------------------------------------------------------- |
| Purple Potassium                      | unused or broader-than-needed permission                         | remove it, or appeal with the map row and a recording          |
| Yellow Magnesium                      | reviewer blocked by login, server down, missing file             | test instructions, account-required state, test the packed CRX |
| Yellow Zinc                           | missing icon, screenshot or description                          | complete the listing                                           |
| Purple Lithium                        | privacy policy missing, dead, in the description, silent on data | link a working policy in the Privacy field                     |
| Purple Nickel                         | data collected before disclosure and consent                     | disclose and get consent first                                 |
| Purple Magnesium                      | browsing activity collected without a user-facing need           | stop collecting                                                |
| Blue Argon                            | remotely hosted logic                                            | bundle it                                                      |
| Red Titanium                          | obfuscation, legacy bundler output                               | minify only, modern target                                     |
| Red Magnesium, Copper, Lithium, Argon | more than one purpose                                            | split or narrow                                                |
| Yellow Lithium                        | only launches a site, app or promo page                          | add in-extension function                                      |
| Yellow Potassium                      | no utility, or a listed feature only links out                   | deliver the feature in the extension                           |
| Purple Copper                         | user data sent without modern encryption                         | HTTPS everywhere                                               |
| Yellow Nickel                         | repetitive content                                               | consolidate or use a labelled exception                        |

## Appeal (one per violation)

```
Item: <extension ID>, violation <ID>, version <x.y.z>.
The flagged <permission or code> is used by <feature>: <file:line>.
User flow: <steps>, recording: <URL>. Test account: see Test instructions.
We request reinstatement of version <x.y.z>.
```
