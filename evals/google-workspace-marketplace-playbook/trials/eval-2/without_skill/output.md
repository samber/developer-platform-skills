# Is "Internal consent screen + Marketplace domain-wide install" the fastest path?

❌ **No. The plan doesn't work, and it would stall onboarding of all 60 firms.**

## Why each assumption fails

1. **"Internal" only covers users in your own Workspace organization.**
   - Internal means the OAuth project belongs to a Workspace org, and only accounts in that org can authorize.
   - Every law-firm user would get an `org_internal` error.
   - Internal is for in-house tools, not a SaaS sold to other companies.
   - Google doesn't review Internal apps because they never leave your org. You can't use it to skip review for external customers.

2. **Full Drive access is a restricted scope.**
   - `https://www.googleapis.com/auth/drive` and `drive.readonly` are both restricted.
   - An external app that stores or processes restricted-scope data on a server needs OAuth verification and an independent security assessment (CASA, repeated annually).
   - You can't avoid this by changing the consent-screen type.

3. **A Marketplace install doesn't remove review.**
   - A public Marketplace listing has its own review, and it requires a verified OAuth config for the same scopes.
   - Until verification is done, the app is "unverified". Users see the warning screen, and there is a cap of about 100 users per project.
   - For a 60-firm rollout, the cap alone can block you.

4. **Users won't see a warning only in specific cases.**
   - Verified apps show no warning.
   - Customer admins can also mark your app as Trusted in their Admin console (API controls). That removes the warning for their domain.
   - The Trusted route needs a manual step at every firm. It is a workaround, not a way to skip verification.
   - Check Google's current docs on whether trusted apps are exempt from the user cap before you rely on this. I'm not certain of the exact rule.

## Fastest realistic path

1. **Start verification now.** Submit the OAuth consent screen as External, with a domain you control, a privacy policy, and a scope justification. Review and CASA take weeks, so begin them first.
2. **Ask for the narrowest scope.**
   - `drive.readonly` is enough to scan contracts. Don't request full `drive`, which adds write and delete.
   - Reviewers and law-firm security teams will challenge write access you don't need.
3. **Run pilots in parallel, without waiting.**
   - Use testing mode, which allows up to 100 listed test users.
   - Or get 3–5 friendly firms' admins to mark you as Trusted, or to grant domain-wide delegation to a service account.
   - Delegation has to be granted per customer in the Admin console. It is powerful and is itself scrutinized by firms.
4. **Evaluate the `drive.file` + Picker fallback.**
   - Users or admins pick folders explicitly. The scope is non-sensitive, so there is no CASA.
   - The cost is UX: no silent full-Drive scan. That may or may not fit your product.
5. **List on the Marketplace after verification.** Verification comes first, since the listing depends on it.

## Law-firm context

- Firms will likely send security questionnaires, and CASA or SOC 2 evidence helps there.
- Contracts are often privileged, so many firms' IT will balk at broad scopes regardless of Google's rules.
- Expect scope-minimization questions at every one of the 60 firms.

## Questions to answer

- Can the product work with `drive.readonly`, or does it really need write access?
- Do your pilot firms have Workspace admins who can trust the app or delegate to your service account?
- Do you store contract content or derived text on your servers? If you only process and discard, tell the reviewers, because it affects the assessment.
- What is your launch deadline? That decides whether to run the pilots in parallel (step 3) or wait for verification.

I haven't verified current CASA pricing or timelines. Check Google's OAuth verification and CASA pages before committing to dates.