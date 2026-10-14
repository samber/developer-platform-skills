# Parcelwise app directory: description quality bar and rejection triggers

I read `app-marketplace-listing-standards/SKILL.md` and `references/marketplace-listing-benchmarks.md`. I skipped the interview because you asked for the deliverable directly. I assumed a live directory, self-serve installers, and vendor-maintained listings. If installs are actually decided by an admin doing diligence, tell me. That changes video length and tone, not the triggers below.

## Your four decisions

| Item | Verdict | Rule it fails or passes |
|---|---|---|
| Name "Parcelwise Label Printer" | ❌ Reject | Trademark naming order |
| Opener (a) "Our sync engine uses a persistent WebSocket channel…" | ❌ Reject | Outcome-first bar |
| Opener (b) "Know which shipments are stuck before your customers call you." | ✅ Accept | Outcome-first bar |
| Support surface is a PDF on Google Drive | ❌ Reject | Off-listing trust gates (landing page and support channel) |
| "A warehouse manager in Ohio… cut costs 40%" | ❌ Reject | Unattributed testimonial and unsubstantiated outcome claim |

**1. The name is not fine.** The accepted shape is "{App} for {Platform}". A name that leads with the platform's own name is rejected. Atlassian, Slack, and Zoom each enforce this independently.

- Rejected: "Parcelwise Label Printer".
- Accepted: "Label Printer for Parcelwise".
- If the vendor has its own brand, "AcmeLabels Label Printer for Parcelwise" passes the same test.
- Say this to the vendor as a rule, not a judgment call. Any submitter can check it before submitting.

**2. Accept (b), reject (a).** This is the same pair Shopify publishes.

- Shopify accepts: "Reports that show you sales data in real time."
- Shopify rejects: "Reports that use the latest push technology… with only 250ms of latency."
- Opener (a) leads with mechanism: WebSocket, sync engine, "sub-second latency". The buyer doesn't evaluate on those.
- Opener (b) leads with the result the shipping manager wants.
- The mechanism may appear lower in the body. It may not be the opener.
- Opener (b) still has to be true. If the app doesn't detect stuck shipments, it falls under Misrepresentation below.

**3. A Drive PDF fails two hard gates.**

- The landing page must be public, with no login. A PDF is explicitly not a landing page.
- A support channel needs a contact route that requires no new account signup. It also needs a stated response commitment. The Slack benchmark commits to 2 business days.
- A PDF is a document, not a channel.
- These gates apply however good the copy is.

**4. The testimonial fails on two counts.**

- "A warehouse manager in Ohio" is anonymous. Anonymous testimonials are a named trigger.
- "Cut costs 40%" is an outcome claim with no source or time period.
- The vendor can fix this by naming the person, role, and company (with permission) and stating the basis for the number. Otherwise they remove it.
- The skill's trigger text covers unsubstantiated outcome guarantees. Applying it to a stated percentage is my reading of it. It's a one-line change if you want it narrower.

## Description quality bar

1. **Lead with the customer outcome.** The opener states what the shipper gets, not how the app works.
2. **Tie each feature claim to a measurable result.** Use a number or an observable change. "Know which shipments are stuck" is acceptable as a hook. A body feature like "faster reconciliation" needs a stated result.
3. **Be integration-specific.** Describe what the app does inside Parcelwise, not generic product marketing.
4. **Describe what the app actually does.** The description has to match the app's behavior.
5. **Disclose dependencies.** Name any third-party account the app needs, and say what it costs.

I have not set the numeric caps on name, hook, and body. They belong to the field-spec section, which I'd draft with you next.

## Rejection triggers

Each one is written so the vendor can fail it before they submit.

| # | Trigger | Self-check test |
|---|---|---|
| 1 | **Trademark naming order** | The name starts with "Parcelwise". Fix it to "{App} for Parcelwise". |
| 2 | **Mechanism-first opener** | The first sentence describes technology (protocol, engine, latency) instead of a buyer result. |
| 3 | **Keyword spam** | Any term appears more than 5 times. Also rejected: lists of carriers, brands, or regions with no added value. |
| 4 | **Anonymous or unattributed testimonial** | The quote lacks a real name, role, and company, or lacks permission. |
| 5 | **Unsubstantiated outcome claim** | A stated percentage, saving, or guarantee has no source and time period. |
| 6 | **Misrepresentation** | The description claims behavior the app doesn't have. |
| 7 | **Undisclosed third-party dependency** | A required outside account or its cost is not stated in the listing. |
| 8 | **No public landing page** | The link needs a login, or points to a PDF, document, or code repository. |
| 9 | **No qualifying support channel** | No contact route without account signup, or no stated response time. |
| 10 | **Missing or thin privacy policy** | The policy doesn't cover data collected, usage, retention, request process, and a real contact channel. A street address alone is insufficient. |
| 11 | **Out-of-date listing content** | The description no longer matches the app. |

- **Trigger 3:** the "more than 5 times" figure is borrowed from Chrome's policy. Treat it as your own number, not an industry standard.
- **Trigger 10:** the checklist is Slack's.
- **Trigger 11:** this is named as an explicit violation so reviewers can enforce staleness.

All these triggers are content gates. They fire whether or not the app is secure and functional. Safety review is a separate process and stays out of this rulebook.

## Before you publish

- Give already-listed apps a notice runway before any of these apply to them. Retroactive rules without notice burn partner trust.
- The benchmark pairs, the 5-repeat figure, and the privacy and support checklists all come from other operators' published policies. None is an industry constant. Say that in the rulebook so nobody cites them as one.
- Next section to draft is field-spec strictness. The default is named triggers like these plus numeric caps on name, hook, body, and media geometry only.