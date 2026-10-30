**Short answer: probably not, though his reasons aren't the real ones.** The deciding factor is a Slack API rule he hasn't mentioned. I'm recalling it from memory, so verify it against Slack's current docs before you act.

## The decisive issue: rate limits on unlisted apps

- In 2025 Slack changed its API terms. Commercially distributed apps that aren't in the Marketplace get a tight limit on `conversations.history` and `conversations.replies`. As I remember it, that is about 1 request per minute and 15 messages per request.
- It applied to new installs from late May 2025. Existing installs were pushed to early 2026.
- Your 40 workspaces all installed after June 2025, so they probably fall under it from day one.
- Threadkeeper depends on reading threads, especially backfilling history. That is the call this limit hits hardest.
- Real-time capture through the Events API is likely unaffected. A new customer's history import may be crawling, or may be capped.
- **Check today:** how long does a backfill take for a mid-size workspace? If customers see "indexing…" for days, this is already costing you conversions and churn.

## Where he's partly right

- Review takes effort. You'll go through Slack's security and functionality review, supply a privacy policy, support contact and docs, and keep meeting the requirements afterwards.
- Reviews and analytics are weak or absent, as he says. Verify what the Marketplace dashboard gives you, but don't expect much.
- Your own funnel analytics on your site are better anyway.

## What he's missing

- **Rate limits:** the Marketplace is the way out of the throttling. Verify the exemption terms for your case.
- **Admin trust:** many IT admins only approve Marketplace apps. A tool that reads every message needs that trust more than most. Unlisted apps hit "ask your admin" walls, and those stall larger deals.
- **Discovery:** Slack search and category pages are free inbound. It's a small channel, but it costs nothing per lead.
- **Platform risk:** unlisted commercial apps are the class Slack is tightening on. Staying there is a bet that the rules won't tighten further.

## Recommendation

1. Today, measure backfill time and failure rate on your most recent installs.
2. If throttling is hurting you, apply to the Marketplace. The "hassle" is cheaper than the throttling.
3. If backfill is fine, because customers mainly want forward-looking capture, the urgency drops. Still apply: it's a one-time cost with a lasting trust benefit.
4. Keep your own site's Add to Slack button either way. Listing doesn't remove it.

## What would change my mind

- Slack's current docs say your usage is exempt from the limits.
- Your deals close with no friction from admins.
- The review demands scope or data-handling changes you can't make, such as storing less message content than your product needs. Check the review requirements before you commit.