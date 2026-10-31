# Shiftlane Teams submission: fix list, order, and timeline

**Verdict:** the code fixes take about one day. The 10-day launch date depends on two things you don't control: the attestation blocker and the length of Microsoft's review cycle. Tell marketing today that the date is conditional.

I didn't check Microsoft's current review times or attestation rules. Confirm them in Partner Center and against the validation report text.

## Fix order

### 1. Today: decide the name (30 minutes, blocks everything else)

You have three names: `Shiftlane` (manifest), `Shiftlane for Teams` (Partner Center), and `Shifts` (some listing places).

- **Pick one canonical name.** I recommend `Shiftlane`. It's your brand and already in the manifest.
- **Drop `Shifts` everywhere.** "Shifts" is also the name of Microsoft's own first-party Teams app. A listing named that invites a name-confusion or impersonation rejection, which would be a new finding on round 3.
- **Sweep every surface for the final name:**
  - manifest `name.short` and `name.full`
  - Partner Center listing title
  - listing description and screenshots
  - icons and bot display name
  - help-response text
  - website and support pages
- **Check the Partner Center alias.** If the name Partner Center shows can't be edited, change the manifest to match it instead. Either way, use one name.

### 2. Today: open the attestation ticket in parallel

It has the longest and least controllable lead time, so start it first.

- **Send exact details to Partner Center support.** Include the screenshot or error text, the offer ID, and the validation report ID.
- **Check these first, since each commonly blocks completion:**
  - Your account role isn't Owner or Manager.
  - A prerequisite listing section is incomplete (privacy URL, terms URL, support contact).
  - The form is tied to the wrong account or tenant.
  - It's a UI error, which a different browser or session might clear.
- **Reply to the validation email too**, citing the same report ID.

I can't say why your form refuses completion without the actual error.

### 3. Day 1: one package rebuild fixing everything

Make one rebuild, one version bump, and one resubmission.

- **Domains:**
  - Remove `staging.shiftlane.io` from `validDomains`.
  - Grep the manifest for it elsewhere: `contentUrl`, `configurationUrl`, `webApplicationInfo`, and any bot or messaging endpoint.
  - Move staging to a separate dev manifest with its own app ID, so it never ships in the store package.
- **Name:** apply the decision from step 1.
- **Bot "does not respond to Help":**
  - Handle `help` case-insensitively in every scope you declare (personal, team, group chat).
  - Add `help` to the manifest `commandLists`.
  - Make the reply useful: what the app does, how to start, and a support link.
  - Confirm the production bot endpoint is live and answers fast, not through a cold start that times out.
  - Verify the Azure Bot registration points at the production endpoint, not staging.
- **Retest on production** with a fresh account, ideally from a tenant other than your own. Test every scope and type "help", "Help" and "HELP".
- **Bump the manifest version.**

### 4. Day 2: self-validate, then submit

- **Run the Teams app validation tool** from Developer Portal or the Teams Toolkit before uploading.
- **Re-read the full validation report line by line** and tick off each item. Reviewers often surface new issues each round.
- **Submit as soon as attestation clears.** If it's still stuck, submit anyway if Partner Center allows it, and note the open ticket.

## Is 10 days realistic?

| Scenario | What has to be true | Launch |
|---|---|---|
| Best case | Attestation unblocked by day 2–3, resubmitted by day 3, passes with no new findings, review takes about a week | Day ~10, with no slack |
| Likely | Attestation takes several days, or a round-3 finding appears | Day 14–21 |
| Bad | Attestation needs escalation, plus another failed round | Beyond 3 weeks |

A fourth failed report would restart the clock. Approval is also not the same as live: allow a day or two before the listing is visible.

## What to tell marketing today

1. **Don't announce a public date until Microsoft approves.** Say "launch within 2 days of approval."
2. **Have a fallback.** Early customers can use the app now via admin-uploaded custom apps, which skips the store review. That makes a "available to customers on day 10" announcement possible even if the store listing lags.
3. **Share a weekly checkpoint:** attestation status, submission date, review status.

## Questions that would sharpen this

1. What exact message does the attestation form show when it blocks you?
2. Is the Partner Center name editable, or locked to the original alias?
3. Does the bot answer "help" in all scopes you declare, or only in 1:1 chat?