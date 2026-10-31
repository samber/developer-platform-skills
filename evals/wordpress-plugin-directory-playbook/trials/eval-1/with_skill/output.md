# Formline: WordPress.org submission readiness

**Verdict: not ready to submit as built.** The greyed-out Pro tab and the in-plugin 14-day trial would both be rejected as trialware (Rule 1). Both fixes are small and move the logic into your service. Do them first, then submit next week.

## Assumptions (I couldn't ask, so please correct any that are wrong)

1. **Pro features run in your service.** A/B testing and heatmaps are assumed to be a tracking script loaded from Formline, plus API data that the plugin renders locally. If variant swapping must run in local PHP or JS, rung 2 (a premium add-on) moves up. Tell me if that applies.
2. **Plan enforcement.** I assumed your API can return plan, trial status and quota per account. If it can't, building that is the main blocker.
3. **Submitting account.** I assumed you have no WordPress.org account yet, or only a personal or agency one. You need a company account with a company-domain email and 2FA.
4. **Stage and launch.** The plugin is not submitted and not live. I don't know your launch date, so I can't give a launch-date plan yet.

## Paid-value verdict: rung 1

The menu rung is **a directory connector with paid features enforced by your service**. It is one codebase and one review, and it's the default for a SaaS. It still holds if assumption 1 is true.

## Required changes

| Today | Problem | Change |
|---|---|---|
| Pro tab visible but greyed out, with an "Upgrade" button | Locked UI shipped in the plugin is trialware (Rule 1) | See the Pro tab fix below |
| Pro license key unlocks the tab | A key that unlocks local code is banned | Replace it with an account connection (OAuth or an account API key) that only identifies the site to Formline |
| 14-day trial that switches itself off in the plugin | Time-limited features are trialware | Start the trial in your service when the account connects. The plugin shows "N days left" from the API and has no local expiry logic |
| 500 submissions/month on the free plan | Fine only if the service counts it | Count and enforce in your service. The plugin shows usage and a service message at the limit |
| Settings / Insights / Pro tabs | Fine if rendered locally | Build screens in PHP/JS shipped in the plugin. No iframed Formline dashboard |

**Pro tab fix.** Pick one of these:
- **Recommended:** show the A/B and heatmap screens only when the API says the account has them. For other accounts, show one contextual upgrade note on your settings page, with a link to your pricing page.
- Alternative: keep one Pro tab whose content is a service-provided message, with no disabled controls.

**Reviewer risk.** Named-but-absent pro features in free code read as trialware to reviewers, so don't leave them in the code as stubs.

## Name, account, slug

- **Name:** `Formline <job>`, for example "Formline Form Analytics". The brand is first and you own it.
- **Account:** submit from the company WordPress.org account, with a company-domain email and 2FA. A wrong account is fixed by replying to the review email, never by resubmitting.
- **Slug:** avoid "wordpress" and "plugin" in it. You can change it once before approval, never after. The text domain and main file name must equal the final slug.
- **Contributors:** use the submitting username, exactly as cased.

## Packet checklist

| # | Item | Owner |
|---|---|---|
| 1 | Remove the greyed Pro UI, license-key unlock and local trial logic | Plugin dev |
| 2 | API fields for plan, trial days left and quota, plus a service-side 14-day trial | Backend |
| 3 | Heatmap and A/B admin views built locally from API data, no iframes | Plugin dev |
| 4 | Admin UI libraries bundled in the plugin. The front-end tracker may load from Formline if documented | Plugin dev |
| 5 | No call on activation. Count installs at account connection | Plugin dev |
| 6 | Unique prefix of 4+ characters on everything. `wp_enqueue_*` only, no inline script or style | Plugin dev |
| 7 | Plugin Check with no error in the Plugin Repo category. Security category too. Zip under 10 MB† | Plugin dev |
| 8 | Live terms and privacy pages, and live Plugin URI and Author URI | Marketing/Legal |
| 9 | Company WordPress.org account, company-domain email, 2FA | Founder/IT |
| 10 | Readme and External services section (drafts below) | Plugin dev + Legal |
| 11 | Monitored committer email, not an auto-responder | Support |

## Readme header draft

```
=== Formline Form Analytics ===
Contributors: <company-username>
Tags: form analytics, forms, heatmap, a/b testing, conversion
Tested up to: <current major>
Stable tag: 1.0.0
License: GPLv2 or later
License URI: https://www.gnu.org/licenses/gpl-2.0.html

Shows how visitors use your forms. Requires a free or paid Formline account.
```

`Requires at least` and `Requires PHP` go in the main PHP file header. Keep the short description to 150 characters or fewer. Use five tags at most, and no competitor names. Don't list "Pro" as a locked feature in the readme.

## External services draft (check each statement against the real data flow)

```
== External services ==

This plugin connects to the Formline service (api.formline.example) to show
form analytics in your WordPress admin. After an administrator connects a
Formline account on the settings page, it sends the site URL and form
submission and interaction events (for example, which field was abandoned) when
visitors use forms. If heatmaps or A/B tests are enabled for the account, a
script loaded from Formline records visitor interactions on the pages that
contain them.
Formline terms of use: https://<live-url>/terms
Formline privacy policy: https://<live-url>/privacy
```

- **Don't send field contents** unless you disclose it.
- **Don't claim GDPR compliance.** Say what the plugin assists with.
- **Heatmaps** record visitor behavior, so describe that precisely and make sure your privacy policy covers it.

## Timeline

- **This week:** do items 1-9. The fixes in 1-3 are the critical path.
- **Next week:** submit. Only one plugin can be in review per account.
- **After submission:** expect several review rounds. Each fix waits about 10 business days† for a reply. A review still incomplete after 3 months† is rejected.
- **Search listing:** a new plugin appears 6 to 14 days† after its first commit.
- **No queue jumping,** except for security or legal reasons. The queue has swung between near zero and about 1,050† plugins.
- **Don't tie a launch date to approval.** If approval misses the launch, announce "coming to WordPress.org".
- **After approval:** push code before launch. An approved plugin with no code for 6 months† can be closed.

## After approval

- **Release flow.** Treat SVN as a release channel. Put code in `trunk/` and copy each release to `tags/<version>`. Deploy from CI with the SVN password.
- **Release checks.** Run Plugin Check, Security category included, before each tag. Set `Stable tag` to a real tag. Turn on Release Confirmation.
- **Cooldown.** Every release waits 6 hours† for an automated security review. A blocked version leaves sites on the previous one, and the listing stays up.
- **Support.** Support only the free plugin in the forums. Send paid-plan questions to your own channel. Never ask for, pay for or seed reviews.
- **Closing.** Never close the plugin to "pause" it.

## Measures to watch

1. Approval date.
2. Connected sites as a share of active installs.
3. Resolved forum-thread share.

† verify against the current developer.wordpress.org handbook and make.wordpress.org/plugins; the release process changes often.

## Questions

- Do A/B variants and heatmaps run via a Formline-hosted script, or in local PHP?
- Can your API already return plan, trial and quota per account?
- Which WordPress.org account and email domain will submit?