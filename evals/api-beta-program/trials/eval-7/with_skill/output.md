**Change all 8.** Rules 1, 2, 3 and 8 are the risky ones. Fix those first.

## Change first

**8. 2M tile requests/day on live keys, "left alone".** Change this one first.
- Silence is the one option the skill rules out. Production detection must trigger a conversation, never nothing.
- The terms say "no production use" and one partner is doing it anyway, so nobody knows what you promised them.
- Talk to the partner this week and pick one:
  - **Signed production exception.** It names the account and the surface, and it sets a longer notice period. This traffic then counts toward the GA criterion "production traffic on the final shape".
  - **Move them to test or sandbox keys.** Do this only if they agree.
- Check concentration too. With 7 partners, no partner should carry more than about a third of beta traffic. At 2M/day, this one may be well over.
- Production use also lengthens the notice you owe them for breaking changes, so tell them privately before any change that touches their calls.

**2. "Field renames aren't breaking in beta."** Drop it.
- The skill says never invent a beta-only definition. Use the company's breaking-change definition from `api-versioning-policy`.
- A rename breaks the partner's parser. Calling it non-breaking in the terms doesn't change that. The first angry partner will hold you to the plain meaning.
- What beta changes is the permission, not the definition. Breaking changes are allowed, but never silent.
  - **Private preview (style-editor):** direct notice to every enrolled technical owner before the change ships.
  - **Public preview (vector tiles):** see rule 3.

**1. "Freeze both APIs like GA."** Drop it.
- A frozen beta removes the reason for a beta. Partners are there to change the shape before it hardens.
- Freeze later, on a fixed date. Set a contract-freeze date at least one partner release cycle before the exit review. After that date no changes ship, and partners migrate onto the frozen shape before GA.
- Partners feel safe from rules 2 and 3 (notice, changelog, a published notice rule), not from a freeze.

**3. "Push changes straight into the current preview, announce on social."** Change both parts.
- Batch breaking changes into a new preview version. Don't mutate the current one.
- Publish a notice rule for public preview. Vendors range from zero notice to a 90-day availability floor (Azure) to a recommended 180 days (Google AIP-185). I'd pick a floor for the old version, for example 90 days. It's your call.
- Social posts are not notice. The channel of record is the changelog plus a notice to subscribers. Social can echo it.
- Mark the stage on the wire, for example a `v1-preview` version or path, so nobody mistakes it for GA.

## Change next

**5. "No changelog for the private preview."** Write one. Every change gets an entry, and a private changelog is fine. Without it you can't prove you gave notice, and the silent-change metric (target zero) is unmeasurable.

**6. "Slack channel monitored by the team, nobody in particular."**
- Name one owner and a response time, for example one business day. A channel nobody owns teaches partners to stop reporting.
- Add biweekly office hours and a kickoff call for the private preview.
- The skill also rules out any program with no named owner, because an ownerless beta becomes a perpetual one.

**7. "Activated = everyone granted access".** That is the enrolled count.
- Activated means one defined event per account, for example the first successful production-shaped call.
- Report activated over enrolled.
- With 7 partners, state the floor as an absolute count, for example "at least 4 of 7 by the review date".
- Define the event before enrollment opens.

## Change partially

**4. "Halden asked for five features, all on the sprint."** Don't commit all five.
- One partner's request is a data point, not an order.
- Ship a feature when it recurs across partners or matches the problem statement.
- Five asks from one partner can fill the backlog. That is custom development.
- Check the other six partners for each ask. Tell Halden which ones you're taking and why, and log the rest.

## Not on your list, but missing

1. **Exit date.** A dated review for each beta, derived backward from the GA target. Past 12 months counts as a perpetual beta.
2. **Exit criteria.** GA criteria and kill criteria, written before more accounts enroll.
3. **Stage contract.** One row per stage covering SLA, support, breaking changes, data, pricing and discontinuation. The public preview needs it too.
4. **Flag expiry.** It alerts the owner on the exit date and never disables access.
5. **Extension rule.** One extension, at most half the original time box.

## Next action

Pull last week's request logs for the 2M/day account and list the operations it calls. That takes about 15 minutes and gives you the facts for the call about rule 8.

If you want the stage contract and exit criteria drafted, tell me the GA target date and the program owner's name. A first pass takes about an hour.