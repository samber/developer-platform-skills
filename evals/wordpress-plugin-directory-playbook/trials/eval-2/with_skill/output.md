# Plan: Brevlo Forms on WordPress.org

**Verdict:** Don't submit today from your gmail account. Approval before the conference is unlikely either way. The account choice is the decision that matters most, and it can't be fixed after approval.

## Assumptions (tell me which are wrong)

1. **Plugin type:** Brevlo Forms is a connector. Forms run locally and entries go to Brevlo's service.
2. **Paid features:** Plans, trials and quotas are enforced by Brevlo's API. The plugin only displays the answers. If anything is locked or counted in PHP, see "Paid value" below.
3. **Account:** Brevlo has no WordPress.org account yet.
4. **Date:** Today is 2026-10-31, so "the 14th, 10 days away" doesn't add up. The 14th is 14 days out, and 10 days out is the 10th. Please confirm. The plan below holds for either date.
5. **Second plugin:** I don't know its name or whose brand it carries.

## Why not submit today from your gmail

- **Brand-first name:** Brevlo owns the "Brevlo" name. A brand plugin from a personal or agency account gets flagged for trademark, and a brand-first slug is blocked for non-owners.
- **No transfer later:** The plan to hand it over later doesn't work as a fix. The slug is permanent after approval.
- **Contact rules:** Every committer needs 2FA and an email a person reads. A company-domain email on the submitting account is the expected setup.
- **Wrong account after submitting:** Reply to the review email to fix it. Never resubmit.

## Both plugins today: one per account

- **One in review:** Only one plugin per account can be in review at a time.
- **No workaround:** Extra accounts created to get around that limit get suspended.
- **Plan:** Each plugin goes in from its own brand owner's account. Submit them one at a time per account.
- **If the second plugin isn't brand-named:** It can't go in from the same account while another is in review. Queue it behind the first, or submit it from its own client's account.

## Launch date: not achievable, so plan to announce instead

- **No queue jumping:** Only security or legal issues skip the queue. The queue has swung between near zero and about 1,050† plugins within months.
- **Several rounds:** Most plugins need several review rounds, and each fix round waits about 10 business days† for a reply.
- **Search lag:** Search lists a new plugin 6 to 14 days† after its first commit.
- **Fallback:** Announce "coming to WordPress.org" at the conference. Offer a direct download as an interim measure only if Brevlo wants it. That is a self-hosted zip, which has no directory search or core auto-updates.
- **Backward plan:** Treat the conference as a soft date. Submit the clean packet as early as possible, then expect 3 to 5 rounds.

## Blocker: the coming-soon page

Every URL in the plugin headers and readme must be live before submitting. A service plugin also needs live terms and privacy pages.

- **Needed from Brevlo (this week):** Live pages for Plugin URI, Author URI, terms of use and privacy policy.
- **Plugin URI:** A real page describing Brevlo Forms. A coming-soon placeholder risks review flags.
- **Owner:** The Brevlo marketing contact. This is the critical path.

## Paid value (the rule the review enforces most)

- **Allowed:** The plugin shows plan, trial and quota messages returned by Brevlo's API. An API key that identifies the account is fine.
- **Banned:** Features locked or greyed out behind a license check, trials or quotas counted in the plugin, and "Pro" tabs that are present but disabled. These count as trialware.
- **Banned:** Embedding Brevlo's dashboard in an iframe in wp-admin. Build the settings screen locally and call the API.
- **Install analytics:** Don't ping Brevlo's API on activation to count installs. Count connections when the admin links an account.
- **If paid features must run locally in PHP:** Move to the second option, a free directory plugin plus a premium add-on sold on Brevlo's site. That option costs a second codebase, its own Plugin URI, and its own updater.

## Name, account and slug

| Item | Decision |
|---|---|
| Name | `Brevlo Forms` (brand owner, then job) |
| Slug | `brevlo-forms`. Check it in the confirmation email. You can change it once before approval, never after. |
| Text domain and main file | `brevlo-forms` and `brevlo-forms.php` |
| Submitting account | A new Brevlo company WordPress.org account, with a Brevlo-domain email read by a person and 2FA on |
| Your role | Add your own account as a committer after approval, with 2FA. Support staff go in as Support Representatives, not committers. |
| Contributors header | The Brevlo username, exactly as cased |

## Packet checklist

| # | Item | Owner |
|---|---|---|
| 1 | Create the Brevlo WordPress.org account with a company-domain email and 2FA | Brevlo |
| 2 | Live Plugin URI, Author URI, terms and privacy pages | Brevlo |
| 3 | Plugin Check run. No error in the Plugin Repo category. Zip under 10 MB†, no dev folders. | You |
| 4 | Readme header: five tags at most, Tested up to the current major, short description of 150 characters or fewer | You |
| 5 | `Requires at least` and `Requires PHP` in the main file header | You |
| 6 | **External services** section naming Brevlo's API host, the data sent, the trigger (only after an admin connects an account), and terms and privacy links | You, with Brevlo legal for the links |
| 7 | Unique prefix of four or more characters, for example `brevlo_` | You |
| 8 | Scripts and styles through `wp_enqueue_*`, no inline script or style output | You |
| 9 | No telemetry or install ping before a default-off opt-in | You |
| 10 | "Powered by" links default off. Don't claim GDPR or ADA compliance. Say the plugin "assists with" them. | You |
| 11 | Built JS/CSS: ship source or link a public repo from the readme | You |
| 12 | Brevlo approves the final zip | Brevlo |

## Timeline

| When | Step |
|---|---|
| Today | Confirm the date and assumptions. Brevlo creates its account. Start the live pages. |
| Days 1 to 3 | Finish the packet and checks. Review Brevlo's pages. |
| Day 3 to 4 | Submit from the Brevlo account, as soon as the pages are live. |
| After submitting | Answer each review email in the same thread, fixing every point in one upload. |
| Conference | Announce "coming to WordPress.org" unless it is already approved. |
| After approval | Push real code promptly. An approved plugin with no code for 6 months† can be closed and its name reassigned. |

Plan for review rounds of about 10 business days† each, so approval most likely lands after the conference.

## After approval

1. **SVN:** Code goes in `trunk/`, each release is copied to `tags/<version>`, and images go in top-level `assets/`.
2. **CI deploys:** Use the account's separate SVN password, not the login password.
3. **Stable tag:** Set `Stable tag` to a real tag, never `trunk`.
4. **Security check:** Run Plugin Check, Security category included, before every tag.
5. **Release Confirmation:** Turn it on.
6. **Cooldown:** Every release waits about 6 hours† for an automated security review. A blocked version doesn't close the listing. Fix the findings and ship a new version.
7. **Support:** Support only the free plugin in the forums. Send paid-plan questions to Brevlo's own channel.
8. **Reviews:** Never ask for, pay for or seed reviews. Staff conduct can close the owner's plugins.

## The second plugin

Tell me the client's name, the plugin name, and what it does. I need two answers:

1. Is the name brand-first?
2. Is the client's account ready?

It follows the same rules. Note that your gmail account can host at most one plugin in review at a time, and only if the name isn't another company's brand.

## Questions for you

1. Which date is the conference: the 10th or the 14th?
2. Are Brevlo's paid features enforced by the API, or is anything locked in the plugin?
3. Can Brevlo create an account with a company email this week?
4. Who owns the live Plugin URI, terms and privacy pages, and by when?
5. Who is the second client, and is its plugin brand-named?

**Measures to watch:**
- Approval date.
- Connected sites as a share of active installs.
- Resolved-thread share in the support forum.

† Verify against the current developer.wordpress.org handbook and make.wordpress.org/plugins; the release process changes often.