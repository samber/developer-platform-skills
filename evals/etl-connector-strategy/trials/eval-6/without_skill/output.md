# Sablefin marketplace listing: wording and Partner Certified badge cost

## Summary

- ❌ **Don't publish "Certified connector, supported by the platform."** A merged PR and a marketplace listing show the connector passed review and is live. They don't show that the platform certified it or supports it.
- ⚠️ **I can't give you a cost for the Partner Certified badge.** I don't have the platform's partner-program terms, and you didn't name the platform. Any figure I gave would be invented. Below is the email that gets the real answer this week.

## 1. Why the claim is risky

| Phrase | What you can prove today | Gap |
|---|---|---|
| "Certified" | The PR was merged and the listing is live. | Certification is usually a separate program with its own criteria and badge. Your CTO is asking about that badge, which suggests you don't have it yet. |
| "Supported by the platform" | Nothing, unless a written agreement says so. | Marketplace connectors are normally supported by the publisher, which is Sablefin. Customers who believe the platform will fix their reconciliation problems will escalate to the wrong party. |

The questionnaire boilerplate carries the most risk. Buyers read security questionnaires as attestations, and they are often incorporated into the contract. A wrong statement there can be treated as misrepresentation, and a bank or enterprise procurement team will remember it. Fix this one first.

The platform may also restrict how its name and badges can be used. Check the partner brand guidelines before publishing anything that uses its name.

## 2. Copy you can publish now

**Integrations page**

> **Now available in the [Platform] Marketplace.** Sablefin's reconciliation connector is listed in the [Platform] Marketplace. Install it from the marketplace and start matching payments to your ledger. Supported by Sablefin: [support contact / SLA link].

**Security questionnaire boilerplate**

> Sablefin's connector for [Platform] is published in the [Platform] Marketplace (live since 2026-10-06) following the platform's connector review process. The connector is developed, maintained, and supported by Sablefin. [Platform] does not provide support for this connector. *(Edit if the partner agreement says otherwise.)*

Before you reuse the boilerplate, confirm with security or legal that "following the platform's connector review process" matches what the review covered. If it was a code review only, say "code review" and not "security review."

## 3. When you can upgrade the claim

Use "Certified" only when all of these are true:

1. The platform has awarded the Partner Certified badge to Sablefin, or to this connector, in writing.
2. You have read the certification's scope. It may cover the connector, the company, or a specific version.
3. The platform's brand guidelines permit the wording and the badge artwork.

Use "supported by the platform" only if a written agreement or support SLA says the platform supports the connector. Otherwise leave it out.

## 4. Answer for the CTO

> "I don't know the badge cost yet. We have a live marketplace listing, but not the certification. I'm asking the platform's partner team this week for price, requirements, and timeline. I'll report back by [date]. If the timeline fits March, we plan the announcement around it. If not, the conference story is 'live in the marketplace', which is true today."

Open questions the platform has to answer:

- **Fees:** Is there an application fee, annual fee, or revenue share, and what is each amount?
- **Requirements:** Is a security assessment, pen test, or SOC 2 report needed? Third-party audits are often the largest cost, and they sit outside the platform's fee.
- **Timeline:** How long from application to badge, and how long does a re-review take?
- **Scope:** Does the badge cover the company, the connector, or a specific version? Is it lost if we ship a major version?
- **Prerequisites:** How many live customers or installs are needed, and for how long?
- **Marketing rights:** What are we allowed to say, and where can we use the badge?
- **Support:** Does certification create any platform-side support, or is support always the publisher's?

**Draft email to the partner manager**

> Subject: Partner Certified program: requirements, cost, and timeline
>
> Hi [name],
>
> Thanks for getting our reconciliation connector live in the Marketplace on Tuesday. We'd like to pursue the Partner Certified badge and aim to have it before our user conference in March.
>
> Could you share: (1) program fees, (2) certification requirements including any security or compliance evidence, (3) the typical timeline from application to award, (4) the scope of the badge, and (5) brand and usage guidelines for the listing and the conference?
>
> Also, can you confirm that support for the connector remains with Sablefin, so we word our materials accurately?
>
> Thanks,
> [name], Sablefin

## 5. Planning against March

It is 2026-10-08, so you have about five months. That is enough for a review that takes weeks. It is tight if the program requires a third-party security audit, because audit scheduling alone can take months.

- **Set a decision date.** If you have no written timeline by about mid-November, plan the conference around "live in the marketplace".
- **Don't announce the badge in conference materials until it's awarded.** Printed or stage claims about a certification that hasn't been awarded can't be taken back.

## Next steps

1. Pull "Certified" and "supported by the platform" from any draft or live copy, and swap in the Section 2 text.
2. Send the Section 4 email.
3. Give the CTO the Section 4 answer.

If you tell me which platform it is, I can look up its public partner-program page and check the actual criteria. Fees may still be quote-only.