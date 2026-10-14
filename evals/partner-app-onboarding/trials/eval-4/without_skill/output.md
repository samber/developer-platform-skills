## Benchmark

**I don't have a credible industry benchmark for "time to first submitted app," and I'd advise against quoting one to the exec.** I know of no published, comparable standard for it. Platforms define "partner," "submitted," and "start of clock" differently, so any figure from a blog or deck can't be compared with yours.

For the exec, use these instead:

1. **Your own baseline.** At 5 weeks you have too few partners and too little history. Treat weeks 1-12 as baseline-setting and set a target at the 90-day mark.
2. **Cohort vs cohort.** Compare each signup week against the previous one. This is the benchmark you can defend.
3. **Peer review SLAs as context only.** Public marketplaces (Shopify, Atlassian, Slack) publish review expectations. Those cover approval time, not time to first submission, so don't present them as the same metric.

## Problem with the number as the north star

- **It's censored.** Partners who haven't submitted yet are missing from the median, so it looks good precisely when many partners are stuck. Report it as a survival curve: % of partners submitted within 7, 14, and 30 days of signup. Show the count of not-yet-submitted partners next to it.
- **It stops at submission.** An app can be submitted, rejected, and abandoned and still count as a success.
- **At n of roughly a dozen, a median is noise.** Show counts, not just percentages.

**Suggested north star:** *partners with an approved app that has at least one customer actively using it* (or the count of active installs). Keep time to first submission as the lead indicator beneath it. If the exec insists on the original ask, give them both and explain why.

## What belongs on the dashboard

**1. Partner funnel (counts and conversion per step, by signup-week cohort)**
- Partner signup
- Sandbox or API credentials created
- First successful API call
- Draft app created
- First submission
- Approved and listed
- First customer install
- Active at 30 days

**2. Time metrics (median and p90, with the number not yet reached)**
- Signup to first API call
- Signup to first submission (the exec's number)
- Submission to approval
- Approval to first install

**3. Review health (your side of the experience)**
- Review queue backlog and age of oldest item
- Rejection rate and top rejection reasons
- Resubmission rate and time to resubmit

**4. Stalled partners**
- Partners with no activity for 14 days or more, and the step where they stopped
- This is your outreach list, and it tells you where docs or sandbox friction sits.

**5. Customer-side value (the reason the marketplace exists)**
- % of Halmsted customers with at least one marketplace app installed
- Installs per listed app (look at the distribution, since a few apps will carry the total)
- Retention and expansion of customers with apps vs without, treated as correlation only until you have enough history

**6. App quality guardrails**
- Uninstall rate within 30 days
- App error rate and rating
- Support tickets per app

**7. Partner support**
- Partner ticket first-response time
- Docs search no-result rate

**Segment cuts on everything:** partner type (ISV, agency, customer-built) and integration category.

## Suggested exec framing

"Five weeks in, we have no valid external benchmark. Here is our week-by-week baseline. The north star is partners with an app that customers actually use. Time to first submission is the leading indicator, and we'll set targets at 90 days."