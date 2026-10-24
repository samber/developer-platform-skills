# Fixes for the three perpetual-diff issues in terraform-provider-quillstack v2.3.1

Neither of your two proposals is the right fix. I haven't seen the provider code, so the "likely cause" lines below are inferences from the symptoms. Check each one against the code.

The common cause is that `Read` overwrites state with whatever the API returns. For fields the API never returns, that is null or empty, so every plan shows a diff. The fix is in `Read`: preserve the prior state value for these fields. Don't rely on a doc note.

## (a) `quillstack_webhook.signing_secret`

**Don't ship the "ignore this diff" doc note.** Users can't suppress a diff that appears on every plan, and it would hide real changes to the field.

**Don't make it write-only on its own either.** Write-only arguments need Terraform and OpenTofu 1.11+, and your minimum is 1.5. Removing or replacing the existing attribute would also be a breaking change.

**The fix:**
1. Keep `signing_secret` as a `Sensitive` attribute. In `Read`, stop overwriting it. Keep the prior state value, and don't set it from the hash or null the API returns.
2. Add a write-only `signing_secret_wo` plus a `signing_secret_wo_version` trigger beside it. Use `ConflictsWith` between the two. Put the `PreferWriteOnlyAttribute` validator on the old one so users on 1.11+ are steered to the new one.
   - Write-only can't be Computed or sit in a set.
   - Users bump `signing_secret_wo_version` to rotate.
3. Document that drift on this field is undetectable, because the API stores only a hash.

**Upgrade effect:** users whose state already holds null see one in-place update on the first plan after upgrading. It then goes quiet.

## (b) `quillstack_integration.api_token`

**Don't mark it write-only.** Write-only is for secrets the user supplies. A write-only argument can't be Computed, so it can't carry a generated token back to the user. Users need the token, for example to reference it from other resources.

**The fix is the "API generates it, returns it once" pattern:**
1. Make `api_token` a `Sensitive`, Computed-only attribute. Set it from the create response.
2. Add `UseStateForUnknown`, and no `RequiresReplace`.
3. In `Read`, never overwrite it. After import, set it to **null**, not an empty string.
4. Document three things:
   - The token is stored in plaintext in state, because `Sensitive` only hides it in plan output.
   - After import it is null.
   - The only way to recover or rotate it is to replace the resource (`-replace`).

**Likely cause of the recreate:** a Computed-only attribute with no config can't produce a diff by itself. So check for `RequiresReplace` or a custom plan modifier on `api_token`, or a `Read` that writes `""` and trips one.

**Ask the API team:** can callers supply the token? If so, it can become write-only later, which keeps it out of state.

## (c) `quillstack_project.notes`

**Keep it a normal attribute. Don't make it write-only.** Write-only is for secrets, and it would remove drift detection and plan visibility for plain text.

**The fix:**
1. Make `notes` Optional. In `Read`, keep the prior state value.
2. Document that out-of-band edits to `notes` can't be detected.
3. Ask the API team to return `notes` in GET. That is the real fix and would remove the workaround. Until then, treat this row of the API readiness gate as COMP (compensated), not PASS.

**After import:** `notes` is null until the user sets it, so the first plan shows one update.

## Tests (all three)

- Add an import step to each resource's `_basic` test. Put only these fields in `ImportStateVerifyIgnore`: `signing_secret`, `api_token`, `notes`.
- The harness already fails any step whose post-apply plan isn't empty, so these tests reproduce your bug. Never add `ExpectNonEmptyPlan`.
- Add an upgrade test: apply with 2.3.1, plan with the new build, expect no changes.
- For the write-only pair, assert two things: the value reaches the API but never appears in state, and bumping `signing_secret_wo_version` triggers an update.
- Write the failing tests first, then the fixes in a second commit.

## Versioning

- The `Read` fixes are drift-detection fixes, so a patch release.
- Adding `signing_secret_wo` and `signing_secret_wo_version` is a new attribute, so a minor release.
- Ship them together as 2.4.0, or ship the `Read` fixes alone as 2.3.2.
- Leave your 1.5 minimum alone. Nothing here needs a major release.