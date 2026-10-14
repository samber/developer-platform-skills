# Latchpoint: AppExchange + Built for NetSuite

## The number

**About $300K in year 1, and about $100K a year after that.** Three-year total is roughly $500K. I built this from assumptions, not quotes. The fees marked "verify" below are from memory.

| Line | Year 1 | Run-rate/yr |
|---|---|---|
| Engineer, about 11 months sequential (NetSuite SuiteApp about 6, Salesforce managed package about 5) at ~$220K loaded | ~$200K | ~$60K (about 25–30% of an engineer for upgrades, API changes, and support) |
| Security review and scans (Salesforce review fee, code scanning, a pen test) | ~$15K | ~$10K (re-review per major release) |
| Partner programs, dev/sandbox orgs, listing assets, legal terms | ~$15K | ~$10K |
| Support, onboarding, and docs for two new channels | ~$30K | ~$20K |
| Contingency (2–3 security-review rounds are normal) | ~$40K | n/a |
| **Total** | **~$300K (range $250–400K)** | **~$100K** |

Treat the Salesforce revenue share (historically 15% on the first $1M) and the Salesforce review fee (a few thousand dollars) as unverified. Check both before the CFO signs.

The cash number leaves out the biggest cost. **You have one integration engineer, so the whole roadmap stops for about a year.** If that engineer also covers your existing integrations, those get worse.

## Is the $900K real?

It is bookings, not profit, and it isn't yet probability-weighted.

- At a 40% close rate and 75% gross margin, $900K becomes roughly $270K a year of recurring gross profit.
- Against about $300K up front and $100K a year after, that pays back in about year 2, and only if the deals survive a 12-month wait.
- Deals stalled today won't wait a year. Many will close elsewhere or die.

## Should you do it?

**Not both, and not as one commitment. Do one, gated.**

1. **Split the $900K by platform.** Which deals need NetSuite, and which need Salesforce? Build for the larger half first.
2. **Ask Sales what actually blocks each deal.** Is it the badge or listing, or is it that no working connector exists? Buyers often need the integration, not the credential. If it's the connector, ship it unlisted in about 3 months, which is far cheaper. An iPaaS such as Celigo or Workato is another option.
3. **Check Built for NetSuite eligibility before spending anything.** As I recall, it requires a SuiteApp built on NetSuite's platform, a technical review, and a minimum number of live customers. You have two. This could be a hard blocker, so verify it first.
4. **Get written commitment.** Ask for signed LOIs or contingent POs from the stalled deals that name the listing or badge as the condition. If Sales can't get them, the $900K is a hope, not a number.
5. **Review the second platform at month 6.** Use real close data from the first.

**My recommendation:** approve about $150–200K for the first platform only. Make the second a separate decision, gated on step 3 and on evidence that the first one unblocked deals. Doing both at once would take your only integration engineer for a year on a bet nobody has validated.

## Questions for you

- What's the NetSuite versus Salesforce split of the $900K?
- Does a working connector already exist for either platform?

Those two answers could move this from "one, gated" to "NetSuite only" or "neither, build an unlisted connector."