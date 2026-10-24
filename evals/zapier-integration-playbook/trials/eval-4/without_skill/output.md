# Review of the Quillbase Zapier app before 1.0.0

I haven't run any of this. I read your snippet and checked it against how `zapier-platform-core` v16 behaves as I remember it. Verify the items marked "check" with `zapier validate` and `zapier test`.

## Blockers (fix before pushing)

1. **Live secret in source.** `client_secret: 'sk_live_9c1e77d2'` and the client ID are committed.
   - Move both to `{{process.env.CLIENT_ID}}` and `{{process.env.CLIENT_SECRET}}`, and set them with `zapier env:set 1.0.0 CLIENT_SECRET=...`.
   - **Rotate the secret.** It is already in git history.

2. **The `afterResponse` that forces `status: 200` must go.** It hides every failure from the platform:
   - 401 never triggers a token refresh.
   - 429 never triggers Zapier's throttling or retry, because the platform no longer sees a 429.
   - Creates return `{ error: ... }` as a successful step, so the Zap runs green and downstream steps get garbage.
   - Triggers emit the error object as a new item.
   - Zapier's own `throwForStatus` never fires, so you lose error surfacing, retries and the auth-error UI.

3. **Your real expired-token case is not handled.** The API returns 200 with `{ "error": "token_expired" }`, and nothing detects it. The fix is below, together with these OAuth gaps:
   - `refreshAccessToken` is missing.
   - `autoRefresh: true` is missing.
   - `grant_type` and `redirect_uri` are missing.
   - `state` is missing from the authorize step. This is a CSRF risk.

4. **Nothing authenticates requests.** There is no `beforeRequest` adding the bearer token, so every `z.request` goes out anonymous.

5. **`skipThrowForStatus: true` in `create_contact` swallows 401, 429 and 5xx.** Only the 409 is handled, so everything else returns `res.data` as success. Handle 409 and call `res.throwForStatus()` for the rest. Check: confirm the 409 body shape. Returning the existing contact may be better than failing, if your API gives you its ID.

6. **`connectionLabel: '{{bundle.authData.access_token}}'` shows the access token in the Zapier UI.** Use something human-readable, such as `{{email}}` from a `/me` response. Use that same endpoint for `test` instead of `contacts?limit=500`, which is heavy and called on every connection check.

## Should fix

7. **`new_attachment` stashes every file on every poll.** `z.stashFile` runs eagerly for all returned items. Use `z.dehydrateFile` so files download only when a later step needs them. The download request must carry the token, so the `beforeRequest` from item 4 must apply to it. Don't send the token to a different host.

8. **Trigger and create definitions are incomplete.** Both are missing `key`, `noun`, `display`, `sample` and `outputFields`, and the create is missing `inputFields`. `zapier validate` should fail on these. Trigger items also need a unique `id` for deduplication.

9. **`body: bundle.inputData` forwards every input field as-is.** Build the body explicitly and drop empty values.

10. **Dependencies and CI.**
    - Pin `zapier-platform-core` to an exact version (for example `16.1.0`). The caret range lets core drift from the CLI and schema version you validate and push with.
    - Node 18 is end-of-life. Check the Node versions supported by your core version and move CI to the newest one it supports.
    - `zapier test` should use test fixtures, not live credentials.

## Suggested changes

```js
const BASE = 'https://api.quillbase.test/v2';

const addAuth = (request, z, bundle) => {
  if (bundle.authData.access_token) {
    request.headers.Authorization = `Bearer ${bundle.authData.access_token}`;
  }
  return request;
};

const handleErrors = (response, z) => {
  // Expired token arrives as HTTP 200, so check the body before the status.
  if (response.status === 401 || response.data?.error === 'token_expired') {
    throw new z.errors.RefreshAuthError();
  }
  if (response.status === 429) {
    const retryAfter = Number(response.headers['retry-after']);
    throw new z.errors.ThrottledError(
      'Quillbase rate limit reached',
      Number.isFinite(retryAfter) ? retryAfter : undefined
    );
  }
  if (response.status === 200 && response.data?.error) {
    throw new z.errors.Error(String(response.data.error), 'api_error', 200);
  }
  return response; // non-2xx falls through to the built-in throwForStatus
};

const App = {
  version: require('./package.json').version,
  platformVersion: require('zapier-platform-core').version,
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
          grant_type: 'authorization_code',
          code: '{{bundle.inputData.code}}',
          redirect_uri: '{{bundle.inputData.redirect_uri}}',
          client_id: '{{process.env.CLIENT_ID}}',
          client_secret: '{{process.env.CLIENT_SECRET}}',
        },
      },
      refreshAccessToken: {
        url: 'https://auth.quillbase.test/oauth/token',
        method: 'POST',
        body: {
          grant_type: 'refresh_token',
          refresh_token: '{{bundle.authData.refresh_token}}',
          client_id: '{{process.env.CLIENT_ID}}',
          client_secret: '{{process.env.CLIENT_SECRET}}',
        },
      },
      autoRefresh: true,
    },
    test: { url: `${BASE}/me` },
    connectionLabel: '{{email}}', // adjust to a field your /me endpoint returns
  },
  beforeRequest: [addAuth],
  afterResponse: [handleErrors],
  creates: {
    create_contact: {
      key: 'create_contact',
      noun: 'Contact',
      display: { label: 'Create Contact', description: 'Creates a contact in Quillbase.' },
      operation: {
        inputFields: [
          { key: 'email', required: true },
          { key: 'name' },
        ],
        perform: async (z, bundle) => {
          const { email, name } = bundle.inputData;
          const res = await z.request({
            url: `${BASE}/contacts`,
            method: 'POST',
            body: { email, ...(name ? { name } : {}) },
            skipThrowForStatus: true,
          });
          if (res.status === 409) {
            throw new z.errors.Error('Contact already exists', 'contact_exists', 409);
          }
          res.throwForStatus(); // 401/429/5xx still reach the platform
          return res.data;
        },
        sample: { id: 'ct_123', email: 'ada@example.com', name: 'Ada' },
      },
    },
  },
  triggers: {
    new_attachment: {
      key: 'new_attachment',
      noun: 'Attachment',
      display: { label: 'New Attachment', description: 'Triggers when an attachment is added.' },
      operation: {
        perform: async (z) => {
          const res = await z.request({ url: `${BASE}/attachments?sort=-created_at` });
          return res.data.map((a) => ({
            ...a,
            file: z.dehydrateFile(downloadFile, { url: a.download_url }),
          }));
        },
        sample: { id: 'at_123', created_at: '2026-10-23T10:00:00Z', file: 'hydrate|||...' },
      },
    },
  },
  hydrators: { downloadFile },
};

function downloadFile(z, bundle) {
  // Only send the token to Quillbase hosts, never to a third-party download URL.
  return z.stashFile(z.request({ url: bundle.inputData.url, raw: true }));
}
```

Two things the snippet needs:
- Define `downloadFile` as a function declaration, as above, so it is hoisted for `hydrators`.
- Make `addAuth` skip non-Quillbase hosts if `download_url` can point elsewhere.

## Things to check against your API and the SDK

- **`/me`:** confirm it exists, and which field is best for `connectionLabel`.
- **`response.data` in `afterResponse`:** confirm it is populated for your core version. Fall back to `response.json` if it isn't.
- **Retries:** confirm how your 429 behaves with `ThrottledError`, using a test that mocks a 429 with `Retry-After`.
- **Tests:** add them for the cases below.
  - 200 with `token_expired` throws `RefreshAuthError`.
  - 429 with `Retry-After` throws `ThrottledError` with the right delay.
  - 409 on create.
  - 500 on create is not swallowed.
  - An empty attachments list.
- **Order of work:**
  1. Rotate the secret and move it to env vars.
  2. Remove the 200-masking hook.
  3. Add `beforeRequest` and the new `afterResponse`.
  4. Fix OAuth and `connectionLabel`.
  5. Complete the definitions.
  6. Pin versions and update CI.
  7. Run `zapier validate` and `zapier test`.