# Tallyhub WordPress connector: pre-submission review

**Verdict:** 4 of the 6 items would get the plugin rejected under the WordPress.org Plugin Guidelines. The other 2 need changes to pass or to avoid risk. I'm working from my knowledge of the guidelines and haven't re-checked the live text, so confirm against it before you submit.

## Blockers (reviewers reject for these)

| # | Spec item | Problem | Change |
|---|---|---|---|
| 1 | Admin page is an iframe of app.tallyhub.io | Guideline 8 disallows iframing an external service's admin panel. The plugin must not be a shell around a remote dashboard. | Build a small native settings page: connect (API key or OAuth), widget on/off, placement, status. Add an "Open Tallyhub dashboard" link that opens in a new tab. You don't need to rebuild the dashboard. |
| 2a | Admin UI library loads from your CDN | Guideline 8 forbids loading JS/CSS libraries from CDNs when they could be bundled. | Bundle the admin UI library inside the plugin. Use WordPress's own components where you can. |
| 3 | POST site URL and admin email on activation | Guideline 7 forbids tracking or collecting data without explicit, opt-in consent. Collecting the admin email silently is the worst case. | Make analytics opt-in: an unchecked checkbox or notice, off by default, with nothing sent on activation. Collect only what you need and drop the email. Document it in the readme and privacy policy. WordPress.org already gives you active-install counts. |
| 4 | "Get Tallyhub Pro" downloads and installs a zip from your servers | Guideline 8 forbids plugins from installing other plugins or add-ons from outside the repository, and from custom updaters that bypass it. | Make the button a plain link to your pricing or checkout page. Customers download the Pro zip from your site and upload it themselves. Pro updates can come from the Pro plugin's own distribution. |

## Must change before submitting

| # | Spec item | Problem | Change |
|---|---|---|---|
| 5 | "Powered by Tallyhub" in footer, on by default | Guideline 10 forbids front-end credit links unless the site owner explicitly opts in. | Default to off and add a clearly labeled setting. You can also put the credit inside the chat widget itself, which is part of the service. |
| 6 | "Makes your support desk 100% GDPR compliant" | The plugin can't deliver compliance, and "100%" is an unverifiable legal claim. Guideline 12 covers misleading readmes, and a regulator or customer could hold you to it. The plugin also sends visitor data (IP, chat content, cookies) to a third party, which needs a lawful basis on the site owner's side. | Use a factual line such as "Helps you run your support desk with GDPR-minded controls". List the real features (data retention settings, consent gating, export and delete). Have legal approve the wording. |

## Item 2b: chat widget JS from your CDN

This is allowed in principle. Loading the service's own client script is the service, not a library, and the guidelines permit SaaS connectors. Three conditions apply:

- **Disclose it.** Add an "External services" section to the readme. For each service, state what it is, what data is sent and when, and link to your Terms and Privacy Policy. This section is now routinely required.
- **Make it a real integration.** The plugin must do more than load a stub. Settings, a connection check and a shortcode or block count as substance.
- **Load only when configured and consented.** Don't load the widget before an account is connected. Offer a "load only after visitor consent" option, because the widget sets cookies and transfers visitor data.

Your hotfix goal still works. Keep the widget script remote and ship everything else (admin UI, settings logic) in the plugin.

## Checklist before you submit

1. Run the **Plugin Check** plugin and fix every error.
2. Sanitize input, escape output, and use nonces and capability checks on every admin action.
3. Add `uninstall.php` to remove options on delete.
4. Check the license: GPLv2 or later for all bundled code and assets.
5. Make sure the plugin name and slug don't breach someone else's trademark. "Tallyhub" is yours, so that's fine.
6. Re-read the readme for other superlatives or unverifiable claims.

## Questions for you

1. Is a native settings page plus an "Open dashboard" link acceptable to product? It's the largest scope change.
2. Do you need install analytics, or would opt-in or WordPress.org's own stats cover it?
3. Does the Pro tier need to live in the same plugin? If so, the code can ship but the licensing and download flow must stay off-platform.