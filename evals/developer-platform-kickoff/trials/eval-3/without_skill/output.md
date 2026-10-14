# Nimbus Rota Marketplace: Review Criteria (Draft v0.1)

## Before you circulate this

1. **Count demand.** Your evidence is two unprompted partner asks. Before June, list the last five integrations customers requested that you didn't build, with the customer names. Nine of your 11 integrations are self-built, so you have no proof yet that outsiders will build. Partners' own arithmetic, not your rulebook, decides that.
2. **Check the 15% cut.** At 900 customers, say 5% install a $50/month paid app. That's 45 installs and $27k/year gross, so Nimbus earns about $4k and the partner keeps about $23k. The cut barely moves your revenue, but it takes 15% of a partner's thin margin before there is any market. I recommend this term: **15% in the rulebook, 0% for the first 12 months after launch.** The CEO would need to approve that, so it's flagged in section 7.
3. **Keep the first version small.** Everything below describes "listed partner-built integrations": third parties connect through your API and you list them. It does not cover apps that run inside Nimbus Rota or run your code. That stays a later decision.

Numbers marked *(default)* are my proposals, not industry standards.

## 1. Eligibility

An app is eligible if it:

- Connects to Nimbus Rota only through the public API and webhooks. No scraping, no UI automation, no private endpoints.
- Solves a workflow for shift-scheduling customers. Examples: payroll, time clocks, HRIS, messaging, POS or demand forecasting.
- Comes from a legal entity that signs the Marketplace Partner Agreement and names a security contact and a support contact.
- Has at least one live customer on the production version. The exception is the founding cohort, which you hand-pick.

## 2. Submission package

Required items:

| Item | Requirement |
|---|---|
| App name and one-line description | Name is ≤30 characters and must not imply Nimbus ownership. Description is ≤120 characters and states the outcome. |
| Long description | 100–300 words: what it does, who it's for, what data it reads and writes. |
| Logo | Square PNG or SVG, 512×512 px minimum. |
| Screenshots | 4 to 6 images, specified below. |
| Setup guide | Public URL with steps from install to first working sync. |
| Support | Contact email and response-time commitment. |
| Privacy policy and terms | Public URLs. |
| Scopes declaration | Each API scope requested, with a one-sentence reason for each. |
| Test account | Credentials or a sandbox so a reviewer can run the whole flow. |
| Pricing | Free or paid. If paid, the full price and billing period. |

**Screenshots** (PNG, 1440×900 *(default)* or larger, 16:10, ≤5 MB each). Show these in order:

1. **Connect:** the install or authorize flow, with the permission screen visible.
2. **Configure:** the settings screen where the customer maps data (locations, roles, pay codes).
3. **In use:** the app working with real-looking data inside the Nimbus Rota workflow. For example, shifts syncing out or time-clock hours coming back.
4. **Result:** the outcome the customer cares about, such as a payroll export or a published schedule.
5. *(Optional)* Error or reconnect state.
6. *(Optional)* Disconnect or uninstall.

Screenshot rules:

- Use no real employee names, pay rates, or customer data. Use fictional data.
- No device mockups or marketing overlays.
- No pricing, competitor logos, or claims such as "#1" or "best".
- Show the current product UI. Out-of-date Nimbus Rota screens are rejected.
- Add alt text to each image.

## 3. Functional review

The reviewer runs the full flow with the test account. The app **passes** if:

- Install, authorize, first sync, and disconnect all work end to end.
- It handles API errors, rate limits (429), and expired tokens without data loss or duplicate shifts.
- A webhook retry or replay doesn't create duplicates (idempotent).
- Time zones, overnight shifts, and daylight-saving changes behave correctly. This is the most common scheduling bug.
- Disconnecting stops all access immediately.
- What the setup guide and listing say matches what the app does.

## 4. Security and data review

Schedules include employee names, availability, hours and often pay. Treat it as personal data.

- **Least privilege.** Request only the scopes the app uses. Unneeded write scopes are rejected.
- **Transport and storage.** TLS everywhere. Tokens are encrypted at rest and never logged.
- **Data use.** Customer data is used only to provide the app's function. It isn't sold, used for ads, or used to train models without explicit customer opt-in.
- **Deletion.** Customer data is deleted within 30 days *(default)* of disconnect or on request.
- **Incident notice.** The partner notifies Nimbus within 72 hours of a breach affecting Nimbus customer data.
- **Self-attestation.** Partners complete a short security questionnaire. Independent proof, such as SOC 2, isn't required in v1 but may be required for apps that request payroll or pay-rate scopes. That's an open decision (section 7).

## 5. Listing content review

- No misleading claims, fake reviews, or implied Nimbus endorsement.
- No competing scheduling product presented as an "integration". Apps that migrate customers off Nimbus Rota are rejected.
- Pricing on the listing matches pricing at checkout.
- The listing is in English. Add other languages only if the app supports them.

## 6. What gets rejected

**Reject immediately, no resubmission for 90 days *(default)*:**

- Uses private APIs, scraping, or credential sharing.
- Collects data beyond the declared scopes.
- Misrepresents the publisher, pricing, or Nimbus's endorsement.
- Fails the security review in a way that exposes customer data.

**Fixable, so returned with comments, and resubmission is unlimited:**

- Screenshots that don't meet section 2.
- A missing or broken setup guide.
- Scopes broader than needed.
- Time-zone, duplicate-shift, or error-handling bugs.
- Inaccurate or incomplete listing text.
- No working test account.

Every rejection must cite the specific criterion by section number.

## 7. Paid apps and the 15% cut

- Nimbus keeps **15% of net revenue**, meaning price after refunds and taxes, for apps billed through the marketplace.
- Paid apps bill through one channel. **Open decision:** whether Nimbus collects and pays out, or partners bill directly and report. Collecting makes the cut enforceable but adds payments, tax and refund work for you. Reporting is lighter but depends on partner honesty.
- Payout cadence is monthly, with a stated minimum threshold.
- Free apps pay nothing. Partners may not move customers to off-marketplace billing for the same app to avoid the cut.
- **Recommendation:** waive the 15% for the first 12 months after launch and announce that at the conference. This keeps partners' return positive while you build the pool.
- All commercial terms need a lawyer's review before publication.

## 8. Process and commitments

- First response within 10 business days *(default)*. **Owner needed:** someone must staff the review queue indefinitely. Name that person before June.
- One re-review included per rejection. Disputes go to a named escalation contact.
- After listing: re-review on any scope change, plus an annual check. Apps with no active installs for 12 months may be delisted.
- **Delisting notice:** 30 days, except for security or misrepresentation issues.
- **API stability:** breaking API changes get a minimum of 6 months' notice *(default)*. Every endpoint you document publicly is a promise, so list them deliberately.
- **Roadmap boundary:** publish which categories Nimbus plans to build itself, and commit to notice before you ship a competing feature.

## 9. Decisions to make before June

1. Who owns review and support, and how many hours a week can they commit?
2. Collect payments, or let partners bill and report?
3. Waive the 15% for year one, or charge from day one?
4. Require security proof (SOC 2 or equivalent) for payroll or pay-rate scopes?
5. Which 5 to 8 founding apps launch with the marketplace? Aim to cover your top customer requests, not logos. Your two inbound partners are the obvious start. Also decide which of your nine self-built integrations you hand over or keep.
6. What marketplace number would make you pause it? For example, fewer than N partner-built apps live or fewer than M installs by month 6. Write the number and date now.

I didn't draft the Partner Agreement or the API versioning policy. Both are separate documents and need legal review.