# Chrome Web Store pre-submission check: Leadhound v1

**Verdict: ❌ don't submit as planned.** Three of your four choices each map to a rejection violation. Fix them first. Figures marked † are practitioner-reported or change often, so verify them against current Chrome Web Store docs.

## Assumptions

I don't have your manifest or code, so I assumed the following:
- The extension runs on `linkedin.com/in/*` profile pages.
- It sends the profile URL to your API and renders the enriched data in a panel.
- Users sign in to a Leadhound account.

If any of these is wrong, the permission and Privacy answers below change.

## Blockers

### 1. "Does not collect user data" is false. Don't tick it. 🔴
- **Why:** Page URLs count as browsing activity. Sending them to your API is collection, and so is whatever the analytics snippet sends.
- **Violations if you tick it anyway:**
  - Purple Lithium: privacy policy silent on data.
  - Purple Nickel: data collected before disclosure and consent.
  - Purple Magnesium: browsing activity collected without a user-facing need.
  - The claim also contradicts the code, and review compares the two.
- **Data types to tick, by what the code does:**
  - Web history: the profile URLs you send.
  - Website content: any name, headline or company you read from the page and send.
  - Personally identifiable information: if you send names.
  - User activity: if the analytics snippet records clicks or usage.
  - Authentication information: if you store a session token.
  - Also tick anything stored locally or in `chrome.storage.sync`.
- **Collection rules** (the use is user-facing, because the listing describes the enrichment):
  - Disclose before collecting, with a consent step on first run.
  - Send over HTTPS.
  - Link a working privacy policy in the Privacy field, not only in the description.
  - Certify Limited Use on all three statements, and put the Limited Use sentence on your own site.
- **Policy content:** it must name the profile URLs, what your API does with them, retention, and the analytics.

### 2. Analytics and Intercom loaded from CDNs at runtime: Blue Argon 🔴
- **Why:** All extension logic must ship inside the package. A CDN `<script>` or an SDK that lazy-loads scripts is remotely hosted code.
- **Analytics:** bundle the analytics library into the package, or send events to your own endpoint. Remote data is allowed. Remote code is not. Declare these events in the Privacy tab, as above.
- **Intercom, three options:**
  - **Link out (recommended):** use a "Contact support" link to your help page. Keep it simple for v1.
  - **iframe:** show your own web page that hosts Intercom. Embedding your web app in an iframe is exempt. Its behaviour must still be reviewable, so describe it in the single purpose and justifications.
  - **Bundled SDK:** don't. Most Intercom snippets lazy-load scripts, so it fails the same way.
- **Privacy tab:** answer the remote-code question "No, I am not using remote code" only once the above is done. An honest "no" is what review verifies.

### 3. javascript-obfuscator: Red Titanium 🔴
- **Why:** Minify at most. Obfuscation is a rejection on its own. Legacy polyfills and old async helpers have also been flagged†, so target modern Chrome.
- **Protect the scoring logic by moving it server-side.** You already call an API for matching, so return scores from the API and ship no scoring code in the package. Anything in the package is readable by definition.

## Other likely rejections

4. **Reviewer access (Yellow Magnesium).**
   - A Leadhound login wall without credentials is a rejection.
   - Seed a permanent demo tenant with no SSO, MFA or expiry. Open your server allowlists to reviewers.
   - Show an "account required, sign in" state inside the extension.
   - LinkedIn is a second wall. Reviewers may not have a LinkedIn session, so:
     - Give exact public profile URLs to test on.
     - Add a screen recording of the full flow.
     - Don't ship a shared LinkedIn login in the test instructions.
   - Outside this playbook, check your use against LinkedIn's terms. A takedown on their side would hit you after approval.
5. **Permissions (Purple Potassium).**
   - Use `https://www.linkedin.com/*` as the one host permission, plus your own API origin.
   - Add `activeTab` only if a feature needs it.
   - Don't add `tabs`, `cookies`, `storage` or `<all_urls>` unless a shipped feature uses them. Each needs one justification naming the user-facing feature.
   - Keep `content_scripts.matches` to `linkedin.com/in/*`. Broad matches count as host access.
6. **Single purpose.** Write it as one sentence, e.g. "Shows Leadhound B2B data on LinkedIn profiles." The support widget must not look like a second purpose.

## Privacy tab draft

| Field | Answer |
| --- | --- |
| Single purpose | Enriches LinkedIn profile pages with Leadhound B2B company and contact data. |
| Remote code | No, I am not using remote code (after fixes 2 and 3). |
| Data types | Web history, Website content, User activity, plus PII and Authentication if the code touches them. |
| Limited Use | Certify all three. Publish the sentence on your own site. |
| Privacy policy | Working URL covering URLs sent, retention and analytics. |

## Reviewer test instructions skeleton

```
Account: reviewer@leadhound-demo.com / <password in this field only>
Tenant: permanent demo workspace; no SSO, no MFA, no expiry.
1. Click the toolbar icon, sign in.
2. Open <public LinkedIn profile URL 1>; the enrichment panel appears.
3. Open <public LinkedIn profile URL 2>.
Server allowlists accept any IP. Video walkthrough: <URL>
```

## Timeline back from launch

- **Review time:** Google states a few days to a few weeks†, and queues reached 3-4 weeks† in April 2026. Plan for one rejection round.
- **Resubmission:** don't cancel a pending review to resubmit. Staff warned that it resets your queue position†.
- **Publishing:** untick auto-publish. An approved build waits up to 30 days†, then reverts to draft. Publish on launch day.
- **Launch date risk:** if approval may miss a fixed date, demo a local build and announce the listing as coming.

## Account checklist

- Company mailbox as the developer email, which can't change later.
- 2-Step Verification on.
- Trader status declared. It's shown publicly in the EU.
- Teammates added as members, no shared login.
- CI-built package with the manifest at the root.
- After first publish, opt in to Verified CRX Uploads.
- New publishers get two extension slots† by default.

## Next steps

1. Remove the CDN scripts, drop the obfuscator, and move scoring to the API.
2. Narrow the permissions and write the permission-to-feature map.
3. Write the privacy policy and the consent step, then fill the Privacy tab with the draft above.
4. Seed the demo tenant and record the walkthrough.
5. Submit with auto-publish off.

One question would sharpen the permission map: do you read anything from the LinkedIn page itself, or send only the URL?