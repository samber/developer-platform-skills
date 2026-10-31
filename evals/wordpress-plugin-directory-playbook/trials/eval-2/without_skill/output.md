# Brevlo Forms on WordPress.org: plan

## ⚠️ Two things to settle before you submit today

1. **Don't submit from your gmail.** The plugin will be Brevlo-branded, and WordPress.org guideline 17 reserves a brand-named slug (`brevlo-forms`) for the trademark owner or an authorized representative.
   - The review team will likely ask for proof of authorization.
   - They may want the submitting account's email on Brevlo's domain.
   - A gmail submission invites a "prove you represent Brevlo" round trip, and each round costs days you don't have.
   - Ownership handoff later is also painful. The slug and the plugin's committers are tied to the account. If you leave, Brevlo's plugin is stuck on a personal account.
   - **Fix:** ask Brevlo to create a company wordpress.org account with a `@brevlo.com` email. You then submit as a listed contributor, or log in with their delegated access. If that is impossible, get a signed authorization letter from Brevlo and attach it to the submission.
2. **Don't submit both plugins together from one account.** Check the current limit on pending submissions per account, because new accounts are capped.
   - Two client plugins on your personal account tie both clients' fates together. A flag on one stalls the other.
   - Submit Brevlo first, from the right account. Give the second client its own account too.
   - Both submissions can still go out today.

## ℹ️ Date check

You said "the 14th, 10 days away." Today is 2026-10-31, so 10 days away is **Nov 10**, and **Nov 14** is 14 days away. Which one is it? I planned against the tighter one (Nov 10).

## Reality check on the deadline

- Review time varies from days to weeks, and every fix round re-enters the queue. I can't verify the current queue from here. Check the Plugin Review Team's posts on make.wordpress.org/plugins for the current wait.
- Treat "live on WordPress.org by the conference" as a **target, not a promise**. Don't put "available on WordPress.org" in conference slides until the listing is public.
- **Plan B (build now):** a signed zip download on Brevlo's site or GitHub, plus a "submitted to WordPress.org" line. Swap in the directory link when approved.

## Blocker: the coming-soon site

The review team checks the plugin's external-service disclosure. Brevlo Forms calls Brevlo's API, so the readme must have an **External services** section naming:
- the service,
- what data is sent and when,
- links to Brevlo's **Terms of Service** and **Privacy Policy**.

Those links must resolve to real pages. Also, a Plugin URI / Author URI pointing at a coming-soon page looks unfinished.

**Ask Brevlo today** to publish three live pages, even if minimal: a plugin landing page, the ToS, and the privacy policy. Use the real URLs in the plugin header and readme.

## Timeline

| When | Action |
|---|---|
| **Today (Oct 31)** | Send Brevlo the account and authorization request, plus the three-page request. Run the pre-flight checks below. |
| Nov 1–2 | Get the Brevlo account or letter. Get live URLs. Submit the zip. |
| Nov 2–7 | Answer reviewer emails within hours, not days. Fix everything in one pass per round. |
| Nov 7 | **Decision point:** if not approved, switch to Plan B for the conference. |
| After approval | Push to SVN, add icons and banners, tag the stable release, and enable 2FA (required for committers). |

## Pre-flight checklist (do before submitting)

1. Install and run the **Plugin Check (PCP)** plugin on the zip. Fix all errors.
2. Validate `readme.txt` with the readme validator. It needs a correct `Stable tag`, `Tested up to` (latest WP), `Requires PHP`, a GPL-compatible license, and a text domain equal to the slug.
3. Security basics: sanitize input, escape output, use nonces and capability checks, and use no direct DB queries without `prepare()`.
4. No obfuscated code, no offloaded JS/CSS from third-party CDNs (bundle it), no hidden tracking, and no phone-home without opt-in and disclosure.
5. Unique function, class and option prefixes.
6. Brevlo trademark use is authorized in writing. The readme explains what the plugin does without implying you are Brevlo (if the account isn't theirs).
7. Short description is accurate, with no unverified claims and no spammy keyword stuffing.

## Handoff to Brevlo

- Use their company account from day one and you skip this step.
- If you must start on a personal account, add Brevlo staff as committers before approval. After approval, ask plugins@wordpress.org to transfer ownership. It's slow and not guaranteed on your timeline.
- Get a written agreement on who owns the code, who pays for ongoing maintenance, and who answers support-forum threads. WordPress.org expects responsive support.

## Questions for you

1. Is the conference Nov 10 or Nov 14?
2. Will Brevlo create a company wordpress.org account, or must you sign a letter instead?
3. Does the second client's plugin also carry a brand name, or is it generic? That decides whether it needs the same authorization.
4. Does Brevlo Forms send any user data to Brevlo's API by default? That shapes the disclosure text and the opt-in design.