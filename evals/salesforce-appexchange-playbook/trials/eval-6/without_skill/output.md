# Pellucid on AppExchange: 10-week plan

## Do first (Monday, Nov 2)

1. **Sign up** for the Salesforce Partner Program and request a Partner Business Org (PBO). It's free but it gates everything else, and provisioning takes days.
2. Book a call with a Salesforce partner contact. Ask for the **current security review queue time and fee**.
3. Get a decision from the CEO on the "live" definition below.

## ⚠️ The date is mostly not in your control

- **Security review gates the listing.** A public AppExchange listing needs a passed Salesforce security review. That is a queue on their side.
- **First-time failures are common.** I can't give you a pass rate, so I planned for one failed round and one resubmission.
- **Pellucid's backend is in scope.** The package talks to your SaaS, so Pellucid's endpoints, TLS and auth get scanned too, not just the Apex and LWC.
- **The holidays land in weeks 8–9.** Both your team and Salesforce's reviewers will have reduced capacity.
- **"Live" has three possible meanings.** Ask the CEO which one counts:
  - (a) Listed and installable by anyone.
  - (b) Security review submitted and in progress, with demos from a sandbox.
  - (c) Pilot customers installed.

  My recommendation is to commit to (b) plus (c) as the guaranteed outcome and treat (a) as the stretch goal. Decide this in week 1 and tell the CEO before the booth messaging is written.

I assumed the conference is about Jan 8, 2027. Please confirm.

## Design decisions to lock in week 1

- **Package type:** managed package, probably second-generation (2GP). Confirm with your Salesforce contact.
- **Sync direction:**
  - Prefer Pellucid's backend writing to Salesforce through OAuth into a `Meeting_Note__c` custom object linked to Opportunity. The LWCs then only read and display.
  - This keeps Apex small, and less Apex means a smaller review surface.
  - If the CEO insists on Apex callouts to Pellucid, use Named Credentials and no hard-coded secrets.
- **Apex security basics:** enforce CRUD/FLS, use `with sharing`, avoid SOQL injection, and make everything bulk-safe.
- **Licensing:** use the License Management App (LMA) for per-user seats. For the first release, bill with your own billing system and provision licenses in LMA. AppExchange Checkout can come later. Salesforce takes a revenue share on Checkout, so check the current rate.
- **Owners:** one accountable owner, two engineers, and one person for security and compliance.
  - If nobody has shipped Apex or managed packages, hire an ISV contractor in week 1.
  - Learning on this timeline is the biggest risk after the review queue.

## Week by week

| Week | Dates | Goal | Key work | Exit check |
|---|---|---|---|---|
| 1 | Nov 2 | Enrolled and scoped | PBO, Dev Hub, namespace and LMA set up. Architecture, licensing and billing decisions made. Contractor hired if needed. List Pellucid's security posture (SOC 2, pen test history, TLS, auth). Book a **pen-test vendor now**, since lead time is 2–3 weeks. | PBO live, namespace claimed, scope doc signed |
| 2 | Nov 9 | Skeleton works | Package project and CI with Salesforce Code Analyzer on every PR (scan-clean from day 1). `Meeting_Note__c`, permission sets, OAuth app. LWC #1 (notes panel on the Opportunity page). Pellucid sync endpoint and mapping design. | Notes from one Pellucid account appear on a test Opportunity |
| 3 | Nov 16 | Feature-complete | LWC #2 (setup/connect screen or note detail). Apex sync with error handling and retries. LMA license check in code. Tests above 75% coverage (aim for 90%). Pen test starts. | **Feature freeze Friday** |
| 4 | Nov 23 | Submit security review | Run the Salesforce partner scanner and fix findings. Scan Pellucid endpoints and TLS. Write the review pack: data-flow diagram, test org credentials, setup guide, false-positive notes. Promote the package version. Pay the fee and submit. The US Thanksgiving holiday is Nov 26. | **Submitted by Fri Nov 27. Hard stop: Dec 4.** |
| 5 | Nov 30 | Build while in queue | Listing draft: copy, screenshots, 2–3 min demo video, pricing, terms, privacy, support SLA. Test install and upgrade in fresh orgs, including trial and assigned licenses. Pen-test report in and fixes done. | Listing draft done, pen-test findings closed |
| 6 | Dec 7 | Review feedback | Respond to Salesforce within 24 hours. Fix findings, cut a new package version, resubmit. Start design-partner installs in sandboxes (2–3 customers). | **Go/no-go #1 (Dec 11):** if there's no result or major failures, switch booth messaging to fallback (b)/(c) |
| 7 | Dec 14 | Resubmit and prep booth | Resubmission in queue if needed. Demo script, a stable demo org, one-pager, sales talk track, lead capture. Name two people to answer Salesforce during the holidays. | Booth kit ready, holiday coverage named |
| 8 | Dec 21 | Holiday, minimal work | Only react to Salesforce messages. Marketing prep only. | **Go/no-go #2 (Dec 18)** |
| 9 | Dec 28 | Listing submission | If security review has passed, submit the listing for AppExchange approval and set up billing and trial flow. Draft launch comms. | Security review passed, or fallback confirmed |
| 10 | Jan 4 | Publish and verify | Publish. Install from the live listing into a fresh org and run the whole trial → purchase → license path. Final booth check. | **Listed, or fallback booth plan in use** |

## Outcome scenarios

- **Passes first time (around week 6):** you're listed by weeks 7–8 with about 2 weeks of buffer.
- **Fails once (my base case):** you resubmit in week 7 and pass around week 9, so you go live in week 10 with no slack.
- **Fails twice, or the queue is long:** you're in fallback (b)+(c). Say "in Salesforce security review, available to pilot customers" at the booth. Don't claim "available on AppExchange" until you're listed, and check Salesforce's trademark rules for partner wording.

## Risks and mitigations

- **Review queue or fee changes:** ask in week 1 and re-check at week 4.
- **No Apex experience on the team:** contractor in week 1, not week 4.
- **Pellucid backend findings:** pen test early and fix before submitting.
- **Scope creep (extra components, Checkout, fancy sync):** freeze at end of week 3, with nothing new until after the conference.
- **Silent holiday gaps:** two named responders and a shared inbox.

## Things to verify with Salesforce

The program fees, review fee and turnaround, 2GP vs 1GP guidance, revenue share and listing requirements are from memory and may be out of date. I did not look anything up.

## Questions for you

1. Which of (a), (b) or (c) counts as "live" for the CEO?
2. Is the conference date Jan 8, or earlier?
3. Does anyone on the team have Apex or managed-package experience?
4. Does Pellucid already have a Salesforce integration, or a SOC 2 report or recent pen test?
5. Can Pellucid's backend push notes into Salesforce, or must Apex pull them?
6. What is the budget for a contractor, pen test and fees?