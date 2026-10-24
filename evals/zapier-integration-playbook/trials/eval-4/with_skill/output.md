# Quillbase Zapier app: what to change before pushing 1.0.0

I read the skill and its references. I haven't run any of this code. The fixes below are written from your snippet and the skill's rules.

## 1. Assumptions

- No interview was possible, so each line below is an assumption.
- Stage: private, pre-1.0.0, fewer than 5† users. Keys and shapes are still editable, and this is the cheapest moment to fix them.
- The CLI is your build path, since you run `zapier test` in CI.
- The API has a cheap "who am I" endpoint (assumed `GET /v2/me` returning an `email`).
- The OAuth server can issue refresh tokens.
- Contact fields are `email`, `first_name`, `last_name`.
- Attachments have a unique, stable `id`.
- Attachment `download_url` points at a host that may or may not need your bearer token.
- No webhook subscription endpoint exists, so the trigger is polling.
- No deadline, so the answer is ordered by risk.

## 2. Stage and route

Private, pre-publish. Follow Design (audit), then Build, then Publish. Nothing is live, so classify every change as free now. Once the 1.0.0 keys have live Zaps, renames become breaking.

## 3. Step table

| Key | Label | Type | Class | Reason |
| --- | --- | --- | --- | --- |
| `create_contact` | Create Contact | create | keep key, fix body | Swallowed errors, `skipThrowForStatus` with no rethrow, and a plain `Error` on 409. It also has no `display`, `inputFields`, `sample` or `outputFields`. |
| `new_attachment` | New Attachment | polling trigger | keep key, fix body | `z.stashFile` runs inside the polling `perform`, unawaited. Use `z.dehydrateFile`. It also lacks `display`, `sample` and a page `limit`. |
| `find_contact` + `find_or_create_contact` | Find Contact / Find or Create Contact | search / searchOrCreate | additive (new) | Replaces the 409 dead end. It is also the Zapier-recommended shape for contact apps. |
| `afterResponse` status rewrite | n/a | middleware | rejected | See finding A. |

## 4. Auth and trigger-type decisions

### Blocking findings

**A. Delete the `afterResponse` that turns errors into 200s.** This is the worst problem.
- It breaks the 429 path. Zapier retries a 429 only if the error surfaces. On `^16.1.0` your middleware runs on the 429 and rewrites it to 200. Core v18 and later† raise the throttle error before `afterResponse`, but your `^16.1.0` range doesn't guarantee that.
- Every 4xx or 5xx becomes a "successful" step.
  - `create_contact` returns `{ error: ... }` as the created contact.
  - The trigger emits error objects as new records.
  - Failed Zaps never show as errors, so Zapier's auto-off and your error monitoring go blind.
- Your `res.status === 409` check can never fire. The middleware has already made the status 200.
- "Keep Zaps alive" is the wrong goal. Never return 200 on a failure.

**B. Expiry arrives as 200 `{ "error": "token_expired" }`, and Zapier refreshes on 401 only.**
- Best fix: make the API return 401 for expired tokens. The skill's rule is HTTP 401 on expiry.
- Bridge until then: throw `RefreshAuthError` in `afterResponse` on that body (code below).
- Without either, a step silently "succeeds" with an error body after an hour.
- Refresh also needs `refreshAccessToken` and `autoRefresh: true`. You have neither.

**C. Secrets in source.**
- `client_secret: 'sk_live_9c1e77d2'` and `client_id: 'qb_live_8f3a'` are hardcoded.
- Move both to `zapier-platform env:set 1.0.0 CLIENT_ID=... CLIENT_SECRET=...` and read them as `{{process.env.CLIENT_ID}}`.
- Treat the secret as leaked. Rotate it, and check git history for it.

**D. `connectionLabel: '{{bundle.authData.access_token}}'` prints the bearer token in the Zapier UI.** Use the account's email or name from the `test` response, for example `{{bundle.inputData.email}}`.

**E. No `beforeRequest`, so no request carries the token.** Add one that sets `Authorization: Bearer` on your API origin only. Don't send the token to a different `download_url` host, which may be signed storage.

**F. `new_attachment` calls `z.stashFile` inside the polling `perform`.**
- It isn't awaited, so `file` is a Promise.
- Even awaited, it would download every file on every poll, against the 30 s† limit.
- Return `z.dehydrateFile(hydrator, { url })` and put the download in a registered hydrator. Zapier then fetches the file only when a later step needs it.

### Other findings

- **`create_contact` has `skipThrowForStatus: true` and handles only 409.**
  - A 400, 401, 429 or 5xx returns the error body as a success.
  - Keep the skip only for the 409 case, then call `res.throwForStatus()`.
  - Make 409 a `HaltedError`, not a plain `Error`. A duplicate is an unmet precondition and must not count toward auto-off. Keep the message under 250†characters and name the field.
- **Missing step metadata.** Neither step has `key`, `noun`, `display`, `inputFields`, `outputFields` or `sample`. `validate` will fail, and `body: bundle.inputData` sends whatever the editor holds. Map fields explicitly.
- **`test` hits `contacts?limit=500`.** It should be a cheap identity call. A large list inside a 30 s† budget is fragile.
- **`zapier-platform-core` is `^16.1.0`.** Pin an exact version, and upgrade deliberately to a current core after reading the changelog. That also fixes the 429 ordering in A.
- **CI is on Node 18, but integrations run on Node 22†.** Test on 22.
- **The CLI binary is `zapier-platform`.** `zapier test` is the legacy name, gone from current CLI releases.
- **OAuth is incomplete.**
  - `getAccessToken` lacks `grant_type` and `redirect_uri`.
  - `authorizeUrl` lacks `redirect_uri` and `state`.
  - Zapier supplies `state`, and `zapier-platform describe` shows the `redirect_uri`.
  - Check these against your OAuth server.
- **Trigger shape.** Newest-first (`sort=-created_at`) is right, but add an explicit `limit` of 100†. Zapier reads page one only and dedupes on `id`. Keep `id` stable, and never filter "already seen" server-side.
- **Trigger type.** Stay polling, since there's no webhook subscription API. If real volume exceeds 100† new items per poll, build that API and add an instant twin under a new key.

### Proposed code

```js
// index.js
const zapier = require('zapier-platform-core');

const API_ORIGIN = 'https://api.quillbase.test';
// Zapier's refresh trigger is 401 only. Quillbase signals expiry with a 200 body, so map it.
const TOKEN_EXPIRED = 'token_expired';

const addBearer = (request, z, bundle) => {
  // Scope the token to our API; download_url may point at signed storage.
  if (bundle.authData.access_token && request.url.startsWith(API_ORIGIN)) {
    request.headers.Authorization = `Bearer ${bundle.authData.access_token}`;
  }
  return request;
};

const refreshOnExpiredBody = (response, z) => {
  const body = response.data; // undefined for raw downloads
  if (response.status === 200 && body && !Array.isArray(body) && body.error === TOKEN_EXPIRED) {
    throw new z.errors.RefreshAuthError();
  }
  return response; // never rewrite other statuses: 429 and 5xx must surface
};

const hydrators = {
  downloadAttachment: (z, bundle) => z.stashFile(z.request({ url: bundle.inputData.url, raw: true })),
};

module.exports = {
  version: require('./package.json').version,
  platformVersion: zapier.version,
  hydrators,
  beforeRequest: [addBearer],
  afterResponse: [refreshOnExpiredBody],
  authentication: {
    type: 'oauth2',
    oauth2Config: {
      authorizeUrl: {
        url: 'https://auth.quillbase.test/oauth/authorize',
        params: {
          client_id: '{{process.env.CLIENT_ID}}',
          state: '{{bundle.inputData.state}}',
          redirect_uri: '{{bundle.inputData.redirect_uri}}',
          response_type: 'code',
        },
      },
      getAccessToken: {
        url: 'https://auth.quillbase.test/oauth/token',
        method: 'POST',
        body: {
          code: '{{bundle.inputData.code}}',
          client_id: '{{process.env.CLIENT_ID}}',
          client_secret: '{{process.env.CLIENT_SECRET}}',
          grant_type: 'authorization_code',
          redirect_uri: '{{bundle.inputData.redirect_uri}}',
        },
      },
      refreshAccessToken: {
        url: 'https://auth.quillbase.test/oauth/token',
        method: 'POST',
        body: {
          refresh_token: '{{bundle.authData.refresh_token}}',
          client_id: '{{process.env.CLIENT_ID}}',
          client_secret: '{{process.env.CLIENT_SECRET}}',
          grant_type: 'refresh_token',
        },
      },
      autoRefresh: true,
    },
    test: { url: `${API_ORIGIN}/v2/me` }, // cheap identity call
    connectionLabel: '{{bundle.inputData.email}}',
  },
  creates: {
    create_contact: {
      key: 'create_contact',
      noun: 'Contact',
      display: { label: 'Create Contact', description: 'Creates a contact in Quillbase.' },
      operation: {
        inputFields: [
          { key: 'email', label: 'Email', required: true },
          { key: 'first_name', label: 'First name' },
          { key: 'last_name', label: 'Last name' },
        ],
        perform: async (z, bundle) => {
          const { email, first_name, last_name } = bundle.inputData;
          const res = await z.request({
            url: `${API_ORIGIN}/v2/contacts`,
            method: 'POST',
            body: { email, first_name, last_name },
            skipThrowForStatus: true,
          });
          if (res.status === 409) {
            // Unmet precondition, not a Zap fault: must not count toward auto-off.
            throw new z.errors.HaltedError('A contact with this Email already exists. Use Find or Create Contact to reuse it.');
          }
          res.throwForStatus(); // 400/401/429/5xx surface normally
          return res.data;
        },
        sample: { id: 'ct_123', email: 'ada@example.com', first_name: 'Ada', last_name: 'Lovelace', created_at: '2026-01-15T10:00:00Z' },
        outputFields: [{ key: 'id', label: 'Contact ID' }, { key: 'email', label: 'Email' }],
      },
    },
  },
  triggers: {
    new_attachment: {
      key: 'new_attachment',
      noun: 'Attachment',
      display: { label: 'New Attachment', description: 'Triggers when a new attachment is added.' },
      operation: {
        perform: async (z) => {
          const res = await z.request({ url: `${API_ORIGIN}/v2/attachments`, params: { sort: '-created_at', limit: 100 } });
          return res.data.map((a) => ({
            ...a,
            file: z.dehydrateFile(hydrators.downloadAttachment, { url: a.download_url }),
          }));
        },
        sample: { id: 'att_123', name: 'contract.pdf', created_at: '2026-01-15T10:00:00Z' },
        outputFields: [{ key: 'id', label: 'Attachment ID' }, { key: 'name', label: 'File name' }],
      },
    },
  },
};
```

Add `find_contact` and `find_or_create_contact` as well. The `searchOrCreates` key must equal the search key.

## 5. Publish checklist

| Item | Owner | Week |
| --- | --- | --- |
| Apply fixes A-F, pin core exactly, move CI to Node 22†, rename the CI command | Engineer | 1 |
| Rotate `client_secret`, set `CLIENT_ID` and `CLIENT_SECRET` with `env:set` per version | Engineer + security | 1 |
| Decide whether the API returns 401 on expiry; if yes, keep the middleware only as a bridge | API owner | 1 |
| `validate`: clear every Error and Publishing Task | Engineer | 1-2 |
| Recruit 3† users with a live Zap, then one live Zap and one successful run per visible step | Product + CS | 2-3 |
| Non-expiring paid test account for `integration-testing@zapier.com`, company-domain admin | Ops | 2 |
| Submit from Integration Home; expect about a week† per review round | Engineer | 3-4 |

## 6. Growth actions

Out of scope for this review. First lever after approval: submit 5-10† Zap templates on approval day. They must use the promoted version and avoid Paths, Code, Webhooks, Looping and Formatter steps†.

## 7. Versioning plan

- Target version: push 1.0.0 only after the fixes. The version is private and editable while it has fewer than 5† users.
- After live users exist, any key or shape change needs an additive twin step, not an in-place edit. Never rename `create_contact` or `new_attachment` then.
- Canary (CLI): 5-10% for 30-60 minutes for later non-breaking releases.
- Diff by hand before every promotion. Promotion won't catch these:
  - output keys, output structure and perform behavior;
  - the attachment sort order and the `id` format. Changing either floods live Zaps' dedupe memory.

CI tests to add, with `createAppTester` and `nock`:

- a 200 `token_expired` body raises `RefreshAuthError`;
- a 429 with `Retry-After` is not rewritten to 200;
- a 409 raises `HaltedError`;
- a 500 raises an error;
- the trigger returns a `dehydrateFile` pointer, not a Promise.

## 8. Metric baseline

| Metric | Value |
| --- | --- |
| Activation within 24 h per step | unknown; Developer Platform dashboards after beta |
| Quarterly active users vs. Silver threshold (50†) | unknown; Partner Program page |
| Open bugs and feature requests, median response days | unknown; Bugs & Feature Requests queue |
| Zap error rate (auto-off at 95%† over more than 20† runs in 7 days) | unknown; Monitoring logs |

† Zapier platform numbers: verify against Zapier's live docs before quoting them. This covers the 30 s limit, 100 items per poll, 250-character error truncation, the 5-user edit rule, the 3 live users, Node 22, core v18 early 429 handling, the 50-user Silver tier, the 95%/20-run auto-off rule and the review timing.