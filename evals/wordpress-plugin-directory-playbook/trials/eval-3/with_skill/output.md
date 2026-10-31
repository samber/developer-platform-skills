# Tallyhub v1 WordPress connector: changes needed before submitting

**Verdict:** ❌ Do not submit as specced. Items 1, 3, 4 and 5 break rules the review enforces and would likely bounce the plugin. Items 2 and 6 need rewording or a split. The fixes are cheap, and the plugin keeps its main value: search reach, one-click install and core auto-updates.

## Fixes by item

| # | Spec | Verdict | What to change |
|---|---|---|---|
| 1 | Admin page is an iframe of app.tallyhub.io | ❌ Banned | Guideline 8 bans iframes that connect admin pages. Build a small native settings screen in the plugin. It should have a Connect button (OAuth or registration), the connection status, and the plan and quota as returned by your API. Add a plain "Open Tallyhub dashboard" link that opens app.tallyhub.io in a new tab. The full dashboard stays on your side. |
| 2 | Widget JS and admin UI library both load from the CDN | ⚠️ Split | Widget: **allowed**. It is customer-facing and part of the service, so keep the CDN and hotfix freely, but document it in "External services". Admin UI library: **must ship inside the plugin**. It is not the service, and remote JS or CSS in wp-admin is banned (fonts excepted). Load everything with `wp_enqueue_*`. |
| 3 | On activation, POST site URL and admin email for install analytics | ❌ Banned | Install analytics is not the service, so consent to the service does not cover it. Count installs when the admin connects the account (OAuth or registration), which is already consented. If you want activation-time pings, make them a default-off opt-in. Sending the admin email makes this worse. |
| 4 | "Get Tallyhub Pro" downloads and installs a zip from your servers | ❌ Banned | Installs or updates from your servers and custom updaters are banned. The free plugin may only link to a page on your site. It must not install the add-on or hold its code. |
| 5 | "Powered by Tallyhub" in footer, on by default | ❌ Banned as specced | "Powered by" links in plugin code must default **off**. Make it an opt-in setting. Branding inside widget output rendered by your service is fine. |
| 6 | Readme: "Makes your support desk 100% GDPR compliant" | ❌ Reword | Never imply the plugin guarantees GDPR, PCI or ADA compliance. Say what it assists with, for example: "Helps support teams handle data-subject requests. Requires a Tallyhub account." Only claim features that exist. |

## Item 4 needs a decision

The ranked menu defaults to **rung 1**: one directory connector with paid features enforced by your service. The API returns plan, trial and quota, and the plugin only displays them.

- **Default (rung 1):** drop the Pro button's install behavior and keep a "See plans" link.
- **Rung 2:** use it only if the paid features must run locally in PHP or JS inside WordPress. The add-on is then a separate codebase sold on your site, with its own updater and its own Plugin URI. Free and premium plugins never share a Plugin URI.

Question for the product team: do any pro features need to run on the WordPress site itself?

## Trialware check

Not in your list, but confirm it. Nothing in the plugin may be locked, greyed out, time-limited or quota-capped until payment. The trial and the quota must be granted and counted on your service. The plugin only shows the answer. An account-identifying API key is fine. A key that unlocks local code is not.

## Also add before submitting

1. **External services section** in the readme. One block each for api.tallyhub.io (or your API host) and the widget CDN. Each block names the host, the data sent, when it is sent, and the terms and privacy links. "Uses a third-party service" is not enough.
2. **Account and name.** Submit from a Tallyhub company WordPress.org account with a company-domain email and 2FA, not an agency account. A name like "Tallyhub Support Chat" is fine only because you own the brand. The slug is permanent after approval, and you can change it once before then.
3. **Live pages.** Plugin URI, Author URI, terms and privacy pages must all work. Add a human-read email for the committers, because auto-replies after warnings can close the account's plugins.
4. **Plugin Check.** Run it with no error in the Plugin Repo category. Keep the zip under 10 MB†. Use a unique prefix of four or more characters, such as `tallyhub_`.
5. **Dismissible notices.** Upgrade prompts must be sparing and contextual.

## Hotfix expectation

"Hotfix without releases" holds for the widget only. Every plugin release waits a cooldown of 6 hours† for an automated security review. A high score blocks that version, but the listing stays up. Plan incident timelines with that delay.

## Timeline

- Expect several review rounds, each waiting about 10 business days† for a reply. The queue has swung from near zero to about 1,050† plugins.
- Search lists a new plugin 6 to 14 days† after its first commit.
- Do not promise a launch date tied to approval. If approval misses it, announce "coming to WordPress.org".
- After approval, push code promptly. An approved plugin with no code for 6 months† can be closed and its name reassigned.

## Measure to watch

Approval date first. Then connected sites as a share of active installs, which is also the clean install metric that replaces item 3. Also track the resolved-thread share in the support forums.

## Assumptions

You gave no answer on these, so I assumed:
- The plugin is not yet submitted.
- The submitting account and slug are undecided.
- Paid features can be enforced server-side.

If any is wrong, the account and rung advice changes.

† Verify against the current developer.wordpress.org handbook and make.wordpress.org/plugins; the release process changes often.