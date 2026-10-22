**Next action (15 min):** rewrite the req title and first paragraph (section 2), then pull the PlatformCon booth and Backstage Slack spend (section 3).

## 1. Diagnosis

The 31 applicants are not a bad pool. The req found the people you aimed it at.

- **Title:** "Senior Platform Engineer" means internal platform to most of the market: K8s operators, Argo CD, golden paths.
- **Channels:** PlatformCon and the Backstage Slack are the home of internal-platform engineers. You paid to reach them.
- **Role:** what you need is an **API product engineer**. They run a public API as a product, with versioning, deprecation, rate limits, SDKs, webhooks, metering, a developer portal and customer-facing SLAs. Internal-platform people have a different customer (their own colleagues) and different failure modes.

I have no market data on this pool. This is inferred from your description.

## 2. Change the req (this week)

1. **Retitle.** Use "Senior Engineer, API Platform" or "Senior Engineer, Developer API". Drop bare "Platform Engineer".
2. **Lead with the customer.** Open with "~400 customer dev teams integrate against our shipment-tracking API. You own that surface." Put the business-line goal in the first paragraph.
3. **List concrete work.**
   - Versioning and breaking-change policy
   - Webhook delivery guarantees
   - Rate limiting and usage metering
   - SDK generation
   - Developer portal and changelog
   - API reliability, including p99 and error budget
4. **Add real numbers.** Request volume, SDK languages, current version policy, on-call load.
5. **State the weak parts.** Examples: "the API is not yet a priced product" and "no dev portal yet". Candidates who want to build the business line will read that as a pitch. Internal-platform candidates will filter themselves out.
6. **Publish a salary band.** Senior candidates verify before they apply.
7. **Add a screening question.** Ask: "Describe an API external developers integrated against. What did you deprecate, and how?" This replaces the K8s-flavored screen. It filters the 31 and every future batch.

## 3. Where to fish

Rank by fit and cost, cheapest first.

1. **Your own customers' engineers.** Your 400 dev teams already integrate with the API. Add a "we're hiring" line to the API docs, the changelog, the SDK READMEs and the status page. These people know the product and know its pain. Zero cost, and probably your best channel.
2. **Referrals.** Ask your own engineers and your top customer integrators. Senior hires usually come through reputation and referrals, not postings. Set a bonus.
3. **Alumni of API-as-product companies.** They have shipped something customers integrate against. The adjacent set below is examples of where to look, not verified candidates or openings.
   - Payments and fintech APIs
   - Messaging and communications APIs
   - Shipping and logistics APIs (EasyPost, Shippo, project44, FourKites)
   - API infrastructure vendors (gateways, webhook delivery, API management)

   Source via LinkedIn search on titles like "API Platform", "Developer Experience", "Integrations Engineer".
4. **API-community venues.** Swap the PlatformCon money for these.
   - Events: APIdays, Nordic APIs, QCon API tracks
   - OpenAPI / AsyncAPI / webhook-standards communities
   - Maintainers of OpenAPI tooling and SDK generators
5. **Language-community maintainers.** People who maintain an HTTP client or SDK library have lived the customer-integration side.
6. **Deprioritize.** Job boards, generic sourcing, and the Backstage Slack. Keep the recruiter posting only if the new title routes it to different audiences.

## 4. Process changes

- **Interview loop:** replace the K8s/GitOps deep dive with an **API design review**. Candidates review a proposed change to your tracking API and decide whether it is backward compatible and how to roll it out.
- **Recruiter:** cancel the PlatformCon booth if it is still cancellable, and redirect that budget to section 3 items 2 and 4. Brief the recruiter with the new title and screening question.
- **Instrument:** track source-of-hire and offer-acceptance now. You can't tell which new channel works without it.

## 5. Decision rule

Run the new req 3–4 weeks.

- **Most applicants have shipped customer-facing APIs:** channels are right. Scale referrals.
- **Applicants still show the internal-platform pattern:** the title or JD still pulls it. Re-read the first paragraph.
- **Strong applicants but offers decline:** check comp band, role honesty and loop disorganization before spending more on top-of-funnel.

## 6. One scoping question

Do you need one person to both build the customer-facing product surface and run the gateway/reliability layer? If the work is really two jobs, split the req. "Platform" in the title was probably hiding that.

**Next:** paste your current JD's first paragraph and I'll rewrite it.