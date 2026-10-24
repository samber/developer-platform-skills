# Structuring the payment-reconciliation beta

## Recommendation

Don't announce a public beta on the blog yet. A public beta needs a request/response shape you're willing to support, and you don't have one. Run a staged rollout instead:

1. Pick the design.
2. Give Orvantis private early access.
3. Open the public beta once the shape is frozen.
4. Ship GA.

Orvantis gets early access sooner this way, and you still get a launch moment.

## Why the current plan is risky

- **The shape is undecided.** Anyone who integrates during a public beta is a customer you'll later break or have to support on a frozen contract. With a $600k deal in the middle, that is expensive.
- **The blog post makes the shape a promise.** "Beta" lowers expectations only briefly. After that, people build on it.
- **The Orvantis deal doesn't need a public beta.** It needs early access, which a private allowlist gives them with less exposure.
- **Reconciliation touches bank transactions.** Sensitive financial data, open signup, and an unsettled design is a bad combination.
- **"The platform team as a group owns it" means no one owns it.** Nobody can end the three-way design debate.

## Timeline (10 weeks to GA)

| Weeks | Phase | Output |
|---|---|---|
| 0–1 | **Design decision** (time-boxed) | One shape chosen, written down |
| 1–5 | **Build** (engineering's ~4 weeks) | Working implementation |
| 3–5 | **Orvantis early access**, sandbox first | Their real scenarios tested |
| 5–7 | **Private alpha**: Orvantis plus 3–5 design partners | Feedback, shape frozen |
| 7–8 | **Public beta**: blog, open signup | Launch moment, feedback and metrics |
| 8–10 | **Soak and harden** | GA with exit criteria met |

Engineering's 4 weeks only holds if the design is settled first. Every week the debate runs past week 1 pushes GA back one week.

## 1. Choose the design (week 0–1)

- **Write one test pack** that all three designs must handle:
  - Exact match.
  - Partial payment.
  - One payment covering several invoices.
  - Several payments covering one invoice.
  - Bank fees and FX differences.
  - Unmatched transactions.
  - Retries and idempotency.
- **Score each design** on four things: how well it handles the test pack, whether it can grow by adding fields only, how easy it is to explain in docs, and how hard it is to build in 4 weeks.
- **Show the finalists to Orvantis** and one other design partner. Their real data will settle what the whiteboard can't.
- **Let one named person decide** if there's no consensus at the end of the week.

## 2. Orvantis early access

- **Give them a private allowlist**, not a public announcement.
- **Start with a sandbox** using their data shape, and move to production data only after a security and DPA review.
- **Put the terms in writing:**
  - Beta status, with no SLA.
  - Change notice for breaking changes.
  - Their feedback shapes the design.
  - What happens to their integration at GA.
- **Keep Sales out of date and shape promises.** Delivery dates and API commitments come from the owner of this resource family.

## 3. Beta mechanics (private alpha and public beta)

- **Mark the API unstable in the surface itself**, for example a `v1beta` path or an opt-in header. Docs banners alone aren't enough.
- **State a breaking-change policy.** For example, 14 days' notice during beta, then a freeze for the final 2 weeks before GA.
- **Make the public beta sandbox-only** with synthetic or customer-uploaded data. Add rate limits and abuse controls.
- **Set up a feedback channel and a triage owner.** Without one, public beta feedback gets lost.
- **Write GA exit criteria before launch.** Examples: match rate on the test pack, error rate, open breaking-change requests at zero, and Orvantis sign-off.

## 4. The launch moment

- **Make the public beta the announcement.** The blog post says what's new, shows a working example, and states honestly what may still change.
- **Save a second beat for GA**, such as a changelog entry, customer story, or docs push.
- **Weeks 7–8 leave a short soak.** If beta feedback forces a breaking change, GA slips. Say that to leadership now.

## 5. `invoice.memo`: don't bundle it into the beta

- **Beta and memo have opposite risk profiles.** The beta is unstable and removable. A free-text field in a stable API is effectively permanent.
- **Bundling taints the field.** It would inherit the "may change" label, or it would get frozen early because it's riding along with the beta.
- **Ship it separately** as an additive optional field in the stable API with its own changelog entry.
- **Settle these before shipping:**
  - Maximum length.
  - Encoding.
  - Whether it appears in webhooks, PDFs, and search.
  - Whether it can hold personal data.
  - Whether reconciliation matching will ever read it. Customers often put invoice references in memos, so this coupling is likely. Decide it deliberately, and keep memo out of the matching contract until you have.

## 6. Ownership

- **Name one directly responsible owner** for the reconciliation resource family. They make the design call, own the timeline, and answer to leadership.
- **Name a beta owner**, who can be the same person, to run feedback triage and the breaking-change log.
- **The platform team does the work.** One person is accountable for the outcome.

## Risks to watch

| Risk | Mitigation |
|---|---|
| Design debate runs past week 1 | Time-box it and give one person the deciding vote |
| Beta feedback forces breaking changes late | Alpha with Orvantis and partners freezes the shape first |
| Orvantis expectations outrun the beta | Written terms, with Sales kept out of shape and date promises |
| Public sandbox abused or leaks real data | Synthetic data, rate limits, no live bank feeds in public beta |
| Memo ships with unresolved limits | Separate release with its checklist |
| GA slips because the soak is only 2–3 weeks | Written exit criteria, and tell leadership the soak is short |

## Decisions I need from you

1. Who is the single owner for the reconciliation family?
2. Is leadership willing to move the public announcement from now to about week 7?
3. Can the Orvantis contract be framed around private early access instead of a public beta?
4. Should memo ship now as its own stable change?