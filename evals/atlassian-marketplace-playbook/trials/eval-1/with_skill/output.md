# Notebridge for Jira: Atlassian Marketplace plan

Three of your four decisions change under the Atlassian Marketplace playbook, and the 6-week listing date is at risk.

| Your plan | Verdict | Replace with |
|---|---|---|
| Build as a Connect app | ❌ Not possible | Forge UI with Forge remotes to your existing backend |
| List Free, sell Pro on Stripe | ⚠️ Unruled and risky | Get Atlassian's written ruling before building billing |
| Cloud Fortified right after launch | ❌ Closed to new apps | Atlassian Enterprise Certified (AEC), later |
| Listing live in 6 weeks | ⚠️ Only if the first review round is clean | Demo from a separate dev copy, and don't promise "live" |

Figures marked † are Atlassian's and change often (Atlassian has changed its framework, badge and revenue-share rules within one year). Verify each against current Atlassian developer docs before you quote it.

## Do this first (Mon 2 Nov, about 2 hours)

1. Have the submitter open a test ticket in the ECOHELP portal to confirm access. If it fails, file a support request.
2. Start partner verification (KYC/KYB). It takes 2-3 business days† and happens once.
3. Open an ECOHELP ticket asking for a written ruling: can a free Marketplace app's Jira features (auto-assign, bulk sync) be unlocked by a plan sold on our own site through Stripe? Link the ticket in your tracker.

## 1. Assumptions

I couldn't ask questions, so each gap below is one assumption. Correct any that are wrong.

- **Stage:** Not built. No Connect app exists yet.
- **What works without an account:** Nothing today. Every feature needs a paid Notebridge account.
- **Who pays:** Notebridge seats ($12/user/month, Stripe) are the only revenue. You want to charge for Jira-side features on top of that.
- **Security, data residency and egress:**
  - Enterprise buyers want a security review.
  - Residency is unknown.
  - Meeting summaries flow from your backend into Jira, so egress is unavoidable.
  - You have no SOC 2 or ISO 27001 report yet.
- **Launch date:** A conference around Fri 11 Dec 2026, with the listing pinned to it. Swap in the real date.

## 2. Decisions and the answers that drove them

### Architecture: Forge UI with remotes

- **Forge is the only option.** The Marketplace has accepted only Forge apps since 17 Sep 2025†. Connect-descriptor apps get no updates, and Connect support ends 31 Jan 2027†.
- **What this means for you.** "Connect just points at our servers" is also true of Forge remotes: they call the same backend. The OAuth work you already have is mostly reusable.
- **3LO listing (cheapest path) is out.** Your issue panel needs an in-product surface (your answer 1), and AEC is a stated goal (answer 4). A 3LO listing has neither.
- **"Runs on Atlassian" is out of reach.** It requires no egress, and a connector must send data to your backend. Offer data residency for remote data, disclosed egress and AEC instead.
- **Egress:**
  - Declare every first-hop egress domain in version 1, with no broad wildcards.
  - Set `inScopeEUD` correctly. Summaries are end-user data, so it is probably `true`.
  - Any later addition, or a false → true flip, is a major version.
- **Authentication:**
  - Use OAuth 2.0 or Forge auth.
  - If Notebridge account linking uses a Forge external auth provider, declare it in version 1. Adding one later is a major.
  - Never collect Atlassian API tokens.
- **Budget Forge consumption billing.** Usage above the monthly free allowance is invoiced to you, free apps included.

### Payment model: the open question

Your "Free listing plus Pro on Stripe" plan sits where Atlassian's own texts conflict.

- A free app must be useful "as is".
- Atlassian recommends Paid via Vendor, which Forge apps cannot use.
- Atlassian has published no ruling that an external plan can unlock the app's own features. It reads as Paid via Vendor.
- A rejection costs a 3-week round, which you can't afford.

Recommended path:

1. **Free, as a connector.**
   - The listing states that a paid Notebridge account is required.
   - Add some in-product value that works without an account: a read-only summary panel, a preview, or sample data.
2. **Ship v1 with the core only:** action items → Jira issues, plus the summary panel. Hold the Pro features (auto-assign, bulk sync) for v2.
3. **Decide the Pro route by Fri 13 Nov (the submission gate):**
   - **If Atlassian rules yes in writing:** gate Pro in your backend via Stripe.
   - **If it rules no or stays silent, and you want Atlassian-app revenue:** use Paid via Atlassian (PvA) for Pro. This is a new version with licensing enabled, re-approval, and a major each site admin must accept. Existing installs count as unlicensed until the admin subscribes.
   - **Mitigation:** keep v1 features free for a stated grace period and gate only new features.
4. **Start on PvA from v1 if Atlassian-app revenue is the real goal.** "Ship free, switch to paid later" stalls adoption on sites that never accept the major. The playbook warns against it.

PvA mechanics, if you use it:

- Prices are per host-site user count, with lower per-user rates at higher counts.
- **A PvA license matches the Jira site's licensed users.** Customers can't license only the Notebridge seats, so you can't mirror the $12 per Notebridge seat model.
- Annual price is 10 times monthly†.
- The partner share is 83%† for Forge-only apps, and 100% until $1M lifetime Forge revenue†.
- Payout comes within 30 days after the month in which $500 profit accrues†.
- Adding an edition (Standard or Advanced) is a re-review.
- Every partner tier requires all paid apps to be PvA. A Stripe-only model would block partner tiers later.

### Security: AEC, not Cloud Fortified

Cloud Fortified takes no new apps and is phased out by end 2026†. AEC replaces it. It requires:

- Forge-only with no Connect modules.
- A SOC 2 Type II or ISO 27001 report.
- A public trust center from an accepted provider.
- An annual pen test.
- A public bug bounty.
- A Statuspage URL on the listing.
- Residency for remotely stored end-user data.

"Right after launch" doesn't fit. Without a SOC 2 audit already running, AEC takes months. Run the ladder in value-per-effort order:

1. **Now (hours):** Complete the Privacy & Security tab, with a trust-center link. Every security reviewer reads it. This answers most of what your enterprise prospects ask.
2. **After launch (3+ weeks lead time†):** Run a public Marketplace bug bounty.
   - Notebridge funds the reward pool, minimum $5,000 upfront†.
   - Every finding becomes an SLA-bound ticket.
   - Staff for it first. A Critical finding must be fixed within 10 days†.
3. **Months:** AEC, once a SOC 2 Type II or ISO 27001 audit is under way. Promote it when enterprise deals stall on vendor security review.

**Question for you:** is a SOC 2 audit already planned or running? If yes, AEC moves up the list.

## 3. Irreversibles register

Freeze these by Fri 13 Nov. Owners are roles, so name the people.

| Irreversible | Decision | Owner | Date |
|---|---|---|---|
| Framework | Forge UI + remotes | Eng lead | 2 Nov |
| Payment model | Free v1 now; Pro route via the ruling | Founder/CEO | 13 Nov |
| Licensing flag | Off in v1 unless starting on PvA | Eng lead | 13 Nov |
| Scopes | Minimal, one per v1 feature, justified in writing | Eng lead | 12 Nov |
| Egress domains and `inScopeEUD` | Exact hosts, no wildcards | Eng lead + security | 12 Nov |
| Auth provider and client ID | Declared in v1 | Eng lead | 12 Nov |
| App name | "Notebridge for Jira" (never "Jira Notebridge") | Product | 6 Nov |
| Submitter email | Company domain, needed for PvA | Founder/CEO | 2 Nov |

Two scope warnings:

- **No broad scopes "to avoid future consent prompts."** Reviewers check each scope against a feature, and Ecoscanner flags unused scopes.
- **v2 may need a major.** If auto-assign needs scopes beyond the core, v2 is a major version. Admins must accept it, and until they do their sites stay on the old major. Write release notes explaining why.

## 4. Submission checklist and timeline

### Checklist

| # | Item | Owner |
|---|---|---|
| 1 | ECOHELP access confirmed by a test ticket | Submitter |
| 2 | KYC/KYB complete | Founder/CEO |
| 3 | App security questionnaire (Forge variant); "fail" answers block the listing | Eng lead |
| 4 | Partner security questionnaire (informational) | Eng lead |
| 5 | Privacy & Security tab: data stored and where, one justification per scope, trust-center link | Security |
| 6 | Reviewer list: each scope with its feature; each remote host with the data sent and why | Eng lead |
| 7 | Privacy policy, End User Terms, DPA (you process personal data), documentation URL, support contact | Legal/ops |
| 8 | Payment profile | Finance |
| 9 | Test credentials and sample data for Notebridge on the ticket | Eng lead |
| 10 | Sharing enabled in the developer console, then submit | Eng lead |
| 11 | Listing copy and screenshots (see `integration-listing-optimization`) | Product/marketing |

Warnings:

- Practitioners report most "Timeout" rejections come from unfinished prerequisites, not the reviewer. Ask on the ticket what timed out.
- Once submitted or licensed, the app can't be shared by installation link. Build a separate unlicensed copy for the demo and for testers.
- The listing is locked during review. Request copy changes on the ticket.
- A scan finding rejects the ticket. Fix it, then resubmit.

### Timeline backward from the event

The playbook budgets three weeks per review round plus one returned round. Official figures run from one week to 15 business days†. Six weeks of review is the whole schedule, and it would have needed a submission by today. The first round has to be clean.

| Week | Dates | Work |
|---|---|---|
| 1 | 2-6 Nov | Access ticket, KYC, ruling ticket, Forge scaffold, privacy policy/EUT/DPA, trust-center setup |
| 2 | 9-13 Nov | Core feature working, scope/egress list, questionnaires, payment profile. **Freeze irreversibles and submit by Fri 13 Nov.** |
| 3-5 | 16 Nov-4 Dec | Review round 1. Meanwhile: build the demo copy, finish the trust center, decide on the bug bounty |
| 5 | by 4 Dec | Best case: approved. If returned, fix every point in one pass and resubmit |
| 6 | 7-11 Dec | Conference. If the round was returned, the next decision lands around 25 Dec or later, and holiday slowdown is unmeasured |

**For the conference:** demo from the separate unlicensed dev copy, installed with `forge install`. Say "in Atlassian review" rather than "live". Treat a live listing as a bonus.

For paid testing, never install the production build on your own site, because every production install of a paid app is billed. Use development or staging with `forge install --license active` (or `inactive`, `trial`).

## 5. Post-listing calendar

| When | Action | Check |
|---|---|---|
| Submission → approval | Answer every ticket point in one pass | **Approved within two rounds** |
| Day 1 | Confirm trust-center link and Statuspage on the listing | No gaps in the Privacy & Security tab |
| Day 30 | Review installs by major version | **Share of installs on the latest major is on target** |
| Day 30 | Review bug-bounty readiness | Reward pool funded, triage owner named |
| Day 90 | Re-check install share; batch any privilege-escalating changes into one planned major | **Latest-major share is on target** |
| Continuous | Fix security findings in time: Critical 10 days†, High 4 weeks†, Medium 12 weeks†, Low 25 weeks† | **Zero AMS tickets past due** |
| Continuous | Report any security incident within 24 hours† | Incident runbook names the owner |
| Continuous | Answer Atlassian contacts; 90 days of silence hides the app† | Contact alias monitored |
| Every 18 months | Ship at least one version, or a compliance review starts† | Release on the calendar |
| Quarterly | Review the AEC trigger: SOC 2/ISO audit status and stalled enterprise deals | Go/no-go recorded |
| Pre-v2 | Use `forge version bulk-upgrade` for majors that escalate no privilege; use rolling releases while consent is pending | Previous major still works |

## Open questions for you

1. Must the Pro revenue come from Atlassian-installed Jira customers, or is your Notebridge seat revenue enough? This decides PvA from v1 versus the ruling path.
2. Is a SOC 2 or ISO 27001 audit planned or running?
3. What is the exact conference date? It moves every row in the timeline.