**Next action (10 min):** Ask your eng lead whether Glasswing's package is managed and registered in the License Management App (LMA). That answer sets what you can measure. Everything below assumes LMA exists. If it doesn't, step 1 grows by about a day.

## Big picture

- ✅ Ship the overhaul next week. It's low risk and cheap to reverse.
- ⚠️ Your theory is half right. A better listing can raise fit. It won't fix churn by itself, so keep that out of the success claim.
- ⚠️ A listing has no effect on the 45-day uninstall rate unless the page filters bad fits or sets correct expectations. Design for that on purpose.
- ℹ️ "No numbers" is not fully true. You can't see AppExchange analytics, but you own the install and uninstall data. Use it.

## Why the churn theory needs a test

- 31% in 45 days has at least four possible causes:
  1. Wrong buyer: the listing attracts the wrong org type.
  2. Right buyer, failed setup: onboarding is the problem.
  3. Right buyer, product gap: a feature is missing.
  4. Trial-and-discard: tire-kickers who were never going to stay.
- A listing rewrite only touches causes 1 and 4. Causes 2 and 3 stay.
- Nobody has looked at the listing in 14 months. The product may have moved since, so the page may sell something Glasswing no longer is. That is a mismatch worth checking first.
- Extra risk: a sharper, more attractive listing may raise installs and also raise churn. Plan to measure fit, not volume.

## Step 1: Baseline from data you own (Thu–Fri, about 4 hours)

No AppExchange analytics needed. Pull this from LMA, your backend, or the subscriber org record:

1. Install date, uninstall date, and days-to-uninstall for every org in the last 14 months.
2. Org attributes: edition, org size or user count, industry if known, and country.
3. Activation proxy: did the org complete the key setup step or first workflow within 7 days?
4. Split the 31% by those attributes. Look for one segment that carries most of the uninstalls.
5. Check the listing's Google Analytics option. If you haven't connected a tracking ID, ask Salesforce partner support whether it's available at your tier. Don't assume. Verify before relying on it.
6. Read the last 20 uninstall or support conversations. Tag each as wrong fit, setup failure, missing feature, or no reason.

Output: one page with "who stays" and "who leaves". This feeds the keywords, the copy, and the screenshots.

## Step 2: Keyword overhaul (Fri–Mon)

You have no search volume data. Do not invent it. Use what's observable.

1. **Seed list from customers.** Use the words that retained orgs use in support, onboarding calls, and reviews. These are real.
2. **Autocomplete and competitors.** Search AppExchange directly. Type your category plus each letter. Note the suggestions and the titles, taglines, and categories of the top 10 competing apps for each seed.
3. **Intent buckets.** Group terms into job-to-be-done ("forecast accuracy", "pipeline hygiene"), object-based ("opportunity", "quote"), and role-based ("RevOps manager"). Skip generic terms like "sales" and "CRM". They draw bad-fit traffic.
4. **Pick 3 primary and 10 to 15 secondary terms.** Put primaries in the listing title, tagline, and first sentence of the description. Spread secondaries through the description and the keyword field.
5. **Add fit-qualifying language.** State who it's for and the prerequisites: Salesforce edition, required objects, team size. Example: "Built for RevOps teams of 5+ on Enterprise edition." This is the main lever on churn. It talks some bad fits out of installing.
6. Record the old title, tagline, description, and keywords in a doc before you edit anything.

## Step 3: Screenshot overhaul (Sat–Tue)

1. Audit the current screenshots against the product as it is today. Replace anything stale.
2. Order them by decision value:
   1. Outcome: the result the user gets, with a short caption.
   2. The core workflow, in the real UI.
   3. Setup, showing time-to-value ("live in N minutes", only if true).
   4. Who it's for and prerequisites.
   5. Integrations or reporting.
3. Caption every screenshot with a benefit, not a feature name.
4. Add a demo video or walkthrough if the listing format allows it.
5. Use realistic, anonymized data. Never show a real customer's data without clearance.
6. Show one screenshot honestly about what setup involves. Setup failure is a likely churn driver.

## Step 4: Approval and ship (Tue–Wed of next week)

- ⚠️ Salesforce reviews listing edits. Submit by Tuesday at the latest. If review takes days, "shipped next week" slips.
- Find out your review turnaround today. Ask partner support, or check your last edit's history.
- Change keywords and screenshots in the same release. This is a conscious trade-off. You can't attribute results to one change. You asked for a full overhaul, so accept that.

## Step 5: Measure (start now, read in December)

- The 45-day uninstall window means a clean churn read arrives about mid-to-late December if you ship the week of 12 October.
- Do not claim churn improved before then.
- Leading indicators, readable within 2 to 3 weeks:
  1. Installs per week against your baseline.
  2. Share of installs from your target segment.
  3. Activation within 7 days.
  4. Early (14-day) uninstall rate by cohort.
  5. Share of installs from orgs that match your "who stays" profile.
- Compare the pre-change cohort against the post-change cohort. Keep the pre-change cohort fixed from Step 1.

**Success rule (set it now, before launch):**
- Win: the target-segment share rises and 14-day uninstall falls, with installs flat or higher.
- Mixed: installs rise but fit falls. The listing is too broad.
- Loss: installs fall sharply and fit stays flat. Revert using your saved copy.

## If churn doesn't move

That's the likely outcome for causes 2 and 3. Then work in this order:

1. Fix the first-run experience.
2. Set up an uninstall survey. Ask one question at uninstall.
3. Revisit the product gap list.

## Decisions I need from you

1. Is Glasswing in LMA, and who can pull the data? (Blocks Step 1.)
2. How many installs per month? Under about 30 and cohort comparisons will be noisy. You would judge on qualitative signals instead.
3. Do you have a Salesforce review turnaround estimate? (Decides whether next week holds.)
4. Who produces the screenshots: you, a designer, or me writing the brief? You have said design is not your strength, so I would brief an outside designer.

## Timeline

| Day | Work | Time |
|---|---|---|
| Thu 10-08 | LMA check, data pull | 2h |
| Fri 10-09 | Segment analysis, uninstall tagging | 3h |
| Mon 10-12 | Keywords and copy draft | 4h |
| Tue 10-13 | Screenshots shot and captioned, submit for review | 5h |
| Wed–Fri 10-14 to 10-16 | Review wait, go live | depends |

⏳ Tight but doable. The review turnaround is the only item I can't estimate.

**Next:** answer the four questions above, starting with LMA.