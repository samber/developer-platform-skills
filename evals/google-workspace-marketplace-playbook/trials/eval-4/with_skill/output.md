# What breaks if engineering pushes the manifest on Tuesday

**Short answer:** the manifest push can't go live Tuesday. Neither can the description rewrite. Both need Google approval first, and that approval takes roughly 2–4 weeks†. Pushing anyway breaks the add-on for all 40 customer orgs.

I used the `google-workspace-marketplace-playbook` skill and its submission packet. Every Google figure marked † must be checked against Google's current docs before you quote it.

## Assumptions (please correct)

1. Calendar is a new feature inside your existing Docs/Sheets Editor add-on, with `calendar.events` as the only new scope. If you add Calendar as a new host app or integration type, that change also goes through Marketplace review.
2. `calendar.events` is **sensitive**, not restricted. The skill says most Calendar scopes are sensitive, but check the Calendar scope page. If it's sensitive, there's no CASA assessment.
3. The Cloud project is inside an organization with two or more owners. If it's one person's account, moving it is step one.
4. Your existing scopes are already verified.

## What breaks

| # | Tuesday action | What breaks |
|---|---|---|
| 1 | Push manifest with `calendar.events` | Google hasn't verified the new scope. Users see the "Google hasn't verified this app" screen. An unverified sensitive scope also counts toward the 100-user cap†, which is lifetime and never resets. |
| 2 | Push manifest only | The scope is then declared in the manifest but not in the Marketplace SDK or the consent screen (Data Access). This drift shows users a second consent prompt or the unverified screen, and it's a top rejection cause. |
| 3 | 40 domain-installed orgs get the new scope | Admins must authorize new scopes in the Admin console. Google documents per-user prompts until they do, but listing policy forbids re-prompting admin-installed users. Result: support tickets, or users blocked until each admin acts. Nobody has told the admins. |
| 4 | Rewrite short and detailed description | Any App Details field edit (name, language, short or detailed description) re-enters Marketplace review. It can't go live same day. |
| 5 | Same-day listing and scope change | The listing can't be approved before OAuth verification finishes. The two are linked, so the description change waits on the scope verification. |
| 6 | Calendar copy goes live early | The listing would advertise a feature whose scope isn't approved. Keep the current description live until review passes. |
| 7 | Calendar feature with no partial-grant handling | Users may grant only some scopes. If the Calendar feature breaks when `calendar.events` is missing, reviewers reject it. |
| 8 | Privacy policy and in-app disclosure unchanged | Limited Use covers Calendar data. You need an in-app disclosure right before consent, and the privacy policy must mention Calendar. |

## What to do instead

### Change classification

| Change | Class |
|---|---|
| New `calendar.events` scope | OAuth re-verification, sensitive tier: up to 10 days† |
| Scope added to Marketplace SDK and consent screen | Same change, kept identical in all three places |
| Short and detailed description | Marketplace review |
| New host app, if applicable | Marketplace review |
| CASA | Not triggered (assumption 2) |

### Steps, in order

1. **Tuesday ships nothing to production scopes.** Merge the Calendar code behind a flag, with the manifest scope absent in production.
2. **Check for a narrower scope.** If the feature only reads, use the `.readonly` variant. If it writes, write down why the narrower one fails.
3. **Submit the verification request.** Include the per-scope justification and a demo video segment for `calendar.events`. The justification uses this template:
   ```
   calendar.events lets "<feature name>" <user-visible action>. Users <what they see>.
   <narrower scope> cannot work because <specific failure>.
   ```
4. **Update the privacy policy and in-app disclosure** with the Limited Use statement, covering Calendar.
5. **Declare the same scope in the manifest, the Marketplace SDK, and the consent screen.** Keep it as a draft until approved.
6. **Prepare the listing draft** with marketing's new copy, and submit it for review once verification is moving. Rules for the copy:
   - The short description is ≤200 characters† and the detailed one is different.
   - Google product names appear only in the "for Gmail™"-style form with attribution.
   - Marketing should use `samber/developer-platform-skills@integration-listing-optimization` for the wording.
7. **Update the reviewer test account** with sample data and steps that reach the Calendar feature.
8. **Handle partial grants.** Detect a missing `calendar.events` and re-prompt per feature, with the rest of the add-on still working.
9. **Brief the 40 orgs' admins** before release, using the notice below. Release once they have granted, or once most have and the rest are mailed.
10. **Release** the manifest, then publish the approved description.

### Dated plan (today is Sat 2026-10-31; next Tuesday is 2026-11-03)

| Date | Milestone |
|---|---|
| Mon 11-02 | Submit verification, if you can finish the packet by then |
| about Thu 11-12 | Verification complete, up to 10 days† |
| 11-16 to 11-30 | Listing approved, at the 2–4 week† end-to-end range |
| early Dec | Live date if there's one rejection round |

Answer Trust & Safety mail the same day: the review pauses until you reply. Marketing can set the same-day copy launch for the approval date, not Tuesday.

### Admin notice (send before release)

```
Subject: Action needed: authorize new Calendar permission for <Add-on>

OAuth client ID: <id>.apps.googleusercontent.com
New scope: calendar.events - <feature that needs it>
Existing scopes: unchanged.
Admin console > Apps > Google Workspace Marketplace apps > <Add-on> > review and authorize the new scope.
If you restrict API access: mark the client ID Trusted under Security > API controls.
Date the feature turns on: <date>. Until you authorize, the Calendar feature stays off; Docs and Sheets features are unaffected.
```

## Don't do these as workarounds

- **Don't set the consent screen to Internal.** It only works for the owning organization, and an Internal app fails Marketplace review.
- **Don't publish a second listing** for the Calendar version. Moving an integration into another listing loses user counts and reviews, can cut existing users' access, and needs re-verification.
- **Don't request a broader scope "to future-proof".** That is a policy breach, not a shortcut.

## Open questions for you

1. Is `calendar.events` the only new scope, and is Calendar a feature of the Editor add-on or a new Calendar host?
2. Who owns the Cloud project, and are there two owners?
3. Have you already submitted anything to Google for this scope?