# Quillstream pre-GA features: publishable terms, with open items for Legal

I haven't touched your draft's legal effect, only its wording. Legal needs to confirm the three items in Part 2 before you publish.

## Part 1: Text to publish

### Pre-General-Availability Features: Terms

**Last updated:** [date]

These terms apply to any Quillstream feature, endpoint, or service labeled **Experimental**, **Beta**, or **Early Access** in our documentation (a "Pre-GA Feature"). They supplement your agreement with Quillstream (the "Agreement"). If these terms conflict with the Agreement on a point listed in section 3, these terms control for Pre-GA Features only. On every other point, the Agreement controls.

#### 1. Stages

| Label | What it means | Changes | Availability commitment |
|---|---|---|---|
| **Experimental** | Early idea, open to all users. May be removed at any time. | May change or be withdrawn without notice. | None. Not covered by the SLA. |
| **Beta** | Functionally complete but still evolving. Open to all users or to an opted-in group. | Breaking changes announced at least [30] days ahead, except where needed for security or legal compliance. | None. Not covered by the SLA. No service credits. |
| **Early Access** | Near-final, offered to selected customers. | Breaking changes announced at least [30] days ahead. | [Decision pending. See Part 2, item 4.] |

Each Pre-GA Feature's documentation page shows its label. A feature without a label is generally available and fully covered by the Agreement.

#### 2. What does not change

Pre-GA status affects availability and stability only. It does not change how we protect your data.

- The Agreement's confidentiality, security, and data protection terms apply.
- Our Data Processing Addendum ("DPA") applies to all personal data processed by a Pre-GA Feature. This includes personal data of your signers and other end users.
- Our sub-processor list and notification process apply to Pre-GA Features.
- We will not use personal data processed through a Pre-GA Feature to train models or for any purpose other than providing the feature to you.

#### 3. What differs

- **Service levels.** Pre-GA Features are excluded from the Service Level Agreement. Downtime or errors in a Pre-GA Feature do not earn service credits and do not count toward the uptime calculation for generally available services.
- **Reliability.** Pre-GA Features may have bugs, lower performance, or interruptions. We aim to run them carefully but make no uptime commitment, and any internal targets are goals, not promises.
- **Support.** Support for Pre-GA Features is best-effort, through [channel]. Support response targets in the Agreement do not apply.
- **Changes.** We may change, suspend, or discontinue a Pre-GA Feature as described in section 1. If we discontinue a Beta or Early Access feature, we will give at least [30] days' notice and let you export your data from it.
- **Production use.** You may use Beta and Early Access features in production at your own business risk, taking section 3's exclusions into account. Don't make a Pre-GA Feature the sole control for a legal or compliance obligation unless you've built a fallback.
- **Feedback.** Feedback you give us about a Pre-GA Feature is governed by the Agreement's feedback clause.

#### 4. Audit Trail (Beta)

Audit Trail returns, for each envelope, every signer's name, email address, IP address, and event timestamp. This is personal data.

- **Roles.** You are the controller (or processor on behalf of your customer). Quillstream is your processor under the DPA.
- **Your responsibilities.** Before enabling Audit Trail, make sure you have a lawful basis and any required notices for collecting signer IP addresses and exposing this data to your own systems and users.
- **Access.** Audit Trail is [off by default and enabled per account / available only to API keys with the `audit_trail:read` scope]. Treat responses as sensitive and don't log them in plaintext.
- **Retention.** We retain Audit Trail data for [period], and deletion requests under the DPA apply to it.
- **Service levels.** Audit Trail is not covered by the SLA while in Beta. It will be covered when it becomes generally available, unless we announce otherwise in the Agreement.

#### 5. Acceptance

You opt in to a Pre-GA Feature by [enabling it in the dashboard / calling its endpoint / signing the Early Access order form]. Continued use after a change to these terms means you accept them. Material changes to these terms will be announced at least [30] days ahead.

## Part 2: Decisions and risks for Legal and you

1. **The MSA conflict is the real blocker.**
   - Your enterprise MSA promises the SLA and the DPA on "all Quillstream services." Excluding Beta from the SLA on a docs page may not override that.
   - Legal should check whether the MSA has a carve-out for beta or preview features, or lets you change terms via the docs.
   - If it doesn't, you need an opt-in that counts as an amendment, such as a click-through or order-form addendum. The "Acceptance" section is built for this.
   - Don't launch Audit Trail until this is settled. Otherwise your original draft's "covered by the standard 99.9% SLA" is the only promise customers can point to.

2. **Don't publish the 99.5% SLO.** It makes a promise you can't back with credits, and customers will quote it back to you. It also sits below the 99.9% in the MSA, which invites confusion. If you want to give customers an expectation, say "no uptime commitment" and share the number privately under NDA, labeled non-binding. I removed it from the text.

3. **The DPA stays on, and your draft's other claims are cut.**
   - Audit Trail returns personal data of third parties (signers). Disclaiming the DPA for it would breach the MSA and likely your own data protection obligations.
   - I deleted "use at your own risk" because it's vague and can look like a liability disclaimer you can't enforce. Liability limits belong in the MSA.
   - I deleted "run on the same infrastructure." It isn't accurate if Audit Trail is its own service with its own SLO, and it implies a reliability level you don't promise.

4. **Early Access needs a decision.** I left its availability commitment open because I don't know your intent. If it means "near-GA, selected customers," a sensible default is the full SLA once the feature is stable, with Beta as the stage that is explicitly excluded.

5. **Labels: don't go to four.** Adding "Experimental" on top of Labs, Beta, and Early Access gives customers four stages with unclear differences. I recommend three: Experimental, Beta, Early Access, and retiring "Labs."

6. **Labs has no terms, so it's currently under the MSA.**
   - The two Labs endpoints, live since 2023 with no terms, are "Quillstream services" today. That means the SLA and DPA arguably already cover them.
   - Before relabeling them Experimental or Beta, check who uses them in production.
   - Give existing users at least [30] days' notice, or whatever the MSA's change clause requires, before the new terms apply. Otherwise you are removing a commitment without notice.
   - Alternative: promote them to GA, or sunset them.

7. **Bracketed items** (notice periods, retention period, access scope, support channel, acceptance mechanism) are my placeholders, not facts about your product. Fill them in with what engineering and Legal confirm.

I'm not a lawyer, and this is a drafting aid. Have Legal review it against the MSA before you publish.