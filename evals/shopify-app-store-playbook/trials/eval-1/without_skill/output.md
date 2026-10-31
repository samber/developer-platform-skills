# Go-to-market plan: Ticketly order-lookup app for Shopify

## Read this first: three things could break the 5-week date

I wrote this from memory and could not check Shopify's current rules. Verify the three items below before you commit to the booth date.

1. **App review time is outside your control.** Public listings go through automated checks and then a manual review. Rejections and resubmissions are common, and each cycle can take days to weeks. Plan as if the listing may not be live by the conference.
2. **Order lookup needs protected customer data.** A sidebar showing order, customer name and email needs "protected customer data" access. That means a data-protection declaration and review, and it can run in parallel with app review. Orders older than 60 days need separate `read_all_orders` approval. Ask for that only if you need it, and justify it in the submission.
3. **Billing outside Shopify.** Shopify's rule is that charges for the app must go through its Billing API. "Free app, existing Ticketly subscription billed on Stripe" is a common pattern and is probably allowed, but only if you handle it carefully:
   - List pricing as free to install.
   - State plainly that a Ticketly account is required, and where it's billed.
   - Never sell or upgrade features inside the app.
   - Don't let the app sell a Ticketly plan to merchants who have no account.

   The reviewer decides. Read the current App Store requirements on billing and external accounts, or ask Partner Support, in week 1. If they say no, the plan changes. You would need Billing API for any new-customer path or a different structure.

**Recommended fallback for the booth:** if review isn't done, demo from a development store and give attendees a direct install link. Check whether Shopify allows that for your distribution type. Distribution method (public vs custom) is set per app and, as far as I know, can't be changed later. Decide this in week 1 so you don't end up with two apps and a forced reinstall.

## 1. Goal and success metrics

**Primary goal:** turn existing Ticketly users on Shopify into app users, and use the listing as a new acquisition channel.

| Metric | Target at 30 days after conference | Why |
|---|---|---|
| Installs from existing customers (of ~300) | 90 (30%) | These are the people already asking for it |
| Install-to-connected rate | 70%+ | Connection to Ticketly is the real activation step |
| Weekly active agents using the sidebar | 50% of connected | Shows real use, not installs |
| New Ticketly trials from the listing | Measure only, no target yet | You have no baseline |
| Listing approved | Before the conference | Fallback above if not |

Set the new-trial target after two weeks of data. Any number now would be invented.

## 2. Audience and positioning

**Primary: the ~300 existing Shopify customers.** They asked for this. Message: "The order-lookup sidebar you asked for. Free, installs in minutes, works with your existing Ticketly account."

**Secondary: Shopify merchants with a small support team who don't yet use Ticketly.** The listing is the first thing they'll see. Message: "See the customer's orders next to every ticket. Needs a Ticketly account, $49/agent/month, billed by Ticketly."

State the paid dependency clearly in the listing. Hiding it risks rejection and refunds.

**Positioning line (draft):** "Order details beside every support ticket. No tab switching."

## 3. Listing assets (build in weeks 1-2)

- **App name and tagline:** "Ticketly Order Lookup", with a tagline under the character limit. Check the current limits and the naming rules (no "Shopify" in the name).
- **Icon, 3-5 screenshots, a 30-60 second demo video.** Screenshots show the sidebar inside a real ticket with fake data.
- **Description:** lead with the outcome, then 3 bullets (order status, refund and fulfilment info, link back to Shopify admin). Add one explicit line on the Ticketly account requirement.
- **Pricing section:** free to install, plus the disclosure of the external requirement.
- **Support:** a support email, a help page and a privacy policy URL.
- **Search keywords:** "helpdesk", "order lookup", "customer support", "ticketing". Search the App Store for these terms to see what you're up against.
- **Scopes:** request the minimum (`read_orders`, `read_customers`), and be able to explain each one.
- **Mandatory webhooks:** customer data request, customer erasure, shop erasure. Missing these is an automatic failure.

## 4. Timeline (5 weeks)

| Week | Work |
|---|---|
| 1 | Billing/distribution check with Shopify. Choose distribution. Draft scopes. Start the protected-data declaration. Name and brand check. |
| 2 | Build the OAuth connect flow and sidebar. Mandatory webhooks. Listing assets and copy. |
| 3 | Internal test on a dev store plus 5-10 friendly customers. Fix issues. **Submit for review by end of week 3.** |
| 4 | Respond to review feedback the same day. Prepare launch emails, in-app banner and booth material. |
| 5 | Listing live if approved. Email the 300 customers. Final booth prep. If not approved, switch to the fallback demo plan. |

Submitting at the end of week 3 leaves roughly two review cycles. Anything later is a gamble.

## 5. Launch plan

**Existing customers (300):**
1. Week 3: invite 10 friendly customers to a beta. Collect a quote and a screenshot, with permission.
2. Launch day: email with a one-click install link, plus an in-app banner for Shopify-connected accounts.
3. 7 days later: follow-up to non-installers, with a 2-minute video.
4. Support team mentions the app in every Shopify-related ticket.

**App Store:**
- Ask the beta users for reviews once they've used it for a week. Don't ask on day one. Don't offer incentives (against the rules, and it's bad practice anyway).
- Reply to every review.

**Conference booth:**
- Live demo on a dev store, with a QR code to the listing or the install link.
- One-line pitch on the signage, plus a "free for existing Ticketly customers" sticker.
- Lead capture: scan, then send the install link by email on the day.
- Track booth-sourced installs with a UTM-tagged link, separate from other channels.

**Other (lightweight):** a blog post, a changelog entry, a LinkedIn post and a short docs page. Skip paid ads until you have conversion data.

## 6. Measurement

- Funnel: listing views, installs, connected accounts, weekly active agents. Instrument the connect step yourself, since Shopify shows only listing views and installs.
- Tag the source: existing customer email, App Store organic, booth link.
- Review at 7, 30 and 90 days. Decide on paid promotion only after the 30-day read.

## 7. Risks and mitigations

| Risk | Mitigation |
|---|---|
| Review takes longer than 5 weeks | Submit by end of week 3. Booth fallback with dev-store demo and direct link. |
| Billing model challenged | Ask in week 1. Prepare a Billing API variant as plan B. |
| Protected-data access delayed | Start the declaration in week 1. |
| Users install but never connect | Short connect flow, an email trigger after 24 hours with no connection. |
| Free app attracts merchants who can't use it | Clear "Ticketly account required" copy in the first line of the description. |
| Support load spike after launch | Help page and a macro for the top 5 questions, written before launch. |

## 8. Decisions I need from you

1. Do you know whether Shopify has approved this billing structure, or should we ask in week 1?
2. Public listing only, or also a custom-distribution install link as a booth fallback?
3. Is a new-customer trial flow in scope for v1, or is this existing customers only at launch?
4. Who owns the review-response work in weeks 3-4? It needs same-day replies.