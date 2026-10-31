# Chrome extension publishing review: what should change

**Verdict:** the account is the biggest risk, not the zip upload. Your 2FA is on, but Cyberhaven shows 2FA is not the control that stops this attack. Fix in this order.

The playbook has no section on this exact situation. The transfer mechanics below come from its one line on personal-address accounts. Items marked † need checking against current Chrome Web Store docs.

## What the Cyberhaven attack was

- In December 2024, a phished employee granted a malicious OAuth app publish access to the Chrome Web Store.
- No 2-Step Verification prompt fired.
- The attacker's update passed review and reached installs with no hold.

Your 2FA would not have stopped that. Three controls would have: signed uploads, restricted OAuth app access, and publishing from CI.

## Assumptions

I couldn't ask, so I assumed three things:
1. The former engineer's Gmail is the publisher account and the only owner.
2. The 2FA device or recovery phone may still be his. Please confirm.
3. 80k users means partial rollout is available (it needs over 10,000 seven-day active users†). Customers force-install by extension ID through their IT.

## Gaps, ranked by risk

| # | Gap | Why it matters |
|---|---|---|
| 1 | The account is a departed person's personal Gmail | He holds the ability to recover or reset it, and he knows the password. 1Password sharing does not remove his access. |
| 2 | A shared login, not named members with roles | There is no audit trail and no way to revoke one person. |
| 3 | Manual zip upload from a laptop | A compromised laptop means a compromised release. Nothing proves who built the package. |
| 4 | No signed uploads (Verified CRX Uploads is off) | A stolen session or OAuth grant can publish anything. |
| 5 | OAuth app access unrestricted | This is the exact Cyberhaven path. |
| 6 | No alert on unexpected versions, no rollback runbook | You would learn of a bad publish from customers. |

## Fix plan

### Step 1: this week, contain the account (about 1 day)

1. Find out who controls the Google account's recovery email, recovery phone and 2FA device. If it is the former engineer, treat the account as compromised-by-design.
2. While you still hold the login, change the password and the recovery options. Remove any 2FA device that is not yours, and revoke third-party app access and active sessions.
3. Check the account's connected apps. Remove anything unrecognised.
4. Stop sharing the password. A shared credential was an accepted risk, so rotating it is not enough on its own.

### Step 2: move to a company-owned account (1–3 weeks, mostly waiting)

1. The developer email on a personal-address account never changes. The only path is a **new company publisher account plus an item transfer request**.
2. Create the new account on a dedicated company mailbox, such as a group alias with an owner and a backup owner. Turn on mandatory 2-Step Verification.
3. Declare Trader status with company details, which show publicly in the EU.
4. Add teammates as members with roles. No shared login.
5. File the item transfer request with Chrome Web Store support, with the former engineer cooperating if possible.
6. Ask support to confirm in writing that the **extension ID is preserved**. Your customers force-install by ID. A new item means a new ID, and every customer's IT policy would break. If the ID can't be preserved, stop and plan a customer migration before touching anything.
7. Check the new account's item slot count. New publishers get two slots† by default.
8. Don't change the live listing or ship an update during the transfer window.

### Step 3: lock down publishing (2–4 weeks)

1. **Opt in to Verified CRX Uploads** after the transfer. Every later package must then be a CRX signed with your private key.
2. Keep that private key in CI secrets or an HSM. Never put it in the Google account or on a laptop. A lost key takes up to a week† to replace, so back it up in a second secured location.
3. **Publish from CI** through the Chrome Web Store API with a dedicated service account, never a person's OAuth token. Switch CI from building a zip to building a signed CRX.
4. Guard that service account like a production secret. Its one scope grants full publish rights.
5. **Restrict third-party app access in your Google Workspace.** No unverified app should be able to obtain the Chrome Web Store scope.
6. Tell staff that store policy emails never need OAuth consent. This is the Cyberhaven lure.
7. **Alert on any published version that CI did not produce.** Compare the live version against your CI release log on a schedule.
8. Write a rollback runbook:
   - Rollback republishes the previous version under a new version number within minutes, with no review.
   - It discards pending submissions.
   - During a partial rollout it returns to the last version published to 100%, possibly two versions back.
   - Keep storage migrations backward compatible across both versions.

### Step 4: safer releases for an enterprise fleet

- **Untick auto-publish and stage approved builds.** An approved build waits up to 30 days†, then reverts to draft.
- **Use partial rollout** (over 10,000 users†). Set it before submitting, raise the percentage without review, and change one thing at a time.
- **Stage any new permission as an optional permission** behind an in-product "Enable" button. A permission with a new install warning disables the extension for every user until they accept. For force-installed fleets that is an outage you cannot undo from your side, and users there cannot disable or remove the extension.
- **Test force-installed fleets on a managed profile.** Pack two CRX versions locally to test the upgrade.

## Decisions for you

| Question | Options | Recommendation |
|---|---|---|
| Customer IT needs to trust the publisher change | Notify them proactively, or only if the ID changes | Notify them before Step 2 anyway, so a publisher-name change isn't a surprise. |
| Who owns the new account | A person, or a role alias | A role alias, plus two named owners. |
| Can the former engineer help | Yes or no | Ask him to cooperate on the transfer, then confirm his access is removed. |

## Timeline

- Day 1–2: Step 1.
- Weeks 1–3: Step 2, mostly waiting on support.
- Weeks 3–6: Step 3, in parallel with the transfer wait where possible.
- Do not ship a release between starting the transfer and getting written ID confirmation.

## Report to the CISO

1. The developer account is personal and ex-employee-controlled, and is being moved to a company account via an item transfer request.
2. Publishing is moving from manual zip uploads to signed CRX built and published by CI.
3. OAuth app access is being restricted, which is the Cyberhaven attack path.
4. Rollout and rollback controls and unexpected-version alerting are being added.
5. One open risk remains until Step 2 completes: whether the extension ID survives the transfer.