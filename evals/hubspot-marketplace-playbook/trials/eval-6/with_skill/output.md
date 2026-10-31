# Ledgerly on HubSpot: what's realistic

† Every HubSpot figure below (counts, durations, dates, thresholds) comes from the playbook. Verify each against current HubSpot developer docs and changelog before quoting it to leadership.

## Verdict

| Goal | Verdict |
|---|---|
| Premier tier next quarter | ❌ Not reachable. Premier needs $7M† attached MRR (or $100K† influenced deal MRR), 10+ reviews at 4.0+, certification, an executive sponsor and account-mapping data sharing. Ledgerly has 45 installs, 6 reviews and a 3.8 average. |
| Certified badge next quarter (Q1 2027) | ⚠️ Possible, not safe. Two of the four gates fail today, and the install gap is the schedule risk. |
| $25 gift card per review | ❌ Don't do it. HubSpot's review guidelines ban compensation of any kind. |
| Rising tier | ⚠️ Unknown. Reviews and rating already pass (5+ at 3.5+†). It depends on attached MRR ($400K†), which only the HubSpot partner dashboard shows. |

## Certification gate vs. today

| Gate† | Required | Ledgerly | Status |
|---|---|---|---|
| Time listed | 6 months | 14 months | ✅ |
| Active installs | 60 | 45 | ❌ need 15 more (+33%) |
| Average API success | above 95% | 88%, mostly 429s | ❌ |
| Verified domain | yes | unknown | ❓ |
| Security questionnaire | yes | unknown | ❓ |
| Uninstall App API | yes | unknown | ❓ |
| Setup guide covering install, scopes, disconnect, uninstall and data effects | yes | unknown | ❓ |
| 3-minute demo video | yes | unknown | ❓ |
| No UI-injecting extension | yes | unknown | ❓ |

**Do not apply until the success rate is clean.** A rejection blocks re-applying for 6 months†. Applying at 88% would push certification past mid-2027.

## Assumptions (I couldn't ask)

- The app is built on the developer platform at a supported version, not a legacy public app. **If it is a legacy app, treat that as the first blocker.** Legacy apps are eligible for delisting after September 2027†, and new certifications get about 60 days† to migrate.
- It has no classic CRM cards. Listed apps had to move to app cards by October 31, 2026†, which is today.
- Active installs means unaffiliated production accounts with successful calls in the last 30 days.
- I don't know your MRR, so the tier picture is incomplete.

## Fix the 429s first (weeks 1-3)

HubSpot allows about 100 requests per 10 seconds per account†. An 88% success rate usually means the sync polls or writes record by record.

1. Throttle per account (per-portal token bucket) at about 80% of the limit.
2. Batch reads and writes with the batch endpoints.
3. Replace polling with webhooks where the object supports them.
4. Back off on `429` using `Retry-After`.
5. Check 401s (expired tokens) and 403s (portals missing a scope). The gate counts every failure, not only 429s.
6. Aim for 97%+ so you have margin. Then hold it for a full dashboard window before applying.

This is also the likeliest cause of your 3.8 rating. Stuck syncs produce one-star reviews.

## Reach 60 active installs

Forty-five installs in 14 months is about 3 a month. At that rate you hit 60 around April 2027, after your Q1 deadline. Leadership has to decide to speed this up.

- Start with existing Ledgerly customers who use HubSpot and haven't installed yet. This is the most efficient source.
- Then ask accounting-firm Solutions Partners to install in their clients' own portals, with consent.
- Count only accounts with successful calls in the last 30 days. The counter lags by days, so aim for 65 to leave a buffer.
- Check for dormant installs. An install with no calls doesn't count.

## Reviews and rating

**Don't pay for reviews.** Gift cards, discounts and refunds all count as compensation. The consequences are removed reviews, a delisting risk, and a failed certification or tier check. Marketing's idea would also destroy the credibility the badge is meant to signal.

What works:

- Customize the review request emails HubSpot sends from day 30. Use no incentive language.
- Send your review link to eligible customers only. That excludes trial users and partners. Don't filter by sentiment.
- Reply to every negative review. You get two replies† per review, and certification checks that you did.
- Stars show only from 10 reviews†, so you need 4 more. After the 429 fix, ask customers whose sync now works.
- Premier and Leading need 4.0+ ratings. Getting from 3.8 to 4.0 with 10 reviews means roughly two or three more 5-star reviews than 3-star ones.

## Timeline

Today is 2026-10-31. Dates are targets.

| When | Milestone |
|---|---|
| Nov 2026 | Ship the throttle, batching and webhook fixes. Confirm the platform version. Start the setup guide, demo video and Uninstall API. |
| Dec 2026 | Hold 95%+ across a full dashboard window. Push installs, aiming for 55+. Update the review email flow. |
| Jan 2027 | Reach 60+ active installs. Verify the domain and complete the security questionnaire. |
| Feb 2027 | Apply, with at least 60 installs and a clean success rate. |
| Mar 2027 | Review feedback and one resubmission. |

I haven't found a documented certification review time, so I can't promise a date. If installs reach 60 only in February, the badge likely lands in Q2. Tell leadership "targeting Q1, likely Q2" rather than committing to Q1.

## What to tell leadership

1. Premier is a 2027 or later goal. Re-check it once certification is done. It rests on MRR, and 45 installs at today's rate doesn't reach $7M†.
2. Certification is the real Q1 target. The two blockers are API reliability, which is engineering work, and 15 more installs, which is a growth decision.
3. Reject the gift cards.
4. Pull the tier dashboard numbers: attached MRR, influenced MRR, and whether you submit influenced deals. Then I can say which tier Ledgerly actually sits at.

## Questions that would change this answer

- Which `platformVersion` is Ledgerly on, and does it use classic CRM cards?
- What do the HubSpot partner dashboard figures show for attached and influenced MRR?
- Are the 45 installs all active in the last 30 days?