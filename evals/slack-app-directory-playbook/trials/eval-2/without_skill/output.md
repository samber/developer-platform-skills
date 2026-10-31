**Don't resubmit with only item 1 fixed.** Slack will probably bounce it again on items 2 and 3, and you'd lose a review round for nothing. I'm going from memory of Slack's Marketplace guidelines, so check the current ones before you rely on details.

Why the other two will fail again:
- **Item 2:** A GitHub README is not a landing page. Slack wants a real page covering what the app does, how to install it, a privacy policy, and a support contact. GitHub Issues alone is a weak support channel, because Slack expects a monitored email or help page.
- **Item 3:** Credentials to your internal demo workspace are probably the biggest blocker. Reviewers generally install the app into their own workspace. Logins to someone else's workspace tend to hit 2FA or email verification, or just get ignored.

**Plan: all three, small versions, about 1 day total**
1. **Item 1 (about 45 min):** Rewrite each scope reason as one sentence in this form: "Tallyho uses `X` to do Y when the user does Z." Example: "`chat:write`: posts the daily standup prompt in the channel the admin picks." Include the user action that triggers it, and drop any scope the app doesn't use.
2. **Item 3 (about 2 hours):** Make the app installable by a stranger. Write a short "how to test" doc with these steps: install, run `/standup setup`, answer a prompt, see the summary. Keep the demo workspace only as an optional extra, and give them a guest invite link instead of passwords.
3. **Item 2 (about 3 hours):** Publish a one-page site on GitHub Pages, Carrd, or your own domain. It needs a description, a screenshot, an install button, a privacy policy, and a support email. Keep the GitHub Issues link as secondary.
4. **Resubmit** once all three are done. Make the resubmission note answer the three review points one by one.

If you really want to ship today, fix item 1 and spend the afternoon on item 3. Item 2 can be a plain Pages site tomorrow morning. The difference between today and Monday is small, but one rejected resubmission costs you a full review cycle.

**Next:** paste your current scope list and I'll draft the item 1 reasons now, about 10 minutes.