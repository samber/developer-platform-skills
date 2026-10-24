# Webhook replay API: slip communication package

I read the `public-roadmap-strategy` skill and its references and applied them. I skipped its interview and wrote the package straight from your facts. Anything I assumed is in brackets, and the open questions are listed at the end.

## Your four steps need changing

Your four steps fail the skill's slip playbook. Here is what to do instead.

| Your step | Problem | Do this |
|---|---|---|
| 1. Remove the issue from the board | Deleting erases a record customers have already cited in deals and plans. Watchers notice, and it reads as a hidden broken promise. | Keep the item. Set its status to `delayed`, add a dated update, and move comments to one feedback thread. |
| 2. Newsletter mention | The renewal customer would learn about the slip in public. | Tell the two order-form customers privately first, then update the item, then use the newsletter as a follow-up. |
| 3. Status page "scheduled change" | A roadmap slip is not an incident or maintenance. The status page is for service state, and putting a slip there makes it look "official" while misusing the channel. | Don't post it there. The roadmap item is the official record. |
| 4. Re-add later as "Coming Q1!" | This reads as a silent re-issue with a new date. A bare quarter looks like GA to every buyer and rep. Engineering also said Q1 at the earliest, so it isn't a commitment you can print. | Don't publish a quarter now. Publish one only once the item reaches private preview, and print it with that phase. |

### What to do first: the order-form customers

A feature named in an order form is a binding deliverable, whatever the page disclaimer says. The slip may trigger notice, credit, or termination rights, and the renewal closes in six weeks, before the feature can ship.

1. **Today:** have legal read both order forms and tell you what the slip triggers (notice period, credits, termination, wording of the commitment).
2. **Also today:** ask finance whether a dated or specified replay commitment affects revenue recognition for either deal (ASC 606).
3. **Before any outreach:** decide the renewal posture with product. A deal that depends on an unbuilt feature is a product decision, not a rep's call. The choices are to keep replay as a contracted deliverable with an amended date, replace it with an interim remedy, or remove it from the order form.
4. **Then:** the account owner calls each customer, with the written note below as follow-up. Do this days before the public update.

## 1. Private note to the two order-form customers

**Hold this until legal approves it.** The bracketed items depend on what legal and product decide.

> **Subject: Update on webhook replay for [Customer]**
>
> Hi [Name],
>
> I'm writing before we share this publicly, because webhook replay is part of our agreement with you.
>
> **What changed.** The Webhook replay API will not ship in Q3. In load testing, replay traffic competed with live webhook delivery and slowed it down. We won't ship something that puts your live delivery at risk, so engineering is redesigning the delivery queue first so replay runs separately from live traffic.
>
> **What this means for you.** We now expect replay no earlier than [Q1]. That is an estimate, not a commitment, and we will update you as soon as the redesign has a firm milestone. [Legal/product to insert: what we are offering under the agreement, such as an amended delivery date, a credit, or an interim remedy.]
>
> **What you can use meanwhile.** [Workaround, for example: single-event resend from the dashboard, or a recipe using the events list endpoint. Confirm with engineering that it works for your volumes.] I'd like to set up a call with [engineering contact] to see whether it covers your recovery scenarios.
>
> **What would change this.** [Condition, for example: once replay runs on an isolated queue in private preview, we'd invite you to join it.]
>
> The public roadmap item will be updated on [date], so you'll hear this from me first. I'm available [times] to talk it through.
>
> [Name, role]

**Call talking points for the account owner**
- Lead with the news, then the reason, then what you're offering.
- Don't give a firm date, and don't say "Q1" without "no earlier than" and "estimate".
- Don't promise what legal hasn't approved.
- For the renewal customer, bring product into the conversation, not only the rep.

## 2. Public roadmap item update

Post this as a dated update on the existing item, after the private notes go out.

> **Webhook replay API** `[RM-ID]`
> **Status:** delayed (was: Q3). Now in design.
> **Timing:** none published.
>
> **Update [date]: Webhook replay API is delayed.**
> **What changed:** Load testing showed that replay traffic can starve live webhook delivery. We are redesigning the delivery queue so replay runs in isolation before we ship it.
> **What this means for you:** We are no longer targeting Q3. We will publish a timing once the redesign reaches private preview.
> **Workaround:** [e.g. resend individual events from the dashboard, or fetch missed events via the events endpoint.]
> **What would change this:** Replay running on an isolated queue in internal testing, at which point we will open a private preview.
> **Questions:** [link to one feedback thread]

Housekeeping:
- Move the item out of the "Q3" column into your delayed or in-design bucket.
- Lock comments on the item, and point everyone to the single feedback thread.
- Keep the item visible. If you add a disclaimer to the roadmap later, this item is covered by it.
- Notify watchers, subscribers, and anyone who saw the item in a briefing or deck. Check your sales and CS notes for those names.
- If other Q3 items sit in the same column, check whether they are at risk too. Don't bulk-reset the column.

## 3. Follow-up for the newsletter (after the public update)

> **Roadmap update: Webhook replay API**
> We've delayed the Webhook replay API. Load tests showed replay could slow live delivery, so we're redesigning the queue first. We'll share timing once it reaches private preview. In the meantime, [workaround]. Details and discussion: [link].

Keep it to this length, and link the item instead of repeating a date.

## 4. Internal note for sales, CS, and DevRel

> Webhook replay is delayed. Don't quote a date or "Q1". Say: "It's delayed while engineering redesigns the queue. The roadmap item has the current status and the workaround." If a deal depends on replay, escalate to product. Don't speculate about timing, and don't offer replay as a deal sweetener.

## Open questions

- **Order forms and counsel:** What exactly do the two order forms say? Does your MSA carry a "purchases not contingent on future functionality" clause? The order-form override beats it anyway.
- **Other exposure:** Did anyone else get promised replay in a deck, email, or briefing? Their names should go on the notification list.
- **Workaround:** What actually works today for replay? I used a placeholder because I don't know Orbiflow's product.
- **Timing:** I left the public timing blank because engineering only gave "Q1 at the earliest". Publish a quarter only when the item is in private preview.
- **Policy gap:** After this, write the roadmap policy and the sales citation rule so the next slip follows the same steps. That is a separate task.