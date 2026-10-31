# Tallyforge Tables: Connect to Forge sequencing and revenue share

**Short answer:** Don't add the macro to `atlassian-connect.json`. Ship it as a Forge module in the first Forge version of your existing listing, and do the Forge migration now, not next year. Connect does not "keep working until 2027" in any way that helps you. Migrating does change your revenue share, in your favor, but only once every Connect module and Connect scope is gone.

All figures marked † come from the playbook and its reference. Check them against current Atlassian developer docs before you quote them. Atlassian has changed these rules several times within a year.

## Assumptions

I couldn't ask, so these are my assumptions. Tell me which are wrong.

1. **Macro backend:** the PDF export runs on your existing backend, called through a Forge remote. This decides the egress domains and scopes you must declare up front.
2. **Payment model:** Tallyforge Tables stays Paid via Atlassian (PvA), with no change to free vs paid.
3. **Connect modules:** you have several Connect modules today (macros, admin pages, and so on). I don't know how many, and that is the main schedule risk.
4. **"This month":** today is 31 Oct, so I read it as "as soon as review allows". A Marketplace review cannot finish inside a few days.
5. **Connect updates:** you haven't shipped a Connect descriptor update since March 2026. If you have, that contradicts the platform dates below, so verify with Atlassian.

## Why the Connect plan fails

| Claim | What the platform says |
| --- | --- |
| "Add it to `atlassian-connect.json` like always" | Apps with a Connect descriptor stopped receiving updates in Mar 2026†. Since 17 Sep 2025†, Atlassian accepts only Forge apps for new Marketplace submissions. A new macro in the descriptor would not be published. |
| "Connect keeps working until 2027, migrate next year" | 31 Jan 2027† is Connect **end of support**, with critical security patches only. It is about 13 weeks away. "Next year" starts after that date. |

I can't confirm from these sources whether installed Connect apps keep running after that date. Don't build a plan that relies on it.

## Recommended sequence

**Today (week 0)**
- Freeze the Connect-descriptor macro work. Nothing there can be released.
- Inventory every Connect module and Connect scope, and every remote host.
- Write the end-state list for Forge: each scope with the feature that calls it, and each egress domain with its `inScopeEUD` flag. Include everything the PDF macro needs.

**F1: hybrid Forge version on the same listing, containing the PDF macro**
- Declare Forge on the existing app by setting `app.connect.key` in `manifest.yml`.
- Put the PDF macro in as a Forge module, with a Forge remote to your backend.
- Front-load every Forge scope, remote and fetch permission the end state needs, including the macro's. In the first Forge version these ship without admin approval, except `read:chat:rovo` and scopes that elevate beyond your Connect scopes. Afterwards, while any Connect module remains, the same additions need admin approval.
- Do not change the Connect `baseUrl`, any auth provider, or free vs paid in this version.
- Keep PvA as it is. Don't touch licensing.
- Declare egress correctly now. Adding a domain later, or flipping `inScopeEUD` from false to true, makes a major version.
- Test only in development or staging, with `forge install --license active`. Never install the production build on your own site, because every production install of a paid app is billed.

**F2: remove Connect**
- Port the remaining Connect modules to Forge, then remove every Connect module and Connect scope.
- Removing a scope counts as a major version, and removing the Connect remote needs `forge version bulk-upgrade`.
- Suspended or access-token installs never auto-upgrade. Find them and contact those customers directly.
- Ship this as one planned major, with release notes that tell admins why.

**Timeline (backward from 31 Jan 2027†)**

| Step | Timing |
| --- | --- |
| Submit F1 | First half of Nov, after the ECOHELP access check and the questionnaire and Privacy & Security tab updates |
| Review rounds | About 3 weeks per round†, plus one returned round, so F1 is live early to mid Dec at worst |
| Start F2 | As soon as F1 is submitted, in parallel. F2 can only be submitted once the Connect module ports are done |
| F2 live and bulk-upgraded | Needs about 6 weeks of review, so the module ports must be code-complete around mid Dec to meet 31 Jan |

If the module ports are large, F2 may slip past 31 Jan. That is survivable, but you would be on an unsupported platform. Scope the ports this week, because that answer sets the real date.

The macro still ships this month in the sense that you build and submit it this month. Customers get it when F1 clears review.

## Revenue share if you migrate

**Rates for PvA, from 1 Oct 2026†:**

| Framework of your latest listed version | Partner share |
| --- | --- |
| Connect, or any Connect module or scope | 75%† |
| Forge only (no Connect module or Connect scope, OAuth, Forge UI) | 83%† |

- **Today:** you are at 75%.
- **After F1 (hybrid):** you stay at 75%. A single remaining Connect module or scope keeps you there. The jump to 83% needs F2.
- **100% tier:** Atlassian pays 100% of Forge revenue until $1M lifetime Forge revenue†, summed across your Forge apps. Connect-era revenue from your 1,400 sites does not count toward that threshold. I can't tell from my sources whether a hybrid app's revenue qualifies for the 100% tier, so confirm with Atlassian before you model it.
- **What doesn't change:** payout is within 30 days after the month in which $500 profit accrues†. The refund rules don't change either.

**Costs to budget:**
- Forge consumption billing: usage above each monthly free allowance is invoiced to you†. That is new cost, and it can offset part of the 8-point gain. Estimate it from your PDF rendering and storage patterns.
- Because of the macro, think about where the PDF rendering runs. A remote to your backend keeps compute on your side, but egress must be declared correctly.

## Irreversibles register

| Decision | Locks in | Owner and date |
| --- | --- | --- |
| Forge on the existing listing | `app.connect.key` link, hybrid state | Eng lead, before F1 submit |
| Scopes, remotes, egress in F1 | Each later addition is a major version needing consent | Eng lead + security, scope list frozen this week |
| Payment model stays PvA | Changing it is a re-review plus an admin-consented major | Product, no change |
| Connect `baseUrl`, auth provider | Don't change in F1 | Eng lead |
| App name | Keep as is | Product |
| Removing Connect scopes (F2) | A major version, needs `forge version bulk-upgrade` | Eng lead, F2 |

## Submission checklist (F1)

| Prerequisite | Owner |
| --- | --- |
| Submitter can open ECOHELP tickets (test one) | Eng lead |
| App security questionnaire (Forge variant) | Security |
| Privacy & Security tab: data stored and where, one justification per scope, trust-center link | Security |
| Scope and egress list for the reviewer | Eng lead |
| Privacy policy, End User Terms, DPA, docs URL, support contact current | Legal / support |
| Test credentials and sample data on the ticket | Eng lead |
| Separate unlicensed copy for testers (a licensed app can't be shared by link) | QA |

## Post-listing checks

- F1 approved within two rounds.
- Share of installs on the latest major at 30 and 90 days after F2, with a named list of suspended or access-token installs.
- Zero security tickets past due. Fix times are Critical 10 days and High 4 weeks†.
- Ship at least one version every 18 months†.

## Three questions that would change this plan

1. How many Connect modules and scopes exist, and how long to port them?
2. Does the PDF macro run on your backend, or inside Atlassian's compute?
3. Do enterprise buyers need data residency or a vendor security review? If so, add the trust ladder (Privacy & Security tab, then bug bounty, then Atlassian Enterprise Certified) to the F2 timeline.