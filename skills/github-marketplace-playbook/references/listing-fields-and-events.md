# Listing fields and purchase events

## Listing fields (GitHub's own rules)

```
// ✓ Very short description: 40-80 chars, describes function, sentence case, no final period
Lightweight project management for GitHub issues
// ✗ Call to action
Manage your projects and issues on GitHub
// ✗ Full sentence repeating the app name
Acme is a lightweight project manager for GitHub issues.
```

- Listing name: up to 255 characters, may differ from the app name, cannot match another GitHub account unless it is yours.
- Introductory description: 150-250 characters, starts with the app name, active voice.
- Detailed description: up to 1,000 characters, 3-5 value propositions, each a level-three heading plus one or two sentences.
- Say "people" or "teams", never "users"; serial comma; no exclamation marks; acronyms only when established (API).
- Logo: at least 200x200 px, square, transparent, no text. Feature card background: 965x482 px, shown only when the app lands among the four random homepage features.
- Screenshots: up to five, at least 1,200 px wide, one aspect ratio, no browser chrome.
- One primary category, one optional secondary.
- Pricing plan: name, short description, up to four bullets, "Available for" personal accounts, organizations or both (per-seat plans: organizations only). Up to 10 plans.

## `marketplace_purchase` events

| Action                     | When it arrives                                                                                 | Do                                                                                                                    |
| -------------------------- | ----------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------- |
| `purchased`                | at purchase                                                                                     | provision from `GET /user/marketplace_purchases` after the buyer's OAuth; store `on_free_trial`, `free_trial_ends_on` |
| `pending_change`           | when a downgrade or paid cancellation is scheduled                                              | show the coming change; keep current access                                                                           |
| `pending_change_cancelled` | buyer undoes it                                                                                 | clear the notice                                                                                                      |
| `changed`                  | upgrade or seat add: at once; downgrade: next cycle; trial end; failed upgrade payment (revert) | apply plan, `seat_count` and cycle from `marketplace_purchase`, compare `previous_marketplace_purchase`               |
| `cancelled`                | free plan or trial: at once; paid: at cycle end                                                 | downgrade to free plan, or deactivate, revoke token, delete data within 30 days                                       |

- Verify the webhook signature, deduplicate by delivery ID, and sync periodically (daily works) against `GET /marketplace_listing/plans/{plan_id}/accounts`: GitHub never resends failed deliveries on its own; manual redelivery reaches back 3 days†.
- Upgrade link: `https://www.github.com/marketplace/<LISTING_NAME>/upgrade/<LISTING_PLAN_NUMBER>/<CUSTOMER_ACCOUNT_ID>`; it carries no seat count.

## Test setup

1. Register a second app with the production configuration, installable by any account, never shared.
2. Create its draft listing and publish plans inside it: published plans in a draft listing can be bought at no charge, plans saved as draft cannot.
3. Buy, upgrade, trial and cancel with your own accounts; force pending downgrades with "Apply Pending Change" in billing settings.
