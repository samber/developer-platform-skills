**Don't send "the reviewer is wrong."** The likely cause is that the reviewer couldn't get past your login. Your extension needs company Okta SSO and has a 7-day trial, so a reviewer with no credentials sees a dead extension. Yellow Magnesium is, as far as I recall, the Chrome Web Store code for "functionality not working", and a login wall with no test access is a common trigger. I haven't seen the email's full text, so check that it doesn't name a different failure. An appeal that blames the reviewer usually gets the same rejection back. One that hands them working access usually gets approved.

## Do these first (about 30 minutes)

1. Create a permanent test account in a dedicated Okta test tenant.
   - Turn MFA off for it.
   - Make sure it is not subject to the 7-day trial. The reviewer may test days after you submit.
   - Seed it with demo data so the extension shows real functionality.
2. Open the Developer Dashboard, then your item, then the **Test instructions** tab. Paste the credentials and steps there. That field is private to reviewers, so put the credentials only there and never in the public listing.
3. Make sure the store listing says the extension requires a Clearpath account with SSO sign-in.
4. Test the account yourself in a clean Chrome profile with no existing Okta session.
5. Optionally, record a 60-second screen capture of the full flow and add the link to the test instructions.

## Test instructions (paste into the dashboard)

```
Clearpath requires sign-in. Use the dedicated review account below.

Okta sign-in page: <URL>
Username: <reviewer-test-username>
Password: <reviewer-test-password>
MFA: disabled for this account. The account does not expire and has no trial limit.

Steps:
1. Install the extension and click its toolbar icon.
2. Click "Sign in with SSO". Enter the credentials above on the Okta page.
3. After redirect, the side panel shows <the dashboard>. Demo data is preloaded.
4. To see the core feature: <open page X, click Y, expect Z>.

Expected result: <one sentence describing what the reviewer should see>.
Walkthrough video: <link>
Support contact: <email>, replies within 1 business day.
```

## Appeal draft

**Subject:** Appeal: Clearpath (item ID `<ID>`), violation reference Yellow Magnesium

Hello,

I'm appealing the rejection of Clearpath (item ID `<ID>`), cited as "Yellow Magnesium – functionality not working" on `<date>`.

Clearpath is a B2B analytics extension. It requires signing in through the customer's company Okta SSO, so a reviewer without access to a customer tenant can't reach any functionality. I believe that is why the review concluded it wasn't working. I should have given reviewers working access in the first submission, and I've now fixed that.

**What I've changed:**
- I created a dedicated review account in a test Okta tenant. It has MFA disabled, and it is not subject to our 7-day trial.
- I added the credentials and step-by-step instructions to the **Test instructions** tab of the Developer Dashboard.
- `<I added a walkthrough video: link.>`
- `<I updated the listing description to state that a Clearpath account with SSO sign-in is required.>`

**Expected behavior with the review account:** after SSO sign-in, the extension displays `<describe the dashboard or feature>` with preloaded demo data. I verified this flow today in a clean Chrome profile on `<Chrome version>`.

Could you please re-review the item using the credentials in the Test instructions tab? If anything still fails, please tell me the exact step and error so I can fix it right away. I can be reached at `<email>`.

Thank you,
`<Name>`, `<Role>`, Clearpath

## Before you send

- The reviewer may test days later, and a lapsed trial or a locked account repeats the rejection. Confirm the account stays valid for at least 30 days.
- If the rejection email mentions something else, such as a specific broken feature or a permission, tell me and I'll adjust the draft.
- If you can, resubmit the updated item at the same time as you file the appeal. The new test instructions only help if the reviewer sees them.