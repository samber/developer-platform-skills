# Publishable policy text

## App update policy

Every update to a listed app falls into one of three tiers. The tier depends on what the update changes, not on how large or important the change feels. Check the tier lists below. You do not need to judge whether a change is "substantial".

### Tier 1: Resubmit for full review

Resubmit before release if the update does any of the following:

1. **Permissions.** Adds or changes an OAuth scope, API permission, or access level.
2. **Data.** Reads, stores, or sends a new category of customer data, or sends data to a new third party, domain, or hosting region.
3. **Authentication.** Changes how the app authenticates users or connects to Meridian Stack.
4. **Write actions.** Adds an action that creates, edits, or deletes customer data, or extends an existing one to new data types.
5. **Automated or AI processing.** Adds automated or AI/ML processing of customer data, or changes the provider or model that does it.
6. **Money.** Adds or changes pricing, billing, or paid features, or the way the app charges customers.
7. **Identity.** Changes the app's name, category, or stated purpose, or transfers it to a different publisher or legal entity.
8. **Placement.** Adds a new place where the app appears in the Meridian Stack interface.

The following changes are not limited to the list above. We may also require full review of any change that we reasonably judge to alter the app's features, purpose, or functionality in a way customers did not agree to.

### Tier 2: Ship, then notify

For a new feature or behavior change that does not match any Tier 1 item, release it first. Then submit the update notice with a changelog within 2 business days of release. Meridian Stack may spot-check it. If a spot-check finds a Tier 1 change, the app is treated as having shipped an unreviewed update (see "Misclassification").

### Tier 3: No action

Bug fixes, performance improvements, security patches that do not change permissions or data flows, dependency updates, text and translation edits, and visual changes within existing screens.

### How to classify an update

1. Every update submission includes the Tier 1 checklist. Answer yes or no to each of the 8 items.
2. Any "yes" means full review. The submission form will not accept the release otherwise.
3. If you are unsure about an item, answer "yes". You can also ask us at partner-review@[domain]. We answer within 2 business days, and the answer is binding for that update.
4. We publish answers to common questions in the classification log, so the same question is not asked twice.

### Misclassification

- We compare each release against its previous version, including scopes, domains, and endpoints. Changes to permissions and data destinations are detected automatically.
- We also audit a random sample of Tier 2 and Tier 3 updates each month.
- An update that should have gone to full review but did not is a violation. First violation: the update is reverted until reviewed, and the publisher gets a written warning. Second violation within 12 months: listing suspended. Repeat or deliberate violations: delisting.
- Reporting a violation yourself before we find it counts in your favor.

### Disputes

The classification checklist decides the tier. If you disagree with a reviewer's classification, you can appeal once to the review lead, who responds within 2 business days. The update stays unreleased during the appeal, and the lead's decision is final.

---

# Notes for you (not for publication)

**Why this should cut the arguments.** The old line asks the developer to judge "substantial", which gives a partner an incentive to answer "no". The new text uses yes/no questions about facts: scopes, data destinations, pricing. Most of these can be checked automatically against a manifest diff, so the reviewer compares the form against the diff instead of debating intent.

**Your suspicion is testable.** Before publishing, pull the last 6 months of updates and diff the scopes, domains, and listing text between versions. Count how many changed a Tier 1 item without being resubmitted. That number tells you how large the problem is, and you can cite it when you present the change to legal. I haven't seen your data, so I can't say what it will show.

**Legal.** I kept your original sentence as a backstop (the "may also require" paragraph), so legal's sign-off still covers the principle. The tier lists and penalties are new, so legal should re-read at least those sections and the "binding answer" line. I'm not a lawyer and can't tell you whether they need a new review.

**Open choices that are yours to make:**
- **Tier 2 deadline of 2 business days.** At 140 updates a month, Tier 2 notices will be most of your volume, so check this against your reviewers' capacity.
- **Audit sampling rate.** I left it as "random sample" so you can pick a number your team can sustain.
- **Penalty ladder.** It is a draft. Adjust it to what your partner contracts allow you to enforce.
- **Tier 1 list.** It covers the common high-risk changes. If your marketplace has other risky surfaces, such as webhooks or file access, add them as items, not as vague wording.

**Tooling that makes it hold up.** The policy only works if the submission form enforces the checklist and the manifest diff runs automatically. Without that, you are back to reviewers reading changelogs.