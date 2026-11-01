# Brightslot and the Google Workspace Marketplace

## Verdict

**No, Brightslot does not need a listing.** Do the OAuth app verification, and skip the Marketplace for now.

Both other asks are no:
- **Billing through the Marketplace:** not possible. Google bills nothing, and you stay the seller.
- **Paying for Editor's Choice:** not possible. Featuring cannot be bought, and Brightslot doesn't qualify anyway.

## Assumptions (please confirm)

1. **Surface:** Brightslot is a web app that calls the Google Calendar API through its own OAuth flow. It has no Workspace add-on, Chat app, or Gmail or Drive surface inside Google.
2. **Data:** Calendar data (events and free/busy) reaches your servers. None of it goes into AI model training.
3. **Buyers:** Customers sign up themselves, and their admins sometimes need to approve the integration.
4. **Cloud project:** I don't know who owns the Google Cloud project. If it's one person's account, moving it into an organization with two owners is step one.
5. **Dates:** There is no launch date. The plan below is relative.

Figures marked † change over time. Check them against Google's current docs before quoting them.

## 1. Do you need a listing?

A listing earns its cost when you want one of three things: an install surface inside Google's apps, admin install without a per-user consent prompt, or self-serve discovery on the Marketplace. Brightslot's integration is a button in your own web app, so you want none of these.

| Option | What it gives you | Verdict for Brightslot |
|---|---|---|
| **A. Verified OAuth client, no listing** | Removes the "Google hasn't verified this app" screen. Each user still consents. | **Do this now.** |
| B. Public listing, Individual + Admin install | Admin install without per-user consent, plus Marketplace discovery. | Not now. It adds Marketplace review on top of verification. |
| C. Public listing, Admin Only | Works only when domain-installed. | No. |

The 100-user cap is the real deadline. An app showing sensitive scopes while unverified is capped at 100 users† over its lifetime, with no reset. Verification, not the listing, removes that cap.

## 2. Scope table

Verification cost depends on the scope tier. Most Calendar scopes are sensitive, which means verification takes up to 10 days† and needs no CASA assessment. Check each scope's tier on its API scope page.

| Feature | API method | Minimum scope | Tier |
|---|---|---|---|
| Show availability | `freebusy.query` | `calendar.freebusy`, or a narrower or readonly variant | Check the scope page |
| Read events to avoid double-booking | `events.list` | `calendar.events.readonly` | Sensitive |
| Create the booking event | `events.insert` | `calendar.events` | Sensitive |

Rules for the table:
- Request only scopes your shipped features call, with a written reason why a narrower scope fails.
- Use the `.readonly` variant wherever a feature never writes.
- Declare the identical scope list in three places: your code, the consent screen (Data Access), and, only if you list later, the Marketplace SDK. Any drift shows users the unverified-app screen or a second prompt.
- Do not ask for "future" scopes.

Brightslot's data is under Limited Use. In practice:
- Use Calendar data only for user-facing features.
- Show no ads against it.
- Allow no human reading without the user's consent.
- Use none of it to train models.
- Show an in-app disclosure right before the consent request.

## 3. Plan: verification without a listing

Allow roughly 2 to 4 weeks†, including one rejection round. Run steps 2 and 3 in parallel.

1. **Cloud project.** Put it inside an organization with two owners and billing enabled. Reuse the project that holds the production OAuth client. Delete any OAuth clients that aren't production-ready.
2. **Brand verification.**
   - The homepage describes the app (not only a login page) and links the privacy policy.
   - The domain is verified in Search Console.
   - The same privacy URL is on the homepage and the consent screen.
   - Publish branding within 7 days† of passing.
3. **Data access request** in the Verification Center. It needs:
   - The scope list, with a justification per scope.
   - Up to three doc links.
   - An unlisted YouTube demo video, with an English consent screen and the OAuth client ID visible in the address bar. It shows the full grant flow, then one segment per sensitive scope showing the feature using it.
4. **Privacy policy.** It must say how you access, use, store, and share Google data, and carry the Limited Use statement: "The use of information received from Google Workspace scopes will adhere to the Google User Data Policy, including the Limited Use requirements."
5. **In-app disclosure and help docs.** The disclosure appears right before consent. The help docs explain how users delete their data.
6. **Granular consent.** Users may grant only some scopes. Detect missing ones and re-prompt per feature instead of breaking.
7. **Switch the consent screen to "In production"** before you submit. Testing status limits you to named test users.
8. **Answer Trust & Safety email fast.** The review pauses until you reply.

Justification pattern, using Brightslot's own scopes:

```
calendar.events lets "Confirm booking" create the meeting on the host's calendar. Users click
Confirm and see the event in Google Calendar. calendar.events.readonly cannot work because the
app must write the new event.
```

Owner assignments (placeholders for you to fill in): Cloud project and domain (platform or IT), privacy policy and Limited Use text (legal or product), demo video (product or QA), justifications (engineering).

## 4. Admin-facing doc

Enterprise admins who restrict third-party access will ask for your client ID. Publish this in your help center:

```
OAuth client ID: <id>.apps.googleusercontent.com
Scopes: <one line each, with the feature that needs it>
Restricted services: mark the client ID Trusted under Security > API controls.
```

Verification does not replace admin approval. In orgs that block unconfigured apps, the admin still has to mark the client ID Trusted. A listing doesn't change that for a web-app integration, but a listed app can be admin-installed.

## 5. Marketplace billing

Google Workspace Marketplace does not bill customers. You are the seller, and you collect payment through your own billing stack. If you ever list, the listing must state:
- That you are the seller.
- The total price, with mandatory fees included.
- How usage pricing is calculated.
- The renewal terms.
- The UK 14-day cancellation right for subscriptions.

A listing therefore adds no billing, and there is nothing to route through Google.

## 6. Editor's Choice

Featuring cannot be bought, so there is nothing to pay for. The gates are:

- Editor's Choice requires:
  - A Workspace add-on.
  - Individual installability.
  - Free or free trial pricing.
  - 100,000 installs†, or 10,000 installs and a rating of 4 or above if published in the last 6 months†.
- The security badge requires CASA AL2†.
- "Recommended for Google Workspace" is a yearly application.

Brightslot has no add-on, so it can't qualify today. Even with one, 100,000 installs† is far off.

## 7. What marketing can do instead

You can get most of the discoverability goal without a listing:
- Publish an "Integrations → Google Calendar" page on your site.
- Add the integration to SEO and AI-search content.
- Put a Brightslot link in your own docs for admins.

## 8. When a listing becomes worth it

Revisit if one of these happens:
- Enterprise prospects demand admin domain-wide install with no user consent prompt.
- You build a Calendar or Gmail add-on, so users can book from inside Google.
- Marketplace search shows real demand for scheduling add-ons.

At that point you add the listing on top of the verification you've already passed. Cost: a Marketplace review round, plus work on the listing and the Marketplace SDK configuration. Two things to know before you decide:
- Visibility (public or private) is permanent once saved. Private listings only reach your own organization, never customers.
- Choose Individual + Admin install by default.

Most of the cost is in verification, which you pay anyway.

## Decisions for you

1. **Confirm the assumptions**, especially that Brightslot has no in-Google surface.
2. **Pick the minimum scopes** your features need. If any feature needs a restricted scope, it triggers CASA and weeks of review. Tell me so I can re-rank the plan.
3. **Name the Cloud project owners.**