# Ferrocline: GitHub Marketplace answer

The skill's route for this is **Action** listings. The pricing question also touches the "deciding" route for GitHub Apps. I ran no interview, so the assumptions are stated below.

## 1. Are you verified on Marketplace? No.

You have three different marks, and your blue badge is the wrong one:

| Mark | What earns it | Does it pass a "GitHub and verified creators" Actions policy? |
|---|---|---|
| Org domain badge (the blue check on your profile) | Verifying your domain | No |
| App publisher verification | Org-wide 2FA, a verified domain, a contact email. It only matters for selling a GitHub App. | No |
| **Actions verified creator badge** | Acceptance into GitHub's Technology Partner Program: an established company, a commercially available product, and an NDA. Then you email partnerships@github.com. | **Yes** |

- The domain badge only shows you control the domain. It doesn't make `ferrocline/scan-action` a verified creator's action.
- GitHub publishes no timeline for the verified creator badge. Don't promise the customer a date.

## 2. Unblocking the big customer

The customer's policy is working as designed, so this is a customer-side fix. Their GitHub admins can allowlist your action in two ways:

- **`ferrocline/scan-action@*`** allows every version of the action.
- **A full commit SHA** allows one exact version and is the stricter option.

A tag does not work. Locked workflows don't match tags, so don't tell them to allowlist `@v2`.

**Next steps**

1. Send the customer's admin the exact allowlist string. Offer both the `@*` form and the SHA form, and let their security team pick.
2. Tell them to pin the action by SHA in their workflows. That is what their policy wants anyway.
3. Start the Technology Partner Program application now as a parallel track. It fixes this for every enterprise customer, but plan around it taking a long time.
4. Treat the allowlist as the default answer for every enterprise buyer, and put it in your onboarding docs.

## 3. The move to ferrocline-oss next week

- **The badge does not follow the move.** A repository transfer keeps the Marketplace listing and the redirect. It drops the verified creator badge unless the new owner is also a verified creator.
- **Decide which org should own the badge before you apply.** If the move is happening, the Technology Partner Program application should name the org that will own the action, which is `ferrocline-oss`. Otherwise you risk applying for `ferrocline` and then losing the badge on transfer.
- **Customer allowlists name the owner.** Entries for `ferrocline/scan-action@*` may not match once the action lives under `ferrocline-oss`. I can't confirm from the skill whether GitHub's policy evaluation follows the redirect, so test it. Until then, tell customers to add `ferrocline-oss/scan-action@*` before the cutover and keep the old entry too.
- **Never create a new repo at the old `ferrocline/scan-action` path.** It would break the redirect. Only archive or delete a retired action's repo deliberately, because deleting a repo frees its name for anyone.
- **Check the listing after the transfer.** Confirm it is still published and that the name has no clash.

**My recommendation:** if no customer is blocked by the move itself, delay it until the badge application is accepted and made for `ferrocline-oss`. If the move must happen next week, send customers the new allowlist string first.

## 4. Can finance put a price on the action? No.

- **Actions carry no pricing on Marketplace.** They publish instantly with no review and no price. The skill's rule for this is "sell the product the action calls".
- **Practical shape:** the action stays free and acts as the funnel. The paid thing is the drift scanner itself, sold through your own billing or direct contracts.

If finance specifically wants GitHub billing, there is a different product, a **GitHub App** with paid plans. I'd treat it as a later option:

- **It is a separate build.** You would build an app, not reuse the action.
- **Requirements:**
  - A publisher-verified organization.
  - 100 or more installations† before you can request paid plans.
  - `marketplace_purchase` billing event handling.
  - Financial onboarding.
- **Costs:** a 5%† fee. Payout comes at the end of the following month once a month reaches $500†, and the first payout can take up to 90 days† after registration.
- **Timeline:** two to four months for paid plans.
- **Prices are permanent.** A published price can only be retired, and buyers keep it.
- **Your big customer can't use it anyway.** Invoiced enterprises can't buy paid apps through Marketplace. Only an enterprise owner who is also an org owner can buy, through the enterprise account. Keep a direct contract path regardless.

Per the skill's default menu, stay on an unlisted public app until someone owns billing, then a free listing, and go paid only once card-paying teams self-serve past 100 installs†.

## Assumptions, since I couldn't ask

- Ferrocline's action is a standalone Action, not a GitHub App or OAuth app.
- The scanner is sold outside Marketplace, through your own site or contracts.
- Nobody currently owns billing-event handling, so a paid app isn't feasible this quarter.
- The cutover is a straight repository transfer.

**Questions that would change this answer:**
1. Is the move to `ferrocline-oss` fixed, or can it wait for the badge?
2. Is the action already published on Marketplace?
3. Is the customer's block specifically "verified creators only", or a full allowlist?
4. Do you have engineer-weeks for a paid app?

## Actions in order

1. **This week:** send the customer the allowlist strings and the SHA-pinning advice.
2. **This week:** decide whether to delay the move. Then email partnerships@github.com naming the org that will own the action.
3. **Before the cutover:** publish the new allowlist string to customers. After the cutover, check the listing and the redirect.
4. **Tell finance:** the action cannot be priced. The price goes on the scanner. A paid GitHub App is an optional later project with a 5%† fee.

`†` These are GitHub figures from the skill. I haven't checked them against the current GitHub Marketplace docs, so verify them before anyone plans around them. GitHub has changed its fee and categories before.