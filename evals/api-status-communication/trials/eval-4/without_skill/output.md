**Post-ready status page update**

**Title:** Elevated API errors

**Status:** Investigating

**Body:**
> We are investigating elevated error rates on API requests. Some requests are failing, and the issue began at [HH:MM UTC].
>
> Retrying a failed request usually succeeds. If your integration has automatic retries with backoff, we recommend enabling them for now.
>
> Our engineering team is actively working on this. We are examining several possible causes, including an issue with our infrastructure provider's network, and have not yet confirmed a root cause.
>
> We will post our next update by [HH:MM UTC], or sooner if we learn more.

Fill in two placeholders before posting: the start time (use when errors first appeared, not when you noticed) and the next-update time (30 minutes out is typical, and keep it). If you can name the affected scope, add one line such as "Affecting all API endpoints" or "Affecting some requests across regions."

**What I changed and why**

- **Removed "Operation Redwing" and INC-CORK-77.** Customers can't use internal names, and they read as noise or as dramatic.
- **Softened the AWS claim.** You said it's unconfirmed. Publicly blaming a vendor on a guess is hard to walk back if it's your own bug, and a wrong guess costs credibility. "Possible causes, including our infrastructure provider's network" is true either way. You can name AWS explicitly once confirmed.
- **Dropped the Kubernetes and ingress detail.** Customers can't act on it. It also exposes internal architecture and implies you already know the cause.
- **Moved "retries usually succeed" up and made it actionable.** It's the most useful fact for customers right now, and it tells them what to do.
- **Replaced "will post more when we know more"** with a committed update time. That is what readers want from a status page.
- **Added a start time**, which customers use for their own incident timelines.

**Follow-up updates**

- **If AWS is confirmed:** "We have identified the cause as a networking issue at our infrastructure provider, AWS. We are working on mitigations and tracking their resolution."
- **If it's your own system:** "We have identified the cause as an issue in our request-routing layer and are deploying a fix."
- **On resolution:** state the end time, say that errors have stopped, and promise a post-incident summary.

If the errors are partial, say so. Don't use "major outage" wording unless most requests fail.