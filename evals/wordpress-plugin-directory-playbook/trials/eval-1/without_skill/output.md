# Formline WordPress plugin: WordPress.org readiness review

I reviewed the setup as you described it. I did not see the plugin code, so the code-level checks at the end are for you to run.

**Next action:** drop the in-plugin 14-day trial and the key-gated Pro tab before submitting. As described, both would very likely be rejected.

## Verdict

| Item | Status | Why |
|---|---|---|
| Free plan, 500 submissions/month | ✅ OK if the service enforces it | WordPress.org allows plugins that front an external service. The limit must live on Formline's servers, not in plugin code. |
| Settings tab, free Insights tab | ✅ OK | Both need the external-service disclosure and consent flow below. |
| Pro tab, greyed out until a license key unlocks it | ❌ Likely rejected | Guideline 5 bars features that are locked in the plugin's own code. |
| 14-day trial that switches off inside the plugin | ❌ Rejected | Guideline 5 bars trialware, meaning any plugin limited by time, usage, or quota in its own code. |
| Data sent to Formline | ⚠️ Needs work | Guidelines 6 and 7 require consent, and the readme must disclose the service. |
| "Upgrade" prompts | ⚠️ Keep small | Guideline 11 bars nagging and hijacking the admin. |

## Fix 1: Pro tab

The question reviewers ask is whether Pro code ships in the plugin and is disabled until payment. If A/B testing and heatmaps are PHP or JS in the plugin that a key switches on, that is locked code and gets rejected.

Pick one:

1. **Serviceware (recommended).**
   - A/B testing and heatmaps run on Formline's servers.
   - The plugin only displays results and settings fetched from your API for the connected account.
   - A Pro account unlocks them server-side. The plugin ships no Pro logic to unlock.
   - A license key is acceptable if it only authenticates the account to your service.
2. **Separate Pro plugin.** Host a "Formline Pro" add-on on formline.com. The .org plugin never contains the Pro code.

Whichever you pick, change the Pro tab:

- Do not render dead, greyed-out controls. Show a short description with one link to the pricing page.
- If the account is Pro, render the real data from the API.
- Keep upgrade prompts to that tab, plus at most one dismissible notice. No banners on every admin page.
- Do not store the license key unencrypted in a public-readable location. Use an options row with `autoload` off.

## Fix 2: 14-day trial

Move the trial to the Formline account:

1. The user starts the trial on formline.com, or from a button in the plugin that opens formline.com. Your server records `trial_ends_at` on the account.
2. The plugin asks your API for the plan and its state (`free`, `pro_trial`, `pro`) and shows it. It never computes expiry itself, and no timestamp or counter in `wp_options` can disable anything.
3. When the trial ends, the server stops serving Pro data. The plugin shows the free-plan view and an upgrade link. No code path in the plugin turns itself off.
4. Server errors fall back to the free view. Never lock out the free features.

This is the same model as the 500-submission quota. The service decides and the plugin displays.

## Fix 3: External service, consent, privacy

Form analytics can see personal data, so this is where a reviewer or a GDPR complaint is most likely.

- **Opt-in only.** Send nothing until the admin connects a Formline account or ticks an explicit consent box. Do not auto-connect on activation.
- **Data minimization.** Default to metadata only: field names, timings, drop-off, and counts. Do not send field values unless the admin enables it. Document exactly what is sent.
- **No tracking of visitors outside forms.** No analytics beacons to Formline for plugin telemetry unless it is opt-in.
- **Privacy policy.** Register suggested text with `wp_add_privacy_policy_content()`.
- **No third-party code on the front end** except from your own service, and any script loaded from it must be disclosed. Bundle every library locally and use no CDNs.
- **No "Powered by Formline" link** on the public site unless it is off by default.

### Draft readme.txt section (fill in the URLs)

```
== External services ==

This plugin connects to the Formline service (https://formline.com) to analyze
how visitors interact with your forms. The connection is off until you connect
a Formline account in Settings.

What is sent and when:
* After you connect: form IDs, field names, field-level timing and drop-off
  events, and submission counts, sent when a form is viewed, interacted with,
  or submitted.
* Field values are not sent unless you turn on "Send field values".
* Your site URL and account token are sent with each request.

Free accounts include up to 500 submissions per month. Higher limits, A/B
testing, and heatmaps are provided by paid Formline plans on the Formline
service.

Terms of service: <URL>
Privacy policy: <URL>
```

Rewrite the "what is sent" list to match what the code actually sends.

## Fix 4: Technical checklist

Run these before submitting:

1. **Plugin Check (PCP).** Install the official "Plugin Check" plugin and clear every error and warning.
2. **Licensing.** Use GPLv2-or-later (or compatible) for the whole plugin, with the `License:` header and a `LICENSE` file. Check that all bundled libraries are compatible.
3. **readme.txt.** Include:
   - `Stable tag`
   - `Tested up to` (current WordPress)
   - `Requires at least`
   - `Requires PHP`
   - License
   - The External services section above
   - A short, non-misleading description with no keyword stuffing and no fake reviews
4. **Naming and trademarks.** The slug must start with a brand you control. Submit from an email on your own domain so ownership is clear. The slug is hard to change later.
5. **Security.** Check each of these:
   - Every admin action has a `current_user_can()` capability check.
   - Every form and AJAX handler has a nonce.
   - Input is sanitized and output is escaped (`esc_html`, `esc_attr`, `esc_url`).
   - Database access uses `$wpdb->prepare()`.
6. **Prefixing.** Use a unique prefix for functions, classes, options, and hooks, such as `formline_`.
7. **Text domain.** It must match the slug, and all strings must be translatable.
8. **Uninstall.** Add `uninstall.php` that removes options and any stored tokens.
9. **Code readability.** Ship source for any minified JS/CSS (or a build link in the readme). No obfuscated code.
10. **No update or license phone-home** that bypasses WordPress.org updates. Updates come only from the .org repository.
11. **Assets.** Provide icons and banners, and make sure screenshots show only the free features.

## Plan for next week

| Day | Task |
|---|---|
| Mon | Decide Pro model (serviceware or separate plugin). Make the server-side trial and plan API changes. |
| Tue | Remove local gating and the trial logic from the plugin. Rebuild the Pro tab as an API-driven view. |
| Wed | Add the consent flow, data-minimization default, and privacy text. Write the External services readme section. |
| Thu | Run Plugin Check and the security pass. Prepare assets. |
| Fri | Submit from the company-domain email. |

Review time on WordPress.org varies, and reviewers often ask for changes. Treat Friday as the submission date, not the approval date.

## Questions for you

1. Do A/B testing and heatmaps run on Formline's servers today, or in the plugin's own code? This decides which Pro model above applies.
2. Does the plugin send field values, or only metadata?
3. Is the license key checked against your API, or validated locally?

If you share the plugin zip or repo path, I can run the technical checklist against the real code.