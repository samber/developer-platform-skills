# Chrome Web Store setup for Brightdesk: 30 white-label extensions with enterprise force-install

I wrote this from memory and did not check the live Chrome Web Store policy pages. Before you commit to a design, confirm the three items marked ⚠️ with Chrome Web Store developer support. Policies and limits change.

## Next action (about 30 minutes)

Open a Chrome Web Store developer support ticket and ask:
1. ⚠️ Is a family of near-identical, customer-branded extensions from one publisher allowed? I mean white-label items with the same code and different name, logo, and config.
2. ⚠️ What is the per-account item limit, and can it be raised? I recall about 20 items per developer account, which would rule out 30 in one account.
3. ⚠️ Does an unlisted item count toward the same duplicate-content scrutiny as a public one?

Get the answers in writing. Don't build 30 listings before you have them.

## The plan has three risks

| Risk | Why it matters |
|---|---|
| ⚠️ Repetitive-content policy | The store's spam rules prohibit multiple extensions with duplicate functionality or experiences. 30 public items with the same code and a swapped config is the pattern that rule targets. Enforcement can remove items and, with repeat violations, suspend the whole publisher account. |
| ⚠️ Item limit | If the per-account limit is below 30, the plan fails regardless of policy. |
| Operational load | Each release becomes 30 submissions and 30 reviews, with 30 privacy-practices forms and 30 permission justifications. One rejection or takedown wave hits every customer at once. |

## Recommended design: one listing, branding at runtime

1. **Publish one extension**, "Brightdesk", under your developer account. The extension ID is the same for every customer.
2. **Load customer config at runtime**, not at build time. Two sources:
   - **Managed policy.** Declare a `managed_schema` in the manifest. Each customer's IT sets `tenantId`, brand name, logo URL, and endpoint through their policy, and the extension reads it with `chrome.storage.managed`.
   - **Sign-in lookup.** Resolve the tenant from the user's email domain after login, and fetch a branding config from your backend.
3. **Apply the brand in the UI.** Use `chrome.action.setIcon` and `setTitle` for the toolbar. Render the logo and name in the side panel, popup, and in-page widgets.
4. **Keep the config as data only.** Manifest V3 forbids remotely hosted code. Remote JSON for branding and settings is fine. Remote scripts are not.

This gives you one review, one listing, and one ID for IT to allow-list. The trade-off is that the store page, extension name, and `chrome://extensions` entry say "Brightdesk", not the customer's name.

## If a customer insists on its own name in the store

Rank the options by risk:

1. **Customer-owned item (lowest risk).** The customer registers their own developer account (a one-time $5 fee) and publishes the package you give them as unlisted or private. Their name and logo are theirs, the item sits in their account and quota, and your account carries no duplicate risk. You supply the build and a release process.
2. **Unlisted item in your account.** Use this for a small number of customers, only after support confirms it is acceptable. Unlisted means not searchable, reachable only by direct link. IT can still force-install it by ID. It still counts toward your item limit.
3. **30 public items (avoid).** This is the original plan and carries all three risks above.

Whichever option you choose, get written permission from each customer to use their name and logo. The store's impersonation rules apply to branded listings.

## How enterprise IT pushes it to all employees

Force-install works for public, unlisted, and private items alike. The admin needs only the extension ID.

1. **Google Workspace or Chrome Browser Cloud Management.** In Admin console, go to Devices > Chrome > Apps & extensions > Users & browsers. Select the org unit, choose Add from Chrome Web Store, and enter the ID. Set the install policy to **Force install**, and optionally **Force install + pin to toolbar**.
2. **Without a cloud console.** Use the `ExtensionInstallForcelist` policy via GPO (Windows), MDM or a configuration profile (macOS), or JSON policy files (Linux). The value is `<extension-id>;https://clients2.google.com/service/update2/crx`.
3. **Customers that block all extensions.** If they use `ExtensionInstallBlocklist = *`, they must also allow-list your ID in `ExtensionInstallAllowlist`.
4. **Per-tenant settings.** In the single-listing design, IT pastes your JSON config into the extension's policy field (the `3rdparty` extension policy). The extension reads it from `chrome.storage.managed`.
5. **Give IT an admin guide** with the ID, the required permissions (so security can pre-approve), the policy snippets for each platform, and the managed-config JSON schema.

## Account setup checklist for the new developer account

1. Enable 2-step verification on the publishing Google account. The store requires it.
2. Use a group publisher or a shared company account, not a personal one. This avoids a single point of failure.
3. Declare trader status honestly. If you sell to businesses in the EU, you are likely a trader. The store then publicly shows your verified address and contact details.
4. Verify and link your domain (brightdesk.com) so the listing shows a verified publisher.
5. Fill in the Privacy practices tab: single purpose, justification for each permission, and the data-use disclosure.
6. Request the narrowest permissions you can. Prefer `activeTab` and optional host permissions over broad host access. Broad access slows review.
7. Publish a privacy policy URL on your domain.
8. Set up staged rollout (a percentage of users) for releases. With one listing you can pilot with one customer first.

## Decision summary

- **Default:** one multi-tenant listing, with branding delivered by managed policy or sign-in lookup.
- **Exception:** customers who need their own store identity publish in their own developer account.
- **Do not** launch 30 public lookalike items before support confirms the policy and the item limit.