**Next action (10 min):** open the Platform UI, go to the integration's usage view, and write down how many live Zaps use `trigger_1`, `search_2` and Delete Invoice. The decisions below depend on those counts.

## Three plan changes

1. **Do not rename keys.** A Zap stores the key of each step. Renaming `trigger_1` breaks every Zap that uses it, and the ~40 customers won't know why. Users never see keys; they see labels. Fix the labels and keep the keys.
2. **The sort order is a functional bug, not a cosmetic one.** Zapier reads the first page of a polling trigger and expects newest-first. Yours returns the 20 oldest invoices, so a customer with more than 20 invoices likely never sees new ones fire. Check whether customers already complain that "Updated invoice" is flaky.
3. **API key by email blocks a directory submission.** Users must be able to connect without contacting you. You already issue OAuth tokens, so use OAuth.

I haven't seen the integration code, so check the assumptions marked below against it.

## Plan

### Phase 0: Audit (½ day)
1. Get Zap counts per step (the next action above).
2. Convert the Platform UI integration to Zapier CLI, if your account offers it (check the current docs). Put it in git. Every change below needs code and tests, and the UI gives you neither.
3. Read the trigger code. Record which field it returns as `id` and what the sort and page parameters are.

### Phase 1: Version 1.1.0, non-breaking (3–4 days)
Ship to the 40 customers via `zapier migrate`. Keys stay unchanged.

1. **Trigger `trigger_1`:**
   - Request newest-first and return up to 100 items, not 20.
   - Make `id` change on each update, for example `${uuid}-${updated_at}`. If it returns the bare UUID today (assumption), "Updated" fires once per invoice ever.
   - Changing the `id` scheme makes up to 100 recent invoices look new to Zapier's dedupe on the first poll, so some Zaps will fire once more. Ship it with the sort fix, and tell customers beforehand.
2. **Add a "New Invoice" trigger** with a clean key (`invoice_new`). Directory reviewers and users expect one.
3. **Tax profile:**
   - Add a hidden trigger `tax_profile_list` that returns `{id, name}`.
   - Point the field at it with `dynamic: 'tax_profile_list.id.name'`.
   - Keep the field key. Existing Zaps with a typed id keep working.
   - First confirm your API has a tax-profile list endpoint.
4. **Delete Invoice:**
   - Put "Permanently deletes an invoice. This cannot be undone." in the description and help text.
   - If the audit shows zero Zaps use it, hide it from the public version.
   - Product question: invoices are financial records. A "Void Invoice" action may be the safer public replacement.
5. **Labels and copy:**
   - Use Title Case labels: "Updated Invoice", "Find Invoice", "Create Customer".
   - Write one-sentence descriptions in the style "Triggers when an invoice is updated."
   - Add realistic sample data and labelled `outputFields`.
   - Make the search return an empty array, not an error, when nothing matches.
   - Use clean snake_case keys on new items only (`invoice_new`, `tax_profile_list`).

Webhooks are not an option because you have no subscription endpoint, so polling stays. A subscription endpoint is a later backlog item.

### Phase 2: Version 2.0.0, OAuth (3–5 days, mostly on the API side)
1. Register a **new** OAuth client for Zapier. Don't reuse the mobile app's client: Zapier needs a confidential client with a secret and its own redirect URI.
2. Whitelist the redirect URI that Zapier shows for your integration.
3. Use the authorization-code flow with refresh tokens, minimal scopes, a `/me`-style test endpoint, and a connection label (the account name).
4. Zapier almost certainly can't convert an API-key connection to OAuth in place (verify in the docs). Customers have to reconnect. Keep 1.x live, email the ~40 customers, and migrate them in a batch once they have reconnected.
5. If OAuth slips, ship an interim fix: a self-serve API-key page in your app settings, linked from the auth field's help text.

### Phase 3: Submission prep (2–3 days, next quarter)
Check the current Zapier publishing checklist before you start.

1. Prepare a reviewer test account with sample invoices and tax profiles.
2. Add a logo to Zapier's spec, a support email, and privacy and terms links.
3. Add help docs and 3–5 Zap templates.
4. Submit once 2.0.0 is live and all customers have migrated.

## Decisions I need from you

1. **Keys:** keep the old ones (my recommendation), or add new keys and hide the old ones? Hiding means two parallel steps forever.
2. **Delete Invoice:** keep with a warning, hide, or replace with Void? Decide after the audit.
3. **Duplicate firing:** accept one refire when the `id` scheme changes (my recommendation), or stagger the rollout?
4. **OAuth:** include it in this quarter's work (my recommendation), or ship the interim key page first?

Reply with answers to 1–4, or at least the Zap counts from the audit.