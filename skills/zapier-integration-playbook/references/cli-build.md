# Building with the Zapier Platform CLI

Source: docs.zapier.com `integrations/build-cli/*` (overview, input-fields, dynamic-dropdowns, making-http-requests, testing-and-debugging, hydration), `integrations/build/cli-hook-trigger`, the CLI command reference and the platform schema (`packages/schema/docs/build/schema.md` in `zapier/zapier-platform`). Check the schema and CLI reference for the installed `zapier-platform-core` version before copying a key.

## Contents

- UI or CLI
- Project and app definition
- Authentication
- Triggers
- Creates, searches, search-or-create
- Input fields
- Output fields and samples
- Requests, middleware, errors
- Files and hydration
- Test, push, release

## UI or CLI

- Platform UI: form editor plus Code Mode; fine for a small API-key or OAuth integration a non-engineering owner maintains.
- CLI: source control, unit tests in CI, shared modules and npm packages, middleware, custom auth, `primary: true` output keys, canary releases.
- UI → CLI: `zapier-platform convert <path> --integrationId <id> --version <x.y.z>`, then `zapier-platform push`. The project links to the same integration (`.zapierapprc`); push creates a new version, so users carry over through normal migration.
- CLI → UI: no conversion. Developer Support creates an empty version, you rebuild it by hand, and users cannot be migrated to it. The move is one-way once users run on CLI versions; before that, delete the CLI version and continue in the UI.

## Project and app definition

```bash
npm install -g zapier-platform-cli
zapier-platform login            # --sso with a deploy key for SSO accounts
zapier-platform init my-app      # pick a template: minimal, oauth2, custom-auth, dynamic-dropdown...; --language typescript
zapier-platform register "Acme Billing"   # creates the integration on Zapier
zapier-platform scaffold trigger invoice  # adds triggers/invoice.js and wires it into index.js
```

- Integrations run on Node.js 22; run tests on 22 in CI even if you develop on another version.
- `index.js` exports one app object: `version` (from `package.json`), `platformVersion` (from `zapier-platform-core`), `authentication`, `beforeRequest`, `afterResponse`, `requestTemplate`, `hydrators`, `triggers`, `searches`, `creates`, `searchOrCreates`, `resources`, `flags`, `throttle`.
- Pin `zapier-platform-core` to an exact version in `package.json` and upgrade deliberately; old cores keep working, but `D027` warns when you lag, and Zapier may set an upgrade deadline.
- Secrets live in per-version environment variables: `zapier-platform env:set 1.0.0 CLIENT_ID=... CLIENT_SECRET=...`; locally in `.env`.

## Authentication

`authentication.type` is one of `basic`, `custom`, `digest`, `oauth1`, `oauth2`, `session`; `test` (a request or function hitting a cheap "who am I" endpoint) is required.

| Need | Type | Key parts |
| --- | --- | --- |
| API key, or key-as-Basic | `custom` | `fields` (key, plus subdomain if any), a `beforeRequest` that adds the header |
| Username + password | `basic` / `digest` | fields provided automatically |
| Token exchange, non-standard grant (e.g. `client_credentials`) | `session` | `sessionConfig.perform` returns `{ sessionKey }`; `beforeRequest` adds it |
| Third-party OAuth | `oauth2` | `oauth2Config.authorizeUrl`, `getAccessToken`, optional `refreshAccessToken`, `autoRefresh: true`, `scope`, `enablePkce` |

- `connectionLabel`: a `{{...}}` string or a function naming the account (email, workspace). Never a secret.
- OAuth2: store the app's client id and secret as `CLIENT_ID` / `CLIENT_SECRET` environment variables (`env:set`) and read them as `{{process.env.CLIENT_ID}}`; Zapier generates `state`; find the `redirect_uri` with `zapier-platform describe`.
- With `autoRefresh`, a 401 triggers `refreshAccessToken` (session: `sessionConfig.perform`) and a retry. Extra values returned there are stored in `bundle.authData`; declare them as `computed: true` fields.
- Validate any user-supplied subdomain before building URLs from it.

## Triggers

```js
triggers: {
  new_invoice: {
    key: 'new_invoice',
    noun: 'Invoice',
    display: { label: 'New Invoice', description: 'Triggers when a new invoice is created.' },
    operation: {
      perform: async (z, bundle) => {
        const res = await z.request({ url: 'https://api.acme.test/invoices', params: { sort: '-created_at', limit: 100 } });
        return res.data.items;          // array; the deduper keys on `id`
      },
      sample: { id: 1042, number: 'INV-1042', total: 120.5, created_at: '2026-01-15T10:00:00Z' },
      outputFields: [{ key: 'id', label: 'Invoice ID', primary: true }, { key: 'number', label: 'Invoice Number' }],
    },
  },
},
```

- Polling: return an array, newest first. Without an `id`, map one in (`item.id = item.invoiceId`) or set `primary: true` on output fields (v15.6.0+).
- REST hook: `type: 'hook'` plus four functions:
  - `performSubscribe`: POST `bundle.targetUrl` to your API; the returned JSON becomes `bundle.subscribeData`.
  - `performUnsubscribe`: delete using `bundle.subscribeData.id`.
  - `perform`: turn `bundle.cleanedRequest` into an array; return `[]` to skip an event.
  - `performList`: same shape as the webhook payload, for editor samples.
- Honour `bundle.meta` in polling `perform`: `isLoadingSample`, `isFillingDynamicDropdown`, `isPopulatingDedupe` (first poll seeding the dedupe list), `limit`, `page`. Test with `invoke --isPopulatingDedupe` and `--limit`.
- Hidden polling triggers (`display.hidden: true`) power dynamic dropdowns; set `canPaginate: true` and read `bundle.meta.page` for long lists.

## Creates, searches, search-or-create

- Create: `perform` returns one object (id, name, link to the record). Search: returns an array, best match first; a miss is `[]`.
- `searchOrCreates: { find_customer: { key: 'find_customer', display: {...}, search: 'find_customer', create: 'create_customer' } }`: the key must equal the search key. `update` and `updateInputFromSearchOutput` are marked experimental.
- `lock` on a create serializes runs that must not overlap; `throttle` caps calls per window.

## Input fields

`inputFields` entries: `key`, `label`, `type` (`string`, `text`, `integer`, `number`, `boolean`, `datetime`, `file`, `password`, `copy`, `code`, `json` (core v18.4.0+)), `required`, `helpText`, `default`, `placeholder`, `choices`, `list`, `children`, `dynamic`, `search`, `dependsOn`, `altersDynamicFields`, `computed`.

- Dynamic dropdown from a hidden trigger: `dynamic: 'list_customers.id.name'`, plus `search: 'find_customer.id'` so users can map a value.
- Function dropdown (core v18.4.0+): `choices: { perform: async (z, bundle) => [...] }`, with `dependsOn: ['account_id']` for parent fields.
- Dynamic fields: put a function in the `inputFields` array returning field objects (e.g. the account's custom fields); `bundle.inputData` holds values chosen so far. Only dropdowns accept `altersDynamicFields: true`, which re-runs those functions on change.
- Line items: a field with `children: [...]` sends an array of objects; don't use `children` for visual grouping.
- `json` fields accept a JSON Schema in `schema`; `copy` shows read-only Markdown help, e.g. the irreversibility warning on a delete.

## Output fields and samples

- `sample`: one realistic record with keys every account returns; validated against `outputFields` (D024).
- `outputFields`: labels for abbreviations, units and ids; nested keys as `parent__key`, line items as `parent[]key`; a function entry adds per-account custom fields.

## Requests, middleware, errors

- `z.request(url | options)` returns a response with `.status` and parsed `.data` (core v10+); `{{bundle.authData.x}}` curlies work in shorthand request objects.
- Request lifecycle: defaults → `beforeRequest` middleware → auth headers → params → send → parse → log → 401 + `autoRefresh` raises refresh-auth → `afterResponse` middleware → automatic throw on status ≥ 400 unless `skipThrowForStatus`.
- From core v18, a 429 raises `ThrottledError` before `afterResponse` (opt out with `flags.throwForThrottlingEarly: false`; the default is `true`, though the schema text reads the other way). Never swallow 401 or 429 in `afterResponse`.
- Throw platform errors, never plain `Error`:
  - `z.errors.Error(message, code, status)`: user must fix the Zap; counts toward auto-off.
  - `z.errors.HaltedError(message)`: precondition not met; never turns the Zap off.
  - `z.errors.ExpiredAuthError(message)`: user must reconnect; runs held for replay.
  - `z.errors.RefreshAuthError()`: refresh and retry (OAuth2, session).
  - `z.errors.ThrottledError(message, delaySeconds)`: retry later; use it for a known outage too.
- Log with `z.console.log`; read logs with `zapier-platform logs`.

## Files and hydration

- `z.dehydrateFile(fn, inputData)` returns a pointer Zapier resolves only when a later step needs the file; `z.dehydrate(fn, inputData)` does the same for expensive extra data. Register `fn` under `hydrators`.
- `z.stashFile(bufferStringStream, [knownLength], [filename], [contentType])` uploads file content to Zapier storage and returns a URL to pass downstream. Call it only inside a hydrator, or in a hook `perform` for short-lived URLs; never in a polling `perform`.

## Test, push, release

```bash
zapier-platform invoke auth start             # write authData to .env
zapier-platform invoke auth test              # run authentication.test
zapier-platform invoke trigger new_invoice    # local run; -r for remote
zapier-platform test                          # unit tests (createAppTester + nock)
zapier-platform validate                      # schema and publishing checks
zapier-platform push                          # uploads the version in package.json
zapier-platform promote 1.1.0
zapier-platform migrate 1.0.3 1.1.0 10        # percent, same major only
zapier-platform canary:create 1.0.3 1.1.0 -p 10 -d 3600
zapier-platform deprecate 1.0.0 2027-03-01 --reason=...
zapier-platform pull                          # fetch changes Zapier engineers made
```

- Unit tests: `const appTester = zapier.createAppTester(App); zapier.tools.env.inject();` then `await appTester(App.triggers.new_invoice.operation.perform, bundle)`; mock HTTP with `nock` so CI needs no credentials.
- Invite testers to a private version with `zapier-platform users:add <email> <version>` or `users:links`; add co-developers with `team:add`. Publishing needs 3 users with live Zaps.
- Bump `package.json` version before each push; unlabelled versions push in sequence. Use labelled versions (`1.2.0-beta`) to iterate.
- The legacy `zapier` binary is gone from current CLI releases; use `zapier-platform`.
