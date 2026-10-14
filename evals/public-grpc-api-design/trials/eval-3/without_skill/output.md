# Can you sign it? ❌ No, not as worded

"The published contract cannot break without CI catching it" is stronger than your pipeline supports. I'm working only from your description, not your `buf.yaml` or CI config. Eight months of green shows the checks haven't fired. It doesn't show they would fire on a real break.

## Why not

1. 🔴 **The REST surface isn't covered.**
   - Buf's breaking rules check the proto schema. As far as I know, they don't check `google.api.http` annotations.
   - Changing a path, verb, `body`, `response_body` or `additional_bindings` breaks REST clients. `buf breaking` stays green.
   - The same goes for transcoder or gateway config that lives outside the protos, such as an Envoy or grpc-gateway service YAML.
   - Behavior changes, such as new semantics for the same field, status-code mapping, or pagination, are also invisible to it.

2. 🟠 **`PACKAGE` is too loose for published `.proto` files.**
   - `PACKAGE` doesn't flag moving a message between files in the same package, deleting a file, or changing file options like `go_package` or `java_package`. Only `FILE` catches those.
   - Partners who import your `.proto` files by path, or who rely on generated-code layout, break on those changes.
   - `FILE` is the standard choice when you publish the protos themselves.

3. 🟠 **`--against main` is a moving baseline, not the published contract.**
   - Any break that lands on main, through an override, a bypass or a direct push, becomes the new accepted baseline.
   - What partners hold is your last release, not main. Compare against the released tag or BSR version.

4. 🟠 **The PR can change the rules that judge it.**
   - `buf.yaml` is read from the PR's working copy. A PR can add `ignore`, `ignore_only` or `except`, or change the category, and still pass.
   - Unless `buf.yaml` is under CODEOWNERS and the check is a required status with no admin bypass, "cannot break" is false.

5. 🟡 **`buf lint` STANDARD is irrelevant to the claim.** It checks style, not compatibility.

6. 🟡 **Some breaks are compatible by design.** Adding an enum value is allowed by buf, but it breaks clients with closed-enum handling. Decide whether that counts as a break for your contract.

## What you can sign today

> "CI blocks wire-incompatible and source-incompatible changes at the proto package level on pull requests, relative to the main branch."

## What gets you to the stronger statement

1. Move `breaking` to `FILE`. Review the diff against main first.
2. Add a REST contract check:
   - Generate OpenAPI from the protos and commit it.
   - Run a diff tool such as `oasdiff breaking` against the last release.
   - Fail the PR on any break.
3. Change the baseline to the latest release tag or BSR module version.
4. Protect `buf.yaml` and the CI workflow with CODEOWNERS. Make both checks required, and disable admin bypass.
5. Run canary PRs and confirm each goes red:
   - rename a field
   - change an `http` path
   - move a message to another file
   - add `ignore` to `buf.yaml`

   Use their results as the audit evidence for compliance.
6. Document what the checks don't cover, such as semantics and closed-enum behavior. Then scope the statement to the checks you actually run.

I can draft the CI changes or the narrower compliance wording if you want either.