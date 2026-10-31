# Linkwise HubSpot Marketplace listing: submission plan

I wrote this from memory of HubSpot's app listing process and haven't checked it against the current docs. I marked the items to verify on day 1. Don't commit to an approval date, because HubSpot's review is outside your control.

## Verdict

Submitting next week is feasible. Approval next week is not. Plan on weeks for review plus at least one round of fixes.

**One structural risk could sink the listing: a standalone Marketplace install.** Linkwise is white-label, so today every install starts inside a customer SaaS's UI. A HubSpot user who finds "Linkwise" in the Marketplace has no host app to connect to. Reviewers reject listings where install leads nowhere useful. Solve this on day 1 (see Decision 1).

## Decisions needed before Monday

1. **What does a Marketplace-initiated install do?**
   - **Option A (recommended):** the install lands on a Linkwise page. It lists the apps that embed Linkwise ("Connect HubSpot to X, Y, Z") and deep-links into each one. It also shows a clear "already installed via [partner]" state.
   - **Option B:** you position the listing as infrastructure ("powers HubSpot sync in the apps below"), with a partner directory and an install state that explains the next step.
   - Either way, the listing needs a working end-to-end install that a reviewer can complete with a test account.
2. **Branding conflict.**
   - The consent screen and the listing both say "Linkwise", while your customers sell the integration under their own names.
   - Check with your customers that a visible "Linkwise" brand on their users' consent screen is acceptable. Decide whether the listing names them.
   - Do not name customers publicly without their written OK.
3. **Is it one OAuth app or several?**
   - Install counts and reviews attach to one app ID.
   - If the 400 portals sit under one app, they count. If you use per-customer apps, only the app you list counts.
   - Changing the app ID or client ID would break existing tokens, so don't migrate anything for this listing.
4. **Who owns the listing?**
   - Name one owner, one support email and one escalation contact.
   - The owner needs an admin role on the HubSpot developer account that owns the app.

## Day 1: verify the facts

Open HubSpot's current "App Marketplace listing requirements" and the review checklist. Confirm each of these:

| Item | What to confirm |
|---|---|
| Install threshold | The minimum number of **active** installs (I recall 60), how "active" is defined, and the window. Query your own data: portals with API calls in the last 30 days, not 400 raw tokens. |
| Customer references | The number required, whether they must come from unrelated portals, and whether they must be reachable. |
| Account prerequisites | Developer account verification and any partner program requirements. |
| Submission mechanics | Who can submit, the required assets, and typical review time. |
| Certification | Whether a separate certification badge applies, and its extra thresholds. Defer it unless it's required. |

If the active-install count falls short of the threshold, stop. Don't submit.

## Day-by-day schedule

**Day 1 (Mon): decisions and verification**
- Settle Decisions 1-4.
- Pull the active-portal count and the list of eligible reference portals.
- Confirm the requirement list above.

**Day 2 (Tue): app hardening** (engineering)
- **Scopes:** compare requested scopes to what the connector uses. Move non-essential scopes to optional, and drop any you can't justify in one sentence each. Reviewers check least privilege.
- **OAuth flow:**
  - A fresh install from the Marketplace must work with no pre-existing state parameter from a host app.
  - The redirect URL must be stable, and the app must handle denial and re-install.
  - Token refresh must work.
- **Uninstall:**
  - Handle the uninstall event. Revoke tokens, stop syncs, and delete or anonymize HubSpot data on your stated schedule.
  - Document the retention period.
- **Rate limits:** handle 429 responses with backoff.
- Test on a clean developer test account with no prior state.

**Day 3 (Wed): legal and trust**
- Public privacy policy that covers HubSpot data, and public terms of service.
- A data processing agreement and a sub-processor list.
- A security page: hosting region, encryption in transit and at rest, access controls, and incident contact.
- A published support page with a support email and a response-time target.
- Check that none of this exposes internal hostnames or customer names.

**Day 4 (Thu): listing content**
- **Name:** "Linkwise" plus a short descriptor.
- **Tagline** and **long description:**
  - Lead with the user outcome: contacts, companies and deals sync both ways between HubSpot and the apps that embed Linkwise.
  - State exactly which HubSpot objects are read and written.
  - State what you don't do.
- **Assets:**
  - Logo meeting the size specs.
  - 3-5 screenshots of the real install and connect flow.
  - A short demo video if one is supported.
- **Setup instructions:** a numbered, tested install guide.
- **Documentation URL, support URL and pricing statement:**
  - The pricing statement must be accurate and say free to the HubSpot user.
  - If the host SaaS charges, say so.
- **Customer references:** contact 5-6 candidates to land the required number. Brief each one on what HubSpot may ask and get their written consent.

**Day 5 (Fri): dry run and submit**
- A teammate who hasn't seen the flow completes install, connect, sync and uninstall on a fresh test account while following only the published instructions.
- Fix what breaks.
- Give the reviewer test credentials plus a short walkthrough note. Provide a way to reach a working host app, because the reviewer can't test the connector without one.
- Submit only if the Day 1 threshold checks pass.

## Where reviews usually fail

- Scopes broader than the connector uses.
- An install that dead-ends without a host app.
- Missing or generic privacy and security documentation.
- Uninstall that leaves tokens or data behind.
- Setup docs that don't match the real flow.
- A reviewer who can't reproduce the sync.
- Branding or description that overstates what the app does.

## After submission

- Watch the support inbox daily. Reviewer questions have deadlines, and slow answers stall the review.
- Keep one engineer on call to fix review findings the same day.
- Don't change scopes or the redirect URL while the review is open.
- Tell your customers the listing is coming only after approval.

## Open questions for you

1. One OAuth app ID for all 400 portals, or several?
2. How many of the 400 had API activity in the last 30 days?
3. Do your customers agree to the Linkwise brand showing on the consent screen?
4. Which Option (A or B) do you want for the standalone install?
5. Which 5-6 customers can serve as references?

Once you answer 1, 2 and 4, I can turn this into a dated checklist, draft the listing copy, or write the reviewer walkthrough note.