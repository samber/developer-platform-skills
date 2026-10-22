# Recommendation: open listing, gated access

Don't launch fully open and add badges later. Separate two decisions your head of ecosystem has bundled together:

- **Who can list** an app: open, after a completeness check. She's right about this.
- **What data an app can touch**: tiered, with write access gated from day one. This is where the open-first plan breaks.

The gate sits on data scopes, not on the shelf. That should still get you most of the 50 apps.

## Why not "open now, badge later"

1. **The risk is different from a typical marketplace.** A bad app on a content marketplace is spam. A bad app here has write access to your customers' contacts, deals and job files. One bulk overwrite or one leaked token is a customer-data incident, and your name is on the marketplace. You can't take that back with post-publication moderation.
2. **Badges can't be retrofitted onto installs that already exist.** Once 50 apps hold write scopes at customers, the badge can only decorate them. Adding a requirement later means breaking live integrations or grandfathering the riskiest ones. A badge works as a trust signal only if the baseline was already enforced.
3. **Security is a buying criterion for your best accounts.** Your top 20 accounts raise app security in every renewal. If their admins can't answer "what can these apps do to our data, and who vetted them?" at launch, the marketplace becomes a renewal risk instead of a retention feature.
4. **The open playbook assumes a lower-stakes ecosystem.** The standard rule is to curate when brand or security risk is high and open up when it's low. It also says to control quality through discovery and trust signals, not submission gates. That works when a bad listing costs a bad impression. Here a bad listing costs customer data, so the "remove after publication" step is too late.

## What to ship in 11 weeks

**Three trust levels, tied to scopes, not just badges.**

| Level | How an app gets it | What it can do |
|---|---|---|
| **Listed** | Completeness check plus automated checks: HTTPS, signed webhooks, declared scopes and data use, privacy policy, security contact, verified business identity | Read-only, narrow scopes. Not shown in the default "recommended" ranking |
| **Verified** | Listed, plus a security questionnaire, DPA signed, automated scan of the OAuth flow, and a named responder for incidents | Write access and broader reads, with admin approval at install |
| **Certified** (the badge program) | Verified, plus independent evidence such as SOC 2 or a pen-test summary and a re-review every year | Everything. Becomes the enterprise tier |

**Platform controls that need no human review and protect you regardless of tier:**
- Granular per-object OAuth scopes, with a clear permission screen at install.
- Workspace-admin approval for any write scope, and an admin allow-list or block-list.
- An audit log of every app action on records, visible to the customer.
- Per-app rate limits, instant token revocation, and a platform kill switch.
- A sandbox with fake data, so developers build without touching real records.
- A written delisting policy and an incident-disclosure SLA.

**The enterprise tier is the same ladder, not a separate project.** Offer an account-level setting: "only Certified apps may be installed." That gives your top 20 accounts a direct answer in renewals. Ask 3 to 5 of them now what evidence they'd need. Their answers become the Certified requirements, and they become launch design partners.

## The 50-app number

- Count live installs and active apps, not listings. 50 dead listings look worse than 20 apps people use.
- Most apps in a construction CRM probably need modest access: reading contacts or deals for accounting, scheduling, estimating or e-signature. Many fit under Listed, and your launch partners can go through Verified before day one.
- I'd expect Listed plus a few Verified launch partners to reach 30 to 50 listings. That figure is my estimate, not data. Check it against your actual pipeline of interested developers.
- Pre-seed the marketplace with first-party and partner apps so launch day isn't empty.

## What would change my answer

- **Your API has no granular scopes today.** Building them is then your critical path, and 11 weeks may be too short. Fallback: launch with read-only access for everyone except hand-picked, reviewed launch partners, and open write access once scopes ship. That still beats open write access.
- **Your customers are mostly small contractors who never ask about security.** Then lean lighter on Verified. But your top 20 accounts say otherwise, so I'd design for them.
- **The 12-versus-50 gap holds up under a gate that only touches write scope.** Then her main objection mostly goes away. Test this before arguing it: list the apps you expect at launch and mark how many need write access.

## Questions that would sharpen this

1. Does the API support per-object scopes and admin-level install approval today?
2. How many of the expected launch apps need write access, versus read-only?
3. Who owns an incident when a third-party app corrupts customer data: your contract, your support team, or the developer?

The third question is a legal and contract question, and the answer decides how strict Verified needs to be.