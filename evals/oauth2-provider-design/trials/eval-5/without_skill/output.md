# Marlowe Analytics: consent screen redesign and the board number

## The number: I can't give you one

I have no reliable source for "50% conversion lost to an over-scoped consent screen." I won't put an invented figure in a board deck.

- **The 50% is unverified.** Figures like it usually come from vendor blog posts, with no stated population, funnel step, or method. I can't trace it to a study.
- **Published research doesn't give one transferable number.** The permission-comprehension studies I know of (Android and OAuth research) show users rarely understand permission lists. None gives a conversion penalty that transfers to B2B workspace-admin installs.
- **Your context differs.** An admin approving an app for a workspace decides on security, not on convenience. Their rejection reasons are different from those of a consumer tapping "Allow."

**What to put in the deck instead:**

1. **Your own number:** "About one in three install requests is rejected by workspace admins." This is real and defensible.
2. **Honest framing:** "We don't yet know why. We're testing a least-privilege consent screen and will report the measured lift."
3. **A commitment:** a measured result by a named date, from the experiment below.

If the VP insists on an external benchmark, ask whoever quoted the 50% for the source. If they can't produce one, drop it. A board member who checks it will do more damage than an empty slot.

## Redesign

**Problem with the current screen:** the grouping is by access type (Read, Write, Admin) and shows raw scope strings. Admins can't tell what we do with the access, and they can't approve less. Without any evidence, I'd guess the "Admin" group and the all-or-nothing choice are the main drivers.

### Layout (top to bottom)

1. **Header:** "Marlowe Analytics is requesting access to *[Workspace name]*"
   - Subline: "Requested by *[requester name]*. You're approving for the whole workspace."
2. **Core, required (always on):** capabilities grouped by purpose, in plain language.
   - "See your events and dashboards: *read* events, projects, members"
   - "Create and update reports we generate for you: *write* reports only"
   - Each line has a "Why we need this" expander and an "Exact scopes" expander. The raw strings move there for security reviewers.
3. **Optional, off by default (individual toggles):**
   - "Manage members and roles (admin). Needed only for automatic seat sync."
   - "Write back to events/annotations. Needed only for alerting."
   - Each line states what breaks if left off: "Seat sync won't run. You can enable it later."
4. **"What we never do"** (only list claims the product backs up): e.g. "We don't read message content / delete data / change billing." Verify each line with engineering before shipping.
5. **Actions:**
   - Primary: **Approve core access**
   - Secondary: **Approve selected** (reflects the toggles)
   - Tertiary: **Send to my security team**, which generates a shareable summary or PDF (scopes, purposes, data handling, revoke steps)
   - **Cancel**
6. **Footer:** "You can change or revoke access anytime in *Settings > Integrations*." Link to the data-handling page.

### Design principles

- **Group by purpose, not access type.** Admins judge risk by "what is it for," not by the word "Write."
- **Least privilege by default.** Anything not needed for first value goes in the optional tier, and the install doesn't wait on it.
- **Incremental consent.** Request the Admin scopes at the moment the user first enables seat sync or alerting, not at install.
- **Make rejection recoverable.** The "send to security team" path and a decline-reason prompt turn a silent no into data.
- **Make the screen forwardable.** Many admins aren't the final approver, and a clean summary shortens the review.

## How to get the real number

1. **Instrument now (free):** log screen view, each toggle, approve, cancel, and a one-click decline reason ("Too many permissions / Need security approval / Don't recognize this app / Other"). This likely explains the third that reject, and it may show the cause isn't the screen at all.
2. **A/B test:** old screen vs. redesign, randomized by workspace. The primary metric is the approval rate among viewed requests. Secondary metrics are time to decision and activation within 7 days.
3. **Sample size:** check this against your weekly volume before promising a date. Detecting a drop from 33% to 25% rejection needs roughly 400 requests per arm. This is my own calculation, so check it.
4. **Segment the results:** by workspace size, since large workspaces' security reviews may not respond to UX changes.

## Caveats

- **Nothing here is validated against your data.** The redesign is a hypothesis built on common consent-UX practice.
- **Some rejections may be policy-driven.** Admins who block third-party apps won't be moved by any screen.
- **Check the "never do" claims** against the actual product before they ship.

I didn't look at the codebase or any internal files for this answer.