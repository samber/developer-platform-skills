**Do today: revoke the `bp_live_` key in the `checkout-node` 2024 commit.** The customer emailed a week ago. Confirm whose key it is and whether it is already dead. Revoking is the fix. Rewriting git history does not remove forks or cached copies.

## Triage

| Repo | Verdict | Owner | Note |
|---|---|---|---|
| checkout-node | 🔴 Keep, fix now | Ingrid | Key leak. Fix CI. 11 docs pages link here. |
| auth-quickstart | 🔴 Keep, fix | Ingrid | Page two of onboarding. Fix before v3. |
| webhooks-node | 🔴 Keep, fix | Ingrid | Top ticket topic. |
| checkout-python, -java, -go | 🟢 Keep | Tomasz | Tier-1. |
| payouts-node | 🟢 Keep | Ingrid | Tier-1. |
| payouts-python | 🟢 Keep | Tomasz | Tier-1. |
| deploy-starter | 🟢 Keep | DevRel | Named exception, not an SDK language. |
| checkout-elixir | Hand off | You, then Marek | See below. |
| checkout-dotnet | ⚠️ Dana-gated | DevRel | See below. |
| subscriptions-ruby | Archive | none | No SDK, no owner. |
| api-v1-samples | Archive | none | See assumption below. |
| hackathon-demo-2025 | Archive | none | No owner. |
| marketplace-reference-app | Archive | none | Needs a Dana nudge for the slide. |

That is 9 kept, 4 archived, 2 pending.

**Assumption on `api-v1-samples`:** I read "sunset in January" as January 2026, which has already passed. If it means January 2027, keep the repo until then and link it to the v3 migration guide.

## Reasoning on the hard calls

- **Archiving keeps links working.** An archived repo stays public and readable. The 11 docs pages and the sales slide keep resolving. Edit the README banner first, because archived repos are read-only. You can unarchive later.
- **Elixir:** a community dev would maintain a payments sample under your brand. Customers copy that code into payment flows. I recommend transferring the repo to Marek and labelling it "community-maintained" in the docs. Do not give him write access to your org. Ask him first.
- **.NET:** Dana's veto is likely satisfied by archive plus a banner, because the repo stays visible. But it has been red for 5 months and was shown to prospects, so ask her what they actually need. Timebox a fix at 6 hours:
  - If it goes green, keep it as best-effort, not tier-1.
  - If not, offer Dana archive plus banner.
  - Two prospects is a demand signal, not a tier-1 decision. Defer it to the first quarterly review.
- **Webhooks:** 14 tickets shows the topic is hard, not that the repo is the cause. Fix it anyway. Record the ticket count per quarter as the baseline.
- **Single-scenario repos** (`webhooks-node`, `payouts-*`): do not consolidate them before v3. Moving them breaks links. Revisit in the second quarter.
- **GitHub traffic** only keeps 14 days of data and measures views, not usage. Do not decide on it this round. Snapshot it weekly from now on. Optionally tag sandbox requests per repo with a `User-Agent` such as `brackenpay-sample/<repo>`.
- **Green on today's API is not green on v3.** Reserve time to re-run every kept sample against v3 before launch.

## One-off budget: 60h

| Item | Hours |
|---|---|
| Key revoke, secret scan of all 15 repos, org push protection, `checkout-node` CI fix, short note to the customer | 6 |
| `auth-quickstart` fix | 8 |
| `webhooks-node` fix | 6 |
| `checkout-dotnet` timebox | 6 |
| 4 archives (banner, link check, archive, fix the slide link) | 3 |
| Elixir transfer | 1 |
| Quarterly process setup (owners, tiers, scheduled CI) | 6 |
| v3 re-run on the 9 kept repos | 12 |
| Buffer | 12 |
| **Total** | **60** |

Run the secret scan **before** archiving anything. Archived repos stay public, and `deploy-starter` clones into customer accounts.

## Quarterly: 40h

- **Ingrid:** 4 Node repos, 12h.
- **Tomasz:** Python, Java, Go, payouts-python, 12h.
- **DevRel:** `deploy-starter` 2h, `.NET` 4h if kept, review and report 4h. That is 10h.
- **Reserve for red triage:** 6h.

Rules:

1. Every repo has a named owner and a tier in its README.
2. A scheduled CI runs weekly against the sandbox with test keys. Red for 2 weeks notifies the owner. Red for 30 days makes it an archive candidate.
3. Tier-1 language means keep by default. Anything else needs a named exception with an owner and an expiry date.
4. Snapshot traffic weekly.
5. One 2h review per quarter. You get archive proposals, and Dana has a 5-business-day veto window.

## Timeline (decision around 2026-12-04)

1. **Week 1:** key revoked, secret scan done, owners confirmed, archive list sent to Dana.
2. **Week 2:** `.NET` timebox, Marek answer, `auth-quickstart` fixed.
3. **Week 3:** `webhooks-node` fixed, `checkout-node` CI green, Dana's veto window closes.
4. **Week 4:** archives executed, v3 re-run.
5. **Week 5:** buffer and your sign-off.

## Questions for you

1. Whose key is it, and is it already revoked?
2. Does "sunset in January" mean 2026 or 2027?
3. Can Ingrid and Tomasz work in those languages and take those splits?
4. Is v3 breaking for the checkout, payouts and webhooks samples?

**Next (2 minutes):** open the `bp_live_` key in the dashboard and check its status.