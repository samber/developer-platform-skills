**Diagnosis: the dashboard has the wrong reader.** More promotion won't fix that.

Next action: pull the number of the 6,000 customer admins who opened the log in the last 30 days. If it is under about 5%, the diagnosis below holds.

## What the facts say

- The log is a pull tool. It helps only if someone opens it.
- The people who can open it are customer admins. They are not the people who can fix the app.
- The people who can fix the app are the 22 ISVs. They can't see the log, because it is scoped to one customer's account.
- When an app breaks, the customer sees a broken feature in the ISV's UI. They write to the ISV, not to Tuliphase.
- The ISV learns of the break from the support queue. That is the pattern you describe.
- The ISV may be outside the log's reach even if it gets access. It only records calls that reached Tuliphase, and many breaks happen before that.

## Why promotion fails

1. **Wrong audience for the ISV.** Promoting to ISVs tells them about a tool they can't use on their installs.
2. **Wrong moment for the admin.** An admin won't dig through a 30-day searchable log of someone else's integration. They report the symptom to the vendor. Promotion won't change that.
3. **Wrong shape for the job.** Detecting a break across 6,000 installs needs aggregate error rates and alerts. A per-customer search UI gives neither.
4. **Wrong privacy position.** The log shows bodies, and the customer owns that data. You can't just open it to the ISV, so the ISV has no route in without the customer.

## What would fix it

Ranked by effort, lowest first:

1. **Push failure alerts to ISVs.** Send a webhook or email per app when its error rate crosses a threshold on any install. Send metadata only: status codes, endpoints, counts, install ID. Send no bodies.
2. **Add a partner-level view.** Show each ISV error rate, latency and 4xx/5xx by endpoint across its own installs. Add a drill-down by install.
3. **Add "Share with vendor" in the customer dashboard.** One click gives the ISV time-boxed access to a specific log slice, bodies included. The customer controls it. The admin's report to the vendor then carries the evidence.
4. **Show app health in the customer UI.** A red badge on a failing integration lets admins see a break before the support ticket exists. It also gives them something to forward to the ISV.
5. **Keep a modest promotion.** Mention the dashboard in ISV docs and onboarding as a debugging tool, once items 1 to 3 exist.

## What I don't know

- I haven't seen usage data, so the "admins don't open it" claim is inferred, not measured.
- I don't know whether ISVs have any Tuliphase-side signal today, such as an API-key-level metrics page or 4xx emails.
- I don't know how many breaks occur inside the ISV and never reach your API. Those would stay invisible even after the fixes above.

## Checks, about an hour in total

1. Count admins who opened the log in 30 days, against the 6,000.
2. Take the last 5 breaks and check the call logs. See whether Tuliphase saw errors before the customer complained.
3. Ask 3 ISVs what they would want at 2 a.m. when an install fails.

If check 2 shows Tuliphase saw the errors early in most cases, items 1 and 2 above fix it directly. If it shows no errors in the logs, the breaks are on the ISV side and need an ISV-facing health signal. A Tuliphase alert will not catch them.

Tell your head of partnerships this: the dashboard is good, but it is aimed at the customer and the ISV needs the signal. The fix is to send the signal to the ISV.