# Customer communication: Webhook replay API delay

## Your plan needs changes first

Steps 1, 3 and 4 will hurt you more than the delay does.

- **Step 1 (remove the issue):** Removing it hides the slip, and people will notice. The issue's subscribers and commenters will see it vanish, and a roadmap that deletes slipped items teaches 3,000 integrators not to trust it. Keep the issue, move it, and explain the move in a comment.
- **Step 3 (status page as "scheduled change"):** A status page is for incidents and maintenance. A roadmap slip there looks like an outage notice, triggers subscriber alerts, and sets a precedent you won't want. It also doesn't make anything "official". A dated, owned comment on the roadmap item does.
- **Step 4 ("Coming Q1!"):** Engineering said "Q1 at the earliest" while the queue is being redesigned. A celebratory "Coming Q1!" turns a floor into a promise. You would be doing this to the same audience you just slipped once.
- **Missing step:** Tell the two enterprise customers directly, before anything public. The renewal customer must hear this from you and not from a board change, a newsletter, or a colleague. Their order form has the words "webhook replay" in it, so loop in the account owner and whoever handles contracts. They may need an amendment, a credit, or an interim commitment.

Revised order:

1. **Today:** Internal alignment (draft D below).
2. **Within 48 hours:** Direct emails or calls to the two enterprise customers (drafts A and B).
3. **After those land:** Move the board item and post the comment (draft C).
4. **Next newsletter:** Short, factual note (draft E).

## Before you send, fill in or decide

- **Interim workaround:** Is there something customers can use today? Examples are manual redelivery from the dashboard or fetching the event log and re-sending. The drafts have a slot for it. If there's nothing, delete that sentence.
- **Next-update date:** Pick a real date, for example the end of November. Don't send without one.
- **What the customer gets:** The renewal customer will ask for something. Decide with the account owner before the call: a credit, an early-access slot, or a contract amendment. Don't let me or the email invent this.
- **Placeholders:** Everything in `[brackets]` is yours to fill in.

## A. Email to the renewal customer (send first, ideally followed by a call)

**Subject:** Webhook replay: timing change, and what we propose

Hi [Name],

I'm writing before our renewal conversation because I want you to hear this from us directly.

Webhook replay was planned for this quarter. It will not ship this quarter, and our earliest realistic window is Q1 [year]. I can't give you a firmer date yet, and I'd rather say that than guess.

The reason is that in load testing, replay traffic slowed down live webhook delivery. We won't ship a feature that puts your live events at risk, so engineering is redesigning the delivery queue first. That work is underway.

What this means for you:

- **Today:** [Interim workaround, e.g. "you can re-send individual events from the dashboard, and fetch failed deliveries via the events endpoint"]. If it doesn't cover your use case, tell me what's missing and I'll find out what we can do.
- **Next update:** You'll hear from me by [date] with a progress report, and then at each milestone after that.
- **The order form:** I know webhook replay is named in your agreement. I'd like to talk through how to handle that as part of the renewal, and I'll bring [proposal, to be agreed internally] to that conversation.

Could we find 30 minutes this week? I'd like your questions before anything is final.

[Name, role]

## B. Email to the second enterprise customer

**Subject:** Webhook replay: timing update

Hi [Name],

A heads-up on webhook replay, which is named in your agreement.

It will not ship this quarter. The earliest we expect it is Q1 [year]. Replay slowed down live delivery in load testing, so we're redesigning the delivery queue before releasing it. We won't trade the reliability of your live webhooks for an earlier date.

- **Today:** [Interim workaround, or delete this line].
- **Next update:** By [date].
- **Your agreement:** I'd like to talk about how this affects your terms. [Account owner] will reach out to schedule that.

If replay timing matters for a specific project of yours, tell me the date and I'll tell you honestly whether we can help.

[Name, role]

## C. Public comment on the roadmap issue (post, then move the item)

Move the item out of "Q3" to a "Later / Planned" column, or label it `target: Q1 earliest`. Don't call it "Coming Q1".

> **Update ([date]): Webhook replay API is moving from Q3.**
>
> This will not ship in Q3. Our earliest target is now Q1 [year], and that is a floor, not a commitment.
>
> Why: in load testing, replay traffic competed with live webhook delivery and slowed it down. We're redesigning the delivery queue so replay can't affect live events, and we'd rather ship it late than ship it unsafe.
>
> What you can do today: [interim workaround, or "no workaround yet; see below"].
>
> What's next: we'll post an update here by [date], and again when the queue redesign reaches [milestone].
>
> If you depend on replay, add a comment describing your use case (what you replay, how often, how many events). It directly shapes what we build first. We know this was on the Q3 column since spring, and we're sorry about the missed expectation.

## D. Internal note for sales, support and CS (before anything goes out)

> Webhook replay will not ship in Q3. Earliest is Q1 [year], not committed.
> Cause: replay starved live delivery in load tests; queue redesign comes first.
> Say: "earliest Q1, next update [date]". Don't say: "Q1", "soon", or "a few months".
> Two enterprise accounts have it in their order forms. Account owners contact them before the board changes. Do not discuss those accounts or their terms in public channels.
> Questions go to [owner]. Don't promise credits, dates or workarounds beyond this note.

## E. Newsletter item (a few sentences, no spin)

> **Roadmap update: webhook replay**
> Webhook replay is moving from Q3 to Q1 [year] at the earliest. During load testing, replay slowed down live delivery, so we're redesigning our queue first. [Interim workaround, one sentence.] Details and our next update date are on the roadmap issue: [link]. If you rely on replay, tell us how you'd use it in the issue comments.

## Two things worth knowing

- **Comments will rise at first**, then fall. People comment when a date moves without an explanation, and they stop once there's a dated answer and a next-update date. Hiding the item is what prolongs the comments.
- **Keep the promise you make in C and E.** The next-update date matters more than the Q1 target. If you post nothing by that date, you will have repeated the original problem.

Want me to tighten any of these for a specific tone, for example shorter for the second customer, or an agenda for the renewal call?