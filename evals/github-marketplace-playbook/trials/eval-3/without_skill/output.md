# Ferrocline: Marketplace verification, the org move, and pricing

I didn't re-fetch GitHub's docs for this. Check the items marked ⚠️ against the current docs before you act on them.

## Short answers

1. ❌ **The blue badge on your org profile doesn't make you a verified creator on Marketplace.** They are two separate badges. Domain verification is a prerequisite for the Marketplace badge, not the badge itself.
2. ⚠️ **Do the org move after the badge is in place, or accept that you lose it.** The badge belongs to the owning org, so a move to `ferrocline-oss` probably resets it.
3. ❌ **You can't charge for the action itself on Marketplace.** Actions are free listings. Paid plans exist only for GitHub Apps.

## 1. The verified-badge confusion

| Badge | Where it shows | What it proves | Does the customer's policy read it? |
|---|---|---|---|
| Verified (org profile) | `github.com/ferrocline` | You proved control of your domain | ❌ No |
| Verified creator | The Marketplace listing for `scan-action` | GitHub verified the publisher, after a separate application | ✅ Yes |

The customer's enterprise policy is "Allow GitHub-created actions and Marketplace actions from verified creators". It looks at the Marketplace creator badge, so your action gets blocked until that exists.

### Fix the customer today

You don't need to wait for the badge. An enterprise or org owner can add your action to the allow list:

- Open the enterprise policy under Actions → Policies → "Allow enterprise, and select non-enterprise, actions".
- Add `ferrocline/scan-action@*`, or pin a tag or full commit SHA for stricter control.
- If they pin by SHA, they get the best supply-chain posture and approve each upgrade.

If you move the repo, they must add `ferrocline-oss/scan-action@*` too. Don't rely on GitHub's old-name redirect satisfying an allow list. ⚠️

### Get the Verified creator badge

1. Confirm the domain verification is done on the org that will own the action. It already is for `ferrocline`.
2. Request the Verified creator badge from the Marketplace publisher settings or listing, following the "About badges in GitHub Marketplace" docs. ⚠️
3. Confirm 2FA is required for the org and that the listing is published and current. ⚠️
4. Wait for GitHub's review. I don't know the turnaround, so don't promise the customer a date.
5. Check the listing page itself for the "Verified creator" tag, not the org page.

## 2. The move to `ferrocline-oss` next week

### Why it is risky

- The badge attaches to the creator org, so the new owner starts without it. ⚠️
- A repo transfer redirects git URLs, but a Marketplace listing and existing `uses:` references may not follow. Test with a throwaway repo.
- Every customer allow list entry naming `ferrocline/scan-action` breaks or needs updating.
- If anyone ever creates a new repo at the old `ferrocline/scan-action`, the redirect dies.

### Recommendation

Pick one of these:

- **A. Delay the move** until the badge is granted and confirmed. This is the safest option, because the customer is blocked now.
- **B. Move, then re-verify.** Verify the domain on `ferrocline-oss`, apply for the badge there, and accept the Marketplace agreement as that org. Re-publish the listing and tell customers the new allow-list string. Expect a gap with no badge.
- **C. Keep the listed action in `ferrocline`.** Use `ferrocline-oss` for other open-source repos only. This avoids all of the above.

I recommend A or C unless there's a strong reason for the move. If you must move next week, do B with the customer's allow-list entry as the bridge, and give them the new name before you transfer.

Marketplace listing rules to remember: one action per repo, `action.yml` at the root, no workflow files in the listed repo, and a release published with "Publish this release to Marketplace". ⚠️

## 3. Charging for the action

- ❌ Marketplace has no paid plans for Actions, so the action listing can't carry a price.
- ✅ Paid plans are available only for GitHub Apps, which need a verified publisher organization and financial onboarding. ⚠️ There are also minimum-install thresholds, so check the current numbers.

### Options for finance

1. **Keep the action free and sell the scanner.** The action is a thin client that needs a Ferrocline API key or account, and revenue comes from your own billing. This is the common pattern and needs no Marketplace approval.
2. **Add a GitHub App listing with paid plans.** This works if you want GitHub to handle billing, and it means a separate product surface. Expect GitHub's revenue share, so check the current terms.
3. **Do both.** The free action drives installs, and the paid plan unlocks higher scan limits or more features.

My suggestion is option 1 now, and a revisit of the App route if customers ask for Marketplace billing. It also avoids tying revenue to the org-move question.

## Next steps

1. Today: send the customer admin the allow-list entry.
2. Today: submit the Verified creator application, or confirm one is open.
3. Before the move: decide A, B or C and tell the customer.
4. For finance: confirm the action stays free and revenue rides on the Ferrocline account or key.