# Briefly "catch me up": what the Friday plan is missing

**Verdict:** the plan breaks the listing. Don't change the install URL or email customers until Slack has approved the new scope. Deploying the code on Friday is fine if the feature stays dark.

I made these assumptions because I couldn't ask:
- **Public channels only:** "channels the bot is in" could also include private channels and DMs, which need different scopes (see the scope table).
- **User-triggered:** a user invokes catch-up (slash command or shortcut). It isn't a scheduled digest.
- **No stored messages:** you fetch the last day of messages when the user asks.
- **No Enterprise Grid or Slack Connect customers:** if you have them, test both before submitting.
- **No fixed launch date:** if one is pinned, tell me, because the timeline section is built backward from it.

## 1. Changing the live install URL fails

The live app is locked. New scopes go through a resubmission, and an unreviewed scope in the live install URL makes installs fail for everyone, not only for catch-up users. Slack also delists without notice for a substantial change shipped without review.

- Don't add `channels:history` to the production install URL.
- Don't edit app settings by hand. Apply the change through your manifest.
- Deploy the code behind a feature flag, off for everyone.
- Send the reinstall email only after approval. The order is: approval, update the OAuth URL, then ask existing workspaces to reinstall (App Home plus a message).

## 2. Friday isn't possible

This resubmission adds a feature and a scope, so it needs a video and a staging app, and Slack reviews it at enhanced depth.

| Stage | Duration† |
|---|---|
| Preliminary review | up to 10 business days |
| Functional review | up to 6 weeks for an update |
| One returned round | count it as another preliminary cycle |

- **Realistic window:** about 8 weeks or more from submission, and review can't be expedited.
- **Resubmissions:** a resubmission in preliminary resets your queue position, so fix all feedback in one pass. In functional review you keep your place.
- **Announcing it:** say "coming soon" and publish on the day you choose after approval. Don't point customers at an unreviewed build.

## 3. Scope table

`*:history` scopes get enhanced review. Slack rarely approves broad history access, so the justification has to describe on-demand use and nothing else.

| Scope | Token | Methods | Feature | Required or optional | Enhanced review |
|---|---|---|---|---|---|
| `channels:history` | bot | `conversations.history`, `conversations.replies` | Reads the last 24h of a public channel when a user asks for a catch-up | **Optional** (`bot_optional`) | Yes |
| `groups:history` | bot | same | Only if private channels are in scope | Optional | Yes |
| `im:history`, `mpim:history` | bot | same | Only if DMs are in scope. I'd drop them. | Optional | Yes |
| `users:read` | bot | `users.info` | Only if summaries show display names; check whether you already have it | Optional | No |

**Make the new scope optional.** Catch-up only enhances the core experience, so `bot_optional` is legitimate here. Your existing features then keep working for customers who never reinstall.

**Handle `missing_scope` in the product.** When it appears, show a clear "ask your admin to reinstall to enable catch-up" message instead of an error.

**Draft justification** (a feature, a trigger and what is kept, not a restatement of the scope):

> `channels:history` (bot) – Reads up to the last 24 hours of messages in a public channel the bot was invited to, only when a user runs `/briefly-catchup` there, to produce a summary shown to that user. Messages are not stored; they are sent for summarization and discarded.

Check that last sentence is true before you submit it. See §5 on OpenAI retention.

Also name the Real-time Search or MCP use case in the notes. The Real-time Search API† serves listed apps only. Describe both paths: `conversations.history` today, Real-time Search if you adopt it later.

## 4. Privacy model: the biggest product risk

Reviewers check that no user sees a private channel, message, file or action Slack would hide from them. That includes guests and Slack Connect members.

- The bot being in a channel does not mean the requester can read it. Verify the requester is a member of the channel (`conversations.members` or `conversations.info`) before summarizing.
- Reject, or block, catch-up for guests, Slack Connect channels and private channels unless you've handled each case.
- Return the summary ephemerally to the requester, never into the channel by default.
- Don't auto-join channels. The bot has to be invited.

## 5. Sending Slack data to GPT-4.1

This is an AI feature with data flowing to a third party, which brings extra obligations.

**Eligibility.** Slack bars apps that train LLMs on Slack data, run unexplained sentiment analysis, or let AI take consequential decisions without human review. Summaries are fine. Confirm and document that your OpenAI account does not train on API data and what retention applies. I haven't verified OpenAI's current terms. Check them, and ask for zero data retention if you can get it.

**Security & Compliance tab** (self-certified, and admins read it before approving). Fill in the AI fields:
- model used: GPT-4.1
- retention, and how the LLM uses user data
- LLM data tenancy
- LLM data residency

Add OpenAI to the sub-processor list, data-center locations and hosting answers.

**Documents.** Update the privacy policy to cover:
- Slack message content sent to OpenAI
- retention and deletion
- data received but not stored

Keep the privacy policy, landing page and Security & Compliance answers consistent with each other.

**Listing and landing page.** State that LLM output can be inaccurate.

**Customers.** If you have DPAs, a new sub-processor will probably need advance notice. Check your contracts. That's a legal question for you, not a Slack rule.

## 6. In-app checks reviewers run

- **Prefix and visibility:** the slash command is prefixed with the app name and ephemeral by default.
- **Help reply:** `help` works on the new command.
- **Acknowledgement:** you acknowledge within 3 seconds, then post the summary asynchronously. LLM latency makes this a real risk.
- **Onboarding:** a first-run message explains the feature and the bot-must-be-invited requirement.
- **Security basics:** signing-secret verification, TLS 1.2+, and no tokens or message text in logs. Log message content to OpenAI request logs nowhere.

## 7. Test information for the resubmission

- **Staging app:** cloned from the published manifest through your environments-as-code flow. Run `apps.manifest.export` and diff against your template. That diff is the change list reviewers test.
- **Unlisted rate limits:** the staging app is distributed but unlisted, so new installs get roughly 1 request/minute and 15 objects† on `conversations.history`. A reviewer testing catch-up may hit that. Say so in the submission notes, keep test channels tiny, and consider event-driven fetching for the staging build.
- **Reviewer access:** reviewers can't enter your Slack workspace. Give them an install link, test channels with dummy messages, and test accounts on your service.
- **Video:** install, enabling the optional scope, running catch-up, and each new scope's use. For updates it should show the new feature and every new scope.
- **Security readiness:** a security contact (email and phone), an architecture diagram showing the OpenAI hop, and one test account per permission role.

## 8. Keep the listing

- **Support:** answer Slack within 2 business days†. Ship nothing else substantial to the live app unreviewed.
- **Your own tracking:** keep your own install and uninstall tracking, because Slack doesn't provide it.
- **Install count:** check you still have 10 or more active workspaces†. Slack changed this gate twice in a year, so verify the current rule.
- **Do not say "approved" or "certified by Slack"** in the reinstall email or anywhere else.

## Recommended plan

1. **Now:** build catch-up behind a flag, add the requester-membership check, and implement `missing_scope` handling.
2. **This week:**
   - Add `channels:history` as `bot_optional` to the manifest template.
   - Update the privacy policy, landing page and Security & Compliance AI fields.
   - Stand up the staging app.
   - Record the video.
3. **Next week:** resubmit once, with all of the above.
4. **After approval:** update the production OAuth URL, publish, send the reinstall message, and flip the flag.

## Questions that would change this answer

1. Do you need private channels or DMs? That adds enhanced-review scopes, and I'd resist both.
2. Is a launch date or event pinned? If so, the 8-week-plus window may force the "coming soon" announcement.
3. Do any customers run Enterprise Grid or Slack Connect?
4. Does your OpenAI account have zero data retention, or is the default retention acceptable to your customers?

† Verify against current Slack Marketplace docs. Slack changed its install gate twice in a year. This covers the 10 active workspaces, review durations, the unlisted rate limits and the support response time.