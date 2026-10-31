I couldn't reach Atlassian's pages (web access was denied in this session), so the dates and revenue-share points below come from memory. Check each one against the sources I list at the end before you commit to a plan. I also didn't touch `skill-wip/`, as you asked.

## Short answer

1. **Don't plan around "Connect works until 2027."** My recollection is that Atlassian announced end of support for Connect for **31 Dec 2026**, with restrictions on new Connect apps and features starting before that. That is about two months from today. If the date is right, "next year" means after Connect is no longer supported. Check this first, because it sets how urgent everything else is.
2. **Build the PDF macro on Forge, not in `atlassian-connect.json`.** Adding a new Connect module means shipping new surface area on a platform that is going away. It also adds to the migration work.
3. **Migration alone shouldn't change your revenue share** (see below), but confirm that against your current partner terms.

## Recommended sequencing

| Step | When | What |
|---|---|---|
| 0 | This week | Read Atlassian's current Connect end-of-support page and the Connect-to-Forge migration guide. Confirm the exact dates, any freeze on new Connect modules or versions, and what happens to installs at end of support. |
| 1 | This week | Decide the architecture. The usual choice is a hybrid: keep the existing Connect app and add Forge modules to it (Atlassian's Connect-on-Forge path). Your new macro is then Forge-native and the old surface moves over incrementally. |
| 2 | This month | Ship the export-to-PDF macro as a Forge module. Check the Forge limits early, because PDF rendering is the risky part: function timeout, memory, payload size, and egress. If rendering is heavy, use Forge Remote or an external renderer and declare the egress. |
| 3 | Next 4–8 weeks | Migrate the existing Connect modules to Forge (macros, storage, lifecycle and webhook handling, auth, and any iframe UI moved to UI Kit or Custom UI). |
| 4 | Before the cutoff | Run the migration for the 1,400 sites. Use a staged rollout, and have a rollback and a support plan ready for customers who must approve new scopes. |

Reasons for this order:

- **Forge-native new work avoids double implementation.** The macro is the only thing that must ship this month. Building it on Forge means you won't port it later.
- **Hybrid is the lowest-risk path for an app with paying installs.** You keep the same app key, listing and licences, and you don't ask customers to reinstall.
- **Consent prompts are the hidden cost.** Moving to Forge usually adds scopes and egress declarations, and admins have to approve those. At 1,400 sites, expect some to stall. Start customer communication before you migrate.

## Revenue share

- **The platform doesn't set your share.** To my knowledge, Atlassian's Marketplace commission depends on the listing and payment model (Paid via Atlassian), not on whether you run Connect or Forge. Migrating an existing app with its listing and licences should leave your share the same.
- **A new listing is a different case.** Don't create a separate Forge app or listing, because that would lose your installs and licences. Use the in-place migration path.
- **Atlassian may offer Forge-specific incentives or changes.** I recall programs or tier changes tied to Forge, "Runs on Atlassian" and other badges, but I'm not confident of the details. Check the current Marketplace Partner Agreement and revenue-share page, or ask your Atlassian partner contact.
- **Forge usage costs are a separate margin issue.** Atlassian has been introducing consumption-based pricing for Forge. That isn't a revenue-share change, but a PDF-rendering macro could use a lot of compute. Estimate those costs before you launch.

## What to verify

- The Connect end-of-support date and any freeze on new modules or app versions (Atlassian developer docs, Connect end-of-support page).
- The exact hybrid or "Connect on Forge" migration steps for Paid-via-Atlassian apps (Forge migration guide).
- Revenue-share and incentive terms (Marketplace Partner Agreement, and your Atlassian partner manager).

I can draft the Forge manifest for the macro, or a customer-communication plan for the consent step, if you want either.