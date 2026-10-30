**Verdict: split the plan. The revocation is defensible as security hygiene, but it won't do what you want for the v1 sunset. Keeping v1 as the default for new keys undermines the sunset.**

## Problems

1. **New keys default to v1, so the residue refills.**
   - Every new key adds to the v1 tail. You'd clean the dashboard this week and watch it regrow.
   - "Backward compat" doesn't apply to a brand-new key, because a new customer has no v1 client to protect.
   - Fix: default new keys to v2 now. Anyone who really needs v1 can opt in explicitly, and you can log those opt-ins.

2. **Dormant keys aren't v1 traffic.**
   - A key unused for 60+ days sends no requests. Revoking it removes zero live v1 load.
   - If the dashboard counts keys, it will look cleaner, but the real v1 traffic stays the same. That makes it a cosmetic win.
   - The actual residue is the active keys still calling v1. Those are the ones to chase.

3. **60 days of silence doesn't mean abandoned.**
   - Quarterly and annual jobs, disaster-recovery failover paths, seasonal batches, and CI for rarely released software all go quiet that long.
   - Revoking gives them a hard 401, and customers find out at the worst moment.
   - Your support and churn cost may exceed the security gain.

4. **The sunset date is unclear.** If Feb 28 has already passed, v1 should be off and traffic still flowing is a separate issue. If it's Feb 28, 2027, you have about four months and should use brownouts. Which is it?

## Recommended plan

1. **This week:**
   - Switch the new-key default to v2.
   - Change the dashboard metric to v1 requests and distinct active customers on v1, not key count.
2. **Dormant keys:**
   - Tier them by last use: never used, 180+ days, then 60–180 days.
   - Notify key owners and give 14–30 days' notice.
   - **Suspend** the keys, which is reversible, before deleting them. Keep a restore path for 30–60 days.
   - Start with a canary slice (about 10%) and watch for 401 spikes and support tickets.
   - Handle enterprise and multi-key accounts through their account managers.
3. **Real v1 residue:**
   - Rank active v1 callers by volume and customer.
   - Contact the top ones directly with a migration guide.
   - Run scheduled brownouts before the final cutoff.
4. **Reporting:** tell stakeholders the revocation is a security cleanup, and report the sunset on v1 request volume. A dashboard that looks clean after the revocation would overstate migration progress.

## Questions for you

- Does the sunset dashboard count keys or requests?
- Is Feb 28 past or upcoming?
- Is there a concrete reason new keys default to v1, such as an SDK or docs pinned to it?
- Has Security assessed these 1,400 keys as a risk, such as leaked or over-privileged ones? If so, that group can be revoked first and faster.