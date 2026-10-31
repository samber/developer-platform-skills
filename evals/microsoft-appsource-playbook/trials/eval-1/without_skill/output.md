# Tallyfold AppSource and co-sell plan: sanity check and steps

**Verdict:** ⚠️ The plan is half right. Submitting the Teams app this month is fine. "Then apply for co-sell, and customers burn their Azure commit" has two problems.

I did this from memory, without live research. I'm confident in the structure. Check the thresholds and policy numbers marked ⚠️ against current Partner Center docs before you commit.

## What's wrong with the plan

1. **A Teams app listing is not a transactable listing.** The Teams app (bot plus meeting extension) is a free-to-install listing. It can't be bought through the marketplace, so it can't burn a commit. You need a separate transactable SaaS offer in Partner Center, linked to the Teams app. Co-sell is configured on that SaaS offer.
2. **Burning Azure commit (MACC) is gated on Azure.** As I understand it, a SaaS offer counts toward a customer's MACC only if it's transactable and "Azure benefit eligible". That in turn depends on Azure IP co-sell status, which expects the solution to run on Azure. ⚠️ Verify the exact wording, but you are 100% AWS. That is probably the CRO's biggest blocker.
3. **Co-sell isn't one thing.** There are two tiers, and only one of them motivates Microsoft reps:
   - **Standard co-sell ("co-sell ready"):** You get listed in the partner catalog, and reps may bring you into deals. It carries no quota credit, so reps have little reason to chase it. You can reach this tier from AWS, as long as the product meaningfully integrates with Microsoft. Your Teams and Entra integration should qualify.
   - **Azure IP co-sell:** Reps get quota credit and customers get MACC burn-down. It requires an Azure-hosted solution and a transactable offer. ⚠️ There has historically been a billed-revenue threshold too.
4. **Timeline.** Today is Oct 31, so "this month" means November. Submitting in November is realistic. Being live in November isn't. Allow 2–6+ weeks for Teams validation and rework. Partner Center account verification can add days to weeks, so start it now.
5. **Nobody has asked whether the demand exists.** Count how many open enterprise deals have a MACC and would actually spend it on Tallyfold. Without that evidence, hosting on Azure is a large bet.

## Decision for the CRO (before engineering starts)

| Path | What it gives | Cost |
|---|---|---|
| **A. Teams listing, plus transactable SaaS, plus standard co-sell, stay on AWS** | Discovery in Teams and AppSource, private offers, a co-sell catalog entry | Low. No MACC burn-down, little rep motivation. |
| **B. Path A, plus move enough of the stack to Azure for Azure IP co-sell and MACC eligibility** | Rep quota credit and MACC burn-down | High. A multi-quarter infrastructure project for a 40-person team. |
| **C. Also list on AWS Marketplace** | Customers burn AWS commit on you, and you're already on AWS | Low–medium. The same offer-mechanics work, aimed at the cloud you already run on. |

**Recommendation:** Do A now. Defer the decision on B until you have deal evidence. Consider C in parallel, since it delivers the "burn their commit" story with no migration.

## Steps

### Phase 0: this week (⏳ 2–3 hours)
1. Ask the CRO for the number of open enterprise deals with an Azure commit, and for a named Microsoft contact if any exists.
2. Confirm the Entra tenant and who will own the Partner Center account.
3. Choose A, B, or C above. Get the CRO to agree that "co-sell" means standard co-sell until B is decided.

### Phase 1: Partner Center and compliance (start now, runs in parallel)
1. Enroll in the commercial marketplace program, with legal and tax profile and payout details. Verification can take days to weeks.
2. Complete publisher verification and domain verification for your Entra app registrations.
3. Complete Microsoft 365 App Compliance **publisher attestation**. ⚠️ I believe it is mandatory for Teams store listing. Consider the Microsoft 365 Certification later, because enterprise security reviewers like it.
4. Prepare the privacy policy, terms of use, support URL, and test accounts with a populated tenant.

### Phase 2: Teams app submission (target: submit in November)
1. Finalize the manifest, with a valid bot ID, valid domains, and only the permissions you need. Reviewers reject over-asking.
2. Test the meeting extension (side panel, in-meeting tab, and so on) on desktop, web, and mobile.
3. Check meeting-data access: transcripts, recordings, and real-time media need specific Graph permissions. ⚠️ Some are protected APIs that need Microsoft approval. Request them early because they can gate the submission.
4. Prepare listing assets: icons, screenshots, descriptions, and a demo video if you have one.
5. Submit through Partner Center (the Microsoft 365 and Copilot offer type) and plan for at least one rejection and resubmit cycle.
6. Once approved, publish and set a go-live date.

### Phase 3: transactable SaaS offer (after Phase 1 is done; roughly Dec–Jan)
1. Create a SaaS offer with plans and pricing, and a landing page that accepts the marketplace purchase token.
2. Build the fulfillment integration: a landing page, a webhook for subscription lifecycle events, and the SaaS Fulfillment and Metering APIs. Your billing system must map marketplace subscriptions to Tallyfold accounts.
3. Link the Teams app to the SaaS offer.
4. Set up private offers for enterprise deals. This is the real enterprise-sales workflow. Expect a transaction fee on marketplace sales (⚠️ currently around 3%).

### Phase 4: standard co-sell (after the SaaS offer is live)
1. Complete the co-sell configuration on the offer: a one-pager, ideal customer profile, value proposition, and named sales contacts.
2. Submit for co-sell ready status.
3. Run a partner-development motion alongside the listing:
   - Ask for a Partner Development Manager.
   - Get introductions to Microsoft account teams in your target accounts.
   - Register deals in Partner Center.

   A listing alone gets Microsoft reps' attention only if you do this outreach.

### Phase 5: Azure IP co-sell and MACC (only if you chose Path B)
1. Scope the migration: which workloads need to run on Azure to qualify, and whether a partial footprint is enough. ⚠️ Confirm this with Microsoft before engineering starts.
2. Pass Azure technical validation for the SaaS offer.
3. Meet the revenue thresholds, if any are still in force.
4. After approval, customers can burn MACC on private offers.

## Risks to flag to the CRO

- ⚠️ Teams validation failures often come from permissions, privacy, or a broken meeting flow. Budget rework time.
- ⚠️ Reps rarely sell something they get no quota credit for. Standard co-sell is mostly lead sharing.
- ⚠️ Moving to Azure is not a quick follow-up task. Treat it as a separate project with its own business case.
- ✅ The Teams listing alone still gives you inbound discovery and enterprise trust, and it unlocks private offers.

## Revised one-line plan

Submit the Teams app in November. Start Partner Center enrollment now. Build the transactable SaaS offer in Q1. Treat standard co-sell as a Q1 deliverable. Make the MACC and Azure IP co-sell decision only after the deal-evidence check.

## Questions for you

1. Do you know how many enterprise prospects have a MACC and would use it on Tallyfold?
2. Is any Azure hosting (even a partial footprint) acceptable to engineering?
3. Does Tallyfold already have a Partner Center account and a Microsoft contact?