# Sable Grid account model

I read `developer-portal-design/SKILL.md` and `references/component-checklist.md` and used steps 1, 3, 6 and 7. I skipped the interview and the section-by-section approval gate because you asked for the deliverable directly. My assumptions are listed at the end, so correct any that are wrong.

## Decision

Use one account model and one console, with two entry doors:

- **Public door.** Open signup. An org is created automatically and a test key is issued immediately.
- **Partner door.** Separate sign-in page, SSO-only, approval-gated. Sable Grid staff create the org.

Both doors produce the same objects and the same roles. They differ only in how an org is admitted and who unlocks live access. A separate partner portal would double the product surface for no model benefit. Revisit that only if the partners want their own domain and branding.

## 1. Objects

```
User (one identity per person, any number of memberships)
 └─ Membership (user ↔ org, carries org role)
Organization = billing entity, SSO config, contract, status
 ├─ Project (workspace: "Default", "Regional ops", ...)
 │   ├─ Environment: test   ← keys, logs, usage
 │   └─ Environment: live   ← keys, logs, usage, live_access state
 ├─ Billing profile (plan, payment, invoices, spend)
 └─ Audit log
```

- **Users and memberships.** A user is separate from a membership, so a consultant who works for two utilities holds two memberships. SSO enforcement applies per org.
- **Org.** Every self-serve developer gets a personal org with one member, so there is no special case in the model. Partner orgs carry `contract_id`, `partner_tier`, a verified-domain list, and an SSO config.
- **Project.** Keys, logs, usage and environments scope to the project, not the org. Every org starts with a Default project.
- **Environment.** Test and live are separate and first-class. Every key, log row and usage chart shows its environment, and the toggle sits in the header.
- **Keys are owned by the project, not by a user.** When an employee leaves, production keeps working.

## 2. Test credentials

- Every project has a test environment with its own keys, synthetic data, rate limits and zero billing.
- Keys are prefixed `sg_test_` and `sg_live_`, so the environment is readable from the key itself.
- Multiple named keys per environment. Scope is chosen at creation. Expiry is chosen at creation. Rotation uses an overlap window. Last-used time is shown.
- Test and live keys appear as parallel pairs on one Keys page.
- **Self-serve:** a test key is auto-provisioned at signup and injected into the quickstart snippets and the try-it console. That is the TTFC lever. Target under 15 minutes, because this is a simple REST API with key auth.
- Fixtures, simulated meter events and key mechanics belong to `api-test-mode-design` and `api-auth-key-management`. This model only fixes where they live.

## 3. Roles

Org-level roles are bundles of capabilities. Nobody is assigned a capability individually.

| Capability | Owner | Admin | Billing | Developer | Viewer |
|---|:-:|:-:|:-:|:-:|:-:|
| Manage SSO, delete org, transfer ownership | ✅ | | | | |
| Invite and remove members, set roles | ✅ | ✅ | | | |
| Create and archive projects | ✅ | ✅ | | | |
| Create, rotate and revoke **live** keys | ✅ | ✅ | | project grant | |
| Create, rotate and revoke **test** keys | ✅ | ✅ | | ✅ | |
| View request logs | ✅ | ✅ | | ✅ | ✅ (redacted) |
| View usage | ✅ | ✅ | ✅ | ✅ | ✅ |
| View spend, invoices, plan | ✅ | ✅ | ✅ | | |
| Change plan, payment method, spend caps | ✅ | | ✅ | | |
| See key list or key metadata | ✅ | ✅ | | ✅ | |

**Your finance request is the Billing role.**

- Billing sees spend and usage, broken down by project and environment.
- Billing never sees key values, the key list, or request logs. Logs can contain meter payloads.
- Billing can set spend alerts and caps.
- The Billing role does not appear in the Keys or Logs navigation. Their landing page is Usage & Billing.

Other role rules:

- **Live keys are narrower than test keys.** Developers get test freely. Live is granted per project, as a project-level override.
- **Owners.** At least one is required and two are recommended. Ownership transfer is deliberate and audited.
- **Viewer** sees logs with payloads redacted.

## 4. Admission and approval

Both groups follow the same four states. What differs is who moves the org between states.

| State | Self-serve | Partner (35 utilities) |
|---|---|---|
| Org admitted | Automatic on email verification | Sable Grid staff approve: contract and DPA on file, domain verified |
| Auth | Email/password or social login | SAML/OIDC through the org's IdP. SSO is enforced. |
| Test access | Immediate | On approval |
| Live access, per project | Automatic once a payment method is on file | Granted by Sable Grid staff, per project, on a named approval |

- **Staff approval lives in a separate internal admin console.** The staff "partner admin" role is never a customer role. Every approval is written to the audit log with the approver's name.
- **Verified partner domains are blocked from public signup.** A utility employee who signs up publicly is routed to the partner door. Without this, anyone can sidestep approval with a work email. An existing self-serve user on a claimed domain is invited to join, never silently migrated.
- **SSO.** SAML/OIDC is configured per org. Domain verification comes first. Provisioning is just-in-time. SCIM is added later. IdP groups map to the roles in section 3. Deprovisioning a user suspends the membership but leaves the project's keys untouched.
- **Break-glass.** Each partner org keeps one documented owner recovery path, so an IdP outage doesn't lock the utility out.
- **Audit log.** Visible to Owner and Admin, exportable. Partners' legal teams will ask for it.
- **Build vs buy.** Buy a managed identity layer for SAML and SCIM. Build the org, project, role and approval logic yourselves, because that is your product.

## 5. Placement in the console

- Header, left to right: **org switcher → project switcher → test/live toggle**. The toggle is visible on every credential, log and usage surface.
- Project pages: Keys, Logs, Usage, Sandbox.
- Org pages: Members, SSO (Owner only), Usage & Billing, Audit log.
- Docs, pricing and the catalog stay readable without signup for both audiences.
- Changelog, status link and a support escalation path sit in the footer of every surface.

## 6. Migration of the current setup

1. Each existing account becomes an org with one Default project.
2. The existing single key becomes the **live** key in Default. Keep its value and format so no integration breaks. Label it "legacy", and nudge rotation through the overlap window.
3. Issue a new `sg_test_` key to every account on migration.
4. Map old roles. The account creator becomes Owner. Other `admin` users become Admin. `member` becomes Developer.
5. Add Billing as a new role. Each org's Owners invite their finance people.
6. Partner accounts migrate with `live_access` already granted, plus an SSO onboarding task per utility.

## 7. Metrics

- **Self-serve TTFC.** Instrument landing → signup and signup → first test call separately. Target under 15 minutes.
- **Partner time to approved access.** Partner TTFC includes human approval, so TTFC alone would mislead. Track request → approved → SSO working → first live call as a separate funnel with its own SLA.
- **Watched trends, not gates.**
  - Share of orgs using more than one project.
  - Share of orgs that add a Billing user.
  - Number of support tickets about keys.

## 8. Phasing

1. **Priority 1.** Org, project and environment model, test keys, the Billing role, and migration. This covers both customer asks.
2. **Priority 1.** The partner door: SSO enforcement, approval states, domain claiming, audit log. Legal requires it, so it runs in parallel.
3. **Priority 2.** SCIM and IdP group mapping, project-level role overrides, key scoping and expiry policies.
4. **Priority 3.** Spend caps and alerts, audit-log export.

## Assumptions to confirm

1. The current key is a production key, which section 6 assumes.
2. A pending partner org sees docs only. A pre-approval sandbox on synthetic data is possible if legal agrees.
3. Self-serve orgs don't get SSO. Say so if you want it as a paid-plan feature.
4. No deadline or effort ceiling was given. Priorities 1 and 2 assume a funded owner. The skill says to treat an unowned portal as decaying.
5. Partners may want several projects per utility, for example per region. The model supports that. If most won't, hide the project switcher until a second project exists.