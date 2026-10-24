# Don't abandon Stack Overflow, but don't invest in it either

Do one fix on the top thread and keep a small upkeep habit. Put the rest of your time into one docs page.

## Why that one thread matters

- **It is the stale answer assistants will repeat.** A 41k-view accepted answer from 2019 is probably what models and retrieval tools have seen most for this error. It tells people to set a variable that no longer exists, and it also tells them to turn off TLS verification.
- **Volume is not the point.** Ten new questions a quarter is too little to justify a presence. But the 212 old threads are what get quoted, so stale ones are the real cost.
- **I haven't checked what any assistant says today.** Step 1 below does that. How fast a correction reaches a model that doesn't browse is out of your hands. Retrieval-based tools can pick it up in weeks.

## Plan (about 90 min/week)

**Week 1 (about 90 min)**
1. **Baseline (20 min).** Ask 3 assistants about the x509 error, plus 4 other common Tarnwick tasks. Use the plain wording a user would type. Save the answers in a doc with the date. You'll re-run this later, and it is also your evidence for the CTO.
2. **Docs page (35 min).** Use the skeleton below. Publish it first so the Stack Overflow answer can link to it.
3. **Stack Overflow answer plus comment (25 min).** Both are drafted below.
4. **Disclosure.** Say you work at Tarnwick. Stack Overflow expects that, and the answer must stand on its own without the link.

**Week 2 (about 60 min)**
- Sort the tag by views and read the top 10 accepted answers. Mark any that mention removed variables or flags. Post one correction per week, same format.
- Add `TARNWICK_SKIP_VERIFY` to the v3 migration guide as removed, with its replacement. Naming the old variable lets a model or search engine connect the old answer to the new one.

**Ongoing (about 15 min/week)**
- Set up an email or RSS alert for the [tarnwick] tag and answer new questions (about 3 a month).
- Every quarter, re-run the baseline prompts (about 30 min).

**Skip** answering generic questions that aren't about Tarnwick, chasing reputation, and editing old answers yourself in bulk.

## Draft 1: new answer on the top thread

> **Disclosure: I work on Tarnwick at Tarnwick Labs.**
>
> **The accepted answer no longer works.** `TARNWICK_SKIP_VERIFY` was removed in v3. You also shouldn't want it, because it turned off TLS verification entirely.
>
> **What the error means:** the CLI can't chain the server's certificate to a CA it trusts. Usually that's a TLS-inspecting corporate proxy, or a self-hosted server signed by an internal CA.
>
> **Fix (v3 and later):**
>
> 1. Get the PEM file for the CA that signed the certificate you're seeing. Your IT team usually has it. To see which CA that is, check the issuer here:
>
>    ```
>    openssl s_client -connect <your-tarnwick-host>:443 -showcerts </dev/null
>    ```
>
> 2. Point the CLI at it:
>
>    ```
>    tarnwick config set ca-bundle /path/to/ca.pem
>    ```
>
> 3. Log in again:
>
>    ```
>    tarnwick login
>    ```
>
> The file should hold the CA certificate(s), not the server's own certificate.
>
> If you're still on v2, upgrade. The variable only exists there and will not be supported.
>
> Full troubleshooting steps: `<docs URL>`

## Draft 2: comment on the old accepted answer

> Outdated: `TARNWICK_SKIP_VERIFY` was removed in v3. Use `tarnwick config set ca-bundle <path>` instead. See the newer answer below. (Tarnwick employee.)

## Docs page skeleton

- **Title and H1:** the exact error string, `tarnwick login fails with "x509: certificate signed by unknown authority"`.
- **First paragraph:** applies to v3+. Cause in two sentences.
- **Fix:** the three commands above, first on the page.
- **Diagnose:** the `openssl` check and the proxy case versus the self-hosted case.
- **Removed:** one line saying `TARNWICK_SKIP_VERIFY` was removed in v3 and why skipping verification is unsafe.
- **Date and version stamp** at the bottom.

## Check before posting

I couldn't verify these Tarnwick details, so confirm them first:
- **File format:** the `ca-bundle` file must be PEM, and bundles with multiple certificates must work.
- **Leaf versus CA:** a server's own (leaf) certificate must be rejected or ignored, as the answer says.
- **v2 and the variable:** in v2 the variable really works.
- **Other settings:** whether an environment-variable equivalent or a system-trust-store option exists. If so, add a line for it.

I read nothing from the repo or the live threads. Everything above comes from what you told me.