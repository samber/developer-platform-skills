## Ready to post

**Title:** Elevated error rates on the API
**Status:** Investigating
**Component:** API → state per breadth of impact (see the notes below)

> **[HH:MM] UTC** – Since approximately **[HH:MM] UTC**, some API requests are failing. Requests that succeed are processing normally, and retrying a failed request usually succeeds. If you retry, use exponential backoff with jitter so retries don't add load.
>
> We have not yet confirmed the cause and are actively investigating. We will post the next update by **[HH:MM] UTC**, even if we have nothing new to report.

If your monitoring can give a scope, add one sentence before "We have not yet confirmed". Use only measured figures, for example: "Roughly a third of API requests are affected." Also name the endpoints or regions that are healthy.

## What I changed and why

- **Dropped "Operation Redwing" and INC-CORK-77.** Public titles use plain language about the problem and never an internal codename or ticket ID. Keep both internally.
- **Removed the AWS theory.** You haven't confirmed it, and the skill's rule is to post only what is confirmed. If you blame AWS publicly and it turns out to be your own bug, you've lost credibility. If AWS really is the cause, you still shouldn't blame them in the post. Your customers' contract is with you. When you do confirm a cause, say something like "a networking issue in our cloud infrastructure".
- **Removed the k8s ingress and endpoint-churn detail.** Integrators can't act on it, and it's another unconfirmed guess. It belongs in the postmortem once you have verified it.
- **Replaced "Will post more when we know more" with a named next-update time.** Pick a time you can keep, such as 20–30 minutes out. Keep that promise even if the update says "still investigating, nothing new".
- **Added the retry workaround.** You said retries usually succeed, so it's the most useful thing in the post. "Usually" is hedged accurately in the draft. I added the backoff-with-jitter advice because naive retries during a partial failure can make the load worse.

## Before you hit publish

1. **Post now.** The incident is already 20 minutes old. This post is late, and the skill treats the gap between the alert firing and the page updating as the thing to drive down. Don't wait for the AWS theory to be confirmed.
2. **Set the component state by breadth, not by how bad it feels.** Retries mostly work and not everyone is affected, so this is probably **Partial Outage** if some requests or customers fail. Use **Degraded Performance** only if everyone is slow but nothing fails. Use **Major Outage** only if the API is unavailable for everyone.
3. **Leave dashboard, webhooks and docs green** unless they are actually affected.
4. **Send the same text to email, RSS, X and any other channel at the same time.**
5. **Next statuses:** move to *Identified* once the cause is confirmed (e.g., "We have identified the cause as …"). Then move to *Monitoring* when the fix is in, and *Resolved* with the impact window and affected share.
6. **Plan the follow-up.** Customers felt this, so promise a summary postmortem on the incident ("within 3 business days"). That is the default for any incident consumers noticed.

## Fill-ins I need from you

- **Start time of impact,** and whether it is still ongoing.
- **Scope:** share of requests failing, affected regions or endpoints, and which components are healthy.
- **Next-update time** you can commit to.

Send me those and I'll finalize the post. I can also draft the *Identified* update for the moment you confirm the cause.