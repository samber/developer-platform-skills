# Tallyfold: Microsoft Marketplace plan check

## Verdict

The plan is half right. Two parts of it won't deliver what the CRO expects:

1. **A Teams app never earns co-sell.** Microsoft excludes Teams, Outlook and Excel apps from co-sell-ready status. Co-sell and MACC run on a separate transactable SaaS offer, which the Teams app links to. "Submit the Teams app, then apply for co-sell" has no co-sell target at the end. Plan three objects with three reviews: the Teams app, the SaaS offer, and the co-sell solution (collateral attached to the offer).
2. **"Enterprise customers burn their Azure commit on us" is not reachable while you run on AWS.** MACC drawdown requires Azure IP co-sell eligibility. That means a solution primarily on Azure, technical validation, an architecture diagram, and $100K† of Azure consumed or billed. MACC counts only usage that runs in Azure. Your realistic ceiling is **co-sell ready**, which costs days of collateral work. It makes you visible in Microsoft's internal seller catalogs. It is not pipeline, and practitioners report months before any seller engages.

Two things do work in your favor:

- A non-Azure SaaS may list only if it integrates with or extends a Microsoft product and accepts Entra SSO. Your Teams bot and meeting extension should meet that test, but confirm it in the certification notes.
- Transactable SaaS plus private offers still gives enterprise buyers a Microsoft-billed procurement path at a 3% fee†. The fee halves† for renewals, migrated contracts and upsells if you tick the renewal attestation when creating the offer.

If the real goal is burning cloud commits, you run on AWS, so AWS Marketplace is the matching channel. See `samber/developer-platform-skills@aws-marketplace-playbook`.

## Assumptions (gaps I could not ask about)

- **Stage:** Building. The app is done, but I assume no Partner Center account and no SaaS offer yet.
- **Pricing:** I assume per user or per seat. Teams linking requires it. If you price on meeting minutes or usage (metering), that conflicts, and you must decide now.
- **Hosting:** AWS us-east-1 only, no Azure workload and no migration planned.
- **Microsoft integration:** The Teams bot and meeting extension count as the integration, and Entra SSO is acceptable.
- **Ownership:** Nobody yet owns Microsoft seller outreach. Please name an owner.
- **Date:** "This month" is already October 31, so I read it as "submit in November". Microsoft figures marked † need verifying in Partner Center before you quote them.

## Path

**Transact SaaS + private offers, plus the linked Teams app. Stop at co-sell ready.** Delete Azure IP co-sell and MACC unless an Azure migration is already decided.

- **Answer 2 (AWS)** removed Azure IP co-sell and kept co-sell ready.
- **Answer 1 (Teams app)** added the Teams-linked rung, which forces per-user pricing.
- **Answer 3 (pricing)** is still unknown. Per-user pricing is a lock-in, so it's the first decision.
- **Answer 5 (date)** is vague. A hard first-transaction date would promote private offers over the Teams link.

## Locked-choice register

These cannot change after the SaaS offer or plan publishes. Decide before the first publish.

| Choice | Proposed | Owner | Decision date |
|---|---|---|---|
| Pricing model (same for all plans in the offer) | Per user | unassigned | unassigned |
| Plan IDs | one per tier, e.g. `team`, `business`, `enterprise` | unassigned | unassigned |
| Per-user seat minimum and maximum | unknown | unassigned | unassigned |
| Metered dimensions | none (Teams-linked offers must be per user, and metering exists only on flat-rate plans) | unassigned | unassigned |
| Public plan going private | not allowed afterwards, so choose deliberately | unassigned | unassigned |
| Standard contract vs your own terms | unknown | unassigned | unassigned |

Questions for you:
- Who owns each row?
- Do you sell on usage anywhere today?

Don't do "flat rate now, Teams link later". It needs a second offer, a new review and a new MACC enrollment.

Microsoft pages disagree on whether a published listing-only SaaS offer can switch to transact. Build transact from day one.

## Steps

**Week 1 (Nov 2–6): accounts and decisions**
1. Create the Partner Center account in the AI Cloud Partner Program. Validate the tax profile (up to 48 h†) before the payout profile.
2. Complete **Publisher Verification**. It is a Must fix for the Teams app.
3. Fill the locked-choice register above.
4. Register a multitenant Entra app that accepts work and personal Microsoft accounts. Request only `User.Read` during activation.

**Weeks 2–3 (Nov 9–20): submit Teams in parallel with the offer build**
5. Check the Teams package against `references/submission-packet.md`:
   - names, descriptions, icons and terms/privacy URLs identical in the manifest and Partner Center;
   - brand-prefixed app name, with no "Teams", "Microsoft" or "Beta" in it;
   - at least three captioned screenshots inside Teams;
   - production-only `validDomains`;
   - a bot that sends a welcome message, answers Hi, Hello and Help, and never dead-ends;
   - a tab that adds value beyond hosting your website;
   - manifest schema 1.25 or later† for channel-enabled apps.
6. Write the Teams Notes for certification: two or more test accounts with no MFA, setup steps, a demo video, the SSO fallback flow, and support/privacy/EULA links that work without login.
7. Validate the package in the Teams Developer Portal on desktop, web and mobile, then submit.
8. Build the SaaS offer in parallel:
   - a landing page that is always up, has no `#` in the URL, shows no secrets and offers no downloads;
   - Fulfillment API v2 (resolve the purchase token within 24 h, then activate);
   - a webhook that validates every call through the Get Operation API and answers plan and seat changes within 10 seconds;
   - hourly metering only if you use it (you shouldn't);
   - Entra SSO, with the admin consent disclosed in the description.
9. Write the SaaS Notes for certification: test accounts without MFA and the purchase-to-activation steps. Missing notes are a top failure.
10. Test on a separate DEV offer in preview at a nominal price. **Never press Go live on it.** Test purchases are invoiced and refunded only if cancelled within 72 h†.

**Weeks 4–8 (Nov 23 – Dec 18+): review cycles**
11. Teams validation takes 3–6 weeks†, with a report targeted within 24 working hours†. Feedback arrives as Must fix, Good-to-fix, Blocker or Query. Fix, reply, wait for confirmation, then resubmit. Budget one failed cycle.
12. **Publisher Attestation:** complete it the day the Teams app goes live. It is a post-listing duty, not a listing gate. Renew it yearly. An already listed app attests before each update.
13. Publish the real SaaS offer to a preview audience, then Go live. Certification duration isn't in the sources I have, so verify it in Partner Center.

**After both are live (likely January)**
14. Add `subscriptionOffer` (`publisherId.offerId`) to the manifest and set "Additional purchases" to Yes. This update goes through Teams validation again.
15. Run the link checks:
    - admins and non-admins can buy;
    - admins can bulk-buy in the Teams admin center;
    - "Set up now" reaches the landing page;
    - assigning, removing and reassigning licenses shows correct counts.

    The Notes must carry an end-to-end functional document and license-management steps. The same publisher must publish both objects, or you need written authorization from the other.
16. Sell the first deals as private offers, and tick the renewal attestation on any renewal, migrated contract or upsell. It cannot be added after creation.

## Submission plan summary

- **Teams validation items:** the checklist in step 5, with Publisher Verification first.
- **SaaS certification notes:** steps 8–9.
- **Attestation date:** Teams go-live day, then yearly.

## Co-sell plan

- **Target status:** co-sell ready, not Azure IP co-sell eligible.
- **Threshold gap:** the $100K† Azure-consumed-or-billed bar and the primarily-on-Azure test are both unmet. They stay out of scope unless you commit to an Azure migration.
- **Enrollment:** enroll in Frontier Accelerate for Marketplace first. Its FAQ makes enrollment a prerequisite for any co-sell listing. A no-cost tier exists.
- **Collateral (Co-sell > Solutions):**
  - one-pager and pitch deck, on Microsoft templates;
  - a reference architecture diagram, recommended even at co-sell ready;
  - the Microsoft platforms you integrate with (Teams, Entra);
  - a sales contact per geography;
  - expect a few weeks of review†.
- **Owner:** unassigned. Raise it with the CRO.
- **First seller accounts:** target customers with Microsoft-managed accounts that run Teams meetings heavily. Register your own opportunities in Partner Center referrals, because unmanaged accounts never qualify for IP co-sell registration. Sellers act on quota, so bring named deals. You can't lead with MACC drawdown, so lead with the Microsoft-billed procurement path and the Teams integration.

## Timeline from today (Oct 31)

| When | Milestone |
|---|---|
| Nov 2–6 | Partner Center, verification, register decisions |
| By Nov 20 | Teams app submitted; SaaS offer and DEV tests done |
| Late Nov – mid Dec | Review cycles, including one failed round |
| Mid Dec – early Jan | Teams app live and attested; SaaS offer live. Holidays will slow this. |
| Jan–Feb 2027 | `subscriptionOffer` link revalidated, in-Teams purchase live |
| Parallel, after offer live | Frontier Accelerate enrollment and co-sell-ready collateral (a few weeks†) |

The first private-offer transaction is possible once the SaaS offer is live, around mid-December to January. The in-Teams purchase flow comes a few weeks later.

## What to tell the CRO

- "On AppSource" is achievable in about 6–10 weeks.
- "Microsoft reps selling us" is only possible as co-sell ready visibility, and it needs your own named opportunities.
- "Customers burn Azure commit on us" needs an Azure-primary architecture. On AWS, use AWS Marketplace for commit burn.

## Open questions for you

1. Is your pricing per user today, or usage-based?
2. Who owns Microsoft seller outreach?
3. Is any Azure migration actually on the table?
4. Do you already have a Partner Center account?