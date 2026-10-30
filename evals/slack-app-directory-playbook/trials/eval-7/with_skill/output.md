# Lumatrace Slackbot MCP app: what to change for Slack Marketplace review

## Verdict

- **Eligible.** An app whose only feature is an MCP server for Slackbot can list with `mcp:connect` required, if its tools do meaningful work inside Slackbot conversations.
- **Not eligible as written.** One-word tool descriptions are the failure Slack rejects: a thin, vaguely described tool set.
- **"List next month" is not achievable.** The review alone can take longer than that, and the install gate may block submission outright (see Timeline).

## Assumptions

I couldn't ask, so each of these is flagged. Correct any that are wrong, because some change the plan.

1. **Install count:** Lumatrace has fewer than 10 active Slack workspaces†, since no Slack app exists yet.
2. **Launch date:** "next month" means a target in November 2026, with no event pinned to it.
3. **LLM data:** Slackbot's LLM receives your tool outputs (log lines, traces). You don't send Slack data to an LLM yourselves.
4. **Customers:** Some customers run Enterprise Grid or Slack Connect. If so, test org-ready deployment and Slack Connect behaviour before submitting.
5. **Server access:** Your MCP server is HTTPS on a domain you control and uses OAuth.

## 1. Fix the tools (the main blocker)

Every tool needs four things: a human-readable title, an accurate description, `readOnlyHint`, and a valid `inputSchema`. Run **Fetch Tools** in App Settings before submitting.

| Tool | Title | `readOnlyHint` | Description should say |
|---|---|---|---|
| `search_logs` | "Search logs" | `true` | What it searches (Lumatrace log streams), filters (service, time range, severity, text query), the result cap and ordering, and what an empty result means. |
| `get_trace` | "Get trace" | `true` | What it takes (trace ID), what it returns (spans, durations, errors, linked services), and what happens when the ID is unknown or expired. |
| `create_alert` | "Create alert" | `false` | That it creates a persistent alert rule that can notify people. State the condition, threshold, window and destination fields, and that it creates a rule and doesn't edit existing ones. |

Details that matter for each:

- **`inputSchema`:** Give every parameter a type, a description, an example, and bounds. Set required versus optional explicitly.
- **`create_alert` is the risky tool.** It writes to your product, and the policy bars AI taking consequential decisions without human review. Make Slackbot ask the user to confirm before it runs, and say so in the description. It isn't read-only, so setting `readOnlyHint: false` is the honest answer.
- **Descriptions must match behaviour.** The reviewer calls each tool and compares the output. Rewrite them to match what the tool does today.
- **Failures count.** After listing, repeated tool failures switch the app off automatically. Return clear errors (bad time range, unknown trace) instead of 500s.
- **Output size:** Cap result sizes so Slackbot conversations stay usable.

## 2. Check the data you send into Slack

Logs often contain secrets, PII, and sometimes financial or health data. The unsuitable list bars sharing sensitive financial or health data in Slack.

- Redact known secret and PII patterns in `search_logs` output, or offer a workspace-level setting for it.
- Respect the privacy model: a user must never see logs or traces in Slackbot that they couldn't see in Lumatrace. Map each Slack user to a Lumatrace identity through an authorize step, and apply Lumatrace permissions to every call. Never map users by hand and never share one user's authorization with others.
- Write the retention story for tool outputs: what Lumatrace logs about calls, and that Slack data isn't stored.

## 3. Scope table

| Scope | Token | Methods | Feature | Justification | Required or optional | Enhanced review |
|---|---|---|---|---|---|---|
| `mcp:connect` | bot | MCP connection to your server URL | Lumatrace tools in Slackbot | "Connects Slackbot to the Lumatrace MCP server so a user can ask Slackbot to search logs, fetch a trace, or create an alert for their own Lumatrace account; the app calls nothing else in Slack." | Required, because MCP is the only function | No |

- Request nothing else. Don't add `chat:write`, `*:history` or `commands` "for later". Untestable scopes return the submission, and `*:history` triggers enhanced review.
- Your plan to make `mcp:connect` required is correct for this app. It would be optional if the app had other features.
- **Server setup:** The OAuth redirect to your server is `https://oauth2.slack.com/external/auth/callback`.

## 4. Install gate: the submission blocker

- Slack blocks submission below 10 active workspaces† (used in the last 28 days, sandboxes excluded). You must keep that count through the whole review.
- **Fastest route, ranked by efficiency, highest first:**
  1. Existing Lumatrace customers already asking for Slack, as an unlisted pilot.
  2. Design partners recruited for the pilot.
  3. Staff or partner teams on their own paid workspaces.
- **Start recruiting this week.** Your launch is inside three months.
- Never rely on your own dev or test workspaces. Reviewers expect the app proven where it wasn't built.
- **Pilot as an unlisted distributed app** (staging app, see section 7).
- **Rate limits:** New unlisted installs get throttled history methods (1 request/minute and 15 objects† on `conversations.history` and `conversations.replies`). Your app calls no history methods, so this doesn't hurt you.
- **Don't stay unlisted.** Slack's API terms name the Marketplace the only channel for commercial apps, and listing costs no fee.

## 5. Submission packet checklist

| Item | Owner | Notes |
|---|---|---|
| Listing name | Marketing | Service first: "Lumatrace for Slack", never "Slack Lumatrace". |
| Short description | Marketing | 10 words or fewer, plain text. |
| Long description | Marketing | One line on Lumatrace, the problem, how it works in Slackbot. Show the most-used tools. No superlatives. |
| Icon | Design | High resolution, little text. |
| Screenshots | Design | 1600x1000 px, JPG or PNG under 2 MB. At least one shows a Lumatrace tool in a Slackbot conversation, not only your own UI. |
| Landing page | Web | Public, built for the Slack app (not a doc or repo). Overview, how it works in Slackbot, install path, post-install success page, privacy link. |
| Support page | Support | Email or form needing no new account (GitHub issues alone fail). Response within 2 business days†. |
| Privacy policy | Legal | Slack data handling stated, retention period, access and deletion requests, email or web-form contact. State data received but never used (logs, payload IDs). |
| Test information | Eng | Install path reviewers run themselves, no Slack workspace login. Lumatrace test accounts, paid tier if needed, loaded with dummy logs and traces, the longest trial you can grant. |
| Submission notes | Eng | Walk install, authentication, one tool call and its response. |
| Video demo | Eng | Install and OAuth, setup, each tool end-to-end, uninstall. Optional public YouTube listing video: 30–90 s, captions on. |
| Security & Compliance answers | Security | Self-certified, shown to customer admins. Cover data retention and removal, storage and encryption, hosting and sub-processors, certifications, SSO, security contact, vulnerability disclosure covering the Slack app, token rotation. They must match the privacy policy. |
| AI disclosure | Product | Say on the listing and landing page that LLM output can be inaccurate. In Security & Compliance, state your role: your tools return Lumatrace data to Slackbot's LLM, and you run no model on Slack data. Describe retention of tool outputs. |
| Security review readiness | Security | Contact with email and phone, architecture diagram, one test account per permission role. |
| Cleanup | Eng | Remove test slash commands (you have none) and clear the automated checks. |

Never write "Slack-certified", "approved by Slack" or similar anywhere. The Marketplace Agreement forbids implying endorsement.

## 6. Timeline, worked backward

All durations are estimates†. Read the current figures on the submission page.

- **Today:** 2026-10-30.
- **Fix tools, write the packet, stand up the staging app:** about 1 week, so submit around 2026-11-06 at the earliest. This assumes the install gate is already met, which I assume it is not.
- **Preliminary review:** up to 10 business days†, to about 11-20. A returned round counts as another cycle and resets your queue position, so fix all feedback in one pass: about 12-04.
- **Functional review:** up to 10 weeks† for a new app, which cannot be expedited. That puts the worst case at roughly mid-February 2027, with this app's wait possibly shorter.

So "list next month" won't happen. Instead:

1. Announce "coming to the Slack Marketplace".
2. Take pilot sign-ups (these also help clear the install gate).
3. Publish on approval. Approval and publishing are separate, so you choose the day.
4. Never drive general-audience installs to the unlisted app.

## 7. Environments as code

Keep one manifest in your repo and apply it with `apps.manifest.update` or the Slack CLI. Never edit settings by hand.

- `lumatrace-dev`: distribution off.
- `lumatrace-staging`: distribution on, never listed. Send its link only to reviewers and pilot testers.
- `lumatrace` (production).

Each app gets its own signing secret, client secret and token store. The configuration token expires after 12 hours†. Rotate it with `tooling.tokens.rotate`. Diff the template against the live app (`apps.manifest.export`) before every resubmission.

## 8. After listing

- **The live app is locked.** New tools or scopes need a resubmission with a video and the staging app (up to 6 weeks† for updates). Never put an unreviewed scope in the live install URL.
- **Support:** Answer within 2 business days†. Keep developer, support and security contacts current, and a second collaborator on the app.
- **Delisting triggers:** a broken landing page or install flow, an abandoned app, or a substantial change shipped without review. A security review can arrive at any time.
- **Analytics:** Slack gives you none. Track installs and uninstalls yourself (`app_uninstalled` and an OAuth install ledger).
- **Visibility:** Put the `slack-app-id` meta tag on every page of your domain first. Then add direct install from the listing, then Add to Slack in your product settings, then ask Slack to feature the app.

## Do this week

1. Rewrite the three tools (titles, descriptions, schemas, `readOnlyHint`) and add the `create_alert` confirmation.
2. Count your active Slack workspaces and start pilot recruiting.
3. Build the staging app and the dummy-data Lumatrace test account.
4. Draft the privacy policy and Security & Compliance answers together so they match.

† Verify against current Slack Marketplace docs. Slack changed its install gate twice in a year.