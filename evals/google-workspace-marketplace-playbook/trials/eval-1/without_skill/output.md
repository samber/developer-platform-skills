# Quillpost Gmail add-on: Google-side plan

**Caveat:** WebFetch was denied, so I couldn't check Google's docs live. Everything below comes from memory. Two things need a 15-minute check before you commit to dates:
- The scope classification table for the `gmail.addons.*` scopes.
- Current verification and CASA turnaround.

## 1. Recommendation: do not request `gmail.readonly` or `gmail.modify`

- **Both are restricted scopes.** Restricted scopes trigger OAuth verification plus a CASA security assessment. Because Quillpost stores email on its own servers, CASA applies, and it repeats every year.
- **"Everything we might need later" is a likely rejection reason.** Google requires the minimum scopes for features that exist today. Reviewers reject over-broad requests and ask you to justify each scope in the verification form and demo video.
- **Nothing in your feature set needs `gmail.modify`.** Logging an email and starting a follow-up need no mailbox write access.
- **Adding scopes later is possible but costs a re-review.** Each new scope means another verification pass and a re-consent prompt for every installed user.

## 2. Scopes that cover the stated features

Gmail add-ons have per-interaction scopes that expose only the email the rep has open. They do not expose the whole mailbox.

| Feature | Scope | Notes |
|---|---|---|
| Add-on runs in Gmail | `gmail.addons.execute` | Required |
| Read the open email to log it | `gmail.addons.current.message.readonly` | Current message only, via a short-lived token. Use `...message.metadata` if you only need subject, sender and recipients. |
| Templated follow-up | `gmail.addons.current.action.compose` | Fills a draft or reply window and the rep clicks Send. |
| Identify the rep to Quillpost | `openid`, `email`, `profile` | Non-sensitive |
| Apps Script runtime only | `script.external_request` | Needed to call your API |

- **Send behaviour:** the compose scope opens a prefilled draft for the rep to review and send. Sending silently from the sidebar needs `gmail.send`, which is sensitive and adds review time. I'd pitch the draft flow as a feature: reps see what goes out.
- **Open check #1:** I believe `message.action` and `action.compose` are non-sensitive. I'm not sure how Google classifies `message.readonly` and `message.metadata`. If `message.readonly` is restricted, CASA is back on your critical path even with the narrow scope. This is the biggest schedule driver.
- **Fallback:** if the read scope is restricted and the schedule can't absorb CASA, launch with `message.metadata` only. Reps would log subject, sender, recipients and date, plus a note they type or paste. Add body capture in v1.1 after CASA.

## 3. What Google requires, in order

1. **Standard GCP project.** Apps Script's default project can't be published. Create a dedicated project owned by a company account, not an individual's.
2. **Verified domain.** Verify `quillpost.*` in Search Console. The homepage, privacy policy and ToS must live on that domain.
3. **OAuth consent screen and brand verification.** Set the app name, logo, support email and authorized domains. Brand verification typically takes a few business days.
4. **Privacy policy.** It must disclose Google data access, use, storage, retention and deletion. You must comply with the **Google API Services User Data Policy, Limited Use**:
   - No ads.
   - No sale of data.
   - No training generalized AI models on Gmail data.
   - No human reading of email content except with consent, for security, or as legally required.
   - Check this against any "AI summary" ideas on your roadmap.
5. **OAuth verification.** Required for any sensitive or restricted scope on a public app. Submit:
   - Per-scope justification.
   - A demo video showing the full consent flow and each scope in use.
   - Test credentials.
6. **CASA Tier 2.** Only if a restricted scope is in play.
   - You pick an Google-authorized assessor lab, run the scan, remediate findings, and receive a Letter of Validation.
   - You submit it to Google, and it must be renewed annually.
   - Expect roughly four weeks end to end, and a fee in the low-thousands USD range. Both figures are from memory.
   - Your server security and data-handling controls are what get tested.
7. **Google Workspace Marketplace SDK listing.**
   - Enable the Marketplace SDK in the same project.
   - Complete the app configuration and link the add-on deployment.
   - Add the store listing: icons, screenshots, description, support URL, privacy policy and ToS links.
   - Choose visibility and submit for Marketplace review.
8. **Apps Script only:** declare `urlFetchWhitelist` for your API hosts. Using an HTTP runtime backed by your own service avoids this.

## 4. Timeline against the 5-week pin

Google's turnarounds are not SLAs. Plan for one rejection round on each review.

| Week | Track A: build | Track B: Google paperwork |
|---|---|---|
| 1 | Cards for message context, deal picker, log action, template picker | Standard GCP project, domain verification, privacy policy and ToS update, consent screen, brand verification submitted. Decide scopes (open check #1). |
| 2 | End-to-end flow in a test deployment | **Record the demo video. Submit OAuth verification and Marketplace listing by end of week 2.** If CASA applies, book the lab this week. |
| 3 | Fix bugs, polish; build the answers to expected reviewer questions | Respond to reviewer feedback within 24 hours |
| 4 | Harden, load-test, prepare the conference demo | Second review round. If CASA applies, remediation and Letter of Validation submitted. |
| 5 | Conference | Listing live if approved; otherwise use the fallback below |

- **Narrow scopes, no restricted scope:** feasible in 5 weeks if you submit by end of week 2. Slack is about 2 to 3 weeks for rejection cycles.
- **Restricted scope plus CASA:** not safely feasible. Even a clean run puts approval at the edge of the conference date, and a single failed round misses it.
- **Do not let the date drive the scope.** An over-broad request fails and costs more calendar time than a narrow one.

## 5. Conference fallback if the public listing isn't live

- **Private or internal publishing:** a Marketplace listing limited to your own domain needs no public review. Reps and the booth demo run on it.
- **Test users:** an unverified app in testing mode is capped at 100 test users and shows a warning screen. Use it for design-partner customers, with a warning to them.
- **Domain install:** customer Workspace admins can install a private app for their domain.
- **Messaging:** announce "available now to early-access customers, Marketplace listing pending" rather than promising a live listing.

## 6. Decisions for your eng lead and you

1. Does logging need the email body, or is metadata plus a rep note enough for v1? This sets the restricted-scope question.
2. Draft-and-review follow-up, or direct send? Direct send adds `gmail.send` and review time.
3. Who owns the GCP project and the Google support contact? Use a role mailbox so verification emails don't get lost.
4. Will any roadmap feature use Gmail content for AI? If so, it needs a Limited Use review before anything ships.
5. Where is email content stored, for how long, and how is it deleted when a rep disconnects? The verification form and the privacy policy both ask.

## 7. Actions today

1. Confirm the `gmail.addons.current.message.readonly` classification in Google's Gmail scope table. This decides whether CASA is in scope.
2. Reply to your eng lead with section 1: narrow scopes now, restricted scopes only as a planned v2 with its own CASA budget.
3. Create the GCP project and start domain and brand verification. Neither depends on any other decision.