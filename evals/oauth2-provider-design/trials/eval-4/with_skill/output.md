**Do not ship the plan as written.** Three parts of it are the failure modes this design guide names. A taxonomy that avoids them is below.

## Verdict

1. **Do not redefine `full_access`.** Keep it exactly as is.
2. **Do not add `full_write`.** Use `resource:action` scopes instead.
3. **Do not defer the integration/user token split.** Bind every scope to a token type now. Logs from the existing 120 apps already show how they use tokens, so you can check usage now, before you ship.

## Why

- **Redefinition repurposes a scope.** Scopes must be additive-only. Existing grants and live tokens currently authorize read and write. After the change, one of two things happens:
  - The tokens become read-only. Every writing app gets 403s, and you touch all 120 registrations anyway, during an incident.
  - The tokens are grandfathered. Then `full_access` means two things depending on grant date.
- **The name lies.** Old docs, SDKs, and Stack Overflow answers say `full_access` means write. New developers will request it and break.
- **`full_write` is another catch-all.** It is the single broad scope again, with write added on. Under your plan every app still reads all timesheets of all users, because `full_access` still grants all reads. You cut write blast radius and left read blast radius untouched.
- **Deferred binding costs a reauthorization.** Slack's `chat:write` posts as the app on a bot token and as the human on a user token. Slack documents that changing the binding later "requires reauthorization from every user". You would pay that price after shipping `full_write`.

Your goal was "don't touch the 120 registrations". Freezing `full_access` as-is meets that goal. Redefining it does not.

## Taxonomy

**Naming:** `resource:action`, using the API's own nouns: `projects`, `tasks`, `comments`, `timesheets`. Two actions, `read` and `write`.

- `:write` means create and update only.
- `:write` does not imply `:read`. An app requests both when it needs both.
- A write response may return the written object. Nothing more.
- No delete scope at launch. Delete is not grantable to new apps. Add `:delete` later when traffic shows demand. Adding a scope is additive, but shrinking `:write` later would be repurposing.
- Embedded or expanded related objects in a response are filtered by the caller's scopes. For example, `tasks:read` must not leak `projects` fields unless `projects:read` is also held.

| Scope | Integration token | User token | Verification tier |
|---|---|---|---|
| `projects:read` | yes | yes | 1 |
| `projects:write` | yes | yes | 2 |
| `tasks:read` | yes | yes | 1 |
| `tasks:write` | yes | yes | 2 |
| `comments:read` | yes | yes | 1 |
| `comments:write` | yes, posts as the app | yes, posts as the person | 2 |
| `timesheets:read` | hold | yes | 3 |
| `timesheets:write` | hold | yes | 3 |
| `full_access` (legacy) | yes | yes | grandfathered (see below) |

**Token types:** An integration token acts as the app itself (`client_credentials`). A user token acts as a signed-in person (`authorization_code` with PKCE). The same scope name works on both. The token type decides who acts, and the table above says which type may hold each scope.

- **Integration tokens:** An org admin always approves the install. App identity is org-wide, as with Microsoft's application permissions.
- **User tokens:** The end user consents, and a user token can never exceed what that person can do. Add an org-level policy so admins can gate or block specific scopes.
- **`hold`:** The scope is not grantable on that token type yet. It can be widened later without changing any existing grant.
- **Why timesheets integration is on hold:** Org-wide timesheet read reaches other users' data. That needs the tier 3 review (below) to exist first. Existing integrations keep timesheet access through legacy `full_access`.

**Verification tiers (proposed, based on the skill's ladder):**

- **Tier 1:** publisher identity verification.
- **Tier 2:** tier 1 plus self-attestation.
- **Tier 3:** a third-party security assessment, annual.

The skill draws the tier 3 line at "scope reaches other users' data or PII". Timesheets are my judgement call for that line. Projects, tasks, and comments are shared workspace data. Until tier 3 exists, grant timesheet scopes only to apps you have allowlisted by manual review.

At runtime, reject any scope request that is not a subset of what the app declared and had approved at registration.

## Consent copy (one plain sentence per scope)

Write each sentence when the scope is created. A scope that cannot be explained in one sentence is a design smell.

| Scope | User token | Integration token |
|---|---|---|
| `projects:read` | See your projects and who is in them. | See all projects in this workspace. |
| `projects:write` | Create and edit projects as you. | Create and edit projects as the app. |
| `tasks:read` | See tasks you can see. | See all tasks in this workspace. |
| `tasks:write` | Create and edit tasks as you. | Create and edit tasks as the app. |
| `comments:read` | See comments you can see. | See all comments in this workspace. |
| `comments:write` | Post and edit comments as you. | Post and edit comments as the app. |
| `timesheets:read` | See time entries you can see, including your team's if you are a manager. | not available yet |
| `timesheets:write` | Create and edit time entries as you. | not available yet |

**Consent mechanics:**

- Support partial grants. A user may allow `tasks:read` and deny `tasks:write`.
- Always return the granted scope set in the token response. Integration tests must cover the granted-versus-requested diff.
- Re-consent shows only the net-new scopes. Test this explicitly.
- Do not quote any consent drop-off percentage. No rigorous study exists.

## Legacy `full_access`

**Definition:** `full_access` equals the union of the 8 scopes above, frozen to the four current resources. It never grows when you add new API resources. Its consent copy stays as it is today.

**Migration steps:**

1. **Instrument now (about 1–2 days, if request logs are queryable).** Per app, record token type, read versus write calls, and the resources touched. This gives you the minimal scope set for each of the 120 apps. It also settles your "sort out the flavours later" question using existing traffic.
2. **Ship the 8 scopes.** Close `full_access` to new registrations from that date. Existing grants are untouched.
3. **Show recommendations in the developer portal:** "Your app only uses `tasks:read` and `comments:write`. Switch." Moving to new scopes is a new grant and needs consent. Batch the move so users see one re-consent, not several.
4. **Deprecate.** Announce with a notice window and sunset signalling, following your API versioning policy. Choose the length yourself. For about 120 B2B apps, I would plan on the order of a year.
5. **Keep the coarse tier alive until the fine-grained scopes cover the edge cases.** GitHub's fine-grained model "cannot accomplish every task" the broad one can. Expect the same gap, and do not force a lossy cutover.

**Admin control:** Give org admins a list of installed apps holding `full_access`, and a policy to block it. Apps that keep timesheet access through `full_access` should either pass tier 3 or drop timesheet calls.

## Rules that stay in force

- Additive-only, forever. Never change the meaning of a shipped scope.
- Every scope has a token-type binding, consent copy, and a verification tier before it ships.
- Widen bindings and tiers only additively.
- Never create a single broad catch-all scope. No `full_write`.

## Assumptions to confirm

These are not known from your message. Each answer can change the table.

1. Does the API have DELETE endpoints? If yes, I need to know whether any new app needs them at launch.
2. Are timesheets only ever the requesting user's own data? If yes, tier 3 drops to tier 2.
3. Do payroll or billing integrations exist that need org-wide timesheets? If yes, plan tier 3 first and unhold that cell.
4. Does admin consent for integrations match your current install flow? If no, the admin approval surface is the first thing to build.
5. Do the 120 apps use both token types today? If so, the split affects them directly.

**Next action:** Run the step 1 usage query on the 120 apps' existing token traffic. Then check which assumptions above it answers.