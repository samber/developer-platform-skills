# Pre-submission check: Leadhound v1

❌ **Don't submit as is.** Three of your four choices are likely to get v1 rejected or pulled. I haven't seen your manifest or code, so this is based on your description and my knowledge of the Chrome Web Store (CWS) policies.

## 1. Remote CDN scripts (analytics and Intercom): ❌ blocker
- Manifest V3 bans remotely hosted code. All executable code must ship in the package.
- This is a common rejection reason. The extension CSP also blocks remote script tags in extension pages.
- **Analytics:** bundle the SDK into the build. Or skip the snippet and send events with `fetch` to your analytics endpoint (for example GA4 Measurement Protocol, or PostHog capture).
- **Intercom:** don't load `widget.intercom.io` in the extension. Link to a support page on your own domain that hosts the widget. Or open that page in a tab or popup.
- Remote data and config are fine. Remote code is not.

## 2. javascript-obfuscator: ❌ blocker
- CWS prohibits obfuscated code. Minification is allowed. String-array, control-flow flattening and dead-code injection are not.
- Reviewers flag the obfuscator's output, and you can't appeal it.
- **Real protection for the scoring logic:** keep it on your server. You already call an API for matching, so return the score or enrichment from there. The extension then holds nothing worth copying.
- For the client, use a plain minifier (terser or esbuild) and ship source maps privately.

## 3. "Does not collect user data": ❌ wrong answer
- Page URLs of LinkedIn profiles count as web history. Profile data is also personal information about third parties.
- You must declare at least these categories:
  - **Web history** (the URLs you send)
  - **Website content** or **Personally identifiable information**, if you read names, titles or companies from the page
  - **User activity**, if your analytics tracks clicks or usage
  - Anything Intercom collects (identity, messages), if you keep it
- Add a **privacy policy URL**. It must name the API, the analytics vendor and Intercom as recipients, and give retention and deletion terms.
- Certify the three Limited Use statements. They're true only if you don't sell the data or use it for ads or unrelated purposes.
- A false declaration is grounds for removal, and it's the easiest one for a reviewer to verify.

## 4. Other things to check
- ⚠️ **LinkedIn terms.** Enriching LinkedIn profiles likely conflicts with their User Agreement, which bars scraping and automated overlays. They actively report extensions. This won't necessarily fail CWS review, but it's a takedown risk, so get a legal view.
- ⚠️ **GDPR.** Profiles of EU people mean you are a controller. You need a lawful basis, a notice and a deletion path. Given the Nantes base, treat this as a launch task.
- **Permissions.** Request host access only for `https://www.linkedin.com/in/*`, not `<all_urls>`. Broad permissions slow review.
- **Single purpose.** Describe it in one line and keep the listing, permissions and code consistent with it.
- **Justifications.** Write a short justification for each permission and host pattern in the dashboard.

## Fix order (about 1 day of work)
1. Remove the remote scripts. Bundle analytics. Move Intercom to a hosted page.
2. Drop the obfuscator. Move the scoring logic to the API.
3. Publish the privacy policy and fill the Privacy tab with the real categories.
4. Rebuild, then grep the output for `http` script URLs and for `_0x` obfuscator patterns.
5. Submit.

If you send the manifest and the analytics and Intercom init code, I can check the permissions and CSP and draft the Privacy tab answers and policy text.