ℹ️ I assumed this is the WordPress.org Plugin Directory review, since those three reasons are its standard wording. If it's a different marketplace, tell me and I'll adjust.

## Do this before sending

1. **Don't submit a new zip as a new submission.** Reply to the review email and attach the fixed zip, or upload it through the existing submission. A second submission makes a duplicate and can put you at the back of the queue. It also confuses the reviewer who already has your plugin context.
2. **Pick the new prefix first.** `ai_` is only 3 characters and is too generic. Use 4 to 5 characters or more, specific to your brand, such as `acmeinv_`. Apply it to every function, class, define, namespace, option, transient, hook name, post type, REST route, and global variable. Reviewers check all of these, not only functions.
3. **Document the external service in `readme.txt`** under a `== External services ==` section. For each service, state:
   - what it is and what the plugin uses it for
   - which data is sent, and when (on which action or schedule)
   - links to the service's Terms of Service and Privacy Policy
4. **Replace every inline `<script>` tag.** Move the code into a `.js` file loaded with `wp_enqueue_script()`. Pass PHP values with `wp_localize_script()` or `wp_add_inline_script()`.
5. ⚠️ **Fix the German readme.** The directory expects `readme.txt` in English. German belongs in translations through translate.wordpress.org, which fits your DACH customers. A German-only readme will probably be your next review round. Put the external-services section in English.
6. **Check for installed copies.** If any customers already run the old `ai_` options, add a one-time migration that copies the old option names to the new ones.

## Reply to send

**Subject:** Re: [Review feedback] Acme Inventory Sync – updated version attached

Hello,

Thank you for the review. We've addressed all three points and attached the updated zip to this email, so it stays in the same review thread. We have not opened a new submission.

**1. Undocumented use of a 3rd party / external service**
We added an "External services" section to `readme.txt`. For each service the plugin connects to, it now states:
- what the service is and why the plugin uses it
- exactly which data is sent and when it is sent
- links to the service's Terms of Service and Privacy Policy

We also checked the code for other outbound requests (`wp_remote_*`, cURL, and any scripts or assets loaded from remote hosts). All of them are now documented in the readme.

**2. Generic function/class/define/namespace/option names**
We replaced the `ai_` prefix with the longer, plugin-specific prefix `[NEW_PREFIX]_`. It now applies to all functions, classes, constants, namespaces, options, transients, hooks, REST routes, and global variables. We searched the whole codebase to confirm nothing generic is left, including in the uninstall routine. [If relevant: We also added a migration that moves existing `ai_` option values to the new names.]

**3. Inline `<script>` tags in the admin page**
We removed all inline `<script>` tags. The JavaScript now lives in separate files loaded with `wp_enqueue_script()` on the plugin's admin screens only. Dynamic values are passed with `wp_localize_script()` / `wp_add_inline_script()`.

**Additional change**
Our `readme.txt` was previously written in German for our DACH customers. We have rewritten it in English, as the directory requires. We will provide German through translate.wordpress.org.

Please let us know if anything else needs to change. We will respond quickly.

Kind regards,
[Name]
[Plugin contact email]

## Fill in before sending

- ❗ `[NEW_PREFIX]`: your chosen prefix.
- ❗ The service name(s), data sent, and ToS and privacy links, in the readme itself. The email only summarizes them.
- Remove the bracketed migration sentence if there are no existing installs.
- Attach the zip. Make sure its top-level folder matches the plugin slug.