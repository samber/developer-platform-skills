# Reply to the Plugins Team, plus what to tell your dev

## Don't submit a new zip as a fresh submission

Reply in the same "Review in Progress" email thread, and upload the fixed zip on the submission page first. A new submission doesn't restart anything cleanly. It drops the review history, and only one plugin can be in review per account. The first review email isn't a rejection. Plugins usually need several rounds. A review still incomplete after 3 months† is rejected, and then you resubmit.

## Fix list for your dev (before sending)

1. **External service.** Add a `== External services ==` section to `readme.txt`.
   - Cover every host the plugin calls, your own Acme API included. Run a search for `wp_remote_*`, `curl`, `file_get_contents(http`, and `fetch(`/`XMLHttpRequest` in JS.
   - For each host, state what it is, which data is sent, and when (the trigger).
   - Add terms and privacy links that are live.
2. **Prefix.** `ai_` is only 2 letters. The rule is a unique prefix of 4 or more characters†, and `ai_` is also generic.
   - Pick something unique, such as `acmeinvsync_` (functions, `AcmeInvSync_` for classes, `ACMEINVSYNC_` for constants).
   - Apply it to every function, class, namespace, define, option, transient, hook, and script handle.
   - Write a migration for existing option names if any site already stores `ai_*` options.
3. **Inline `<script>`.** Move the code into a `.js` file in the plugin. Load it with `wp_enqueue_script()` from `admin_enqueue_scripts`, only on your settings screen. Pass small bits of PHP data with `wp_add_inline_script()` or `wp_localize_script()`, not raw `<script>` output. Do the same for any inline `<style>`, which the reviewer will flag next.
4. **Readme language.** Not flagged yet, but the readme must be in English. Translations come from translate.wordpress.org, not from a German `readme.txt`.
   - Make `readme.txt` English.
   - Make sure the plugin's strings are translatable and use the text domain that equals the slug.
   - Your DACH customers get German through the translation project. Contributors can be invited there, and you can write German docs on your own site.
5. **Version.** Bump `Version` in the main file to 1.0.1 (assumed) and `Stable tag` in the readme.
6. **Run Plugin Check** and fix any error in the Plugin Repo category before uploading. Reviewers re-run it.

## Text to send

> Subject: Re: [Review in Progress] Acme Inventory Sync
>
> Hello,
>
> Thank you for the review. Version 1.0.1 is uploaded on the submission page and addresses each point:
>
> 1. **Undocumented external service:** the readme now has an "External services" section. It names each service the plugin calls (`<api.acme.example>`), the data sent (`<fields, e.g. inventory items, site URL>`), when it is sent (`<only after an administrator connects an Acme account>`), and links to the terms of use and privacy policy.
> 2. **Generic names:** the `ai_` prefix is replaced by `<acmeinvsync_>` across functions, classes, defines, options, transients, hooks and script handles. Existing `ai_*` options are migrated on update.
> 3. **Inline scripts:** the admin page's inline `<script>` code is moved into `<assets/admin.js>`, loaded with `wp_enqueue_script()` on our settings screen only. Small amounts of PHP data are passed with `wp_add_inline_script()`.
>
> We also converted the readme to English, since translations come from translate.wordpress.org. We re-checked the whole plugin for other inline scripts and styles and for other outbound calls, and found `<none / list them>`. Plugin Check passes with no errors in the Plugin Repo category.
>
> Kind regards,
> `<Name>`, Acme `<role>`

## Before you send

- **Fill the angle-bracket placeholders.** I don't know the service host, the data sent, the new prefix, or the file names, so the reply states them as blanks. Don't send guesses. Make sure each claim is true in the uploaded zip.
- **Check the audit result.** If the "none / list them" sentence isn't true, list the extra services in the readme and the reply.
- **Plugin name.** "Acme Inventory Sync" starts with your brand, which is fine only if the plugin is submitted from the company's own WordPress.org account with a company-domain email. If it came from an agency or personal account, say so in this reply and ask the team to move it. Don't resubmit.
- **Next steps.** Expect a reply in about 10 business days†. Another round is likely, so don't promise a launch date. If approval misses it, announce "coming to WordPress.org".

Measure to watch: approval date, then connected sites as a share of active installs, and the resolved-thread share.

† Verify against the current developer.wordpress.org handbook and make.wordpress.org/plugins; the release process changes often.