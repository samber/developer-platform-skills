# Fixes for the three quillstack provider issues

All three have the same cause, and none of the three fixes involves write-only. `Read` replaces what the config set with whatever the API returns, which is empty for these fields. The diff is real, so a doc note won't fix it.

## Summary

| Issue | Right fix | Not this |
|---|---|---|
| (a) `webhook.signing_secret` | `Read` keeps the prior state value. Mark it `Sensitive`. | A doc note saying "ignore this diff". |
| (b) `integration.api_token` | `Computed` + `Sensitive`. `Read` never overwrites it. Drop any `RequiresReplace`. | Write-only. |
| (c) `project.notes` | Same as (a). Better still, have the API return `notes` in GET. | A doc note. |

## Why the doc note fails for (a)

- Every `terraform plan` shows a change, so `-detailed-exitcode` returns 2 forever. CI drift checks break.
- Every `apply` re-sends the secret to the API. That can fire webhook-update events or audit entries each time.
- Users learn to ignore plan diffs, including real ones.

## Why write-only fails for (b)

1. **Version:** write-only attributes need Terraform 1.11 or later. Your floor is 1.5.
2. **Computed:** write-only attributes can't be `Computed`. They are config-only inputs, and `api_token` is an output your API generates.
3. **Usability:** a write-only value is never stored in state, so nobody could reference `quillstack_integration.x.api_token` in other resources or outputs. Users need that value, so it has to stay in state.
4. **Import:** write-only wouldn't fix the import problem anyway.

## (a) and (c): keep the prior value in `Read`

Map the API response onto the existing state model. Don't build a fresh model from the API response. Fields the API doesn't return then keep their previous value.

```go
func (r *webhookResource) Read(ctx context.Context, req resource.ReadRequest, resp *resource.ReadResponse) {
    var state webhookModel
    resp.Diagnostics.Append(req.State.Get(ctx, &state)...)
    if resp.Diagnostics.HasError() { return }

    w, err := r.client.GetWebhook(ctx, state.ID.ValueString())
    // ...handle 404 with resp.State.RemoveResource, other errors with diagnostics...

    state.URL = types.StringValue(w.URL)
    // signing_secret is never returned: leave state.SigningSecret untouched.
    resp.Diagnostics.Append(resp.State.Set(ctx, &state)...)
}
```

- **Schema:** `signing_secret` is `Optional` or `Required`, plus `Sensitive: true`. `notes` is `Optional`. Neither is `Computed`.
- **Cost:** out-of-band changes to these fields can't be detected. State the limitation in the attribute description.
- **Import:** these fields are null after import. If the config sets them, the first plan after import shows one in-place update, which is correct and converges.
- **Better for (c):** `notes` is plain text, not a secret, and GET dropping it is an API bug. Ask the API team to return it. Then `Read` maps it normally and you get real drift detection.
- **Better for (a):** ask the API team to return a fingerprint, such as a SHA-256 prefix of the secret. Store it in private state at create and update, then compare in `Read` to detect rotation outside Terraform.

## (b): `api_token` as a create-time-only output

1. Schema: `Computed: true`, `Sensitive: true`. Remove `RequiresReplace`. That plan modifier is almost certainly what turns the empty token into a recreate.
2. Add `stringplanmodifier.UseStateForUnknown()` so ordinary updates don't show "known after apply".
3. `Create`: set `api_token` from the create response. This is the only time you get it.
4. `Read`: never touch `api_token`. If the code does `state.APIToken = types.StringValue(resp.Token)`, that line is the bug. Delete it.
5. `Update`: copy the prior state value into the new state. Don't leave it unknown.
6. `ImportState`: use passthrough on `id`. `api_token` stays **null**, not `""`. An empty string would look like a real value.

After import, `api_token` is null, and `UseStateForUnknown` does nothing for a null state value. So the first update after import shows `api_token` as "known after apply". Handle this in `Update` by setting it to null when the prior state value is null.

Document that imported integrations have no token, because the API only reveals it once. To get one, the user must replace the resource, for example with `terraform apply -replace=quillstack_integration.x`, or use a rotation endpoint if the API has one. A separate `quillstack_integration_token` resource would be a clean way to offer rotation.

## Tests, to catch regressions

- **Acceptance step:** after `Config`, run a second step with `PlanOnly: true` and `ExpectNonEmptyPlan: false`. Today this fails for all three fields, which proves the bug.
- **Import step:** `ImportState: true, ImportStateVerify: true, ImportStateVerifyIgnore: []string{"signing_secret", "api_token", "notes"}`. The ignore list is legitimate because the API never returns these fields.
- **Post-import plan:** for (b), add a step that plans after import and asserts the integration is not replaced.
- **Pivot cases:** empty-string `notes` versus null `notes`, and a token containing special characters.

## Optional later

Once you can raise the minimum to Terraform 1.11 or later, add `signing_secret_wo` and `signing_secret_wo_version` as an alternative input. That keeps the secret out of state entirely, but it doesn't fit the 1.5 floor, so it can't replace the fix above. Confirm the plugin framework version and the behavior on older Terraform before shipping it.

This is based on framework behavior as I know it, and I didn't run any of it against your repo. Run the `PlanOnly` regression test first to confirm the diagnosis before changing the schema.