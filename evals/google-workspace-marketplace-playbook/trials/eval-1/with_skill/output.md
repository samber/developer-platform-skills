# Quillpost Gmail add-on: Google verification, Marketplace and timeline

**Next action this week:** tell your eng lead the answer on scopes is no. Drop `gmail.readonly` and `gmail.modify`. Start with the non-sensitive scopes below, which make the 5-week launch realistic. Adding the two restricted scopes would put CASA (Google's paid security assessment) on your critical path, and it would likely miss the conference.

Figures marked † come from the playbook and Google changes them often. Re-check them on Google's current pages before you quote them to anyone.

## Assumptions

I couldn't ask, so each gap gets one assumption. Correct any that are wrong.

1. **Surface:** a Workspace add-on for Gmail (sidebar), with a Quillpost backend. It is not a Chrome extension and not a web app.
2. **Data:** Quillpost's servers receive the open email's content when a rep logs it. None of it goes to AI model training.
3. **Installers:** both Workspace admins (whole domains) and individual reps.
4. **Stage:** building, with nothing submitted to Google yet. Today is 2026-10-31, so launch is about **Fri 2026-12-04**.
5. **Cloud project ownership:** unknown. If it sits in one person's account, step 1 below is moving it into an organization.

## Why the two restricted scopes fail

- **Cost:** `gmail.readonly` and `gmail.modify` are restricted scopes. They bring OAuth verification that takes several weeks†. They also bring a paid third-party CASA assessment that Google assigns (AL1 or AL2†). Labs quote 2–6 weeks†, and the assessment renews every 12 months†.
- **No date control:** Google starts CASA by email, as the last verification step. You can't book it early.
- **Policy:** "everything we might need later" is a policy breach, not a convenience. Each scope needs a written reason a narrower scope fails, and you have none:
  - Logging an email never modifies the mailbox, so `gmail.modify` has no feature behind it.
  - `gmail.readonly` is whole-mailbox read. A rep logs the email they have open, which needs no more than that one message.
- **"Narrow later" doesn't work in reverse:** adding a restricted scope after launch is a new verification round. Users see the unverified-app screen until it passes, and domain-installed admins must re-authorize.
- **Fit if you want it later:** a CRM is a permitted restricted app type for Gmail. If you later want auto-logging of all mail, plan it as a v2 with its own CASA and date.

## Scope table

| Feature | Mechanism | Minimum scope | Tier | Justification |
|---|---|---|---|---|
| Log the open email to a deal | Rep clicks "Log to Quillpost" on the open message | `gmail.addons.current.message.action` | Non-sensitive | Lets "Log to Quillpost" read the open message when the rep clicks. Users see the email attached to the deal. Whole-mailbox read is not needed. |
| Templated follow-up | Button inserts a template draft into the compose window; rep reviews and sends | `gmail.addons.current.action.compose` | Non-sensitive | Lets "Follow-up" insert Quillpost's template into the reply the rep is writing. The app never sends on its own. |
| Identity and backend call | Sign-in to Quillpost, calls to your server | `openid`/email scopes and the Apps Script outbound-request scope (`script.external_request`) | Check tier† | Required because the add-on calls your backend. |

The top row is the one to check first. Confirm on Google's scope page that `message.action` exposes the message body to your add-on.

**Fallbacks, only if a feature demands them:**
- If `message.action` doesn't cover what logging needs, use `gmail.addons.current.message.readonly`. It is **sensitive**: verification takes up to 10 days†, with no CASA.
- If product insists on one-click send without a compose window, use `gmail.send`. It is also **sensitive** (same up to 10 days†). Don't take `gmail.compose`, which is restricted.

**Ladder rung chosen:** non-sensitive and contextual, the cheapest rung. Result: brand verification only, with no CASA.

## Listing verdict

- **Public listing, Individual + Admin install.** This is the default. It gives admin domain-wide install without per-user consent, plus self-serve discovery.
- **No private listing.** Private listings serve only your own organization, never customers. Visibility is permanent once saved.
- **Pilots:** testing status reaches customers only through your web app's own OAuth flow, and draft testers must be Gmail accounts. Customer-company users get the add-on only after public approval, so you can't pilot it with Workspace customers first. Use internal and Gmail test accounts.
- **Billing:** Google bills nothing. You are the seller. Show the total price and renewal terms in the listing.
- **Featuring:** it can't be bought.

## Dated plan (launch backward, one rejection round)

The Marketplace review is the long pole. The playbook's 2–4 weeks† is for sensitive scopes and practitioner-reported. Google itself says "several days". With the non-sensitive set, I'd still plan on the slow end. Verification and the Marketplace listing run in parallel, but the listing can't be approved before verification completes.

| When | What | Owner |
|---|---|---|
| **Nov 2–6** | Freeze the scope table with eng lead. Move the Cloud project into an organization with 2 owners and billing on. Verify the domain in Search Console. Publish a privacy policy with the Limited Use statement, using the same URL on the homepage and the consent screen. Submit brand verification. | Eng lead, ops |
| **Nov 9–13** | Brand verification passes. Publish branding within 7 days†. Declare the same scopes in code, the Marketplace SDK and the consent screen. Configure the Marketplace SDK (not the Marketplace API), install setting and a deliverable developer email. Build the listing (name ≤50 characters†, "for Gmail™" form with trademark attribution). Create a reviewer test account with sample data and steps. Handle partial scope grants. | Eng, product |
| **Fri Nov 13** | **Submit for Marketplace review. Hard decision point.** Later than Nov 16 means the launch date is at risk. | Product |
| **Nov 16–27** | Review. Answer Trust & Safety mail the same day, because the review pauses until you reply. Plan for one rejection: fix every point in the review document, then resubmit once. | Eng lead |
| **Fri Nov 27** | Latest resubmission. | Eng lead |
| **Nov 30–Dec 4** | Buffer and approval. Publish admin docs (OAuth client ID, scopes, install steps, Trusted setting). Record launch assets. | Marketing |
| **Fri Dec 4** | Launch, if approved. | All |

If approval hasn't landed by about Dec 1, launch the conference demo and the Quillpost web-app side, and announce the add-on as "rolling out". Don't promise a specific install date on stage.

## Verification packet owners

Most of this is needed for the listing and reviewers even though the non-sensitive set needs no data-access request. If you move to a sensitive scope, you also owe the justification and demo video below.

- **Privacy policy and Limited Use statement:** legal or ops. Google Workspace data is for user-facing features only, with no ads, no human reading without consent for specific data, and no model training.
- **In-app disclosure** right before consent, and help docs on data deletion: eng and product.
- **Justifications**, in the playbook template "`<scope>` lets `<feature>` `<action>`. Users `<see>`. `<narrower>` cannot work because...": product.
- **Demo video** (only if a sensitive scope is added): unlisted YouTube, English consent screen, address bar showing the OAuth client ID, one segment per scope.
- **Reviewer access:** test account, sample data, steps to every scoped feature.
- **Workspace add-on pre-check:** homepage card, a welcome card that names Quillpost as a third party, and working Sign out and Support actions.

## After launch

- A new Marketplace integration type, host app, or App Details field (name, description) means a new Marketplace review. Graphics and links publish from a draft.
- A new sensitive or restricted scope means new OAuth verification before release. Domain-installed customers' admins must then authorize it. Tell each admin in advance.
- CASA does not apply unless you add a restricted scope.

## Decisions for you

1. Confirm the non-sensitive scope set (log via `message.action`, follow-up as a compose draft). Say if product needs direct send, which adds a sensitive scope.
2. Who owns the Google Cloud project today? That sets how much of the first week goes on step 1.
3. Is "rolling out" acceptable on stage if approval slips past Dec 1?