# WordPress.org submission packet

Items marked † change often: verify against the current handbook at developer.wordpress.org/plugins/wordpress-org/.

## Contents

1. Readme header
2. External services section
3. Pre-submit checks
4. Reviewer reply
5. Release checklist

## 1. Readme header

The readme must be in English; translations come from translate.wordpress.org.

```
=== Acme Forms Sync ===
Contributors: acmeinc
Tags: forms, crm, lead capture, contact form, sync
Tested up to: <current major, e.g. 7.1>
Stable tag: 1.0.0
License: GPLv2 or later
License URI: https://www.gnu.org/licenses/gpl-2.0.html

Sends form entries to your Acme workspace. Requires a free or paid Acme account.
```

- Contributors: the submitting WordPress.org username, exactly as cased.
- `Requires at least` and `Requires PHP` go in the main PHP file header: the readme copies are not parsed.
- Tags: five at most; only the first five display and count, and more than 12 is spam. No competitor names, no tag only you use.
- Tested up to: the major version you tested, never above the current release candidate.
- Short description: 150 characters or fewer, no markup.
- Main PHP file `Plugin Name` must match the readme title.

## 2. External services section

One block per service the plugin calls, your own included.

```
== External services ==

This plugin connects to the Acme API (api.acme.example) to sync form entries.
It sends the entry fields and the site URL when a form is submitted, and only
after an administrator connects an Acme account on the settings page.
Acme terms of use: https://acme.example/terms
Acme privacy policy: https://acme.example/privacy
```

```
// ✓ Good - names the host, the data, the trigger, and both links
// ✗ Bad - "This plugin uses a third-party service." with no host, data or trigger
```

## 3. Pre-submit checks

- Plugin Check passes with no error in the Plugin Repo category.
- Zip under 10 MB†, installable via Upload Plugin; no `node_modules`, tests, demos, logs or zip files inside.
- Built JS/CSS: source included, or a public repository linked from the readme; keep `composer.json`.
- Unique prefix of four or more characters on functions, classes, options, transients, hooks and constants.
- Scripts and styles through `wp_enqueue_*`; no inline `<script>` or `<style>` output; WordPress's bundled jQuery.
- No call unrelated to the service (install analytics, telemetry) before a default-off opt-in; count installs when the admin connects.
- Site-wide notices dismissible; upgrade prompts sparing, contextual or on your settings page.
- Plugin URI and Author URI live and complete; terms and privacy pages live. Free and premium plugins never share a Plugin URI.
- Text domain and main file name (`<slug>.php`) equal the slug.
- Submitting account: company domain email, 2FA on.

## 4. Reviewer reply

Reply in the thread of the "Review in Progress" email, after uploading the fixed zip on the submission page.

```
Thanks for the review. Version 1.0.1 is uploaded and addresses each point:
1. Undocumented external service: added an "External services" section naming api.acme.example, the data sent, when, and the terms and privacy links.
2. Inline script: moved to wp_add_inline_script() on our settings page only.
3. Generic prefix: renamed acf_ to acmefs_ across functions, options and hooks.
```

## 5. Release checklist

1. Run Plugin Check, Security category included.
2. Bump `Version` in the main file and `Stable tag` in `trunk/readme.txt`; add the changelog entry (current and previous major only).
3. Commit `trunk/`, then copy it to `tags/<version>` (numbers and periods only).
4. With Release Confirmation on, confirm from the emailed link; pick the 24-hour auto-update delay† for risky releases (manual updates still go through).
5. Expect the cooldown of 6 hours† before sites see it; watch committer email for a block notice.
6. On a block: fix the findings, release a new version; reply to the email only for a clear false positive.
7. Readme-only edits (Tested up to, FAQ): update `trunk/` and the current tag, no version bump. With Release Confirmation on, released tags are frozen, readme included: ship the Tested up to bump with the next release. Assets sit outside tags and never need a release.
