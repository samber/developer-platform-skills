# Clearpath rejection (Yellow Magnesium): don't file "the reviewer is wrong"

I haven't seen the rejection email's full text or your submitted Test instructions. This is based on the playbook's reading of Yellow Magnesium.

## Do this first

1. Don't appeal that the reviewer is wrong. Your two facts, Okta SSO and a 7-day trial, are the textbook cause of Yellow Magnesium. The reviewer can't reach your Okta tenant, and a 7-day trial expires mid-queue (reviews can take weeks†). The reviewer is probably right that they couldn't use it.
2. An appeal counts once per violation†, and frivolous appeals can cost future appeal rights†. A "reviewer is wrong" appeal would use that one up on a claim that doesn't hold.
3. Fix the access problem, then resubmit with working Test instructions. A resubmission is not an appeal and costs nothing. Appeal only if they reject again and the reviewer clearly had working credentials.

## What to build before resubmitting (about 1-2 hours of work)

1. Create a permanent demo tenant, seeded with sample data. It needs:
   - email and password login, with no Okta/SSO, no MFA and no expiry (not a 7-day trial);
   - server and IP allowlists open to reviewers.
2. Add an "Account required, sign in" state inside the extension, so a reviewer who lands logged out sees what to do.
3. Test the packed CRX, not just your dev build.
4. Record a short screen recording of the full flow (sign in, then each feature), host it at a stable URL, and link it in the instructions.

## Paste into the dashboard "Test instructions" field

Replace the `<…>` placeholders. Put the password only in this field.

```
Account: <reviewer@clearpath-demo.example> / <password>
Tenant: permanent demo workspace, seeded with sample analytics data.
Login is email + password. No SSO, no MFA, no trial expiry.
(Production customers sign in with their company Okta SSO; this
demo tenant bypasses SSO for review only.)
1. Click the Clearpath toolbar icon and sign in with the account above.
2. <Step: open <URL>, click <button>, expect <result>>.
3. <Step for each remaining feature>.
Server allowlists accept any IP.
Video walkthrough: <URL>
```

## Optional: note to include on resubmission, or in a support clarification

Use this if you want to answer the rejection in writing. Support clarification comes before any appeal.

```
Item: <extension ID>, violation Yellow Magnesium, version <x.y.z>.
We understand the reviewer could not access the extension's features
because sign-in requires company Okta SSO.
We have added a permanent demo tenant with email/password login
(no SSO, MFA or expiry) and updated the Test instructions with
credentials, steps to each feature, and a video walkthrough: <URL>.
The extension also now shows an "account required, sign in" state.
We request review of version <x.y.z> with these instructions.
```

## What I need from you to tighten this

- Were the Test instructions blank, or did they say "use Okta SSO / start a trial"?
- Can Clearpath add a non-SSO login for one demo tenant, or must it go through Okta? If it must, tell me, and we'll plan an alternative such as a review-only local login.
- Which features does the extension have, and on which sites does it run? I can then fill steps 2-3 and the permission-to-feature map.

## Timeline

Your live version and listing stay up while you resubmit. A rejection can trigger re-review of the live version, so fix everything cited in one resubmission. Review time is a few days to a few weeks†. Publish after approval, not on a fixed date, because approved builds can wait up to 30 days† before reverting to draft.

† Verify against current Chrome Web Store docs, which changed in 2026.